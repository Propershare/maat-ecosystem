# LLM/Embedding Speed Optimization Implementation

## Problem
Processing 1303-page PDFs creates 5816 chunks, and embedding generation is the bottleneck (processing chunks one-by-one).

## Solution: Batch Processing

### 1. Batch Embedding Generation

**Current (SLOW)**:
```python
processed_chunks = []
if self.embeddings:
    for i, chunk in enumerate(chunks):
        try:
            embedding = self.embeddings.embed_query(chunk.page_content)
            processed_chunks.append({
                "content": chunk.page_content,
                "embedding": embedding,
                "metadata": chunk.metadata,
                "chunk_index": i,
            })
        except Exception as e:
            log.warning(f"Failed to generate embedding for chunk {i}: {e}")
```

**Optimized (FAST)**:
```python
processed_chunks = []
if self.embeddings:
    # Batch process all embeddings at once
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    
    try:
        # Use embed_documents for batch processing (10-50x faster)
        embeddings = self.embeddings.embed_documents(texts)
        
        # Create processed chunks with embeddings
        for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
            processed_chunks.append({
                "content": text,
                "embedding": embedding,
                "metadata": metadata,
                "chunk_index": i,
            })
        log.info(f"Generated {len(embeddings)} embeddings in batch")
    except Exception as e:
        log.error(f"Batch embedding generation failed: {e}")
        # Fallback to individual processing
        for i, chunk in enumerate(chunks):
            try:
                embedding = self.embeddings.embed_query(chunk.page_content)
                processed_chunks.append({
                    "content": chunk.page_content,
                    "embedding": embedding,
                    "metadata": chunk.metadata,
                    "chunk_index": i,
                })
            except Exception as e2:
                log.warning(f"Failed to generate embedding for chunk {i}: {e2}")
```

### 2. Batch Vector Store Insertion

**Current (SLOW)**:
```python
# In store_document or similar method
for chunk in processed_chunks:
    vector_store.add_texts([chunk["content"]], metadatas=[chunk["metadata"]])
```

**Optimized (FAST)**:
```python
# Batch insert all chunks at once
if processed_chunks:
    texts = [chunk["content"] for chunk in processed_chunks]
    metadatas = [chunk["metadata"] for chunk in processed_chunks]
    
    # Insert in batches of 500 to avoid memory issues
    batch_size = 500
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_metadatas = metadatas[i:i+batch_size]
        vector_store.add_texts(batch_texts, metadatas=batch_metadatas)
        log.info(f"Inserted batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
```

### 3. Optimize Chunk Size for Large PDFs

**Current**:
```python
chunk_size=1000
chunk_overlap=200
```

**Optimized** (for large PDFs):
```python
# Adaptive chunk size based on document size
if total_pages > 500:
    chunk_size = 2500
    chunk_overlap = 400
elif total_pages > 100:
    chunk_size = 2000
    chunk_overlap = 300
else:
    chunk_size = 1000
    chunk_overlap = 200
```

### 4. Add Progress Tracking

```python
from tqdm import tqdm

# In processing loop
chunks_with_progress = tqdm(chunks, desc="Processing chunks", unit="chunk")
for chunk in chunks_with_progress:
    # process chunk
```

### 5. GPU Optimization for Embeddings

```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cuda'},  # Use GPU
    encode_kwargs={'batch_size': 32, 'normalize_embeddings': True}  # Batch processing
)
```

## Files to Modify

1. **`core/chains/document_processor.py`**
   - `process_rbg_pdf()` method: Replace embedding loop with batch processing
   - Add adaptive chunk sizing
   - Add progress bars

2. **`core/chains/maat_rag.py`**
   - `store_document()` method: Replace individual inserts with batch inserts

3. **`core/integrations/tehuti_lab.py`**
   - `get_vector_store()`: Add GPU optimization to embeddings

## Expected Performance

- **Before**: ~2-5 minutes per PDF (1303 pages)
- **After**: ~10-30 seconds per PDF
- **Speedup**: 10-30x faster

## Implementation Steps

1. Update `document_processor.py` to use `embed_documents()` instead of `embed_query()` in loop
2. Update `maat_rag.py` to batch insert chunks
3. Add adaptive chunk sizing
4. Add progress bars with `tqdm`
5. Test with `--limit 1` to verify speedup

## Testing

```bash
cd /home/suspect/.n8n/maatlangchain
time python3 scripts/process_rbg_library.py --limit 1
```

Compare before/after times.

