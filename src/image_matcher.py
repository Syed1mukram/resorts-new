from pathlib import Path
from collections import deque
from typing import Optional, List, Tuple

import torch
import open_clip
from PIL import Image

from src.utils import (
    get_images,
    log,
)


class ImageMatcher:

    def __init__(self):

        self.last_scene = None
        log("Loading CLIP model...")

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model, _, self.preprocess = (
            open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="laion2b_s34b_b79k"
            )
        )

        self.model = (
            self.model
            .to(self.device)
            .eval()
        )

        self.tokenizer = open_clip.get_tokenizer(
            "ViT-B-32"
        )

        # Indexed images
        self.image_data = []

        # Prevent recent duplicates
        
        self.current_image_folder = None

        self.recent_images = deque(
            maxlen=15
        )

        # Prevent reuse until every image
        # has been shown once
        self.used_images = set()

    # ---------------------------------------------------------

    @torch.no_grad()
    def index_images(
        self,
        image_folder: Path
    ):

        self.current_image_folder = Path(image_folder)

        self.image_data.clear()
        self.recent_images.clear()
        self.used_images.clear()

        images = get_images(image_folder)

        log(
            f"Indexing {len(images)} images..."
        )

        for image_path in images:

            try:

                image = (
                    Image.open(image_path)
                    .convert("RGB")
                )

                tensor = (
                    self.preprocess(image)
                    .unsqueeze(0)
                    .to(self.device)
                )

                feature = self.model.encode_image(
                    tensor
                )

                feature = (
                    feature
                    / feature.norm(
                        dim=-1,
                        keepdim=True
                    )
                )

                self.image_data.append({

                    "path": image_path,

                    "feature": feature.cpu()

                })

            except Exception as e:

                log(
                    f"Skipped {image_path.name}: {e}"
                )

        self.image_data.sort(
            key=lambda x: x["path"].name.lower()
        )

        log(
            f"Indexed {len(self.image_data)} images."
        )

    # ---------------------------------------------------------

    @torch.no_grad()
    def _encode_text(
        self,
        text: str
    ):

        tokens = self.tokenizer(
            [text]
        ).to(self.device)

        feature = self.model.encode_text(
            tokens
        )

        feature = (
            feature
            / feature.norm(
                dim=-1,
                keepdim=True
            )
        )

        return feature.cpu()
    # ---------------------------------------------------------

    @torch.no_grad()
    def find_top_k(
        self,
        text: str,
        k: int = 10,
        min_score: float = 0.15,
        allow_recent: bool = False,
    ) -> List[Tuple[Path, float]]:

        if not self.image_data:
            return []

        text_feature = self._encode_text(text)

        candidates = []

        for item in self.image_data:

            image_path = item["path"]

            if (
                not allow_recent
                and image_path in self.recent_images
            ):
                continue

            score = float(

                (
                    text_feature
                    @ item["feature"].T
                ).item()

            )

            if score < min_score:
                continue

            candidates.append(

                (
                    image_path,
                    score
                )

            )

        if (
            not candidates
            and
            not allow_recent
        ):

            return self.find_top_k(

                text=text,

                k=k,

                min_score=min_score,

                allow_recent=True,

            )

        candidates.sort(

            key=lambda x: x[1],

            reverse=True

        )

        return candidates[:k]
    # ---------------------------------------------------------

    @torch.no_grad()
    def find_best(
        self,
        prompt: str,
        scene: str = "general"

    ):

        intro_image = None

        for ext in [".avif", ".webp", ".jpg", ".jpeg", ".png"]:
            p = self.current_image_folder / f"intro{ext}"
            if p.exists():
                intro_image = p
                break

        print("USED:", len(self.used_images))
        print("INTRO:", intro_image)

        if (
            not self.used_images
            and intro_image
        ):
            self.used_images.add(intro_image)
            self.recent_images.append(intro_image)
            self.last_scene = scene
            return intro_image, 1.0
    
        if not self.image_data:
            return None

        if not self.image_data:
            return None

        if len(self.used_images) >= len(self.image_data):
            self.used_images.clear()

        candidates = self.find_top_k(
            text=prompt,
            k=20,
            min_score=0.12
        )

        if not candidates:
            return None

        # Same scene -> don't change image if possible
        if scene == self.last_scene:

            for image_path, score in candidates:

                if image_path in self.recent_images:

                    return image_path, score

        available = [

            c for c in candidates

            if c[0] not in self.used_images

        ]

        if not available:
           available = candidates

        image_path, score = available[0]

        self.used_images.add(image_path)
        self.recent_images.append(image_path)

        self.last_scene = scene

        return image_path, score

    # ---------------------------------------------------------

    def mark_used(
        self,
        image_path
    ):

        self.used_images.add(
            image_path
        )

        self.recent_images.append(
            image_path
        )
    # ---------------------------------------------------------

    def reset(self):

        self.used_images.clear()

        self.recent_images.clear()

    # ---------------------------------------------------------

    def image_count(self):

        return len(
            self.image_data
        )

    # ---------------------------------------------------------

    def all_images(self):

        return [

            item["path"]

            for item in self.image_data

        ]

    # ---------------------------------------------------------

    def is_recent(
        self,
        image_path
    ):

        return (
            image_path
            in self.recent_images
        )

    # ---------------------------------------------------------

    def debug(
        self,
        text,
        top=10
    ):

        print()
        print("-" * 60)
        print("TEXT :", text)
        print("-" * 60)

        results = self.find_top_k(

            text,

            k=top,

            allow_recent=True

        )

        if not results:

            print("No matches.")
            return

        for index, (

            image,

            score

        ) in enumerate(

            results,

            start=1

        ):

            print(

                f"{index:02d}. "

                f"{image.name:<45}"

                f"{score:.4f}"

            )

        print("-" * 60)


# ---------------------------------------------------------

if __name__ == "__main__":

    matcher = ImageMatcher()

    matcher.index_images(
        IMAGES_DIR
    )

    print()
    print("-" * 60)
    print(
        f"Indexed Images : {matcher.image_count()}"
    )
    print("-" * 60)

    while True:

        text = input(
            "\nSearch : "
        ).strip()

        if not text:
            break

        matcher.debug(
            text,
            top=10
        )

        result = matcher.find_best(
            text
        )

        if result:

            image,
            score = result

            print()
            print(
                "Selected :",
                image.name
            )
            print(
                f"Score : {score:.4f}"
            )