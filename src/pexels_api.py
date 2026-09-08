from pathlib import Path
from collections import deque
import hashlib
import requests

from config import (
    PEXELS_API_KEY,
    STOCK_DIR,
)

from src.utils import log


SEARCH_URL = "https://api.pexels.com/videos/search"


class PexelsAPI:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({

            "Authorization": PEXELS_API_KEY

        })

        Path(STOCK_DIR).mkdir(
            parents=True,
            exist_ok=True
        )

        # Recently used videos
        self.used = deque(maxlen=50)

    # -----------------------------------------------------

    def _key(self, url):

        return hashlib.md5(

            url.encode("utf8")

        ).hexdigest()

    # -----------------------------------------------------

    def search(

        self,

        query,

        per_page=10,

    ):

        response = self.session.get(

            SEARCH_URL,

            params={

                "query": query,

                "per_page": per_page,

                "orientation": "landscape",

            },

            timeout=30,

        )

        response.raise_for_status()

        return response.json().get(

            "videos",

            []

        )
    # -----------------------------------------------------

    def best_video(

        self,

        query,

    ):

        videos = self.search(query)

        if not videos:
            return None

        # Prefer videos that have not been used recently
        for video in videos:

            files = video.get(
                "video_files",
                []
            )

            if not files:
                continue

            best = max(
                files,
                key=lambda f: f.get(
                    "width",
                    0
                )
            )

            url = best.get("link")

            if not url:
                continue

            key = self._key(url)

            if key in self.used:
                continue

            self.used.append(key)

            return {

                "id": video.get("id"),

                "url": url,

            }
        # -----------------------------------------
        # All recent videos already used.
        # Don't repeat them.
        # Let TimelineBuilder use an image instead.
        # -----------------------------------------

        return None

    # -----------------------------------------------------

    def download(

        self,

        query,

    ):

        video = self.best_video(query)

        if video is None:
            return None

        url = video["url"]

        filename = (

            str(video["id"])

            + ".mp4"

        )

        output = Path(

            STOCK_DIR

        ) / filename

        if output.exists():

            return output

        log(f"Downloading : {query}")

        response = self.session.get(

            url,

            stream=True,

            timeout=60,

        )

        response.raise_for_status()

        with open(output, "wb") as f:

            for chunk in response.iter_content(
                1024 * 1024
            ):

                if chunk:

                    f.write(chunk)

        return output
# -----------------------------------------------------

if __name__ == "__main__":

    api = PexelsAPI()

    query = "luxury beach resort"

    result = api.download(query)

    print("-" * 60)

    if result:

        print("Downloaded :", result)

    else:

        print("No video found.")

    print("-" * 60)