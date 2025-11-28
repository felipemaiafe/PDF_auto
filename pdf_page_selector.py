import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from pypdf import PdfReader, PdfWriter

def parse_page_selection(selection_str, total_pages):
    """
    Parses a string of page selections into a LIST (preserving order).
    """
    # We use a list instead of a set to preserve order and allow duplicates
    selected_pages = [] 
    
    # Remove spaces and split by comma
    parts = selection_str.replace(" ", "").split(',')

    for part in parts:
        if not part:
            continue

        if '-' in part:
            try:
                start_str, end_str = part.split('-')
                start = int(start_str)
                end = int(end_str)
                
                # Check bounds
                if not (1 <= start <= total_pages and 1 <= end <= total_pages):
                    continue 

                # Handle forward range (1-5) and backward range (5-1)
                step = 1 if start <= end else -1
                
                # We need to add +1 to end if step is positive, or -1 if negative for python range
                range_end = end + 1 if step == 1 else end - 1
                
                for i in range(start, range_end, step):
                    selected_pages.append(i - 1) # Convert to 0-indexed
                    
            except ValueError:
                continue 
        else:
            try:
                page_num = int(part)
                if not (1 <= page_num <= total_pages):
                    continue 
                selected_pages.append(page_num - 1) # Convert to 0-indexed
            except ValueError:
                continue 
    
    # We return the list directly, WITHOUT sorting
    return selected_pages

def main():
    root = tk.Tk()
    root.withdraw()

    input_pdf_path = filedialog.askopenfilename(
        title="Select Input PDF",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not input_pdf_path:
        return

    try:
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
    except Exception as e:
        messagebox.showerror("Error", f"Could not read PDF file:\n{e}")
        return

    selected_page_indices = []
    
    while True:
        page_selection_str = simpledialog.askstring(
            "Select Pages",
            f"File has {total_pages} pages.\n"
            "Enter pages in the EXACT order you want them.\n"
            "(e.g., '10, 1, 5-8'):"
        )

        if page_selection_str is None:
            return

        selected_page_indices = parse_page_selection(page_selection_str, total_pages)
        
        if selected_page_indices:
            break 
        else:
            retry = messagebox.askretrycancel("Invalid Selection", "No valid pages detected.")
            if not retry:
                return

    output_pdf_path = filedialog.asksaveasfilename(
        title="Save New PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not output_pdf_path:
        return

    writer = PdfWriter()
    
    try:
        for page_idx in selected_page_indices:
            writer.add_page(reader.pages[page_idx])

        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)
        
        messagebox.showinfo("Success", f"Saved at: {output_pdf_path}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error saving:\n{e}")

if __name__ == "__main__":
    main()