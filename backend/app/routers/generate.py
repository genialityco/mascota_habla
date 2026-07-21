import logging
import re
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

from app.config import Settings, get_settings
from app.deps import get_elevenlabs_service, get_gemini_service
from app.schemas import GenerateResponse, PetMetadata
from app.services.elevenlabs_service import ElevenLabsError, ElevenLabsService
from app.services.gemini_service import GeminiError, GeminiService
from app.services.media_service import MediaError, build_card, build_video, crop_grid_to_frames, new_generation_dir

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["generate"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_SPECIES = {"perro", "gato", "otro"}
MAX_TRAITS = 3


def _prepare_monologue_text(monologue_text: str) -> str:
    cleaned = re.sub(r"\s+", " ", monologue_text).strip()
    if len(cleaned) > 240:
        cleaned = cleaned[:240].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
    return cleaned


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    photo: UploadFile,
    species: str = Form(...),
    pet_name: str = Form(""),
    traits: str = Form(""),
    anecdote: str = Form(""),
    settings: Settings = Depends(get_settings),
    gemini: GeminiService = Depends(get_gemini_service),
    elevenlabs: ElevenLabsService = Depends(get_elevenlabs_service),
) -> GenerateResponse:
    if photo.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, "Formato de imagen no soportado. Usá JPG, PNG o WEBP.")
    if species not in ALLOWED_SPECIES:
        raise HTTPException(400, "Especie inválida.")

    image_bytes = await photo.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(image_bytes) > max_bytes:
        raise HTTPException(400, f"La imagen supera el límite de {settings.max_upload_mb}MB.")
    if not image_bytes:
        raise HTTPException(400, "La imagen está vacía.")

    trait_list = [t.strip() for t in traits.split(",") if t.strip()][:MAX_TRAITS]
    meta = PetMetadata(
        pet_name=pet_name.strip(),
        species=species,  # type: ignore[arg-type]
        traits=trait_list,
        anecdote=anecdote.strip(),
    )

    generation_id = uuid.uuid4().hex
    gen_dir = new_generation_dir(generation_id)

    try:
        monologue = gemini.generate_monologue(image_bytes, photo.content_type, meta)
        illustrations_bytes = gemini.generate_illustrations(
            image_bytes,
            photo.content_type,
            meta,
            monologue.monologo,
            count=1,
        )
        prepared_monologue = _prepare_monologue_text(monologue.monologo)
        audio_bytes = elevenlabs.synthesize(prepared_monologue, species=meta.species)
    except (GeminiError, ElevenLabsError) as exc:
        raise HTTPException(502, str(exc)) from exc

    illustration_path = gen_dir / "illustration.png"
    audio_path = gen_dir / "audio.mp3"
    card_path = gen_dir / "card.png"
    video_path = gen_dir / "video.mp4"

    illustration_paths = crop_grid_to_frames(illustrations_bytes[0], gen_dir)
    if illustration_paths:
        illustration_path.write_bytes(illustration_paths[0].read_bytes())
    audio_path.write_bytes(audio_bytes)

    try:
        build_card(illustrations_bytes[0], monologue.titulo, prepared_monologue, card_path)
        build_video(illustration_paths, audio_path, video_path)
    except MediaError as exc:
        raise HTTPException(502, str(exc)) from exc

    return GenerateResponse(
        id=generation_id,
        title=monologue.titulo,
        monologue=prepared_monologue,
        illustration_url=f"/media/{generation_id}/illustration.png",
        card_url=f"/media/{generation_id}/card.png",
        audio_url=f"/media/{generation_id}/audio.mp3",
        video_url=f"/media/{generation_id}/video.mp4",
    )
