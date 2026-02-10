"""
Vector Store: Manages embeddings and retrieval
"""
from typing import List, Optional
import chromadb
from chromadb.config import Settings

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document


class VectorStoreManager:
    """Manages ChromaDB vector store for document retrieval"""
    
    def __init__(self, 
                 collection_name: str = "logistics_docs",
                 persist_directory: str = "./chroma_db"):
        """
        Args:
            collection_name: Name for the vector store collection
            persist_directory: Where to save the database
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()  # Uses OPENAI_API_KEY from env
        self.vectorstore = None
    
    def create_vectorstore(self, documents: List[Document]) -> None:
        """Create vector store from documents"""
        print(f"🔄 Creating embeddings for {len(documents)} chunks...")
        print("   (This may take 1-2 minutes depending on document size)")
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )
        
        print(f"✓ Vector store created and saved to {self.persist_directory}")
    
    def load_vectorstore(self) -> None:
        """Load existing vector store from disk"""
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        print(f"✓ Loaded existing vector store from {self.persist_directory}")
    
    def similarity_search(self, 
                         query: str, 
                         k: int = 4) -> List[Document]:
        """
        Search for relevant documents
        
        Args:
            query: User's question
            k: Number of top results to return
        
        Returns:
            List of relevant document chunks
        """
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Call create_vectorstore() or load_vectorstore() first.")
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, 
                                     query: str, 
                                     k: int = 4) -> List[tuple]:
        """Search with relevance scores"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized.")
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results


# Quick test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    vs = VectorStoreManager()
    # Test with: python src/vector_store.py