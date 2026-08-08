# Autonomous Agents System with Quality Validation

## 🎯 Overview

Built an autonomous agent system with LangGraph that executes tasks with multi-stage quality validation. This prevents garbage content from entering the RAG system.

## ✅ What Was Built

### 1. Quality Validation System (`core/chains/quality_validator.py`)

**Multi-stage validation:**
- **OCR Confidence Check** - Validates confidence scores (70% average, 50% minimum)
- **Readability Check** - Filters garbage patterns (only symbols, too short, etc.)
- **Content Quality Check** - Ensures meaningful content (min 5 words, 3 meaningful)
- **Structure Check** - Validates structure for tables/flowcharts

**Configurable thresholds:**
```python
{
    "ocr_confidence_min": 0.7,
    "ocr_confidence_min_single": 0.5,
    "readability_letter_ratio": 0.5,
    "content_min_words": 5,
    "content_meaningful_words": 3
}
```

### 2. OCR Agent (`core/agents/ocr_agent.py`)

**LangGraph workflow with quality gates:**
```
Extract OCR → Check Confidence → Check Readability → 
Check Content → Check Structure → Process & Store
                ↓                    ↓
            Reject              Review
```

**Features:**
- Autonomous OCR processing
- Multi-stage quality validation
- Automatic rejection of garbage
- Human review flagging
- Maat Memory logging

### 3. Task Executor (`core/agents/task_executor.py`)

**Autonomous task execution:**
- Reads tasks from `maat_tasks` table
- Classifies task type (OCR, document, RAG)
- Routes to appropriate agent
- Updates task status
- Logs completion

### 4. Integration (`core/agents/integration.py`)

**TehutiGuard integration:**
- Policy enforcement for quality
- Content validation
- Policy violation detection

## 🔧 Usage

### OCR Agent

```python
from core.agents.ocr_agent import OCRAgent

agent = OCRAgent()
result = agent.process("/path/to/image.png", image_type="table")

if result["status"] == "completed":
    print("✅ OCR processed successfully!")
elif result["status"] == "rejected":
    print(f"❌ Rejected: {result['rejection_reason']}")
elif result["status"] == "review":
    print(f"⚠️ Needs review: {result['review_reason']}")
```

### Task Executor

```python
from core.agents.task_executor import TaskExecutor

executor = TaskExecutor()
results = executor.execute_pending_tasks(limit=10)

for result in results:
    print(f"Task {result['task_id']}: {result['status']}")
```

### Quality Validator

```python
from core.chains.quality_validator import QualityValidator

validator = QualityValidator()

# Validate OCR result
ocr_result = {
    "avg_confidence": 0.85,
    "min_confidence": 0.65,
    "confidence_scores": [0.85, 0.90, 0.80, 0.65, 0.88]
}
result = validator.validate_ocr_confidence(ocr_result)

# Validate text
text = "This is high-quality extracted text."
result = validator.validate_readability(text)
result = validator.validate_content_quality(text)
```

## 🏛️ Maat Principles Applied

- **Truth**: Quality validation ensures only accurate content
- **Balance**: Configurable thresholds for different use cases
- **Order**: Structured workflow with clear quality gates
- **Justice**: Consistent validation for all content
- **Self-Reflection**: Rejections logged to learn from failures

## 📋 Next Steps

1. **Integrate actual OCR engine**
   - Add rapidocr, tesseract, or Datalab Marker integration
   - Replace simulated OCR in `_extract_ocr` method

2. **Add vision model integration**
   - For flowchart understanding
   - For graph/chart data extraction

3. **Add document processing agent**
   - PDF processing
   - Multi-format support

4. **Add RAG query agent**
   - Autonomous RAG queries
   - Query optimization

5. **Human review queue**
   - WebUI for reviewing flagged content
   - Approval/rejection workflow

## 🧪 Testing

Run the test script:
```bash
cd /home/suspect/.n8n/maatlangchain
python3 core/agents/test_ocr_agent.py
```

## 📦 Dependencies Added

- `langgraph>=0.2.0` - Agent workflow framework
- `langgraph-checkpoint>=0.2.0` - State persistence

## 🎉 Result

**Autonomous agents that:**
- ✅ Execute tasks automatically
- ✅ Validate quality at multiple stages
- ✅ Reject garbage content
- ✅ Flag edge cases for review
- ✅ Log everything to Maat Memory
- ✅ Follow Maat principles

**No more garbage extraction!** 🚀

