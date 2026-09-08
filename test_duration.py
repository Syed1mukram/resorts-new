from pathlib import Path
import subprocess

total = 0.0

for clip in sorted(Path("output/temp").glob("clip_*.mp4")):

    d = float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(clip),
            ]
        ).decode().strip()
    )

    total += d
    print(f"{clip.name:15} {d:.3f}")

print("-" * 40)
print(f"TOTAL : {total:.3f} sec")