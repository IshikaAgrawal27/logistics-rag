"""
Main entry point for the RAG system
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# FIX: Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.document_loader import DocumentLoader
from src.vector_store import VectorStoreManager
from src.rag_chain import RAGChain


def setup_vectorstore(force_rebuild: bool = False):
    """Initialize or load the vector store"""
    
    # Check if vector store already exists
    vs_path = Path("./chroma_db")
    vectorstore_exists = vs_path.exists() and any(vs_path.iterdir())
    
    vs_manager = VectorStoreManager()
    
    if vectorstore_exists and not force_rebuild:
        print("📂 Found existing vector store. Loading...")
        vs_manager.load_vectorstore()
    else:
        print("🔨 Building vector store from scratch...")
        
        # Load documents
        loader = DocumentLoader(chunk_size=1000, chunk_overlap=200)
        documents = loader.load_directory("./data/raw")
        
        # Create vector store
        vs_manager.create_vectorstore(documents)
    
    return vs_manager


def main():
    """Main function"""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in .env file!")
    
    print("\n" + "="*60)
    print("🚀 LOGISTICS RAG SYSTEM")
    print("="*60 + "\n")
    
    # Setup
    vs_manager = setup_vectorstore(force_rebuild=False)
    
    # Initialize RAG chain
    rag = RAGChain(
        vectorstore_manager=vs_manager,
        model_name="gpt-3.5-turbo",  # or "gpt-4" for better quality
        temperature=0
    )
    
    # Start interactive chat
    rag.chat()


if __name__ == "__main__":
    main()