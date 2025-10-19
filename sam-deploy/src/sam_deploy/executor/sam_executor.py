from sam_deploy.builder.template_builder import TemplateBuilder
from sam_deploy.config.mapping import Region
from sam_deploy.utils import docker_manager
import os, yaml, json, hashlib
from pathlib import Path
from typing import Optional, Tuple

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
template_builder_root = os.path.join(os.path.dirname(__file__), '..')
cache_dir = Path(project_root) / ".cache"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

class SAMExecutor:

    def __init__(self, builder: TemplateBuilder):
        self.builder = builder
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.hash_cache_file = self.cache_dir / "dependency_hashes.json"

    def _load_template_hashes(self) -> dict:
        """Load cached template hashes from disk (same file as layer hashes)"""
        try:
            if self.hash_cache_file.exists():
                with open(self.hash_cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load template hashes: {e}")
        return {}

    def _save_template_hashes(self, hashes: dict):
        """Save template hashes to disk (same file as layer hashes)"""
        try:
            with open(self.hash_cache_file, 'w') as f:
                json.dump(hashes, f, indent=2)
        except Exception as e:
            print(f"[WARNING] Could not save template hashes: {e}")

    def generate_template_hash(self, template_dict: dict) -> str:
        """Generate SHA256 hash of template for change detection"""
        # Convert template to canonical JSON string (sorted keys)
        template_json = json.dumps(template_dict, sort_keys=True)
        return hashlib.sha256(template_json.encode()).hexdigest()

    def get_template_cache_key(self, deployment_type: str, region: Region) -> str:
        """
        Generate cache key for template hashing.

        Args:
            deployment_type: 'core' or 'ams'
            region: AWS region

        Returns:
            Cache key like 'template-core' or 'template-ams-eu-west-1'
        """
        if deployment_type == 'core':
            return f"template-core-{region.value}"
        else:  # ams
            return f"template-ams-{region.value}"

    def has_template_changed(self, template_dict: dict, deployment_type: str, region: Region) -> Tuple[bool, str]:
        """
        Check if template has changed since last deployment.

        Args:
            template_dict: The SAM template dictionary
            deployment_type: 'core' or 'ams'
            region: AWS region

        Returns:
            (has_changed, current_hash)
        """
        current_hash = self.generate_template_hash(template_dict)
        cache_key = self.get_template_cache_key(deployment_type, region)

        # Load existing hashes
        all_hashes = self._load_template_hashes()
        stored_hash = all_hashes.get(cache_key)

        has_changed = stored_hash != current_hash

        return has_changed, current_hash

    def update_template_hash(self, template_dict: dict, deployment_type: str, region: Region):
        """
        Update stored template hash after successful deployment.

        Args:
            template_dict: The SAM template dictionary
            deployment_type: 'core' or 'ams'
            region: AWS region
        """
        current_hash = self.generate_template_hash(template_dict)
        cache_key = self.get_template_cache_key(deployment_type, region)

        # Load existing hashes, update, and save
        all_hashes = self._load_template_hashes()
        all_hashes[cache_key] = current_hash
        self._save_template_hashes(all_hashes)

        print(f"[CACHE] Updated template hash for {cache_key}: {current_hash[:8]}...")

    def get_template_name(self) -> str:
        """Get the name of the cached SAM template (no environment suffix - single stack)"""
        return 'dzgro-sam'

    def get_sam_bucket_name(self, region: Region) -> str:
        """
        Get the S3 bucket name for SAM deployments in the specified region.

        S3 bucket names must be globally unique, so we include the region in the name.

        Args:
            region: AWS region

        Returns:
            Bucket name like 'dzgro-sam-ap-south-1'
        """
        # S3 bucket names must be globally unique, so include region
        return f"dzgro-sam-{region.value}"

    def create_sam_bucket(self, region: Region) -> None:
        """
        Create S3 bucket for SAM deployment artifacts in the specified region.

        Args:
            region: AWS region to create bucket in
        """
        import boto3
        from botocore.exceptions import ClientError

        bucket_name = self.get_sam_bucket_name(region)
        s3_client = boto3.client('s3', region_name=region.value)

        try:
            # Check if bucket already exists
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                print(f"[OK] SAM deployment bucket '{bucket_name}' already exists in {region.value}")
                return
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    # Bucket doesn't exist, create it
                    pass
                elif error_code == '403':
                    # Bucket exists but we don't have access
                    raise Exception(f"[ERROR] Bucket '{bucket_name}' exists but access is forbidden")
                else:
                    raise

            # Create bucket
            print(f"[CREATE] Creating SAM deployment bucket '{bucket_name}' in {region.value}...")

            if region.value == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                # Other regions need LocationConstraint
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region.value}
                )

            # Enable versioning for better artifact management
            s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )

            # Add lifecycle policy to clean up old artifacts (optional but recommended)
            s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={
                    'Rules': [
                        {
                            'ID': 'DeleteOldArtifacts',  # Must be uppercase ID, not Id
                            'Status': 'Enabled',
                            'Filter': {'Prefix': ''},  # Use Filter instead of Prefix
                            'NoncurrentVersionExpiration': {'NoncurrentDays': 30},
                            'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 7}
                        }
                    ]
                }
            )

            print(f"[OK] Created SAM deployment bucket '{bucket_name}' in {region.value}")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyOwnedByYou':
                print(f"[OK] SAM deployment bucket '{bucket_name}' already exists and is owned by you")
            elif error_code == 'BucketAlreadyExists':
                raise Exception(f"[ERROR] Bucket '{bucket_name}' already exists and is owned by someone else")
            else:
                raise Exception(f"[ERROR] Failed to create bucket '{bucket_name}': {e}")

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
                'UPDATE_ROLLBACK_COMPLETE'
            ]

            # Statuses that require stack deletion before redeployment
            delete_required_statuses = [
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
                print(f"[OK] Stack {stack_name} is in {stack_status} state - ready for deployment")
            elif stack_status in delete_required_statuses:
                print(f"[WARN] Stack {stack_name} is in {stack_status} state - deleting stack before redeployment...")
                cfn.delete_stack(StackName=stack_name)
                print(f"[INFO] Waiting for stack deletion to complete...")
                waiter = cfn.get_waiter('stack_delete_complete')
                waiter.wait(StackName=stack_name)
                print(f"[OK] Stack {stack_name} deleted successfully - will create new stack")
            elif stack_status in in_progress_statuses:
                raise Exception(f"[ERROR] Stack {stack_name} is in {stack_status} state. Wait for current operation to complete before deploying.")
            elif stack_status in failed_statuses:
                raise Exception(f"[ERROR] Stack {stack_name} is in {stack_status} state. Manual intervention required before deploying.")
            else:
                raise Exception(f"[ERROR] Stack {stack_name} is in unexpected state: {stack_status}")

        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError' and 'does not exist' in str(e):
                print(f"[INFO] Stack {stack_name} does not exist - will create new stack")
            else:
                raise Exception(f"[ERROR] Error checking stack status: {str(e)}")

    def get_template_path(self) -> str:
        """Get the path to the cached SAM template"""
        name = self.get_template_name()
        return os.path.join(template_builder_root, f'{name}.yaml')

    def execute(self, region: Region):
        print(f"[DEPLOY] Deploying from template: {self.get_template_path()}")
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
            print(f"[INFO] SAM template for region {region.value} saved to: {template_filename}")
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
            print("[OK] SAM template validation passed!")
        except subprocess.CalledProcessError as e:
            # Check if it's the known SAM CLI bug with 'str' object has no attribute 'get'
            if "'str' object has no attribute 'get'" in str(e.stderr):
                print("[WARNING] Known SAM CLI validation bug detected - template is likely valid")
                print("   This is a SAM CLI issue, not a template problem")
                print("   Proceeding with template generation...")
            else:
                print(f"[ERROR] SAM template validation failed for region {region.value}: {e.stderr}")
            raise e
        except Exception as e:
            print(f"[WARNING] SAM validation encountered an issue: {str(e)}")
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

        result = subprocess.run(wsl_command, capture_output=True, text=True)

        # Print output for debugging
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=__import__('sys').stderr)

        # Check for errors
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, wsl_command, result.stdout, result.stderr)

        return result

    def build_deploy_sam_template(self, region: Region):
        import subprocess
        import os
        template_file = self.get_template_path()
        name = self.get_template_name()
        bucket_name = self.get_sam_bucket_name(region)
        built_template_file = os.path.join(template_builder_root, '.aws-sam', 'build', 'template.yaml')

        # Note: Docker daemon must be running in WSL (started by docker_manager.start_ubuntu_docker())
        # SAM CLI runs through WSL to access the WSL Docker daemon

        # Create S3 bucket for SAM deployment artifacts
        print(f"[S3] Ensuring SAM deployment bucket exists in {region.value}...")
        self.create_sam_bucket(region)

        # Check CloudFormation stack status before proceeding
        self.check_stack_status(region)

        # Build using Docker container through WSL
        build_args = [
            'build',
            '--use-container',  # This flag tells SAM to use Docker
            '--template-file', template_file
        ]

        # Deploy command with specific S3 bucket
        deploy_args = [
            'deploy',
            '--template-file', built_template_file,
            '--region', region.value,
            '--no-confirm-changeset',
            '--capabilities', 'CAPABILITY_NAMED_IAM',
            '--stack-name', name,
            '--s3-bucket', bucket_name  # Use our dedicated SAM bucket
        ]

        try:
            print(f"[BUILD] Building SAM template using Docker containers (via WSL)...")
            print(f"   Template: {template_file}")
            self.run_sam_in_wsl(build_args, template_builder_root)

            print(f"[DEPLOY] Deploying SAM template to region {region.value} (via WSL)...")
            print(f"   S3 Bucket: {bucket_name}")
            self.run_sam_in_wsl(deploy_args, template_builder_root)

            print(f"[OK] Successfully deployed {name} to {region.value}")

            # Clean up template file after successful deployment
            if os.path.exists(template_file):
                os.remove(template_file)
                print(f"[CLEANUP] Cleaned up SAM template: {template_file}")

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error building or deploying SAM template for region {region.value} for {self.builder.env.value}: {e}")
            raise e
