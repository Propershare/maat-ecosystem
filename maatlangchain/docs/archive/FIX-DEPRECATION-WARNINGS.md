# Fix LangChain Deprecation Warnings

Based on the terminal output, here are the deprecation warnings and how to fix them:

## 1. Document Loaders (document_processor.py)

**Current (deprecated)**:
```python
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
```

**Fixed**:
```python
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
```

## 2. Embeddings (document_processor.py and tehuti_lab.py)

**Current (deprecated)**:
```python
from langchain.embeddings import HuggingFaceEmbeddings
```

**Fixed (preferred)**:
```python
from langchain_huggingface import HuggingFaceEmbeddings
```

**Or (alternative)**:
```python
from langchain_community.embeddings import HuggingFaceEmbeddings
```

## 3. Ollama LLM (maat_rag.py)

**Current (deprecated)**:
```python
from langchain_community.llms import Ollama
return Ollama(model=model_name, base_url="http://localhost:11434")
```

**Fixed**:
```python
from langchain_ollama import OllamaLLM
return OllamaLLM(model=model_name, base_url="http://localhost:11434")
```

## Installation

```bash
pip install langchain-ollama langchain-huggingface
```

## Files to Update

1. `core/chains/document_processor.py` - Lines 18-25
2. `core/integrations/tehuti_lab.py` - Line 149
3. `core/chains/maat_rag.py` - Line 196

## Quick Fix Script

Run this to automatically update imports:

```bash
cd /home/suspect/.n8n/maatlangchain

# Fix document_processor.py
sed -i 's/from langchain\.document_loaders import/from langchain_community.document_loaders import/g' core/chains/document_processor.py
sed -i 's/from langchain\.embeddings import HuggingFaceEmbeddings/from langchain_huggingface import HuggingFaceEmbeddings/g' core/chains/document_processor.py

# Fix tehuti_lab.py  
sed -i 's/from langchain\.embeddings import HuggingFaceEmbeddings/from langchain_huggingface import HuggingFaceEmbeddings/g' core/integrations/tehuti_lab.py
sed -i 's/from langchain_community\.embeddings import HuggingFaceEmbeddings/from langchain_huggingface import HuggingFaceEmbeddings/g' core/integrations/tehuti_lab.py

# Fix maat_rag.py
sed -i 's/from langchain_community\.llms import Ollama/from langchain_ollama import OllamaLLM/g' core/chains/maat_rag.py
sed -i 's/Ollama(/OllamaLLM(/g' core/chains/maat_rag.py
```

