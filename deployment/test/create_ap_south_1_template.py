import yaml
from mapping import FUNCTIONS_MAP

region = "ap-south-1"
layer_version_arn = "arn:aws:lambda:ap-south-1:123456789012:layer:dzgroshared-layer:1"  # Example ARN

template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": f"SAM template for region {region}",
    "Resources": {}
}

for func_name, config in FUNCTIONS_MAP.items():
    if region in config.get("region", []):
        template["Resources"][func_name] = {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                "Handler": "handler.handler",
                "Runtime": "python3.12",
                "Architectures": ["x86_64"],
                "CodeUri": config["path"],
                "Description": config.get("description", ""),
                "Timeout": 900,
                "Layers": [layer_version_arn]
            }
        }

with open("d:\github\sam-app\deployment\test\template-ap-south-1.yaml", "w") as f:
    yaml.dump(template, f, sort_keys=False)

print("Test SAM template for ap-south-1 created at deployment/test/template-ap-south-1.yaml")
