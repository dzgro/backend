import cleaner, inquirer, mapping
from dzgroshared.models.enums import ENVIRONMENT

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

def askForSelection():
	question = [
		inquirer.List(
			"script",
			message="Select an Environment to run:",
			choices=[x.value for x in ENVIRONMENT.all()],
		)
	]
	answer = inquirer.prompt(question)
	if not answer or "script" not in answer:
		print("No selection made.")
		exit(1)
	return ENVIRONMENT(answer["script"])
		


def main():
	askSelection = False
	regions = mapping.Region.all() if askSelection else [mapping.Region.DEFAULT]
	env = ENVIRONMENT.DEV if not askSelection else askForSelection()
	try:
		from TemplateBuilder import TemplateBuilder
		TemplateBuilder(env).deploy(regions)

		# Run connect EC2 script after deployment
		# run_connect_ec2_script()
		
		# Clean up deployment assets
		print("\n" + "="*50)
		print("CLEANING UP DEPLOYMENT ASSETS")
		print("="*50)
		cleaner.cleanup_deployment_assets(env)
        
	except Exception as e:
		print(f"Error in main: {e}")
		# Even if deployment fails, offer to clean up
		response = input("Deployment failed. Do you want to clean up created assets? (y/n): ")
		if response.lower() in ['y', 'yes']:
			cleaner.cleanup_deployment_assets(env)

if __name__ == "__main__":
	main()
