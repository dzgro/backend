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

def main():
	try:
		from rolecreator import RoleCreator
		from layer_builder import LayerBuilder
		from template_builder import TemplateBuilder
		import mapping, cleaner
		layerBuilder = LayerBuilder()
		roleCreator = RoleCreator()
		# layerBuilder.build_layer_zip_clean()
		LambdaRole = roleCreator.create_lambda_role()
		ApiGatewayRole = roleCreator.create_api_gateway_role()

        # Prompt user to select regions to deploy
		# print("\nSelect regions to deploy (comma separated indices):")
		for idx, region in enumerate(mapping.REGIONS):
			print(f"{idx}: {region}")
		print(f"{len(mapping.REGIONS)}: all (deploy to all regions)")
		selected_regions:list[str] = []
		selected = input("Enter indices (e.g. 0,2 or all): ").strip().lower()
		if selected == "all" or str(len(mapping.REGIONS)) in selected.split(","):
			# Always keep default_region as first entry
			selected_regions = [mapping.DEFAULT_REGION] + [r for r in mapping.REGIONS if r != mapping.DEFAULT_REGION]
		else:
			selected_indices = [int(i) for i in selected.split(",") if i.strip().isdigit()]
			# Always keep default_region as first entry if selected
			selected_regions = []
			if mapping.DEFAULT_REGION in mapping.REGIONS and mapping.REGIONS.index(mapping.DEFAULT_REGION) in selected_indices:
				selected_regions.append(mapping.DEFAULT_REGION)
			selected_regions += [mapping.REGIONS[i] for i in selected_indices if mapping.REGIONS[i] != mapping.DEFAULT_REGION and i < len(mapping.REGIONS)]

		print("Selected regions for deployment:", selected_regions)
		for region in selected_regions:
			# LayerArn = create_layer(region)
			LayerArn = f"arn:aws:lambda:{region}:522814698847:layer:dzgroshared_layer:7"
			TemplateBuilder(region, ApiGatewayRole, LambdaRole, LayerArn).deploy()
		
		# Run connect EC2 script after deployment
		# run_connect_ec2_script()
		
		# Clean up deployment assets
		print("\n" + "="*50)
		print("CLEANING UP DEPLOYMENT ASSETS")
		print("="*50)
		cleaner.cleanup_deployment_assets()
        
	except Exception as e:
		print(f"Error in main: {e}")
		# Even if deployment fails, offer to clean up
		response = input("Deployment failed. Do you want to clean up created assets? (y/n): ")
		if response.lower() in ['y', 'yes']:
			cleaner.cleanup_deployment_assets()

if __name__ == "__main__":
	main()
