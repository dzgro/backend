
from dzgroshared.models.enums import ENVIRONMENT


def cleanup_deployment_assets(env: ENVIRONMENT):
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
	
	print("Starting cleanup of deployment assets...")
	project_root = os.path.dirname(os.path.dirname(__file__))
	
	# 1. Clean up SAM template files in project root
	sam_templates = glob.glob(os.path.join(project_root, 'dzgro-sam-*.yaml'))
	for template in sam_templates:
		try:
			os.remove(template)
			print(f"Deleted SAM template: {os.path.basename(template)}")
		except OSError as e:
			print(f"Error deleting {template}: {e}")
	
	# 2. Clean up dzgroshared_layer.zip
	layer_zip = os.path.join(project_root, f'dzgroshared-{env.value.lower()}.zip')
	if os.path.exists(layer_zip):
		try:
			os.remove(layer_zip)
			print(f"Deleted layer zip: dzgroshared-{env.value.lower()}.zip")
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

