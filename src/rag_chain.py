"""
RAG Chain: Combines retrieval and generation
"""
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document

from src.vector_store import VectorStoreManager


class RAGChain:
    """Retrieval-Augmented Generation pipeline"""
    
    def __init__(self, 
                 vectorstore_manager: VectorStoreManager,
                 model_name: str = "gpt-3.5-turbo",
                 temperature: float = 0):
        """
        Args:
            vectorstore_manager: Initialized VectorStoreManager
            model_name: OpenAI model to use
            temperature: 0 = deterministic, 1 = creative
        """
        self.vectorstore = vectorstore_manager
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        
        # The prompt template that tells the LLM how to behave
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant for logistics and shipping operations.
            
Answer questions based ONLY on the provided context from company documents.

CRITICAL RULES:
1. If the answer is not in the context, say "I don't have that information in the available documents."
2. Always cite the source document and page number when providing information.
3. Be precise with numbers, dates, and regulatory information.
4. If context contains conflicting information, mention both and note the discrepancy.

Context from documents:
{context}
"""),
            ("human", "{question}")
        ])
    
    def format_docs(self, docs: List[Document]) -> str:
        """Format retrieved documents for the prompt"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'Unknown')
            formatted.append(
                f"--- Document {i} ---\n"
                f"Source: {source}, Page: {page}\n"
                f"{doc.page_content}\n"
            )
        return "\n".join(formatted)
    
    def ask(self, question: str, k: int = 4, verbose: bool = False) -> Dict:
        """
        Ask a question and get an answer with sources
        
        Args:
            question: User's question
            k: Number of document chunks to retrieve
            verbose: Whether to print retrieved chunks
        
        Returns:
            Dictionary with answer and source documents
        """
        # Step 1: Retrieve relevant chunks
        retrieved_docs = self.vectorstore.similarity_search(question, k=k)
        
        if verbose:
            print(f"\n🔍 Retrieved {len(retrieved_docs)} relevant chunks:")
            for i, doc in enumerate(retrieved_docs, 1):
                print(f"\n--- Chunk {i} ---")
                print(f"Source: {doc.metadata.get('source')}, Page: {doc.metadata.get('page')}")
                print(f"Content: {doc.page_content[:200]}...")
        
        # Step 2: Format context
        context = self.format_docs(retrieved_docs)
        
        # Step 3: Generate answer
        messages = self.prompt_template.format_messages(
            context=context,
            question=question
        )
        
        response = self.llm.invoke(messages)
        
        return {
            "answer": response.content,
            "source_documents": retrieved_docs,
            "question": question
        }
    
    def chat(self):
        """Interactive chat loop"""
        print("🤖 Logistics RAG Assistant")
        print("=" * 50)
        print("Ask questions about your documents. Type 'quit' to exit.\n")
        
        while True:
            question = input("You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            result = self.ask(question, verbose=False)
            print(f"\n🤖 Assistant: {result['answer']}\n")
            print(f"📄 Sources: {len(result['source_documents'])} documents")
            print("-" * 50 + "\n")


# Test function
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # This will work after you've created the vector store
    vs = VectorStoreManager()
    vs.load_vectorstore()
    
    rag = RAGChain(vs)
    rag.chat()