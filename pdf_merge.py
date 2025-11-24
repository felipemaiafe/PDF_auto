import tkinter as tk
from tkinter import filedialog
from pypdf import PdfWriter
import sys

def main():
    # Initialize tkinter and hide the main root window
    root = tk.Tk()
    root.withdraw()

    print("Step 1: Please select the PDF files you want to merge...")
    
    # 1. Ask the user to select the PDF files
    file_paths = filedialog.askopenfilenames(
        title="Select PDF files to merge",
        filetypes=[("PDF Files", "*.pdf")]
    )

    # Check if the user cancelled the selection
    if not file_paths:
        print("No files selected. Exiting.")
        sys.exit()

    print(f"Selected {len(file_paths)} files. Merging...")

    # 2. Merge the files
    merger = PdfWriter()

    try:
        for path in file_paths:
            merger.append(path)
    except Exception as e:
        print(f"An error occurred while reading files: {e}")
        sys.exit()

    print("Step 2: Files merged in memory.")
    print("Step 3: Please choose where to save the new file...")

    # 3. Ask the user to name the newly merged PDF file
    output_path = filedialog.asksaveasfilename(
        title="Save Merged PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )

    # Check if the user cancelled the save dialog
    if not output_path:
        print("Save cancelled. Exiting.")
        merger.close()
        sys.exit()

    # Write the final file
    try:
        merger.write(output_path)
        merger.close()
        print(f"Success! Merged PDF saved at: {output_path}")
    except Exception as e:
        print(f"An error occurred while saving: {e}")

if __name__ == "__main__":
    main()