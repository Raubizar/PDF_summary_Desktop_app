import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QFileDialog, QMessageBox, QLabel, QTextEdit, 
                             QProgressBar, QFrame)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon
from core.file_processor import process_files
from config.settings import Settings
import requests


class FileProcessingThread(QThread):
    progress_update = pyqtSignal(int, str)  # progress percentage, status message
    file_processed = pyqtSignal(str)  # filename processed
    finished_processing = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        
    def run(self):
        try:
            from pathlib import Path
            import pandas as pd
            from core.summarizer import read_file, rag_summarize
            
            input_folder = Path(self.folder_path)
            output_folder = input_folder / "output_rag"
            output_folder.mkdir(exist_ok=True)
            
            settings = Settings()
            query = settings.get_default_query()
            
            # Find all supported files
            files = (list(input_folder.glob("*.txt")) + 
                    list(input_folder.glob("*.pdf")) + 
                    list(input_folder.glob("*.PDF")))
            
            if not files:
                self.finished_processing.emit(False, "No supported files (PDF or TXT) found in the selected folder.")
                return
            
            self.progress_update.emit(0, f"Found {len(files)} files to process...")
            
            results = []
            for i, file in enumerate(files):
                try:
                    self.progress_update.emit(
                        int((i / len(files)) * 90), 
                        f"Processing: {file.name}"
                    )
                    self.file_processed.emit(file.name)
                    
                    # Read and process file
                    text = read_file(file)
                    answer = rag_summarize(text, query)
                    
                    # Save individual summary
                    output_file = output_folder / f"{file.stem}_rag_answer.txt"
                    output_file.write_text(answer, encoding="utf-8")
                    
                    results.append((file.name, answer))
                    
                except Exception as e:
                    error_msg = f"Error processing {file.name}: {str(e)}"
                    self.progress_update.emit(
                        int((i / len(files)) * 90), 
                        error_msg
                    )
                    
            # Create Excel summary
            if results:
                self.progress_update.emit(95, "Creating summary spreadsheet...")
                df = pd.DataFrame(results, columns=["Filename", "Summary"])
                excel_path = output_folder / "summaries.xlsx"
                df.to_excel(excel_path, index=False)
                
                self.progress_update.emit(100, "Processing complete!")
                self.finished_processing.emit(
                    True, 
                    f"Successfully processed {len(results)} files.\nResults saved to: {output_folder}"
                )
            else:
                self.finished_processing.emit(False, "No files could be processed successfully.")
                
        except Exception as e:
            self.finished_processing.emit(False, f"Unexpected error: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.processing_thread = None
        self.setWindowTitle("PDF Summarizer - AI Document Analysis")
        self.setGeometry(100, 100, 700, 500)
        self.setMinimumSize(600, 400)
        
        self.init_ui()
        self.check_dependencies_on_startup()

    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("PDF Summarizer")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Select a folder containing PDF or text files to generate AI-powered summaries")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 20px;")
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)
        
        # Status frame
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Box)
        status_frame.setStyleSheet("QFrame { border: 1px solid #bdc3c7; border-radius: 5px; padding: 10px; background-color: #ecf0f1; }")
        status_layout = QVBoxLayout(status_frame)
        
        self.status_label = QLabel("Ready to process files")
        self.status_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        status_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        status_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(status_frame)
        
        # Current file being processed
        self.current_file_label = QLabel("")
        self.current_file_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.current_file_label.setVisible(False)
        main_layout.addWidget(self.current_file_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Select folder button
        self.select_folder_button = QPushButton("📁 Select Folder")
        self.select_folder_button.setMinimumHeight(50)
        self.select_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.select_folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_folder_button)
        
        # Help button
        help_button = QPushButton("❓ Help")
        help_button.setMinimumHeight(50)
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        help_button.clicked.connect(self.show_help)
        button_layout.addWidget(help_button)
        
        main_layout.addLayout(button_layout)
        
        # Results text area
        results_label = QLabel("Processing Log:")
        results_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        main_layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                background-color: #f8f9fa;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        self.results_text.setPlaceholderText("Processing details will appear here...")
        main_layout.addWidget(self.results_text)

    def check_dependencies_on_startup(self):
        """Check if Ollama is available when the app starts"""
        QTimer.singleShot(1000, self.validate_ollama)  # Check after 1 second delay

    def validate_ollama(self):
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                self.status_label.setText("✅ Ready to process files (Ollama connected)")
                self.status_label.setStyleSheet("font-weight: bold; color: #27ae60;")
                return True
            else:
                self.show_ollama_error()
                return False
        except:
            self.show_ollama_error()
            return False

    def show_ollama_error(self):
        """Show error message if Ollama is not available"""
        self.status_label.setText("⚠️ Ollama not detected - Please install and start Ollama")
        self.status_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Ollama Required")
        msg.setText("Ollama AI service is required but not detected.")
        msg.setInformativeText(
            "To use this application, you need to:\n\n"
            "1. Download and install Ollama from: https://ollama.ai/\n"
            "2. Open a terminal/command prompt\n"
            "3. Run: ollama pull gemma3:1b\n"
            "4. Keep Ollama running in the background\n\n"
            "Then restart this application."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def select_folder(self):
        """Handle folder selection and start processing"""
        if not self.validate_ollama():
            return
            
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "Select Folder Containing PDF/Text Files",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder_path:
            self.start_processing(folder_path)

    def start_processing(self, folder_path):
        """Start file processing in a separate thread"""
        # Disable button during processing
        self.select_folder_button.setEnabled(False)
        self.select_folder_button.setText("🔄 Processing...")
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.current_file_label.setVisible(True)
        
        # Clear previous results
        self.results_text.clear()
        self.results_text.append(f"Starting processing of folder: {folder_path}\n")
        
        # Start processing thread
        self.processing_thread = FileProcessingThread(folder_path)
        self.processing_thread.progress_update.connect(self.update_progress)
        self.processing_thread.file_processed.connect(self.file_processed)
        self.processing_thread.finished_processing.connect(self.processing_finished)
        self.processing_thread.start()

    def update_progress(self, percentage, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        self.results_text.append(f"[{percentage:3d}%] {message}")
        
        # Auto-scroll to bottom
        cursor = self.results_text.textCursor()
        cursor.movePosition(cursor.End)
        self.results_text.setTextCursor(cursor)

    def file_processed(self, filename):
        """Update current file being processed"""
        self.current_file_label.setText(f"Currently processing: {filename}")

    def processing_finished(self, success, message):
        """Handle completion of processing"""
        # Re-enable button
        self.select_folder_button.setEnabled(True)
        self.select_folder_button.setText("📁 Select Folder")
        
        # Hide progress elements
        self.progress_bar.setVisible(False)
        self.current_file_label.setVisible(False)
        
        # Update status
        if success:
            self.status_label.setText("✅ Processing completed successfully!")
            self.status_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            QMessageBox.information(self, "Success", message)
        else:
            self.status_label.setText("❌ Processing failed")
            self.status_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
            QMessageBox.critical(self, "Error", message)
        
        self.results_text.append(f"\n{'='*50}")
        self.results_text.append(f"FINAL RESULT: {message}")

    def show_help(self):
        """Show help dialog"""
        help_text = """
PDF Summarizer - Help

HOW TO USE:
1. Make sure Ollama is installed and running
2. Click "Select Folder" to choose a folder with PDF or text files
3. Wait for processing to complete
4. Find summaries in the "output_rag" folder

SUPPORTED FILES:
• PDF files (.pdf)
• Text files (.txt)

REQUIREMENTS:
• Ollama must be installed and running
• Internet connection for AI processing

TROUBLESHOOTING:
• If you see "Ollama not detected", install Ollama from https://ollama.ai/
• Run "ollama pull gemma3:1b" in terminal before using
• Make sure Ollama is running in the background

OUTPUT:
• Individual summary files: filename_rag_answer.txt
• Combined spreadsheet: summaries.xlsx
• Located in: [your_folder]/output_rag/
        """
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Help - PDF Summarizer")
        msg.setText("PDF Summarizer Help")
        msg.setDetailedText(help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def closeEvent(self, event):
        """Handle application closing"""
        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self, 
                'Confirm Exit', 
                'Processing is still running. Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.processing_thread.terminate()
                self.processing_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()