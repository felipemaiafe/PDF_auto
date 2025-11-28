import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from pypdf import PdfReader, PdfWriter

def parse_page_selection(selection_str, total_pages):
    """
    Parses a string of page selections (e.g., "1,3-5,8") into a list of 0-indexed page numbers.
    """
    selected_pages = set()
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
                if not (1 <= start <= total_pages and 1 <= end <= total_pages and start <= end):
                    continue # Skip invalid range
                
                for i in range(start - 1, end):
                    selected_pages.add(i)
            except ValueError:
                continue # Skip invalid format
        else:
            try:
                page_num = int(part)
                if not (1 <= page_num <= total_pages):
                    continue # Skip out of bounds
                selected_pages.add(page_num - 1) # Convert to 0-indexed
            except ValueError:
                continue # Skip non-integers
    
    return sorted(list(selected_pages))

def main():
    # Initialize Tkinter and hide the main window
    root = tk.Tk()
    root.withdraw()

    # 1. Select PDF from computer
    input_pdf_path = filedialog.askopenfilename(
        title="Select Input PDF",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not input_pdf_path:
        print("No file selected. Exiting.")
        return

    try:
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
    except Exception as e:
        messagebox.showerror("Error", f"Could not read PDF file:\n{e}")
        return

    # 2. Ask which pages should be selected
    selected_page_indices = []
    
    while True:
        # Show input dialog
        page_selection_str = simpledialog.askstring(
            "Select Pages",
            f"File has {total_pages} pages.\n"
            "Enter page numbers (e.g., '1,3-5,8'):"
        )

        # If user pressed Cancel
        if page_selection_str is None:
            print("Operation cancelled.")
            return

        selected_page_indices = parse_page_selection(page_selection_str, total_pages)
        
        if selected_page_indices:
            break # Valid pages found, proceed
        else:
            # Show warning and loop back
            retry = messagebox.askretrycancel(
                "Invalid Selection", 
                "No valid pages were detected in your input.\nPlease try again."
            )
            if not retry:
                return

    # 3. Create new PDF file with those pages selected
    output_pdf_path = filedialog.asksaveasfilename(
        title="Save New PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not output_pdf_path:
        print("Save cancelled.")
        return

    # 4. Write the file
    writer = PdfWriter()
    
    try:
        for page_idx in selected_page_indices:
            writer.add_page(reader.pages[page_idx])

        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)
        
        # Success message
        messagebox.showinfo(
            "Success", 
            f"New PDF created successfully!\nSaved at: {output_pdf_path}\nPages extracted: {len(writer.pages)}"
        )
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving:\n{e}")

if __name__ == "__main__":
    main()