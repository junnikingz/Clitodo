# CliTodo Terminal v1.0

A hierarchical terminal workspace engine designed for cross-platform task tracking. Built with python-curses, it features mouse-click interaction, multi-line text wrapping for long tasks or subtasks, layout boundary controls, and a portable environment framework.

Developed by **Jiokuach Chuol**.

---

## Features

* **Multi-Line Text Wrapping:** Long tasks and subtasks wrap over multiple rows instead of truncating or breaking.
* **Mouse & Keyboard Navigation:** Click tabs, rows, checkboxes, and action panels directly, or navigate using keyboard hotkeys (`TAB`, `Arrow Keys`, `ENTER`).
* **Layout Guardrails:** Position and rendering loops prevent crashes (`wmove() ERR`) during window adjustments.
* **JSON Storage Engine:** Saves category listings, configurations, and parent-child items via local database serialization.
* **Dual-Platform Portability:** Runs on Windows and adapts to Linux distributions.

---

## Deployment

### Windows Installation
1. Ensure Python 3.x is installed.
2. Install the `windows-curses` dependency:
   ```bash
   pip install windows-curses