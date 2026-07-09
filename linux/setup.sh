#!/bin/bash

# =========================================================================
#  CliTodo Workspace Environment Automated Installer for Linux Desktop
#  Copyright (C) 2026 JUNIOR
#  Licensed under the GNU General Public License v3
# =========================================================================

# Stop on any unexpected script execution errors
set -e

echo "Starting CliTodo Linux Environment Deployment Setup..."

# 1. Define sandboxed local install destination paths
TARGET_DIR="$HOME/.local/share/clitodo"
APP_LAUNCHER_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"

# 2. Create clean destination directory trees if they don't exist
mkdir -p "$TARGET_DIR"
mkdir -p "$APP_LAUNCHER_DIR"
mkdir -p "$ICON_DIR"

# 3. Check for app source code file dependencies
if [ ! -f "cli_todo.py" ]; then
    echo "Error: cli_todo.py not found in the current working directory!"
    echo "Please run this installer from inside your source project folder."
    exit 1
fi

# 4. Sync application source file binaries and icons to the deployment sandbox
echo "Staging application code assets..."
cp cli_todo.py "$TARGET_DIR/"
if [ -f "db_v2.json" ]; then
    cp db_v2.json "$TARGET_DIR/"
fi

# Set up an app icon shortcut (Fallback to a default generic terminal grid design if none exists)
if [ -f "app_icon.png" ]; then
    cp app_icon.png "$ICON_DIR/clitodo.png"
else
    # Use a generic desktop system fallback utility icon link if custom asset is absent
    ICON_DIR="/usr/share/icons/hicolor/scalable/apps"
fi

# 5. Dynamically compile the native .desktop launcher with absolute system path tags
echo "Compiling Linux Desktop Configuration Entry specifications..."
CAT_DESKTOP_FILE="$APP_LAUNCHER_DIR/clitodo.desktop"

cat << EOF > "$CAT_DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=CliTodo Workspace
Comment=Advanced Terminal Task Management Engine
Exec=python3 $TARGET_DIR/cli_todo.py
Icon=clitodo
Terminal=true
Categories=Utility;Office;TaskManagement;
StartupNotify=true
X-KeepTerminal=true
EOF

# 6. Adjust executable permission modes across binaries
echo "Setting executable file permission rules..."
chmod +x "$TARGET_DIR/cli_todo.py"
chmod +x "$CAT_DESKTOP_FILE"

# 7. Force desktop systems to scan the launcher cache registers instantly
echo "Updating desktop application launcher databases..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APP_LAUNCHER_DIR"
fi

echo "Deployment Complete! CliTodo is now available in your Application Menu drawer."
echo "   You can now pin it directly to your system Taskbar Dock panel!"