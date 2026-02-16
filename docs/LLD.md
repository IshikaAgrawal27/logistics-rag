# Logistics RAG System - Low-Level Design Document

## Document Information
- **Project**: Logistics RAG (Retrieval-Augmented Generation) System
- **Version**: 1.0
- **Last Updated**: February 2026
- **Author**: Engineering Team

---

## Table of Contents
1. [Document Purpose](#document-purpose)
2. [Class Diagrams](#class-diagrams)
3. [Sequence Diagrams](#sequence-diagrams)
4. [Module Specifications](#module-specifications)
5. [Data Models](#data-models)
6. [Algorithm Details](#algorithm-details)
7. [API Specifications](#api-specifications)
8. [Error Handling](#error-handling)
9. [Testing Strategy](#testing-strategy)
10. [Code Standards](#code-standards)

---

## 1. Document Purpose

This Low-Level Design (LLD) document provides detailed technical specifications for implementing the Logistics RAG system. It serves as a blueprint for developers, covering class structures, data flows, algorithms, and implementation details.

**Target Audience**: Software engineers, QA engineers, technical reviewers

**Scope**: Covers current MVP implementation with notes on future enhancements

---

## 2. Class Diagrams

### 2.1 Core Class Structure

```
┌─────────────────────────────────────────────────────────┐
│                    DocumentLoader                        │
├─────────────────────────────────────────────────────────┤
│ - text_splitter: RecursiveCharacterTextSplitter         │
│ - chunk_size: int = 1000                                │
│ - chunk_overlap: int = 200                              │
├─────────────────────────────────────────────────────────┤
│ + __init__(chunk_size, chunk_overlap)                   │
│ + load_pdf(pdf_path: str) → List[Document]             │
│ + load_directory(directory_path: str) → List[Document] │
│ - _add_metadata(pages: List[Document]) → None          │
└─────────────────────────────────────────────────────────┘
                         │
                         │ uses
                         ▼
┌─────────────────────────────────────────────────────────┐
│                VectorStoreManager                        │
├─────────────────────────────────────────────────────────┤
│ - collection_name: str                                  │
│ - persist_directory: str                                │
│ - embeddings: OpenAIEmbeddings                          │
│ - vectorstore: Optional[Chroma]                         │
├─────────────────────────────────────────────────────────┤
│ + __init__(collection_name, persist_directory)          │
│ + create_vectorstore(documents: List[Document]) → None  │
│ + load_vectorstore() → None                             │
│ + similarity_search(query: str, k: int) → List[Doc]    │
│ + similarity_search_with_score(query, k) → List[tuple] │
│ - _validate_vectorstore() → None                        │
└─────────────────────────────────────────────────────────┘
                         │
                         │ used by
                         ▼
┌─────────────────────────────────────────────────────────┐
│                      RAGChain                            │
├─────────────────────────────────────────────────────────┤
│ - vectorstore: VectorStoreManager                       │
│ - llm: ChatOpenAI                                       │
│ - prompt_template: ChatPromptTemplate                   │
│ - model_name: str                                       │
│ - temperature: float                                    │
├─────────────────────────────────────────────────────────┤
│ + __init__(vectorstore_manager, model_name, temp)       │
│ + ask(question: str, k: int, verbose: bool) → Dict     │
│ + chat() → None                                         │
│ + format_docs(docs: List[Document]) → str              │
│ - _build_prompt(context: str, question: str) → str     │
│ - _validate_response(response: str) → bool             │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Class Relationships

```
                 ┌──────────┐
                 │   main   │
                 └────┬─────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │ Document     │ │ VectorStore  │ │   RAGChain   │
 │ Loader       │ │ Manager      │ │              │
 └──────────────┘ └──────────────┘ └──────────────┘
         │                │                │
         │                │                │
         ▼                ▼                ▼
 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │  PyPDFLoader │ │   ChromaDB   │ │  ChatOpenAI  │
 │ (LangChain)  │ │              │ │  (OpenAI)    │
 └──────────────┘ └──────────────┘ └──────────────┘
```

### 2.3 Data Flow Class Diagram

```
┌─────────────┐
│   PDF File  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  DocumentLoader     │──┐
│  .load_pdf()        │  │
└──────┬──────────────┘  │
       │                 │
       │ List[Document]  │ Creates
       ▼                 │
┌─────────────────────┐  │
│  Document Objects   │◄─┘
│  (with metadata)    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ VectorStoreManager  │──┐
│ .create_vectorstore │  │
└──────┬──────────────┘  │
       │                 │
       │ embeddings      │ Stores
       ▼                 │
┌─────────────────────┐  │
│   ChromaDB          │◄─┘
│   (persisted)       │
└──────┬──────────────┘
       │
       │ query
       ▼
┌─────────────────────┐
│   RAGChain          │
│   .ask()            │
└──────┬──────────────┘
       │
       │ response
       ▼
┌─────────────┐
│   User      │
└─────────────┘
```

---

## 3. Sequence Diagrams

### 3.1 Document Ingestion Sequence

```
User          Main          DocumentLoader     PyPDFLoader      VectorStoreManager    OpenAI API    ChromaDB
 │              │                  │                 │                   │                │            │
 │ start app    │                  │                 │                   │                │            │
 │─────────────►│                  │                 │                   │                │            │
 │              │ load_directory() │                 │                   │                │            │
 │              │─────────────────►│                 │                   │                │            │
 │              │                  │ load_pdf()      │                   │                │            │
 │              │                  │────────────────►│                   │                │            │
 │              │                  │                 │ extract pages     │                │            │
 │              │                  │                 │──────────────────┐│                │            │
 │              │                  │                 │                  ││                │            │
 │              │                  │                 │◄─────────────────┘│                │            │
 │              │                  │ pages[]         │                   │                │            │
 │              │                  │◄────────────────│                   │                │            │
 │              │                  │ split_documents()                   │                │            │
 │              │                  │─────────────────────────────────────┐                │            │
 │              │                  │                 │                   │                │            │
 │              │                  │◄────────────────────────────────────┘                │            │
 │              │ chunks[]         │                 │                   │                │            │
 │              │◄─────────────────│                 │                   │                │            │
 │              │ create_vectorstore(chunks)         │                   │                │            │
 │              │────────────────────────────────────────────────────────►│                │            │
 │              │                  │                 │                   │ embed(chunk1)  │            │
 │              │                  │                 │                   │───────────────►│            │
 │              │                  │                 │                   │ vector1        │            │
 │              │                  │                 │                   │◄───────────────│            │
 │              │                  │                 │                   │ embed(chunk2)  │            │
 │              │                  │                 │                   │───────────────►│            │
 │              │                  │                 │                   │ vector2        │            │
 │              │                  │                 │                   │◄───────────────│            │
 │              │                  │                 │                   │ (repeat for all chunks)     │
 │              │                  │                 │                   │                │            │
 │              │                  │                 │                   │ store vectors  │            │
 │              │                  │                 │                   │───────────────────────────►│
 │              │                  │                 │                   │                │ persisted  │
 │              │                  │                 │                   │◄───────────────────────────│
 │              │ success          │                 │                   │                │            │
 │◄─────────────│                  │                 │                   │                │            │
```

### 3.2 Query Processing Sequence

```
User     RAGChain    VectorStoreManager    OpenAI API (Embed)    ChromaDB    OpenAI API (Chat)
 │          │                │                      │                 │              │
 │ "What is│                │                      │                 │              │
 │ hazmat  │                │                      │                 │              │
 │ protocol│                │                      │                 │              │
 │ at Port │                │                      │                 │              │
 │ X?"     │                │                      │                 │              │
 │─────────►│                │                      │                 │              │
 │          │ similarity_search()                   │                 │              │
 │          │───────────────►│                      │                 │              │
 │          │                │ embed(query)         │                 │              │
 │          │                │─────────────────────►│                 │              │
 │          │                │ query_vector         │                 │              │
 │          │                │◄─────────────────────│                 │              │
 │          │                │ search(query_vector, k=4)              │              │
 │          │                │────────────────────────────────────────►│              │
 │          │                │                      │ top 4 chunks    │              │
 │          │                │◄────────────────────────────────────────│              │
 │          │ chunks[]       │                      │                 │              │
 │          │◄───────────────│                      │                 │              │
 │          │ format_docs(chunks)                   │                 │              │
 │          │─────────────────────────────────────┐ │                 │              │
 │          │                │                    │ │                 │              │
 │          │◄────────────────────────────────────┘ │                 │              │
 │          │ build_prompt(context, question)       │                 │              │
 │          │─────────────────────────────────────┐ │                 │              │
 │          │                │                    │ │                 │              │
 │          │◄────────────────────────────────────┘ │                 │              │
 │          │ invoke_llm(prompt)                    │                 │              │
 │          │───────────────────────────────────────────────────────────────────────►│
 │          │                │                      │                 │ generate     │
 │          │                │                      │                 │ answer       │
 │          │                │                      │                 │──────────┐   │
 │          │                │                      │                 │          │   │
 │          │                │                      │                 │◄─────────┘   │
 │          │ response       │                      │                 │              │
 │          │◄───────────────────────────────────────────────────────────────────────│
 │          │ format_response(response, chunks)     │                 │              │
 │          │─────────────────────────────────────┐ │                 │              │
 │          │                │                    │ │                 │              │
 │          │◄────────────────────────────────────┘ │                 │              │
 │ result   │                │                      │                 │              │
 │◄─────────│                │                      │                 │              │
```

### 3.3 Error Handling Sequence

```
User     RAGChain    VectorStoreManager    ChromaDB
 │          │                │                 │
 │ query    │                │                 │
 │─────────►│                │                 │
 │          │ similarity_search()              │
 │          │───────────────►│                 │
 │          │                │ search()        │
 │          │                │────────────────►│
 │          │                │                 │ error: DB not initialized
 │          │                │ VectorStoreError│
 │          │                │◄────────────────│
 │          │ catch exception│                 │
 │          │◄───────────────│                 │
 │          │ log error      │                 │
 │          │──────────────┐ │                 │
 │          │              │ │                 │
 │          │◄─────────────┘ │                 │
 │          │ return error message             │
 │ error    │                │                 │
 │◄─────────│                │                 │
 │ "Vector │                │                 │
 │ store   │                │                 │
 │ not     │                │                 │
 │ loaded" │                │                 │
```

---

## 4. Module Specifications

### 4.1 DocumentLoader Module

**File**: `src/document_loader.py`

#### 4.1.1 Class: DocumentLoader

**Purpose**: Extract and chunk text from PDF documents

**Attributes**:
```python
text_splitter: RecursiveCharacterTextSplitter
    - Purpose: Split text into manageable chunks
    - Type: LangChain text splitter
    - Configuration:
        * chunk_size: 1000 characters
        * chunk_overlap: 200 characters
        * separators: ["\n\n", "\n", " ", ""]
```

**Methods**:

##### `__init__(chunk_size: int = 1000, chunk_overlap: int = 200)`
```python
"""
Initialize the document loader.

Parameters:
    chunk_size (int): Maximum characters per chunk. 
        Range: 500-2000. Default: 1000.
        Rationale: Balance between context and token efficiency
    
    chunk_overlap (int): Overlap between chunks.
        Range: 50-300. Default: 200.
        Rationale: Prevents context loss at chunk boundaries

Returns:
    None

Raises:
    ValueError: If chunk_size < chunk_overlap
"""
```

**Implementation Details**:
```python
def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
    if chunk_size < chunk_overlap:
        raise ValueError("chunk_size must be >= chunk_overlap")
    
    self.text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
```

##### `load_pdf(pdf_path: str) -> List[Document]`
```python
"""
Load and chunk a single PDF file.

Parameters:
    pdf_path (str): Absolute or relative path to PDF file
        Example: "./data/raw/manual.pdf"

Returns:
    List[Document]: List of document chunks with metadata
        Each Document contains:
            - page_content: str (chunk text)
            - metadata: dict {
                'source': str,  # filename
                'page': int,    # page number (0-indexed)
                'chunk_id': int # chunk sequence number
              }

Raises:
    FileNotFoundError: If pdf_path does not exist
    ValueError: If file is not a valid PDF
    PyPDFError: If PDF is corrupted or encrypted

Time Complexity: O(n) where n = number of pages
Space Complexity: O(m) where m = total text length
"""
```

**Algorithm**:
```python
ALGORITHM load_pdf:
    INPUT: pdf_path (string)
    OUTPUT: chunks (List[Document])
    
    1. VALIDATE file exists
       IF NOT file_exists(pdf_path):
           RAISE FileNotFoundError
    
    2. INITIALIZE PyPDFLoader with pdf_path
    
    3. EXTRACT pages
       pages ← loader.load()
       # Each page is a Document object
    
    4. ENRICH metadata
       FOR each page IN pages:
           page.metadata['source'] ← filename from pdf_path
           page.metadata['page'] ← page index
    
    5. CHUNK text
       chunks ← text_splitter.split_documents(pages)
    
    6. ADD chunk IDs
       FOR i, chunk IN enumerate(chunks):
           chunk.metadata['chunk_id'] ← i
    
    7. LOG statistics
       PRINT "Loaded {pdf_path}: {page_count} pages → {chunk_count} chunks"
    
    8. RETURN chunks
```

##### `load_directory(directory_path: str) -> List[Document]`
```python
"""
Load all PDFs from a directory.

Parameters:
    directory_path (str): Path to directory containing PDFs
        Example: "./data/raw"

Returns:
    List[Document]: Combined chunks from all PDFs

Raises:
    ValueError: If no PDF files found in directory
    FileNotFoundError: If directory does not exist

Notes:
    - Processes files in alphabetical order
    - Skips hidden files (starting with '.')
    - Aggregates all chunks into single list
"""
```

**Pseudocode**:
```
ALGORITHM load_directory:
    1. GET all .pdf files in directory
    2. IF no files found:
           RAISE ValueError("No PDFs found")
    3. INITIALIZE empty chunks list
    4. FOR each pdf_file:
           pdf_chunks ← load_pdf(pdf_file)
           chunks.extend(pdf_chunks)
    5. LOG total statistics
    6. RETURN chunks
```

---

### 4.2 VectorStoreManager Module

**File**: `src/vector_store.py`

#### 4.2.1 Class: VectorStoreManager

**Purpose**: Manage vector embeddings and similarity search

**Attributes**:
```python
collection_name: str
    - Purpose: Identifier for ChromaDB collection
    - Default: "logistics_docs"
    - Constraints: Alphanumeric + underscore only

persist_directory: str
    - Purpose: Disk location for database
    - Default: "./chroma_db"
    - Type: Relative or absolute path

embeddings: OpenAIEmbeddings
    - Purpose: Generate text embeddings
    - Model: text-embedding-3-small
    - Dimensions: 1536
    - Cost: $0.02 per 1M tokens

vectorstore: Optional[Chroma]
    - Purpose: ChromaDB instance
    - Initially: None
    - Set by: create_vectorstore() or load_vectorstore()
```

**Methods**:

##### `create_vectorstore(documents: List[Document]) -> None`
```python
"""
Create and persist a new vector store from documents.

Parameters:
    documents (List[Document]): Chunked documents with metadata

Returns:
    None

Side Effects:
    - Creates embeddings via OpenAI API (API calls)
    - Writes to disk at persist_directory
    - Sets self.vectorstore

Raises:
    OpenAIError: If API call fails (rate limit, auth error)
    IOError: If cannot write to persist_directory

Performance:
    - Time: ~0.1s per chunk (network latency)
    - Cost: $0.02 per 1M tokens (~$0.001 per 100 chunks)
    - API Rate Limit: 3,000 requests/minute

Notes:
    - Idempotent: Overwrites existing collection
    - Progress shown via print statements
"""
```

**Algorithm**:
```python
ALGORITHM create_vectorstore:
    INPUT: documents (List[Document])
    OUTPUT: None (side effect: creates DB)
    
    1. VALIDATE inputs
       IF documents is empty:
           RAISE ValueError("No documents provided")
    
    2. LOG start message
       PRINT "Creating embeddings for {len(documents)} chunks..."
    
    3. BATCH documents (groups of 100)
       batches ← split(documents, batch_size=100)
    
    4. FOR each batch:
           # API call happens here
           embedded_batch ← embeddings.embed_documents(batch)
           
           # Handle rate limits
           IF RateLimitError:
               WAIT 60 seconds
               RETRY
    
    5. CREATE ChromaDB collection
       vectorstore ← Chroma.from_documents(
           documents=documents,
           embedding=embeddings,
           collection_name=collection_name,
           persist_directory=persist_directory
       )
    
    6. PERSIST to disk
       vectorstore.persist()
    
    7. ASSIGN to instance
       self.vectorstore ← vectorstore
    
    8. LOG completion
       PRINT "Vector store created at {persist_directory}"
```

##### `similarity_search(query: str, k: int = 4) -> List[Document]`
```python
"""
Find k most similar documents to query.

Parameters:
    query (str): User's question
        Example: "What is the hazmat protocol?"
    
    k (int): Number of results to return
        Range: 1-20
        Default: 4
        Rationale: Balance between context and token cost

Returns:
    List[Document]: Top-k relevant chunks, ordered by relevance
        Length: min(k, total_docs)

Raises:
    ValueError: If vectorstore not initialized
    OpenAIError: If embedding API call fails

Algorithm:
    1. Embed query → query_vector (1536-dim)
    2. Compute cosine similarity with all stored vectors
    3. Return top-k by similarity score

Time Complexity: O(n) where n = number of stored documents
    - Embedding: O(1) (API call)
    - Search: O(n) (ChromaDB internal)

Space Complexity: O(k) for results
"""
```

**Mathematical Foundation**:
```
Cosine Similarity Formula:

similarity(A, B) = (A · B) / (||A|| * ||B||)

Where:
    A = query vector (1536 dimensions)
    B = document vector (1536 dimensions)
    A · B = dot product = Σ(A[i] * B[i])
    ||A|| = magnitude = sqrt(Σ(A[i]²))

Range: [-1, 1]
    - 1.0 = identical
    - 0.0 = orthogonal (unrelated)
    - -1.0 = opposite

In practice for text:
    - >0.8 = highly relevant
    - 0.6-0.8 = relevant
    - <0.6 = marginally relevant
```

---

### 4.3 RAGChain Module

**File**: `src/rag_chain.py`

#### 4.3.1 Class: RAGChain

**Purpose**: Orchestrate retrieval and generation pipeline

**Attributes**:
```python
vectorstore: VectorStoreManager
    - Purpose: Handle document retrieval
    - Must be initialized before use

llm: ChatOpenAI
    - Model: "gpt-3.5-turbo" (default) or "gpt-4"
    - Temperature: 0 (deterministic)
    - Max tokens: 1000 (configurable)

prompt_template: ChatPromptTemplate
    - Structure: System message + Human message
    - Enforces grounding rules
    - Includes source citation requirements
```

**Methods**:

##### `ask(question: str, k: int = 4, verbose: bool = False) -> Dict`
```python
"""
Answer a question using RAG pipeline.

Parameters:
    question (str): User's natural language query
        Example: "What is the shipping cost for 20ft containers?"
    
    k (int): Number of documents to retrieve
        Range: 1-10
        Default: 4
        Impact: More context = better accuracy but higher cost
    
    verbose (bool): Print debug information
        - Shows retrieved chunks
        - Shows prompt sent to LLM

Returns:
    Dict: {
        'answer': str,              # Generated response
        'source_documents': List[Document],  # Retrieved chunks
        'question': str,            # Original question
        'metadata': {               # Optional
            'model': str,
            'tokens_used': int,
            'latency_ms': int
        }
    }

Raises:
    ValueError: If question is empty
    OpenAIError: If LLM API call fails
    RetrievalError: If no relevant documents found

Pipeline Steps:
    1. Retrieve relevant chunks (k documents)
    2. Format chunks into prompt context
    3. Generate answer via LLM
    4. Package response with sources

Performance:
    - Latency: 1.5-3.5 seconds
    - Cost: ~$0.002 per query (GPT-3.5-turbo)
"""
```

**Detailed Algorithm**:
```python
ALGORITHM ask:
    INPUT: question (string), k (int), verbose (bool)
    OUTPUT: result (dictionary)
    
    1. VALIDATE inputs
       IF question is empty:
           RAISE ValueError("Question cannot be empty")
       
       IF k < 1 OR k > 10:
           RAISE ValueError("k must be between 1 and 10")
    
    2. RETRIEVE relevant documents
       START_TIMER
       retrieved_docs ← vectorstore.similarity_search(question, k)
       retrieval_time ← STOP_TIMER
       
       IF verbose:
           FOR each doc IN retrieved_docs:
               PRINT source, page, snippet
    
    3. FORMAT context
       context ← format_docs(retrieved_docs)
       # Example output:
       # --- Document 1 ---
       # Source: manual.pdf, Page: 3
       # [chunk text]
       # --- Document 2 ---
       # ...
    
    4. BUILD prompt
       messages ← prompt_template.format_messages(
           context=context,
           question=question
       )
       
       # Resulting structure:
       # [
       #   SystemMessage("You are a helpful assistant..."),
       #   HumanMessage("Context: ...\n\nQuestion: ...")
       # ]
    
    5. GENERATE answer
       START_TIMER
       response ← llm.invoke(messages)
       generation_time ← STOP_TIMER
       
       # Error handling
       IF response contains error:
           LOG error details
           RETURN default "Unable to process" message
    
    6. EXTRACT answer text
       answer_text ← response.content
    
    7. VALIDATE response
       IF "I don't have that information" NOT IN answer_text:
           # Verify answer uses context
           IF no overlap between answer and context:
               LOG warning("Possible hallucination")
    
    8. PACKAGE result
       result ← {
           'answer': answer_text,
           'source_documents': retrieved_docs,
           'question': question,
           'metadata': {
               'retrieval_time_ms': retrieval_time,
               'generation_time_ms': generation_time,
               'model': llm.model_name,
               'chunks_used': len(retrieved_docs)
           }
       }
    
    9. RETURN result
```

##### `format_docs(docs: List[Document]) -> str`
```python
"""
Format retrieved documents into LLM-readable context.

Parameters:
    docs (List[Document]): Retrieved document chunks

Returns:
    str: Formatted context string

Format:
    --- Document 1 ---
    Source: logistics_manual.pdf, Page: 3
    [full chunk text]
    
    --- Document 2 ---
    Source: shipping_guide.pdf, Page: 12
    [full chunk text]

Design Rationale:
    - Clear separators help LLM distinguish sources
    - Metadata (source, page) enables citation
    - Sequential numbering for reference
"""
```

**Implementation**:
```python
def format_docs(self, docs: List[Document]) -> str:
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
```

---

## 5. Data Models

### 5.1 Document Schema

```python
class Document:
    """LangChain Document object"""
    
    page_content: str
        # The actual text content
        # Type: string
        # Length: Variable (typically 500-1500 chars per chunk)
        # Encoding: UTF-8
    
    metadata: Dict[str, Any]
        # Associated metadata
        # Type: dictionary
        # Structure: {
        #     'source': str,      # Filename of PDF
        #     'page': int,        # Page number (0-indexed)
        #     'chunk_id': int,    # Sequential chunk number
        #     'doc_type': str     # Optional: 'manual', 'manifest', etc.
        # }

# Example instance:
Document(
    page_content="Class 3 hazardous materials require temperature-controlled storage...",
    metadata={
        'source': 'hazmat_guidelines.pdf',
        'page': 5,
        'chunk_id': 12,
        'doc_type': 'safety_manual'
    }
)
```

### 5.2 Vector Representation

```python
class Embedding:
    """Embedding vector (not an actual class, conceptual)"""
    
    vector: List[float]
        # Dense vector representation
        # Dimensions: 1536 (OpenAI text-embedding-3-small)
        # Range: Each element in [-1.0, 1.0]
        # Normalization: L2-normalized (||v|| = 1)
    
    metadata: Dict
        # Links back to source document
        # Includes all Document.metadata fields
    
    id: str
        # Unique identifier in ChromaDB
        # Format: UUID v4
        # Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# Conceptual example:
{
    'id': 'uuid-123',
    'vector': [0.0023, -0.0145, 0.0089, ..., 0.0034],  # 1536 floats
    'metadata': {
        'source': 'manual.pdf',
        'page': 3,
        'chunk_id': 7
    }
}
```

### 5.3 Query Response Schema

```python
class QueryResponse(TypedDict):
    """Structure of RAGChain.ask() return value"""
    
    answer: str
        # Generated answer from LLM
        # Type: string
        # Length: Variable (typically 50-500 words)
        # Includes source citations
    
    source_documents: List[Document]
        # Retrieved chunks used for answer
        # Type: list of Document objects
        # Length: k (query parameter, default 4)
        # Ordered by relevance score (highest first)
    
    question: str
        # Original user question
        # Type: string
        # Preserved for logging/audit trail
    
    metadata: Optional[Dict]
        # Query execution metadata
        # Type: dictionary (optional)
        # Structure: {
        #     'model': str,               # LLM model name
        #     'retrieval_time_ms': int,   # Time to retrieve docs
        #     'generation_time_ms': int,  # Time to generate answer
        #     'tokens_used': int,         # API tokens consumed
        #     'chunks_used': int          # Number of chunks retrieved
        # }

# Example:
{
    'answer': 'At Port X, hazmat requires storage between -5°C and +25°C...',
    'source_documents': [
        Document(page_content='...', metadata={...}),
        Document(page_content='...', metadata={...})
    ],
    'question': 'What is the hazmat protocol at Port X?',
    'metadata': {
        'model': 'gpt-3.5-turbo',
        'retrieval_time_ms': 45,
        'generation_time_ms': 2100,
        'tokens_used': 850,
        'chunks_used': 4
    }
}
```

### 5.4 Configuration Schema

```yaml
# config.yaml (future enhancement)
document_loader:
  chunk_size: 1000
  chunk_overlap: 200
  separators:
    - "\n\n"
    - "\n"
    - " "
    - ""

vector_store:
  collection_name: "logistics_docs"
  persist_directory: "./chroma_db"
  embedding_model: "text-embedding-3-small"
  embedding_dimensions: 1536

rag_chain:
  llm_model: "gpt-3.5-turbo"
  temperature: 0
  max_tokens: 1000
  top_k: 4
  
system_prompt: |
  You are a helpful assistant for logistics operations.
  Answer questions based ONLY on the provided context.
  If the answer is not in the context, say "I don't have that information."
  Always cite the source document and page number.
```

---

## 6. Algorithm Details

### 6.1 Text Chunking Algorithm

**Problem**: Split long documents into semantically coherent chunks

**Approach**: Recursive Character Text Splitter

**Pseudocode**:
```python
ALGORITHM RecursiveChunk:
    INPUT: text (string), chunk_size (int), separators (list)
    OUTPUT: chunks (list of strings)
    
    1. INITIALIZE empty chunks list
    2. INITIALIZE current_separator = separators[0]
    
    3. SPLIT text by current_separator
       segments ← text.split(current_separator)
    
    4. FOR each segment IN segments:
           IF len(segment) <= chunk_size:
               # Segment fits, add to chunks
               chunks.append(segment)
           
           ELSE IF more separators available:
               # Try next separator (recursive)
               next_separator ← next separator in list
               sub_chunks ← RecursiveChunk(
                   segment, 
                   chunk_size, 
                   separators[1:]
               )
               chunks.extend(sub_chunks)
           
           ELSE:
               # Forced split (no good separator left)
               FOR i in range(0, len(segment), chunk_size):
                   chunks.append(segment[i:i+chunk_size])
    
    5. RETURN chunks
```

**Example**:
```
Input text (300 chars):
"Chapter 3: Safety\n\nHazmat Class 3 materials require special storage.\n\nTemperature: -5°C to +25°C.\nContact: 555-SAFE"

Separators: ["\n\n", "\n", " "]
Chunk size: 100

Step 1: Split by "\n\n"
  Segment 1: "Chapter 3: Safety"  (18 chars) ✓ fits
  Segment 2: "Hazmat Class 3 materials require special storage." (51 chars) ✓ fits
  Segment 3: "Temperature: -5°C to +25°C.\nContact: 555-SAFE" (46 chars) ✓ fits

Output: 3 chunks
```

### 6.2 Embedding Generation

**Problem**: Convert text to numerical vector

**Provider**: OpenAI text-embedding-3-small

**Process**:
```
INPUT: "Hazmat storage requires temperature control"
       ↓
   [Tokenization]
       ↓
   [Neural Network Encoding]
   - Transformer architecture
   - 12 attention layers
   - Trained on web-scale text
       ↓
   [Vector Output]
       ↓
OUTPUT: [0.0023, -0.0145, 0.0089, ..., 0.0034]  (1536 floats)
```

**Properties**:
- **Dimensionality**: 1536
- **Normalization**: L2-normalized (unit vector)
- **Similarity Metric**: Cosine similarity
- **Semantic**: Similar meanings = close vectors

**Example**:
```python
text_1 = "hazardous materials storage"
text_2 = "dangerous goods warehouse"
text_3 = "apple fruit nutrition"

# After embedding:
vector_1 ≈ [0.02, 0.15, -0.08, ...]
vector_2 ≈ [0.03, 0.14, -0.07, ...]  # Similar to vector_1
vector_3 ≈ [-0.31, 0.02, 0.19, ...]  # Different from vector_1

cosine_similarity(vector_1, vector_2) ≈ 0.89  # High similarity
cosine_similarity(vector_1, vector_3) ≈ 0.12  # Low similarity
```

### 6.3 Similarity Search Algorithm

**Problem**: Find top-k most similar documents to query

**Implementation**: Approximate Nearest Neighbors (ANN)

**ChromaDB Internal Algorithm** (HNSW - Hierarchical Navigable Small World):

```python
ALGORITHM HNSW_Search:
    INPUT: query_vector, k, graph (pre-built index)
    OUTPUT: top_k documents
    
    1. START at random entry point in graph
    
    2. NAVIGATE hierarchically:
       current_layer ← top_layer
       
       WHILE current_layer >= 0:
           # Greedy search in current layer
           neighbors ← get_neighbors(current_node, current_layer)
           
           FOR each neighbor IN neighbors:
               distance ← cosine_distance(query_vector, neighbor.vector)
               
               IF distance < current_best_distance:
                   current_node ← neighbor
                   current_best_distance ← distance
           
           # Move to lower layer
           current_layer ← current_layer - 1
    
    3. REFINE in bottom layer:
       candidates ← get_k_nearest(current_node, k * 2)
       
       # Calculate exact distances
       FOR each candidate IN candidates:
           candidate.distance ← cosine_distance(
               query_vector, 
               candidate.vector
           )
       
       # Sort and trim
       candidates.sort(by=distance)
       top_k ← candidates[:k]
    
    4. FETCH documents
       results ← []
       FOR each candidate IN top_k:
           doc ← fetch_document(candidate.id)
           results.append(doc)
    
    5. RETURN results
```

**Time Complexity**:
- **Exact Search**: O(n) - compare with all vectors
- **HNSW (ChromaDB)**: O(log n) - approximate, much faster
- **Trade-off**: 99%+ accuracy at 100x speed

**Space Complexity**: O(n * d) where:
- n = number of documents
- d = embedding dimensions (1536)

### 6.4 Prompt Construction

**Goal**: Create effective context for LLM

**Template Structure**:
```
┌─────────────────────────────────────────┐
│          SYSTEM MESSAGE                 │
│  (Sets role, rules, constraints)        │
├─────────────────────────────────────────┤
│  You are a helpful assistant for        │
│  logistics operations.                  │
│                                         │
│  CRITICAL RULES:                        │
│  1. Answer ONLY from context            │
│  2. Cite sources (doc + page)           │
│  3. Say "I don't know" if not in context│
│  4. Be precise with numbers/dates       │
├─────────────────────────────────────────┤
│          CONTEXT (Retrieved)            │
│  (Top-k chunks from vector search)      │
├─────────────────────────────────────────┤
│  --- Document 1 ---                     │
│  Source: manual.pdf, Page: 3            │
│  Hazmat Class 3 materials require...    │
│                                         │
│  --- Document 2 ---                     │
│  Source: guide.pdf, Page: 12            │
│  Storage temperature must be...         │
├─────────────────────────────────────────┤
│          HUMAN MESSAGE                  │
│  (User's question)                      │
├─────────────────────────────────────────┤
│  What is the protocol for hazmat        │
│  storage at Port X?                     │
└─────────────────────────────────────────┘
```

**Token Budget Management**:
```python
ALGORITHM ManageTokens:
    max_context_tokens ← 4000  # GPT-3.5-turbo limit: 4096
    
    # Estimate tokens (rough: 1 token ≈ 4 chars)
    system_tokens ← len(system_message) / 4
    question_tokens ← len(question) / 4
    max_output_tokens ← 1000  # reserved for answer
    
    available_for_context ← (
        max_context_tokens 
        - system_tokens 
        - question_tokens 
        - max_output_tokens
    )
    
    # Truncate context if needed
    IF context_tokens > available_for_context:
        # Option 1: Reduce k (fewer chunks)
        # Option 2: Truncate each chunk
        # Option 3: Use gpt-4-turbo (16k context)
```

---

## 7. API Specifications

### 7.1 Internal APIs

#### 7.1.1 DocumentLoader API

```python
# Method: load_pdf
# HTTP: N/A (internal)
# Purpose: Load single PDF

Request:
    pdf_path: str = "./data/raw/manual.pdf"
    
Response:
    List[Document]
    
    Example:
    [
        Document(
            page_content="Chapter 1: Introduction...",
            metadata={'source': 'manual.pdf', 'page': 0, 'chunk_id': 0}
        ),
        Document(
            page_content="Safety protocols require...",
            metadata={'source': 'manual.pdf', 'page': 1, 'chunk_id': 1}
        )
    ]

Errors:
    FileNotFoundError: PDF not found
    PyPDFError: Invalid or corrupted PDF
```

#### 7.1.2 VectorStoreManager API

```python
# Method: similarity_search
# HTTP: N/A (internal)
# Purpose: Retrieve relevant documents

Request:
    query: str = "What is the hazmat protocol?"
    k: int = 4  # optional, default: 4
    
Response:
    List[Document]  # ordered by relevance
    
    Example:
    [
        Document(
            page_content="Hazmat Class 3 requires...",
            metadata={'source': 'manual.pdf', 'page': 3}
        ),
        # ... 3 more documents
    ]

Errors:
    ValueError: vectorstore not initialized
    OpenAIError: Embedding API failure
```

#### 7.1.3 RAGChain API

```python
# Method: ask
# HTTP: N/A (internal, but basis for future REST API)
# Purpose: Answer question using RAG

Request:
    question: str = "What is the cost for 20ft container?"
    k: int = 4  # optional
    verbose: bool = False  # optional
    
Response:
    Dict = {
        'answer': str,
        'source_documents': List[Document],
        'question': str,
        'metadata': Dict  # optional
    }
    
    Example:
    {
        'answer': 'The cost for a 20ft container is $1,200 base + $50/ton (Source: manual.pdf, Page 5).',
        'source_documents': [<Document>, <Document>],
        'question': 'What is the cost for 20ft container?',
        'metadata': {
            'model': 'gpt-3.5-turbo',
            'tokens_used': 450
        }
    }

Errors:
    ValueError: Empty question
    OpenAIError: LLM API failure
    RetrievalError: No relevant documents
```

### 7.2 Future REST API Design

```yaml
# Future web API endpoints

POST /api/v1/documents/upload
  Description: Upload and index a new PDF
  Request:
    - file: multipart/form-data
    - metadata: JSON (optional)
  Response: {
    'document_id': str,
    'chunks_created': int,
    'status': 'indexed'
  }

GET /api/v1/documents
  Description: List all indexed documents
  Response: {
    'documents': [
      {'id': str, 'name': str, 'chunks': int, 'uploaded_at': datetime}
    ]
  }

POST /api/v1/query
  Description: Ask a question
  Request: {
    'question': str,
    'k': int (optional),
    'model': str (optional)
  }
  Response: {
    'answer': str,
    'sources': [
      {'document': str, 'page': int, 'relevance': float}
    ]
  }

DELETE /api/v1/documents/{document_id}
  Description: Remove a document from index
  Response: {
    'status': 'deleted',
    'chunks_removed': int
  }
```

---

## 8. Error Handling

### 8.1 Error Taxonomy

```
Application Errors
├── Input Errors
│   ├── FileNotFoundError (PDF missing)
│   ├── ValueError (invalid parameters)
│   └── ValidationError (malformed query)
│
├── Processing Errors
│   ├── PyPDFError (corrupted PDF)
│   ├── ChunkingError (text splitting failure)
│   └── EncodingError (non-UTF8 text)
│
├── External Service Errors
│   ├── OpenAIError
│   │   ├── AuthenticationError (invalid API key)
│   │   ├── RateLimitError (quota exceeded)
│   │   └── ServiceUnavailableError (API down)
│   │
│   └── ChromaDBError
│       ├── ConnectionError (DB unreachable)
│       └── PersistenceError (disk write failure)
│
└── Business Logic Errors
    ├── NoRelevantDocumentsError
    ├── AnswerNotFoundError
    └── HallucinationDetectedError
```

### 8.2 Error Handling Strategy

#### 8.2.1 DocumentLoader Errors

```python
def load_pdf(self, pdf_path: str) -> List[Document]:
    try:
        # Validate file existence
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Validate file type
        if not pdf_path.endswith('.pdf'):
            raise ValueError(f"Not a PDF file: {pdf_path}")
        
        # Attempt to load
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        
        # Validate content
        if not pages:
            raise ValueError(f"PDF contains no readable pages: {pdf_path}")
        
        # Process chunks
        chunks = self.text_splitter.split_documents(pages)
        return chunks
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise  # Re-raise to caller
    
    except PyPDFError as e:
        logger.error(f"PDF parsing error: {e}")
        # Attempt OCR as fallback
        try:
            return self._ocr_fallback(pdf_path)
        except Exception as ocr_error:
            logger.error(f"OCR fallback failed: {ocr_error}")
            raise RuntimeError(f"Could not extract text from {pdf_path}")
    
    except Exception as e:
        logger.error(f"Unexpected error in load_pdf: {e}")
        raise RuntimeError(f"Failed to load {pdf_path}: {str(e)}")
```

#### 8.2.2 VectorStoreManager Errors

```python
def similarity_search(self, query: str, k: int = 4) -> List[Document]:
    try:
        # Validate state
        if not self.vectorstore:
            raise ValueError(
                "Vector store not initialized. "
                "Call create_vectorstore() or load_vectorstore() first."
            )
        
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if k < 1 or k > 20:
            raise ValueError("k must be between 1 and 20")
        
        # Perform search
        results = self.vectorstore.similarity_search(query, k=k)
        return results
        
    except openai.error.AuthenticationError:
        logger.error("OpenAI API key invalid")
        raise RuntimeError(
            "Authentication failed. Check OPENAI_API_KEY in .env file."
        )
    
    except openai.error.RateLimitError:
        logger.warning("OpenAI rate limit hit, retrying after delay")
        time.sleep(60)  # Wait 1 minute
        return self.similarity_search(query, k)  # Retry once
    
    except openai.error.ServiceUnavailableError:
        logger.error("OpenAI API unavailable")
        raise RuntimeError(
            "OpenAI service is currently unavailable. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in similarity_search: {e}")
        raise RuntimeError(f"Search failed: {str(e)}")
```

#### 8.2.3 RAGChain Errors

```python
def ask(self, question: str, k: int = 4, verbose: bool = False) -> Dict:
    try:
        # Retrieve
        retrieved_docs = self.vectorstore.similarity_search(question, k)
        
        # Check if any relevant docs found
        if not retrieved_docs:
            return {
                'answer': "I don't have any relevant documents to answer this question.",
                'source_documents': [],
                'question': question
            }
        
        # Format and generate
        context = self.format_docs(retrieved_docs)
        messages = self.prompt_template.format_messages(
            context=context,
            question=question
        )
        
        response = self.llm.invoke(messages)
        
        # Validate response
        if not response or not response.content:
            raise RuntimeError("LLM returned empty response")
        
        return {
            'answer': response.content,
            'source_documents': retrieved_docs,
            'question': question
        }
        
    except ValueError as e:
        # Propagate validation errors
        logger.error(f"Validation error: {e}")
        raise
    
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return {
            'answer': f"I apologize, but I encountered an error: {str(e)}",
            'source_documents': [],
            'question': question
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in ask: {e}")
        return {
            'answer': "I apologize, but I encountered an unexpected error processing your question.",
            'source_documents': [],
            'question': question
        }
```

### 8.3 User-Facing Error Messages

| Internal Error | User-Facing Message |
|----------------|---------------------|
| `FileNotFoundError` | "The document '{filename}' could not be found. Please check the file path." |
| `OpenAI AuthenticationError` | "API authentication failed. Please contact support." |
| `OpenAI RateLimitError` | "We're experiencing high demand. Retrying your request..." |
| `No relevant documents` | "I don't have information about that in the available documents." |
| `LLM timeout` | "The request took too long. Please try a simpler question." |
| `Empty response` | "I apologize, but I couldn't generate a proper answer. Please rephrase your question." |

---

## 9. Testing Strategy

### 9.1 Unit Tests

#### 9.1.1 DocumentLoader Tests

```python
# tests/test_document_loader.py

import pytest
from src.document_loader import DocumentLoader

class TestDocumentLoader:
    
    def test_init_default_params(self):
        """Test initialization with default parameters"""
        loader = DocumentLoader()
        assert loader.text_splitter is not None
        assert loader.text_splitter._chunk_size == 1000
        assert loader.text_splitter._chunk_overlap == 200
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters"""
        loader = DocumentLoader(chunk_size=500, chunk_overlap=100)
        assert loader.text_splitter._chunk_size == 500
        assert loader.text_splitter._chunk_overlap == 100
    
    def test_init_invalid_params(self):
        """Test initialization with invalid parameters"""
        with pytest.raises(ValueError):
            DocumentLoader(chunk_size=100, chunk_overlap=200)
    
    def test_load_pdf_success(self, tmp_path):
        """Test successful PDF loading"""
        # Create a test PDF
        pdf_path = tmp_path / "test.pdf"
        # ... create PDF using reportlab ...
        
        loader = DocumentLoader()
        chunks = loader.load_pdf(str(pdf_path))
        
        assert len(chunks) > 0
        assert all(hasattr(chunk, 'page_content') for chunk in chunks)
        assert all(hasattr(chunk, 'metadata') for chunk in chunks)
    
    def test_load_pdf_file_not_found(self):
        """Test loading non-existent PDF"""
        loader = DocumentLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load_pdf("nonexistent.pdf")
    
    def test_load_pdf_invalid_file(self, tmp_path):
        """Test loading non-PDF file"""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("This is not a PDF")
        
        loader = DocumentLoader()
        
        with pytest.raises(ValueError):
            loader.load_pdf(str(txt_path))
    
    def test_load_directory_success(self, tmp_path):
        """Test loading directory with multiple PDFs"""
        # Create test PDFs
        # ...
        
        loader = DocumentLoader()
        chunks = loader.load_directory(str(tmp_path))
        
        assert len(chunks) > 0
    
    def test_load_directory_no_pdfs(self, tmp_path):
        """Test loading empty directory"""
        loader = DocumentLoader()
        
        with pytest.raises(ValueError, match="No PDF files found"):
            loader.load_directory(str(tmp_path))
```

#### 9.1.2 VectorStoreManager Tests

```python
# tests/test_vector_store.py

import pytest
from src.vector_store import VectorStoreManager
from langchain.schema import Document

class TestVectorStoreManager:
    
    def test_init(self):
        """Test initialization"""
        vs = VectorStoreManager()
        assert vs.collection_name == "logistics_docs"
        assert vs.vectorstore is None
    
    def test_create_vectorstore(self, sample_documents):
        """Test vector store creation"""
        vs = VectorStoreManager(persist_directory="./test_chroma_db")
        vs.create_vectorstore(sample_documents)
        
        assert vs.vectorstore is not None
    
    def test_similarity_search_before_init(self):
        """Test search before initialization"""
        vs = VectorStoreManager()
        
        with pytest.raises(ValueError, match="not initialized"):
            vs.similarity_search("test query")
    
    def test_similarity_search_success(self, initialized_vectorstore):
        """Test successful similarity search"""
        results = initialized_vectorstore.similarity_search(
            "hazmat protocol",
            k=2
        )
        
        assert len(results) == 2
        assert all(isinstance(r, Document) for r in results)
    
    def test_similarity_search_with_score(self, initialized_vectorstore):
        """Test search with relevance scores"""
        results = initialized_vectorstore.similarity_search_with_score(
            "shipping cost",
            k=3
        )
        
        assert len(results) == 3
        assert all(isinstance(r, tuple) for r in results)
        assert all(isinstance(r[1], float) for r in results)

# Fixtures
@pytest.fixture
def sample_documents():
    return [
        Document(
            page_content="Hazmat requires special handling",
            metadata={'source': 'manual.pdf', 'page': 1}
        ),
        Document(
            page_content="Shipping costs are $1200 per container",
            metadata={'source': 'manual.pdf', 'page': 2}
        )
    ]
```

### 9.2 Integration Tests

```python
# tests/test_integration.py

import pytest
from src.main import setup_vectorstore
from src.rag_chain import RAGChain

class TestEndToEndFlow:
    
    def test_full_rag_pipeline(self, test_pdf_path):
        """Test complete RAG pipeline from PDF to answer"""
        # 1. Load documents
        vs_manager = setup_vectorstore(force_rebuild=True)
        
        # 2. Create RAG chain
        rag = RAGChain(vs_manager)
        
        # 3. Ask question
        result = rag.ask("What is the hazmat protocol?")
        
        # 4. Validate response
        assert 'answer' in result
        assert len(result['source_documents']) > 0
        assert result['question'] == "What is the hazmat protocol?"
        assert result['answer'] != "I don't have that information"
    
    def test_question_not_in_documents(self, initialized_system):
        """Test handling of out-of-scope questions"""
        rag = initialized_system
        
        result = rag.ask("What is the weather forecast?")
        
        assert "don't have" in result['answer'].lower()
```

### 9.3 Performance Tests

```python
# tests/test_performance.py

import pytest
import time

class TestPerformance:
    
    def test_query_latency(self, initialized_system):
        """Test query response time"""
        rag = initialized_system
        
        start = time.time()
        result = rag.ask("What is the shipping cost?")
        latency = time.time() - start
        
        # Should respond in < 5 seconds
        assert latency < 5.0
    
    def test_batch_processing(self, initialized_system):
        """Test processing multiple queries"""
        rag = initialized_system
        questions = [
            "What is the hazmat protocol?",
            "What are the shipping costs?",
            "What is the emergency contact?"
        ]
        
        start = time.time()
        results = [rag.ask(q) for q in questions]
        total_time = time.time() - start
        
        # Should process 3 queries in < 15 seconds
        assert total_time < 15.0
        assert len(results) == 3
```

### 9.4 Test Coverage Goals

| Module | Target Coverage | Priority |
|--------|----------------|----------|
| `document_loader.py` | 90% | High |
| `vector_store.py` | 85% | High |
| `rag_chain.py` | 80% | High |
| `main.py` | 70% | Medium |
| Error handling | 100% | High |

---

## 10. Code Standards

### 10.1 Naming Conventions

```python
# Class names: PascalCase
class DocumentLoader:
    pass

class VectorStoreManager:
    pass

# Function/method names: snake_case
def load_pdf(pdf_path: str):
    pass

def similarity_search(query: str, k: int):
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_CHUNK_SIZE = 1000
MAX_RETRIES = 3
API_TIMEOUT = 30

# Private methods: _leading_underscore
def _validate_input(data):
    pass

def _format_response(raw_data):
    pass

# Variables: snake_case
chunk_size = 1000
retrieved_docs = []
```

### 10.2 Type Hints

```python
# All public functions must have type hints
def load_pdf(pdf_path: str) -> List[Document]:
    pass

def similarity_search(
    query: str, 
    k: int = 4
) -> List[Document]:
    pass

# Use typing module for complex types
from typing import List, Dict, Optional, Union

def ask(
    question: str,
    k: int = 4,
    verbose: bool = False
) -> Dict[str, Union[str, List[Document]]]:
    pass
```

### 10.3 Docstring Format

```python
def load_pdf(pdf_path: str) -> List[Document]:
    """
    Load and chunk a PDF document.
    
    This function reads a PDF file, extracts text from each page,
    and splits the content into overlapping chunks suitable for
    embedding and retrieval.
    
    Args:
        pdf_path: Absolute or relative path to the PDF file.
            Example: "./data/raw/logistics_manual.pdf"
    
    Returns:
        List of Document objects, each containing:
            - page_content: Text chunk
            - metadata: Dict with 'source', 'page', 'chunk_id'
    
    Raises:
        FileNotFoundError: If pdf_path does not exist
        ValueError: If file is not a valid PDF
        PyPDFError: If PDF is corrupted or encrypted
    
    Examples:
        >>> loader = DocumentLoader()
        >>> chunks = loader.load_pdf("./data/manual.pdf")
        >>> print(f"Loaded {len(chunks)} chunks")
        Loaded 45 chunks
    
    Notes:
        - Chunks may overlap by chunk_overlap characters
        - Metadata includes 0-indexed page numbers
        - Empty pages are skipped
    """
    pass
```

### 10.4 Logging Standards

```python
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Log levels:
# DEBUG: Detailed info for debugging
logger.debug(f"Retrieved {len(docs)} documents for query: {query}")

# INFO: General informational messages
logger.info(f"Vector store created with {len(documents)} chunks")

# WARNING: Unexpected but handled situations
logger.warning(f"Rate limit hit, retrying after 60s")

# ERROR: Errors that are caught and handled
logger.error(f"Failed to load PDF: {pdf_path}", exc_info=True)

# CRITICAL: Severe errors causing system failure
logger.critical("OpenAI API key not configured")
```

### 10.5 Code Organization

```python
# File structure within a module:

# 1. Module docstring
"""
Vector Store Manager

This module handles vector embeddings and similarity search
for the RAG pipeline.
"""

# 2. Imports (grouped)
# Standard library
import os
from pathlib import Path
from typing import List, Optional

# Third-party
import chromadb
from langchain_openai import OpenAIEmbeddings

# Local
from .utils import validate_path

# 3. Constants
DEFAULT_COLLECTION = "logistics_docs"
MAX_BATCH_SIZE = 100

# 4. Classes
class VectorStoreManager:
    """Main class docstring"""
    
    def __init__(self):
        """Constructor"""
        pass
    
    def public_method(self):
        """Public method"""
        pass
    
    def _private_method(self):
        """Private method"""
        pass

# 5. Module-level functions (if any)
def helper_function():
    """Helper function"""
    pass

# 6. Main block (for testing)
if __name__ == "__main__":
    # Quick test code
    pass
```

### 10.6 Error Messages

```python
# Good error messages: specific, actionable

# BAD:
raise ValueError("Invalid input")

# GOOD:
raise ValueError(
    f"chunk_size ({chunk_size}) must be greater than "
    f"chunk_overlap ({chunk_overlap})"
)

# BAD:
raise RuntimeError("API error")

# GOOD:
raise RuntimeError(
    f"OpenAI API request failed: {error.message}. "
    f"Check your API key in the .env file."
)
```

---

## Appendix A: Database Schema (ChromaDB)

### Collection Structure
```json
{
  "collection_name": "logistics_docs",
  "embedding_dimension": 1536,
  "documents": [
    {
      "id": "uuid-1",
      "embedding": [0.02, -0.15, ...],  // 1536 floats
      "metadata": {
        "source": "logistics_manual.pdf",
        "page": 3,
        "chunk_id": 7,
        "doc_type": "manual"
      },
      "document": "Hazmat Class 3 materials require..."
    }
  ],
  "index_type": "HNSW",
  "distance_function": "cosine"
}
```

---

## Appendix B: Configuration Files

### requirements.txt
```
langchain==0.1.0
langchain-community==0.0.13
langchain-openai==0.0.2
chromadb==0.4.22
pypdf==3.17.4
python-dotenv==1.0.0
tiktoken==0.5.2
openai==1.7.2

# Development dependencies
pytest==7.4.3
pytest-cov==4.1.0
black==23.12.1
pylint==3.0.3
```

### .env.template
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_key_here

# Vector Store Configuration
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=logistics_docs

# Model Configuration
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0
MAX_TOKENS=1000

# Retrieval Configuration
DEFAULT_K=4
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Feb 2026 | Engineering Team | Initial LLD document |

---

**END OF LOW-LEVEL DESIGN DOCUMENT**
