from pathlib import Path
import pandas as pd
from .summarizer import read_file, rag_summarize


def process_files(folder_path: str) -> bool:
    """
    Process all supported files in the specified folder and generate summaries.
    This is the main function called from the GUI.
    """
    try:
        input_folder = Path(folder_path)
        output_folder = input_folder / "output_rag"
        output_folder.mkdir(exist_ok=True)
        
        query = "Summarize the key points of this document or the main argument."
        
        files = list(input_folder.glob("*.txt")) + list(input_folder.glob("*.pdf")) + list(input_folder.glob("*.PDF"))
        
        if not files:
            print("No supported files found in the input folder.")
            return False
        
        results = []
        for file in files:
            print(f"\nProcessing file: {file.name} with RAG.")
            result = process_file(file, output_folder, query)
            if result:
                results.append(result)
        
        if results:
            df = pd.DataFrame(results, columns=["Filename", "Summary"])
            excel_path = output_folder / "summaries.xlsx"
            df.to_excel(excel_path, index=False)
            print(f"\nAll summaries saved to {excel_path}")
            return True
        
        return False
    except Exception as e:
        print(f"Error processing files: {e}")
        return False


def process_file(file_path: Path, output_folder: Path, query: str):
    """
    Process a file using RAG: read the file, summarize it,
    save the summary as a .txt file, and return (filename, summary).
    """
    try:
        text = read_file(file_path)
    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")
        return None

    try:
        answer = rag_summarize(text, query)
        output_file = output_folder / f"{file_path.stem}_rag_answer.txt"
        output_file.write_text(answer, encoding="utf-8")
        print(f"RAG answer for {file_path.name} saved to {output_file}")
        return file_path.name, answer
    except Exception as e:
        print(f"Error summarizing {file_path.name}: {e}")
        return None