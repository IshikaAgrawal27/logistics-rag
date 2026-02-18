"""
app.py - FastAPI backend for RAG system
Run: uvicorn app:app --reload
"""
import os
import sys
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
load_dotenv()

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"
STATIC_DIR = PROJECT_ROOT / "static"
COLLECTION = "logistics_docs"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5
GEMINI_MODEL = "models/gemini-2.5-flash"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────
app = FastAPI(title="Logistics RAG System")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ─────────────────────────────────────────────
# GLOBAL STATE
# ─────────────────────────────────────────────
vectorstore = None
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def safe_delete_chromadb(path: Path):
    """Delete ChromaDB directory"""
    if path.exists():
        try:
            shutil.rmtree(path)
            print(f"✓ Deleted vector store at {path}")
        except Exception as e:
            print(f"Warning: Could not delete {path}: {e}")


def load_documents():
    """Load and chunk all PDFs from raw directory"""
    pdf_files = list(RAW_DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        raise ValueError(f"No PDFs found in {RAW_DATA_DIR}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    all_chunks = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        chunks = splitter.split_documents(pages)

        for chunk in chunks:
            chunk.metadata["source"] = pdf_path.name

        all_chunks.extend(chunks)
        print(f"  ✓ {pdf_path.name}: {len(pages)} pages → {len(chunks)} chunks")

    return all_chunks


def rebuild_vectorstore():
    """Rebuild the vector store from PDFs"""
    global vectorstore
    
    print("\n🔨 Rebuilding vector store...")
    safe_delete_chromadb(CHROMA_DB_DIR)
    
    chunks = load_documents()
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=str(CHROMA_DB_DIR)
    )
    
    print(f"✓ Built vector store with {len(chunks)} chunks\n")
    return len(chunks)


def get_answer(question: str, include_sources: bool = True):
    """Get answer from RAG system"""
    global vectorstore
    
    if vectorstore is None:
        # Try to load existing vectorstore
        if CHROMA_DB_DIR.exists():
            vectorstore = Chroma(
                collection_name=COLLECTION,
                embedding_function=embeddings,
                persist_directory=str(CHROMA_DB_DIR)
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="No documents uploaded yet. Please upload a PDF first."
            )
    
    # Retrieve relevant chunks
    docs = vectorstore.similarity_search(question, k=TOP_K)
    
    if not docs:
        return {
            "answer": "I couldn't find any relevant information in the documents.",
            "sources": []
        }
    
    # Build context
    context_parts = []
    sources = []
    
    for i, doc in enumerate(docs, 1):
        src = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        context_parts.append(f"[Excerpt {i} | {src} | page {page}]\n{doc.page_content}")
        
        if include_sources:
            sources.append({
                "filename": src,
                "page": page,
                "content": doc.page_content[:200] + "..."
            })
    
    context = "\n\n".join(context_parts)
    
    # Generate answer with Gemini
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
        convert_system_message_to_human=True
    )
    
    prompt_template = """You are a helpful logistics assistant. Use the document excerpts below to answer the question.

Rules:
- Answer using ONLY the information in the excerpts.
- Quote exact numbers, names, and codes where possible.
- If the excerpts do not contain the answer, say: "I could not find that information in the provided documents."
- Be concise and clear.

Document excerpts:
----------------
{context}
----------------

Question: {question}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("human", prompt_template)
    ])
    
    messages = prompt.format_messages(context=context, question=question)
    response = llm.invoke(messages)
    
    return {
        "answer": response.content,
        "sources": sources if include_sources else []
    }


# ─────────────────────────────────────────────
# API MODELS
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str
    include_sources: bool = True


class ChatResponse(BaseModel):
    answer: str
    sources: list


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int


# ─────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────
@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF and rebuild the vector store"""
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save the uploaded file
    file_path = RAW_DATA_DIR / file.filename
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    print(f"✓ Saved {file.filename} to {RAW_DATA_DIR}")
    
    # Rebuild vector store
    try:
        chunks_created = rebuild_vectorstore()
        
        return UploadResponse(
            message="PDF uploaded and processed successfully",
            filename=file.filename,
            chunks_created=chunks_created
        )
    except Exception as e:
        # Clean up the file if processing fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Ask a question and get an answer"""
    
    try:
        result = get_answer(request.question, request.include_sources)
        return ChatResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/documents")
async def list_documents():
    """List all uploaded PDFs"""
    pdf_files = list(RAW_DATA_DIR.glob("*.pdf"))
    
    return {
        "documents": [
            {
                "filename": f.name,
                "size_kb": round(f.stat().st_size / 1024, 2)
            }
            for f in pdf_files
        ]
    }


@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a PDF and rebuild vector store"""
    
    file_path = RAW_DATA_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete the file
    file_path.unlink()
    print(f"✓ Deleted {filename}")
    
    # Rebuild vector store with remaining PDFs
    pdf_files = list(RAW_DATA_DIR.glob("*.pdf"))
    
    if pdf_files:
        chunks_created = rebuild_vectorstore()
        return {
            "message": f"Deleted {filename} and rebuilt vector store",
            "remaining_documents": len(pdf_files),
            "chunks_created": chunks_created
        }
    else:
        # No PDFs left, clear the vector store
        safe_delete_chromadb(CHROMA_DB_DIR)
        global vectorstore
        vectorstore = None
        return {
            "message": f"Deleted {filename}. No documents remaining.",
            "remaining_documents": 0,
            "chunks_created": 0
        }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "vectorstore_initialized": vectorstore is not None
    }


# ─────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Load vector store on startup if it exists"""
    global vectorstore
    
    if CHROMA_DB_DIR.exists():
        try:
            vectorstore = Chroma(
                collection_name=COLLECTION,
                embedding_function=embeddings,
                persist_directory=str(CHROMA_DB_DIR)
            )
            count = vectorstore._collection.count()
            print(f"✓ Loaded vector store with {count} vectors")
        except Exception as e:
            print(f"Warning: Could not load vector store: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)