# Autonomous Agents System

## Overview

Autonomous agents that execute tasks with quality validation, following Maat principles.

## Agents

### OCR Agent (`ocr_agent.py`)

Autonomous OCR processing with multi-stage quality validation.

**Features:**
- Multi-stage quality gates (confidence, readability, content, structure)
- Automatic rejection of low-quality extractions
- Human review flagging for edge cases
- Integration with Maat Memory for logging

**Usage:**
```python
from core.agents.ocr_agent import OCRAgent

agent = OCRAgent()
result = agent.process("/path/to/image.png", image_type="table")

if result["status"] == "completed":
    print("OCR processed successfully!")
elif result["status"] == "rejected":
    print(f"Rejected: {result['rejection_reason']}")
elif result["status"] == "review":
    print(f"Needs review: {result['review_reason']}")
```

### Task Executor (`task_executor.py`)

Autonomous task execution agent that reads from Maat Memory and executes tasks.

**Features:**
- Fetches pending tasks from `maat_tasks` table
- Classifies task type (OCR, document, RAG)
- Routes to appropriate agent
- Updates task status
- Logs completion

**Usage:**
```python
from core.agents.task_executor import TaskExecutor

executor = TaskExecutor()
results = executor.execute_pending_tasks(limit=10)

for result in results:
    print(f"Task {result['task_id']}: {result['status']}")
```

## Quality Validation

### Quality Validator (`quality_validator.py`)

Multi-stage quality checking system.

**Validation Stages:**
1. **OCR Confidence** - Checks confidence scores from OCR engine
2. **Readability** - Validates text is readable (not garbage)
3. **Content Quality** - Checks for meaningful content
4. **Structure** - Validates structure for tables/flowcharts

**Configurable Thresholds:**
- `ocr_confidence_min`: 0.7 (70% average)
- `ocr_confidence_min_single`: 0.5 (50% minimum)
- `readability_letter_ratio`: 0.5 (50% letters)
- `content_min_words`: 5
- `content_meaningful_words`: 3

## Workflow

### OCR Processing Workflow

```
Extract OCR → Check Confidence → Check Readability → 
Check Content → Check Structure → Process & Store
                ↓                    ↓
            Reject              Review
```

### Task Execution Workflow

```
Fetch Task → Classify → Route to Agent → Execute → Update Status → Log
```

## Integration

- **Maat Memory**: All actions logged to gitMaat
- **TehutiGuard**: Policy enforcement (via `integration.py`)
- **RAG System**: Processed content stored in vector database

## Next Steps

1. Integrate actual OCR engine (rapidocr, tesseract, Datalab Marker)
2. Add document processing agent
3. Add RAG query agent
4. Add vision model integration for flowchart understanding
5. Add human review queue system

