# 📦 Logistics RAG System

A production-ready **Retrieval-Augmented Generation (RAG)** system built with Google Gemini for intelligent document question-answering. Upload PDF documents and get accurate, source-cited answers powered by AI.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🌟 Features

- **📄 PDF Document Processing** - Upload and automatically parse PDF files
- **🤖 AI-Powered Q&A** - Ask questions in natural language and get accurate answers
- **📚 Source Attribution** - Every answer includes citations from source documents
- **💾 Vector Database** - Efficient semantic search using ChromaDB
- **🔄 Real-time Updates** - Automatically rebuilds index when documents are added/removed
- **🎨 Clean UI** - Modern, professional web interface
- **⚡ Fast API** - RESTful API built with FastAPI
- **🔐 Document Management** - Upload, view, and delete documents easily

---

## 🏗️ Architecture

```
┌─────────────┐
│  User       │
│  Uploads    │
│  PDF        │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  1. Document Loader (PyPDF)         │
│     • Extracts text from PDF        │
│     • Splits into chunks            │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  2. Embeddings (Gemini)             │
│     • Converts chunks to vectors    │
│     • Captures semantic meaning     │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  3. Vector Store (ChromaDB)         │
│     • Stores document vectors       │
│     • Enables similarity search     │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  User asks a question               │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  4. Retrieval                       │
│     • Searches relevant chunks      │
│     • Ranks by similarity           │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  5. Generation (Gemini LLM)         │
│     • Reads retrieved context       │
│     • Generates accurate answer     │
│     • Cites sources                 │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **Git** (optional)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/logistics-rag.git
cd logistics-rag
```

**2. Create virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

**5. Run the application**

```bash
uvicorn app:app --reload
```

**6. Open your browser**

Navigate to: **http://localhost:8000**

---

## 📁 Project Structure

```
logistics-rag/
├── app.py                      # FastAPI backend
├── static/
│   └── index.html             # Web interface
├── src/
│   └── main.py                # CLI version (optional)
├── data/
│   └── raw/                   # Uploaded PDFs stored here
├── chroma_db/                 # Vector database (auto-generated)
├── requirements.txt           # Python dependencies
├── .env                       # API keys (not in git)
└── README.md                  # This file
```

---

## 🎯 Usage

### Web Interface

1. **Upload a PDF**: Click "Upload PDF" button in the header
2. **Wait for Processing**: System will chunk and embed the document
3. **Ask Questions**: Type your question in the chat input
4. **View Answers**: Get AI-generated responses with source citations

### API Endpoints

#### **Upload PDF**
```bash
POST /upload
Content-Type: multipart/form-data

Response:
{
  "message": "PDF uploaded and processed successfully",
  "filename": "document.pdf",
  "chunks_created": 23
}
```

#### **Ask Question**
```bash
POST /chat
Content-Type: application/json

{
  "question": "What is the next review date?",
  "include_sources": true
}

Response:
{
  "answer": "The next review date is January 2026.",
  "sources": [
    {
      "filename": "logistics_manual.pdf",
      "page": 1,
      "content": "Next Review Date: January 2026..."
    }
  ]
}
```

#### **List Documents**
```bash
GET /documents

Response:
{
  "documents": [
    {
      "filename": "logistics_manual.pdf",
      "size_kb": 27.7
    }
  ]
}
```

#### **Delete Document**
```bash
DELETE /documents/{filename}

Response:
{
  "message": "Deleted logistics_manual.pdf and rebuilt vector store",
  "remaining_documents": 0,
  "chunks_created": 0
}
```

---

## ⚙️ Configuration

Edit these variables in `app.py`:

```python
CHUNK_SIZE = 1000          # Characters per chunk
CHUNK_OVERLAP = 200        # Overlap between chunks
TOP_K = 5                  # Number of chunks to retrieve
GEMINI_MODEL = "models/gemini-2.5-flash"  # LLM model
```

---

## 🔧 Troubleshooting

### **Problem**: "No documents uploaded yet" error
**Solution**: Upload a PDF first before asking questions

### **Problem**: Embeddings fail with 404 error
**Solution**: Check you're using `models/gemini-embedding-001` (not `text-embedding-004`)

### **Problem**: ChromaDB file locked error
**Solution**: 
```bash
# Close all Python processes, then:
rmdir /s /q chroma_db  # Windows
rm -rf chroma_db       # Mac/Linux
```

### **Problem**: Answers are always "I don't have that information"
**Solution**: 
- Check if PDF has extractable text (not scanned images)
- Try increasing `TOP_K` value
- Verify vector store was created: check if `chroma_db/` folder exists

---

## 📦 Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0
langchain==0.1.0
langchain-community==0.0.13
langchain-google-genai==0.0.6
chromadb==0.4.22
pypdf==3.17.4
google-generativeai==0.3.2
```

---

## 🎨 Customization

### Change UI Colors

Edit `static/index.html`, line ~30:

```css
/* Primary color */
.upload-btn {
    background: #3182ce;  /* Change this */
}
```

### Change AI Model

Edit `app.py`, line ~25:

```python
GEMINI_MODEL = "models/gemini-1.5-pro"  # Better quality but slower
```

### Adjust Chunk Size

Edit `app.py`, line ~21:

```python
CHUNK_SIZE = 500      # Smaller = more precise
CHUNK_OVERLAP = 100   # More overlap = better context
```

---

## 🚀 Deployment

### Deploy to Railway

1. Create a `railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app:app --host 0.0.0.0 --port $PORT"
```

2. Push to GitHub
3. Connect to Railway
4. Add `GOOGLE_API_KEY` environment variable

### Deploy to Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: logistics-rag
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app:app --host 0.0.0.0 --port $PORT"
```

2. Push to GitHub
3. Connect to Render
4. Add `GOOGLE_API_KEY` environment variable

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** for the powerful LLM and embeddings
- **LangChain** for the RAG framework
- **ChromaDB** for vector storage
- **FastAPI** for the web framework

---

## 📧 Contact

**Your Name** - your.email@example.com

Project Link: [https://github.com/yourusername/logistics-rag](https://github.com/yourusername/logistics-rag)

---

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Conversation memory (multi-turn chat)
- [ ] Support for Word/Excel documents
- [ ] Table extraction from PDFs
- [ ] User authentication
- [ ] Document versioning
- [ ] Export chat history
- [ ] Dark mode UI
- [ ] Mobile app

---

## 📊 Performance

- **Upload Speed**: ~2-3 seconds per PDF page
- **Query Response**: ~1-2 seconds
- **Embedding Time**: ~500ms per 1000 tokens
- **Max PDF Size**: Recommended <10MB

---

## ❓ FAQ

**Q: Can I use OpenAI instead of Gemini?**  
A: Yes! Just change the embeddings and LLM classes to use OpenAI's API.

**Q: Does it work with scanned PDFs?**  
A: Not by default. You need to add OCR support with `pytesseract` and `pdf2image`.

**Q: Can I run this offline?**  
A: No, it requires internet for the Gemini API. Consider using local LLMs like Llama.

**Q: How much does it cost?**  
A: Gemini has a free tier with 15 requests/minute. Perfect for testing!

**Q: Can I add multiple PDFs?**  
A: Yes! Upload as many as you want. The system handles them all together.

---

Made by Ishika Agrawal
