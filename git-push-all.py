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

def run_cleanup():
    """Import and run the cleanup function from deployment/deploy.py"""
    try:
        from deployment import cleaner
        print("\n" + "="*50)
        print("RUNNING CLEANUP BEFORE COMMIT")
        print("="*50)
        cleaner.cleanup_deployment_assets()
        print("Cleanup completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return False

# Run cleanup before committing
print("Running cleanup to remove deployment artifacts before committing...")
if not run_cleanup():
    print("ERROR: Cleanup failed! Aborting commit to prevent committing build artifacts.")
    sys.exit(1)

# Add all changes
run(["git", "add", "."])

# Commit with a generic message
run(["git", "commit", "-m", "Auto commit: workspace changes"])

# Push to current branch
run(["git", "push"])
