# This script will add, commit, and push all changes in the current repository.
# Usage: Run this file with Python in your repo root.
import subprocess
import sys
import os
import importlib.util

def run(cmd):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        sys.exit(result.returncode)

# Add all changes
run(["git", "add", "."])

# Commit with a generic message
run(["git", "commit", "-m", "Auto commit: workspace changes"])

# Push to current branch
run(["git", "push"])
