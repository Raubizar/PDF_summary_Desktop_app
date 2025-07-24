# PDF Summarizer GUI

A desktop application that uses AI to summarize PDF and text documents using Retrieval-Augmented Generation (RAG).

## Features

- **GUI Interface**: Easy-to-use desktop application built with PyQt5
- **Folder Selection**: Select any folder containing PDF/text files
- **AI Summarization**: Uses Ollama with Gemma 3 model for intelligent summarization
- **RAG Technology**: Retrieval-Augmented Generation for better context-aware summaries
- **Batch Processing**: Processes multiple files automatically
- **Excel Output**: Creates a summary spreadsheet for easy review

## Prerequisites

### For Running the Executable
- **Ollama**: Must be installed and running on your system
  - Download from: https://ollama.ai/
  - Run: `ollama pull gemma3:1b` to download the required model

### For Development
- Python 3.7+
- All dependencies listed in `requirements.txt`

## Quick Start (End Users)

1. **Install Ollama**:
   - Download and install Ollama from https://ollama.ai/
   - Open terminal/command prompt and run: `ollama pull gemma3:1b`
   - Keep Ollama running in the background

2. **Run the Application**:
   - Download `PDF-Summarizer.exe` from the releases
   - Double-click to run
   - Click "Select Folder" and choose a folder with PDF/text files
   - Wait for processing to complete
   - Find summaries in the `output_rag` subfolder

## Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python src/main.py
   ```

## Building Executable

To create a standalone executable:

```bash
python build_exe.py
```

This will:
- Install PyInstaller if needed
- Create a single executable file
- Place it in the `dist/` folder

## How It Works

1. **File Selection**: User selects a folder containing documents
2. **Text Extraction**: Extracts text from PDF and text files
3. **Chunking**: Splits documents into manageable chunks
4. **Embedding**: Creates semantic embeddings using sentence transformers
5. **Retrieval**: Finds most relevant chunks for the query
6. **Generation**: Uses Ollama/Gemma to generate summaries based on relevant context
7. **Output**: Saves individual summaries and creates an Excel file

## Supported File Types

- PDF files (`.pdf`, `.PDF`)
- Text files (`.txt`)

## Output

The application creates:
- Individual summary files (`filename_rag_answer.txt`)
- Consolidated Excel file (`summaries.xlsx`)
- All outputs saved in `output_rag/` subfolder

## Installation
To install the required dependencies, run the following command:

```
pip install -r requirements.txt
```

## Usage
1. Run the application by executing the main script:
   ```
   python src/main.py
   ```
2. Use the folder selector to choose the directory containing your documents.
3. Click on the "Summarize" button to start the summarization process.
4. View the progress in the dialog and check the output for the generated summaries.

## Requirements
- Python 3.x
- Required libraries listed in `requirements.txt`

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.