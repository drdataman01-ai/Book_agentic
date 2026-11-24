#!/usr/bin/env python3
"""Turn the Chapter 1 narration script into one audio file per slide.

Usage
-----
Google Cloud Text-to-Speech (natural voices, recommended):
    pip install google-cloud-texttospeech
    gcloud auth application-default login
    gcloud services enable texttospeech.googleapis.com
    python make_narration_audio.py Chapter_1_narration_script.txt --engine google

macOS built-in voices (free, offline, lower quality):
    python make_narration_audio.py Chapter_1_narration_script.txt --engine mac

Check the slide split without making any audio:
    python make_narration_audio.py Chapter_1_narration_script.txt --dry-run

Output goes to ./audio_ch01/: slide01.mp3, slide02.mp3, ... and, if ffmpeg
is installed, chapter01_full.mp3 with all slides joined in order.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def read_slides(path):
    """Split the script file on its '=== Slide N ... ===' headers."""
    text = Path(path).read_text(encoding="utf-8")
    parts = re.split(r"^=== Slide (\d+)[^\n]*===\s*$", text, flags=re.M)
    slides = []
    for i in range(1, len(parts), 2):
        body = parts[i + 1].strip()
        if body:
            slides.append((int(parts[i]), body))
    return slides


def synth_google(text, out_path, voice, rate):
    from google.cloud import texttospeech as tts
    client = tts.TextToSpeechClient()
    # Text-to-Speech accepts up to 5,000 bytes per request; every slide in
    # this script is well under that, but split on paragraphs just in case.
    chunks, cur = [], ""
    for para in text.split("\n\n"):
        if len((cur + "\n\n" + para).encode()) > 4500 and cur:
            chunks.append(cur)
            cur = para
        else:
            cur = (cur + "\n\n" + para).strip()
    chunks.append(cur)
    audio = b""
    for chunk in chunks:
        resp = client.synthesize_speech(
            input=tts.SynthesisInput(text=chunk),
            voice=tts.VoiceSelectionParams(language_code=voice[:5], name=voice),
            audio_config=tts.AudioConfig(
                audio_encoding=tts.AudioEncoding.MP3, speaking_rate=rate),
        )
        audio += resp.audio_content
    out_path.write_bytes(audio)


def synth_mac(text, out_path, voice, rate):
    aiff = out_path.with_suffix(".aiff")
    words_per_min = str(int(175 * rate))
    subprocess.run(["say", "-v", voice, "-r", words_per_min, "-o", str(aiff), text],
                   check=True)
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff),
                        "-b:a", "128k", str(out_path)], check=True)
        aiff.unlink()
    else:  # afconvert ships with macOS; produce .m4a instead of .mp3
        m4a = out_path.with_suffix(".m4a")
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(aiff), str(m4a)],
                       check=True)
        aiff.unlink()
        return m4a
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--engine", choices=["google", "mac"], default="google")
    ap.add_argument("--voice", help="Google default: en-US-Chirp3-HD-Charon; "
                                    "mac default: Samantha")
    ap.add_argument("--rate", type=float, default=1.0,
                    help="speaking rate; 1.0 is normal, 0.9 is a little slower")
    ap.add_argument("--out", default="audio_ch01")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    slides = read_slides(args.script)
    if not slides:
        sys.exit("No '=== Slide N ===' sections found in the script.")
    for n, body in slides:
        print(f"slide {n:02d}: {len(body.split())} words")
    if args.dry_run:
        return

    voice = args.voice or ("en-US-Chirp3-HD-Charon" if args.engine == "google"
                           else "Samantha")
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    made = []
    for n, body in slides:
        target = out_dir / f"slide{n:02d}.mp3"
        print(f"Generating {target.name} ...", flush=True)
        if args.engine == "google":
            synth_google(body, target, voice, args.rate)
        else:
            target = synth_mac(body, target, voice, args.rate)
        made.append(target)

    if shutil.which("ffmpeg"):
        # Join all slides with one second of silence between them.
        listfile = out_dir / "concat.txt"
        silence = out_dir / "silence.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                        "-i", "anullsrc=r=24000:cl=mono", "-t", "1",
                        "-b:a", "128k", str(silence)], check=True)
        lines = []
        for f in made:
            lines += [f"file '{f.name}'", f"file '{silence.name}'"]
        listfile.write_text("\n".join(lines))
        full = out_dir / "chapter01_full.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
                        "-safe", "0", "-i", str(listfile), "-ar", "24000",
                        "-ac", "1", "-b:a", "128k", str(full)], check=True)
        listfile.unlink()
        silence.unlink()
        print(f"Full chapter: {full}")
    print(f"Done: {len(made)} slide files in {out_dir}/")


if __name__ == "__main__":
    main()
