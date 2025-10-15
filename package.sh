#!/bin/bash

# Create the executable
pyinstaller --name "Ajyad Accountant" \
            --onefile \
            --windowed \
            --add-data "app/locale:app/locale" \
            main.py

# Create a distributable archive
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    tar -czvf "Ajyad Accountant-linux.tar.gz" -C dist "Ajyad Accountant"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    hdiutil create "Ajyad Accountant-mac.dmg" -srcfolder "dist/Ajyad Accountant.app" -ov
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Create a zip file for Windows
    powershell -Command "Compress-Archive -Path 'dist/Ajyad Accountant.exe' -DestinationPath 'Ajyad Accountant-windows.zip'"
fi