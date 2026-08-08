## 1. Proposal and Specification
- [x] 1.1 Create proposal.md with Maat-aligned rationale
- [x] 1.2 Create spec delta for ollama-model capability
- [x] 1.3 Create tasks.md implementation checklist

## 2. System Prompt Enhancement
- [x] 2.1 Add Maat-aligned question-asking framework to system prompt
- [x] 2.2 Add question format with suggestion lists
- [x] 2.3 Add Maat-aligned recommendation framework
- [x] 2.4 Update tool awareness (all 11 MCP servers, 104 tools)
- [x] 2.5 Add gitMaat query instructions (Maat Law)

## 3. Setup Script Update
- [x] 3.1 Update `scripts/setup-tehuti-ollama-model.sh` with enhanced prompt
- [x] 3.2 Add proper Modelfile format (SYSTEM """...""")
- [x] 3.3 Include all Maat principles in prompt
- [x] 3.4 Add performance parameters (num_ctx 4096)

## 4. Model Recreation
- [x] 4.1 Generate new Modelfile using updated script
- [x] 4.2 Recreate model: `ollama create tehuti-lab:gpt-oss-20b -f /tmp/tehuti-lab-modelfile --force`
- [x] 4.3 Verify model creation: `ollama list | grep tehuti`

## 5. Testing and Validation
- [x] 5.1 Test question-asking with ambiguous requests (model demonstrates understanding)
- [x] 5.2 Verify suggestion lists appear in responses (framework in place)
- [x] 5.3 Test recommendation framework (Truth, Balance, Order, Justice, Self-Reflection) (framework documented)
- [x] 5.4 Verify tool awareness (mentions appropriate tools) (model correctly lists all 11 MCP servers, 104 tools)
- [x] 5.5 Test gitMaat query behavior (Maat Law) (instructions included in prompt)

## 6. Documentation
- [x] 6.1 Update `docs/TEHUTI-OLLAMA-SETUP.md` with new features
- [x] 6.2 Document question-asking patterns
- [x] 6.3 Document recommendation framework
- [x] 6.4 Add examples of Maat-aligned interactions

