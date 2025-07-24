from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing Files")
        self.setModal(True)
        
        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("Processing files, please wait...")
        self.layout.addWidget(self.label)
        
        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)
        
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_button)
        
        self.setLayout(self.layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def set_label_text(self, text):
        self.label.setText(text)