import random

import cv2
import numpy as np


class Camera:

    def __init__(self):

        self.zoom_strength = 0.04
        self.pan_strength = 0.02

    # -----------------------------------------------------

    def ease(self, t):

        return t * t * (2.0 - 1.0 * t)

    # -----------------------------------------------------

    def random_motion(self):

        return random.choice([

            "zoom_in",

            "zoom_out",

            "left",

            "right",

            "up",

            "down",

        ])

    # -----------------------------------------------------

    def get_transform(

        self,

        progress,

        motion,

        img_width,

        img_height,

        out_width,

        out_height,

    ):

        progress = self.ease(progress)

        zoom = 1.0

        if motion == "zoom_in":

            zoom = 1.0 + (
                self.zoom_strength * progress
            )

        elif motion == "zoom_out":

            zoom = (
                1.0 + self.zoom_strength
            ) - (
                self.zoom_strength * progress
            )

        max_x = max(
            0.0,
            img_width - out_width
        )

        max_y = max(
            0.0,
            img_height - out_height
        )

        tx = max_x / 2.0
        ty = max_y / 2.0

        if motion == "left":

            tx = max_x * (1.0 - progress) * 0.85

        elif motion == "right":

            tx = max_x * progress * 0.85

        elif motion == "up":

            ty = max_y * (1.0 - progress)

        elif motion == "down":

            ty = max_y * progress

        return (

            float(tx),

            float(ty),

            float(zoom)

        )
    # -----------------------------------------------------

    def render(
        self,
        image,
        progress,
        motion,
        out_width,
        out_height,
    ):

        img_h, img_w = image.shape[:2]

        tx, ty, zoom = self.get_transform(
            progress,
            motion,
            img_w,
            img_h,
            out_width,
            out_height,
        )

        # Add padding to avoid mirror at edges
        pad = 300

        image = cv2.copyMakeBorder(
            image,
            pad,
            pad,
            pad,
            pad,
            borderType=cv2.BORDER_REPLICATE,
        )

        img_h, img_w = image.shape[:2]

        # Shift translation because of padding
        tx += pad
        ty += pad

        # Image center
        cx = img_w * 0.5
        cy = img_h * 0.5

        # Camera translation
        dx = tx - (img_w - out_width) / 2.0
        dy = -(ty - (img_h - out_height) / 2.0)

        # Affine matrix
        M = np.array(
            [
                [zoom, 0.0, (1.0 - zoom) * cx + dx],
                [0.0, zoom, (1.0 - zoom) * cy + dy],
            ],
            dtype=np.float32,
        )

        frame = cv2.warpAffine(
            image,
            M,
            (img_w, img_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

        # Center crop
        crop_x = (img_w - out_width) // 2
        crop_y = (img_h - out_height) // 2

        frame = frame[
            crop_y:crop_y + out_height,
            crop_x:crop_x + out_width,
        ]

        return frame