"""
Build Assets Infrastructure
Creates S3 buckets and CloudFront distributions for public assets with custom domains
"""
from sam_deploy.config.mapping import Region
from dzgroshared.db.enums import ENVIRONMENT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sam_deploy.builder.template_builder import TemplateBuilder


class AssetsBuilder:
    """Builds S3 buckets and CloudFront distributions for public assets (all 3 environments)"""

    def __init__(self, builder: 'TemplateBuilder'):
        self.builder = builder

    def execute_for_all_environments(self, region: Region, all_certificates: dict, environments: list):
        """
        Create S3 buckets and CloudFront distributions for all environments

        Args:
            region: AWS region
            all_certificates: Dictionary with certificate ARNs for all environments
            environments: List of ENVIRONMENT enums (e.g., [DEV, STAGING, PROD])
        """
        from sam_deploy.builder.template_builder import TemplateBuilder

        print(f"  [ASSETS] Creating assets infrastructure for all environments...")

        for env in environments:
            # Create temporary builder for this environment
            env_builder = TemplateBuilder(env)

            bucket_name = env_builder.getAssetsBucketName()
            domain_name = env_builder.getAssetsDomainName()
            assets_cert_arn = all_certificates['Assets'][env.value]

            # Build allowed origins based on environment
            allowed_origins = [f'https://{domain_name}']
            if env == ENVIRONMENT.DEV:
                allowed_origins.append('http://localhost:4200')

            # Create S3 bucket for assets
            bucket_resource_name = f'AssetsBucket{env_builder.envtextTitle}'
            self.builder.resources[bucket_resource_name] = {
                'Type': 'AWS::S3::Bucket',
                'Properties': {
                    'BucketName': bucket_name,
                    'PublicAccessBlockConfiguration': {
                        'BlockPublicAcls': False,
                        'BlockPublicPolicy': False,
                        'IgnorePublicAcls': False,
                        'RestrictPublicBuckets': False
                    },
                    'CorsConfiguration': {
                        'CorsRules': [{
                            'AllowedOrigins': allowed_origins,
                            'AllowedMethods': ['GET', 'HEAD'],
                            'AllowedHeaders': ['*'],
                            'MaxAge': 3000
                        }]
                    },
                    'Tags': env_builder.getListTag()
                }
            }

            # Create CloudFront Origin Access Control
            oac_resource_name = f'AssetsOAC{env_builder.envtextTitle}'
            self.builder.resources[oac_resource_name] = {
                'Type': 'AWS::CloudFront::OriginAccessControl',
                'Properties': {
                    'OriginAccessControlConfig': {
                        'Name': f'dzgro-assets-oac-{env_builder.envtextlower}',
                        'OriginAccessControlOriginType': 's3',
                        'SigningBehavior': 'always',
                        'SigningProtocol': 'sigv4'
                    }
                }
            }

            # Create CloudFront distribution
            distribution_resource_name = f'AssetsDistribution{env_builder.envtextTitle}'

            self.builder.resources[distribution_resource_name] = {
                'Type': 'AWS::CloudFront::Distribution',
                'Properties': {
                    'DistributionConfig': {
                        'Enabled': True,
                        'Comment': f'Assets distribution for {env_builder.envtextlower}',
                        'DefaultRootObject': 'index.html',
                        'Aliases': [domain_name],
                        'Origins': [{
                            'Id': 'S3-Assets',
                            'DomainName': {'Fn::GetAtt': [bucket_resource_name, 'RegionalDomainName']},
                            'OriginAccessControlId': {'Ref': oac_resource_name},
                            'S3OriginConfig': {}
                        }],
                        'DefaultCacheBehavior': {
                            'TargetOriginId': 'S3-Assets',
                            'ViewerProtocolPolicy': 'redirect-to-https',
                            'AllowedMethods': ['GET', 'HEAD', 'OPTIONS'],
                            'CachedMethods': ['GET', 'HEAD'],
                            'Compress': True,
                            'ForwardedValues': {
                                'QueryString': False,
                                'Cookies': {'Forward': 'none'},
                                'Headers': ['Origin', 'Access-Control-Request-Method', 'Access-Control-Request-Headers']
                            },
                            'MinTTL': 0,
                            'DefaultTTL': 86400,  # 1 day
                            'MaxTTL': 31536000     # 1 year
                        },
                        'ViewerCertificate': {
                            'AcmCertificateArn': assets_cert_arn,
                            'SslSupportMethod': 'sni-only',
                            'MinimumProtocolVersion': 'TLSv1.2_2021'
                        },
                        'HttpVersion': 'http2',
                        'PriceClass': 'PriceClass_All',
                        'Restrictions': {
                            'GeoRestriction': {
                                'RestrictionType': 'none'
                            }
                        }
                    },
                    'Tags': env_builder.getListTag()
                }
            }

            # Create bucket policy to allow CloudFront access
            bucket_policy_resource_name = f'AssetsBucketPolicy{env_builder.envtextTitle}'
            self.builder.resources[bucket_policy_resource_name] = {
                'Type': 'AWS::S3::BucketPolicy',
                'Properties': {
                    'Bucket': {'Ref': bucket_resource_name},
                    'PolicyDocument': {
                        'Statement': [{
                            'Sid': 'AllowCloudFrontServicePrincipal',
                            'Effect': 'Allow',
                            'Principal': {
                                'Service': 'cloudfront.amazonaws.com'
                            },
                            'Action': 's3:GetObject',
                            'Resource': {'Fn::Sub': f'arn:aws:s3:::{bucket_name}/*'},
                            'Condition': {
                                'StringEquals': {
                                    'AWS:SourceArn': {'Fn::Sub': f'arn:aws:cloudfront::${{AWS::AccountId}}:distribution/${{{distribution_resource_name}}}'}
                                }
                            }
                        }]
                    }
                },
                'DependsOn': distribution_resource_name
            }

            print(f'       - {env.value}: {bucket_name} -> {domain_name}')

        print(f'  [OK] Created 3 assets buckets with CloudFront distributions')
