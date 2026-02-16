"""
Main entry point for the RAG system (Gemini version)
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.document_loader import DocumentLoader
from src.vector_store import VectorStoreManager
from src.rag_chain import RAGChain


def setup_vectorstore(force_rebuild: bool = False):
    """Initialize or load the vector store"""

    vs_path = Path("./chroma_db")
    vectorstore_exists = vs_path.exists() and any(vs_path.iterdir())

    vs_manager = VectorStoreManager()

    if vectorstore_exists and not force_rebuild:
        print("📂 Found existing vector store. Loading...")
        vs_manager.load_vectorstore()
    else:
        print("🔨 Building vector store from scratch...")

        loader = DocumentLoader(chunk_size=1000, chunk_overlap=200)
        documents = loader.load_directory("./data/raw")

        vs_manager.create_vectorstore(documents)

    return vs_manager


def main():
    """Main function"""
    load_dotenv()

    # ✅ Gemini API key check
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY not found in .env file!")

    print("\n" + "=" * 60)
    print("🚀 LOGISTICS RAG SYSTEM (Gemini)")
    print("=" * 60 + "\n")

    vs_manager = setup_vectorstore(force_rebuild=False)

    # ✅ Gemini model
    rag = RAGChain(
        vectorstore_manager=vs_manager,
        model_name="gemini-2.5-flash",
        temperature=0
    )

    rag.chat()


if __name__ == "__main__":
    main()
