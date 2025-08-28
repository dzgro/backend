"""
Docker Desktop management utilities for Windows.
"""
import subprocess
import time
import os


def start_docker_desktop():
    """
    Starts Docker Desktop on Windows if it's not already running.
    
    Returns:
        bool: True if Docker is running, False otherwise
    """
    try:
        # Check if Docker is already running
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("Docker Desktop is already running.")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("Docker is not running or not found.")
    
    print("Starting Docker Desktop...")
    
    # Common paths for Docker Desktop executable
    docker_desktop_paths = [
        r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
        r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
        r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe",
        os.path.expanduser(r"~\AppData\Local\Docker\Docker Desktop.exe"),
        os.path.expanduser(r"~\AppData\Roaming\Docker Desktop\Docker Desktop.exe")
    ]
    
    docker_exe = None
    for path in docker_desktop_paths:
        if os.path.exists(path):
            docker_exe = path
            break
    
    if not docker_exe:
        print("Docker Desktop executable not found in common locations.")
        print("Please start Docker Desktop manually or check installation.")
        return False
    
    try:
        # Start Docker Desktop (detached process)
        subprocess.Popen([docker_exe], shell=True)
        print("Docker Desktop is starting up...")
        
        # Wait for Docker to be ready (up to 60 seconds)
        for i in range(12):  # 12 attempts, 5 seconds each = 60 seconds
            time.sleep(5)
            try:
                result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("✓ Docker Desktop is now running and ready.")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            print(f"Waiting for Docker to start... ({(i+1)*5}/60 seconds)")
        
        print("Docker Desktop took too long to start. Please check manually.")
        return False
        
    except Exception as e:
        print(f"Error starting Docker Desktop: {e}")
        return False


def close_docker_desktop():
    """
    Closes Docker Desktop on Windows.
    
    Returns:
        bool: True if Docker was closed successfully, False otherwise
    """
    try:
        print("Closing Docker Desktop...")
        
        # Method 1: Try to stop Docker Desktop gracefully with psutil
        try:
            import psutil
            subprocess.run(['docker', 'context', 'use', 'default'], capture_output=True, timeout=5)
            # Find and terminate Docker Desktop processes
            for proc in psutil.process_iter(['pid', 'name']):
                if 'Docker Desktop' in proc.info['name'] or 'Docker' in proc.info['name']:
                    try:
                        proc.terminate()
                        print(f"Terminated {proc.info['name']} (PID: {proc.info['pid']})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except ImportError:
            print("psutil not available, using taskkill method...")
        except Exception:
            pass
        
        # Method 2: Use taskkill as backup
        try:
            subprocess.run(['taskkill', '/f', '/im', 'Docker Desktop.exe'], capture_output=True)
            subprocess.run(['taskkill', '/f', '/im', 'dockerd.exe'], capture_output=True)
            subprocess.run(['taskkill', '/f', '/im', 'com.docker.backend.exe'], capture_output=True)
            subprocess.run(['taskkill', '/f', '/im', 'com.docker.cli.exe'], capture_output=True)
        except Exception:
            pass
        
        # Wait a moment for processes to close
        time.sleep(3)
        
        # Verify Docker is no longer running
        try:
            result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                print("✓ Docker Desktop has been closed.")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("✓ Docker Desktop has been closed.")
            return True
        
        print("Docker Desktop may still be running.")
        return False
        
    except Exception as e:
        print(f"Error closing Docker Desktop: {e}")
        return False