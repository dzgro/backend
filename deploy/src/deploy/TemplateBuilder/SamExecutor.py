from deploy.TemplateBuilder.Builder import TemplateBuilder
from deploy.TemplateBuilder.StarterMapping import Region
from deploy.TemplateBuilder import docker_manager
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

    def get_template_name(self) -> str:
        """Get the name of the cached SAM template"""
        return f'dzgro-sam-{self.builder.envtextlower}'

    def check_stack_status(self, region: Region) -> None:
        """Check if CloudFormation stack is in a valid state for deployment"""
        import boto3
        from botocore.exceptions import ClientError

        stack_name = self.get_template_name()
        cfn = boto3.client('cloudformation', region_name=region.value)

        try:
            response = cfn.describe_stacks(StackName=stack_name)
            stack_status = response['Stacks'][0]['StackStatus']

            # Statuses that are OK for deployment
            deployable_statuses = [
                'CREATE_COMPLETE',
                'UPDATE_COMPLETE',
                'UPDATE_ROLLBACK_COMPLETE',
                'ROLLBACK_COMPLETE'
            ]

            # Statuses that indicate stack is in transition
            in_progress_statuses = [
                'CREATE_IN_PROGRESS',
                'UPDATE_IN_PROGRESS',
                'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
                'UPDATE_ROLLBACK_IN_PROGRESS',
                'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
                'DELETE_IN_PROGRESS',
                'REVIEW_IN_PROGRESS'
            ]

            # Failed statuses
            failed_statuses = [
                'CREATE_FAILED',
                'DELETE_FAILED',
                'UPDATE_FAILED'
            ]

            if stack_status in deployable_statuses:
                print(f"✅ Stack {stack_name} is in {stack_status} state - ready for deployment")
            elif stack_status in in_progress_statuses:
                raise Exception(f"❌ Stack {stack_name} is in {stack_status} state. Wait for current operation to complete before deploying.")
            elif stack_status in failed_statuses:
                raise Exception(f"❌ Stack {stack_name} is in {stack_status} state. Manual intervention required before deploying.")
            else:
                raise Exception(f"❌ Stack {stack_name} is in unexpected state: {stack_status}")

        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError' and 'does not exist' in str(e):
                print(f"ℹ️  Stack {stack_name} does not exist - will create new stack")
            else:
                raise Exception(f"❌ Error checking stack status: {str(e)}")

    def get_template_path(self) -> str:
        """Get the path to the cached SAM template"""
        name = self.get_template_name()
        return os.path.join(template_builder_root, f'{name}.yaml')

    def execute(self, region: Region):
        print(f"🚀 Deploying from template: {self.get_template_path()}")
        self.build_deploy_sam_template(region)

    def saveTemplateAsYaml(self, region: Region):
        try:
            # Save template in TemplateBuilder directory alongside functions
            name = self.get_template_name()
            template_filename = self.get_template_path()
            
            template = {
                'AWSTemplateFormatVersion': '2010-09-09',
                'Transform': 'AWS::Serverless-2016-10-31',
                'Description': f'SAM {self.builder.env.value} template',
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
            raise e
        except Exception as e:
            print(f"⚠️  SAM validation encountered an issue: {str(e)}")
            print("   Template has been generated and may still be valid")
            raise e

    def run_sam_in_wsl(self, sam_args, cwd, distro="Ubuntu", user="dzgro"):
        """
        Run SAM CLI command through WSL to access WSL Docker daemon

        Args:
            sam_args: List of SAM command arguments (e.g., ['build', '--use-container', ...])
            cwd: Working directory (Windows path, will be converted to WSL path)
            distro: WSL distribution name
            user: WSL username

        Returns:
            subprocess.CompletedProcess result
        """
        import subprocess

        # Convert Windows paths in arguments to WSL paths
        converted_args = []
        for arg in sam_args:
            # Check if this looks like a Windows path
            if len(arg) > 2 and arg[1] == ':' and arg[0].isalpha():
                converted_args.append(docker_manager.convert_windows_path_to_wsl(arg))
            else:
                converted_args.append(arg)

        # Convert working directory to WSL path
        wsl_cwd = docker_manager.convert_windows_path_to_wsl(cwd)

        # Build the command: wsl -d Ubuntu -u dzgro bash -c "cd /path && sam ..."
        sam_command = " ".join(converted_args)
        bash_command = f"cd {wsl_cwd} && sam {sam_command}"

        wsl_command = [
            "wsl", "-d", distro, "-u", user, "--exec", "bash", "-c", bash_command
        ]

        return subprocess.run(wsl_command, check=True)

    def build_deploy_sam_template(self, region: Region):
        import subprocess
        import os
        template_file = self.get_template_path()
        name = self.get_template_name()
        built_template_file = os.path.join(template_builder_root, '.aws-sam', 'build', 'template.yaml')

        # Note: Docker daemon must be running in WSL (started by docker_manager.start_ubuntu_docker())
        # SAM CLI runs through WSL to access the WSL Docker daemon

        # Check CloudFormation stack status before proceeding
        self.check_stack_status(region)

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

        # Build using Docker container through WSL
        build_args = [
            'build',
            '--use-container',  # This flag tells SAM to use Docker
            '--template-file', template_file
        ]

        # Deploy command
        deploy_args = [
            'deploy',
            '--template-file', built_template_file,
            '--region', region.value,
            '--no-confirm-changeset',
            '--capabilities', 'CAPABILITY_NAMED_IAM',
            '--stack-name', name,
            '--s3-bucket', name,
            '--force-upload'
        ]

        try:
            print(f"🔨 Building SAM template using Docker containers (via WSL)...")
            print(f"   Template: {template_file}")
            self.run_sam_in_wsl(build_args, template_builder_root)

            print(f"🚀 Deploying SAM template to region {region.value} (via WSL)...")
            self.run_sam_in_wsl(deploy_args, template_builder_root)

            print(f"✅ Successfully deployed {name} to {region.value}")

            # Clean up template file after successful deployment
            if os.path.exists(template_file):
                os.remove(template_file)
                print(f"🧹 Cleaned up SAM template: {template_file}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Error building or deploying SAM template for region {region.value} for {self.builder.env.value}: {e}")
            raise e
