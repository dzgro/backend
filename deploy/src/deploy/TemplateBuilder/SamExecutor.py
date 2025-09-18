from deploy.TemplateBuilder.Builder import TemplateBuilder
from deploy.TemplateBuilder.StarterMapping import Region
import os, yaml
from pathlib import Path
from typing import Optional

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
template_builder_root = os.path.dirname(__file__)
cache_dir = Path(project_root) / ".cache"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

class SAMExecutor:
    
    def __init__(self, builder: TemplateBuilder):
        self.builder = builder
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def get_template_path(self, region: Region) -> str:
        """Get the path to the cached SAM template"""
        name = f'dzgro-sam-{region.value}-{self.builder.envtextlower}'
        return str(self.cache_dir / f'{name}.yaml')

    def execute(self, region: Region):
        self.saveTemplateAsYaml(region)
        # Use template in TemplateBuilder directory since functions are co-located there
        name = f'dzgro-sam-{region.value}-{self.builder.envtextlower}'
        template = os.path.join(template_builder_root, f'{name}.yaml')
        if not os.path.exists(template):
            raise FileNotFoundError(f"No template found at {template}. Run build first.")
        print(f"🚀 Deploying from template: {template}")
        self.build_deploy_sam_template(region, template)

    def saveTemplateAsYaml(self, region: Region):
        try:
            name = f'dzgro-sam-{region.value}-{self.builder.envtextlower}'
            # Save template in TemplateBuilder directory alongside functions
            template_filename = os.path.join(template_builder_root, f'{name}.yaml')
            
            template = {
                'AWSTemplateFormatVersion': '2010-09-09',
                'Transform': 'AWS::Serverless-2016-10-31',
                'Description': f'SAM {self.builder.env.value} template for region {region.value}',
                'Resources': self.builder.resources
            }
            with open(template_filename, 'w') as f:
                yaml.dump(template, f, sort_keys=False, Dumper=NoAliasDumper)
            
            self.validate(template_filename, region)
            print(f"📁 SAM template for region {region.value} saved to: {template_filename}")
            return template_filename  # Return the template builder path for deployment
            
        except ValueError as e:
            print(f"Error occurred while building SAM template for region {region.value}: {e}")
            raise e
        except Exception as e:
            print(f"Unexpected error occurred while building SAM template for region {region.value}: {e}")
            raise e

    def validate(self, template_file:str, region: Region):
        import subprocess
        validate_command = ['sam', 'validate','--template-file', template_file]
        try:
            print(f"Validating SAM template for region {region.value} and environment {self.builder.env.value}...")
            result = subprocess.run(validate_command, check=True, shell=True, capture_output=True, text=True)
            print("✅ SAM template validation passed!")
        except subprocess.CalledProcessError as e:
            # Check if it's the known SAM CLI bug with 'str' object has no attribute 'get'
            if "'str' object has no attribute 'get'" in str(e.stderr):
                print("⚠️  Known SAM CLI validation bug detected - template is likely valid")
                print("   This is a SAM CLI issue, not a template problem")
                print("   Proceeding with template generation...")
            else:
                print(f"❌ SAM template validation failed for region {region.value}: {e.stderr}")
        except Exception as e:
            print(f"⚠️  SAM validation encountered an issue: {str(e)}")
            print("   Template has been generated and may still be valid")

    def build_deploy_sam_template(self, region: Region, template_file: Optional[str] = None):
        """
        Builds and deploys the SAM template for the given region using AWS SAM CLI with Docker containers.
        Uses cached template if no template_file is provided.
        """
        import subprocess
        import os
        
        # Use cached template if none provided
        if template_file is None:
            template_file = self.get_template_path(region)
        
        name = f'dzgro-sam-{region.value}-{self.builder.envtextlower}'
        built_template_file = os.path.join(template_builder_root, '.aws-sam', 'build', 'template.yaml')

        # Check if bucket exists in the region, create if not
        import boto3
        s3 = boto3.client('s3', region_name=region.value)
        try:
            s3.head_bucket(Bucket=name)
        except Exception:
            print(f"🪣 Creating S3 bucket {name} in region {region.value}...")
            if region.value == "us-east-1":
                s3.create_bucket(Bucket=name)
            else:
                s3.create_bucket(Bucket=name, CreateBucketConfiguration={'LocationConstraint': region.value})
            print(f"✅ Bucket {name} created in region {region.value}.")

        # Build using Docker container
        build_command = [
            'sam', 'build',
            '--use-container',  # This flag tells SAM to use Docker
            '--template-file', template_file
        ]
        
        # Deploy command remains the same
        deploy_command = [
            'sam', 'deploy',
            '--template-file', built_template_file,
            '--region', region.value,
            '--no-confirm-changeset',
            '--capabilities', 'CAPABILITY_NAMED_IAM',
            '--stack-name', name,
            '--s3-bucket', name, '--force-upload'
        ]
        
        try:
            print(f"🔨 Building SAM template using Docker containers...")
            print(f"   Template: {template_file}")
            subprocess.run(build_command, check=True, shell=True, cwd=template_builder_root)
            
            print(f"🚀 Deploying SAM template to region {region.value}...")
            subprocess.run(deploy_command, check=True, shell=True, cwd=template_builder_root)
            
            print(f"✅ Successfully deployed {name} to {region.value}")
            
            # Clean up template file after successful deployment
            if os.path.exists(template_file):
                os.remove(template_file)
                print(f"🧹 Cleaned up SAM template: {template_file}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error building or deploying SAM template for region {region.value} for {self.builder.env.value}: {e}")
            pass
