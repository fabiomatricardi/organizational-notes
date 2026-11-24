"""
Generate the narration for the tutorial with Microsoft Edge TTS.

Voice: en-US-BrianNeural (US, male, conversational). No API key: Edge TTS is the
same service the Edge browser uses for Read Aloud.

    uvx --from edge-tts edge-tts --list-voices

Usage (from the video/ directory):

    uv run --with edge-tts python tools/build_audio.py
    uv run --with edge-tts python tools/build_audio.py --only idea

Output: video/public/audio/*.mp3, one clip per beat, so each line is placed at
the frame where its visual appears. The script also measures every clip against
its window and warns before a line can overlap the next beat.

The narration text lives in src/narration.json — the spoken words, written to be
heard rather than read, so they are allowed to differ from the on-screen lines.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # video/
NARRATION = ROOT / "src" / "narration.json"
OUT = ROOT / "public" / "audio"

# Budgets in seconds, matching src/script.ts and Video.tsx placement.
BUDGET = {
    "intro": 4.2,
    "lead": 4.8,
    "step": 4.9,
    "lands": 4.4,
    "outro": 8.7,
}

STAMP = re.compile(r"(\d\d):(\d\d):(\d\d),(\d\d\d)")


def srt_seconds(path: Path) -> float | None:
    """End time of the last subtitle line — the speech end."""
    if not path.is_file():
        return None
    stamps = STAMP.findall(path.read_text(encoding="utf-8", errors="ignore"))
    if not stamps:
        return None
    h, m, s, ms = (int(x) for x in stamps[-1])
    return h * 3600 + m * 60 + s + ms / 1000


def synth(voice: str, text: str, mp3: Path) -> float | None:
    srt = mp3.with_suffix(".srt")
    mp3.parent.mkdir(parents=True, exist_ok=True)

    if shutil.which("uvx"):
        base = ["uvx", "--from", "edge-tts", "edge-tts"]
    else:
        base = [sys.executable, "-m", "edge_tts"]

    cmd = [
        *base,
        "--voice", voice,
        "--text", text,
        "--write-media", str(mp3),
        "--write-subtitles", str(srt),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    seconds = srt_seconds(srt)
    srt.unlink(missing_ok=True)
    return seconds


def jobs(data: dict):
    yield "intro", data["intro"], "intro"
    for sid, block in data["scenes"].items():
        yield f"{sid}-lead", block["lead"], "lead"
        for i, line in enumerate(block["steps"], start=1):
            yield f"{sid}-step-{i:02d}", line, "step"
        yield f"{sid}-lands", block["lands"], "lands"
    yield "outro", data["outro"], "outro"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="generate one clip by name, e.g. idea-lead")
    args = parser.parse_args()

    data = json.loads(NARRATION.read_text(encoding="utf-8"))
    voice = data["voice"]
    out_of_budget = []

    print(f"voice  {voice}")
    for name, text, kind in jobs(data):
        if args.only and args.only != name:
            continue
        mp3 = OUT / f"{name}.mp3"
        seconds = synth(voice, text, mp3)
        budget = BUDGET[kind]
        flag = "ok "
        if seconds is None:
            flag = "?? "
        elif seconds > budget:
            flag = "LONG"
            out_of_budget.append((name, seconds, budget))
        shown = f"{seconds:4.1f}s" if seconds is not None else "  ?  "
        print(f"  {flag} {name:18s} {shown} / {budget:4.1f}s  {text[:52]}")
        if seconds is None:
            out_of_budget.append((name, 0.0, budget))

    print(f"\n{len(out_of_budget)} clip(s) over budget")
    return 1 if out_of_budget else 0


if __name__ == "__main__":
    raise SystemExit(main())
