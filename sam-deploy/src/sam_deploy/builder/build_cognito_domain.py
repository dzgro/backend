"""
Cognito User Pool Domain Builder with parallel creation and status polling.

This module handles creating Cognito User Pool custom domains for multiple environments
simultaneously, similar to how certificate creation works.
"""

import boto3
import time
from typing import Dict
from botocore.exceptions import ClientError
from dzgroshared.db.enums import ENVIRONMENT
from sam_deploy.config.mapping import Region
from sam_deploy.builder.template_builder import TemplateBuilder


class CognitoDomainBuilder:
    """
    Builder for AWS Cognito User Pool Custom Domains.

    Handles parallel domain creation across multiple environments with:
    - Parallel domain creation for dev, staging, prod
    - Status polling with formatted logging
    - Managed login branding setup after domains are ACTIVE
    """

    @staticmethod
    def createUserPoolDomainsForAllEnvironments(
        environments: list[ENVIRONMENT],
        auth_certificate_arns: Dict[str, str],
        region: Region = Region.DEFAULT
    ) -> Dict[str, Dict]:
        """
        Create/retrieve Cognito User Pool domains for all environments simultaneously.

        This method:
        1. Checks existing domains and creates new ones for all environments at once
        2. Polls all domains together until ALL are ACTIVE
        3. Creates/updates managed login branding for all domains
        4. Logs status of all domains during polling

        Args:
            environments: List of ENVIRONMENT enums (e.g., [DEV, STAGING, PROD])
            auth_certificate_arns: Dict mapping env.value to ACM certificate ARN (us-east-1)
            region: AWS region for Cognito User Pools (default: ap-south-1)

        Returns:
            Dictionary with structure:
            {
                'dev': {
                    'domain': 'auth.dev.dzgro.com',
                    'cloudfront_distribution': 'dxxxxx.cloudfront.net',
                    'status': 'ACTIVE',
                    'user_pool_id': 'ap-south-1_xxxxx',
                    'branding_id': 'xxxxx'
                },
                'staging': {...},
                'prod': {...}
            }
        """
        print(f"\n[DOMAIN] Creating/checking Cognito User Pool domains for {len(environments)} environments...")

        # Initialize Cognito IDP client
        idp = boto3.client("cognito-idp", region_name=region.value)

        # Domain tracking: {env.value: {'domain': str, 'user_pool_id': str, 'client_id': str,
        #                                'status': str, 'cloudfront_distribution': str, 'builder': TemplateBuilder}}
        domain_tracker = {}

        # Step 1: Check existing domains and create new ones if needed
        print(f"\n[DOMAIN] Step 1: Checking existing domains and creating new ones if needed...")

        for env in environments:
            # Create builder for this environment to get domain names
            builder = TemplateBuilder(env)
            domain = builder.getAuthDomainName()
            user_pool_name = builder.getUserPoolName()
            client_name = builder.getUserPoolClientName()

            # Get certificate ARN for this environment
            auth_cert_arn = auth_certificate_arns.get(env.value)
            if not auth_cert_arn:
                raise ValueError(f"No Auth certificate ARN provided for {env.value}")

            # Find User Pool ID
            user_pools = idp.list_user_pools(MaxResults=60)
            user_pool_id = None
            for pool in user_pools['UserPools']:
                if pool['Name'] == user_pool_name:
                    user_pool_id = pool['Id']
                    break

            if not user_pool_id:
                print(f"  [SKIP] User Pool {user_pool_name} not found - skipping {env.value}")
                continue

            # Find User Pool Client ID
            clients_response = idp.list_user_pool_clients(
                UserPoolId=user_pool_id,
                MaxResults=60
            )
            client_id = None
            for client in clients_response['UserPoolClients']:
                if client['ClientName'] == client_name:
                    client_id = client['ClientId']
                    break

            if not client_id:
                print(f"  [WARNING] User Pool Client {client_name} not found for {env.value}")

            # Check if domain exists
            domain_exists = False
            try:
                desc = idp.describe_user_pool_domain(Domain=domain)
                domain_desc = desc.get('DomainDescription')

                # Check if domain description exists and has content
                if domain_desc and domain_desc.get('Status'):
                    # Domain exists
                    status = domain_desc['Status']
                    cloudfront_dist = domain_desc.get('CloudFrontDistribution', 'N/A')
                    print(f"  [FOUND] Domain {domain}: {status}")

                    domain_tracker[env.value] = {
                        'domain': domain,
                        'user_pool_id': user_pool_id,
                        'client_id': client_id,
                        'status': status,
                        'cloudfront_distribution': cloudfront_dist,
                        'builder': builder,
                        'needs_creation': False
                    }
                    domain_exists = True

            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code == 'ResourceNotFoundException':
                    # Domain doesn't exist - will create it below
                    pass
                else:
                    # Some other error - re-raise
                    raise

            if not domain_exists:
                # Domain doesn't exist - create it
                print(f"  [NEW] Creating domain {domain} with cert {auth_cert_arn[:50]}...")

                try:
                    response = idp.create_user_pool_domain(
                        Domain=domain,
                        UserPoolId=user_pool_id,
                        ManagedLoginVersion=2,
                        CustomDomainConfig={
                            "CertificateArn": auth_cert_arn
                        }
                    )
                    cloudfront_dist = response.get('CloudFrontDomain', 'N/A')
                    print(f"  [CREATED] Domain {domain} with CloudFront: {cloudfront_dist}")

                    domain_tracker[env.value] = {
                        'domain': domain,
                        'user_pool_id': user_pool_id,
                        'client_id': client_id,
                        'status': 'CREATING',
                        'cloudfront_distribution': cloudfront_dist,
                        'builder': builder,
                        'needs_creation': True
                    }

                except ClientError as e:
                    print(f"  [ERROR] Failed to create domain {domain}: {e}")
                    raise

        if not domain_tracker:
            print(f"\n[DOMAIN] No domains to process - all User Pools may be missing")
            return {}

        # Step 2: Wait for all domains to be ACTIVE
        print(f"\n[DOMAIN] Step 2: Waiting for all {len(domain_tracker)} domains to be ACTIVE...")

        # Check if all domains are already active
        all_active = all(info['status'] == 'ACTIVE' for info in domain_tracker.values())

        if all_active:
            print(f"  [OK] All {len(domain_tracker)} domains are already ACTIVE - skipping polling")

        check_count = 0

        while not all_active:
            check_count += 1
            print(f"\n[DOMAIN] Check #{check_count} - Domain Status:")
            print("=" * 120)

            all_active = True
            active_count = 0
            creating_count = 0
            failed_domains = []

            # Check status of all domains
            for env_val, domain_info in domain_tracker.items():
                try:
                    # Get current status
                    desc = idp.describe_user_pool_domain(Domain=domain_info['domain'])
                    if desc.get('DomainDescription'):
                        current_status = desc['DomainDescription']['Status']
                        cloudfront_dist = desc['DomainDescription'].get('CloudFrontDistribution', 'N/A')

                        # Update tracking info
                        domain_info['status'] = current_status
                        domain_info['cloudfront_distribution'] = cloudfront_dist

                        # Log status
                        status_emoji = "✓" if current_status == 'ACTIVE' else "⏳" if current_status == 'CREATING' else "✗"
                        print(f"  {status_emoji} {env_val:8} | {domain_info['domain']:30} | {current_status:12} | {cloudfront_dist}")

                        # Check if all are active
                        if current_status == 'ACTIVE':
                            active_count += 1
                        elif current_status == 'CREATING':
                            creating_count += 1
                            all_active = False
                        else:
                            # Failed status
                            all_active = False
                            failed_domains.append((env_val, domain_info['domain'], current_status))
                    else:
                        # Domain description is empty
                        all_active = False
                        failed_domains.append((env_val, domain_info['domain'], 'EMPTY_DESCRIPTION'))
                        print(f"  ✗ {env_val:8} | {domain_info['domain']:30} | EMPTY_DESCRIPTION")

                except ClientError as e:
                    all_active = False
                    failed_domains.append((env_val, domain_info['domain'], str(e)))
                    print(f"  ✗ {env_val:8} | {domain_info['domain']:30} | ERROR: {e}")

            print("=" * 120)
            print(f"  Summary: {active_count} active, {creating_count} creating")

            # Check for failed domains
            if failed_domains:
                error_msg = "The following domains failed:\n"
                for env_val, domain, status in failed_domains:
                    error_msg += f"  - {env_val}: {domain} - Status: {status}\n"
                raise Exception(error_msg)

            # Wait before next check if not all active
            if not all_active:
                print(f"\n[DOMAIN] Waiting 15 seconds before next check...")
                time.sleep(15)

        print(f"\n[DOMAIN] ✓ All {len(domain_tracker)} domains are ACTIVE!")

        # Step 3: Create/update managed login branding for all domains
        print(f"\n[DOMAIN] Step 3: Creating/updating managed login branding...")

        for env_val, domain_info in domain_tracker.items():
            if not domain_info.get('client_id'):
                print(f"  [SKIP] No client ID for {env_val} - skipping branding")
                continue

            user_pool_id = domain_info['user_pool_id']
            client_id = domain_info['client_id']
            builder = domain_info['builder']

            try:
                # Load assets from CloudFront CDN
                import requests

                # Get CloudFront domain for this environment
                assets_domain = builder.getAssetsDomainName()

                # Define assets to fetch from CloudFront
                asset_configs = [
                    {
                        'url': f'https://{assets_domain}/images/dzgro-logo.png',
                        'category': 'PAGE_HEADER_LOGO',
                        'extension': 'PNG'
                    },
                    {
                        'url': f'https://{assets_domain}/images/dzgro-ico.ico',
                        'category': 'FAVICON_ICO',
                        'extension': 'ICO'
                    },
                    {
                        'url': f'https://{assets_domain}/images/cognito-bg.png',
                        'category': 'PAGE_HEADER_BACKGROUND',
                        'extension': 'PNG'
                    }
                ]

                # Fetch assets from CloudFront
                assets = []
                print(f"  [ASSETS] Fetching {len(asset_configs)} assets from {assets_domain}...")
                for asset_config in asset_configs:
                    try:
                        response = requests.get(asset_config['url'], timeout=10)
                        response.raise_for_status()

                        assets.append({
                            'Category': asset_config['category'],
                            'ColorMode': 'LIGHT',
                            'Extension': asset_config['extension'],
                            'Bytes': response.content
                        })

                        file_size_kb = len(response.content) / 1024
                        print(f"    - {asset_config['category']}: {file_size_kb:.1f} KB ({asset_config['extension']})")
                    except Exception as e:
                        print(f"    [ERROR] Failed to fetch {asset_config['url']}: {e}")
                        raise

                if len(assets) != len(asset_configs):
                    raise Exception(f"Failed to fetch all assets. Got {len(assets)}/{len(asset_configs)}")

                # Check if branding already exists
                branding_exists = False
                try:
                    response = idp.describe_managed_login_branding_by_client(
                        UserPoolId=user_pool_id,
                        ClientId=client_id,
                        ReturnMergedResources=True
                    )
                    branding_id = response['ManagedLoginBranding']['ManagedLoginBrandingId']
                    print(f"  [UPDATE] Updating branding {branding_id} for {env_val}...")

                    response = idp.update_managed_login_branding(
                        UserPoolId=user_pool_id,
                        ManagedLoginBrandingId=branding_id,
                        UseCognitoProvidedValues=True,
                        Assets=assets
                    )
                    domain_info['branding_id'] = branding_id
                    branding_exists = True
                    print(f"  [OK] Updated branding for {env_val}")

                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    if error_code == 'ResourceNotFoundException':
                        # Branding doesn't exist - will create below
                        print(f"  [INFO] No existing branding for {env_val}, will create new")
                    else:
                        # Some other error during describe/update
                        print(f"  [ERROR] Error checking/updating branding for {env_val}: {error_code} - {e}")
                        raise

                if not branding_exists:
                    # Branding doesn't exist - create it
                    print(f"  [CREATE] Creating new branding for {env_val}...")

                    response = idp.create_managed_login_branding(
                        UserPoolId=user_pool_id,
                        ClientId=client_id,
                        UseCognitoProvidedValues=True,
                        Assets=assets
                    )
                    branding_id = response['ManagedLoginBranding']['ManagedLoginBrandingId']
                    domain_info['branding_id'] = branding_id
                    print(f"  [OK] Created branding {branding_id} for {env_val}")

            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                error_msg = e.response.get('Error', {}).get('Message', str(e))
                print(f"  [ERROR] Failed to create/update branding for {env_val}:")
                print(f"    Error Code: {error_code}")
                print(f"    Error Message: {error_msg}")
                # Don't fail the entire operation if branding fails
                domain_info['branding_id'] = None
            except Exception as e:
                print(f"  [ERROR] Unexpected error with branding for {env_val}: {e}")
                import traceback
                traceback.print_exc()
                domain_info['branding_id'] = None

        print(f"\n[DOMAIN] ✓ Managed login branding complete!")

        # Print final summary
        print(f"\n[DOMAIN] Final Summary:")
        print("=" * 120)
        for env_val, domain_info in domain_tracker.items():
            domain = domain_info['domain']
            env_domain = domain_info['builder'].envDomain()
            cname_value = domain.replace(f'.{env_domain}', '')
            print(f"  {env_val:8} | {domain:30} | {domain_info['cloudfront_distribution']}")
            print(f"           | CNAME: {cname_value}")
        print("=" * 120)

        # Build result dictionary (remove builder from results)
        result = {}
        for env_val, domain_info in domain_tracker.items():
            result[env_val] = {
                'domain': domain_info['domain'],
                'cloudfront_distribution': domain_info['cloudfront_distribution'],
                'status': domain_info['status'],
                'user_pool_id': domain_info['user_pool_id'],
                'branding_id': domain_info.get('branding_id')
            }

        return result
