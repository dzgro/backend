import boto3

client = boto3.client("lambda")

def delete_all_layers():
    paginator = client.get_paginator("list_layers")

    for page in paginator.paginate():
        for layer in page["Layers"]:
            layer_name = layer["LayerName"]
            print(f"Processing layer: {layer_name}")

            # List all versions
            versions = client.list_layer_versions(LayerName=layer_name)
            for v in versions["LayerVersions"]:
                version_number = v["Version"]
                print(f"  Deleting version {version_number}...")
                client.delete_layer_version(
                    LayerName=layer_name,
                    VersionNumber=version_number
                )
                print("  ✅ Deleted")

if __name__ == "__main__":
    delete_all_layers()
