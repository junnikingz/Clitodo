import sys
from cx_Freeze import setup, Executable

# 1. FIX: Define the icon mapping identifier for the MSI engine database
# The 9th column points to our explicit internal Icon asset ID ("MainAppIcon.ico")
shortcut_table = [
    (
        "DesktopShortcut",           # Component Unique Identifier Key
        "DesktopFolder",             # Destination target location property
        "CliTodo Workspace",         # Readable Label displayed on user's desktop
        "TARGETDIR",                 # Installation directory component anchor
        "[TARGETDIR]cli_todo.exe",   # Target system path pointer pointing to binary
        None,                        # Execution arguments
        "Professional CLI Todo App", # Desktop hover context description tag
        None,                        # Hotkey triggers
        "MainAppIcon.ico",           # FIX: Points directly to the registered MSI Icon object ID below
        0,                           # Icon index reference channel
        None,                        # Show window execution options
        "TARGETDIR",                 # Working execution directory context
    )
]

# 2. FIX: Explicitly register the raw icon data inside the Windows Installer table
# This bakes the icon asset metadata directly inside the final .msi payload package file!
msi_data = {
    "Shortcut": shortcut_table,
    "Icon": [("MainAppIcon.ico", "app_icon.ico")] 
}

bdist_msi_options = {
    "data": msi_data,
    "all_users": True, 
}

build_exe_options = {
    "include_files": ["db_v2.json", "app_icon.ico", "LICENSE"], 
    "excludes": [],
}

setup(
    name="CliTodo Terminal",
    version="1.0",
    description="Professional Hierarchical Terminal Workspace System Layout Framework",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[
        Executable(
            script="cli_todo.py",
            base=None, 
            icon="app_icon.ico", 
            target_name="cli_todo.exe"
        )
    ]
)