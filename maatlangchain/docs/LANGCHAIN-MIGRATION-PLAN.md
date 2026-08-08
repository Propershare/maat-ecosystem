# LangChain Migration Plan: Build Our Own Core

## Goal
Replace LangChain dependencies with minimal, direct libraries while keeping Maat governance as the unique value proposition.

## Current LangChain Usage

### What We're Using
1. **Document Loaders**: `PyPDFLoader`, `TextLoader`, `UnstructuredMarkdownLoader`
2. **Embeddings**: `HuggingFaceEmbeddings` wrapper
3. **Vector Stores**: `PGVector` wrapper
4. **RAG Chains**: `RetrievalQA` chain
5. **LLM**: `Ollama` wrapper

### What We Actually Need
1. **PDF Parsing**: `pypdf` or `PyPDF2` (already have)
2. **Text Processing**: Built-in Python (already have)
3. **Embeddings**: `sentence-transformers` directly (already have)
4. **Vector Store**: Direct `psycopg2` + `pgvector` (already have)
5. **RAG Logic**: Custom implementation (we build this)
6. **LLM**: Direct Ollama API (simpler)

## Migration Steps

### Step 1: Replace Document Loaders ✅ Easy
**File**: `core/chains/document_processor.py`

**Current**:
```python
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader(pdf_path)
documents = loader.load()
```

**Replace with**:
```python
import pypdf

def load_pdf(pdf_path):
    documents = []
    with open(pdf_path, 'rb') as file:
        pdf_reader = pypdf.PdfReader(file)
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            documents.append({
                'content': text,
                'metadata': {'source': pdf_path, 'page': page_num}
            })
    return documents
```

### Step 2: Replace Embedding Wrapper ✅ Easy
**File**: `core/chains/document_processor.py`, `core/integrations/tehuti_lab.py`

**Current**:
```python
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="...")
embedding = embeddings.embed_query(text)
```

**Replace with**:
```python
from sentence_transformers import SentenceTransformer

class MaatEmbeddings:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_query(self, text: str):
        return self.model.encode(text).tolist()
    
    def embed_documents(self, texts: list):
        return self.model.encode(texts).tolist()
```

### Step 3: Replace Vector Store Wrapper ⚠️ Medium
**File**: `core/integrations/tehuti_lab.py`

**Current**:
```python
from langchain_community.vectorstores import PGVector
vector_store = PGVector(connection_string=..., embedding_function=...)
vector_store.add_texts(texts, metadatas)
```

**Replace with**:
```python
import psycopg2
from pgvector.psycopg2 import register_vector

class MaatVectorStore:
    def __init__(self, connection_string, embedding_model):
        self.conn = psycopg2.connect(connection_string)
        register_vector(self.conn)
        self.embedding_model = embedding_model
    
    def add_texts(self, texts, metadatas=None):
        embeddings = self.embedding_model.embed_documents(texts)
        # Direct SQL insert with pgvector
        with self.conn.cursor() as cur:
            for text, embedding, metadata in zip(texts, embeddings, metadatas or []):
                cur.execute(
                    "INSERT INTO maat_knowledge (content, embedding, metadata) VALUES (%s, %s, %s)",
                    (text, embedding, json.dumps(metadata))
                )
        self.conn.commit()
    
    def similarity_search(self, query, k=5):
        query_embedding = self.embedding_model.embed_query(query)
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT content, metadata FROM maat_knowledge ORDER BY embedding <=> %s LIMIT %s",
                (query_embedding, k)
            )
            return cur.fetchall()
```

### Step 4: Replace RAG Chain ⚠️ Medium-Hard (But We Control It)
**File**: `core/chains/maat_rag.py`

**Current**:
```python
from langchain.chains import RetrievalQA
chain = RetrievalQA.from_llm(llm=llm, retriever=retriever)
result = chain.invoke({"query": question})
```

**Replace with**:
```python
class MaatRAG:
    def __init__(self, llm, vector_store):
        self.llm = llm
        self.vector_store = vector_store
    
    def query(self, question: str):
        # 1. Retrieve relevant documents
        docs = self.vector_store.similarity_search(question, k=5)
        
        # 2. Build context
        context = "\n\n".join([doc['content'] for doc in docs])
        
        # 3. Build prompt with Maat governance
        prompt = self._build_maat_prompt(question, context, docs)
        
        # 4. Generate response
        response = self.llm.generate(prompt)
        
        # 5. Add Maat metadata (attribution, uncertainty, etc.)
        return self._add_maat_metadata(response, docs)
    
    def _build_maat_prompt(self, question, context, docs):
        # Custom prompt with Maat principles
        sources = [doc['metadata'].get('source', 'unknown') for doc in docs]
        return f"""Answer the following question using the provided context.

Context (from {len(docs)} sources):
{context}

Question: {question}

Provide your answer with:
1. Direct answer to the question
2. Sources used (attribution)
3. Any uncertainty or limitations

Answer:"""
    
    def _add_maat_metadata(self, response, docs):
        # Add Maat governance metadata
        return {
            'answer': response,
            'sources': [doc['metadata'] for doc in docs],
            'attribution': True,
            'uncertainty_acknowledged': True,
            'classification': 'middle',  # Three-ring classification
        }
```

### Step 5: Replace LLM Wrapper ✅ Easy
**File**: `core/chains/maat_rag.py`

**Current**:
```python
from langchain_ollama import OllamaLLM
llm = OllamaLLM(model="qwen2.5:14b", base_url="http://localhost:11434")
```

**Replace with**:
```python
import requests

class MaatOllama:
    def __init__(self, model="qwen2.5:14b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str):
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"]
```

## Benefits of Migration

### 1. IP Ownership
- Own the core RAG implementation
- No external dependencies for critical paths
- Clear monetization path

### 2. Control
- No breaking changes from external libraries
- Customize for Maat needs
- Optimize for our use cases

### 3. Simplicity
- Fewer dependencies
- Easier to understand and maintain
- Less code to manage

### 4. Performance
- Direct API calls (faster)
- No wrapper overhead
- Better error handling

## Migration Timeline

### Phase 1: Document Loaders (1-2 hours)
- Replace PDF loader
- Replace text loader
- Test with sample documents

### Phase 2: Embeddings (1 hour)
- Replace embedding wrapper
- Test batch processing
- Verify performance

### Phase 3: Vector Store (2-3 hours)
- Replace PGVector wrapper
- Test insertions
- Test similarity search

### Phase 4: RAG Chain (4-6 hours)
- Build custom RAG implementation
- Add Maat governance
- Test query functionality

### Phase 5: LLM Wrapper (1 hour)
- Replace Ollama wrapper
- Test generation
- Verify responses

**Total**: ~10-15 hours of focused work

## Testing Strategy

1. **Unit Tests**: Each component individually
2. **Integration Tests**: Full RAG pipeline
3. **Performance Tests**: Compare before/after
4. **RBG Library Test**: Process sample PDFs

## Risk Mitigation

- **Keep LangChain code**: Comment out, don't delete (backup)
- **Gradual migration**: One component at a time
- **Test thoroughly**: Don't break working system
- **Rollback plan**: Can revert if needed

## Success Criteria

- ✅ No LangChain dependencies in core RAG path
- ✅ All functionality preserved
- ✅ Performance equal or better
- ✅ Maat governance intact
- ✅ Production-ready code

