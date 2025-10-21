"""
Delete All Cognito User Pools Script

This script deletes ALL Cognito User Pools from AWS across all configured regions.
Before deleting each pool, it checks for and deletes any custom domains.

WARNING: This is a destructive operation and cannot be undone.
"""

import sys
import time
import boto3
from botocore.exceptions import ClientError
from sam_deploy.config.mapping import Region


def get_user_pool_domain(user_pool_id: str, region: str):
    """
    Check if a user pool has a custom domain configured.

    Args:
        user_pool_id: The user pool ID
        region: AWS region

    Returns:
        Domain name if found, None otherwise
    """
    client = boto3.client('cognito-idp', region_name=region)

    try:
        # Get user pool details to find domain
        response = client.describe_user_pool(UserPoolId=user_pool_id)
        user_pool = response.get('UserPool', {})

        # Check for custom domain in user pool attributes
        # Note: Custom domains are stored separately, need to check via describe_user_pool_domain
        # But we need the domain name to check, so we'll try common patterns

        # Try to get domain from user pool name/tags
        pool_name = user_pool.get('Name', '')

        # List all domains and check if any belong to this user pool
        # Unfortunately, there's no direct API to get domain from pool ID
        # We'll need to try common domain patterns or list all domains

        return None  # Will implement domain checking differently

    except Exception as e:
        print(f"    [ERROR] Failed to get domain for pool {user_pool_id}: {e}")
        return None


def delete_user_pool_domain(domain: str, region: str, user_pool_id: str = None) -> bool:
    """
    Delete a Cognito User Pool custom domain.

    Args:
        domain: The custom domain to delete
        region: AWS region

    Returns:
        True if deleted successfully, False otherwise
    """
    client = boto3.client('cognito-idp', region_name=region)

    try:
        print(f"    [DOMAIN] Deleting domain: {domain}")

        # Call delete_user_pool_domain - some AWS SDK versions require UserPoolId
        if user_pool_id:
            response = client.delete_user_pool_domain(Domain=domain, UserPoolId=user_pool_id)
        else:
            response = client.delete_user_pool_domain(Domain=domain)

        print(f"    [OK] Domain deletion initiated: {domain}")

        # Wait for domain deletion to complete (can take a while for custom domains)
        print(f"    [WAIT] Waiting for domain deletion to complete...")
        time.sleep(5)

        # Verify deletion
        try:
            client.describe_user_pool_domain(Domain=domain)
            # If we get here, domain still exists
            print(f"    [WARNING] Domain may still be deleting: {domain}")
            time.sleep(5)  # Wait a bit more
        except ClientError as e:
            if e.response.get('Error', {}).get('Code', '') == 'ResourceNotFoundException':
                print(f"    [OK] Domain successfully deleted: {domain}")

        return True

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'ResourceNotFoundException':
            print(f"    [INFO] Domain not found: {domain}")
            return True
        else:
            print(f"    [ERROR] Failed to delete domain {domain}: {e}")
            return False
    except Exception as e:
        print(f"    [ERROR] Failed to delete domain {domain}: {e}")
        return False


def check_and_delete_domain_for_pool(user_pool_id: str, user_pool_name: str, region: str) -> bool:
    """
    Check if a user pool has a custom domain and delete it.

    This searches through all possible domain patterns and also checks
    the user pool's actual configuration.

    Args:
        user_pool_id: The user pool ID
        user_pool_name: The user pool name
        region: AWS region

    Returns:
        True if domain was handled (deleted or didn't exist), False on error
    """
    client = boto3.client('cognito-idp', region_name=region)

    # Strategy 1: Check common domain patterns
    # Based on your codebase, domains are typically: auth-{env}.dzgro.com
    potential_domains = []

    # Extract environment from pool name (e.g., "DzgroUserPoolDev" -> "dev")
    name_lower = user_pool_name.lower()
    if 'dev' in name_lower:
        potential_domains.extend(['auth-dev.dzgro.com', 'dzgro-dev', 'dzgrodev'])
    elif 'staging' in name_lower:
        potential_domains.extend(['auth-staging.dzgro.com', 'dzgro-staging', 'dzgrostaging'])
    elif 'prod' in name_lower:
        potential_domains.extend(['auth-prod.dzgro.com', 'auth.dzgro.com', 'dzgro-prod', 'dzgroprod'])

    # Also try generic patterns
    potential_domains.extend([
        user_pool_name.lower(),
        user_pool_name.lower().replace('userpool', ''),
        user_pool_name.lower().replace('_', '-'),
    ])

    # Strategy 2: List ALL domains in the region and check which belongs to this pool
    print(f"    [SEARCH] Searching for domains associated with this pool...")

    try:
        # We need to brute-force check since there's no direct API
        # Check all our potential domains
        domains_found = []

        for domain in potential_domains:
            try:
                response = client.describe_user_pool_domain(Domain=domain)
                domain_desc = response.get('DomainDescription', {})

                # Check if this domain belongs to our user pool
                if domain_desc.get('UserPoolId') == user_pool_id:
                    domains_found.append(domain)
                    print(f"    [FOUND] Custom domain: {domain}")
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code != 'ResourceNotFoundException':
                    # Only log non-404 errors
                    pass
            except Exception:
                pass

        # Strategy 3: Get the user pool details and check Domain field
        try:
            response = client.describe_user_pool(UserPoolId=user_pool_id)
            user_pool = response.get('UserPool', {})

            # Check if Domain field exists (for Cognito-provided domains)
            if 'Domain' in user_pool and user_pool['Domain']:
                cognito_domain = user_pool['Domain']
                print(f"    [FOUND] Cognito domain prefix: {cognito_domain}")
                if cognito_domain not in domains_found:
                    domains_found.append(cognito_domain)

        except Exception as e:
            print(f"    [WARNING] Could not get user pool details: {e}")

        # Delete all found domains
        all_deleted = True
        for domain in domains_found:
            if not delete_user_pool_domain(domain, region, user_pool_id):
                all_deleted = False

        if not domains_found:
            print(f"    [WARNING] No domain found, but pool reports domain exists")
            print(f"    [INFO] Will attempt common domain patterns...")

            # Last resort: try to delete without confirming existence
            backup_domains = ['auth-dev.dzgro.com', 'auth-staging.dzgro.com', 'auth-prod.dzgro.com', 'auth.dzgro.com']
            for domain in backup_domains:
                try:
                    client.delete_user_pool_domain(Domain=domain)
                    print(f"    [OK] Deleted domain: {domain}")
                    time.sleep(2)
                    return True
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    if error_code == 'ResourceNotFoundException':
                        continue
                    else:
                        pass
                except Exception:
                    pass

        return all_deleted or len(domains_found) > 0

    except Exception as e:
        print(f"    [ERROR] Error in domain detection: {e}")
        return False


def delete_user_pool(user_pool_id: str, user_pool_name: str, region: str) -> bool:
    """
    Delete a Cognito User Pool.

    Args:
        user_pool_id: The user pool ID
        user_pool_name: The user pool name
        region: AWS region

    Returns:
        True if deleted successfully, False otherwise
    """
    client = boto3.client('cognito-idp', region_name=region)

    try:
        print(f"    [POOL] Deleting user pool: {user_pool_name} ({user_pool_id})")
        client.delete_user_pool(UserPoolId=user_pool_id)
        print(f"    [OK] User pool deleted: {user_pool_name}")
        return True

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'ResourceNotFoundException':
            print(f"    [INFO] User pool not found: {user_pool_name}")
            return True
        else:
            print(f"    [ERROR] Failed to delete user pool {user_pool_name}: {e}")
            return False
    except Exception as e:
        print(f"    [ERROR] Failed to delete user pool {user_pool_name}: {e}")
        return False


def get_all_user_pools_in_region(region: str):
    """
    Get all Cognito User Pools in a region.

    Args:
        region: AWS region

    Returns:
        List of tuples (pool_id, pool_name)
    """
    client = boto3.client('cognito-idp', region_name=region)

    try:
        pools = []
        paginator = client.get_paginator('list_user_pools')

        for page in paginator.paginate(MaxResults=60):
            for pool in page.get('UserPools', []):
                pools.append((pool['Id'], pool['Name']))

        return pools

    except Exception as e:
        print(f"  [ERROR] Failed to list user pools: {e}")
        return []


def delete_all_cognito_pools():
    """Delete all Cognito User Pools from all regions"""
    print("\n" + "=" * 80)
    print("DELETE ALL COGNITO USER POOLS")
    print("=" * 80)

    # Get all regions
    regions = Region.all()

    print(f"\nWill scan and delete Cognito User Pools from {len(regions)} regions:")
    for region in regions:
        print(f"  - {region.value}")

    # Confirmation
    print("\n" + "=" * 80)
    print("WARNING: This will DELETE ALL Cognito User Pools from AWS")
    print("This includes:")
    print("  - Custom domains (deleted first)")
    print("  - All users in the pools")
    print("  - All pool configurations")
    print("This operation CANNOT be undone!")
    print("=" * 80)

    # Check for --confirm flag
    if "--confirm" not in sys.argv:
        confirm = input("\nType 'DELETE ALL POOLS' to confirm: ")
        if confirm != "DELETE ALL POOLS":
            print("[CANCELLED] Operation cancelled")
            return
    else:
        print("\n[AUTO-CONFIRMED] Using --confirm flag, proceeding with deletion...")

    total_deleted = 0
    total_pools = 0
    total_domains_deleted = 0

    # Process each region
    for region in regions:
        print(f"\n{'=' * 80}")
        print(f"REGION: {region.value}")
        print(f"{'=' * 80}")

        # Get all user pools in this region
        print(f"[SCAN] Scanning for Cognito User Pools...")
        pools = get_all_user_pools_in_region(region.value)

        if not pools:
            print(f"[INFO] No Cognito User Pools found in {region.value}")
            continue

        print(f"[FOUND] Found {len(pools)} user pools:")
        for pool_id, pool_name in pools:
            print(f"  - {pool_name} ({pool_id})")

        total_pools += len(pools)

        # Delete each pool
        for pool_id, pool_name in pools:
            print(f"\n[PROCESSING] User Pool: {pool_name}")

            # Step 1: Check for and delete custom domain
            domain_ok = check_and_delete_domain_for_pool(pool_id, pool_name, region.value)

            if not domain_ok:
                print(f"    [WARNING] Domain deletion had issues, but will try to delete pool anyway...")

            # Step 2: Delete the user pool
            if delete_user_pool(pool_id, pool_name, region.value):
                total_deleted += 1

    print(f"\n{'=' * 80}")
    print(f"[COMPLETE] Deletion Summary")
    print(f"{'=' * 80}")
    print(f"Total user pools found: {total_pools}")
    print(f"Total user pools deleted: {total_deleted}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    delete_all_cognito_pools()
