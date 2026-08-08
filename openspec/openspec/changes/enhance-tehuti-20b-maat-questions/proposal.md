# Change: Enhance Tehuti 20B Model with Maat-Aligned Question Asking and Recommendations

## Why

The current `tehuti-lab:gpt-oss-20b` Ollama model only includes a basic system prompt wrapper. It lacks:
1. **Proactive question-asking**: The model doesn't ask clarifying questions when uncertain, leading to assumptions and inaccurate responses
2. **Structured suggestions**: No framework for providing suggestion lists to guide users
3. **Maat-aligned recommendations**: Recommendations lack the structured, evidence-based format aligned with Maat principles (Truth, Balance, Order, Justice, Self-Reflection)
4. **Tool awareness**: System prompt doesn't fully leverage the 11 MCP servers (104 tools) available

This enhancement will make the model more interactive, helpful, and aligned with Maat principles by teaching it to ask questions with suggestions and provide structured recommendations.

## What Changes

- **MODIFIED**: Ollama Modelfile system prompt to include Maat-aligned question-asking framework
- **ADDED**: Question format with suggestion lists (checkboxes/options)
- **ADDED**: Maat-aligned recommendation framework (Truth, Balance, Order, Justice, Self-Reflection)
- **MODIFIED**: Enhanced tool awareness in system prompt (all 11 MCP servers, 104 tools)
- **MODIFIED**: Updated setup script (`scripts/setup-tehuti-ollama-model.sh`) with enhanced prompt
- **ADDED**: Suggestion prompts metadata for Open WebUI integration

## Impact

- **Affected specs**: `specs/ollama-model/spec.md` (new capability)
- **Affected code**: 
  - `scripts/setup-tehuti-ollama-model.sh` - Modelfile generation
  - `tehuti-lab-ollama-template.md` - Template format (if used)
- **User impact**: 
  - Model will ask clarifying questions proactively
  - Users receive structured suggestion lists
  - Recommendations follow Maat principles with evidence and options
  - Better tool selection awareness
- **Breaking changes**: None - this is an enhancement to existing model behavior

## Maat Principles Applied

- **Truth**: Questions ask for evidence and clarification; recommendations are evidence-based
- **Balance**: Questions explore multiple perspectives; recommendations provide options with trade-offs
- **Order**: Questions are structured systematically; recommendations are prioritized
- **Justice**: Questions ask for attribution; recommendations credit sources properly
- **Self-Reflection**: Questions learn from past; recommendations incorporate learnings

## Success Criteria

1. Model asks clarifying questions when user requests are ambiguous
2. Questions include structured suggestion lists (checkboxes/options)
3. Recommendations follow Maat framework (Truth, Balance, Order, Justice, Self-Reflection)
4. Model demonstrates awareness of all 11 MCP servers and 104 tools
5. Model queries gitMaat first before starting tasks (Maat Law)

