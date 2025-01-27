import tkinter as tk
from tkinter import ttk, scrolledtext, font
import difflib

class ModernDiffChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Diff Checker")
        self.root.geometry("1200x800")
        self.style = ttk.Style()
        self.configure_styles()
        
        self.create_widgets()
        self.setup_tags()

    def configure_styles(self):
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6)
        self.style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'), background='#e0e0e0')
        self.style.map('TButton',
            foreground=[('active', 'white'), ('!active', 'black')],
            background=[('active', '#0052cc'), ('!active', '#e1e1e1')]
        )

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Input panels
        input_panels = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        input_panels.pack(fill=tk.BOTH, expand=True)

        # Original text panel
        original_frame = ttk.Frame(input_panels)
        self.create_text_panel(original_frame, "Original Text", 'original')
        input_panels.add(original_frame)

        # Modified text panel
        modified_frame = ttk.Frame(input_panels)
        self.create_text_panel(modified_frame, "Modified Text", 'modified')
        input_panels.add(modified_frame)

        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="🔄 Compare", command=self.compare_texts, style='Accent.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="🧹 Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=2)
        
        # Diff output
        diff_frame = ttk.Frame(main_frame)
        diff_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(diff_frame, text="Comparison Results", style='Header.TLabel').pack(pady=(5, 0))
        self.diff_output = scrolledtext.ScrolledText(
            diff_frame, wrap=tk.NONE, font=('Consolas', 10), 
            bg='#f8f9fa', padx=10, pady=10, spacing3=3
        )
        self.diff_output.pack(fill=tk.BOTH, expand=True)

    def create_text_panel(self, parent, title, side):
        container = ttk.Frame(parent)
        header = ttk.Frame(container)
        header.pack(fill=tk.X)
        
        ttk.Label(header, text=title, style='Header.TLabel').pack(side=tk.LEFT, padx=5)
        ttk.Button(header, text="× Clear", command=lambda: self.clear_panel(side)).pack(side=tk.RIGHT)
        
        text_widget = scrolledtext.ScrolledText(
            container, wrap=tk.WORD, font=('Consolas', 10),
            bg='white', padx=10, pady=10, undo=True
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        setattr(self, f'{side}_text', text_widget)
        container.pack(fill=tk.BOTH, expand=True)

    def setup_tags(self):
        tags = {
            'add': {'foreground': '#155724', 'background': '#d4edda'},
            'remove': {'foreground': '#721c24', 'background': '#f8d7da'},
            'header': {'foreground': '#004085', 'background': '#cce5ff'},
            'context': {'foreground': '#6c757d'}
        }
        for tag, config in tags.items():
            self.diff_output.tag_config(tag, **config)

    def compare_texts(self):
        text1 = self.original_text.get('1.0', tk.END).splitlines()
        text2 = self.modified_text.get('1.0', tk.END).splitlines()
        
        diff = difflib.unified_diff(
            text1, text2,
            fromfile='Original',
            tofile='Modified',
            n=9999
        )
        
        self.diff_output.delete('1.0', tk.END)
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
            tag = 'context'
        
        self.diff_output.insert(tk.END, line + '\n', tag)

    def clear_panel(self, side):
        getattr(self, f'{side}_text').delete('1.0', tk.END)

    def clear_all(self):
        self.original_text.delete('1.0', tk.END)
        self.modified_text.delete('1.0', tk.END)
        self.diff_output.delete('1.0', tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernDiffChecker(root)
    root.mainloop()
