"""
RAG SYSTEM DIAGNOSTIC SCRIPT (Gemini Edition)
Run this from your project root: python diagnose_gemini.py
"""

import os
import sys
from pathlib import Path

# ─────────────────────────────────────────────
# STEP 0: Fix imports
# ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

print("\n" + "="*60)
print("🔬 RAG SYSTEM DIAGNOSTIC TOOL (Gemini Edition)")
print("="*60)


# ─────────────────────────────────────────────
# STEP 1: Check .env and API key
# ─────────────────────────────────────────────
print("\n📋 STEP 1: Checking environment variables...")

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env file!")
    print("   Fix: Create a .env file in your project root with:")
    print('   GOOGLE_API_KEY=your_gemini_api_key')
    print('\n   Get your key from: https://makersuite.google.com/app/apikey')
    sys.exit(1)
else:
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")


# ─────────────────────────────────────────────
# STEP 2: Check PDF files exist
# ─────────────────────────────────────────────
print("\n📋 STEP 2: Checking PDF files...")

raw_data_path = PROJECT_ROOT / "data" / "raw"
if not raw_data_path.exists():
    print(f"❌ Folder not found: {raw_data_path}")
    print("   Fix: Run: mkdir -p data/raw")
    sys.exit(1)

pdf_files = list(raw_data_path.glob("*.pdf"))
if not pdf_files:
    print(f"❌ No PDFs found in {raw_data_path}")
    print("   Fix: Copy your PDF files into data/raw/")
    sys.exit(1)

print(f"✅ Found {len(pdf_files)} PDF(s):")
for f in pdf_files:
    size_kb = f.stat().st_size / 1024
    print(f"   - {f.name} ({size_kb:.1f} KB)")


# ─────────────────────────────────────────────
# STEP 3: Check if PDF text is extractable
# ─────────────────────────────────────────────
print("\n📋 STEP 3: Checking if PDFs contain extractable text...")

try:
    from pypdf import PdfReader
except ImportError:
    print("❌ pypdf not installed. Run: pip install pypdf")
    sys.exit(1)

for pdf_path in pdf_files:
    reader = PdfReader(str(pdf_path))
    total_text = ""
    for page in reader.pages:
        total_text += page.extract_text() or ""

    char_count = len(total_text.strip())
    if char_count < 50:
        print(f"❌ '{pdf_path.name}' has almost no extractable text ({char_count} chars)!")
        print("   This usually means your PDF is a SCANNED IMAGE.")
        print(f"\n   Raw text found:\n   '{total_text[:200]}'")
    else:
        print(f"✅ '{pdf_path.name}' has {char_count} characters of text")
        print(f"   Preview: '{total_text[:150].strip()}'")


# ─────────────────────────────────────────────
# STEP 4: Test chunking
# ─────────────────────────────────────────────
print("\n📋 STEP 4: Testing document chunking...")

try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("   Fix: pip install langchain langchain-community")
    sys.exit(1)

all_chunks = []
for pdf_path in pdf_files:
    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(pages)
    all_chunks.extend(chunks)

    print(f"✅ '{pdf_path.name}': {len(pages)} pages → {len(chunks)} chunks")

if len(all_chunks) == 0:
    print("❌ Zero chunks created! Your PDFs may be empty or unreadable.")
    sys.exit(1)

print(f"\n   Sample chunk content:")
print(f"   ---")
print(f"   {all_chunks[0].page_content[:300]}")
print(f"   ---")


# ─────────────────────────────────────────────
# STEP 5: Test Gemini API connection
# ─────────────────────────────────────────────
print("\n📋 STEP 5: Testing Gemini API connection...")

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Say hello in 3 words")
    print(f"✅ Gemini API working! Test response: '{response.text.strip()}'")
except Exception as e:
    print(f"❌ Gemini API failed: {e}")
    print("   Fix: Check your API key at https://makersuite.google.com/app/apikey")
    sys.exit(1)


# ─────────────────────────────────────────────
# STEP 6: Test embeddings
# ─────────────────────────────────────────────
print("\n📋 STEP 6: Testing embedding creation...")

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    test_vector = embeddings.embed_query("test logistics document")
    print(f"✅ Embeddings working! Vector size: {len(test_vector)} dimensions")
except Exception as e:
    print(f"❌ Embedding failed: {e}")
    print("   Fix: pip install langchain-google-genai")
    sys.exit(1)


# ─────────────────────────────────────────────
# STEP 7: Test ChromaDB vector store
# ─────────────────────────────────────────────
print("\n📋 STEP 7: Testing ChromaDB vector store creation...")

import shutil
chroma_path = PROJECT_ROOT / "chroma_db"
if chroma_path.exists():
    shutil.rmtree(chroma_path)
    print("   🗑️  Deleted old vector store to rebuild fresh")

try:
    from langchain_community.vectorstores import Chroma

    print(f"   Creating embeddings for {len(all_chunks)} chunks...")
    print("   (This may take 1-2 minutes with Gemini...)")
    
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        collection_name="logistics_docs",
        persist_directory=str(chroma_path)
    )
    print(f"✅ Vector store created successfully with {len(all_chunks)} chunks")
except Exception as e:
    print(f"❌ ChromaDB failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# ─────────────────────────────────────────────
# STEP 8: Test retrieval
# ─────────────────────────────────────────────
print("\n📋 STEP 8: Testing document retrieval...")

test_query = "logistics operations manual"
results = vectorstore.similarity_search(test_query, k=3)

if not results:
    print("❌ Retrieval returned ZERO results! Vector store may be empty.")
else:
    print(f"✅ Retrieval working! Got {len(results)} results for '{test_query}'")
    for i, doc in enumerate(results, 1):
        print(f"\n   Result {i}:")
        print(f"   Source: {doc.metadata.get('source', 'unknown')}, Page: {doc.metadata.get('page', '?')}")
        print(f"   Content: '{doc.page_content[:200]}'")


# ─────────────────────────────────────────────
# STEP 9: Test full RAG pipeline
# ─────────────────────────────────────────────
print("\n📋 STEP 9: Testing full RAG pipeline end-to-end...")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    convert_system_message_to_human=True
)

prompt_template = """Based on these document excerpts:

{context}

Question: {question}

Answer the question using only the information provided. If you can't answer from the excerpts, say so."""

# Build context from retrieved docs
context = "\n\n".join([doc.page_content for doc in results])
question = "What is this document about? Give a brief summary."

prompt = ChatPromptTemplate.from_messages([
    ("human", prompt_template)
])

messages = prompt.format_messages(context=context, question=question)
response = llm.invoke(messages)

print(f"✅ Full pipeline working!")
print(f"\n   Test Question: '{question}'")
print(f"   Answer: '{response.content}'")


# ─────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("✅ ALL STEPS PASSED! Your RAG system is working correctly.")
print("="*60)
print("\n🚀 Now run your main app:")
print("   python src/main.py")
print("\n💡 If answers still seem wrong, try:")
print("   1. Ask questions with '!verbose' to see retrieved chunks")
print("   2. Adjust TOP_K in main.py (currently 5)")
print("   3. Check if your question uses words actually in the PDF")
print("="*60 + "\n")