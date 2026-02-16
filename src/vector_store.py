"""
Vector store manager using Chroma + GoogleGenerativeAIEmbeddings (Gemini)
"""
import os
from typing import List, Optional

from langchain.schema import Document
from langchain.vectorstores import Chroma

# Gemini embeddings (langchain-google-genai)
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class VectorStoreManager:
    """
    Simple wrapper around a Chroma vector store.
    - create_vectorstore(documents): embed and persist to ./chroma_db
    - load_vectorstore(): load existing persisted Chroma store
    - similarity_search(query): run semantic search over the store
    """

    def __init__(self, persist_directory: str = "chroma_db", embedding_model: str = "models/gemini-embedding-001"):
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.embedding_fn: Optional[GoogleGenerativeAIEmbeddings] = None
        self.db: Optional[Chroma] = None

    def _get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        # Reuse single instance
        if self.embedding_fn is None:
            # The class will read GOOGLE_API_KEY from env if you don't pass api_key explicitly.
            # Optionally you can pass project/location/vertexai=True for Vertex AI usage.
            self.embedding_fn = GoogleGenerativeAIEmbeddings(
                model=self.embedding_model
            )
        return self.embedding_fn

    def create_vectorstore(self, documents: List[Document], collection_name: str = "default") -> None:
        """
        Create a new Chroma vector store from a list of LangChain Documents and persist it.
        """
        embeddings = self._get_embeddings()

        # Use LangChain's Chroma wrapper to create a persistent DB
        print(f"🔁 Creating vector store at '{self.persist_directory}' using embedding model '{self.embedding_model}'...")
        self.db = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,          # some langchain versions use embedding_function=...
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )

        # persist to disk (Chroma wrapper usually persists automatically, but call persist to be sure)
        try:
            self.db.persist()
        except Exception:
            # older/newer chroma/langchain API differences: some versions don't have persist()
            pass

        print("✅ Vector store created and persisted.")

    def load_vectorstore(self, collection_name: str = "default") -> None:
        """
        Load an existing Chroma vector store from disk.
        """
        embeddings = self._get_embeddings()
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(f"Persist directory '{self.persist_directory}' does not exist. Build the store first.")

        print(f"📦 Loading Chroma vector store from '{self.persist_directory}'...")
        # instantiate Chroma with the same embedding function
        try:
            # Newer LangChain/Chroma wrapper:
            self.db = Chroma(
                persist_directory=self.persist_directory,
                embedding=embeddings,
                collection_name=collection_name
            )
        except TypeError:
            # Fallback for versions that expect different kwarg name
            self.db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name=collection_name
            )

        print("✅ Vector store loaded.")

    def similarity_search(self, query: str, k: int = 4):
        """
        Run a similarity search over the loaded DB.
        Returns a list of LangChain Documents (or raises if DB not loaded).
        """
        if self.db is None:
            raise ValueError("Vector store is not loaded. Call load_vectorstore() or create_vectorstore() first.")

        # Some Chroma wrappers expect 'k' or 'n_results' depending on versions. Try common ones.
        try:
            return self.db.similarity_search(query, k=k)
        except TypeError:
            return self.db.similarity_search(query, k=k, include_metadata=True)
