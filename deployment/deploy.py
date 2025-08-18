def build_layer_zip_clean():
	"""
	Creates dzgroshared_layer.zip at the project root with all dependencies and custom code.
	This creates a proper AWS Lambda layer structure with dependencies in python/lib/python3.12/site-packages/
	"""
	import os
	import shutil
	import zipfile
	import subprocess
	
	# Paths
	project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
	dzgroshared_dir = os.path.join(project_root, 'dzgroshared')
	layer_build_dir = os.path.join(os.path.dirname(__file__), 'layer_build')
	python_dir = os.path.join(layer_build_dir, 'python')
	site_packages_dir = os.path.join(python_dir, 'lib', 'python3.12', 'site-packages')
	layer_zip = os.path.join(project_root, 'dzgroshared_layer.zip')

	print("Building Lambda layer with dependencies...")
	
	# Clean up previous build
	if os.path.exists(layer_build_dir):
		shutil.rmtree(layer_build_dir)
	
	# Create layer directory structure
	os.makedirs(site_packages_dir, exist_ok=True)
	
	try:
		# Step 1: Install dependencies using pip from the dzgroshared project
		print("Installing dependencies...")
		pip_install_cmd = [
			'pip', 'install', '--target', site_packages_dir,
			'--no-deps',  # Don't install sub-dependencies to avoid conflicts
			dzgroshared_dir
		]
		subprocess.run(pip_install_cmd, check=True, cwd=project_root)
		
		# Step 2: Install dependencies listed in pyproject.toml with specified versions
		print("Installing project dependencies...")
		import toml
		pyproject_path = os.path.join(dzgroshared_dir, 'pyproject.toml')
		pyproject = toml.load(pyproject_path)
		# Get dependencies from [tool.poetry.dependencies] (excluding python itself)
		deps = pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})
		dep_list = []
		for pkg, ver in deps.items():
			if pkg.lower() == 'python':
				continue
			# Poetry allows version to be a string or a dict (for extras)
			if isinstance(ver, str):
				# Handle version constraints like "^1.0.0" by converting to specific version
				if ver.startswith('^'):
					dep_list.append(f"{pkg}>={ver[1:]}")
				elif ver.startswith('~'):
					dep_list.append(f"{pkg}>={ver[1:]}")
				else:
					dep_list.append(f"{pkg}=={ver}")
			elif isinstance(ver, dict) and 'version' in ver:
				version = ver['version']
				if version.startswith('^'):
					dep_list.append(f"{pkg}>={version[1:]}")
				elif version.startswith('~'):
					dep_list.append(f"{pkg}>={version[1:]}")
				else:
					dep_list.append(f"{pkg}=={version}")
			else:
				dep_list.append(pkg)
		pip_deps_cmd = [
			'pip', 'install', '--target', site_packages_dir,
			# Remove --no-deps to allow installation of required sub-dependencies
			*dep_list
		]
		subprocess.run(pip_deps_cmd, check=True, cwd=project_root)
		
		# Step 3: Copy the source code properly
		print("Copying dzgroshared source code...")
		src_dir = os.path.join(dzgroshared_dir, 'src', 'dzgroshared')
		dest_dir = os.path.join(site_packages_dir, 'dzgroshared')
		
		if os.path.exists(dest_dir):
			shutil.rmtree(dest_dir)
		shutil.copytree(src_dir, dest_dir)
		
		# Step 4: Create the zip file with proper Lambda layer structure
		print("Creating layer zip file...")
		with zipfile.ZipFile(layer_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
			# Add all files from python directory to the zip
			for root, dirs, files in os.walk(python_dir):
				for file in files:
					file_path = os.path.join(root, file)
					# Create archive path relative to layer_build_dir
					archive_path = os.path.relpath(file_path, layer_build_dir)
					zf.write(file_path, archive_path)
		
		print(f"Layer zipped at {layer_zip}")
		
		# Get zip file size for verification
		zip_size = os.path.getsize(layer_zip) / (1024 * 1024)  # Size in MB
		print(f"Layer zip size: {zip_size:.2f} MB")
		
	except subprocess.CalledProcessError as e:
		print(f"Error during pip install: {e}")
		raise
	except Exception as e:
		print(f"Error building layer: {e}")
		raise
	finally:
		# Clean up build directory
		if os.path.exists(layer_build_dir):
			shutil.rmtree(layer_build_dir)
			print(f"Deleted intermediary build directory: {layer_build_dir}")

def create_layer(region: str):
	

	# Publish layer using boto3
	client = boto3.client("lambda", region_name=region)
	import os
	layer_name = "dzgroshared_layer"
	project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
	layer_zip = os.path.join(project_root, "dzgroshared_layer.zip")
	with open(layer_zip, "rb") as f:
		response = client.publish_layer_version(
			LayerName=layer_name,
			Description="dzgroshared poetry project layer",
			Content={"ZipFile": f.read()},
			CompatibleRuntimes=["python3.12"],
			LicenseInfo="MIT"
		)
	layer_arn = response["LayerVersionArn"]
	print(f"Published Lambda layer ARN: {layer_arn}")
	return layer_arn

def build_deploy_sam_template(region):
	"""
	Builds and deploys the SAM template for the given region using AWS SAM CLI.
	"""
	import subprocess
	import os
	project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
	template_file = os.path.join(f'sam-template-{region}.yaml')
	built_template_file = os.path.join(project_root, '.aws-sam', 'build', 'template.yaml')
	s3_bucket = f'dzgro-sam-{region}'
	
	# Check if dzgro-sam bucket exists in the region, create if not
	import boto3
	s3 = boto3.client('s3', region_name=region)
	try:
		s3.head_bucket(Bucket=s3_bucket)
	except Exception:
		print(f"Bucket {s3_bucket} does not exist in region {region}, creating...")
		if region == "us-east-1":
			s3.create_bucket(Bucket=s3_bucket)
		else:
			s3.create_bucket(Bucket=s3_bucket, CreateBucketConfiguration={'LocationConstraint': region})
		print(f"Bucket {s3_bucket} created in region {region}.")
	
	build_command = [
		'sam', 'build',
		'--template-file', template_file
	]
	deploy_command = [
		'sam', 'deploy',
		'--template-file', built_template_file,  # Use built template from .aws-sam/build
		'--region', region,
		'--no-confirm-changeset',
		'--stack-name', f"dzgro-sam-{region}",
		'--s3-bucket', s3_bucket, '--force-upload'
	]
	
	try:
		subprocess.run(build_command, check=True, shell=True)
		subprocess.run(deploy_command, check=True, shell=True)
	except subprocess.CalledProcessError as e:
		print(f"Error building or deploying SAM template for region {region}: {e.stderr}")
def upload_sam_template(region, api_gateway_role, lambda_role, layer_arn):
	"""
	Dynamically generates a SAM template for the given region using deployment.txt step 3 logic and saves it as sam-template-<region>.yaml.
	"""
	import importlib.util
	import os
	import yaml
	mapping_path = os.path.join(os.path.dirname(__file__), 'mapping.py')
	spec = importlib.util.spec_from_file_location('mapping', mapping_path)
	if spec is None or spec.loader is None:
		print("Error: Could not load mapping.py spec or loader.")
		return
	mapping = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mapping)

	# Build SAM template structure
	template = {
		'AWSTemplateFormatVersion': '2010-09-09',
		'Transform': 'AWS::Serverless-2016-10-31',
		'Description': f'SAM template for region {region}',
		'Resources': {}
	}

	# Lambda Functions
	for func_key, func in mapping.FUNCTIONS_MAP.items():
		if region in func.get('region', []):
			resource_name = f'{func_key}Function'
			# Check if this function is triggered by a queue
			triggered_by_queue = False
			for queue in mapping.QUEUES_MAP.values():
				if region in queue.get('region', []):
					if queue.get('function') == func_key:
						triggered_by_queue = True
						break
			timeout_value = 60 if triggered_by_queue else 900
			template['Resources'][resource_name] = {
				'Type': 'AWS::Serverless::Function',
				'Properties': {
					'Handler': 'handler.handler',
					'Runtime': 'python3.12',
					'Architectures': ['x86_64'],
					'CodeUri': func['path'],
					'Description': func.get('description', ''),
					'Timeout': timeout_value,
					'Layers': [layer_arn],
					'Role': lambda_role
				}
			}

	# SQS Queues
	for queue_key, queue in mapping.QUEUES_MAP.items():
		if region in queue.get('region', []):
			main_queue_name = f'{queue_key}Q'
			dlq_name = f'{queue_key}DLQ'
			template['Resources'][main_queue_name] = {
				'Type': 'AWS::SQS::Queue',
				'Properties': {
					'QueueName': main_queue_name,
					'VisibilityTimeout': 60,
					'RedrivePolicy': {
						'deadLetterTargetArn': {'Fn::GetAtt': [dlq_name, 'Arn']},
						'maxReceiveCount': 1
					}
				}
			}
			# Add SQS policy for AmsPerformance queue
			if queue_key == 'AmsPerformance':
				policy = mapping.getAMSPerformancePolicy(region)
				template['Resources']['AmsPerformancePolicy'] = policy
			if queue_key == 'AmsChange':
				policy = mapping.getAMSChangeSetPolicy(region)
				template['Resources']['AmsChangePolicy'] = policy
			template['Resources'][dlq_name] = {
				'Type': 'AWS::SQS::Queue',
				'Properties': {
					'QueueName': dlq_name,
					'VisibilityTimeout': 60
				}
			}
			# Event source mapping for Lambda trigger
			if 'function' in queue:
				event_mapping_name = f'{queue_key}EventSourceMapping'
				template['Resources'][event_mapping_name] = {
					'Type': 'AWS::Lambda::EventSourceMapping',
					'Properties': {
						'EventSourceArn': {'Fn::GetAtt': [main_queue_name, 'Arn']},
						'FunctionName': {'Ref': f"{queue['function']}Function"}
					}
				}

	# S3 Buckets (default region only)
	if region == mapping.DEFAULT_REGION:
		for bucket in ['dzgro-reports', 'dzgro', 'dzgro-invoices', 'dzgro-cloudfront']:
			resource_name = bucket.replace('-', '').title()
			template['Resources'][resource_name] = {
				'Type': 'AWS::S3::Bucket',
				'Properties': {
					'BucketName': bucket
				}
			}

	# API Gateway (default region only)
	if region == mapping.DEFAULT_REGION:
		api_resource = {
			'Type': 'AWS::Serverless::Api',
			'Properties': {
				'StageName': 'prod',
				'EndpointConfiguration': 'REGIONAL',
				'DefinitionBody': {
					'openapi': '3.0.1',
					'info': {'title': 'Dzgro API', 'version': '1.0'},
					'paths': {}
				}
			}
		}
		# Add routes from QUEUES_MAP
		for queue_key, queue in mapping.QUEUES_MAP.items():
			if 'routes' in queue:
				for idx, route in enumerate(queue['routes']):
					path = route['path']
					method = route['method'].lower()
					destination = route['destination']
					headers = route.get('headers', [])
					integration = {}
					if destination.lower() == 'lambda':
						integration = {
							'x-amazon-apigateway-integration': {
								'type': 'aws',
								'httpMethod': 'POST',
								'uri': f"arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{LambdaFunctionArn}}/invocations",
								'credentials': api_gateway_role,
								'requestTemplates': {
									'application/json': '{ "body": $input.json(\'$\') }'
								}
							}
						}
					elif destination.lower() == 'sqs':
						queue_name = queue_key
						uri = f"arn:aws:apigateway:${{AWS::Region}}:sqs:path/${{AWS::AccountId}}/{queue_name}"
						request_template = "Action=SendMessage&MessageBody=$input.body"
						if headers:
							for i, header in enumerate(headers, 1):
								request_template += f"&MessageAttribute.{i}.Name={header}" \
									f"&MessageAttribute.{i}.Value.StringValue=$input.params().header.get('{header}')" \
									f"&MessageAttribute.{i}.Value.DataType=String"
						integration = {
							'x-amazon-apigateway-integration': {
								'type': 'aws',
								'httpMethod': 'POST',
								'uri': uri,
								'credentials': api_gateway_role,
								'requestParameters': {
									'integration.request.header.Content-Type': "'application/x-www-form-urlencoded'"
								},
								'requestTemplates': {
									'application/x-www-form-urlencoded': request_template
								}
							}
						}
					# Add to OpenAPI paths
					if path not in api_resource['Properties']['DefinitionBody']['paths']:
						api_resource['Properties']['DefinitionBody']['paths'][path] = {}
					api_resource['Properties']['DefinitionBody']['paths'][path][method] = {
						'responses': {'200': {'description': 'Success'}},
						**integration
					}
		template['Resources']['ApiGateway'] = api_resource

	# Save template to file
	filename = os.path.join(f'sam-template-{region}.yaml')
	with open(filename, 'w') as f:
		yaml.dump(template, f, sort_keys=False)
	print(f"SAM template for region {region} saved to {filename}")
def get_regions_from_mapping():
	"""
	Returns a list of all unique regions and the default region from mapping.py FUNCTIONS_MAP.
	"""
	import importlib.util
	import os
	mapping_path = os.path.join(os.path.dirname(__file__), 'mapping.py')
	spec = importlib.util.spec_from_file_location('mapping', mapping_path)
	if spec is None or spec.loader is None:
		raise ImportError("Could not load mapping.py")
	mapping = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mapping)

	regions = []
	for func in mapping.FUNCTIONS_MAP.values():
		regions.extend(func.get('region', []))
	# Remove duplicates by converting to set, then back to list
	unique_regions = list(set(regions))
	default_region = getattr(mapping, 'DEFAULT_REGION', None)
	return unique_regions, default_region

def create_api_gateway_role():
	"""
	Creates IAM role DzgroAPIGatewayRole with required policies and returns the role ARN.
	"""
	iam = boto3.client('iam')
	role_name = 'DzgroAPIGatewayRole'
	assume_role_policy = {
		"Version": "2012-10-17",
		"Statement": [
			{
				"Effect": "Allow",
				"Principal": {"Service": "apigateway.amazonaws.com"},
				"Action": "sts:AssumeRole"
			}
		]
	}
	policies = [
		'arn:aws:iam::aws:policy/AWSLambdaBasicExecutionRole',
		'arn:aws:iam::aws:policy/AmazonSQSFullAccess'
	]
	try:
		# Check if role exists
		response = iam.get_role(RoleName=role_name)
		print(f"Role {role_name} already exists.")
		return response['Role']['Arn']
	except ClientError as e:
		if e.response['Error']['Code'] == 'NoSuchEntity':
			try:
				print(f"Creating role: {role_name}")
				response = iam.create_role(
					RoleName=role_name,
					AssumeRolePolicyDocument=json.dumps(assume_role_policy)
				)
				for policy_arn in policies:
					iam.attach_role_policy(
						RoleName=role_name,
						PolicyArn=policy_arn
					)
				print(f"Role {role_name} created and policies attached.")
				return response['Role']['Arn']
			except ClientError as ce:
				print(f"Error creating role {role_name}: {ce}")
				return None
		else:
			print(f"Error checking role {role_name}: {e}")
			return None
import boto3
from botocore.exceptions import ClientError
import json

def create_lambda_role():
	"""
	Creates IAM role DzgroLambdaRole with required policies and returns the role details.
	"""
	iam = boto3.client('iam')
	role_name = 'DzgroLambdaRole'
	assume_role_policy = {
		"Version": "2012-10-17",
		"Statement": [
			{
				"Effect": "Allow",
				"Principal": {"Service": "lambda.amazonaws.com"},
				"Action": "sts:AssumeRole"
			}
		]
	}
	policies = [
		'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
		'arn:aws:iam::aws:policy/AmazonRDSFullAccess',
		'arn:aws:iam::aws:policy/AmazonS3FullAccess'
	]
	try:
		# Check if role exists
		response = iam.get_role(RoleName=role_name)
		print(f"Role {role_name} already exists.")
		return response['Role']['Arn']
	except ClientError as e:
		if e.response['Error']['Code'] == 'NoSuchEntity':
			try:
				print(f"Creating role: {role_name}")
				response = iam.create_role(
					RoleName=role_name,
					AssumeRolePolicyDocument=json.dumps(assume_role_policy)
				)
				for policy_arn in policies:
					iam.attach_role_policy(
						RoleName=role_name,
						PolicyArn=policy_arn
					)
				print(f"Role {role_name} created and policies attached.")
				return response['Role']['Arn']
			except ClientError as ce:
				print(f"Error creating role {role_name}: {ce}")
				return None
		else:
			print(f"Error checking role {role_name}: {e}")
			return None
		

def run_connect_ec2_script():
	"""
	Runs the connect-ec2.ps1 PowerShell script to deploy to EC2.
	"""
	import subprocess
	import os
	
	script_path = os.path.join(os.path.dirname(__file__), 'connect-ec2.ps1')
	
	try:
		print("Running connect-ec2.ps1 script...")
		result = subprocess.run(
			['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', script_path],
			cwd=os.path.dirname(os.path.dirname(__file__)),  # Run from project root
			check=True,
			capture_output=True,
			text=True
		)
		print("Connect EC2 script completed successfully.")
		print(f"Output: {result.stdout}")
		if result.stderr:
			print(f"Warnings: {result.stderr}")
	except subprocess.CalledProcessError as e:
		print(f"Error running connect-ec2.ps1 script: {e}")
		print(f"Error output: {e.stderr}")
	except FileNotFoundError:
		print("PowerShell not found. Please ensure PowerShell is installed and in PATH.")
	except Exception as e:
		print(f"Unexpected error running connect-ec2.ps1: {e}")

def cleanup_deployment_assets():
	"""
	Cleans up all assets created during the deployment process.
	This includes:
	- SAM template YAML files
	- dzgroshared_layer.zip
	- .aws-sam build directory
	- deploy_upload folder and zip
	- Poetry build artifacts (dist/ folders)
	- SAM deployment buckets (optionally)
	- Layer build directory
	"""
	import os
	import shutil
	import glob
	import boto3
	from botocore.exceptions import ClientError
	
	print("Starting cleanup of deployment assets...")
	project_root = os.path.dirname(os.path.dirname(__file__))
	
	# 1. Clean up SAM template files in project root
	sam_templates = glob.glob(os.path.join(project_root, 'sam-template-*.yaml'))
	for template in sam_templates:
		try:
			os.remove(template)
			print(f"Deleted SAM template: {os.path.basename(template)}")
		except OSError as e:
			print(f"Error deleting {template}: {e}")
	
	# 2. Clean up dzgroshared_layer.zip
	layer_zip = os.path.join(project_root, 'dzgroshared_layer.zip')
	if os.path.exists(layer_zip):
		try:
			os.remove(layer_zip)
			print(f"Deleted layer zip: dzgroshared_layer.zip")
		except OSError as e:
			print(f"Error deleting layer zip: {e}")
	
	# 3. Clean up .aws-sam build directory
	aws_sam_dir = os.path.join(project_root, '.aws-sam')
	if os.path.exists(aws_sam_dir):
		try:
			shutil.rmtree(aws_sam_dir)
			print(f"Deleted .aws-sam build directory")
		except OSError as e:
			print(f"Error deleting .aws-sam directory: {e}")
	
	# 4. Clean up deploy_upload folder and zip
	deploy_upload_dir = os.path.join(project_root, 'deploy_upload')
	if os.path.exists(deploy_upload_dir):
		try:
			shutil.rmtree(deploy_upload_dir)
			print(f"Deleted deploy_upload directory")
		except OSError as e:
			print(f"Error deleting deploy_upload directory: {e}")
	
	deploy_upload_zip = os.path.join(project_root, 'deploy_upload.zip')
	if os.path.exists(deploy_upload_zip):
		try:
			os.remove(deploy_upload_zip)
			print(f"Deleted deploy_upload.zip")
		except OSError as e:
			print(f"Error deleting deploy_upload.zip: {e}")
	
	# 5. Clean up Poetry build artifacts (dist/ folders)
	for subdir in ['api', 'dzgroshared', 'test', 'utilities/make_mask_square']:
		dist_dir = os.path.join(project_root, subdir, 'dist')
		if os.path.exists(dist_dir):
			try:
				shutil.rmtree(dist_dir)
				print(f"Deleted {subdir}/dist directory")
			except OSError as e:
				print(f"Error deleting {subdir}/dist directory: {e}")
	
	# 6. Clean up layer_build directory in deployment folder
	layer_build_dir = os.path.join(os.path.dirname(__file__), 'layer_build')
	if os.path.exists(layer_build_dir):
		try:
			shutil.rmtree(layer_build_dir)
			print(f"Deleted deployment/layer_build directory")
		except OSError as e:
			print(f"Error deleting layer_build directory: {e}")
	
	# 7. Clean up any temporary pem files
	pem_files = glob.glob(os.path.join(project_root, '*.pem'))
	for pem_file in pem_files:
		try:
			os.remove(pem_file)
			print(f"Deleted temporary pem file: {os.path.basename(pem_file)}")
		except OSError as e:
			print(f"Error deleting {pem_file}: {e}")
	
	# 8. Clean up __pycache__ directories
	for root, dirs, files in os.walk(project_root):
		if '__pycache__' in dirs:
			pycache_dir = os.path.join(root, '__pycache__')
			try:
				shutil.rmtree(pycache_dir)
				print(f"Deleted __pycache__ in {os.path.relpath(pycache_dir, project_root)}")
			except OSError as e:
				print(f"Error deleting __pycache__ in {root}: {e}")
	
	# 9. Optionally clean up S3 buckets created for SAM deployment (commented out for safety)
	# This is commented out because these buckets might contain important deployment artifacts
	# Uncomment and modify as needed
	"""
	try:
		regions, _ = get_regions_from_mapping()
		for region in regions:
			bucket_name = f'dzgro-sam-{region}'
			try:
				s3 = boto3.client('s3', region_name=region)
				# Delete all objects in bucket first
				response = s3.list_objects_v2(Bucket=bucket_name)
				if 'Contents' in response:
					objects = [{'Key': obj['Key']} for obj in response['Contents']]
					s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})
				# Delete the bucket
				s3.delete_bucket(Bucket=bucket_name)
				print(f"Deleted S3 bucket: {bucket_name}")
			except ClientError as e:
				if e.response['Error']['Code'] != 'NoSuchBucket':
					print(f"Error deleting S3 bucket {bucket_name}: {e}")
	except Exception as e:
		print(f"Error during S3 bucket cleanup: {e}")
	"""
	
	print("Cleanup completed!")

def main():
	try:
		build_layer_zip_clean()
		LambdaRole = create_lambda_role()
		print("Lambda_ARN:", LambdaRole)
		if LambdaRole is None:
			raise RuntimeError("Failed to create or retrieve Lambda role ARN.")
		ApiGatewayRole = create_api_gateway_role()
		print("ApiGateway_ARN:", ApiGatewayRole)
		if ApiGatewayRole is None:
			raise RuntimeError("Failed to create or retrieve API Gateway role ARN.")

		regions, default_region = get_regions_from_mapping()
		
			
		print("Regions:", regions)
		print("Default Region:", default_region)
		for region in regions:
			if region==default_region:
				LayerArn = create_layer(region)
                # LayerArn = f"arn:aws:lambda:{region}:522814698847:layer:dzgroshared_layer:1"
				upload_sam_template(region, ApiGatewayRole, LambdaRole, LayerArn)
				build_deploy_sam_template(region)
		
		# Run connect EC2 script after deployment
		# run_connect_ec2_script()
		
		# Clean up deployment assets
		print("\n" + "="*50)
		print("CLEANING UP DEPLOYMENT ASSETS")
		print("="*50)
		cleanup_deployment_assets()
        
	except Exception as e:
		print(f"Error in main: {e}")
		# Even if deployment fails, offer to clean up
		response = input("Deployment failed. Do you want to clean up created assets? (y/n): ")
		if response.lower() in ['y', 'yes']:
			cleanup_deployment_assets()

if __name__ == "__main__":
	import sys
	
	# Check if cleanup argument is provided
	if len(sys.argv) > 1 and sys.argv[1].lower() == 'cleanup':
		print("Running cleanup only...")
		cleanup_deployment_assets()
	else:
		main()
