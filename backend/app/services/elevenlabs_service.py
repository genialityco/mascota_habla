import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from elevenlabs.client import ElevenLabs
from elevenlabs.types.voice_settings import VoiceSettings

from app.config import Settings

logger = logging.getLogger(__name__)

# Pitch shift (ratio) applied on top of the base ElevenLabs voice.
# The account only has one (deep, male-sounding) voice available, so
# macho/hembra and perro/gato are all differentiated via pitch instead
# of separate voice ids. Kept close to 1.0 so nothing sounds unnaturally
# grave — combos range roughly from 0.94 (macho + perro) to 1.24 (hembra + gato).
SEXO_BASE_PITCH = {
    "macho": 0.97,
    "hembra": 1.18,
}
SPECIES_PITCH_ADJUST = {
    "perro": -0.03,
    "gato": 0.05,
    "otro": 0.0,
}

# Exaggerated, snappy delivery for a more comedic read regardless of species.
COMIC_VOICE_SETTINGS = VoiceSettings(
    stability=0.3,
    similarity_boost=0.8,
    style=0.85,
    use_speaker_boost=True,
    speed=1.1,
)


class ElevenLabsError(RuntimeError):
    pass


class ElevenLabsService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = ElevenLabs(api_key=settings.elevenlabs_api_key)

    def synthesize(self, text: str, species: str | None = None, sexo: str | None = None) -> bytes:
        prepared_text = shorten_text_for_voice(text)
        voice_id = self._voice_id_for(sexo)
        try:
            audio_chunks = self._client.text_to_speech.convert(
                text=prepared_text,
                voice_id=voice_id,
                model_id=self._settings.elevenlabs_model_id,
                output_format="mp3_44100_128",
                voice_settings=COMIC_VOICE_SETTINGS,
            )
            speech_bytes = b"".join(audio_chunks)
            return _apply_pitch(speech_bytes, species, sexo)
        except Exception as exc:
            logger.exception("ElevenLabs TTS failed")
            raise ElevenLabsError("No se pudo generar la voz de la mascota.") from exc

    def _voice_id_for(self, sexo: str | None) -> str:
        if sexo == "macho" and self._settings.elevenlabs_voice_id_macho:
            return self._settings.elevenlabs_voice_id_macho
        if sexo == "hembra" and self._settings.elevenlabs_voice_id_hembra:
            return self._settings.elevenlabs_voice_id_hembra
        return self._settings.elevenlabs_voice_id


def _apply_pitch(audio_bytes: bytes, species: str | None, sexo: str | None) -> bytes:
    pitch = SEXO_BASE_PITCH.get(sexo or "macho", 1.0) + SPECIES_PITCH_ADJUST.get(species or "otro", 0.0)
    if pitch == 1.0:
        return audio_bytes

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        logger.warning("ffmpeg no disponible; se omite el efecto de voz por sexo/especie.")
        return audio_bytes

    with tempfile.TemporaryDirectory() as tmp_dir:
        in_path = Path(tmp_dir) / "in.mp3"
        out_path = Path(tmp_dir) / "out.mp3"
        in_path.write_bytes(audio_bytes)
        result = subprocess.run(
            [ffmpeg_path, "-y", "-i", str(in_path), "-af", f"rubberband=pitch={pitch}", str(out_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.warning("No se pudo aplicar el efecto de voz por sexo/especie: %s", result.stderr[-500:])
            return audio_bytes
        return out_path.read_bytes()


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
