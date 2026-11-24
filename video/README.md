# Tutorial video

The six scenes from [`docs/10-scenarios.md`](../docs/10-scenarios.md), rendered as a narrated 16:9 video. Black, white and grey — the same paper as the print editions.

## Run it

```powershell
npm.cmd install
npm.cmd run render      # -> out/tutorial.mp4
npm.cmd run studio      # live editor for timing and layout
npm.cmd run still       # -> out/still.png, one frame
```

At the repository root, `.venv\Scripts\python.exe tools\build_print.py --only 10` builds the printable cards from the same script.

## Audio

Narration is Microsoft Edge TTS, voice **en-US-BrianNeural**, one clip per beat, so each line starts on the frame where its visual appears.

```powershell
npm.cmd run audio       # regenerate public/audio/*.mp3
```

- The words live in `src/narration.json`: `intro`, one block per scene (`lead`, `steps[]`, `lands`), `outro`. They are written to be heard, so they differ from the on-screen text on purpose.
- `tools/build_audio.py` measures each clip against its window (lead 4.8 s, step 4.9 s, lands 4.4 s) and exits non-zero if a line would overlap the next beat.
- 35 MP3s, 0.8 MB, are committed — a fresh clone renders with sound and no network.
- No key, no account: Edge TTS is the browser's Read Aloud service. The script uses `uvx --from edge-tts` and falls back to `python -m edge_tts`.

## Structure

```
src/
  script.ts        the six scenes: time, title, situation, steps, "not this", where it lands
  narration.json   the spoken words, one block per scene
  Video.tsx        the renderer: paper components, caption column, the six visuals
  Root.tsx         one composition, scene durations derived from the script
  index.ts         registerRoot
  theme.ts         colours and font stack
tools/
  build_audio.py   Edge TTS generator + timing check
public/audio/      35 generated MP3s, committed
```

**Edit words in `script.ts` only.** Every beat is a pure function of the frame number, so the video is reproducible: same source, same MP4.

## Machine notes

- Remotion 4.0.546, React 19, Node 24.
- **Use the installed Chrome** — Remotion's own browser download fails behind the corporate TLS proxy with `unable to get local issuer certificate`. The npm scripts pass `--browser-executable="C:/Program Files/Google/Chrome/Application/chrome.exe"`.
- `out/` is gitignored. The MP4 is a build artefact: publish it as a release asset, not a commit.
- The marks `⇒`, `✓`, `✗` need the Segoe UI Symbol fallback in `theme.ts`. Check one frame after any font change.
