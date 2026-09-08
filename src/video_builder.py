from pathlib import Path
import subprocess

from config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    FPS,
)


class VideoBuilder:

    def __init__(self):
        pass

    # ---------------------------------------------------------

    def build(
        self,
        video_path,
        output_path,
        duration
    ):

        vf = (

            f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:"

            f"force_original_aspect_ratio=increase,"

            f"crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},"

            f"fps={FPS}"

        )

        cmd = [

            "ffmpeg",

            "-y",

            "-stream_loop",
            "-1",

            "-i",
            str(video_path),

            "-t",
            f"{duration + 0.05:.3f}",
            "-vf",
            vf,

            "-an",

            "-c:v",
            "h264_nvenc",

            "-preset",
            "medium",

            "-cq",
            "18",

            "-pix_fmt",
            "yuv420p",

            "-r",
            str(FPS),

            "-movflags",
            "+faststart",

            str(output_path)

        ]

        subprocess.run(
            cmd,
            check=True
        )