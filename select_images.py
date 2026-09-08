from pathlib import Path
from collections import OrderedDict

from src.transcript import TranscriptGenerator
from src.image_matcher import ImageMatcher


BASE_DIR = Path("input/images")

MIN_SCORE = 0.18
SAME_IMAGE_THRESHOLD = 0.08
RECENT_WINDOW = 2


def find_hotels():
    hotels = []

    if not BASE_DIR.exists():
        raise RuntimeError(f"Missing folder: {BASE_DIR}")

    for folder in BASE_DIR.iterdir():
        if not folder.is_dir():
            continue

        voice = folder / "voice.mp3"
        images = folder / "images"

        if voice.exists() and images.exists():
            hotels.append(folder)

    def sort_key(path):
        try:
            return (0, int(path.name))
        except ValueError:
            return (1, path.name.lower())

    return sorted(hotels, key=sort_key)


def select_hotel(hotel_dir):

    voice_file = hotel_dir / "voice.mp3"
    images_dir = hotel_dir / "images"

    print("\n" + "=" * 60)
    print(f"HOTEL {hotel_dir.name}")
    print("=" * 60)

    print("\n[1/3] Generating transcript...")

    transcript = TranscriptGenerator()
    segments = transcript.transcribe(voice_file)

    print("\n[2/3] Indexing images...")

    matcher = ImageMatcher()
    matcher.index_images(images_dir)

    print("\n[3/3] Selecting useful images...\n")

    selected = OrderedDict()
    recent_images = []
    last_image = None
    last_score = 0.0

    for segment in segments:

        text = segment["text"].strip()

        if not text:
            continue

        result = matcher.find_best(text)

        if not result:
            print(f"SKIP | {text}")
            continue

        image_path, score = result
        image_path = Path(image_path)
        score = float(score)

        if score < MIN_SCORE:
            print(
                f"SKIP WEAK | {image_path.name} "
                f"| {score:.3f} | {text}"
            )
            continue

        # Same image can continue naturally
        if image_path == last_image:
            print(
                f"CONTINUE | {image_path.name} "
                f"| {score:.3f} | {text}"
            )
            continue

        # Avoid unnecessary image changes when the new match
        # is only slightly better than the current image.
        if last_image is not None:
            score_difference = score - last_score

            if (
                score_difference < SAME_IMAGE_THRESHOLD
                and last_image not in recent_images
            ):
                print(
                    f"KEEP | {last_image.name} "
                    f"| current={score:.3f} "
                    f"| previous={last_score:.3f} "
                    f"| {text}"
                )
                continue

        # Avoid immediate repetition
        if image_path in recent_images:
            print(
                f"SKIP RECENT | {image_path.name} "
                f"| {score:.3f} | {text}"
            )
            continue

        selected[image_path] = {
            "score": score,
            "text": text,
            "start": float(segment["start"]),
            "end": float(segment["end"]),
        }

        last_image = image_path
        last_score = score

        recent_images.append(image_path)

        if len(recent_images) > RECENT_WINDOW:
            recent_images.pop(0)

        print(
            f"{len(selected):02d}. "
            f"{image_path.name} "
            f"| {score:.3f} "
            f"| {text}"
        )

    output_file = Path(
        f"selected_images_{hotel_dir.name}.txt"
    )

    with output_file.open("w", encoding="utf-8") as f:

        f.write(f"HOTEL {hotel_dir.name}\n")
        f.write("=" * 70 + "\n\n")

        for number, (image, data) in enumerate(
            selected.items(),
            start=1
        ):
            f.write(
                f"{number:02d} | "
                f"{image.name} | "
                f"score={data['score']:.3f} | "
                f"{data['start']:.2f}-{data['end']:.2f} | "
                f"{data['text']}\n"
            )

    print("\n----------------------------------------")
    print(f"Selected images : {len(selected)}")
    print(f"Saved           : {output_file}")
    print("----------------------------------------")


def main():

    hotels = find_hotels()

    if not hotels:
        raise RuntimeError("No hotel folders found.")

    print(f"Found {len(hotels)} hotel(s).")

    for hotel in hotels:
        select_hotel(hotel)

    print("\n========================================")
    print("IMAGE SELECTION COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()