import hashlib
import os
from pathlib import Path

import hashlib
import os
from pathlib import Path


def hash_poetry_dependencies(pyproject_path):
    """Hash the dependencies section of a pyproject.toml file."""
    import toml
    data = toml.load(pyproject_path)
    deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
    # Convert to sorted string for stable hash
    dep_str = '\n'.join(f"{k}={v}" for k, v in sorted(deps.items()))
    return hashlib.sha256(dep_str.encode()).hexdigest()

def freeze_dependencies(project_dir):
    pyproject_path = Path(project_dir) / 'pyproject.toml'
    lock_path = Path(project_dir) / 'poetry.lock'
    hash_path = Path(project_dir) / '.dep_hash'
    if not pyproject_path.exists():
        print(f"No pyproject.toml in {project_dir}")
        return
    dep_hash = hash_poetry_dependencies(pyproject_path)
    prev_hash = hash_path.read_text() if hash_path.exists() else None
    if prev_hash == dep_hash:
        print(f"Dependencies unchanged for {project_dir}, skipping lock file recreation.")
        return
    # Hash changed, recreate lock file
    if lock_path.exists():
        os.remove(lock_path)
    os.system(f"poetry lock --directory {project_dir}")
    hash_path.write_text(dep_hash)
    print(f"Lock file recreated for {project_dir}.")

# Example usage: freeze all shared and functions subdirs
ROOT = Path(__file__).parent.resolve()
for subdir in (ROOT / 'shared').iterdir():
    if (subdir / 'pyproject.toml').exists():
        freeze_dependencies(subdir)
for subdir in (ROOT / 'functions').iterdir():
    if (subdir / 'pyproject.toml').exists():
        freeze_dependencies(subdir)
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).parent.resolve()

# Recursively find all pyproject.toml files
pyproject_files = [p for p in ROOT.rglob('pyproject.toml')]

for pyproject in pyproject_files:
    folder = pyproject.parent
    lock_file = folder / "poetry.lock"
    if lock_file.exists():
        print(f"Deleting poetry.lock in: {folder}")
        lock_file.unlink()
    print(f"Installing dependencies in: {folder}")
    try:
        subprocess.run(["poetry", "install"], cwd=folder, check=True)
        print(f"✅ Installed dependencies and created poetry.lock in {folder}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies in {folder}: {e}")
