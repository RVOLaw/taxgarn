import os
import fitz
import shelve
import threading
from pathlib import Path
from database_operations import DatabaseOperations
from PIL import Image, ImageSequence
from PyPDF2 import PdfMerger

# Import SQL credentials
with shelve.open('P:/Users/Justin/sql_creds/credentials') as db:
    server = db['server']
    database = 'DMSEngine'
    username = db['username']
    password = db['password']

connection_string = f"DRIVER=ODBC Driver 18 for SQL Server;SERVER={server};DATABASE=DMSEngine;ENCRYPT=no;UID={username};PWD={password}"
database_operations = DatabaseOperations(connection_string)

# Set the temp folder location
temp_folder = Path(r"P:\Users\Justin\taxgarn\temp")

def convert_tiff_to_pdf(tiff_path, output_pdf_path):
    try:
        im = Image.open(tiff_path)
        im.save(output_pdf_path, save_all=True, append_images=list(ImageSequence.all_frames(im)))
    except Exception as e:
        print(f"Error converting TIFF to PDF: {e}")

def merge_pdfs_in_folder(output_folder):
    try:
        merger = PdfMerger()
        pdf_files = sorted(output_folder.glob('*.pdf'), key=lambda x: x.stat().st_ctime)

        for pdf_file in pdf_files:
            merger.append(str(pdf_file))

        merged_output_path = output_folder / 'merged_output.pdf'
        with open(merged_output_path, 'wb') as merged_output_file:
            merger.write(merged_output_file)

        merger.close()

        # Delete other individual PDF files after merging
        for pdf_file in pdf_files:
            if pdf_file != merged_output_path:
                try:
                    pdf_file.unlink()
                    print(f"Deleted: {pdf_file}")
                except Exception as e:
                    print(f"Error deleting file '{pdf_file}': {e}")

        return merged_output_path

    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return None

def delete_temp_files(temp_folder, file_number):
    for temp_file in temp_folder.glob(f'{file_number}.pdf'):
        try:
            temp_file.unlink()
            print(f"Deleted temp file: {temp_file}")
        except Exception as e:
            print(f"Error deleting temp file '{temp_file}': {e}")

def vasion_pull(user_input, database_operations, open_file_explorer_callback, output_path):
    requested_file_numbers, output_path = user_input
    
    # Initialize output_file_paths list
    output_file_paths = []

    # Create a list of FILENOs where the documents couldn't be found
    no_documents_found = []

    for file_number in requested_file_numbers:
        documents = database_operations.get_documents_for_file_number(file_number)

        if not documents:
            print(f"No documents found for file number {file_number}")
            no_documents_found.append(file_number)
            continue

        combined_pdf = PdfMerger()

        for row in documents:
            document_path, document_name = row.DocumentPath, row.DocumentName
            file_path = Path(document_path) / document_name

            # Convert TIFF to PDF if the file is a TIFF
            if file_path.suffix.lower() in ['.tif', '.tiff']:
                pdf_output_path = temp_folder / f'{file_number}_{file_path.stem}.pdf'
                convert_tiff_to_pdf(file_path, pdf_output_path)
                combined_pdf.append(pdf_output_path)
            else:
                try:
                    combined_pdf.append(file_path)
                except Exception as e:
                    print(f"Error reading PDF file '{file_path}': {e}")

        # Set output_file_path inside the loop
        output_file_path = output_path / f'{file_number}.pdf'
        with open(output_file_path, 'wb') as output_file:
            combined_pdf.write(output_file)

        # Explicitly close the combined PDF object
        combined_pdf.close()

        # Append the output_file_path to the list
        output_file_paths.append(output_file_path)

        # Delete files in the temp folder after creating the PDF using threading
        threading.Thread(target=delete_temp_files, args=(temp_folder, file_number)).start()

    # Check if there are FILENOs with no documents
    if no_documents_found:
        no_documents_file_path = output_path / 'no_documents_found.txt'
        with open(no_documents_file_path, 'w') as no_documents_file:
            no_documents_file.write('\n'.join(map(str, no_documents_found)))
        print(f"FILENOs with no documents written to: {no_documents_file_path}")

    if output_file_paths:
        print(f"Generated PDFs: {', '.join(map(str, output_file_paths))}")

    # Merge PDFs in the order they were entered
    merged_output_path = merge_pdfs_in_order(output_file_paths, output_path, requested_file_numbers)

    # Open file explorer only once after all files are created
    if merged_output_path:
        open_file_explorer_callback(merged_output_path)

# Function for merging PDFs in order
def merge_pdfs_in_order(output_file_paths, output_folder, original_order):
    try:
        merged_output_path = output_folder / f'taxgarn2pdf_output.pdf'
        pdf_writer = fitz.open()

        # Sort the PDF paths based on the original order of file numbers
        sorted_pdf_paths = sorted(output_file_paths, key=lambda x: original_order.index(Path(x).stem))

        for pdf_path in sorted_pdf_paths:
            try:
                with fitz.open(pdf_path) as pdf_doc:
                    # Add only the first page to the writer
                    pdf_writer.insert_pdf(pdf_doc, from_page=0, to_page=0)
            except Exception as open_error:
                print(f"Error opening PDF file '{pdf_path}': {open_error}")

        if pdf_writer.page_count == 0:
            print("No valid pages to merge.")
            return None

        # Save the merged output PDF
        pdf_writer.save(merged_output_path)
        pdf_writer.close()

        # Delete other individual PDF files after merging
        for pdf_path in sorted_pdf_paths:
            if pdf_path != merged_output_path:
                try:
                    Path(pdf_path).unlink()
                    print(f"Deleted: {pdf_path}")
                except Exception as delete_error:
                    print(f"Error deleting file '{pdf_path}': {delete_error}")

        return merged_output_path

    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return None
    