import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mapping import FUNCTIONS_MAP
import subprocess
import shutil
import boto3

# Dynamically get all unique regions from FUNCTIONS_MAP
UNIQUE_REGIONS = set()
for config in FUNCTIONS_MAP.values():
    UNIQUE_REGIONS.update(config.get('region', []))
UNIQUE_REGIONS = list(UNIQUE_REGIONS)

def create_layer_zip():
    print("Step 1: Creating dzgroshared layer zip using deploy_dzgroshared_layer.py logic...")
    BUILD_DIR = "layer_build"
    PYTHON_VERSION = "python3.12"
    PYPROJECT_PATH = "../dzgroshared/pyproject.toml"
    SRC_PATH = "../dzgroshared/src/dzgroshared"
    DEPLOYMENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # Step 1: Install dependencies to python/lib directory
    os.makedirs(f"{BUILD_DIR}/python/lib/{PYTHON_VERSION}/site-packages", exist_ok=True)
    if not os.path.exists(PYPROJECT_PATH):
        print(f"Error: {PYPROJECT_PATH} not found. Please ensure you are running from the workspace root and the file exists.")
        sys.exit(1)
    subprocess.run([
        "poetry", "export", "-f", "requirements.txt", "--output", "requirements.txt", "--without-hashes"
    ], cwd="../dzgroshared", check=True)
    shutil.move("../dzgroshared/requirements.txt", f"{BUILD_DIR}/requirements.txt")
    subprocess.run([
        "pip", "install", "-r", f"{BUILD_DIR}/requirements.txt", "-t", f"{BUILD_DIR}/python/lib/{PYTHON_VERSION}/site-packages"
    ], check=True)
    shutil.copytree(SRC_PATH, f"{BUILD_DIR}/python/lib/{PYTHON_VERSION}/site-packages/dzgroshared", dirs_exist_ok=True)
    zip_path = shutil.make_archive("dzgroshared_layer", "zip", BUILD_DIR)
    # Move the zip to deployment folder
    final_zip_path = os.path.join(DEPLOYMENT_DIR, "dzgroshared_layer.zip")
    shutil.move(zip_path, final_zip_path)
    print(f"Zip creation step complete. Saved to {final_zip_path}")

def publish_layer(region):
    print(f"Step 2: Publishing dzgroshared Lambda Layer for region: {region}...")
    LAYER_NAME = "dzgroshared-layer"
    ZIP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dzgroshared_layer.zip")
    PYTHON_VERSION = "python3.12"
    client = boto3.client("lambda", region_name=region)
    with open(ZIP_FILE, "rb") as f:
        layer_zip = f.read()
    # Publish the layer
    response = client.publish_layer_version(
        LayerName=LAYER_NAME,
        Description="dzgroshared dependencies and code",
        Content={"ZipFile": layer_zip},
        CompatibleRuntimes=[PYTHON_VERSION],
    )
    print(f"Layer published in {region}: {response['LayerVersionArn']}")
    return response["LayerVersionArn"]

def create_template_file(region, layer_version_arn):
    print(f"Step 3: Creating template file dynamically for region: {region} with layer version ARN: {layer_version_arn}...")
    # Code to create template file will be added here
    print(f"Template file creation step complete for region: {region}.")

def deploy_template_with_sam(region):
    print(f"Step 4: Deploying template file using AWS SAM for region: {region}...")
    # Code to deploy template file with AWS SAM will be added here
    print(f"Template deployment step complete for region: {region}.")

def deploy_api_on_ec2():
    print("Step 5: Deploying API on EC2...")
    # Code to deploy API on EC2 will be added here
    print("API deployment on EC2 step complete.")

if __name__ == "__main__":
    create_layer_zip()
    for region in UNIQUE_REGIONS:
        layer_version_arn = publish_layer(region)
        create_template_file(region, layer_version_arn)
        deploy_template_with_sam(region)
    deploy_api_on_ec2()
