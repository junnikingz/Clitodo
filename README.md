# CliTodo Terminal v1.0

A hierarchical terminal workspace engine designed for cross-platform task tracking. Built with `python-curses`, it features mouse-click interaction, multi-line text wrapping for long tasks or subtasks, layout boundary controls, and a portable environment framework.

Developed by **Jiokuach Chuol**.

---

## Pre-Built Downloads

If you want to use the application without compiling the source code yourself, the pre-built binaries are located directly inside the repository folders:

### For Windows Users

- **Portable Version** (`build/portable_windows/`)
  A completely self-contained, standalone version that requires no installation. Copy the `portable_windows` folder to any location, including a USB drive, and run `cli_todo.exe` to manage tasks locally.

- **Desktop Setup Installer** (`dist/`)
  Run the `CliTodo Terminal-1.0-amd64.msi` installation package to install the program on your system, configure the launch boundaries, and create a desktop shortcut.

### For Linux Users

- **Automated Deployment Script** (`dist/`)
  Navigate into the `dist` folder and execute the installer script. This maps paths, links taskbar configuration files, and integrates the workspace launcher into your desktop application menu.

---

## How to Build From Source

To compile and build these release binaries on your local machine, ensure you have Python 3.x and your build utilities installed, then follow these steps:

### 1. Preparation and Dependencies

Before starting the build process for either platform, make sure your workspace contains the source files and required assets:

**Source files:**
- `cli_todo.py`
- `setup.py`

**Required assets:**
- `db_v2.json`
- `app_icon.ico`
- `LICENSE`


```bash
# (dependency installation command to be added here)
```

### 2. Building the Windows Packages

Open your terminal (Command Prompt, PowerShell, or Git Bash) in the project root directory and run the compilation routines:

**To Build the Portable Standalone Version:**

```dos
python setup.py build
```

This processes your build choices and creates a standalone environment folder inside `build/portable_windows/` containing `cli_todo.exe` along with its shared library references.

**To Build the `.msi` System Installer:**

```dos
python setup.py bdist_msi
```

This compiles the deployment tables and generates your final setup executable inside the `dist/` folder.

### 3. Setting Up the Linux Version

Because Linux relies on the native system terminal environment, you do not need to compile the code into an executable. Instead, you build the installation link wrapper:

1. Move `cli_todo.py`, `install_linux.sh`, and `clitodo.desktop` into your workspace.
2. Grant executable permissions to your installation script:

   ```bash
   chmod +x install_linux.sh
   ```

3. Run the deployment script to register your system launcher files:

   ```bash
   ./install_linux.sh
   ```

---

## Features

- **Multi-Line Text Wrapping** — Long tasks and subtasks wrap over multiple rows instead of truncating or breaking.
- **Mouse and Keyboard Navigation** — Click tabs, rows, checkboxes, and action panels directly, or navigate using keyboard hotkeys (`TAB`, Arrow Keys, `ENTER`).
- **Layout Guardrails** — Position and rendering loops prevent crashes (`wmove() ERR`) during window adjustments.
- **JSON Storage Engine** — Saves category listings, configurations, and parent-child items via local database serialization.
- **Dual-Platform Portability** — Runs on Windows and adapts to Linux distributions with a locked-down, native terminal design.

---

## Navigation Scheme

| Action Key | Operation |
|---|---|
| `TAB` | Cycles focus through UI zones (Tabs → Task List → Input Box → Action Panel). |
| `UP` / `DOWN` Arrows | Scrolls through structured list indices inside the viewpane. |
| `LEFT` / `RIGHT` Arrows | Switches category header tabs or shifts button options. |
| `ENTER` / `SPACEBAR` | Toggles checkmarks, creates items, or activates button inputs. |
| `ESCAPE` | Wipes current textual input characters inside data fields. |

---

## Open Source Contributions and Bug Reports

This project is a public repository. Contributions can be submitted via the tracking workflows below.

### Reporting Bugs

If you encounter an application freeze, layout misalignment, or database exception, open a ticket:

1. Navigate to the **Issues** tab at the top of the GitHub project page.
2. Click **New Issue**.
3. Specify your platform configuration (Windows version or Linux distribution) and provide the exact traceback details or terminal state snapshots.

### Pull Requests

To introduce features or resolve issues, utilize the following workflow:

1. Fork the repository into your profile workspace.
2. Create a feature branch tracking your optimization:

   ```bash
   git checkout -b feature/optimization-name
   ```

3. Commit your modifications with clear references:

   ```bash
   git commit -m "Resolve rendering issue on narrow display configurations"
   ```

4. Push your changes to your remote fork:

   ```bash
   git push origin feature/optimization-name
   ```

5. Submit a Pull Request against the `main` branch for review and integration.

---

## License

This software is distributed under the GNU General Public License v3. Check the accompanying `LICENSE` document for complete guidelines.
