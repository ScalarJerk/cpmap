import os
import sys
import subprocess
import venv
from pathlib import Path

def setup_virtual_environment():
    """Set up a virtual environment and install required packages."""
    venv_dir = "venv"
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in {venv_dir}...")
        venv.create(venv_dir, with_pip=True)
    else:
        print(f"Virtual environment already exists in {venv_dir}")
    
    # Determine the pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
    else:  # Unix/MacOS
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    # Install requirements
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        print(f"Installing required packages from {requirements_file}...")
        subprocess.check_call([pip_path, "install", "-r", requirements_file])
    else:
        print(f"Warning: {requirements_file} not found. No packages installed.")
    
    print("Virtual environment setup complete!")

if __name__ == "__main__":
    setup_virtual_environment()
