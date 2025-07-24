import os

class Settings:
    def __init__(self):
        self.default_query = "Summarize the key points of this document or the main argument."
        self.max_chunk_length = 2500
        self.top_k_retrieval = 3
        self.output_folder_name = "output_summaries"
        self.embedder_model = "all-MiniLM-L6-v2"
        self.pdf_reader = "PyPDF2"
    
    def get_output_folder(self):
        return os.path.join(os.getcwd(), self.output_folder_name)

    def get_embedder_model(self):
        return self.embedder_model

    def get_max_chunk_length(self):
        return self.max_chunk_length

    def get_top_k_retrieval(self):
        return self.top_k_retrieval

    def get_default_query(self):
        return self.default_query