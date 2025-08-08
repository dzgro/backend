import os
import subprocess
import shutil
import zipfile
import yaml
from pathlib import Path

import hashlib

def hash_folder(folder: Path) -> str:
    """Create a SHA256 hash of all files in the folder recursively."""
    sha = hashlib.sha256()
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            sha.update(path.name.encode())
            with path.open("rb") as f:
                while chunk := f.read(8192):
                    sha.update(chunk)
    return sha.hexdigest()

ROOT = Path(__file__).parent.resolve()
SHARED_DIR = ROOT / "shared"
FUNCTIONS_DIR = ROOT / "functions"
LAYERS_BUILD_DIR = ROOT / ".build" / "layers"
LAYERS_OUTPUT_DIR = ROOT / ".layers"
TEMPLATE_YAML = ROOT / "template.yaml"

# Clean previous builds
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

for project_dir in SHARED_DIR.iterdir():
    if not (project_dir / "pyproject.toml").exists():
        continue

    layer_name = project_dir.name
    current_hash = hash_folder(project_dir)
    new_layer_hashes[layer_name] = current_hash

    if layer_hashes.get(layer_name) == current_hash:
        print(f"⚡ Skipping unchanged layer: {layer_name}")
        # Still register layer ARN for template output
        zip_path = LAYERS_OUTPUT_DIR / f"{layer_name}.zip"
        layer_arns[layer_name] = {
            "LayerName": layer_name,
            "ContentUri": str(zip_path)
        }
        continue

    print(f"📦 Building layer: {layer_name}")
    ...
    # (keep rest of your layer-building code unchanged)

print("🔧 Building layers from shared projects...")

for project_dir in SHARED_DIR.iterdir():
    if not (project_dir / "pyproject.toml").exists():
        continue

    layer_name = project_dir.name
    print(f"\n📦 Processing layer: {layer_name}")

    # Hash project to detect changes
    current_hash = hash_folder(project_dir)
    hash_file = LAYERS_BUILD_DIR / f"{layer_name}.hash"

    if hash_file.exists() and hash_file.read_text() == current_hash:
        print(f"⏭️ Skipping unchanged layer: {layer_name}")
        # Reuse existing zip if present
        zip_path = LAYERS_OUTPUT_DIR / f"{layer_name}.zip"
        if not zip_path.exists():
            print(f"⚠️ Zip file missing for {layer_name}, forcing rebuild.")
        else:
            layer_arns[layer_name] = {
                "LayerName": layer_name,
                "ContentUri": str(zip_path)
            }
            continue  # ✅ Skip to next layer

    print(f"🔨 Building layer: {layer_name}")

    # Clean previous build for this layer only
    build_path = LAYERS_BUILD_DIR / layer_name / "python"
    if build_path.parent.exists():
        shutil.rmtree(build_path.parent)

    build_path.mkdir(parents=True, exist_ok=True)

    # Export dependencies
    req_path = build_path / "requirements.txt"
    subprocess.run(
        ["poetry", "export", "-f", "requirements.txt", "--without-hashes", "-o", str(req_path)],
        cwd=project_dir,
        check=True,
    )

    subprocess.run(
        ["pip", "install", "-r", str(req_path), "-t", str(build_path)],
        check=True,
    )

    # Zip using zipfile
    zip_path = LAYERS_OUTPUT_DIR / f"{layer_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(build_path):
            for file in files:
                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(build_path.parent)
                zipf.write(abs_path, rel_path)

    print(f"✅ Zipped {layer_name} to {zip_path}")

    # Save hash
    hash_file.write_text(current_hash)

    # Store ARN reference
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
    "Resources": {
        "RazorpayWebhookDLQ": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "QueueName": "RazorpayWebhookDLQ",
                "RedriveAllowPolicy": {
                    "redrivePermission": "allowAll"
                }
            }
        },
        "RazorpayWebhook": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "QueueName": "RazorpayWebhook",
                "VisibilityTimeout": 900,
                "RedrivePolicy": {
                    "deadLetterTargetArn": "!GetAtt RazorpayWebhookDLQ.Arn",
                    "maxReceiveCount": 1
                }
            }
        },
        "NewUserDLQ": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "QueueName": "NewUserDLQ",
                "RedriveAllowPolicy": {
                    "redrivePermission": "allowAll"
                }
            }
        },
        "NewUser": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "QueueName": "NewUser",
                "VisibilityTimeout": 900,
                "RedrivePolicy": {
                    "deadLetterTargetArn": "!GetAtt NewUserDLQ.Arn",
                    "maxReceiveCount": 1
                }
            }
        },
        "AmazonReportsDLQ": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "QueueName": "AmazonReportsDLQ",
                "RedriveAllowPolicy": {
                    "redrivePermission": "allowAll"
                }
            }
        },
        "AmazonReports": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "QueueName": "AmazonReports",
                "VisibilityTimeout": 900,
                "RedrivePolicy": {
                    "deadLetterTargetArn": "!GetAtt AmazonReportsDLQ.Arn",
                    "maxReceiveCount": 1
                }
            }
        }
    }
}

for func_dir in FUNCTIONS_DIR.iterdir():
    if not (func_dir / "pyproject.toml").exists():
        continue

    func_name = func_dir.name.replace('_',' ').title().replace(' ', '')
    src_path = func_dir / "src"

    # Read local dependencies
    pyproject = (func_dir / "pyproject.toml").read_text()
    deps = []
    for shared_name in layer_arns:
        if f'path = "../../shared/{shared_name}"' in pyproject or f'path = "../{shared_name}"' in pyproject:
            deps.append(layer_arns[shared_name]["LayerName"])

    template["Resources"][f"Function{func_name}"] = {
        "Type": "AWS::Serverless::Function",
        "Properties": {
            "FunctionName": func_name,
            "CodeUri": str(src_path),
            "Handler": f"{func_name}.handler.handler",
            "Runtime": "python3.12",
            "Timeout": 10,
            "Layers": [f"!Ref {name}Layer" for name in deps] if deps else [],
        }
    }

# Add layer resources
for layer_name, info in layer_arns.items():
    template["Resources"][f"{layer_name}Layer"] = {
        "Type": "AWS::Serverless::LayerVersion",
        "Properties": {
            "LayerName": layer_name,
            "ContentUri": info["ContentUri"],
            "CompatibleRuntimes": ["python3.12"]
        }
    }



# Write template.yaml
with open(TEMPLATE_YAML, "w") as f:
    yaml.dump(template, f, sort_keys=False)

with open(LAYER_HASH_CACHE_FILE, "w") as f:
    json.dump(new_layer_hashes, f, indent=2)

print("✅ SAM template.yaml generated.")

# ⛳ Final instructions
print("\n🚀 To build & deploy:")
print("   sam build && sam deploy --guided")