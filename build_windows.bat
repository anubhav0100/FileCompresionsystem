@echo off
echo Building TeraZip for Windows...

pip install -r requirements.txt

pyinstaller --noconfirm --onefile --windowed --name "TeraZip" gui.py

echo Build complete! Check the 'dist' folder for TeraZip.exe
pause
