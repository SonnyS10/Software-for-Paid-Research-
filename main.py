from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os
import subprocess
import sys
from LSL import LSL  # Import the LSL class from LSL.py

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subject Information")
        self.setGeometry(100, 100, 400, 300)

        # Create the central widget and set it as the central widget of the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout(central_widget)

        # LSL Status
        self.lsl_status_label = QLabel("LSL Status:", self)
        layout.addWidget(self.lsl_status_label)
        self.lsl_status_icon = QLabel(self)
        self.update_lsl_status_icon(False)
        layout.addWidget(self.lsl_status_icon)

        # Subject ID input
        self.subject_id_label = QLabel("Subject ID:", self)
        layout.addWidget(self.subject_id_label)
        self.subject_id_input = QLineEdit(self)
        layout.addWidget(self.subject_id_input)

        # Test number input
        self.test_number_label = QLabel("Test Number (1 or 2):", self)
        layout.addWidget(self.test_number_label)
        self.test_number_input = QLineEdit(self)
        layout.addWidget(self.test_number_input)

        # Start button
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_experiment)
        self.start_button.setEnabled(False)  # Disable until LSL is streaming
        layout.addWidget(self.start_button)

        # Initialize LSL
        self.init_lsl()

    def init_lsl(self):
        """
        Initialize LSL and update the status icon.
        """
        try:
            LSL.init_lsl_stream()  # Call the LSL initialization method
            self.update_lsl_status_icon(True)
            self.start_button.setEnabled(True)
            LSL.start_collection()  # Start collecting data
        except Exception as e:
            self.show_error_message(f"Failed to initialize LSL: {str(e)}")
            self.update_lsl_status_icon(False)

    def update_lsl_status_icon(self, is_streaming):
        """
        Update the LSL status icon to show a red or green light.
        """
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.green if is_streaming else Qt.red)
        self.lsl_status_icon.setPixmap(pixmap)

    def show_error_message(self, message):
        """
        Show an error message in a popup dialog.
        """
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.exec_()

    def start_experiment(self):
        """
        Start the experiment after ensuring LSL is streaming.
        """
        # Get the subject ID and test number from the input fields
        subject_id = self.subject_id_input.text()
        test_number = self.test_number_input.text()

        # Check if the subject ID and test number are valid
        if subject_id and test_number in ['1', '2']:
            # Create base directory structure
            base_dir = os.path.join('subject_data', f'subject_{subject_id}', f'test_{test_number}')
            os.makedirs(base_dir, exist_ok=True)

            # List of tests
            passive_tests = [
                'Unisensory Neutral Visual',
                'Unisensory Alcohol Visual',
                'Multisensory Neutral Visual & Olfactory',
                'Multisensory Alcohol Visual & Olfactory',
                'Multisensory Neutral Visual, Tactile & Olfactory',
                'Multisensory Alcohol Visual, Tactile & Olfactory'
            ]

            stroop_tests = [
                'Multisensory Alcohol (Visual & Tactile)',
                'Multisensory Neutral (Visual & Tactile)',
                'Multisensory Alcohol (Visual & Olfactory)',
                'Multisensory Neutral (Visual & Olfactory)'
            ]

            # Select the appropriate tests based on the test number
            if test_number == '1':
                selected_tests = passive_tests
            else:
                selected_tests = stroop_tests

            # Create subdirectories for each selected test and clear the data.csv file if it exists
            for test in selected_tests:
                test_dir = os.path.join(base_dir, test)
                os.makedirs(test_dir, exist_ok=True)
                file_path = os.path.join(test_dir, 'data.csv')
                if os.path.exists(file_path):
                    with open(file_path, 'w') as file:
                        file.truncate(0)

            # Pass the subject ID, test number, and base directory as environment variables
            env = os.environ.copy()
            env['SUBJECT_ID'] = subject_id
            env['TEST_NUMBER'] = test_number
            env['BASE_DIR'] = base_dir

            # Run the GUI_pyQt.py file
            subprocess.Popen([sys.executable, 'GUI_pyQt.py'], env=env)
        else:
            print("Please enter a valid Subject ID and Test Number (1 or 2).")

if __name__ == "__main__":
    # Create the application and main window, then run the application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
