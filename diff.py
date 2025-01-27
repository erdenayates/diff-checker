import tkinter as tk
from tkinter import scrolledtext, ttk
import difflib

class DiffCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Diff Checker")
        
        # Create PanedWindow for resizable panels
        paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (Original text)
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Original Text").pack(padx=5, pady=2)
        self.left_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, width=40)
        self.left_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(left_frame, text="Clear", command=lambda: self.left_text.delete('1.0', tk.END)).pack(pady=2)
        
        # Right panel (Modified text)
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Modified Text").pack(padx=5, pady=2)
        self.right_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=40)
        self.right_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(right_frame, text="Clear", command=lambda: self.right_text.delete('1.0', tk.END)).pack(pady=2)
        
        # Compare button
        compare_frame = ttk.Frame(root)
        compare_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(compare_frame, text="Compare Texts", command=self.compare_texts).pack(side=tk.LEFT)
        ttk.Button(compare_frame, text="Clear Diff", command=lambda: self.diff_output.delete('1.0', tk.END)).pack(side=tk.LEFT, padx=5)
        
        # Diff output
        diff_frame = ttk.Frame(root)
        diff_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(diff_frame, text="Diff Output").pack(pady=2)
        self.diff_output = scrolledtext.ScrolledText(
            diff_frame, wrap=tk.WORD, width=80, font=('Consolas', 10)
        )
        self.diff_output.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for coloring
        self.diff_output.tag_config('add', foreground='green')
        self.diff_output.tag_config('remove', foreground='red')
        self.diff_output.tag_config('header', foreground='blue')
        self.diff_output.tag_config('context', foreground='grey')
    
    def compare_texts(self):
        # Get texts from both panels
        text1 = self.left_text.get('1.0', tk.END).splitlines()
        text2 = self.right_text.get('1.0', tk.END).splitlines()
        
        # Generate unified diff with all lines in context
        diff = difflib.unified_diff(
            text1, text2,
            fromfile='Original',
            tofile='Modified',
            n=9999  # Show all lines
        )
        diff_lines = list(diff)
        
        # Clear previous diff
        self.diff_output.delete('1.0', tk.END)
        
        # Insert diff lines with appropriate tags
        for line in diff_lines:
            if line.startswith('+'):
                self.diff_output.insert(tk.END, line + '\n', 'add')
            elif line.startswith('-'):
                self.diff_output.insert(tk.END, line + '\n', 'remove')
            elif line.startswith('@@'):
                self.diff_output.insert(tk.END, line + '\n', 'header')
            else:
                self.diff_output.insert(tk.END, line + '\n', 'context')

if __name__ == "__main__":
    root = tk.Tk()
    app = DiffCheckerApp(root)
    root.geometry("1000x800")
    root.mainloop()
