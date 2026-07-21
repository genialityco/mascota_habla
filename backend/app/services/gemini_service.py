import logging

from google import genai
from google.genai import types

from app.config import Settings
from app.prompts import build_illustration_prompt, build_monologue_prompt
from app.schemas import MonologueResponse, PetMetadata

logger = logging.getLogger(__name__)


class GeminiError(RuntimeError):
    pass


class GeminiService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def generate_monologue(self, image_bytes: bytes, mime_type: str, meta: PetMetadata) -> MonologueResponse:
        prompt = build_monologue_prompt(meta)
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        try:
            response = self._client.models.generate_content(
                model=self._settings.gemini_text_model,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MonologueResponse,
                ),
            )
        except Exception as exc:
            logger.exception("Gemini monologue generation failed")
            raise GeminiError("No se pudo generar el monólogo de la mascota.") from exc

        parsed = response.parsed
        if not isinstance(parsed, MonologueResponse):
            raise GeminiError("Gemini devolvió una respuesta inesperada para el monólogo.")
        return parsed

    def generate_illustration(self, image_bytes: bytes, mime_type: str, meta: PetMetadata) -> bytes:
        prompt = build_illustration_prompt(meta)
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        try:
            response = self._client.models.generate_content(
                model=self._settings.gemini_image_model,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
            )
        except Exception as exc:
            logger.exception("Gemini illustration generation failed")
            raise GeminiError("No se pudo generar la ilustración de la mascota.") from exc

        candidates = response.candidates or []
        for candidate in candidates:
            parts = candidate.content.parts if candidate.content else []
            for part in parts or []:
                if part.inline_data and part.inline_data.data:
                    return part.inline_data.data

        raise GeminiError("Gemini no devolvió ninguna imagen para la ilustración.")
