# Logistics RAG System - Architecture Document

## Document Information
- **Project**: Logistics RAG (Retrieval-Augmented Generation) System
- **Version**: 1.0
- **Last Updated**: February 2026
- **Author**: System Architecture Team

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Patterns](#architecture-patterns)
4. [Component Architecture](#component-architecture)
5. [Data Flow](#data-flow)
6. [Technology Stack](#technology-stack)
7. [Deployment Architecture](#deployment-architecture)
8. [Security Architecture](#security-architecture)
9. [Scalability & Performance](#scalability--performance)
10. [Future Enhancements](#future-enhancements)

---

## 1. Executive Summary

### 1.1 Purpose
The Logistics RAG System is an intelligent document query system that enables users to interact with logistics documentation through natural language. The system addresses the critical challenge of quickly retrieving accurate, context-aware information from large volumes of technical manuals, shipping manifests, and regulatory documents.

### 1.2 Key Objectives
- **Accuracy**: Provide factually correct answers grounded in source documents
- **Speed**: Retrieve information in milliseconds vs. manual document search
- **Privacy**: Process proprietary logistics data without external training
- **Compliance**: Maintain audit trails for regulatory requirements

### 1.3 Business Value
- Reduces document search time by 95% (from 20 minutes to <10 seconds)
- Eliminates hallucination risks present in general-purpose AI systems
- Enables 24/7 self-service access to logistics knowledge
- Improves compliance through accurate regulatory information retrieval

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                    (CLI / Web / API Endpoints)                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │   Query     │  │   Document   │  │   Orchestration     │   │
│  │  Processor  │  │   Ingestion  │  │   Controller        │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RAG PIPELINE LAYER                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  Retrieval  │  │  Embedding   │  │    Generation       │   │
│  │   Engine    │  │   Service    │  │      (LLM)          │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │   Vector    │  │   Document   │  │    Metadata         │   │
│  │  Database   │  │    Store     │  │      Store          │   │
│  │ (ChromaDB)  │  │   (S3/Local) │  │   (SQLite/Postgres) │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 System Context Diagram

```
                    ┌──────────────┐
                    │              │
                    │   End Users  │
                    │  (Logistics  │
                    │  Operations) │
                    │              │
                    └──────┬───────┘
                           │
                           │ Natural Language Queries
                           ▼
              ┌────────────────────────┐
              │                        │
              │   Logistics RAG System │◄────── PDF Documents
              │                        │
              └────────┬───────────────┘
                       │
                       │ API Calls
                       ▼
         ┌─────────────────────────────┐
         │                             │
         │   OpenAI Embeddings API     │
         │   OpenAI Chat Completions   │
         │                             │
         └─────────────────────────────┘
```

### 2.3 Core Capabilities
1. **Document Ingestion**: PDF parsing, text extraction, intelligent chunking
2. **Semantic Search**: Vector-based similarity matching
3. **Context-Aware Generation**: LLM-powered answer synthesis
4. **Source Attribution**: Automatic citation with page numbers
5. **Conversational Interface**: Multi-turn dialogue support (future)

---

## 3. Architecture Patterns

### 3.1 Primary Pattern: RAG (Retrieval-Augmented Generation)

**Definition**: Combines information retrieval with language generation to produce accurate, grounded responses.

**Why RAG over Fine-Tuning?**
| Aspect | RAG | Fine-Tuning |
|--------|-----|-------------|
| **Data Updates** | Instant (re-index documents) | Slow (retrain model) |
| **Cost** | Low (pay per query) | High (training GPU costs) |
| **Accuracy** | High (uses exact sources) | Medium (can hallucinate) |
| **Privacy** | High (data stays local) | Low (data used in training) |

### 3.2 Supporting Patterns

#### 3.2.1 Pipeline Architecture
- Sequential processing: Load → Chunk → Embed → Store → Retrieve → Generate
- Each stage is independently testable and replaceable

#### 3.2.2 Separation of Concerns
- **Document Loader**: PDF parsing only
- **Vector Store Manager**: Embedding and retrieval only
- **RAG Chain**: Orchestration and generation only

#### 3.2.3 Configuration-Driven Design
- Embedding model, chunk size, retrieval parameters externalized
- Allows experimentation without code changes

---

## 4. Component Architecture

### 4.1 Document Loader Component

```
┌────────────────────────────────────────────────┐
│          DocumentLoader                        │
├────────────────────────────────────────────────┤
│  Responsibilities:                             │
│  • PDF text extraction                         │
│  • Text chunking (recursive splitter)          │
│  • Metadata enrichment (source, page, chunk_id)│
├────────────────────────────────────────────────┤
│  Key Methods:                                  │
│  + load_pdf(path) → List[Document]            │
│  + load_directory(path) → List[Document]      │
├────────────────────────────────────────────────┤
│  Dependencies:                                 │
│  • PyPDFLoader (langchain-community)           │
│  • RecursiveCharacterTextSplitter             │
└────────────────────────────────────────────────┘
```

**Design Decisions**:
- **Chunk Size (1000 chars)**: Balance between context preservation and embedding efficiency
- **Chunk Overlap (200 chars)**: Prevents splitting of critical context across boundaries
- **Recursive Splitting**: Prioritizes natural text boundaries (paragraphs → sentences → words)

### 4.2 Vector Store Manager Component

```
┌────────────────────────────────────────────────┐
│         VectorStoreManager                     │
├────────────────────────────────────────────────┤
│  Responsibilities:                             │
│  • Generate embeddings via OpenAI API          │
│  • Persist vectors in ChromaDB                 │
│  • Execute similarity searches                 │
├────────────────────────────────────────────────┤
│  Key Methods:                                  │
│  + create_vectorstore(docs)                    │
│  + load_vectorstore()                          │
│  + similarity_search(query, k) → List[Doc]    │
│  + similarity_search_with_score(query, k)     │
├────────────────────────────────────────────────┤
│  Dependencies:                                 │
│  • OpenAIEmbeddings (text-embedding-3-small)   │
│  • ChromaDB (vector database)                  │
└────────────────────────────────────────────────┘
```

**Design Decisions**:
- **ChromaDB**: Chosen for simplicity (no server required), suitable for <1M documents
- **OpenAI Embeddings**: text-embedding-3-small (1536 dimensions, $0.02/1M tokens)
- **Persistence**: Local disk storage with automatic serialization

### 4.3 RAG Chain Component

```
┌────────────────────────────────────────────────┐
│              RAGChain                          │
├────────────────────────────────────────────────┤
│  Responsibilities:                             │
│  • Orchestrate retrieval + generation          │
│  • Format context for LLM prompt               │
│  • Manage conversational flow                  │
│  • Enforce grounding constraints               │
├────────────────────────────────────────────────┤
│  Key Methods:                                  │
│  + ask(question, k, verbose) → Dict           │
│  + chat() → Interactive loop                   │
│  + format_docs(docs) → String                 │
├────────────────────────────────────────────────┤
│  Dependencies:                                 │
│  • ChatOpenAI (gpt-3.5-turbo / gpt-4)         │
│  • VectorStoreManager                          │
│  • ChatPromptTemplate                          │
└────────────────────────────────────────────────┘
```

**Design Decisions**:
- **Temperature=0**: Deterministic outputs for consistency
- **System Prompt**: Explicitly forbids hallucination, requires source citation
- **Top-K=4**: Balance between context richness and token costs

---

## 5. Data Flow

### 5.1 Document Ingestion Flow

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌───────────┐      ┌──────────┐
│   PDF   │─────►│  Parse   │─────►│  Chunk   │─────►│  Embed    │─────►│  Store   │
│  Files  │      │   Text   │      │   Text   │      │ (API Call)│      │ (Vector) │
└─────────┘      └──────────┘      └──────────┘      └───────────┘      └──────────┘
                      ▲                  ▲                  ▲                  ▲
                      │                  │                  │                  │
              PyPDFLoader    RecursiveTextSplitter   OpenAI API         ChromaDB

Metadata Added: source, page, chunk_id
```

**Processing Steps**:
1. **PDF → Text**: PyPDFLoader extracts text page-by-page
2. **Text → Chunks**: Splitter creates 1000-char chunks with 200-char overlap
3. **Chunks → Vectors**: OpenAI API converts text to 1536-dim embeddings
4. **Vectors → DB**: ChromaDB persists embeddings with metadata

**Performance Metrics**:
- 1-page PDF: ~2 seconds
- 100-page PDF: ~30-45 seconds
- Rate limit: OpenAI allows 3,000 RPM (requests per minute)

### 5.2 Query Processing Flow

```
User Question
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ "What are the hazmat protocols at Port X?"                  │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│  Embed Query        │  (OpenAI API: text → 1536-dim vector)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Vector Search      │  (ChromaDB: cosine similarity)
│  Top-K = 4          │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Retrieved Chunks:                                          │
│  1. "Hazmat Class 3 materials require storage at Port X..." │
│  2. "Port X protocols: temp -5°C to +25°C..."              │
│  3. "Emergency contact: 555-PORT..."                        │
│  4. "Storage duration: max 72 hours..."                     │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Format Prompt                                              │
│  System: "Answer only from context..."                      │
│  Context: [4 chunks with metadata]                          │
│  User Question: "What are the hazmat protocols at Port X?"  │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│  LLM Generation     │  (GPT-3.5-turbo)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Generated Answer:                                          │
│  "At Port X, Class 3 hazmat requires temperature-controlled │
│   storage between -5°C and +25°C, with a maximum duration   │
│   of 72 hours. Contact: 555-PORT (Source: Logistics Manual, │
│   Page 3)"                                                   │
└─────────────────────────────────────────────────────────────┘
```

**Latency Breakdown**:
- Query embedding: ~100-200ms
- Vector search: ~10-50ms
- LLM generation: ~1-3 seconds
- **Total**: ~1.5-3.5 seconds per query

---

## 6. Technology Stack

### 6.1 Core Technologies

| Layer | Technology | Version | Purpose | Alternatives Considered |
|-------|------------|---------|---------|-------------------------|
| **Language** | Python | 3.9+ | Primary language | - |
| **LLM Provider** | OpenAI | GPT-3.5/4 | Text generation | Anthropic Claude, Llama |
| **Embeddings** | OpenAI | text-embedding-3-small | Vector embeddings | Cohere, Sentence-Transformers |
| **Vector DB** | ChromaDB | 0.4.22 | Vector storage | Pinecone, Weaviate, Qdrant |
| **Orchestration** | LangChain | 0.1.0 | RAG pipeline | LlamaIndex, custom |
| **PDF Parser** | PyPDF | 3.17.4 | Document extraction | PyMuPDF, pdfplumber |

### 6.2 Technology Selection Rationale

#### ChromaDB vs. Alternatives
| Feature | ChromaDB | Pinecone | Weaviate |
|---------|----------|----------|----------|
| **Deployment** | Embedded/local | Cloud-only | Self-hosted or cloud |
| **Cost** | Free | $70+/month | Free (self-hosted) |
| **Setup Complexity** | Low | Low | Medium |
| **Scale Limit** | ~1M vectors | Billions | Billions |
| **Best For** | Prototypes, small prod | Enterprise scale | Privacy-focused |

**Decision**: ChromaDB chosen for MVP due to zero infrastructure overhead.

#### GPT-3.5-turbo vs. GPT-4
| Aspect | GPT-3.5-turbo | GPT-4 |
|--------|---------------|-------|
| **Speed** | ~2 sec/response | ~5 sec/response |
| **Cost** | $0.50/1M tokens | $10/1M tokens (20x) |
| **Accuracy** | Good for straightforward queries | Better for complex reasoning |

**Decision**: Start with GPT-3.5-turbo, upgrade to GPT-4 for high-stakes queries.

### 6.3 Development Tools

```yaml
Package Management: pip + requirements.txt
Version Control: Git
Environment Management: venv (Python virtual environments)
Code Quality: pylint, black (future)
Testing: pytest (future)
Documentation: Markdown
```

---

## 7. Deployment Architecture

### 7.1 Current (MVP) Architecture

```
┌─────────────────────────────────────┐
│        Local Development Machine    │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Python Application          │  │
│  │  (src/main.py)               │  │
│  └────────┬─────────────────────┘  │
│           │                         │
│  ┌────────▼─────────────────────┐  │
│  │  ChromaDB (./chroma_db/)     │  │
│  │  PDFs (./data/raw/)          │  │
│  └──────────────────────────────┘  │
│                                     │
│  External API Calls:                │
│  └─► OpenAI (embeddings + LLM)     │
└─────────────────────────────────────┘
```

**Characteristics**:
- Single-machine deployment
- No network dependencies (except OpenAI API)
- Suitable for: testing, small teams, <1000 documents

### 7.2 Production Architecture (Future)

```
                       Internet
                          │
                          ▼
                 ┌────────────────┐
                 │  Load Balancer │
                 └────────┬───────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │  API     │    │  API     │    │  API     │
  │  Server  │    │  Server  │    │  Server  │
  │  (FastAPI│    │  (FastAPI│    │  (FastAPI│
  └────┬─────┘    └────┬─────┘    └────┬─────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Pinecone   │ │  PostgreSQL │ │   S3/Blob   │
│  (Vectors)  │ │  (Metadata) │ │    (PDFs)   │
└─────────────┘ └─────────────┘ └─────────────┘
```

**Enhancements**:
- Horizontal scaling (multiple API servers)
- Managed vector database (Pinecone/Weaviate)
- Persistent metadata storage (PostgreSQL)
- Cloud object storage (S3/Azure Blob)
- Redis caching layer (future)

### 7.3 Deployment Options Comparison

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **Local** | No infra costs, instant setup | Single-user, no HA | Development, POC |
| **Docker** | Portable, consistent env | Requires container knowledge | Team deployments |
| **Cloud VM** | Simple, traditional | Manual scaling | Small prod (1-10 users) |
| **Kubernetes** | Auto-scaling, resilient | Complex, expensive | Enterprise (100+ users) |
| **Serverless** | Pay-per-use, auto-scale | Cold starts, limited runtime | Sporadic usage |

---

## 8. Security Architecture

### 8.1 Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| **API Key Exposure** | Unauthorized OpenAI usage ($$$) | Store in `.env`, never commit |
| **Data Exfiltration** | Proprietary docs leaked | Access controls, audit logs |
| **Prompt Injection** | Malicious query manipulation | Input sanitization, output filtering |
| **Model Hallucination** | Incorrect safety-critical info | RAG grounding, confidence scores |

### 8.2 Security Controls

```
┌─────────────────────────────────────────────┐
│           Security Layers                   │
├─────────────────────────────────────────────┤
│  1. Authentication (Future)                 │
│     • OAuth 2.0 / API keys                  │
│     • Role-based access control             │
├─────────────────────────────────────────────┤
│  2. Data Protection                         │
│     • Secrets in .env (never in git)        │
│     • PDFs in private data/ directory       │
│     • ChromaDB on encrypted filesystem      │
├─────────────────────────────────────────────┤
│  3. API Security                            │
│     • Rate limiting (OpenAI: 3000 RPM)      │
│     • Input validation (query length)       │
│     • Output sanitization                   │
├─────────────────────────────────────────────┤
│  4. Audit & Compliance                      │
│     • Query logging (who asked what)        │
│     • Source document tracking              │
│     • Version control for docs              │
└─────────────────────────────────────────────┘
```

### 8.3 Data Classification

| Data Type | Sensitivity | Storage | Encryption |
|-----------|-------------|---------|------------|
| **Source PDFs** | High (proprietary) | Local disk | FileVault/BitLocker |
| **Embeddings** | Medium (derived) | ChromaDB | At-rest encryption |
| **User Queries** | Low (logged) | SQLite (future) | Optional |
| **API Keys** | Critical | .env file | Environment-based |

---

## 9. Scalability & Performance

### 9.1 Current Limitations

| Resource | Current Limit | Bottleneck |
|----------|---------------|------------|
| **Documents** | ~1,000 PDFs | ChromaDB memory |
| **Concurrent Users** | 1 | CLI interface |
| **Query Throughput** | ~20/min | OpenAI rate limits |
| **Response Time** | 2-4 seconds | LLM generation |

### 9.2 Scaling Strategies

#### 9.2.1 Vertical Scaling (Easier)
```
Current: 8GB RAM, 2 CPU cores
↓
Upgrade: 32GB RAM, 8 CPU cores
↓
Impact: 4x document capacity, faster embeddings
Cost: $50-100/month (cloud VM)
```

#### 9.2.2 Horizontal Scaling (Production)
```
Load Balancer
    ↓
┌───────┬───────┬───────┐
│ API 1 │ API 2 │ API 3 │  (Stateless app servers)
└───┬───┴───┬───┴───┬───┘
    └───────┼───────┘
            ↓
   Pinecone (Managed Vector DB)
```

### 9.3 Performance Optimization Techniques

| Technique | Impact | Complexity | Priority |
|-----------|--------|------------|----------|
| **Caching frequent queries** | 90% latency reduction | Low | High |
| **Batch embedding generation** | 50% cost reduction | Medium | High |
| **Async API calls** | 2x throughput | Medium | Medium |
| **Hybrid search (BM25 + vector)** | 15% accuracy gain | Medium | Medium |
| **GPU acceleration** | 5x embedding speed | High | Low |

---

## 10. Future Enhancements

### 10.1 Short-Term (Next 3 Months)

#### 10.1.1 Web Interface
```
Technology: FastAPI + React
Features:
  • Multi-user support
  • Document upload UI
  • Chat history
  • Source highlighting
Effort: 2-3 weeks
```

#### 10.1.2 Hybrid Search
```
Technology: rank-bm25 + existing vector search
Features:
  • Combine keyword + semantic search
  • Reranking with Cohere API
Effort: 1 week
Impact: +15-20% retrieval accuracy
```

#### 10.1.3 Conversation Memory
```
Technology: LangChain ConversationBufferMemory
Features:
  • Multi-turn dialogue
  • Context tracking
Effort: 3-4 days
```

### 10.2 Medium-Term (6 Months)

#### 10.2.1 Multi-Modal Support
```
Features:
  • Extract tables from PDFs
  • Parse images/diagrams
  • Handle Excel spreadsheets
Technologies: pdfplumber, pytesseract, pandas
Effort: 2-3 weeks
```

#### 10.2.2 Advanced Analytics
```
Features:
  • Query analytics dashboard
  • Answer accuracy tracking
  • User satisfaction metrics
Technologies: PostgreSQL, Grafana
Effort: 2 weeks
```

#### 10.2.3 Production Database Migration
```
Migration: ChromaDB → Pinecone/Weaviate
Benefits:
  • 1000x scale (millions of docs)
  • Multi-region support
  • Better uptime guarantees
Effort: 1 week
Cost: $70-300/month
```

### 10.3 Long-Term (1 Year)

#### 10.3.1 Agentic Workflows
```
Use Cases:
  • "Compare safety protocols across 3 ports"
  • "Generate a compliance checklist"
  • "Draft a shipping manifest"
Technologies: LangChain Agents, function calling
Effort: 1-2 months
```

#### 10.3.2 Fine-Tuned Models
```
Approach: Fine-tune GPT-3.5 on logistics terminology
Benefits:
  • Better domain-specific understanding
  • Reduced token costs
  • Lower latency
Effort: 2-3 months (data collection + training)
Cost: $10k-30k (one-time)
```

#### 10.3.3 Voice Interface
```
Technologies: Whisper API (speech-to-text) + TTS
Use Case: Hands-free queries in warehouse environments
Effort: 1 month
```

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **RAG** | Retrieval-Augmented Generation: AI pattern combining search + generation |
| **Embedding** | Numerical representation of text (e.g., 1536-dimensional vector) |
| **Vector Database** | Database optimized for similarity search over embeddings |
| **Chunking** | Splitting documents into smaller pieces for processing |
| **Cosine Similarity** | Mathematical measure of how similar two vectors are |
| **Top-K Retrieval** | Returning the K most relevant documents |
| **Hallucination** | AI generating false information not present in training data |
| **Grounding** | Constraining AI responses to source documents |

---

## Appendix B: References

1. **RAG Paper**: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)
2. **LangChain Docs**: https://python.langchain.com/docs/
3. **OpenAI Embeddings Guide**: https://platform.openai.com/docs/guides/embeddings
4. **ChromaDB Documentation**: https://docs.trychroma.com/

---

## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Feb 2026 | Architecture Team | Initial architecture document |

---

**END OF ARCHITECTURE DOCUMENT**
