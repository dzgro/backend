import inquirer
import subprocess
from pathlib import Path

# User-friendly options and their corresponding script files
options = [
    ("Deploy", "deployment/deploy.py"),
    ("Git Commit & Push", "git-push-all.py"),
]

question = [
    inquirer.List(
        "script",
        message="Select an operation to run:",
        choices=[opt[0] for opt in options],
    )
]
answer = inquirer.prompt(question)
if not answer or "script" not in answer:
    print("No selection made.")
    exit(1)
selected_name = answer["script"]
selected_file = next(f for n, f in options if n == selected_name)

script_path = Path(__file__).parent / selected_file
if not script_path.exists():
    print(f"Script not found: {script_path}")
    exit(1)

print(f"Running: {selected_name}")
try:
    subprocess.run(["python", str(script_path)], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running {selected_file}: {e}")
