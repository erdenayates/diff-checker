import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import difflib
import json
import threading
from datetime import datetime

class UltimateDiffChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Diff Checker Pro")
        self.root.geometry("1400x900")
        self.setup_config()
        self.create_menu()
        self.init_ui()
        self.bind_shortcuts()
        self.set_theme(self.config['theme'])
        
        # Initialize real-time comparison thread
        self.compare_active = False
        self.text_change_flag = False
        self.start_comparison_thread()

    def setup_config(self):
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {
                'theme': 'light',
                'colors': {
                    'add': '#d4edda',
                    'remove': '#f8d7da',
                    'header': '#cce5ff',
                    'context': '#f8f9fa'
                },
                'recent_files': []
            }

    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Original", command=lambda: self.open_file('original'))
        file_menu.add_command(label="Open Modified", command=lambda: self.open_file('modified'))
        file_menu.add_command(label="Export Diff", command=self.export_diff)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_checkbutton(label="Dark Mode", command=self.toggle_theme)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="View", menu=view_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

    def init_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Three-pane view
        self.panes = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.panes.pack(fill=tk.BOTH, expand=True)
        
        # Original panel
        self.original_frame = self.create_editor_panel("Original", 'original')
        self.panes.add(self.original_frame)
        
        # Modified panel
        self.modified_frame = self.create_editor_panel("Modified", 'modified')
        self.panes.add(self.modified_frame)
        
        # Diff panel
        self.diff_frame = ttk.Frame(self.panes)
        self.create_diff_panel()
        self.panes.add(self.diff_frame)
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=5, pady=2)

    def create_editor_panel(self, title, side):
        frame = ttk.Frame(self.panes)
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X)
        ttk.Label(header, text=title, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Button(header, text="📁", command=lambda: self.open_file(side)).pack(side=tk.RIGHT)
        ttk.Button(header, text="×", command=lambda: self.clear_panel(side)).pack(side=tk.RIGHT)
        
        # Text area
        text_widget = scrolledtext.ScrolledText(
            frame, wrap=tk.NONE, font=('Consolas', 10),
            undo=True, maxundo=100
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.bind('<KeyRelease>', self.mark_text_changed)
        
        setattr(self, f'{side}_text', text_widget)
        return frame

    def create_diff_panel(self):
        self.unified_diff = scrolledtext.ScrolledText(
            self.diff_frame, wrap=tk.NONE, font=('Consolas', 10)
        )
        self.unified_diff.pack(fill=tk.BOTH, expand=True)
        self.setup_tags()

    def setup_tags(self):
        tags = {
            'add': {'background': self.config['colors']['add']},
            'remove': {'background': self.config['colors']['remove']},
            'header': {'background': self.config['colors']['header']}
        }
        for tag, style in tags.items():
            self.unified_diff.tag_config(tag, **style)

    def start_comparison_thread(self):
        self.compare_active = True
        threading.Thread(target=self.compare_thread, daemon=True).start()

    def compare_thread(self):
        while self.compare_active:
            if self.text_change_flag:
                self.compare_texts()
                self.text_change_flag = False
            self.root.update_idletasks()

    def mark_text_changed(self, event=None):
        self.text_change_flag = True

    def compare_texts(self):
        text1 = self.original_text.get('1.0', tk.END).splitlines()
        text2 = self.modified_text.get('1.0', tk.END).splitlines()
        
        diff = difflib.unified_diff(
            text1, text2,
            fromfile='Original',
            tofile='Modified',
            n=9999
        )
        
        self.unified_diff.delete('1.0', tk.END)
        for line in diff:
            self.insert_diff_line(line)

    def insert_diff_line(self, line):
        if line.startswith('+'):
            tag = 'add'
        elif line.startswith('-'):
            tag = 'remove'
        elif line.startswith('@@'):
            tag = 'header'
        else:
            tag = ''
        
        self.unified_diff.insert(tk.END, line + '\n', tag)

    def open_file(self, side):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as f:
                content = f.read()
            getattr(self, f'{side}_text').delete('1.0', tk.END)
            getattr(self, f'{side}_text').insert('1.0', content)
            self.config['recent_files'].append(file_path)
            self.save_config()

    def export_diff(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".diff", filetypes=[("Diff Files", "*.diff"), ("All Files", "*.*")])
        if file_path:
            diff_content = self.unified_diff.get('1.0', tk.END)
            with open(file_path, 'w') as f:
                f.write(diff_content)
            messagebox.showinfo("Export Successful", f"Diff exported to {file_path}")

    def clear_panel(self, side):
        getattr(self, f'{side}_text').delete('1.0', tk.END)

    def toggle_theme(self):
        if self.config['theme'] == 'light':
            self.set_theme('dark')
        else:
            self.set_theme('light')
        self.save_config()

    def set_theme(self, theme):
        self.config['theme'] = theme
        bg = '#333333' if theme == 'dark' else '#ffffff'
        fg = '#ffffff' if theme == 'dark' else '#000000'
        
        self.root.configure(background=bg)
        for widget in [self.original_text, self.modified_text, self.unified_diff]:
            widget.configure(bg=bg, fg=fg, insertbackground=fg)

    def bind_shortcuts(self):
        self.root.bind('<Control-o>', lambda e: self.open_file('original'))
        self.root.bind('<Control-s>', lambda e: self.export_diff())
        self.root.bind('<Control-d>', lambda e: self.toggle_theme())

    def show_about(self):
        messagebox.showinfo("About", "Ultimate Diff Checker Pro\nVersion 1.0\n\nA powerful tool for comparing text files.")

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateDiffChecker(root)
    root.mainloop()
