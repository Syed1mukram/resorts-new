from pathlib import Path
from typing import List
import subprocess
import shutil
import os

from config import IMAGE_EXTENSIONS


# ==========================================================
# FILES
# ==========================================================

def get_images(folder: Path) -> List[Path]:
    """
    Return all supported images sorted alphabetically.
    """

    images = []

    for ext in IMAGE_EXTENSIONS:
        images.extend(folder.glob(f"*{ext}"))
        images.extend(folder.glob(f"*{ext.upper()}"))

    return sorted(images)


def ensure_dir(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)


def clean_folder(folder: Path):
    if not folder.exists():
        return

    for item in folder.iterdir():
        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception:
            pass


# ==========================================================
# FFMPEG
# ==========================================================

def ffmpeg_exists() -> bool:
    return shutil.which("ffmpeg") is not None


def ffprobe_exists() -> bool:
    return shutil.which("ffprobe") is not None


def run(cmd):
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.returncode != 0:
        raise RuntimeError(process.stderr)

    return process.stdout


# ==========================================================
# AUDIO
# ==========================================================

def get_audio_duration(audio_file: Path) -> float:

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_file),
    ]

    output = run(cmd)

    return float(output.strip())


# ==========================================================
# VIDEO
# ==========================================================

def get_video_duration(video_file: Path) -> float:

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_file),
    ]

    output = run(cmd)

    return float(output.strip())


# ==========================================================
# IMAGE
# ==========================================================

def file_size_mb(file: Path) -> float:
    return round(file.stat().st_size / (1024 * 1024), 2)


def is_image(file: Path) -> bool:
    return file.suffix.lower() in IMAGE_EXTENSIONS


# ==========================================================
# LOGGING
# ==========================================================

def log(message: str):
    print(f"[INFO] {message}")


def warn(message: str):
    print(f"[WARNING] {message}")


def error(message: str):
    print(f"[ERROR] {message}")