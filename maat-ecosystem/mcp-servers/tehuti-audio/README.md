# Tehuti Audio - Bark TTS MCP Server

Bark TTS integration for Tehuti Lab, providing text-to-speech, multilingual, and creative audio generation capabilities.

## Overview

This MCP server exposes Bark's text-to-audio capabilities as OpenAPI endpoints, making them accessible through Open WebUI and other MCP-compatible tools.

## Features

- **Text-to-Speech (TTS)**: Generate natural-sounding speech from text
- **Voice Presets**: 100+ speaker presets across multiple languages
- **Multilingual Support**: Auto-detect and generate speech in 13+ languages
- **Music Generation**: Generate music from lyrics with notation
- **Emotion Tags**: Support for [laughs], [sighs], [music], etc.
- **GPU Accelerated**: Optimized for RTX 3080 Ti (12GB VRAM)

## API Endpoints

### POST /api/generate_speech
Basic text-to-speech generation.

**Request:**
```json
{
  "text": "Hello, this is a test",
  "voice_preset": "v2/en_speaker_1",
  "temperature": 0.7
}
```

**Response:**
```json
{
  "audio_file_path": "/tmp/tehuti-audio/uuid.wav",
  "sample_rate": 24000,
  "duration": 5.2,
  "audio_base64": "base64_encoded_audio..."
}
```

### POST /api/generate_speech_with_voice
Generate speech with specific voice preset and emotion tags.

**Request:**
```json
{
  "text": "Hello!",
  "voice_preset": "v2/en_speaker_6",
  "emotion_tags": "[laughs] That's funny!"
}
```

### POST /api/generate_multilingual
Generate speech in multiple languages (auto-detects language).

**Request:**
```json
{
  "text": "Bonjour, comment allez-vous?",
  "language": "fr"
}
```

### POST /api/generate_music
Generate music from lyrics.

**Request:**
```json
{
  "lyrics": "♪ In the jungle, the mighty jungle, the lion barks tonight ♪"
}
```

### GET /health
Health check endpoint.

### GET /openapi.json
OpenAPI specification for tool discovery.

## Voice Presets

Bark supports 100+ speaker presets. Common examples:
- `v2/en_speaker_1` through `v2/en_speaker_9` (English speakers)
- Language-specific presets for German, Spanish, French, etc.

Browse full list: https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683

## Emotion Tags

Supported emotion tags:
- `[laughs]`, `[laugh]` - Laughter
- `[sighs]`, `[sigh]` - Sighing
- `[music]` - Music generation
- `[gasps]` - Gasping
- `[clears throat]` - Throat clearing
- `...` - Hesitations
- `CAPITALIZATION` - Emphasis

## Supported Languages

- English (en)
- German (de)
- Spanish (es)
- French (fr)
- Hindi (hi)
- Italian (it)
- Japanese (ja)
- Korean (ko)
- Polish (pl)
- Portuguese (pt)
- Russian (ru)
- Turkish (tr)
- Chinese, simplified (zh)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Bark is installed at `/home/suspect/bark`

3. Install systemd service:
```bash
sudo cp /home/suspect/.n8n/systemd-services/mcpo-tehuti-audio.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mcpo-tehuti-audio.service
sudo systemctl start mcpo-tehuti-audio.service
```

## Usage

### Direct API Call

```python
import requests

response = requests.post(
    "http://127.0.0.1:8021/api/generate_speech",
    json={
        "text": "Hello, this is Bark TTS!",
        "voice_preset": "v2/en_speaker_1"
    }
)

audio_data = response.json()
print(f"Audio generated: {audio_data['audio_file_path']}")
```

### Via Open WebUI

The server is automatically discovered by Open WebUI and available as a tool in the chat interface.

## Configuration

### GPU Settings

The service is configured for RTX 3080 Ti (12GB VRAM):
- `SUNO_USE_SMALL_MODELS=False` - Use full models
- `SUNO_OFFLOAD_CPU=False` - Keep everything on GPU

For smaller GPUs, modify the systemd service:
```ini
Environment="SUNO_USE_SMALL_MODELS=True"
Environment="SUNO_OFFLOAD_CPU=True"
```

### Audio Storage

Generated audio files are stored in `/tmp/tehuti-audio/` with UUID-based filenames. Files are temporary and may be cleaned up by the system.

## Troubleshooting

### Models not loading
- Check GPU availability: `nvidia-smi`
- Verify Bark installation: `python3 -c "import bark; print('OK')"`
- Check logs: `journalctl -u mcpo-tehuti-audio.service -n 50`

### Out of memory
- Enable small models: `SUNO_USE_SMALL_MODELS=True`
- Enable CPU offloading: `SUNO_OFFLOAD_CPU=True`

### Service not starting
- Check Python path: Ensure Python 3 is in PATH
- Check permissions: Service runs as user `suspect`
- Check logs: `journalctl -u mcpo-tehuti-audio.service`

## Performance

- **GPU (RTX 3080 Ti)**: ~2-5 seconds per generation
- **CPU**: Significantly slower (10x+)
- **Model Loading**: One-time cost on first request (~30 seconds)

## License

Bark is licensed under MIT License. See `/home/suspect/bark/LICENSE` for details.

## References

- Bark GitHub: https://github.com/suno-ai/bark
- Voice Presets: https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683
- Bark Examples: https://suno.ai/examples/bark-v0

