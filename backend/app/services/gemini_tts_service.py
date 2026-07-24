import logging
import random
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from google import genai
from google.genai import types

from app.config import Settings
from app.services.gemini_service import GeminiError
from app.services.text_utils import shorten_text_for_voice

logger = logging.getLogger(__name__)

DEFAULT_SAMPLE_RATE = 24000
STYLE_INSTRUCTION = (
    "Decí el siguiente texto con voz de mascota de película animada: tierna, juguetona y muy "
    "expresiva, nunca robótica ni monótona. Texto: "
)


class GeminiTTSService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def synthesize(self, text: str, sexo: str | None = None) -> bytes:
        prepared_text = shorten_text_for_voice(text)
        voice_name = self._voice_name_for(sexo)

        try:
            response = self._client.models.generate_content(
                model=self._settings.gemini_tts_model,
                contents=STYLE_INSTRUCTION + prepared_text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                        )
                    ),
                ),
            )
        except Exception as exc:
            logger.exception("Gemini TTS failed")
            raise GeminiError("No se pudo generar la voz de la mascota con Gemini.") from exc

        pcm_bytes = None
        sample_rate = DEFAULT_SAMPLE_RATE
        for candidate in response.candidates or []:
            parts = candidate.content.parts if candidate.content else []
            for part in parts or []:
                if part.inline_data and part.inline_data.data:
                    pcm_bytes = part.inline_data.data
                    sample_rate = _extract_sample_rate(part.inline_data.mime_type) or DEFAULT_SAMPLE_RATE
                    break
            if pcm_bytes:
                break

        if not pcm_bytes:
            raise GeminiError("Gemini no devolvió audio para la voz de la mascota.")

        return _pcm_to_mp3(pcm_bytes, sample_rate)

    def _voice_name_for(self, sexo: str | None) -> str:
        raw = (
            self._settings.gemini_tts_voices_macho
            if sexo == "macho"
            else self._settings.gemini_tts_voices_hembra
        )
        pool = [name.strip() for name in raw.split(",") if name.strip()]
        return random.choice(pool) if pool else "Puck"


def _extract_sample_rate(mime_type: str | None) -> int | None:
    if not mime_type:
        return None
    match = re.search(r"rate=(\d+)", mime_type)
    return int(match.group(1)) if match else None


def _pcm_to_mp3(pcm_bytes: bytes, sample_rate: int) -> bytes:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise GeminiError("No se encontró 'ffmpeg' para convertir el audio generado por Gemini.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = Path(tmp_dir) / "out.mp3"
        result = subprocess.run(
            [
                ffmpeg_path,
                "-y",
                "-f",
                "s16le",
                "-ar",
                str(sample_rate),
                "-ac",
                "1",
                "-i",
                "pipe:0",
                "-codec:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(out_path),
            ],
            input=pcm_bytes,
            capture_output=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode(errors="ignore")[-2000:] if result.stderr else ""
            logger.error("ffmpeg failed converting Gemini TTS audio: %s", stderr)
            raise GeminiError("No se pudo convertir el audio generado por Gemini.")
        return out_path.read_bytes()
