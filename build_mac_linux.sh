#!/bin/bash
# TeraZip Build Script for macOS and Linux

echo "Building TeraZip for $(uname -s)..."

# Ensure pyinstaller is installed
pip install -r requirements.txt

# Run PyInstaller
pyinstaller --noconfirm --onefile --windowed --name "TeraZip" gui.py

echo "Build complete! Check the 'dist' folder for the executable."
