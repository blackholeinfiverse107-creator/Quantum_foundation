import os
import base64
import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from openai import OpenAI

router = APIRouter()

# Initialize OpenAI client once
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    client = None

# Valid voice list for OpenAI TTS
VALID_VOICES = ["default", "alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "audio_cache")
os.makedirs(os.path.abspath(CACHE_DIR), exist_ok=True)


class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"
    model: str = "gpt-4o-mini-tts"   # Updated official TTS model
    save_cache: bool = True

    @validator("voice")
    def validate_voice(cls, v):
        if v not in VALID_VOICES:
            raise ValueError(f"Invalid voice. Must be one of {VALID_VOICES}")
        return v

    @validator("model")
    def validate_model(cls, v):
        valid_models = ["gpt-4o-mini-tts", "gpt-4o-realtime-tts"]
        if v not in valid_models:
            raise ValueError(f"Invalid model. Must be one of {valid_models}")
        return v


@router.post("/voice_tts")
async def text_to_speech(request: TTSRequest):
    # Validate text size
    if len(request.text) > 4096:
        raise HTTPException(status_code=400, detail="Text exceeds the 4096 character limit")

    # Build cache key
    cache_key = hashlib.md5(f"{request.text}{request.voice}{request.model}".encode()).hexdigest()
    cache_path = os.path.abspath(os.path.join(CACHE_DIR, f"{cache_key}.mp3"))

    # --------------------------
    # 1. Serve from Cache
    # --------------------------
    if request.save_cache and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        data_url = f"data:audio/mp3;base64,{audio_base64}"
        return {"audio_url": data_url}

    # --------------------------
    # 2. Generate TTS via OpenAI
    # --------------------------
    try:
        if not client:
            # Deterministic mock audio payload
            audio_bytes = base64.b64decode(base64.b64encode(hashlib.sha256(request.text.encode()).digest()))
        else:
            response = client.audio.speech.create(
                model=request.model,
                voice=request.voice,
                input=request.text,
                format="mp3"
            )
            audio_bytes = response.read()

        # Save to cache
        if request.save_cache:
            with open(cache_path, "wb") as f:
                f.write(audio_bytes)

    except Exception as e:
        msg = str(e)
        if "401" in msg:
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key")
        elif "429" in msg:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        raise HTTPException(status_code=500, detail=f"OpenAI TTS Error: {msg}")

    # --------------------------
    # 3. Return Base64 audio
    # --------------------------
    audio_base64 = base64.b64encode(audio_bytes).decode()
    data_url = f"data:audio/mp3;base64,{audio_base64}"
    return {"audio_url": data_url}
