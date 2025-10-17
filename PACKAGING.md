# How to Package Ajyad Accountant

This guide provides instructions for packaging the Ajyad Accountant application for **Windows, macOS, and Linux**.

The process uses **PyInstaller** to bundle the Python application and its dependencies into a single executable file.

---

## 1. Prerequisites

Before you can package the application, you must have the following software installed:

*   **Python 3.8+**
*   **Pip** (the Python package installer)

## 2. Installation

Follow these steps to set up your environment:

**A. Install Application Dependencies:**

First, install all the Python packages required by the application. From the root directory of the project, run:

```bash
pip install -r requirements.txt
```

**B. Install PyInstaller:**

Next, install PyInstaller, the tool used for packaging:

```bash
pip install pyinstaller
```

---

## 3. Running the Packaging Script

Once you have installed all the prerequisites, you can package the application by running the `package.sh` script from the project's root directory:

```bash
./package.sh
```

The script will automatically perform the following steps:
1.  Clean up any previous builds.
2.  Run PyInstaller to create a single executable file.
3.  Create a platform-specific distributable archive (`.zip` for Windows, `.dmg` for macOS, `.tar.gz` for Linux).

Upon successful completion, you will find the final package in the root directory of the project.

---

## 4. Platform-Specific Instructions

### ❖ Windows

*   **Output:** `Ajyad Accountant-windows.zip`
*   **To Run:**
    1.  Extract the contents of the zip file.
    2.  Double-click the `Ajyad Accountant.exe` file to run the application.

### ❖ macOS

*   **Output:** `Ajyad Accountant-macos.dmg`
*   **To Run:**
    1.  Double-click the `.dmg` file to mount it.
    2.  Drag the `Ajyad Accountant.app` bundle into your `/Applications` folder.
    3.  Eject the disk image and run the application from your Applications folder.

### ❖ Linux

*   **Output:** `Ajyad Accountant-linux.tar.gz`
*   **To Run:**
    1.  Extract the contents of the `.tar.gz` file: `tar -xzvf Ajyad Accountant-linux.tar.gz`
    2.  Navigate into the `dist` directory.
    3.  Make the application executable: `chmod +x "Ajyad Accountant"`
    4.  Run the application: `./"Ajyad Accountant"`

---

## 5. Troubleshooting

*   **"Command not found: pyinstaller"**: This means PyInstaller is not installed or not in your system's PATH. Make sure you have run `pip install pyinstaller`.
*   **"Permission denied" when running `./package.sh`**: You may need to make the script executable first. Run `chmod +x package.sh`.
*   **Packaging fails on Windows:** The script uses Python's built-in `zipfile` module and should be reliable. If it fails, ensure your Python installation is correct.
*   **App fails to start on Linux:** Some Linux distributions may require additional libraries to be installed for PyQt to work correctly (e.g., `libxcb-cursor0`). Check the PyQt documentation for your specific distribution.