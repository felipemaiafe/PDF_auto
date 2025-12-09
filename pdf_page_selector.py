import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter
import os

class PDFSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() # Hide the main background window
        self.run_process()
        self.root.destroy() # Close everything when done

    def run_process(self):
        # 1. Select Input File
        input_pdf_path = filedialog.askopenfilename(
            title="Select Input PDF", 
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not input_pdf_path: return

        try:
            reader = PdfReader(input_pdf_path)
            total_pages = len(reader.pages)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read PDF:\n{e}")
            return

        # 2. CUSTOM INPUT WINDOW
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Pages")
        dialog.geometry("400x180")
        
        # Center the text and input
        tk.Label(dialog, text=f"File: {os.path.basename(input_pdf_path)}\nTotal Pages: {total_pages}", pady=10).pack()
        tk.Label(dialog, text="Enter page numbers (e.g. 1, 3-5):", font=("Arial", 10, "bold")).pack()
        
        # The input box
        entry = tk.Entry(dialog, font=("Arial", 12))
        entry.pack(fill=tk.X, padx=20, pady=5)
        entry.focus_set() # Allow typing immediately

        # Variable to store the user's input
        user_input = {"text": None}

        def on_submit(event=None):
            user_input["text"] = entry.get()
            dialog.destroy() # Close the popup

        # OK Button
        tk.Button(dialog, text="OK", command=on_submit, bg="#2196F3", fg="white", width=10).pack(pady=10)
        
        # Allow pressing 'Enter' key
        dialog.bind('<Return>', on_submit)

        # PAUSE CODE until this window is closed
        self.root.wait_window(dialog)

        # 3. Check result
        page_str = user_input["text"]
        if not page_str: return # User closed window or cancelled

        indices = self.parse_page_selection(page_str, total_pages)
        if not indices:
            messagebox.showwarning("Error", "No valid pages selected.")
            return

        # 4. Select Output File
        output_path = filedialog.asksaveasfilename(
            title="Save Extracted PDF As", 
            defaultextension=".pdf", 
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not output_path: return

        # 5. Save
        writer = PdfWriter()
        try:
            for idx in indices:
                writer.add_page(reader.pages[idx])
            with open(output_path, "wb") as f:
                writer.write(f)
            messagebox.showinfo("Success", f"Extracted {len(indices)} pages.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def parse_page_selection(self, selection_str, total_pages):
        selected_pages = [] 
        parts = selection_str.replace(" ", "").split(',')
        for part in parts:
            if not part: continue
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if not (1 <= start <= total_pages and 1 <= end <= total_pages): continue 
                    step = 1 if start <= end else -1
                    range_end = end + 1 if step == 1 else end - 1
                    for i in range(start, range_end, step):
                        selected_pages.append(i - 1)
                except ValueError: continue 
            else:
                try:
                    page_num = int(part)
                    if 1 <= page_num <= total_pages:
                        selected_pages.append(page_num - 1)
                except ValueError: continue 
        return selected_pages

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSelectorApp(root)