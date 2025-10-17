#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
APP_NAME="Ajyad Accountant"
ENTRY_POINT="main.py"
LOCALE_DIR="app/locale"
DIST_DIR="dist"
BUILD_DIR="build"

# --- Functions ---
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Main Script ---
echo "--- Starting Ajyad Accountant Packaging Script ---"

# 1. Check for pyinstaller
if ! command_exists pyinstaller; then
    echo "Error: pyinstaller is not installed."
    echo "Please install it by running: pip install pyinstaller"
    exit 1
fi

# 2. Clean up previous builds
echo "Cleaning up previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR" "*.spec"

# 3. Run PyInstaller
echo "Creating the executable with PyInstaller..."
pyinstaller --name "$APP_NAME" \
            --onefile \
            --windowed \
            --noconfirm \
            --add-data "$LOCALE_DIR:app/locale" \
            "$ENTRY_POINT"

if [ $? -ne 0 ]; then
    echo "Error: PyInstaller failed to create the executable."
    exit 1
fi

echo "PyInstaller completed successfully."

# 4. Create a distributable archive based on the OS
echo "Creating distributable archive..."
PLATFORM_ARCHIVE_NAME=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
    ARCHIVE_NAME="$APP_NAME-$PLATFORM.tar.gz"
    echo "Creating archive for Linux..."
    tar -czvf "$ARCHIVE_NAME" -C "$DIST_DIR/" "$APP_NAME"
    PLATFORM_ARCHIVE_NAME="$ARCHIVE_NAME"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
    ARCHIVE_NAME="$APP_NAME-$PLATFORM.dmg"
    echo "Creating archive for macOS..."
    hdiutil create "$ARCHIVE_NAME" -srcfolder "$DIST_DIR/$APP_NAME.app" -ov -format UDZO
    PLATFORM_ARCHIVE_NAME="$ARCHIVE_NAME"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    PLATFORM="windows"
    ARCHIVE_NAME="$APP_NAME-$PLATFORM.zip"
    echo "Creating archive for Windows..."
    # Using Python's zipfile module for cross-platform compatibility
    python -c "import shutil; shutil.make_archive('$APP_NAME-$PLATFORM', 'zip', '$DIST_DIR')"
    PLATFORM_ARCHIVE_NAME="$ARCHIVE_NAME"
else
    echo "Warning: Unsupported OS type '$OSTYPE'. No distributable archive created."
    exit 0
fi

if [ -f "$PLATFORM_ARCHIVE_NAME" ]; then
    echo ""
    echo "--- Packaging Complete ---"
    echo "Successfully created distributable package: $PLATFORM_ARCHIVE_NAME"
else
    echo "Error: Failed to create the distributable package."
    exit 1
fi

echo "You can find the final package in the root directory."