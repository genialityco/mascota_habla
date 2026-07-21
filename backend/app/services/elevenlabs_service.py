import logging
import re
import subprocess
import tempfile
from pathlib import Path

from elevenlabs.client import ElevenLabs

from app.config import Settings

logger = logging.getLogger(__name__)


class ElevenLabsError(RuntimeError):
    pass


class ElevenLabsService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = ElevenLabs(api_key=settings.elevenlabs_api_key)

    def synthesize(self, text: str, species: str | None = None) -> bytes:
        prepared_text = shorten_text_for_voice(text)
        try:
            audio_chunks = self._client.text_to_speech.convert(
                text=prepared_text,
                voice_id=self._settings.elevenlabs_voice_id,
                model_id=self._settings.elevenlabs_model_id,
                output_format="mp3_44100_128",
            )
            speech_bytes = b"".join(audio_chunks)
            return speech_bytes
        except Exception as exc:
            logger.exception("ElevenLabs TTS failed")
            raise ElevenLabsError("No se pudo generar la voz de la mascota.") from exc


def shorten_text_for_voice(text: str, max_words: int = 36, max_chars: int = 220) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return ""
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
    words = cleaned.split()
    if len(words) > max_words:
        cleaned = " ".join(words[:max_words]).rstrip(".,;:") + "..."
    return cleaned
