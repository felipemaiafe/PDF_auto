import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfWriter
import os

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger Tool")
        self.root.geometry("600x500")

        self.file_rows = [] 
        self.drag_data = {"item": None, "y": 0, "index": -1}

        # --- 1. TOP BUTTONS ---
        header_frame = tk.Frame(root, pady=10, bg="#f0f0f0")
        header_frame.pack(fill=tk.X)

        tk.Button(header_frame, text="+ Add PDFs", command=self.add_files, 
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT, padx=10)
        
        tk.Button(header_frame, text="Clear List", command=self.clear_all, 
                  bg="#f44336", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=10)

        # --- 2. SCROLLABLE AREA SETUP ---
        # Container to hold canvas and scrollbar
        container = tk.Frame(root, bd=2, relief=tk.SUNKEN)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas
        self.canvas = tk.Canvas(container, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        # The Frame INSIDE the Canvas
        self.inner_frame = tk.Frame(self.canvas, bg="white")
        
        # Create a window inside the canvas to hold the frame
        # We start with a generic width, but bind it to resize later
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # --- BINDINGS FOR SCROLLING ---
        # 1. When the Inner Frame changes size (rows added), update the scroll region
        self.inner_frame.bind("<Configure>", self.on_frame_configure)
        # 2. When the Canvas changes size (window resize), force Inner Frame width to match
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        # 3. Mousewheel
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # --- 3. FOOTER ---
        footer_frame = tk.Frame(root, pady=10, bg="#f0f0f0")
        footer_frame.pack(fill=tk.X)
        
        tk.Button(footer_frame, text="MERGE FILES", command=self.merge_files, 
                  bg="#2196F3", fg="white", font=("Arial", 12, "bold"), height=2).pack(fill=tk.X, padx=20)

    # --- SCROLL HELPERS ---
    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """When canvas resizes, resize the inner frame to match width"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # --- FILE LOGIC ---
    def add_files(self):
        filepaths = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF Files", "*.pdf")]
        )
        
        if not filepaths:
            return

        print(f"Adding {len(filepaths)} files...") # Debug print

        for path in filepaths:
            self.create_row(path)

    def create_row(self, path):
        filename = os.path.basename(path)

        # Create row frame inside the INNER FRAME
        row_frame = tk.Frame(self.inner_frame, bd=1, relief=tk.RAISED, bg="#f9f9f9")
        row_frame.pack(fill=tk.X, pady=2, padx=5)

        # Drag Handle
        handle = tk.Label(row_frame, text="☰", cursor="hand2", bg="#e0e0e0", width=4, font=("Arial", 10))
        handle.pack(side=tk.LEFT, fill=tk.Y)

        # Label
        lbl = tk.Label(row_frame, text=filename, anchor="w", bg="#f9f9f9", padx=10)
        lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Buttons
        ctrl_frame = tk.Frame(row_frame, bg="#f9f9f9")
        ctrl_frame.pack(side=tk.RIGHT)

        tk.Button(ctrl_frame, text="▲", width=2, command=lambda: self.move_row_up(row_frame)).pack(side=tk.LEFT)
        tk.Button(ctrl_frame, text="▼", width=2, command=lambda: self.move_row_down(row_frame)).pack(side=tk.LEFT)
        tk.Button(ctrl_frame, text="✕", width=2, bg="#ffcccc", command=lambda: self.remove_row(row_frame)).pack(side=tk.LEFT, padx=5)

        # Save reference
        self.file_rows.append({'path': path, 'widget': row_frame})

        # Drag Bindings
        for w in [handle, lbl, row_frame]:
            w.bind("<Button-1>", lambda e, rf=row_frame: self.on_start_drag(e, rf))
            w.bind("<B1-Motion>", self.on_drag_motion)
            w.bind("<ButtonRelease-1>", self.on_stop_drag)

    # --- REORDERING LOGIC ---
    def get_index_by_widget(self, widget):
        for i, row in enumerate(self.file_rows):
            if row['widget'] == widget:
                return i
        return None

    def swap_rows(self, i, j):
        self.file_rows[i], self.file_rows[j] = self.file_rows[j], self.file_rows[i]
        # Repack
        for row in self.file_rows:
            row['widget'].pack_forget()
            row['widget'].pack(fill=tk.X, pady=2, padx=5)

    def move_row_up(self, widget):
        idx = self.get_index_by_widget(widget)
        if idx is not None and idx > 0:
            self.swap_rows(idx, idx - 1)

    def move_row_down(self, widget):
        idx = self.get_index_by_widget(widget)
        if idx is not None and idx < len(self.file_rows) - 1:
            self.swap_rows(idx, idx + 1)

    def remove_row(self, widget):
        idx = self.get_index_by_widget(widget)
        if idx is not None:
            self.file_rows.pop(idx)
            widget.destroy()
            # Force update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def clear_all(self):
        for row in self.file_rows:
            row['widget'].destroy()
        self.file_rows = []
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # --- DRAG LOGIC ---
    def on_start_drag(self, event, row_widget):
        self.drag_data["item"] = row_widget
        self.drag_data["index"] = self.get_index_by_widget(row_widget)
        row_widget.configure(bg="#cce5ff") # Highlight Blue

    def on_stop_drag(self, event):
        if self.drag_data["item"]:
            self.drag_data["item"].configure(bg="#f9f9f9") # Reset Color
        self.drag_data = {"item": None, "index": -1}

    def on_drag_motion(self, event):
        if not self.drag_data["item"]: return
        
        # Check what's under the mouse
        x, y = self.root.winfo_pointerx(), self.root.winfo_pointery()
        target = self.root.winfo_containing(x, y)

        target_row_widget = None
        current = target
        # Traverse up to find the row frame
        while current and current != self.root:
            if any(r['widget'] == current for r in self.file_rows):
                target_row_widget = current
                break
            current = current.master

        if target_row_widget and target_row_widget != self.drag_data["item"]:
            idx_from = self.get_index_by_widget(self.drag_data["item"])
            idx_to = self.get_index_by_widget(target_row_widget)
            
            if idx_from is not None and idx_to is not None:
                self.swap_rows(idx_from, idx_to)

    # --- MERGE LOGIC ---
    def merge_files(self):
        if not self.file_rows:
            messagebox.showwarning("Warning", "No files to merge.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not out_path:
            return

        merger = PdfWriter()
        try:
            for row in self.file_rows:
                merger.append(row['path'])
            merger.write(out_path)
            merger.close()
            messagebox.showinfo("Success", f"Saved to:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()