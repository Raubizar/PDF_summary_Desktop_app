import os
from pathlib import Path
import re
import numpy as np
import ollama
from sentence_transformers import SentenceTransformer
import PyPDF2
from config.settings import Settings


def read_file(file_path: Path) -> str:
    """Read text content from PDF or TXT files with better error handling"""
    try:
        if file_path.suffix.lower() == ".txt":
            return file_path.read_text(encoding="utf-8")
        elif file_path.suffix.lower() == ".pdf":
            text = ""
            with file_path.open("rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {page_num + 1} of {file_path.name}: {e}")
                        continue
            
            if not text.strip():
                raise ValueError(f"No text could be extracted from PDF: {file_path.name}")
            return text
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}. Supported types: .pdf, .txt")
    except Exception as e:
        raise Exception(f"Error reading file {file_path.name}: {str(e)}")


def clean_text(text: str) -> str:
    """Remove bibliography/references sections and clean up text"""
    # Remove bibliography/references section
    match = re.search(r"(Bibliography|References|Works Cited)", text, re.IGNORECASE)
    if match:
        text = text[:match.start()]
    
    # Basic text cleaning
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize line breaks
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    return text.strip()


def chunk_text(text: str, max_chunk_length: int = None) -> list:
    """Split text into manageable chunks for RAG processing"""
    if max_chunk_length is None:
        settings = Settings()
        max_chunk_length = settings.get_max_chunk_length()
    
    # Split by paragraphs first
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # If adding this paragraph would exceed the limit
        if len(current_chunk) + len(para) + 2 > max_chunk_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
            else:
                # Paragraph is longer than max_chunk_length, split by sentences
                sentences = re.split(r'[.!?]+', para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    if len(current_chunk) + len(sentence) + 1 > max_chunk_length:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                    else:
                        current_chunk += sentence + ". "
        else:
            current_chunk += para + "\n\n"
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return [chunk for chunk in chunks if len(chunk.strip()) > 50]  # Filter out very short chunks


def embed_chunks(chunks: list, embedder) -> np.ndarray:
    """Create embeddings for text chunks with error handling"""
    try:
        embeddings = []
        for i, chunk in enumerate(chunks):
            try:
                embedding = embedder.encode(chunk)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Warning: Could not embed chunk {i + 1}: {e}")
                # Use zero vector as fallback
                embedding_size = 384  # Standard size for all-MiniLM-L6-v2
                embeddings.append(np.zeros(embedding_size))
        
        return np.array(embeddings)
    except Exception as e:
        raise Exception(f"Error creating embeddings: {str(e)}")


def retrieve_relevant_chunks(query: str, chunks: list, chunk_embeddings: np.ndarray,
                              embedder, top_k: int = None) -> list:
    """Retrieve the most relevant chunks for the query"""
    if top_k is None:
        settings = Settings()
        top_k = settings.get_top_k_retrieval()
    
    try:
        query_embedding = embedder.encode(query)
        
        # Calculate cosine similarity
        norms = np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_embedding)
        # Add small epsilon to avoid division by zero
        similarities = np.dot(chunk_embeddings, query_embedding) / (norms + 1e-10)
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Filter out chunks with very low similarity (< 0.1)
        relevant_chunks = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                relevant_chunks.append(chunks[idx])
        
        # Ensure we have at least one chunk
        if not relevant_chunks and chunks:
            relevant_chunks = [chunks[top_indices[0]]]
        
        return relevant_chunks
    except Exception as e:
        print(f"Warning: Error in chunk retrieval: {e}")
        # Fallback: return first few chunks
        return chunks[:min(top_k, len(chunks))]


def rag_summarize(document_text: str, query: str = None) -> str:
    """
    Perform RAG-based summarization of document text
    """
    try:
        settings = Settings()
        
        if query is None:
            query = settings.get_default_query()
        
        # Clean and chunk the text
        cleaned_text = clean_text(document_text)
        if not cleaned_text.strip():
            return "Error: No readable text found in the document."
        
        chunks = chunk_text(cleaned_text, settings.get_max_chunk_length())
        if not chunks:
            return "Error: Document could not be processed into chunks."
        
        # Create embeddings
        embedder_model = settings.get_embedder_model()
        try:
            embedder = SentenceTransformer(embedder_model)
        except Exception as e:
            return f"Error: Could not load embedding model {embedder_model}: {str(e)}"
        
        embeddings = embed_chunks(chunks, embedder)
        
        # Retrieve relevant chunks
        relevant_chunks = retrieve_relevant_chunks(
            query, chunks, embeddings, embedder, settings.get_top_k_retrieval()
        )
        
        if not relevant_chunks:
            return "Error: No relevant content found in the document."
        
        # Prepare context for the AI model
        context = "\n\n---\n\n".join(relevant_chunks)
        
        # Limit context length to avoid token limits
        max_context_length = 4000  # Conservative limit for Gemma
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        # Create prompt for Ollama
        prompt = f"""Based on the following document content, please provide a comprehensive summary that addresses this question: {query}

Document Content:
{context}

Please provide a clear, structured summary that:
1. Captures the main points and key insights
2. Is well-organized and easy to understand
3. Focuses on the most important information
4. Is concise but comprehensive

Summary:"""

        # Call Ollama for summarization
        try:
            response = ollama.generate(model="gemma3:1b", prompt=prompt)
            summary = response.get("response", "").strip()
            
            if not summary:
                return "Error: AI model returned empty response. Please check Ollama is running."
            
            return summary
            
        except Exception as e:
            return f"Error: Could not generate summary using AI model: {str(e)}. Please ensure Ollama is running and the 'gemma3:1b' model is installed."
    
    except Exception as e:
        return f"Error during summarization: {str(e)}"