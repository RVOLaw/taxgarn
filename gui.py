import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
from main import vasion_pull, database_operations

class GUI:
    def __init__(self, master, processing_callback):
        self.master = master
        self.master.title("Taxgarn2PDF")

        self.requested_file_numbers = tk.StringVar()
        self.requested_document_types = tk.StringVar()
        self.output_path = tk.StringVar()
        self.merge_var = tk.BooleanVar()

        self.processing_callback = processing_callback  # Store the callback function

        self.create_widgets()

        self.message_label = tk.Label(self.master, text="", fg="grey")
        self.message_label.grid(row=4, column=0, columnspan=2, pady=10)

    def create_widgets(self,):
        # File Numbers Entry
        file_numbers_label = tk.Label(self.master, text="Import taxgarn .DAT file:")
        file_numbers_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        file_numbers_entry = tk.Entry(self.master, textvariable=self.requested_file_numbers)
        file_numbers_entry.grid(row=1, column=2, columnspan=2, padx=10, pady=5)
        import_button = tk.Button(self.master, text="Import", command=self.import_file)
        import_button.grid(row=1, column=1, pady=5)

        # Output Path Entry and Browse Button
        output_path_label = tk.Label(self.master, text="Output Path:")
        output_path_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        output_path_entry = tk.Entry(self.master, textvariable=self.output_path)
        output_path_entry.grid(row=3, column=2, columnspan=2, padx=10, pady=5)
        browse_button = tk.Button(self.master, text="Browse", command=self.browse_output_path)
        browse_button.grid(row=3, column=1, padx=5, pady=5)

        ## Submit Button
        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit_callback)
        self.submit_button.grid(row=4, column=2, pady=10, padx=23, sticky=tk.W)

        # Clear Button
        clear_button = tk.Button(self.master, text="Clear", command=self.clear_entries)
        clear_button.grid(row=4, column=2, pady=10, sticky=tk.E)

    def open_file_explorer(self, folder_path):
        os.startfile(folder_path)

    def submit_callback(self):
        user_input = self.get_user_input()
        output_path = self.output_path.get()

        # Use threading to run the vasion_pull method in a separate thread
        threading.Thread(target=vasion_pull, args=(user_input, database_operations, self.open_file_explorer, output_path)).start()

        self.message_label.config(text="Processing. Please Wait...")
        self.submit_button.config(state=tk.DISABLED)  # Disable the button during processing

    def vasion_pull_threaded(self):
        try:
            user_input = self.get_user_input()
            output_path = self.output_path.get()
            self.vasion_pull(user_input, output_path)
            self.message_label.config(text="File created successfully!")

            # Open the file explorer to the output folder
            self.open_file_explorer(output_path)

        except Exception as e:
            self.message_label.config(text=f"Error: {e}")

    def clear_entries(self):
        # Clear all entry fields
        self.requested_file_numbers.set("")
        self.requested_document_types.set("")
        self.output_path.set("")
        self.message_label.config(text="Entries cleared.")

    def browse_output_path(self):
        folder_selected = filedialog.askdirectory()
        self.output_path.set(folder_selected)

    def extract_filenumbers(self, input_file, output_file, fileno_index=492):
        debtnum_filenos = []

        try:
            with open(input_file, 'r') as infile:
                txt = infile.read().split('\n')

                # Process all lines except the first one
                for i, row in enumerate(txt):
                    if i > 0:
                        row = row.strip()  # Remove leading and trailing whitespaces
                        if row:  # Check if the row is not empty
                            debtnum_fileno = row[fileno_index:].split(' ', 1)[0]
                            debtnum_filenos.append(debtnum_fileno)
        except FileNotFoundError as e:
            print(f"Error: Input file '{input_file}' not found. {e}")
            return debtnum_filenos

        try:
            with open(output_file, 'w') as outfile:
                for fileno in debtnum_filenos:
                    outfile.write(f"{fileno}\n")
        except OSError as e:
            print(f"Error writing to output file '{output_file}': {e}")

        return debtnum_filenos

    def import_file(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
            print(f"Selected file: {file_path}")  # Debugging statement
            if file_path:
                if file_path.lower().endswith('.dat'):
                    print("Processing DAT file...")  # Debugging statement
                    output_file_path = Path("output_file.txt")  # Change the output file path as needed

                    # Use an instance of the GUI class to call the extract_filenumbers method
                    file_numbers = self.extract_filenumbers(file_path, output_file_path)
                    self.requested_file_numbers.set(','.join(file_numbers))
                    print(f"File numbers: {file_numbers}")  # Debugging statement
                else:
                    print("Processing text file...")  # Debugging statement
                    with open(file_path, 'r') as file:
                        file_content = file.read().splitlines()
                        self.requested_file_numbers.set(','.join(file_content))
                        print(f"File content: {file_content}")  # Debugging statement
        except Exception as e:
            print(f"Error in import_file: {e}")

    def get_user_input(self):
        file_numbers_str = self.requested_file_numbers.get()
    
        # Check if the input is a file path
        if file_numbers_str.endswith('.txt'):
            with open(file_numbers_str, 'r') as file:
                file_numbers = file.read().splitlines()
        else:
            file_numbers = file_numbers_str.split(',')

        output_path_str = self.output_path.get()

        output_path = Path(output_path_str)

        return file_numbers, output_path

if __name__ == "__main__":
    def submit_callback(self):
        # Use threading to run the vasion_pull method in a separate thread
        threading.Thread(target=self.vasion_pull_threaded).start()
        self.message_label.config(text="Processing. Please Wait...")

    def vasion_pull_threaded(self, user_input, output_path):
        try:
            self.vasion_pull(user_input, output_path)
            self.message_label.config(text="File created successfully!")
        except Exception as e:
            self.message_label.config(text=f"Error: {e}")

    root = tk.Tk()
    my_gui = GUI(root, submit_callback)
    root.mainloop()