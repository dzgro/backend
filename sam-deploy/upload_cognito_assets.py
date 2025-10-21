"""
One-time script to upload Cognito branding assets to S3 buckets.

Uploads the 3 image files to dzgro-assets-{env} buckets for dev, staging, and prod.
"""

import boto3
import os
from pathlib import Path

# Environments to upload to
ENVIRONMENTS = ['dev', 'staging', 'prod']

# Image files to upload (from builder/images directory)
IMAGES_DIR = Path(__file__).parent / 'src' / 'sam_deploy' / 'builder' / 'images'
ASSETS = [
    {
        'filename': 'dzgro-logo.png',
        's3_key': 'images/dzgro-logo.png',
        'content_type': 'image/png'
    },
    {
        'filename': 'dzgro-ico.ico',
        's3_key': 'images/dzgro-ico.ico',
        'content_type': 'image/x-icon'
    },
    {
        'filename': 'cognito-bg.png',
        's3_key': 'images/cognito-bg.png',
        'content_type': 'image/png'
    }
]

def upload_assets_to_bucket(env: str):
    """Upload all assets to the specified environment's bucket."""
    bucket_name = f'dzgro-assets-{env}'

    print(f"\n[{env.upper()}] Uploading assets to {bucket_name}...")

    # Initialize S3 client
    s3 = boto3.client('s3', region_name='ap-south-1')

    # Check if bucket exists
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"  [OK] Bucket {bucket_name} exists")
    except Exception as e:
        print(f"  [ERROR] Bucket {bucket_name} not found: {e}")
        return False

    # Upload each asset
    uploaded = 0
    for asset in ASSETS:
        file_path = IMAGES_DIR / asset['filename']

        if not file_path.exists():
            print(f"  [ERROR] File not found: {file_path}")
            continue

        try:
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Upload to S3 (private, will be accessed via CloudFront)
            s3.put_object(
                Bucket=bucket_name,
                Key=asset['s3_key'],
                Body=file_data,
                ContentType=asset['content_type']
            )

            file_size_kb = len(file_data) / 1024
            print(f"  [OK] Uploaded {asset['filename']} -> s3://{bucket_name}/{asset['s3_key']} ({file_size_kb:.1f} KB)")
            uploaded += 1

        except Exception as e:
            print(f"  [ERROR] Failed to upload {asset['filename']}: {e}")

    print(f"  [SUMMARY] Uploaded {uploaded}/{len(ASSETS)} assets to {env}")
    return uploaded == len(ASSETS)


def main():
    """Main function to upload assets to all environment buckets."""
    print("=" * 80)
    print("COGNITO BRANDING ASSETS UPLOAD")
    print("=" * 80)
    print(f"\nUploading {len(ASSETS)} assets to {len(ENVIRONMENTS)} environment buckets")
    print(f"Source directory: {IMAGES_DIR}")

    # Verify all files exist
    print("\nVerifying source files...")
    all_files_exist = True
    for asset in ASSETS:
        file_path = IMAGES_DIR / asset['filename']
        if file_path.exists():
            file_size_kb = file_path.stat().st_size / 1024
            print(f"  [OK] {asset['filename']} ({file_size_kb:.1f} KB)")
        else:
            print(f"  [ERROR] {asset['filename']} NOT FOUND")
            all_files_exist = False

    if not all_files_exist:
        print("\n[ERROR] Some files are missing. Aborting.")
        return

    # Upload to each environment
    results = {}
    for env in ENVIRONMENTS:
        success = upload_assets_to_bucket(env)
        results[env] = success

    # Print summary
    print("\n" + "=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)

    for env, success in results.items():
        status = "[OK]" if success else "[FAILED]"
        print(f"  {status} {env}: dzgro-assets-{env}")

    all_success = all(results.values())

    if all_success:
        print("\n[SUCCESS] All assets uploaded successfully to all environments!")
        print("\nCloudFront URLs will be:")
        for env in ENVIRONMENTS:
            assets_domain = f"assets.{env}.dzgro.com"
            print(f"\n  {env.upper()}:")
            for asset in ASSETS:
                print(f"    - https://{assets_domain}/{asset['s3_key']}")
    else:
        print("\n[WARNING] Some uploads failed. Please check errors above.")


if __name__ == '__main__':
    main()
