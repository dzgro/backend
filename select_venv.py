
import os
import json
from pathlib import Path

# Requires: pip install inquirer
import inquirer

VENV_DIR = Path(r"C:\Users\Kshitiz\AppData\Local\pypoetry\Cache\virtualenvs")
VSCODE_SETTINGS = Path.cwd() / ".vscode" / "settings.json"

# Find all venvs
venvs = [d for d in VENV_DIR.iterdir() if d.is_dir()]
if not venvs:
    print("No virtual environments found.")
    exit(1)

choices = [("Remove Interpreter (set to default Python)", None)]
for venv in venvs:
    # Remove last 16 characters (arbitrary hash + python version suffix)
    if len(venv.name) > 16:
        module_name = venv.name[:-16]
    else:
        module_name = venv.name
    choices.append((module_name, venv))

question = [
    inquirer.List(
        "venv",
        message="Select Poetry environment",
        choices=[c[0] for c in choices],
    )
]
answer = inquirer.prompt(question)
if not answer or "venv" not in answer:
    print("No selection made.")
    exit(1)
selected_name = answer["venv"]
selected_venv = next(v for n, v in choices if n == selected_name)

VSCODE_SETTINGS.parent.mkdir(exist_ok=True)
settings = {}
if VSCODE_SETTINGS.exists():
    with open(VSCODE_SETTINGS) as f:
        try:
            settings = json.load(f)
        except Exception:
            settings = {}

if selected_venv is None:
    # Remove interpreter (set to default)
    settings["python.defaultInterpreterPath"] = "python"
    with open(VSCODE_SETTINGS, "w") as f:
        json.dump(settings, f, indent=2)
    print("VS Code Python interpreter reset to default ('python').")
else:
    # Find python executable in venv
    python_path = selected_venv / "Scripts" / "python.exe"
    if not python_path.exists():
        python_path = selected_venv / "bin" / "python"
    if not python_path.exists():
        print("Python executable not found in selected venv.")
        exit(1)
    print(f"Setting interpreter to: {python_path}")
    settings["python.defaultInterpreterPath"] = str(python_path)
    with open(VSCODE_SETTINGS, "w") as f:
        json.dump(settings, f, indent=2)
    print("VS Code Python interpreter updated.")
