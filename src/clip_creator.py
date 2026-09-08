import random

from moviepy import ImageClip
from moviepy.video.fx.Crop import Crop


WIDTH = 1920
HEIGHT = 1080
FPS = 30


def create_clip(image_path, output_path, duration):

    mode = random.choice([
        "zoom_in",
        "zoom_out",
       ])

    clip = (
        ImageClip(str(image_path))
        .resized(width=int(WIDTH * 1.25))
        .with_duration(duration)
        .with_fps(FPS)
    )

    if mode == "zoom_in":

        clip = clip.resized(
            lambda t: 1.00 + 0.05 * (t / duration)
        )

    elif mode == "zoom_out":

        clip = clip.resized(
            lambda t: 1.05 - 0.05 * (t / duration)
        )

    elif mode == "left":

        clip = clip.with_position(
            lambda t: (
                -120 * (t / duration),
                "center"
            )
        )

    elif mode == "right":

        clip = clip.with_position(
            lambda t: (
                120 * (t / duration),
                "center"
            )
        )

    clip = clip.with_effects([
        Crop(
            width=WIDTH,
            height=HEIGHT,
            x_center=clip.w / 2,
            y_center=clip.h / 2
        )
    ])

    clip.write_videofile(
        str(output_path),
        codec="libx264",
        fps=FPS,
        audio=False,
        preset="medium"
    )

    clip.close()