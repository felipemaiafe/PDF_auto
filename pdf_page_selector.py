import os
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError

def get_valid_file_path(prompt_message, must_exist=True):
    """
    Prompts the user for a file path and validates it.
    Args:
        prompt_message (str): The message to display to the user.
        must_exist (bool): If True, the file must exist. If False, it must not exist (for output).
    Returns:
        str: The validated file path.
    """
    while True:
        file_path = input(prompt_message).strip()
        if not file_path:
            print("File path cannot be empty. Please try again.")
            continue

        if must_exist:
            if not os.path.exists(file_path):
                print(f"Error: File not found at '{file_path}'. Please check the path and try again.")
            elif not os.path.isfile(file_path):
                print(f"Error: '{file_path}' is not a file. Please provide a valid file path.")
            else:
                return file_path
        else: # For output file, ensure directory exists
            output_dir = os.path.dirname(file_path)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                    return file_path
                except OSError as e:
                    print(f"Error creating directory '{output_dir}': {e}. Please provide a valid output path.")
            else:
                return file_path

def parse_page_selection(selection_str, total_pages):
    """
    Parses a string of page selections (e.g., "1,3-5,8") into a list of 0-indexed page numbers.
    Args:
        selection_str (str): The user's input string for page selection.
        total_pages (int): The total number of pages in the PDF.
    Returns:
        list: A sorted list of unique 0-indexed page numbers.
    """
    selected_pages = set()
    parts = selection_str.replace(" ", "").split(',')

    for part in parts:
        if not part:
            continue

        if '-' in part:
            try:
                start_str, end_str = part.split('-')
                start = int(start_str)
                end = int(end_str)
                if not (1 <= start <= total_pages and 1 <= end <= total_pages and start <= end):
                    print(f"Warning: Invalid page range '{part}'. Pages must be between 1 and {total_pages}. Skipping.")
                    continue
                for i in range(start - 1, end):
                    selected_pages.add(i)
            except ValueError:
                print(f"Warning: Invalid page range format '{part}'. Skipping.")
        else:
            try:
                page_num = int(part)
                if not (1 <= page_num <= total_pages):
                    print(f"Warning: Page number '{page_num}' is out of bounds (1-{total_pages}). Skipping.")
                    continue
                selected_pages.add(page_num - 1) # Convert to 0-indexed
            except ValueError:
                print(f"Warning: Invalid page number format '{part}'. Skipping.")
    
    if not selected_pages:
        print("No valid pages were selected. The output PDF will be empty.")

    return sorted(list(selected_pages))

def main():
    print("--- PDF Page Selector ---")

    # 1. Select PDF from computer
    input_pdf_path = get_valid_file_path("Enter the path to the input PDF file: ")

    try:
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
        print(f"Successfully loaded '{os.path.basename(input_pdf_path)}' with {total_pages} pages.")
    except PdfReadError as e:
        print(f"Error: Could not read PDF file. It might be corrupted or encrypted: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred while opening the PDF: {e}")
        return

    # 2. Ask which pages should be selected
    while True:
        page_selection_str = input(
            f"Enter the page numbers to select (e.g., '1,3,5' or '2-4' or '1,3-5,8'). Total pages: {total_pages}: "
        )
        selected_page_indices = parse_page_selection(page_selection_str, total_pages)
        if selected_page_indices:
            print(f"Selected {len(selected_page_indices)} pages: {[p + 1 for p in selected_page_indices]}")
            break
        else:
            print("No valid pages were entered. Please try again.")

    # 3. Create new PDF file with those pages selected
    output_pdf_path = get_valid_file_path("Enter the path for the new output PDF file (e.g., output.pdf): ", must_exist=False)

    writer = PdfWriter()
    for page_idx in selected_page_indices:
        try:
            page = reader.pages[page_idx]
            writer.add_page(page)
        except IndexError:
            print(f"Warning: Page {page_idx + 1} not found in the input PDF. Skipping.")
        except Exception as e:
            print(f"Error adding page {page_idx + 1}: {e}. Skipping this page.")

    if not writer.pages:
        print("No pages were successfully added to the output PDF. The file will not be created.")
        return

    try:
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)
        print(f"\nSuccessfully created new PDF: '{output_pdf_path}' with {len(writer.pages)} pages.")
    except Exception as e:
        print(f"Error saving the new PDF file: {e}")

if __name__ == "__main__":
    main()
