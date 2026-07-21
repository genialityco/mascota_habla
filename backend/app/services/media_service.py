import json
import logging
import shutil
import subprocess
import tempfile
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


def _resolve_binary(binary_name: str) -> str:
    resolved = shutil.which(binary_name)
    if not resolved:
        raise MediaError(
            f"No se encontró '{binary_name}' en el entorno de despliegue. Instala ffmpeg/ffprobe en el servidor."
        )
    return resolved


def _probe_duration_seconds(audio_path: Path) -> float:
    ffprobe_path = _resolve_binary("ffprobe")
    result = subprocess.run(
        [
            ffprobe_path,
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


def _make_frame(image_path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    return _cover_resize(image, size)


def crop_grid_to_frames(image_bytes: bytes, out_dir: Path) -> list[Path]:
    image = Image.open(_bytes_io(image_bytes)).convert("RGB")
    width, height = image.size
    cell_w = width // 2
    cell_h = height // 2
    frames: list[Path] = []
    for row in range(2):
        for col in range(2):
            left = col * cell_w
            top = row * cell_h
            right = left + cell_w
            bottom = top + cell_h
            cropped = image.crop((left, top, right, bottom)).convert("RGB")
            out_path = out_dir / f"scene_{len(frames) + 1}.png"
            cropped.save(out_path, format="PNG")
            frames.append(out_path)
    return frames


def build_video(illustration_paths: list[Path] | Path, audio_path: Path, out_path: Path) -> None:
    duration = _probe_duration_seconds(audio_path)
    total_frames = max(int(duration * VIDEO_FPS), VIDEO_FPS)
    width, height = VIDEO_SIZE

    if isinstance(illustration_paths, (str, Path)):
        illustration_paths = [Path(illustration_paths)]
    resolved_paths = [Path(path) for path in illustration_paths]
    if not resolved_paths:
        raise MediaError("No hay imágenes para el video.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        frame_paths = [Path(path) for path in resolved_paths]
        if not frame_paths:
            raise MediaError("No hay imágenes para el video.")

        frame_paths = frame_paths[:4]
        if len(frame_paths) == 1:
            frame_paths = frame_paths * 2

        ffmpeg_path = _resolve_binary("ffmpeg")
        segment_duration = max(duration / len(frame_paths), 1.0)
        transition_duration = 0.5
        # Pad each looped-image input beyond its nominal segment so frame
        # quantization can't make it hit EOF before the next xfade's offset
        # is reached (which would truncate the whole chain right there).
        input_pad = 0.3
        input_args: list[str] = []
        filter_parts: list[str] = []
        stream_names: list[str] = []

        for idx, frame_path in enumerate(frame_paths):
            input_args.extend(
                ["-loop", "1", "-t", str(segment_duration + input_pad), "-i", str(frame_path)]
            )
            stream_names.append(f"v{idx}")
            filter_parts.append(
                f"[{idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,setsar=1,format=yuv420p[{stream_names[-1]}]"
            )

        if len(frame_paths) == 2:
            filter_complex = ";".join(filter_parts) + f";[{stream_names[0]}][{stream_names[1]}]xfade=transition=fade:duration={transition_duration}:offset={segment_duration - transition_duration}[pretrim]"
        else:
            filter_chain = []
            previous = stream_names[0]
            for idx in range(1, len(frame_paths)):
                offset = segment_duration * idx - transition_duration
                filter_chain.append(
                    f"[{previous}][{stream_names[idx]}]xfade=transition=fade:duration={transition_duration}:offset={offset}[tmp{idx}]"
                )
                previous = f"tmp{idx}"
            filter_complex = ";".join(filter_parts + filter_chain) + f";[{previous}]copy[pretrim]"

        # The xfade chain naturally ends transition_duration short of the full
        # audio length (each crossfade eats into the timeline). Hold the last
        # frame for that gap instead of trimming, so -shortest never has to
        # cut into the audio track and clip the last word.
        filter_complex += (
            f";[pretrim]tpad=stop_mode=clone:stop_duration={transition_duration},"
            f"trim=duration={duration},format=yuv420p[outv]"
        )

        result = subprocess.run(
            [
                ffmpeg_path,
                "-y",
                *input_args,
                "-i",
                str(audio_path),
                "-filter_complex",
                filter_complex,
                "-map",
                "[outv]",
                "-map",
                f"{len(frame_paths)}:a",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-threads",
                "1",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-pix_fmt",
                "yuv420p",
                "-shortest",
                str(out_path),
            ],
            capture_output=True,
            text=True,
        )

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
