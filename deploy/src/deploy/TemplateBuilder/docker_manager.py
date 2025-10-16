import subprocess
import time
import os

def is_ubuntu_running(distro="Ubuntu"):
    result = subprocess.run(["wsl", "--list", "--verbose"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if distro in line and "Running" in line:
            return True
    return False

def is_docker_running(distro="Ubuntu", user="dzgro"):
    try:
        result = subprocess.run(
            ["wsl", "-d", distro, "-u", user, "--exec", "bash", "-c", "sudo service docker status"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        return "active (running)" in result.stdout
    except Exception:
        return False

def wait_for_docker(distro="Ubuntu", user="dzgro", timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(
                ["wsl", "-d", distro, "-u", user, "--exec", "bash", "-c", "docker info"],
                capture_output=True, text=True
            )
            if "Docker Root Dir" in result.stdout:
                return True
        except:
            pass
        time.sleep(1)
    return False

def start_ubuntu_docker(distro="Ubuntu", user="dzgro"):
    """
    Start WSL Ubuntu and Docker service
    WSL Location: D:\WSL-Ubuntu
    Username: dzgro

    This also sets up Docker to be accessible from Windows by exposing
    the Docker socket with proper permissions.
    """
    if not is_ubuntu_running(distro):
        subprocess.Popen(["wsl", "-d", distro, "-u", user, "--exec", "bash", "-c", f"echo 'Ubuntu started as {user}'"])
        time.sleep(2)
        print(f"Ubuntu WSL started (Location: D:\\WSL-Ubuntu, User: {user}).")

    if not is_docker_running(distro, user):
        subprocess.Popen(["wsl", "-d", distro, "-u", user, "--exec", "bash", "-c", "sudo service docker start"])
        print("Docker service starting...")

    if wait_for_docker(distro, user):
        print("Docker is fully ready!")

        # Set proper permissions on Docker socket so it's accessible from Windows
        subprocess.run([
            "wsl", "-d", distro, "-u", user, "--exec", "bash", "-c",
            "sudo chmod 666 /var/run/docker.sock"
        ], capture_output=True)
        print("Docker socket permissions configured for Windows access.")

        # Try to determine the correct Docker socket path for WSL
        # First, try to use the standard WSL path format
        docker_host = f"//wsl$/{distro}/var/run/docker.sock"

        # Set DOCKER_HOST for Windows processes to use WSL Docker
        # We need to use npiperelay or socat for Windows-WSL Docker socket access
        # For now, configure to run SAM commands through WSL
        os.environ['DOCKER_HOST'] = f"unix:///var/run/docker.sock"  # This will be used by WSL commands

        print(f"Docker configured for WSL access at: {docker_host}")
        print("Note: Windows commands will use WSL Docker via wsl command wrapper")
    else:
        print("Warning: Docker did not start within timeout.")

def stop_ubuntu_docker(distro="Ubuntu", user="dzgro", cleanup=True):
    if is_docker_running(distro, user):
        subprocess.Popen(["wsl", "-d", distro, "-u", user, "--exec", "bash", "-c", "sudo service docker stop"])
        print("Docker service stopped.")

    if cleanup:
        # Remove stopped containers and unused images
        subprocess.Popen([
            "wsl", "-d", distro, "-u", user, "--exec", "bash", "-c",
            "docker container prune -f && docker image prune -af && docker volume prune -f"
        ])
        print("Cleaned up stopped containers, images, and volumes.")

    if is_ubuntu_running(distro):
        subprocess.Popen(["wsl", "--terminate", distro])
        print("Ubuntu WSL terminated.")

def run_docker_command_in_wsl(docker_args, distro="Ubuntu", user="dzgro", **kwargs):
    """
    Execute Docker command through WSL

    Args:
        docker_args: List of docker command arguments (e.g., ['build', '-t', 'image:tag', '.'])
        distro: WSL distribution name (default: "Ubuntu")
        user: WSL username (default: "dzgro")
        **kwargs: Additional arguments to pass to subprocess.run

    Returns:
        subprocess.CompletedProcess result
    """
    # Ensure Docker is running
    if not is_docker_running(distro, user):
        start_ubuntu_docker(distro, user)

    # Build the WSL command to run Docker
    wsl_command = ["wsl", "-d", distro, "-u", user, "--exec", "docker"] + docker_args

    # Execute the command
    return subprocess.run(wsl_command, **kwargs)

def convert_windows_path_to_wsl(windows_path):
    """
    Convert Windows path to WSL path format
    Example: D:\github\sam-app -> /mnt/d/github/sam-app
    """
    if not windows_path:
        return windows_path

    # Normalize path separators
    windows_path = os.path.normpath(windows_path)

    # Check if it's a Windows absolute path (e.g., D:\path or D:/path)
    if len(windows_path) >= 2 and windows_path[1] == ':':
        drive_letter = windows_path[0].lower()
        path_without_drive = windows_path[2:]  # Remove "D:"
        # Convert backslashes to forward slashes
        wsl_path = path_without_drive.replace('\\', '/')
        # Prepend /mnt/driveletter
        return f"/mnt/{drive_letter}{wsl_path}"

    # If it's already a relative or Unix-style path, just normalize separators
    return windows_path.replace('\\', '/')
