#!/usr/bin/env python3
"""
DICOM Anonymizer App Launcher
Installs dependencies and launches the PyQt5 GUI application
"""

import sys
import subprocess
from pathlib import Path


def install_dependencies():
    """Install required dependencies"""
    required_packages = [
        'pydicom',
        'PyQt5',
        'tqdm'
    ]
    
    print("Checking and installing dependencies...")
    print("=" * 60)
    
    for package in required_packages:
        try:
            __import__(package if package != 'PyQt5' else 'PyQt5.QtWidgets')
            print(f"✓ {package} is already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
    
    print("=" * 60)
    print("✓ All dependencies ready!\n")


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("DICOM ANONYMIZER - PyQt5 Application")
    print("=" * 60 + "\n")
    
    # Install dependencies
    install_dependencies()
    
    # Launch the application
    print("Launching DICOM Anonymizer GUI...\n")
    
    app_path = Path(__file__).parent / "dicom_anonymizer_app.py"
    
    if not app_path.exists():
        print(f"❌ Error: {app_path} not found!")
        sys.exit(1)
    
    try:
        exec(open(app_path).read())
    except Exception as e:
        print(f"❌ Error launching application: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
