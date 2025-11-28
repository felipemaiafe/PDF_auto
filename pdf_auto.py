import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class PDFToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("My PDF Toolbox")
        self.root.geometry("400x400")
        self.root.configure(bg="#f0f0f0")

        # --- CONFIGURATION ---
        # Add your tools here
        self.tools = [
            {
                "name": "PDF Merger", 
                "file": "pdf_merge.py", # Make sure this matches your filename
                "desc": "Combine multiple PDF files into one.\nSupports reordering."
            },
            {
                "name": "Page Extractor", 
                "file": "pdf_page_selector.py", 
                "desc": "Extract specific pages (e.g., 1, 3-5)\nfrom a PDF file."
            }
        ]

        # --- TITLE ---
        title_frame = tk.Frame(root, bg="#333", pady=15)
        title_frame.pack(fill=tk.X)
        
        tk.Label(title_frame, text="PDF UTILITIES HUB", font=("Arial", 16, "bold"), 
                 bg="#333", fg="white").pack()

        # --- TOOLS LIST ---
        container = tk.Frame(root, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        for tool in self.tools:
            self.create_tool_button(container, tool)

        # --- FOOTER ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        footer = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#e1e1e1")
        footer.pack(side=tk.BOTTOM, fill=tk.X)

    def create_tool_button(self, parent, tool_info):
        frame = tk.Frame(parent, bg="white", bd=2, relief=tk.RAISED)
        frame.pack(fill=tk.X, pady=5)

        def on_click(e=None):
            self.launch_script(tool_info['file'])

        lbl_title = tk.Label(frame, text=tool_info['name'], font=("Arial", 11, "bold"), 
                             bg="white", fg="#007bff", cursor="hand2")
        lbl_title.pack(anchor="w", padx=10, pady=(5, 0))

        lbl_desc = tk.Label(frame, text=tool_info['desc'], font=("Arial", 9), 
                            bg="white", fg="#555", justify=tk.LEFT, cursor="hand2")
        lbl_desc.pack(anchor="w", padx=10, pady=(0, 5))

        btn = tk.Button(frame, text="RUN ➤", command=on_click, 
                        bg="#e1e1e1", font=("Arial", 8, "bold"), cursor="hand2")
        btn.pack(anchor="e", padx=10, pady=5)

        lbl_title.bind("<Button-1>", on_click)
        lbl_desc.bind("<Button-1>", on_click)

    def launch_script(self, filename):
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"Could not find file: {filename}\nMake sure it is in the same folder.")
            return

        self.status_var.set(f"Running {filename}...")
        
        try:
            # Start the process without freezing the GUI
            process = subprocess.Popen([sys.executable, filename])
            
            # Start monitoring the process
            self.monitor_process(process)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch script:\n{e}")
            self.status_var.set("Error occurred.")

    def monitor_process(self, process):
        """
        Checks every 1000ms (1 second) if the subprocess is still running.
        """
        if process.poll() is None:
            # Process is still running (poll returns None)
            # Check again in 1000ms
            self.root.after(1000, lambda: self.monitor_process(process))
        else:
            # Process has finished (poll returned a valid exit code)
            self.status_var.set("Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToolbox(root)
    root.mainloop()