# Tehuti Audio - Bark TTS API

**Maat-Aligned Tool Documentation**

## Overview

Text-to-speech, multilingual, and creative audio generation using Bark

**Version**: 1.0.0  
**Total Tools**: 7

## Maat Principles Alignment

### Truth (Maat)
Bark TTS - text-to-speech, multilingual, music generation

### Balance (Maat)
Balance quality with generation speed

### Order (Maat)
Structured audio generation

### Justice (Maat)
Proper audio attribution

### Self-Reflection (Maat)
Learn from audio patterns

## Available Tools

### Health Check

**Operation ID**: `health_check_health_get`  
**Path**: `GET /health`

Health check endpoint.

### Get Openapi Spec

**Operation ID**: `get_openapi_spec_openapi_json_get`  
**Path**: `GET /openapi.json`

Return OpenAPI specification.

### Generate Speech

**Operation ID**: `generate_speech_api_generate_speech_post`  
**Path**: `POST /api/generate_speech`

Generate speech from text using Bark TTS.

**Request Body**: See OpenAPI spec for schema details

### Generate Speech With Voice

**Operation ID**: `generate_speech_with_voice_api_generate_speech_with_voice_post`  
**Path**: `POST /api/generate_speech_with_voice`

Generate speech with specific voice preset and emotion tags.

**Request Body**: See OpenAPI spec for schema details

### Generate Multilingual

**Operation ID**: `generate_multilingual_api_generate_multilingual_post`  
**Path**: `POST /api/generate_multilingual`

Generate speech in multiple languages (auto-detects language from text).

**Request Body**: See OpenAPI spec for schema details

### Generate Music

**Operation ID**: `generate_music_api_generate_music_post`  
**Path**: `POST /api/generate_music`

Generate music from lyrics with music notation.

**Request Body**: See OpenAPI spec for schema details

### Get Audio File

**Operation ID**: `get_audio_file_api_audio__audio_id__get`  
**Path**: `GET /api/audio/{audio_id}`

Retrieve generated audio file by ID.

**Parameters**:

- `audio_id` (required): 

## Use Cases

- Text-to-speech
- Multilingual audio
- Music generation
- Sound effects

## Common Patterns

- Text → Generate → Return audio

## Tool Selection Decision Tree

1. **Identify the task domain**
   - System operations → `tehuti-core`
   - Workflow automation → `n8n-mcp`
   - File operations → `filesystem-mcp`
   - Database queries → `postgres-mcp`
   - Image generation → `comfyui-intelligent`
   - Audio generation → `tehuti-audio`
   - RAG/Knowledge → `maatlangchain-pipeline`

2. **Check tool availability**
   - Verify tool is accessible (port check)
   - Check OpenAPI spec for available operations

3. **Select appropriate tool**
   - Match user intent to tool capability
   - Consider tool chaining for complex tasks

4. **Execute with Maat principles**
   - Truth: Accurate parameters
   - Balance: Appropriate tool selection
   - Order: Systematic execution
   - Justice: Proper attribution
   - Self-Reflection: Learn from results

## Error Handling

Common errors and solutions:

- **Connection Error**: Check if MCP server is running on expected port
- **Parameter Error**: Verify parameter types match OpenAPI spec
- **Timeout Error**: Increase timeout or optimize operation
- **Permission Error**: Check file/database permissions

## Best Practices

1. Always validate parameters before tool execution
2. Use appropriate timeouts for long-running operations
3. Log tool usage to gitMaat for learning
4. Chain tools systematically for complex tasks
5. Handle errors gracefully with informative messages

## Related Tools

See `training/schemas/tool-relationships.json` for tool dependency information.

---
**Maat Alignment**: This documentation follows Maat principles of Truth, Balance, Order, Justice, and Self-Reflection.
