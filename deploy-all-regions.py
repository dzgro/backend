import subprocess
import sys
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

def get_region_templates():
    return [f for f in ROOT.glob("template-*.yaml")]

def main():
    # Clean up previous build artifacts and layers at the start
    print("🧹 Cleaning up previous build artifacts...")
    
    # Remove .aws-sam build directory
    aws_sam_build_dir = ROOT / ".aws-sam"
    if aws_sam_build_dir.exists():
        shutil.rmtree(aws_sam_build_dir)
        print(f"   ✅ Removed {aws_sam_build_dir}")
    
    # Remove .build layers directory
    build_layers_dir = ROOT / ".build"
    if build_layers_dir.exists():
        shutil.rmtree(build_layers_dir)
        print(f"   ✅ Removed {build_layers_dir}")
    
    # Remove .layers directory
    layers_dir = ROOT / ".layers"
    if layers_dir.exists():
        shutil.rmtree(layers_dir)
        print(f"   ✅ Removed {layers_dir}")
    
    # Remove layer hashes JSON file
    layer_hashes_file = ROOT / ".layer_hashes.json"
    if layer_hashes_file.exists():
        layer_hashes_file.unlink()
        print(f"   ✅ Removed {layer_hashes_file}")
    
    print("🧹 Cleanup completed!\n")
    
    # subprocess.run(["python", "freezedependencies.py"], check=True, shell=True)
    subprocess.run(["python", "build-and-deploy.py"], check=True, shell=True)
    templates = get_region_templates()
    # Step 2: For each region, prompt to build, then immediately prompt to deploy
    for tpl in templates:
        region = tpl.stem.split("template-")[1]
        confirm_build_region = input(f"Build SAM artifact for region '{region}'? [y/N]: ").strip().lower()
        if confirm_build_region != 'y':
            print(f"Skipped build for region: {region}")
            continue
        print(f"\n=== Building for region: {region} ===")
        build_cmd = ["sam", "build", "--template", str(tpl)]
        subprocess.run(build_cmd, check=True, shell=True)
        
        confirm_deploy_region = input(f"Deploy SAM artifact for region '{region}'? [y/N]: ").strip().lower()
        if confirm_deploy_region != 'y':
            print(f"Skipped deployment for region: {region}")
            continue
        print(f"\n=== Deploying for region: {region} ===")
        
        # Change to build directory and deploy using the built template which includes properly packaged dependencies
        build_dir = ROOT / ".aws-sam" / "build"
        deploy_cmd = ["sam", "deploy", "--template-file", "template.yaml", '--s3-bucket', f"dzgro-sam", '--stack-name', f"dzgro-sam-{region}", '--no-confirm-changeset', '--region', region, '--force-upload']
        try:
            result = subprocess.run(deploy_cmd, check=True, shell=True, cwd=str(build_dir))
        except subprocess.CalledProcessError as e:
            print(f"Error deploying to region {region}: {e}")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            sys.exit(1)

main()