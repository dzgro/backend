from mapping import LambdaName, LambdaRequirement, Region
from dzgroshared.models.enums import ENVIRONMENT
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..'))

class CustomLambdaLayerBuilder:

    env: ENVIRONMENT
    name: LambdaName
    region: Region
    requirements: list[LambdaRequirement]

    def __init__(self, env: ENVIRONMENT, name: LambdaName, requirements: list[LambdaRequirement], region: Region):
        self.env = env
        self.region = region
        self.envtextlower = env.value.lower()
        self.name = name
        self.requirements = requirements

    def generate_layer_description(self) -> str:
        """Generate a standardized layer description with all dependencies and versions"""
        deps_list = []
        for req in self.requirements:
            deps_list.append(f"{req.name}=={req.version}")
        
        deps_string = ", ".join(sorted(deps_list))
        return f"Dependencies for {self.name.value} in {self.env.value}: {deps_string}"

    def get_layer_name(self) -> str:
        """Generate standardized layer name"""
        return f"{self.name.value.lower()}-deps-{self.envtextlower}"

    def check_existing_layer(self, layer_name: str) -> tuple[str|None, str|None]:
        """Check if layer exists and return latest version ARN and description"""
        import boto3
        
        try:
            client = boto3.client("lambda", region_name=self.region.value)
            
            # Get latest layer version
            response = client.list_layer_versions(
                LayerName=layer_name,
                MaxItems=1
            )
            
            if not response.get('LayerVersions'):
                print(f"No existing layer found: {layer_name}")
                return None, None
            
            latest_layer = response['LayerVersions'][0]
            layer_arn = latest_layer['LayerVersionArn']
            description = latest_layer.get('Description', '')
            
            print(f"Found existing layer: {layer_name}, Version: {latest_layer['Version']}")
            print(f"Existing description: {description}")
            
            return layer_arn, description
            
        except client.exceptions.ResourceNotFoundException:
            print(f"Layer {layer_name} not found")
            return None, None
        except Exception as e:
            print(f"Error checking existing layer {layer_name}: {e}")
            return None, None

    def build_requirements_layer_with_docker(self) -> str|None:
        """Build layer from requirements list using Docker"""
        import subprocess
        
        layer_name = self.get_layer_name()
        
        # Create temporary requirements.txt content
        requirements_content = "\n".join([
            f"{req.name}=={req.version}" for req in self.requirements
            if req.name and req.version
        ])
        
        if not requirements_content:
            print(f"No valid requirements found for {self.name.value}")
            return None
        
        dockerfile_content = f'''
FROM public.ecr.aws/lambda/python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install zip utility
RUN dnf update -y && dnf install -y zip && dnf clean all

# Upgrade pip and build tools
RUN pip install --upgrade pip setuptools wheel

# Create requirements file using echo -e to interpret \\n as newlines
RUN echo -e "{requirements_content.replace(chr(10), chr(92) + "n")}" > /tmp/requirements.txt

# Create layer directory structure
RUN mkdir -p /tmp/layer/python/lib/python3.12/site-packages/

# Install dependencies with verbose output for debugging
RUN pip install --no-cache-dir -r /tmp/requirements.txt -t /tmp/layer/python/lib/python3.12/site-packages/ --verbose

# Create zip file
WORKDIR /tmp/layer
RUN zip -r {layer_name}.zip python/

# List installed packages for verification
RUN echo "Installed packages:" && pip list
RUN echo "Layer contents:" && find python/ -name "*.py" | head -10
'''

        dockerfile_path = os.path.join(os.path.dirname(__file__), f'Dockerfile.{self.name.value}.requirements')

        try:
            # Save Dockerfile
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)

            print(f"Building requirements layer for {self.name.value}...")
            print(f"Requirements: {requirements_content}")
            
            # Build Docker image with verbose output and UTF-8 encoding
            result = subprocess.run([
                'docker', 'build', 
                '-f', dockerfile_path, 
                '-t', f'lambda-requirements-{self.name.value.lower()}', 
                '.'
            ], check=True, cwd=os.path.dirname(__file__), capture_output=True, text=True, encoding='utf-8')
            
            # Print build output for debugging if needed
            if result.stderr:
                print(f"Docker build stderr: {result.stderr}")
            
            # Create container to extract the zip file (with UTF-8 encoding)
            container_id = subprocess.run([
                'docker', 'create', f'lambda-requirements-{self.name.value.lower()}'
            ], capture_output=True, text=True, check=True, encoding='utf-8').stdout.strip()
            
            # Copy zip file from container to host (with UTF-8 encoding)
            layer_zip_path = os.path.join(project_root, f'{layer_name}.zip')
            subprocess.run([
                'docker', 'cp', f'{container_id}:/tmp/layer/{layer_name}.zip', layer_zip_path
            ], check=True, encoding='utf-8')
            
            # Clean up container and dockerfile (with UTF-8 encoding)
            subprocess.run(['docker', 'rm', container_id], check=True, encoding='utf-8')
            os.remove(dockerfile_path)
            
            print(f"✓ Successfully built requirements layer: {layer_zip_path}")
            return layer_zip_path
            
        except subprocess.CalledProcessError as e:
            print(f"Docker build failed for {self.name.value}: {e}")
            print(f"Return code: {e.returncode}")
            if e.stdout:
                print(f"Stdout: {e.stdout}")
            if e.stderr:
                print(f"Stderr: {e.stderr}")
            if os.path.exists(dockerfile_path):
                os.remove(dockerfile_path)
            return None
        except Exception as e:
            print(f"Unexpected error building requirements layer for {self.name.value}: {e}")
            if os.path.exists(dockerfile_path):
                os.remove(dockerfile_path)
            return None

    def deploy_requirements_layer(self, zip_path: str, layer_name: str, description: str) -> str:
        """Deploy requirements layer to AWS Lambda"""
        import boto3
        
        if not os.path.exists(zip_path):
            raise ValueError(f"Zip path does not exist: {zip_path}")

        try:
            client = boto3.client("lambda", region_name=self.region.value)

            print(f"Publishing layer {layer_name}...")
            print(f"Description: {description}")
            
            with open(zip_path, "rb") as f:
                response = client.publish_layer_version(
                    LayerName=layer_name,
                    Description=description,
                    Content={"ZipFile": f.read()},
                    CompatibleRuntimes=["python3.12"],
                    LicenseInfo="MIT"
                )
            
            layer_arn = response["LayerVersionArn"]
            print(f"✓ Published layer ARN: {layer_arn}")
            
            # Clean up zip file
            os.remove(zip_path)
            
            return layer_arn
            
        except Exception as e:
            raise ValueError(f"Failed to deploy requirements layer {layer_name}: {e}")

    def create_or_reuse_requirements_layer(self) -> str:
        """
        Main function to create or reuse layer based on requirements from mapping.py
        
        Args:
            lambda_name: The Lambda function name
            requirements: List of requirements with name and version
            region: AWS region
            
        Returns:
            Layer ARN if successful, None otherwise
        """
        
        layer_name = self.get_layer_name()
        current_description = self.generate_layer_description()
        
        print(f"\n{'='*60}")
        print(f"PROCESSING REQUIREMENTS LAYER FOR {self.name.value}")
        print(f"{'='*60}")
        print(f"Layer name: {layer_name}")
        print(f"Target description: {current_description}")
        
        # Check if layer exists
        existing_arn, existing_description = self.check_existing_layer(layer_name)
        
        if existing_arn and existing_description:
            # Compare descriptions to see if requirements changed
            if existing_description.strip() == current_description.strip():
                print(f"✓ Existing layer matches requirements, reusing: {existing_arn}")
                return existing_arn
            else:
                print(f"⚠️ Requirements changed, rebuilding layer...")
                print(f"Old: {existing_description}")
                print(f"New: {current_description}")
        else:
            print(f"Creating new layer: {layer_name}")
        
        # Build new layer
        zip_path = self.build_requirements_layer_with_docker()
        if not zip_path:
            print(f"Failed to build layer for {self.name.value}")
            raise ValueError("Failed to build layer")

        # Deploy new layer
        layer_arn = self.deploy_requirements_layer(zip_path, layer_name, current_description)
        print(f"✓ Successfully created/updated layer for {self.name.value}")
        return layer_arn
