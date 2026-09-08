from PIL import Image
from src.camera import Camera
from pathlib import Path
import random
import subprocess

import cv2
import numpy as np

from config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    FPS,
    CRF,
    PRESET,
)


class ImageBuilder:

    def __init__(self):

        self.camera = Camera()

        # Motion strength
        self.zoom_amount = 0.08      # 8%
        self.pan_amount = 0.06       # 6%

    # ---------------------------------------------------------

    def _cover_resize(self, image):

        h, w = image.shape[:2]

        scale = max(
            VIDEO_WIDTH / w,
            VIDEO_HEIGHT / h
        )

        nw = int(np.ceil(w * scale * 1.12))
        nh = int(np.ceil(h * scale * 1.12))

        image = cv2.resize(
            image,
            (nw, nh),
            interpolation=cv2.INTER_LANCZOS4
        )

        return image

    # ---------------------------------------------------------

    def _ease(self, t):

        # Smoothstep easing
        return t * t * (3.0 - 2.0 * t)

    # ---------------------------------------------------------

    def _motion(self):

        return random.choice([
            "zoom_in",
            "zoom_out",
            "left",
            "right",
        ])

    # ---------------------------------------------------------

    def _camera(
        self,
        img_w,
        img_h,
        t,
        motion
    ):

        x_max = img_w - VIDEO_WIDTH
        y_max = img_h - VIDEO_HEIGHT

        x = x_max / 2.0
        y = y_max / 2.0

        if motion == "left":

            x = x_max * (1.0 - t)

        elif motion == "right":

            x = x_max * t

        elif motion == "up":

            y = y_max * (1.0 - t)

        elif motion == "down":

            y = y_max * t

        return (
            float(x),
            float(y)
        )
    # ---------------------------------------------------------

    def build(
        self,
        image_path,
        output_path,
        duration
    ):


        try:

            pil = Image.open(image_path).convert("RGB")

            image = cv2.cvtColor(
                np.array(pil),
                cv2.COLOR_RGB2BGR
            )

        except Exception as e:

           raise RuntimeError(
               f"Cannot read image : {image_path}\n{e}"
           )

        image = self._cover_resize(image)

        writer = cv2.VideoWriter(

            str(output_path),

            cv2.VideoWriter_fourcc(*"mp4v"),

            FPS,

            (
                VIDEO_WIDTH,
                VIDEO_HEIGHT
            )

        )

        frame_count = max(
            1,
            int(np.ceil(duration * FPS))
        )

        motion = self._motion()

        img_h, img_w = image.shape[:2]

        for frame_no in range(frame_count):

            progress = frame_no / max(frame_count - 1, 1)

            frame = self.camera.render(
                image=image,
                progress=progress,
                motion=motion,
                out_width=VIDEO_WIDTH,
                out_height=VIDEO_HEIGHT,

            )

            writer.write(frame)

        writer.release()
        temp_output = Path(output_path).with_suffix(".x264.mp4")

        cmd = [

            "ffmpeg",

            "-y",

            "-i",
            str(output_path),

            "-c:v",
            "h264_nvenc",

            "-preset",
            PRESET,

            "-cq",
            str(CRF),

            "-pix_fmt",
            "yuv420p",

            "-r",
            str(FPS),

            "-movflags",
            "+faststart",

            "-an",

            str(temp_output)

        ]

        subprocess.run(
            cmd,
            check=True
        )

        Path(output_path).unlink(
            missing_ok=True
        )

        temp_output.rename(
            output_path
        )