"""
Document Loader: Extracts text from PDFs and chunks them
"""
from typing import List
from pathlib import Path
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class DocumentLoader:
    """Handles PDF loading and text chunking"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Character overlap between chunks (preserves context)
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]  # Try to split at paragraph > line > word
        )
    
    def load_pdf(self, pdf_path: str) -> List[Document]:
        """Load a single PDF and return chunks"""
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        
        # Add metadata
        for page in pages:
            page.metadata['source'] = Path(pdf_path).name
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(pages)
        
        print(f"✓ Loaded {pdf_path}: {len(pages)} pages → {len(chunks)} chunks")
        return chunks
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """Load all PDFs from a directory"""
        all_chunks = []
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        
        if not pdf_files:
            raise ValueError(f"No PDF files found in {directory_path}")
        
        for pdf_path in pdf_files:
            chunks = self.load_pdf(str(pdf_path))
            all_chunks.extend(chunks)
        
        print(f"\n📚 Total: {len(all_chunks)} chunks from {len(pdf_files)} PDFs")
        return all_chunks


# Quick test function
if __name__ == "__main__":
    loader = DocumentLoader()
    # Test with: python src/document_loader.py
    # (After you add PDFs to data/raw/)