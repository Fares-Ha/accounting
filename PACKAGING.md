# Packaging Ajyad Accountant

This guide provides instructions for packaging the Ajyad Accountant application for Windows, macOS, and Linux.

## Prerequisites

Before you can package the application, you will need to have the following software installed:

*   Python 3.6 or later
*   pip (the Python package installer)

You will also need to install the following Python packages:

*   `pyinstaller`
*   `pyqt6`
*   `sqlalchemy`
*   `bcrypt`
*   `reportlab`
*   `openpyxl`

You can install these packages by running the following command:

```
pip install -r requirements.txt
pip install pyinstaller
```

## Packaging Instructions

Once you have installed the prerequisites, you can package the application by running the `package.sh` script:

```
./package.sh
```

This will create a distributable package in the `dist` directory. The type of package created will depend on your operating system:

*   **Windows:** A `.zip` file containing the application executable.
*   **macOS:** A `.dmg` file containing the application bundle.
*   **Linux:** A `.tar.gz` file containing the application executable.

### Windows

On Windows, the `package.sh` script will create a `Ajyad Accountant-windows.zip` file in the `dist` directory. To run the application, simply extract the contents of the zip file and double-click on the `Ajyad Accountant.exe` file.

### macOS

On macOS, the `package.sh` script will create a `Ajyad Accountant-mac.dmg` file in the `dist` directory. To run the application, simply open the `.dmg` file and drag the `Ajyad Accountant.app` bundle to your `Applications` folder.

### Linux

On Linux, the `package.sh` script will create a `Ajyad Accountant-linux.tar.gz` file in the `dist` directory. To run the application, simply extract the contents of the `.tar.gz` file and run the `Ajyad Accountant` executable.