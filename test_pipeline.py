
from pathlib import Path

from src.timeline_builder import TimelineBuilder
from src.renderer import Renderer
from config import AUDIO_FILE, OUTPUT_VIDEO


def main():

    print("=" * 50)
    print("Pipeline Test")
    print("=" * 50)

    builder = TimelineBuilder()
    timeline = builder.build()

    print(f"Timeline items : {len(timeline)}")

    for i, item in enumerate(timeline[:10]):
        print(
            f"{i+1:02d}. "
            f"{item['media_type']} | "
            f"{Path(item['media']).name} | "
            f"{item['start']:.2f} -> {item['end']:.2f}"
        )

    print("\nRendering...\n")

    renderer = Renderer()
    renderer.render(
        timeline,
        AUDIO_FILE,
        OUTPUT_VIDEO
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
