from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# PROJECT
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parent

INPUT_DIR = ROOT_DIR / "input"
OUTPUT_DIR = ROOT_DIR / "output"
CACHE_DIR = ROOT_DIR / "cache"
ASSETS_DIR = ROOT_DIR / "assets"

# ==========================================================
# INPUT FILES
# ==========================================================

HOTEL_DIR = INPUT_DIR

VOICE_FILE = INPUT_DIR / "voice.mp3"
ORIGINAL_IMAGES_DIR = INPUT_DIR / "images"

# ==========================================================
# CACHE
# ==========================================================

STOCK_DIR = CACHE_DIR / "stock"
TEMP_DIR = CACHE_DIR / "temp"
ENHANCED_DIR = CACHE_DIR / "enhanced"

# ==========================================================
# OUTPUT
# ==========================================================

OUTPUT_VIDEO = OUTPUT_DIR / "final_video.mp4"

# ==========================================================
# VIDEO
# ==========================================================

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

FPS = 30

VIDEO_CODEC = "h264_nvenc"
AUDIO_CODEC = "aac"

PIXEL_FORMAT = "yuv420p"

PRESET = "medium"
CRF = 18

# ==========================================================
# IMAGE
# ==========================================================

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".avif",
)

DEFAULT_ZOOM = 1.05

# ==========================================================
# WHISPER
# ==========================================================

WHISPER_MODEL = "base"
LANGUAGE = "en"

# ==========================================================
# PEXELS
# ==========================================================

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_RESULTS = 5

# ==========================================================
# STOCK VIDEO
# ==========================================================

STOCK_MIN_DURATION = 3
STOCK_MAX_DURATION = 15

# ==========================================================
# TIMELINE
# ==========================================================

TARGET_CLIP_DURATION = 4.0
MIN_SCENE_DURATION = 10.0
IMAGE_RATIO = 0.70

# ==========================================================
# CACHE OPTIONS
# ==========================================================

USE_CACHE = True

# ==========================================================
# CREATE FOLDERS
# ==========================================================

for folder in (
    INPUT_DIR,
    OUTPUT_DIR,
    CACHE_DIR,
    STOCK_DIR,
    TEMP_DIR,
    ENHANCED_DIR,
    HOTELS_DIR,
):
    folder.mkdir(parents=True, exist_ok=True)