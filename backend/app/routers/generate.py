import logging
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

from app.config import Settings, get_settings
from app.deps import get_elevenlabs_service, get_gemini_service
from app.schemas import GenerateResponse, PetMetadata
from app.services.elevenlabs_service import ElevenLabsError, ElevenLabsService
from app.services.gemini_service import GeminiError, GeminiService
from app.services.media_service import MediaError, build_card, build_video, new_generation_dir

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["generate"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_SPECIES = {"perro", "gato", "otro"}
MAX_TRAITS = 3


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
        illustration_bytes = gemini.generate_illustration(image_bytes, photo.content_type, meta)
        audio_bytes = elevenlabs.synthesize(monologue.monologo)
    except (GeminiError, ElevenLabsError) as exc:
        raise HTTPException(502, str(exc)) from exc

    illustration_path = gen_dir / "illustration.png"
    audio_path = gen_dir / "audio.mp3"
    card_path = gen_dir / "card.png"
    video_path = gen_dir / "video.mp4"

    illustration_path.write_bytes(illustration_bytes)
    audio_path.write_bytes(audio_bytes)

    try:
        build_card(illustration_bytes, monologue.titulo, monologue.monologo, card_path)
        build_video(illustration_path, audio_path, video_path)
    except MediaError as exc:
        raise HTTPException(502, str(exc)) from exc

    return GenerateResponse(
        id=generation_id,
        title=monologue.titulo,
        monologue=monologue.monologo,
        illustration_url=f"/media/{generation_id}/illustration.png",
        card_url=f"/media/{generation_id}/card.png",
        audio_url=f"/media/{generation_id}/audio.mp3",
        video_url=f"/media/{generation_id}/video.mp4",
    )
