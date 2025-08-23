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
		import mapping, cleaner, inquirer
		question = [
			inquirer.List(
				"script",
				message="Select an Environment to run:",
				choices=[x.value for x in mapping.Environment.all()],
			)
		]
		answer = inquirer.prompt(question)
		if not answer or "script" not in answer:
			print("No selection made.")
			exit(1)
		env = mapping.Environment(answer["script"])
		from template_builder_new import TemplateBuilder
		TemplateBuilder(env).deploy()
		
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
