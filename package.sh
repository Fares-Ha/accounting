#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if pyinstaller is installed
if ! command_exists pyinstaller; then
    echo "Error: pyinstaller is not installed. Please install it by running 'pip install pyinstaller'"
    exit 1
fi

# Create the executable
echo "Creating the executable..."
pyinstaller --name "Ajyad Accountant" \
            --onefile \
            --windowed \
            --add-data "app/locale:app/locale" \
            main.py

if [ $? -ne 0 ]; then
    echo "Error: pyinstaller failed to create the executable."
    exit 1
fi

# Create a distributable archive
echo "Creating a distributable archive..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    tar -czvf "Ajyad Accountant-linux.tar.gz" -C dist "Ajyad Accountant"
    echo "Successfully created 'Ajyad Accountant-linux.tar.gz'"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    hdiutil create "Ajyad Accountant-mac.dmg" -srcfolder "dist/Ajyad Accountant.app" -ov
    echo "Successfully created 'Ajyad Accountant-mac.dmg'"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Create a zip file for Windows
    if command_exists powershell; then
        powershell -Command "Compress-Archive -Path 'dist/Ajyad Accountant.exe' -DestinationPath 'Ajyad Accountant-windows.zip'"
        echo "Successfully created 'Ajyad Accountant-windows.zip'"
    else
        echo "Warning: powershell is not available. Creating a zip file using a different method."
        # Fallback to a different zip utility if powershell is not available
        if command_exists zip; then
            zip -j "Ajyad Accountant-windows.zip" "dist/Ajyad Accountant.exe"
            echo "Successfully created 'Ajyad Accountant-windows.zip'"
        else
            echo "Error: Could not find a suitable zip utility. Please create the zip file manually."
        fi
    fi
else
    echo "Warning: Unsupported OS type '$OSTYPE'. No distributable archive created."
fi