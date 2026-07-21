import asyncio
import contextlib
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import GENERATED_DIR, get_settings
from app.routers.generate import router as generate_router
from app.services.media_service import cleanup_old_generations

logging.basicConfig(level=logging.INFO)


async def _cleanup_loop() -> None:
    settings = get_settings()
    while True:
        try:
            cleanup_old_generations(settings.cleanup_max_age_minutes)
        except Exception:
            logging.exception("Cleanup task failed")
        await asyncio.sleep(settings.cleanup_interval_minutes * 60)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    task = asyncio.create_task(_cleanup_loop())
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


settings = get_settings()

app = FastAPI(title="¿Qué piensa tu mascota?", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)

GENERATED_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(GENERATED_DIR)), name="media")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
