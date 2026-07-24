from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated"
FONTS_DIR = BASE_DIR / "assets" / "fonts"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str
    gemini_text_model: str = "gemini-2.5-flash"
    gemini_image_model: str = "gemini-2.5-flash-image"

    tts_provider: Literal["elevenlabs", "gemini"] = "elevenlabs"

    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    elevenlabs_voice_id_macho: str = ""
    elevenlabs_voice_id_hembra: str = ""
    elevenlabs_model_id: str = "eleven_multilingual_v2"

    gemini_tts_model: str = "gemini-2.5-flash-preview-tts"
    gemini_tts_voices_macho: str = "Puck,Fenrir,Orus"
    gemini_tts_voices_hembra: str = "Kore,Aoede,Leda"

    cors_origins: str = "http://localhost:5173"

    max_upload_mb: int = 8
    cleanup_max_age_minutes: int = 120
    cleanup_interval_minutes: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
