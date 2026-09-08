from pathlib import Path
import shutil
import subprocess
import sys


BASE_DIR = Path("input/images")
SELECTED_PREFIX = "selected_images_"


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".avif",
    ".bmp",
}


def get_selected_images(hotel_number):
    selected_file = Path(
        f"{SELECTED_PREFIX}{hotel_number}.txt"
    )

    if not selected_file.exists():
        raise RuntimeError(
            f"Missing selection file: {selected_file}"
        )

    images = []

    for line in selected_file.read_text(
        encoding="utf-8"
    ).splitlines():

        parts = line.split("|")

        if len(parts) < 2:
            continue

        filename = parts[1].strip()

        if Path(filename).suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        images.append(filename)

    return images


def upscale_hotel(hotel_dir, selected_images):

    source_dir = hotel_dir / "images"
    work_dir = hotel_dir / "selected_upscaled"

    work_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\n----------------------------------------")
    print(f"Upscaling Hotel {hotel_dir.name}")
    print("----------------------------------------")

    for filename in selected_images:

        source = source_dir / filename
        output = work_dir / filename

        if not source.exists():
            print(f"[Missing] {filename}")
            continue

        if output.exists():
            print(f"[Skip] {filename}")
            continue

        print(f"[Upscale] {filename}")

        command = [
            sys.executable,
            "Real-ESRGAN/inference_realesrgan.py",
            "-n",
            "RealESRGAN_x4plus",
            "-i",
            str(source),
            "-o",
            str(work_dir),
        ]

        subprocess.run(
            command,
            check=True
        )

    return work_dir


def prepare_render_images(hotel_dir, upscaled_dir):

    images_dir = hotel_dir / "images"
    backup_dir = hotel_dir / "original_images_backup"

    backup_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nPreparing render images...")

    # Backup originals only once
    for image in images_dir.iterdir():

        if not image.is_file():
            continue

        if image.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        backup = backup_dir / image.name

        if not backup.exists():
            shutil.copy2(
                image,
                backup
            )

    # Remove current images except backup folders
    for image in images_dir.iterdir():

        if not image.is_file():
            continue

        if image.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        image.unlink()

    # Copy ONLY selected upscaled images
    for image in upscaled_dir.iterdir():

        if not image.is_file():
            continue

        if image.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        shutil.copy2(
            image,
            images_dir / image.name
        )

        print(
            f"[Render] {image.name}"
        )


def main():

    hotels = []

    for folder in BASE_DIR.iterdir():

        if not folder.is_dir():
            continue

        if not folder.name.isdigit():
            continue

        hotels.append(folder)

    hotels.sort(
        key=lambda p: int(p.name)
    )

    if not hotels:
        raise RuntimeError(
            "No hotel folders found."
        )

    # ------------------------------------------------------
    # 1. SELECTED IMAGES → UPSCALE
    # ------------------------------------------------------

    for hotel_dir in hotels:

        selected = get_selected_images(
            hotel_dir.name
        )

        print(
            f"\nHotel {hotel_dir.name}: "
            f"{len(selected)} selected images"
        )

        if not selected:
            print(
                f"[Skip] No selected images for "
                f"Hotel {hotel_dir.name}"
            )
            continue

        upscaled_dir = upscale_hotel(
            hotel_dir,
            selected
        )

        # --------------------------------------------------
        # 2. UPSCALED → ORIGINAL RENDER PATH
        # --------------------------------------------------

        prepare_render_images(
            hotel_dir,
            upscaled_dir
        )

    # ------------------------------------------------------
    # 3. AUTOMATIC RENDER
    # ------------------------------------------------------

    print("\n========================================")
    print("UPSCALING COMPLETE")
    print("Starting automatic render...")
    print("========================================\n")

    subprocess.run(
        [
            sys.executable,
            "main.py",
        ],
        check=True
    )


if __name__ == "__main__":
    main()