# =========================================================================
#  CliTodo Workspace Engine v3.6 (Cross-Platform & Portable)
#  Copyright (C) 2026 JUNIOR
#  Licensed under the GNU General Public License v3
# =========================================================================

import curses
import os
import json
import sys

class AdvancedTUITemplate:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        
        # --- FREEZE WINDOW CONTROLS (WINDOWS ONLY INTEROP) ---
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                if hwnd:
                    GWL_STYLE = -16
                    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
                    
                    WS_MAXIMIZEBOX = 0x00010000
                    WS_THICKFRAME = 0x00040000
                    style &= ~WS_MAXIMIZEBOX
                    style &= ~WS_THICKFRAME
                    
                    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
                    
                    SWP_FRAMECHANGED = 0x0020
                    SWP_NOMOVE = 0x0002
                    SWP_NOSIZE = 0x0001
                    SWP_NOZORDER = 0x0004
                    ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER)
            except Exception:
                pass

        # Core UI State
        self.categories = ["PRODUCTIVITY", "WORK", "HOME", "HOBBIES"]
        self.current_category_idx = 0
        
        # Structural Zones: 0: Tabs, 1: Tasks Grid, 2: Text Input, 3: Bottom Action Buttons
        self.current_zone = 0
        self.input_text = ""
        
        # Selection Navigation Pointers
        self.selected_row_idx = 0    
        self.selected_column = 0     # 0: Checkbox, 1: Add Subtask, 2: Delete Row
        self.selected_btn_idx = 0    
        self.top_line = 0            
        
        # Storage Array
        self.items = []
        self.load_data()
        
        # Curses setup
        curses.curs_set(0)
        self.stdscr.keypad(True)
        
        # --- ENABLE MOUSE MASK ---
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        # Explicit terminal escape code sequences to allow mouse tracking on terminal environments
        print('\033[?1003h', end="", flush=True) 
        
        # Component layout geometry dimensions
        self.header_h = 5 
        self.controls_h = 7          
        self.list_h = curses.LINES - self.header_h - self.controls_h
        
        # Layout coordinate trackers
        self.tab_positions = []
        self.btn_positions = []
        self.visible_row_map = []
        
        # Sub-windows setup
        self.header_win = curses.newwin(self.header_h, curses.COLS, 0, 0)
        self.list_win = curses.newwin(self.list_h, curses.COLS, self.header_h, 0)
        self.controls_win = curses.newwin(self.controls_h, curses.COLS, self.header_h + self.list_h, 0)

    def load_data(self):
        if os.path.exists("db_v2.json"):
            with open("db_v2.json", "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.items = data.get("items", [])
                        self.categories = data.get("categories", ["PRODUCTIVITY", "WORK", "HOME", "HOBBIES"])
                    elif isinstance(data, list):
                        self.items = data
                except json.JSONDecodeError:
                    self.items = []
        else:
            self.items = [
                {"category": "PRODUCTIVITY", "label": "Review blueprint layout", "checked": False, "subtasks": []},
                {"category": "WORK", "label": "Build Rust practical application TUI", "checked": False, "subtasks": []}
            ]

    def save_data(self):
        with open("db_v2.json", "w", encoding="utf-8") as f:
            json.dump({"categories": self.categories, "items": self.items}, f, indent=4)

    # =========================================================================
    # RENDER ENGINE PIPELINES
    # =========================================================================
    def update_header(self):
        self.header_win.erase()
        self.header_win.box()
        self.header_win.addstr(1, 2, "CliTodo Terminal By Jiokuach Chuol v1.0 (Portable Mode)", curses.A_BOLD)
        self.header_win.addstr(1, max(2, curses.COLS - 48), "TAB: Jump Zone | ENTER/MOUSE-CLICK: Execute")
        
        self.tab_positions = []
        start_x = 4
        for idx, tab in enumerate(self.categories):
            is_active_tab = (idx == self.current_category_idx)
            is_active_zone = (self.current_zone == 0)
            
            if is_active_tab and is_active_zone:
                style = curses.A_REVERSE | curses.A_BOLD
            elif is_active_tab:
                style = curses.A_UNDERLINE | curses.A_BOLD
            else:
                style = curses.A_NORMAL
                
            tab_fmt = f"  {tab}  "
            try:
                self.header_win.addstr(3, start_x, tab_fmt, style)
                self.tab_positions.append((start_x, start_x + len(tab_fmt)))
                start_x += len(tab_fmt) + 2
            except curses.error:
                pass
            
        self.header_win.noutrefresh()

    def build_flat_render_list(self):
        flat_list = []
        for parent_idx, item in enumerate(self.items):
            if item["category"] != self.categories[self.current_category_idx]:
                continue
            flat_list.append({"type": "parent", "ref": item, "global_idx": parent_idx, "sub_idx": None})
            for sub_idx, sub in enumerate(item["subtasks"]):
                flat_list.append({"type": "subtask", "ref": sub, "global_idx": parent_idx, "sub_idx": sub_idx})
        return flat_list

    def wrap_text(self, text, width):
        """Splits a string into a list of substrings wrapped cleanly to a maximum width."""
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            if len(word) > width:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = []
                lines.append(word[:width])
                continue
            if sum(len(w) + 1 for w in current_line) + len(word) <= width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines if lines else [""]

    def update_list(self):
        self.list_win.erase()
        self.list_win.box()
        
        flat_rows = self.build_flat_render_list()
        max_display_lines = self.list_h - 2
        self.list_win.addstr(0, 2, f"[ Tasks Box Panel ({len(flat_rows)} items) ]")
        
        if not flat_rows:
            self.list_win.addstr(2, 4, "(No tasks present in this category context)", curses.A_DIM)
            self.visible_row_map = []
            self.list_win.noutrefresh()
            return

        sub_btn_x = max(50, curses.COLS - 32)
        del_btn_x = max(64, curses.COLS - 16)
        text_content_width = sub_btn_x - 8

        all_rendered_lines = []
        for idx, row_data in enumerate(flat_rows):
            item_ref = row_data["ref"]
            status = "X" if item_ref["checked"] else " "
            is_item_focused = (self.current_zone == 1 and idx == self.selected_row_idx)
            
            if row_data["type"] == "parent":
                wrapped_lines = self.wrap_text(item_ref["label"], text_content_width)
                for line_num, text_chunk in enumerate(wrapped_lines):
                    all_rendered_lines.append({
                        "item_idx": idx,
                        "is_first_line": (line_num == 0),
                        "type": "parent",
                        "display_str": f" [{status}] {text_chunk}" if line_num == 0 else f"       {text_chunk}",
                        "is_focused": is_item_focused
                    })
            elif row_data["type"] == "subtask":
                wrapped_lines = self.wrap_text(item_ref["label"], text_content_width - 4)
                for line_num, text_chunk in enumerate(wrapped_lines):
                    all_rendered_lines.append({
                        "item_idx": idx,
                        "is_first_line": (line_num == 0),
                        "type": "subtask",
                        "display_str": f"    └── [{status}] {text_chunk}" if line_num == 0 else f"         {text_chunk}",
                        "is_focused": is_item_focused
                    })

        if self.top_line > max(0, len(all_rendered_lines) - max_display_lines):
            self.top_line = max(0, len(all_rendered_lines) - max_display_lines)

        focused_line_indices = [i for i, line in enumerate(all_rendered_lines) if line["item_idx"] == self.selected_row_idx]
        if focused_line_indices:
            first_f_line = focused_line_indices[0]
            last_f_line = focused_line_indices[-1]
            if first_f_line < self.top_line:
                self.top_line = first_f_line
            elif last_f_line >= self.top_line + max_display_lines:
                self.top_line = last_f_line - max_display_lines + 1

        self.visible_row_map = []
        for screen_y in range(max_display_lines):
            line_idx = self.top_line + screen_y
            if line_idx >= len(all_rendered_lines):
                break
                
            line_data = all_rendered_lines[line_idx]
            self.visible_row_map.append(line_data["item_idx"])
            
            style = curses.A_REVERSE if (line_data["is_focused"] and self.selected_column == 0) else curses.A_NORMAL
            
            try:
                self.list_win.addstr(1 + screen_y, 2, f"{line_data['display_str']:<{text_content_width + 5}}", style)
                
                if line_data["is_first_line"]:
                    if line_data["type"] == "parent":
                        s_style = curses.A_REVERSE if (line_data["is_focused"] and self.selected_column == 1) else curses.A_DIM
                        self.list_win.addstr(1 + screen_y, sub_btn_x, "[+ SUBTASK]", s_style)
                    d_style = curses.A_REVERSE if (line_data["is_focused"] and self.selected_column == 2) else curses.A_DIM
                    self.list_win.addstr(1 + screen_y, del_btn_x, "[DEL]", d_style)
            except curses.error:
                pass

        self.list_win.noutrefresh()

    def update_controls(self):
        self.controls_win.erase()
        self.controls_win.box()
        
        self.controls_win.addstr(1, 2, "Input Field:")
        input_box_fmt = f"[ {self.input_text:<45} ]"
        if self.current_zone == 2:
            self.controls_win.addstr(1, 16, input_box_fmt, curses.A_REVERSE)
        else:
            self.controls_win.addstr(1, 16, input_box_fmt)
            
        buttons = ["  SAVE  ", " RELOAD ", " ADD TAB ", "  EXIT  "]
        self.controls_win.addstr(4, 2, "Actions Panel:")
        
        self.btn_positions = []
        start_x = 16
        for idx, btn_text in enumerate(buttons):
            formatted_btn = f"[ {btn_text} ]"
            if self.current_zone == 3 and idx == self.selected_btn_idx:
                self.controls_win.addstr(4, start_x, formatted_btn, curses.A_REVERSE)
            else:
                self.controls_win.addstr(4, start_x, formatted_btn)
                
            self.btn_positions.append((start_x, start_x + len(formatted_btn)))
            start_x += len(formatted_btn) + 2
            
        self.controls_win.noutrefresh()

    def render_all(self):
        try:
            self.stdscr.noutrefresh()
            self.update_header()
            self.update_list()
            self.update_controls()
            curses.doupdate()
        except curses.error:
            pass

    def get_inline_input(self, prompt_text=""):
        curses.curs_set(1)
        buffer = list(self.input_text) if not prompt_text else []
        win_target = self.controls_win 
        
        max_view_width = 43 
        
        while True:
            display_str = "".join(buffer)
            if len(display_str) >= max_view_width:
                view_start = len(display_str) - max_view_width + 1
                visible_chunk = display_str[view_start:]
            else:
                view_start = 0
                visible_chunk = display_str

            try:
                if not prompt_text:
                    win_target.addstr(1, 18, f"{visible_chunk:<{max_view_width}}")
                    win_target.move(1, min(18 + len(visible_chunk), curses.COLS - 1))
                    win_target.refresh()
                else:
                    clear_spacer = " " * max(1, curses.COLS - 20)
                    win_target.addstr(1, 2, f"{clear_spacer:<45}") 
                    
                    win_target.addstr(1, 2, f"Subtask Name: [ {visible_chunk:<{max_view_width}} ]")
                    win_target.move(1, min(18 + len(visible_chunk), curses.COLS - 1))
                    win_target.refresh()
            except curses.error:
                pass
                
            ch = win_target.getch()
            if ch in (10, 13): # ENTER
                break
            elif ch == 27: # ESC
                buffer = []
                break
            elif ch in (curses.KEY_BACKSPACE, 8, 263): # BACKSPACE
                if buffer:
                    buffer.pop()
            elif 32 <= ch <= 126 and len(buffer) < 200:
                buffer.append(chr(ch))
                
        curses.curs_set(0)
        if prompt_text:
            self.update_controls()
            
        return "".join(buffer)

    def add_category_tab(self):
        self.controls_win.erase()
        self.controls_win.box()
        self.controls_win.addstr(1, 2, "Enter New Tab Name:")
        
        curses.curs_set(1)
        buffer = []
        while True:
            try:
                self.controls_win.addstr(1, 23, f"{''.join(buffer):<20}")
                self.controls_win.move(1, min(23 + len(buffer), curses.COLS - 1))
                self.controls_win.refresh()
            except curses.error:
                pass
            
            ch = self.controls_win.getch()
            if ch in (10, 13):
                break
            elif ch == 27:
                buffer = []
                break
            elif ch in (curses.KEY_BACKSPACE, 8, 263):
                if buffer:
                    buffer.pop()
            elif 32 <= ch <= 126 and len(buffer) < 18:
                buffer.append(chr(ch).upper())
                
        curses.curs_set(0)
        new_tab_name = "".join(buffer).strip()
        
        if new_tab_name and new_tab_name not in self.categories:
            self.categories.append(new_tab_name)
            self.current_category_idx = len(self.categories) - 1
            self.selected_row_idx = 0
            self.top_line = 0
            self.save_data()

    def execute_grid_action(self, flat_rows):
        if not flat_rows: return
        if self.selected_row_idx >= len(flat_rows):
            self.selected_row_idx = max(0, len(flat_rows) - 1)
            
        current_row = flat_rows[self.selected_row_idx]
        g_idx = current_row["global_idx"]
        s_idx = current_row["sub_idx"]
        
        if g_idx >= len(self.items): return
        
        if self.selected_column == 0: 
            if current_row["type"] == "parent":
                self.items[g_idx]["checked"] = not self.items[g_idx]["checked"]
            else:
                self.items[g_idx]["subtasks"][s_idx]["checked"] = not self.items[g_idx]["subtasks"][s_idx]["checked"]
            
        elif self.selected_column == 1 and current_row["type"] == "parent": 
            child_name = self.get_inline_input(prompt_text="subtask")
            if child_name.strip():
                self.items[g_idx]["subtasks"].append({"label": child_name.strip(), "checked": False})
                
        elif self.selected_column == 2: 
            if current_row["type"] == "parent":
                self.items.pop(g_idx)
            else:
                self.items[g_idx]["subtasks"].pop(s_idx)
            self.selected_row_idx = max(0, self.selected_row_idx - 1)
            self.top_line = max(0, self.top_line - 1)

    def execute_button_action(self):
        if self.selected_btn_idx == 0:   
            if self.input_text:
                self.items.append({
                    "category": self.categories[self.current_category_idx],
                    "label": self.input_text,
                    "checked": False,
                    "subtasks": []
                })
                self.input_text = ""
            self.save_data()
        elif self.selected_btn_idx == 1: 
            self.load_data()
            self.selected_row_idx = 0
            self.top_line = 0
        elif self.selected_btn_idx == 2:
            self.add_category_tab()
            self.current_zone = 0 
        elif self.selected_btn_idx == 3: 
            return True 
        return False

    def handle_mouse_click(self, flat_rows):
        try:
            _, mx, my, _, bstate = curses.getmouse()
            if not (bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_PRESSED):
                return False
        except curses.error:
            return False

        if my == 3:
            for idx, (start_x, end_x) in enumerate(self.tab_positions):
                if start_x <= mx < end_x:
                    self.current_zone = 0
                    self.current_category_idx = idx
                    self.selected_row_idx = 0
                    self.top_line = 0
                    return False

        if self.header_h <= my < (self.header_h + self.list_h):
            relative_y = my - self.header_h - 1 
            try:
                if 0 <= relative_y < len(self.visible_row_map):
                    target_idx = self.visible_row_map[relative_y]
                    if 0 <= target_idx < len(flat_rows):
                        self.current_zone = 1
                        self.selected_row_idx = target_idx
                        
                        sub_btn_x = max(50, curses.COLS - 32)
                        del_btn_x = max(64, curses.COLS - 16)
                        
                        if mx >= del_btn_x:
                            self.selected_column = 2 
                        elif mx >= sub_btn_x and flat_rows[target_idx]["type"] == "parent":
                            self.selected_column = 1 
                        else:
                            self.selected_column = 0 
                            
                        self.execute_grid_action(flat_rows)
                        return False
            except Exception:
                pass

        controls_start_y = self.header_h + self.list_h
        if controls_start_y <= my < curses.LINES:
            relative_controls_y = my - controls_start_y
            
            if relative_controls_y == 1: 
                if 16 <= mx <= 65:
                    self.current_zone = 2
                    self.input_text = ""
                    new_label = self.get_inline_input()
                    if new_label.strip():
                        self.input_text = new_label.strip()
                        
            elif relative_controls_y == 4: 
                for idx, (start_x, end_x) in enumerate(self.btn_positions):
                    if start_x <= mx < end_x:
                        self.current_zone = 3
                        self.selected_btn_idx = idx
                        return self.execute_button_action()
                        
        return False

    def run_loop(self):
        while True:
            self.render_all()
            key = self.stdscr.getch()
            max_display = self.list_h - 2
            flat_rows = self.build_flat_render_list()
            
            if key == curses.KEY_MOUSE:
                should_exit = self.handle_mouse_click(flat_rows)
                if should_exit: break
                continue

            if key == 9: 
                self.current_zone = (self.current_zone + 1) % 4
                self.selected_row_idx = 0
                self.selected_column = 0
                self.top_line = 0
                continue

            if self.current_zone == 0:
                if key == curses.KEY_LEFT:
                    self.current_category_idx = (self.current_category_idx - 1) % len(self.categories)
                elif key == curses.KEY_RIGHT:
                    self.current_category_idx = (self.current_category_idx + 1) % len(self.categories)

            elif self.current_zone == 1 and flat_rows:
                if key == curses.KEY_UP:
                    if self.selected_row_idx > 0:
                        self.selected_row_idx -= 1
                        if self.selected_row_idx < self.top_line:
                            self.top_line = self.selected_row_idx
                elif key == curses.KEY_DOWN:
                    if self.selected_row_idx < len(flat_rows) - 1:
                        self.selected_row_idx += 1
                        if self.selected_row_idx >= self.top_line + max_display:
                            self.top_line += 1
                            
                elif key == curses.KEY_LEFT:
                    if flat_rows[self.selected_row_idx]["type"] == "parent":
                        self.selected_column = (self.selected_column - 1) % 3
                    else:
                        self.selected_column = 0 if self.selected_column == 2 else 2
                        
                elif key == curses.KEY_RIGHT:
                    if flat_rows[self.selected_row_idx]["type"] == "parent":
                        self.selected_column = (self.selected_column + 1) % 3
                    else:
                        self.selected_column = 2 if self.selected_column == 0 else 0
                        
                elif key in (10, 13, ord(' ')):
                    self.execute_grid_action(flat_rows)

            elif self.current_zone == 2:
                if key in (10, 13):
                    self.input_text = ""
                    new_label = self.get_inline_input()
                    if new_label.strip():
                        self.input_text = new_label.strip()

            elif self.current_zone == 3:
                if key == curses.KEY_LEFT:
                    self.selected_btn_idx = (self.selected_btn_idx - 1) % 4
                elif key == curses.KEY_RIGHT:
                    self.selected_btn_idx = (self.selected_btn_idx + 1) % 4
                elif key in (10, 13):
                    should_exit = self.execute_button_action()
                    if should_exit: break

advanced_main = lambda stdscr: AdvancedTUITemplate(stdscr).run_loop()

if __name__ == "__main__":
    curses.wrapper(advanced_main)