from pathlib import Path
import shutil
import subprocess

from src.image_builder import ImageBuilder
from src.video_builder import VideoBuilder


class Renderer:

    def __init__(self):

        self.images = ImageBuilder()
        self.videos = VideoBuilder()

        self.temp_dir = Path("output/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------

    def _clean(self):

        if self.temp_dir.exists():

            shutil.rmtree(self.temp_dir)

        self.temp_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # ---------------------------------------------------------

    def _build(self, timeline):

        clips = []

        for i, item in enumerate(timeline):

            clip = self.temp_dir / f"{i:04d}.mp4"

            duration = float(item["duration"])

            if item["media_type"] == "image":

                self.images.build(
                    item["media"],
                    clip,
                    duration
                )

            else:

                self.videos.build(
                    item["media"],
                    clip,
                    duration
                )

            clips.append(clip)

        return clips
    # ---------------------------------------------------------

    def _concat_file(self, clips):

        concat = self.temp_dir / "concat.txt"

        with open(concat, "w", encoding="utf-8") as f:

            for clip in clips:

                f.write(
                    f"file '{clip.resolve().as_posix()}'\n"
                )

        return concat

    # ---------------------------------------------------------

    def render(

        self,
        timeline,
        audio_file,
        output_file,
        hotel_number=None,
        test_duration=None,
    ):

        self._clean()

        clips = self._build(timeline)

        concat = self._concat_file(clips)

        output_file = Path(output_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # ---------------------------------------------------------
        # Optional 5-second hotel title
        # ---------------------------------------------------------
        title_file = Path(audio_file).parent.parent.parent / "title.txt"

        hotel_name = f"Hotel {hotel_number or ''}".strip()
        
        if title_file.exists():
            lines = title_file.read_text(encoding="utf-8").splitlines()

            for line in lines:
                line = line.strip()

                if "|" in line:
                    num, name = line.split("|", 1)

                    if num.strip() == str(hotel_number):
                        hotel_name = name.strip()
                        break

        font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

        def esc(value):
            return (
                str(value)
                .replace("\\", "\\\\")
                .replace(":", "\\:")
                .replace("'", "\\'")
                .replace(",", "\\,")
            )

        title_filter = (
            # BLUE VERTICAL LINE
            "drawbox="
            "x=60:"
            "y=h-280:"
            "w=6:"
            "h=140:"
            "color=19B5FE:"
            "t=fill:"
            "enable='between(t,0,5.25)',"

            # NO. 1 TEXT + LIGHT BLACK BOX
            f"drawtext=fontfile='{font}':"
            f"text='NO. {esc(hotel_number or '')}':"
            "x=88:"
            "y=h-270:"
            "fontsize=60:"
            "fontcolor=FFFFFF:"
            "bordercolor=000000@0.45:"
            "borderw=2:"
            "box=1:"
            "boxcolor=07131C@0.55:"
            "boxborderw=8:"
            "enable='between(t,0,5.25)':"
            "alpha='if(lt(t,0.25),t/0.25,if(gt(t,5),(5.25-t)/0.25,1))',"

            # HOTEL NAME + LIGHT BLACK BOX
            f"drawtext=fontfile='{font}':"
            f"text='{esc(hotel_name.upper())}':"
            "x=92:"
            "y=h-200:"
            "fontsize=75:"
            "fontcolor=FFD21F:"
            "bordercolor=000000@0.50:"
            "borderw=2:"
            "box=1:"
            "boxcolor=07131C@0.55:"
            "boxborderw=10:"
            "enable='between(t,0,5.25)':"
            "alpha='if(lt(t,0.25),t/0.25,if(gt(t,5),(5.25-t)/0.25,1))'"
        )
        cmd = [

            "ffmpeg",

            "-y",

            "-f",
            "concat",

            "-safe",
            "0",

            "-i",
            str(concat),

            "-i",
            str(audio_file),

            "-vf",
            title_filter,
            "-map",
            "0:v:0",

            "-map",
            "1:a:0",

            "-c:v",
            "h264_nvenc",

            "-preset",
            "medium",

            "-cq",
            "22",

            "-pix_fmt",
            "yuv420p",

            "-r",
            "30",

            "-vsync",
            "cfr",

            "-c:a",
            "aac",

            "-b:a",
            "192k",

            "-ar",
            "48000",

            "-movflags",
            "+faststart",

            str(output_file)

        ]

        if test_duration is not None:
            cmd.insert(cmd.index("-c:v"), "-t")
            cmd.insert(cmd.index("-c:v"), f"{test_duration:.3f}")

        subprocess.run(
            cmd,
            check=True
        )
        print("\n----------------------------------------")
        print("Cleaning temporary files...")
        print("----------------------------------------")

        # try:
        #     shutil.rmtree(self.temp_dir)
        # except Exception:
        #     pass

        print("\n----------------------------------------")
        print("Render Complete")
        print("----------------------------------------")
        print(f"Output : {output_file}")

        return output_file