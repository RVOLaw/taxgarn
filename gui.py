import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog
from main import vasion_pull, database_operations

class GUI(QMainWindow):
    def __init__(self, processing_callback):
        super().__init__()
        self.setWindowTitle("Taxgarn2PDF")

        self.processing_callback = processing_callback

        self.initUI()

    def initUI(self):
        # File Numbers Entry
        self.file_numbers_label = QLabel("Import taxgarn .DAT file:", self)
        self.file_numbers_label.setGeometry(10, 10, 150, 20)
        self.file_numbers_entry = QLineEdit(self)
        self.file_numbers_entry.setGeometry(170, 10, 200, 20)
        self.import_button = QPushButton("Import", self)
        self.import_button.setGeometry(380, 10, 80, 20)
        self.import_button.clicked.connect(self.import_file)

        # Output Path Entry and Browse Button
        self.output_path_label = QLabel("Output Path:", self)
        self.output_path_label.setGeometry(10, 40, 150, 20)
        self.output_path_entry = QLineEdit(self)
        self.output_path_entry.setGeometry(170, 40, 200, 20)
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.setGeometry(380, 40, 80, 20)
        self.browse_button.clicked.connect(self.browse_output_path)

        # Submit Button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setGeometry(380, 80, 80, 20)
        self.submit_button.clicked.connect(self.submit_callback)

        # Message Label
        self.message_label = QLabel("", self)
        self.message_label.setGeometry(10, 80, 300, 20)

    def submit_callback(self):
        user_input = self.get_user_input()
        output_path = self.output_path_entry.text()

        try:
            self.submit_button.setEnabled(False)
            self.message_label.setText("Processing. Please Wait...")

            # Invoke the processing callback function
            self.processing_callback(user_input, output_path)

        except Exception as e:
            self.message_label.setText(f"An error occurred during conversion: {e}")

    def enable_submit_button(self):
        self.submit_button.setEnabled(True)
        self.message_label.setText("File created successfully!")

    def import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import taxgarn .DAT file")
        if file_path:
            self.file_numbers_entry.setText(file_path)

    def browse_output_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select output path")
        if folder_path:
            self.output_path_entry.setText(folder_path)

    def get_user_input(self):
        file_numbers_str = self.file_numbers_entry.text()
        file_numbers = file_numbers_str.split(',')
        output_path_str = self.output_path_entry.text()
        return file_numbers, output_path_str

if __name__ == "__main__":
    def processing_callback(user_input, output_path):
        try:
            vasion_pull(user_input, database_operations, lambda path: print(f"File created: {path}"), output_path)
            window.enable_submit_button()
        except Exception as e:
            window.message_label.setText(f"Error: {e}")

    app = QApplication(sys.argv)
    window = GUI(processing_callback)
    window.setGeometry(100, 100, 470, 110)
    window.show()
    sys.exit(app.exec_())
