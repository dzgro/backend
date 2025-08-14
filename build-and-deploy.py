import os
import subprocess
import shutil
import zipfile
import yaml
from pathlib import Path
import hashlib

# Import function mapping
from mapping import FUNCTIONS_MAP, QUEUES_MAP, DEFAULT_REGION

def hash_folder(folder: Path) -> str:
    """Create a SHA256 hash of all files in the folder recursively."""
    sha = hashlib.sha256()
    # Hash all files in the folder recursively
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            sha.update(path.name.encode())
            with path.open("rb") as f:
                while chunk := f.read(8192):
                    sha.update(chunk)
    # Also hash buyproject.toml if present in the folder
    pyproject_file = folder / "pyproject.toml"
    if pyproject_file.exists():
        sha.update(pyproject_file.name.encode())
        with pyproject_file.open("rb") as f:
            while chunk := f.read(8192):
                sha.update(chunk)
    return sha.hexdigest()

ROOT = Path(__file__).parent.resolve()
SHARED_DIR = ROOT / "shared"
FUNCTIONS_DIR = ROOT / "functions"
LAYERS_BUILD_DIR = ROOT / ".build" / "layers"
LAYERS_OUTPUT_DIR = ROOT / ".layers"
                                # "Region": DEFAULT_REGION


LAYERS_BUILD_DIR.mkdir(parents=True, exist_ok=True)
LAYERS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

layer_arns = {}
import json
LAYER_HASH_CACHE_FILE = ROOT / ".layer_hashes.json"
# Load previous hashes
if LAYER_HASH_CACHE_FILE.exists():
    with open(LAYER_HASH_CACHE_FILE) as f:
        layer_hashes = json.load(f)
else:
    layer_hashes = {}
new_layer_hashes = {}

# Build layers
for project_dir in SHARED_DIR.iterdir():
    if not (project_dir / "pyproject.toml").exists():
        continue
    layer_name = project_dir.name
    current_hash = hash_folder(project_dir)
    new_layer_hashes[layer_name] = current_hash
    if layer_hashes.get(layer_name) == current_hash:
        print(f"⚡ Skipping unchanged layer: {layer_name}")
        zip_path = LAYERS_OUTPUT_DIR / f"{layer_name}.zip"
        layer_arns[layer_name] = {
            "LayerName": layer_name,
            "ContentUri": str(zip_path)
        }
        continue
    print(f"🔨 Building layer: {layer_name}")
    build_path = LAYERS_BUILD_DIR / layer_name / "python"
    if build_path.parent.exists():
        shutil.rmtree(build_path.parent)
    build_path.mkdir(parents=True, exist_ok=True)
    req_path = build_path / "requirements.txt"
    subprocess.run([
        "poetry", "export", "-f", "requirements.txt", "--without-hashes", "-o", str(req_path)
    ], cwd=project_dir, check=True)
    # Post-process requirements.txt
    req_lines = req_path.read_text().splitlines()
    new_lines = []
    for line in req_lines:
        if line.startswith("-e "):
            line = line.split(";")[0].strip()
            new_lines.append(line)
        elif "@ file:///" in line:
            pkg, path = line.split("@ file:///")
            new_lines.append(f"-e {path.strip()}")
        else:
            new_lines.append(line)
    req_path.write_text("\n".join(new_lines) + "\n")
    # Install local packages first with --no-deps
    req_lines = req_path.read_text().splitlines()
    local_pkgs = [line for line in req_lines if line.startswith("-e ")]
    other_reqs = [line for line in req_lines if not line.startswith("-e ") and line.strip()]
    for pkg in local_pkgs:
        subprocess.run([
            "pip", "install", "--no-deps", pkg.split("-e ")[1], "-t", str(build_path)
        ], check=True)
    import tempfile
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp_req:
        tmp_req.write("\n".join(other_reqs) + "\n")
        tmp_req_path = tmp_req.name
    subprocess.run([
        "pip", "install", "-r", tmp_req_path, "-t", str(build_path)
    ], check=True)

    # Copy src folder contents into build_path (so custom code is included in layer)
    src_dir = project_dir / "src"
    if src_dir.exists():
        for item in src_dir.iterdir():
            dest = build_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
    zip_path = LAYERS_OUTPUT_DIR / f"{layer_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(build_path):
            for file in files:
                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(build_path.parent)
                zipf.write(abs_path, rel_path)
    print(f"✅ Zipped {layer_name} to {zip_path}")
    hash_file = LAYERS_BUILD_DIR / f"{layer_name}.hash"
    hash_file.write_text(current_hash)
    layer_arns[layer_name] = {
        "LayerName": layer_name,
        "ContentUri": str(zip_path)
    }


# 🧱 Generate SAM Template
print("📝 Generating SAM template.yaml...")
template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Transform": "AWS::Serverless-2016-10-31",
    "Description": "Auto-generated SAM template with layers",
    "Resources": {}
}

# Add SQS queues and DLQs for each region using QUEUES_MAP
for queue_name, queue_info in QUEUES_MAP.items():
    for region in queue_info["region"]:
        main_resource_name = queue_name
        dlq_resource_name = f"{queue_name}DLQ"

        # DLQ properties (unchanged)
        dlq_props = {
            "QueueName": dlq_resource_name,
            "RedriveAllowPolicy": {"redrivePermission": "allowAll"}
        }
        template["Resources"][dlq_resource_name] = {
            "Type": "AWS::SQS::Queue",
            "Properties": dlq_props
        }

        # Main queue properties
        main_props = {
            "QueueName": queue_name,
            "RedriveAllowPolicy": {"redrivePermission": "allowAll"},
            "VisibilityTimeout": 900,
            "RedrivePolicy": {
                "deadLetterTargetArn": f"!GetAtt {dlq_resource_name}.Arn",
                "maxReceiveCount": 1
            }
        }
        # Remove 'function' property if present
        if 'function' in main_props:
            del main_props['function']
        # Remove 'function' from queue_info for template
        queue_info_clean = {k: v for k, v in queue_info.items() if k != 'function'}
        # Add SQS queue resource
        template["Resources"][main_resource_name] = {
            "Type": "AWS::SQS::Queue",
            "Properties": main_props
        }

        # If 'function' property exists, add event source mapping to trigger Lambda
        if 'function' in queue_info:
            function_name = queue_info['function']
            # Find the logical resource name for the function
            func_name = function_name.replace('_',' ').title().replace(' ', '')
            event_source_mapping_name = f"{main_resource_name}To{func_name}Event"
            template["Resources"][event_source_mapping_name] = {
                "Type": "AWS::Lambda::EventSourceMapping",
                "Properties": {
                    "EventSourceArn": f"!GetAtt {main_resource_name}.Arn",
                    "FunctionName": f"!Ref {func_name}Function",
                    "Enabled": True,
                    "BatchSize": 1
                }
            }
# Deploy each function in all regions specified in FUNCTIONS_MAP
for func_key, func_info in FUNCTIONS_MAP.items():
    func_name = func_key.replace('_',' ').title().replace(' ', '')
    src_path = Path(func_info['path']) / "src"
    pyproject_path = Path(func_info['path']) / "pyproject.toml"
    requirements_path = Path(func_info['path']) / "src"
        # Skip requirements.txt generation for shared modules
    if func_info['path'].startswith('shared/'):
        continue
    # Ensure requirements.txt is created from pyproject.toml using poetry
    if pyproject_path.exists():
        result = subprocess.run([
            "poetry", "export", "-f", "requirements.txt", "--without-hashes", "--without-urls","--without","dev", "-o", "requirements.txt"
        ], cwd=requirements_path)
        if result.returncode != 0:
            print(f"ERROR: Poetry export failed for {func_info['path']}. Please check pyproject.toml and run 'poetry install' in that folder.")
            continue
    else:
        print(f"ERROR: pyproject.toml not found in {func_info['path']}. Skipping requirements.txt export.")
        continue
    regions = func_info['region']

    # Removed unused build_codeuri_abs and related code

    # Read local dependencies
    pyproject_path = Path(func_info['path']) / "pyproject.toml"
    if not pyproject_path.exists():
        continue
    pyproject = pyproject_path.read_text()
    deps = []
    for shared_name in layer_arns:
        if f'path = "../../shared/{shared_name}"' in pyproject or f'path = "../{shared_name}"' in pyproject:
            deps.append(layer_arns[shared_name]["LayerName"])

    for region in regions:
        if region == "ap-south-1":
            for bucket in ['dzgro-reports', 'dzgro','dzgro-invoices', 'dzgro-cloudfront']:
                template["Resources"][f"{bucket.replace('-', ' ').title().replace(' ', '')}Bucket"] = {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "BucketName": bucket
                    }
        }
        layers_refs = [f"!Ref {name.replace('_', '')}Layer" for name in deps] if deps else []
        template["Resources"][f'{func_name}Function'] = {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                "FunctionName": f'{func_name}',
                "CodeUri": str(src_path),
                "Handler": f"{func_key}.handler.handler",
                "Runtime": "python3.12",
                "Timeout": 900,
                "Layers": layers_refs,
                "Region": region,
                "Role": "arn:aws:iam::522814698847:role/Lambda_Execution",
                "Architectures": ["x86_64"],
            }
        }

# Add layer resources
for layer_name, info in layer_arns.items():
    logical_id = f"{layer_name}Layer".replace('_', '')
    template["Resources"][logical_id] = {
        "Type": "AWS::Serverless::LayerVersion",
        "Properties": {
            "LayerName": layer_name,
            "ContentUri": info["ContentUri"],
            "CompatibleRuntimes": ["python3.12"]
        }
    }




# --- Multi-region template generation ---
def filter_resources_by_region(resources, region):
    filtered = {}
    for k, res in resources.items():
        # Filter main queues
        if k in QUEUES_MAP:
            if region not in QUEUES_MAP[k]['region']:
                # Region not present for this queue, skip adding to filtered
                continue
        # Filter DLQs (dynamically generated as {queue_name}DLQ)
        elif k.endswith('DLQ'):
            main_queue_name = k[:-3]  # Remove 'DLQ' suffix
            if main_queue_name in QUEUES_MAP:
                if region not in QUEUES_MAP[main_queue_name]['region']:
                    continue
        # Filter functions
        if k.endswith('Function'):
            # Extract function name from resource name
            for func_name, func_info in FUNCTIONS_MAP.items():
                # Logical ID pattern: Function{FuncName}{Region}
                func_name = func_name.replace('_',' ').title().replace(' ', '')
                func_logical_id = f"Function{func_name}"
                if k == func_logical_id and region not in func_info['region']:
                    break
            else:
                # If not found in FUNCTIONS_MAP, keep (could be a layer)
                filtered[k] = res
                continue
            continue
        filtered[k] = res
    return filtered

# Collect all regions from functions and queues
all_regions = set()
for func_info in FUNCTIONS_MAP.values():
    for region in func_info["region"]:
        all_regions.add(region)
for queue_info in QUEUES_MAP.values():
    for region in queue_info["region"]:
        all_regions.add(region)

for region in all_regions:
    import copy
    region_template = copy.deepcopy(template)
    # Remove Region property from all resources
    for res in region_template["Resources"].values():
        props = res.get("Properties", {})
        if "Region" in props:
            del props["Region"]
    # Filter resources by region
    region_template["Resources"] = filter_resources_by_region(region_template["Resources"], region)

    # Only keep layer resources that are referenced by Lambda functions in this region
    used_layers = set()
    for res in region_template["Resources"].values():
        if res["Type"] == "AWS::Serverless::Function":
            for layer_ref in res["Properties"].get("Layers", []):
                # Layer logical id is after !Ref and ends with Layer
                if isinstance(layer_ref, str) and layer_ref.startswith("!Ref "):
                    logical_id = layer_ref.split()[1]
                    used_layers.add(logical_id)
    # Remove unused layer resources
    layer_keys = [k for k, v in region_template["Resources"].items() if v["Type"] == "AWS::Serverless::LayerVersion"]
    for k in layer_keys:
        if k not in used_layers:
            del region_template["Resources"][k]

    region_template_path = ROOT / f"template-{region}.yaml"
        # Remove all single quotes from region_template before dumping
    import re
    region_template_str = yaml.dump(region_template, sort_keys=False)
    region_template_str = re.sub("'", "", region_template_str)
    with open(region_template_path, "w") as f:
        f.write(region_template_str)
    print(f"✅ Generated template for region: {region} -> {region_template_path}")

with open(LAYER_HASH_CACHE_FILE, "w") as f:
    json.dump(new_layer_hashes, f, indent=2)

print("\n🚀 To build & deploy all regions:")
print("   python deploy-all-regions.py")