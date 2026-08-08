#!/usr/bin/env python3
"""
Tehuti Audio - Bark TTS API Server
FastAPI server exposing Bark text-to-speech capabilities as OpenAPI endpoints
"""

import logging
import sys
import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import base64

import torch
import numpy as np
from torch.serialization import add_safe_globals
from numpy.core.multiarray import scalar
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from scipy.io.wavfile import write as write_wav

# Add bark to path
bark_path = Path("/home/suspect/bark")
if str(bark_path) not in sys.path:
    sys.path.insert(0, str(bark_path))

# PyTorch 2.6+ compatibility fixes
add_safe_globals([scalar])
# Fix torch.load for PyTorch 2.6+ - ensure weights_only=False only if not specified
# This prevents "multiple values for keyword argument" errors
original_torch_load = torch.load
def safe_torch_load(*args, **kwargs):
    """
    Wrapper for torch.load that ensures weights_only=False for PyTorch 2.6+ compatibility.
    Only adds weights_only if it's not already present in kwargs.
    """
    # Only add weights_only if not already specified
    # This prevents conflicts when Bark's code already specifies it
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    try:
        return original_torch_load(*args, **kwargs)
    except TypeError as e:
        # If we get a "multiple values" error, try without our override
        if 'multiple values' in str(e) and 'weights_only' in str(e):
            # Remove weights_only from kwargs and try again
            kwargs.pop('weights_only', None)
            return original_torch_load(*args, **kwargs)
        raise
torch.load = safe_torch_load

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tehuti Audio - Bark TTS API",
    description="Text-to-speech, multilingual, and creative audio generation using Bark",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for lab use
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GPU Configuration
device = "cuda" if torch.cuda.is_available() else "cpu"
# Use small models and CPU offloading if GPU memory is constrained
# Check available GPU memory
if device == "cuda":
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader'], 
                               capture_output=True, text=True, timeout=5)
        free_memory_mb = int(result.stdout.strip().split('\n')[0]) if result.returncode == 0 else 0
        # If less than 2GB free, use small models and CPU offloading
        if free_memory_mb < 2048:
            os.environ["SUNO_USE_SMALL_MODELS"] = "True"
            os.environ["SUNO_OFFLOAD_CPU"] = "True"
            log.info(f"GPU memory constrained ({free_memory_mb}MB free), using small models and CPU offloading")
        else:
            os.environ["SUNO_USE_SMALL_MODELS"] = "False"
            os.environ["SUNO_OFFLOAD_CPU"] = "False"
            log.info(f"GPU memory available ({free_memory_mb}MB free), using full models")
    except Exception as e:
        log.warning(f"Could not check GPU memory: {e}, defaulting to small models")
        os.environ["SUNO_USE_SMALL_MODELS"] = "True"
        os.environ["SUNO_OFFLOAD_CPU"] = "True"
else:
    os.environ["SUNO_USE_SMALL_MODELS"] = "True"
    os.environ["SUNO_OFFLOAD_CPU"] = "True"

log.info(f"Using device: {device}")
log.info("Loading Bark models...")

# Lazy load Bark models
_bark_loaded = False

def load_bark_models():
    """Load Bark models on first use."""
    global _bark_loaded
    if not _bark_loaded:
        try:
            from bark import SAMPLE_RATE, preload_models
            preload_models()
            _bark_loaded = True
            log.info("✅ Bark models loaded successfully")
        except Exception as e:
            log.error(f"Failed to load Bark models: {e}")
            raise

# Audio output directory
AUDIO_OUTPUT_DIR = Path("/tmp/tehuti-audio")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Request/Response models
class GenerateSpeechRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    voice_preset: Optional[str] = Field(None, description="Voice preset (e.g., 'v2/en_speaker_1')")
    temperature: Optional[float] = Field(0.7, description="Generation temperature (0.0-1.0)")

class GenerateSpeechWithVoiceRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    voice_preset: str = Field(..., description="Voice preset identifier")
    emotion_tags: Optional[str] = Field(None, description="Emotion tags like [laughs], [sighs]")

class GenerateMultilingualRequest(BaseModel):
    text: str = Field(..., description="Text in any supported language")
    language: Optional[str] = Field(None, description="Language code (auto-detected if not specified)")

class GenerateMusicRequest(BaseModel):
    lyrics: str = Field(..., description="Lyrics with music notation (♪ ... ♪)")

class AudioResponse(BaseModel):
    audio_file_path: str = Field(..., description="Path to generated audio file")
    sample_rate: int = Field(..., description="Audio sample rate (Hz)")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    audio_base64: Optional[str] = Field(None, description="Base64-encoded audio data")

@app.on_event("startup")
async def startup_event():
    """Preload models on startup (lazy loading on first request if memory constrained)."""
    try:
        load_bark_models()
        log.info("✅ Bark models preloaded successfully")
    except Exception as e:
        log.warning(f"Could not preload models on startup: {e}")
        log.info("Models will be loaded on first request (lazy loading)")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "device": device,
        "models_loaded": _bark_loaded
    }

@app.get("/openapi.json")
async def get_openapi_spec():
    """Return OpenAPI specification."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema

@app.post("/api/generate_speech", response_model=AudioResponse)
async def generate_speech(request: GenerateSpeechRequest):
    """Generate speech from text using Bark TTS."""
    try:
        load_bark_models()
        from bark import SAMPLE_RATE, generate_audio
        
        # Prepare text with optional voice preset
        text = request.text
        if request.voice_preset:
            # Note: Bark's generate_audio doesn't directly support voice_preset in this way
            # Voice presets are typically handled via history_prompt parameter
            # For now, we'll use the text as-is
            pass
        
        log.info(f"Generating speech for text: {text[:50]}...")
        
        # Generate audio
        audio_array = generate_audio(
            text,
            history_prompt=request.voice_preset if request.voice_preset else None,
            text_temp=request.temperature,
            waveform_temp=request.temperature
        )
        
        # Save audio file
        audio_id = str(uuid.uuid4())
        audio_file = AUDIO_OUTPUT_DIR / f"{audio_id}.wav"
        write_wav(str(audio_file), SAMPLE_RATE, audio_array)
        
        duration = len(audio_array) / SAMPLE_RATE
        
        # Optionally encode as base64
        with open(audio_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        return AudioResponse(
            audio_file_path=str(audio_file),
            sample_rate=SAMPLE_RATE,
            duration=duration,
            audio_base64=audio_base64
        )
        
    except Exception as e:
        log.error(f"Error generating speech: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")

@app.post("/api/generate_speech_with_voice", response_model=AudioResponse)
async def generate_speech_with_voice(request: GenerateSpeechWithVoiceRequest):
    """Generate speech with specific voice preset and emotion tags."""
    try:
        load_bark_models()
        from bark import SAMPLE_RATE, generate_audio
        
        # Combine text with emotion tags
        text = request.text
        if request.emotion_tags:
            text = f"{text} {request.emotion_tags}"
        
        log.info(f"Generating speech with voice preset: {request.voice_preset}")
        
        # Generate audio with voice preset
        audio_array = generate_audio(
            text,
            history_prompt=request.voice_preset,
            text_temp=0.7,
            waveform_temp=0.7
        )
        
        # Save audio file
        audio_id = str(uuid.uuid4())
        audio_file = AUDIO_OUTPUT_DIR / f"{audio_id}.wav"
        write_wav(str(audio_file), SAMPLE_RATE, audio_array)
        
        duration = len(audio_array) / SAMPLE_RATE
        
        # Encode as base64
        with open(audio_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        return AudioResponse(
            audio_file_path=str(audio_file),
            sample_rate=SAMPLE_RATE,
            duration=duration,
            audio_base64=audio_base64
        )
        
    except Exception as e:
        log.error(f"Error generating speech with voice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")

@app.post("/api/generate_multilingual", response_model=AudioResponse)
async def generate_multilingual(request: GenerateMultilingualRequest):
    """Generate speech in multiple languages (auto-detects language from text)."""
    try:
        load_bark_models()
        from bark import SAMPLE_RATE, generate_audio
        
        text = request.text
        log.info(f"Generating multilingual speech (auto-detect): {text[:50]}...")
        
        # Bark automatically detects language from text
        audio_array = generate_audio(text, text_temp=0.7, waveform_temp=0.7)
        
        # Save audio file
        audio_id = str(uuid.uuid4())
        audio_file = AUDIO_OUTPUT_DIR / f"{audio_id}.wav"
        write_wav(str(audio_file), SAMPLE_RATE, audio_array)
        
        duration = len(audio_array) / SAMPLE_RATE
        
        # Encode as base64
        with open(audio_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        return AudioResponse(
            audio_file_path=str(audio_file),
            sample_rate=SAMPLE_RATE,
            duration=duration,
            audio_base64=audio_base64
        )
        
    except Exception as e:
        log.error(f"Error generating multilingual speech: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")

@app.post("/api/generate_music", response_model=AudioResponse)
async def generate_music(request: GenerateMusicRequest):
    """Generate music from lyrics with music notation."""
    try:
        load_bark_models()
        from bark import SAMPLE_RATE, generate_audio
        
        # Ensure lyrics have music notation
        lyrics = request.lyrics
        if "♪" not in lyrics:
            lyrics = f"♪ {lyrics} ♪"
        
        log.info(f"Generating music from lyrics: {lyrics[:50]}...")
        
        # Generate audio (Bark treats music notation specially)
        audio_array = generate_audio(lyrics, text_temp=0.7, waveform_temp=0.7)
        
        # Save audio file
        audio_id = str(uuid.uuid4())
        audio_file = AUDIO_OUTPUT_DIR / f"{audio_id}.wav"
        write_wav(str(audio_file), SAMPLE_RATE, audio_array)
        
        duration = len(audio_array) / SAMPLE_RATE
        
        # Encode as base64
        with open(audio_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        return AudioResponse(
            audio_file_path=str(audio_file),
            sample_rate=SAMPLE_RATE,
            duration=duration,
            audio_base64=audio_base64
        )
        
    except Exception as e:
        log.error(f"Error generating music: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate music: {str(e)}")

@app.get("/api/audio/{audio_id}")
async def get_audio_file(audio_id: str):
    """Retrieve generated audio file by ID."""
    audio_file = AUDIO_OUTPUT_DIR / f"{audio_id}.wav"
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(audio_file), media_type="audio/wav")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8021)

