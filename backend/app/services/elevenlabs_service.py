import logging

from elevenlabs.client import ElevenLabs

from app.config import Settings

logger = logging.getLogger(__name__)


class ElevenLabsError(RuntimeError):
    pass


class ElevenLabsService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = ElevenLabs(api_key=settings.elevenlabs_api_key)

    def synthesize(self, text: str) -> bytes:
        try:
            audio_chunks = self._client.text_to_speech.convert(
                text=text,
                voice_id=self._settings.elevenlabs_voice_id,
                model_id=self._settings.elevenlabs_model_id,
                output_format="mp3_44100_128",
            )
            return b"".join(audio_chunks)
        except Exception as exc:
            logger.exception("ElevenLabs TTS failed")
            raise ElevenLabsError("No se pudo generar la voz de la mascota.") from exc
