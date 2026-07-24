from functools import lru_cache

from app.config import get_settings
from app.services.elevenlabs_service import ElevenLabsService
from app.services.gemini_service import GeminiService
from app.services.gemini_tts_service import GeminiTTSService
from app.services.tts_service import TTSService


@lru_cache
def get_gemini_service() -> GeminiService:
    return GeminiService(get_settings())


@lru_cache
def get_elevenlabs_service() -> ElevenLabsService:
    return ElevenLabsService(get_settings())


@lru_cache
def get_gemini_tts_service() -> GeminiTTSService:
    return GeminiTTSService(get_settings())


@lru_cache
def get_tts_service() -> TTSService:
    settings = get_settings()
    if settings.tts_provider == "gemini":
        return get_gemini_tts_service()
    return get_elevenlabs_service()
