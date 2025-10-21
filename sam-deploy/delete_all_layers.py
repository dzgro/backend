"""
Delete All Lambda Layers Script

This script deletes ALL lambda layers from AWS across all configured regions.
WARNING: This is a destructive operation and cannot be undone.
"""

import sys
import boto3
from sam_deploy.config.mapping import Region

def delete_all_layer_versions(layer_name: str, region: str):
    """Delete all versions of a specific lambda layer"""
    client = boto3.client('lambda', region_name=region)

    try:
        # List all versions
        response = client.list_layer_versions(LayerName=layer_name)
        versions = response.get('LayerVersions', [])

        if not versions:
            print(f"  [INFO] No versions found for {layer_name}")
            return 0

        print(f"  [DELETE] Deleting {len(versions)} versions of {layer_name}...")
        deleted_count = 0

        for version in versions:
            try:
                client.delete_layer_version(
                    LayerName=layer_name,
                    VersionNumber=version['Version']
                )
                print(f"    [OK] Deleted version {version['Version']}")
                deleted_count += 1
            except Exception as e:
                print(f"    [ERROR] Failed to delete version {version['Version']}: {e}")

        return deleted_count

    except client.exceptions.ResourceNotFoundException:
        print(f"  [INFO] Layer {layer_name} not found")
        return 0
    except Exception as e:
        print(f"  [ERROR] Error processing {layer_name}: {e}")
        return 0


def get_all_layers_in_region(region: str):
    """Get all lambda layers in a region"""
    client = boto3.client('lambda', region_name=region)

    try:
        layers = []
        paginator = client.get_paginator('list_layers')

        for page in paginator.paginate():
            for layer in page.get('Layers', []):
                layers.append(layer['LayerName'])

        return layers
    except Exception as e:
        print(f"  [ERROR] Failed to list layers: {e}")
        return []


def delete_all_layers():
    """Delete all lambda layers from all regions"""
    print("\n" + "=" * 80)
    print("DELETE ALL LAMBDA LAYERS")
    print("=" * 80)

    # Get all regions
    regions = Region.all()

    print(f"\nWill scan and delete layers from {len(regions)} regions:")
    for region in regions:
        print(f"  - {region.value}")

    # Confirmation
    print("\n" + "=" * 80)
    print("WARNING: This will DELETE ALL lambda layers from AWS")
    print("This operation CANNOT be undone!")
    print("=" * 80)

    # Check for --confirm flag
    if "--confirm" not in sys.argv:
        confirm = input("\nType 'DELETE ALL LAYERS' to confirm: ")
        if confirm != "DELETE ALL LAYERS":
            print("[CANCELLED] Operation cancelled")
            return
    else:
        print("\n[AUTO-CONFIRMED] Using --confirm flag, proceeding with deletion...")

    total_deleted = 0
    total_layers = 0

    # Process each region
    for region in regions:
        print(f"\n{'=' * 80}")
        print(f"REGION: {region.value}")
        print(f"{'=' * 80}")

        # Get all layers in this region
        print(f"[SCAN] Scanning for lambda layers...")
        layers = get_all_layers_in_region(region.value)

        if not layers:
            print(f"[INFO] No lambda layers found in {region.value}")
            continue

        print(f"[FOUND] Found {len(layers)} layers:")
        for layer in layers:
            print(f"  - {layer}")

        total_layers += len(layers)

        # Delete each layer
        for layer in layers:
            print(f"\n[LAYER] Processing: {layer}")
            deleted = delete_all_layer_versions(layer, region.value)
            total_deleted += deleted

    print(f"\n{'=' * 80}")
    print(f"[COMPLETE] Deletion Summary")
    print(f"{'=' * 80}")
    print(f"Total layers found: {total_layers}")
    print(f"Total versions deleted: {total_deleted}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    delete_all_layers()
