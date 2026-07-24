import logging
import random

from elevenlabs.client import ElevenLabs
from elevenlabs.types.voice_settings import VoiceSettings

from app.config import Settings
from app.services.text_utils import shorten_text_for_voice

logger = logging.getLogger(__name__)

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

    def synthesize(self, text: str, sexo: str | None = None) -> bytes:
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
            return b"".join(audio_chunks)
        except Exception as exc:
            logger.exception("ElevenLabs TTS failed")
            raise ElevenLabsError("No se pudo generar la voz de la mascota.") from exc

    def _voice_id_for(self, sexo: str | None) -> str:
        pool = self._voice_pool_for(sexo)
        return random.choice(pool) if pool else self._settings.elevenlabs_voice_id

    def _voice_pool_for(self, sexo: str | None) -> list[str]:
        raw = ""
        if sexo == "macho":
            raw = self._settings.elevenlabs_voice_id_macho
        elif sexo == "hembra":
            raw = self._settings.elevenlabs_voice_id_hembra
        return [voice_id.strip() for voice_id in raw.split(",") if voice_id.strip()]
