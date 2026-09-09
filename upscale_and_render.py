from pathlib import Path
import subprocess
import cv2
import torch

from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

from src.timeline_builder import TimelineBuilder
from src.renderer import Renderer
import config


BASE_DIR = Path("/kaggle/working/resorts")
INPUT_DIR = BASE_DIR / "input"
IMAGES_ROOT = INPUT_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"

MODEL_PATH = BASE_DIR / "RealESRGAN_x4plus.pth"

MODEL_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"

if not MODEL_PATH.exists():
    print("Downloading Real-ESRGAN x4 model...")
    subprocess.run(
        ["wget", "-q", MODEL_URL, "-O", str(MODEL_PATH)],
        check=True
    )
    print("Real-ESRGAN model downloaded.")

UPSCALED_ROOT = BASE_DIR / "cache" / "upscaled"
OVERLAY_ROOT = BASE_DIR / "cache" / "stock_overlay"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPSCALED_ROOT.mkdir(parents=True, exist_ok=True)
OVERLAY_ROOT.mkdir(parents=True, exist_ok=True)


# ============================================================
# REAL-ESRGAN 4X
# ============================================================

print("Loading Real-ESRGAN x4plus...")

model = RRDBNet(
    num_in_ch=3,
    num_out_ch=3,
    num_feat=64,
    num_block=23,
    num_grow_ch=32,
    scale=4
)

upsampler = RealESRGANer(
    scale=4,
    model_path=str(MODEL_PATH),
    model=model,
    tile=0,
    tile_pad=10,
    pre_pad=0,
    half=True,
    gpu_id=0
)

print("Real-ESRGAN 4X READY")
print("CUDA:", torch.cuda.is_available())


# ============================================================
# STOCK VIDEO OVERLAY
# ============================================================

def add_stock_overlay(input_video, output_video):
    """
    Adds:
        black box
        yellow 'Stock video'
    at bottom-right.
    """

    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    filter_text = (
        f"drawtext="
        f"fontfile='{font}':"
        f"text='Stock video':"
        f"fontcolor=yellow:"
        f"fontsize=28:"
        f"box=1:"
        f"boxcolor=black@1.0:"
        f"boxborderw=12:"
        f"x=w-tw-30:"
        f"y=h-th-30"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_video),
        "-vf", filter_text,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_video)
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


# ============================================================
# SELECT ONLY IMAGES USED BY TIMELINE
# ============================================================

def get_selected_images(timeline):
    selected = []

    for item in timeline:
        if item.get("media_type") != "image":
            continue

        media = item.get("media")

        if not media:
            continue

        path = Path(media)

        if path.exists() and path not in selected:
            selected.append(path)

    return selected


# ============================================================
# UPSCALE SELECTED IMAGES ONLY
# ============================================================

def upscale_selected_images(timeline, hotel_number):

    hotel_upscaled_dir = UPSCALED_ROOT / str(hotel_number)
    hotel_upscaled_dir.mkdir(parents=True, exist_ok=True)

    selected = get_selected_images(timeline)

    print(f"\nHotel {hotel_number}: {len(selected)} selected images")
    print("Upscaling ONLY selected images...")

    path_map = {}

    for index, image_path in enumerate(selected, 1):

        output_path = hotel_upscaled_dir / image_path.name

        if output_path.exists():
            print(f"[{index}/{len(selected)}] Already exists: {image_path.name}")
            path_map[str(image_path.resolve())] = output_path.resolve()
            continue

        print(f"[{index}/{len(selected)}] 4X: {image_path.name}")

        img = cv2.imread(str(image_path))

        if img is None:
            print("  WARNING: Could not read image")
            continue

        output, _ = upsampler.enhance(
            img,
            outscale=4
        )

        cv2.imwrite(
            str(output_path),
            output,
            [cv2.IMWRITE_JPEG_QUALITY, 95]
        )

        path_map[str(image_path.resolve())] = output_path.resolve()

    # Replace timeline paths with 4X versions
    for item in timeline:

        if item.get("media_type") != "image":
            continue

        media = item.get("media")

        if not media:
            continue

        original = str(Path(media).resolve())

        if original in path_map:
            item["media"] = str(path_map[original])

    print("Selected-image 4X upscale complete.")

    return timeline


# ============================================================
# ADD STOCK OVERLAY TO PEXELS VIDEOS
# ============================================================

def process_stock_videos(timeline, hotel_number):

    hotel_overlay_dir = OVERLAY_ROOT / str(hotel_number)
    hotel_overlay_dir.mkdir(parents=True, exist_ok=True)

    processed = {}

    for item in timeline:

        if item.get("media_type") != "video":
            continue

        media = item.get("media")

        if not media:
            continue

        source = Path(media)

        if not source.exists():
            continue

        source_key = str(source.resolve())

        if source_key in processed:
            item["media"] = str(processed[source_key])
            continue

        output = hotel_overlay_dir / f"{source.stem}_stock.mp4"

        if not output.exists():

            print(f"Adding 'Stock video' overlay: {source.name}")

            try:
                add_stock_overlay(source, output)
            except Exception as e:
                print(f"  Overlay failed: {e}")
                continue

        processed[source_key] = output.resolve()
        item["media"] = str(output.resolve())

    return timeline


# ============================================================
# PROCESS ALL 11 HOTELS
# ============================================================

for hotel_number in range(1, 12):

    print("\n")
    print("=" * 70)
    print(f"PROCESSING HOTEL {hotel_number}")
    print("=" * 70)

    hotel_dir = IMAGES_ROOT / str(hotel_number)
    images_dir = hotel_dir / "images"
    voice_file = hotel_dir / "voice.mp3"

    output_file = OUTPUT_DIR / f"hotel_{hotel_number}.mp4"

    if not images_dir.exists():
        print(f"SKIP: Images folder not found: {images_dir}")
        continue

    if not voice_file.exists():
        print(f"SKIP: Voice file not found: {voice_file}")
        continue

    try:

        print("Building timeline...")

        builder = TimelineBuilder(
            audio_file=voice_file,
            images_dir=images_dir
        )

        timeline = builder.build()

        print(f"Timeline created: {len(timeline)} segments")

        # ----------------------------------------------------
        # PEXELS STOCK VIDEO OVERLAY
        # ----------------------------------------------------

        timeline = process_stock_videos(
            timeline,
            hotel_number
        )

        # ----------------------------------------------------
        # REAL-ESRGAN 4X — SELECTED IMAGES ONLY
        # ----------------------------------------------------

        timeline = upscale_selected_images(
            timeline,
            hotel_number
        )

        # ----------------------------------------------------
        # FINAL RENDER
        # ----------------------------------------------------

        print("Rendering final video...")

        Renderer().render(
            timeline=timeline,
            audio_file=voice_file,
            output_file=output_file,
            hotel_number=hotel_number
        )

        print(f"SUCCESS: {output_file}")

    except Exception as e:

        print(f"ERROR in Hotel {hotel_number}:")
        print(e)

        continue


print("\n")
print("=" * 70)
print("ALL 11 HOTELS FINISHED")
print("=" * 70)
