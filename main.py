from pathlib import Path

from config import VOICE_FILE, ORIGINAL_IMAGES_DIR, OUTPUT_VIDEO
from src.timeline_builder import TimelineBuilder
from src.renderer import Renderer


def main():

    print("========================================")
    print("HOTEL REVIEW PIPELINE")
    print("========================================")

    print(f"Voice: {VOICE_FILE}")
    print(f"Images: {ORIGINAL_IMAGES_DIR}")
    print(f"Output: {OUTPUT_VIDEO}")

    if not VOICE_FILE.exists():
        raise FileNotFoundError(
            f"Voice file not found: {VOICE_FILE}"
        )

    if not ORIGINAL_IMAGES_DIR.exists():
        raise FileNotFoundError(
            f"Images folder not found: {ORIGINAL_IMAGES_DIR}"
        )

    # -----------------------------------------------------
    # BUILD TIMELINE
    # -----------------------------------------------------

    builder = TimelineBuilder(
        audio_file=VOICE_FILE,
        images_dir=ORIGINAL_IMAGES_DIR,
    )

    timeline = builder.build()

    print(
        f"\nTimeline items: {len(timeline)}"
    )

    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    renderer = Renderer()

    renderer.render(
        timeline=timeline,
        output=OUTPUT_VIDEO,
    )

    print("\n========================================")
    print("DONE")
    print("========================================")
    print(f"Final video: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    main()