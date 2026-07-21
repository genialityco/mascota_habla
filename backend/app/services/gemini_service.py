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
        return self.generate_illustrations(image_bytes, mime_type, meta, "", count=1)[0]

    def generate_illustrations(
        self,
        image_bytes: bytes,
        mime_type: str,
        meta: PetMetadata,
        monologue_text: str,
        count: int = 4,
    ) -> list[bytes]:
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        prompts = []
        for index in range(count):
            if index == 0:
                scene_hint = "una escena inicial del monólogo"
            elif index == 1:
                scene_hint = "una escena de transición o emoción"
            elif index == 2:
                scene_hint = "una escena divertida o concreta"
            else:
                scene_hint = "una escena final o resolutiva"
            prompts.append(build_illustration_prompt(meta, scene_hint=scene_hint, monologue=monologue_text))

        generated: list[bytes] = []
        for prompt in prompts:
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
            found = False
            for candidate in candidates:
                parts = candidate.content.parts if candidate.content else []
                for part in parts or []:
                    if part.inline_data and part.inline_data.data:
                        generated.append(part.inline_data.data)
                        found = True
                        break
                if found:
                    break
            if not found:
                raise GeminiError("Gemini no devolvió ninguna imagen para la ilustración.")

        return generated
