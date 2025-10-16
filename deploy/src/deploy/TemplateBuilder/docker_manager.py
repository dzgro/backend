import subprocess
import time

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
    if not is_ubuntu_running(distro):
        subprocess.Popen(["wsl", "-d", distro, "-u", user, "--exec", "bash", "-c", f"echo 'Ubuntu started as {user}'"])
        time.sleep(2)
        print("Ubuntu started.")

    if not is_docker_running(distro, user):
        subprocess.Popen(["wsl", "-d", distro, "-u", user, "--exec", "bash", "-c", "sudo service docker start"])
        print("Docker service starting...")

    if wait_for_docker(distro, user):
        print("Docker is fully ready!")
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
