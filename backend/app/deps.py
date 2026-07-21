from functools import lru_cache

from app.config import get_settings
from app.services.elevenlabs_service import ElevenLabsService
from app.services.gemini_service import GeminiService


@lru_cache
def get_gemini_service() -> GeminiService:
    return GeminiService(get_settings())


@lru_cache
def get_elevenlabs_service() -> ElevenLabsService:
    return ElevenLabsService(get_settings())
