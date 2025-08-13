import subprocess
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).parent.resolve()

# Directory for built templates
BUILT_TEMPLATE_DIR = ROOT / ".aws-sam" / "build"
BUILT_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

def get_region_templates():
    return [f for f in ROOT.glob("template-*.yaml")]

def main():
    # Step 1: Confirm before building templates
    confirm_templates = input("Regenerate region templates with build-and-deploy.py? [y/N]: ").strip().lower()
    if confirm_templates != 'y':
        print("Aborted template generation.")
        return
    subprocess.run(["python", "build-and-deploy.py"], check=True, shell=True)
    # Step 2: Confirm before building SAM artifacts
    confirm_build = input("Build all region SAM artifacts? [y/N]: ").strip().lower()
    if confirm_build != 'y':
        print("Aborted build.")
        return
    templates = get_region_templates()
    # Step 2: For each region, prompt to build, then immediately prompt to deploy
    templates = get_region_templates()
    for tpl in templates:
        region = tpl.stem.split("template-")[1]
        confirm_build_region = input(f"Build SAM artifact for region '{region}'? [y/N]: ").strip().lower()
        if confirm_build_region != 'y':
            print(f"Skipped build for region: {region}")
            continue
        print(f"\n=== Building for region: {region} ===")
        build_cmd = ["sam", "build", "--template", str(tpl)]
        subprocess.run(build_cmd, check=True, shell=True)
        # Copy template file to built template directory for deployment
        built_template_path = BUILT_TEMPLATE_DIR / f"template-{region}.yaml"
        shutil.copy2(tpl, built_template_path)
        confirm_deploy_region = input(f"Deploy to region '{region}'? [y/N]: ").strip().lower()
        if confirm_deploy_region != 'y':
            print(f"Skipped deployment for region: {region}")
            continue
        print(f"\n=== Deploying for region: {region} ===")
        deploy_cmd = ["sam", "deploy", "--template-file", str(built_template_path), "--region", region, "--guided"]
        subprocess.run(deploy_cmd, check=True, shell=True)

main()