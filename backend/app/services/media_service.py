import json
import logging
import shutil
import subprocess
import time
from pathlib import Path
from textwrap import TextWrapper

from PIL import Image, ImageDraw, ImageFont

from app.config import FONTS_DIR, GENERATED_DIR

logger = logging.getLogger(__name__)

CARD_SIZE = (1080, 1350)
VIDEO_SIZE = (1080, 1080)
VIDEO_FPS = 30


class MediaError(RuntimeError):
    pass


def _font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    name = "Baloo2-Bold.ttf" if bold else "Baloo2-Regular.ttf"
    path = FONTS_DIR / name
    return ImageFont.truetype(str(path), size)


def new_generation_dir(generation_id: str) -> Path:
    path = GENERATED_DIR / generation_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_card(illustration_bytes: bytes, title: str, monologue: str, out_path: Path) -> None:
    illustration = Image.open(_bytes_io(illustration_bytes)).convert("RGB")

    card = Image.new("RGB", CARD_SIZE, color=(255, 244, 230))
    illus_w, illus_h = CARD_SIZE[0], int(CARD_SIZE[1] * 0.62)
    fitted = _cover_resize(illustration, (illus_w, illus_h))
    card.paste(fitted, (0, 0))

    draw = ImageDraw.Draw(card, "RGBA")

    panel_top = illus_h - 60
    draw.rounded_rectangle(
        [(0, panel_top), (CARD_SIZE[0], CARD_SIZE[1])],
        radius=48,
        fill=(255, 250, 244, 255),
    )

    title_font = _font(bold=True, size=64)
    body_font = _font(bold=False, size=38)

    text_x = 64
    text_y = panel_top + 56
    draw.text((text_x, text_y), title.strip(), font=title_font, fill=(60, 40, 30), anchor="la")

    wrapper = TextWrapper(width=34)
    lines = wrapper.wrap(monologue.strip())
    line_y = text_y + 96
    for line in lines:
        draw.text((text_x, line_y), line, font=body_font, fill=(80, 60, 50), anchor="la")
        line_y += 52

    card.save(out_path, format="PNG")


def _cover_resize(image: Image.Image, target: tuple[int, int]) -> Image.Image:
    target_w, target_h = target
    src_w, src_h = image.size
    scale = max(target_w / src_w, target_h / src_h)
    new_size = (int(src_w * scale), int(src_h * scale))
    resized = image.resize(new_size, Image.LANCZOS)
    left = (new_size[0] - target_w) // 2
    top = (new_size[1] - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def _bytes_io(data: bytes):
    from io import BytesIO

    return BytesIO(data)


def _probe_duration_seconds(audio_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise MediaError("No se pudo leer la duración del audio generado.")
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def build_video(illustration_path: Path, audio_path: Path, out_path: Path) -> None:
    duration = _probe_duration_seconds(audio_path)
    total_frames = max(int(duration * VIDEO_FPS), VIDEO_FPS)
    width, height = VIDEO_SIZE

    zoompan = (
        f"scale={width * 2}:{height * 2}:force_original_aspect_ratio=increase,"
        f"crop={width * 2}:{height * 2},"
        f"zoompan=z='min(zoom+0.0008,1.15)':d={total_frames}:s={width}x{height}:fps={VIDEO_FPS}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(illustration_path),
        "-i",
        str(audio_path),
        "-vf",
        zoompan,
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg failed: %s", result.stderr[-2000:])
        raise MediaError("No se pudo armar el video de la mascota.")


def cleanup_old_generations(max_age_minutes: int) -> None:
    if not GENERATED_DIR.exists():
        return
    cutoff = time.time() - max_age_minutes * 60
    for child in GENERATED_DIR.iterdir():
        if child.is_dir() and child.stat().st_mtime < cutoff:
            shutil.rmtree(child, ignore_errors=True)
