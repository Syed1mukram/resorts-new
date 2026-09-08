from pathlib import Path

from faster_whisper import WhisperModel

from config import (
    WHISPER_MODEL,
    LANGUAGE,
)

from src.utils import log


MIN_SEGMENT = 1.8
MAX_SEGMENT = 3.2


class TranscriptGenerator:

    def __init__(self):

        log(
            f"Loading Whisper model: {WHISPER_MODEL}"
        )

        self.model = WhisperModel(

            WHISPER_MODEL,

            device="cpu",

            compute_type="int8",

        )

    # -----------------------------------------------------

    def _make_chunk(

        self,

        words,

        start,

        end,

    ):

        return {

            "start": float(start),

            "end": float(end),

            "duration": float(end - start),

            "text": " ".join(

                w.word.strip()

                for w in words

            ).strip(),

        }

    # -----------------------------------------------------

    def _split_segment(

        self,

        segment,

    ):

        words = segment.words or []

        duration = float(
            segment.end - segment.start
        )

        if (
            not words
            or duration <= MAX_SEGMENT
        ):

            return [
                {
                    "start": float(segment.start),
                    "end": float(segment.end),
                    "duration": duration,
                    "text": segment.text.strip(),
                }
            ]

        chunks = []

        current = []

        current_start = float(words[0].start)

        for word in words:

            current.append(word)

            elapsed = float(
                word.end - current_start
            )

            split = False

            if word.word.strip().endswith(
                (".", "!", "?")
            ):
                split = True

            elif elapsed >= 3.0:
                split = True

            if split:

                chunks.append(

                    self._make_chunk(

                        current,

                        current_start,

                        float(word.end),

                    )

                )

                current = []

                if word != words[-1]:
                    current_start = float(word.end)

        if current:

            chunks.append(

                self._make_chunk(

                    current,

                    current_start,

                    float(words[-1].end),

                )

            )

        # Merge very short chunks
        merged = []

        for chunk in chunks:

            if (
                merged
                and chunk["duration"] < MIN_SEGMENT
            ):

                merged[-1]["end"] = chunk["end"]
                merged[-1]["duration"] = (
                    merged[-1]["end"] - merged[-1]["start"]
                )
                merged[-1]["text"] += " " + chunk["text"]

            else:

                merged.append(chunk)

        return merged

    # -----------------------------------------------------

    def transcribe(
        self,
        audio_file: Path
    ):

        segments, info = self.model.transcribe(

            str(audio_file),

            language=LANGUAGE,

            vad_filter=False,

            beam_size=5,

            word_timestamps=True,

            condition_on_previous_text=True,

        )

        results = []

        for segment in segments:

            parts = self._split_segment(
                segment
            )

            for part in parts:

                if (
                    part["duration"] >= MIN_SEGMENT
                    and part["text"].strip()
                ):
                    results.append(part)

                    print(
                        f"{part['start']:.2f} -> "
                        f"{part['end']:.2f} | "
                        f"{part['duration']:.2f} | "
                        f"{part['text']}"
                    )

        log(
            f"Language : {info.language}"
        )

        log(
            f"Segments : {len(results)}"
        )

        if results:

            log(
                f"Transcript End : "
                f"{results[-1]['end']:.2f} sec"
            )

        return results


# -----------------------------------------------------

if __name__ == "__main__":

    from config import AUDIO_FILE

    generator = TranscriptGenerator()

    transcript = generator.transcribe(
        AUDIO_FILE
    )

    print("-" * 70)

    for item in transcript:

        print(

            f"[{item['start']:7.2f} - {item['end']:7.2f}]",

            item["text"]

        )

    print("-" * 70)

    if transcript:

        print(

            "Last Timestamp :",

            transcript[-1]["end"]

        )