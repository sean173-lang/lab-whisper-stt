
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")
client = OpenAI()

# Context helps Whisper recognize relevant technical vocabulary.
CONTEXT_PROMPT = (
    "This is a business meeting about artificial intelligence, "
    "OpenAI, Python, API integration, and project deadlines."
)


def transcribe(audio_path, prompt=None):
    """Transcribe audio and return timestamped segments."""
    with open(audio_path, "rb") as audio_file:
        options = {
            "model": "whisper-1",
            "file": audio_file,
            "response_format": "verbose_json",
            "timestamp_granularities": ["segment"],
        }
        if prompt:
            options["prompt"] = prompt

        response = client.audio.transcriptions.create(**options)

    return [
        {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
        }
        for segment in response.segments
    ]


def split_audio(audio_path, minutes=10):
    """Split long recordings into manageable audio chunks."""
    audio = AudioSegment.from_file(audio_path)
    chunk_length = int(minutes * 60 * 1000)
    chunks = []

    for index, start in enumerate(range(0, len(audio), chunk_length)):
        chunk = audio[start:start + chunk_length]
        path = OUTPUT_DIR / f"chunk_{index:03d}.mp3"
        chunk.export(path, format="mp3", bitrate="128k")
        chunks.append((path, start / 1000))

    return chunks


def transcribe_chunks(audio_path, prompt=None, minutes=10):
    """Transcribe chunks and correct timestamps using chunk offsets."""
    combined = []

    for path, offset in split_audio(audio_path, minutes):
        print(f"Transcribing {path.name}...")
        segments = transcribe(path, prompt)

        for segment in segments:
            combined.append({
                "start": round(segment["start"] + offset, 2),
                "end": round(segment["end"] + offset, 2),
                "text": segment["text"],
            })

    return combined


def timestamp(seconds, srt=False):
    """Format seconds as HH:MM:SS.mmm or SRT timestamps."""
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    secs, ms = divmod(remainder, 1000)

    separator = "," if srt else "."
    return f"{hours:02}:{minutes:02}:{secs:02}{separator}{ms:03}"


def export_results(segments, name):
    """Export a transcription in JSON, TXT, and SRT formats."""
    json_path = OUTPUT_DIR / f"{name}.json"
    txt_path = OUTPUT_DIR / f"{name}.txt"
    srt_path = OUTPUT_DIR / f"{name}.srt"

    json_path.write_text(
        json.dumps(segments, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    with txt_path.open("w", encoding="utf-8") as file:
        for segment in segments:
            file.write(
                f"[{timestamp(segment['start'])}] "
                f"{segment['text']}\n"
            )

    with srt_path.open("w", encoding="utf-8") as file:
        for index, segment in enumerate(segments, 1):
            file.write(
                f"{index}\n"
                f"{timestamp(segment['start'], True)} --> "
                f"{timestamp(segment['end'], True)}\n"
                f"{segment['text']}\n\n"
            )

    print(f"Exported {name}: JSON, TXT, SRT")


def main():
    files = [
        path for path in AUDIO_DIR.iterdir()
        if path.suffix.lower() in (".mp3", ".wav", ".m4a")
    ]

    if not files:
        print("No audio found. Add an MP3, WAV, or M4A to audio/")
        return

    audio_path = files[0]
    print(f"Processing: {audio_path.name}")

    print("\n1. Unguided transcription")
    unguided = transcribe(audio_path)
    export_results(unguided, "unguided")

    print("\n2. Guided transcription")
    guided = transcribe(audio_path, CONTEXT_PROMPT)
    export_results(guided, "guided")

    print("\n3. Chunked transcription")
    chunked = transcribe_chunks(audio_path, CONTEXT_PROMPT, minutes=0.1)
    export_results(chunked, "chunked")

    print("\n4. Comparison")
    unguided_text = " ".join(s["text"] for s in unguided)
    guided_text = " ".join(s["text"] for s in guided)

    comparison = (
        "UNGUIDED:\n" + unguided_text
        + "\n\nGUIDED:\n" + guided_text
    )

    (OUTPUT_DIR / "comparison.txt").write_text(
        comparison, encoding="utf-8"
    )

    print(comparison)
    print("\nAll transcription tasks completed!")


if __name__ == "__main__":
    main()
