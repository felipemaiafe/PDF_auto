import tkinter as tk
from tkinter import messagebox
import sys

# --- IMPORT YOUR TOOLS ---
try:
    import pdf_merge
    import pdf_page_selector
except ImportError as e:
    messagebox.showerror("Critical Error", f"Missing script files.\n{e}")
    sys.exit()

class PDFToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("My PDF Toolbox")
        self.root.geometry("400x400")

        # Dictionary to track open windows { "Tool Name": window_object }
        self.open_windows = {}

        # --- CONFIGURATION ---
        self.tools = [
            {
                "name": "PDF Merger", 
                "class_ref": pdf_merge.PDFMergerApp, 
                "desc": "Combine multiple PDF files into one.\nSupports reordering."
            },
            {
                "name": "Page Extractor", 
                "class_ref": pdf_page_selector.PDFSelectorApp, 
                "desc": "Extract specific pages (e.g., 1, 3-5)\nfrom a PDF file."
            }
        ]

        # --- UI LAYOUT ---
        tk.Label(root, text="PDF UTILITIES HUB", font=("Arial", 16, "bold"), bg="#333", fg="white", pady=15).pack(fill=tk.X)
        
        container = tk.Frame(root, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        for tool in self.tools:
            self.create_tool_button(container, tool)

        self.status_label = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def create_tool_button(self, parent, tool_info):
        frame = tk.Frame(parent, bg="white", bd=2, relief=tk.RAISED)
        frame.pack(fill=tk.X, pady=5)

        def on_click(e=None):
            self.launch_tool(tool_info)

        lbl_title = tk.Label(frame, text=tool_info['name'], font=("Arial", 11, "bold"), fg="#007bff", bg="white")
        lbl_title.pack(anchor="w", padx=10, pady=(5, 0))
        
        lbl_desc = tk.Label(frame, text=tool_info['desc'], font=("Arial", 9), fg="#555", bg="white", justify=tk.LEFT)
        lbl_desc.pack(anchor="w", padx=10, pady=(0, 5))

        btn = tk.Button(frame, text="RUN ➤", command=on_click, bg="#e1e1e1")
        btn.pack(anchor="e", padx=10, pady=5)
        
        for w in [lbl_title, lbl_desc]:
            w.bind("<Button-1>", on_click)

    def launch_tool(self, tool_info):
        name = tool_info['name']

        # 1. Check if window is already open
        if name in self.open_windows:
            existing_window = self.open_windows[name]
            # Check if the user didn't close it manually
            if existing_window.winfo_exists():
                # Bring it to front
                existing_window.lift()
                existing_window.focus_force()
                self.status_label.config(text=f"Switched to {name}")
                return
            else:
                # It was closed, remove from list
                del self.open_windows[name]

        self.status_label.config(text=f"Running {name}...")
        
        # 2. Create new Window
        new_window = tk.Toplevel(self.root)
        
        # 3. Add to tracking list
        self.open_windows[name] = new_window
        
        try:
            app_class = tool_info['class_ref']
            
            # Run the tool
            app_class(new_window)
            
            # Wait for it to close (cleanup)
            try:
                new_window.wait_window()
            except tk.TclError:
                pass 

            self.status_label.config(text="Ready")
            
            # Remove from tracking once closed cleanly
            if name in self.open_windows:
                del self.open_windows[name]

        except Exception as e:
            if "bad window path name" not in str(e):
                messagebox.showerror("Error", f"Failed to launch:\n{e}")
            self.status_label.config(text="Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToolbox(root)
    root.mainloop()