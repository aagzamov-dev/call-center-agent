"""Audio service — Speech-to-Text via OpenAI whisper-1."""

from __future__ import annotations

import io
from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

AUDIO_DIR = Path("storage/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


async def transcribe_audio(
    audio_bytes: bytes,
    filename: str = "recording.webm",
    language: str | None = None,
) -> dict:
    """Transcribe audio to text using whisper-1. Returns transcript + metadata."""
    # Save a copy for reference
    save_path = AUDIO_DIR / filename
    save_path.write_bytes(audio_bytes)

    # Send to OpenAI Whisper
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename  # whisper needs a filename with extension

    kwargs = {"model": settings.STT_MODEL, "file": audio_file}
    if language:
        kwargs["language"] = language

    transcript = await client.audio.transcriptions.create(**kwargs)

    return {
        "text": transcript.text,
        "audio_url": f"/static/audio/{filename}",
        "model": settings.STT_MODEL,
        "file_size": len(audio_bytes),
    }
