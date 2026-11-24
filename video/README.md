# Tutorial video

The six scenes from [`docs/10-scenarios.md`](../docs/10-scenarios.md), rendered as a silent 16:9 video. Black, white and grey — the same paper as the print editions.

## Run it

```powershell
npm.cmd install
npm.cmd run render      # -> out/tutorial.mp4
npm.cmd run studio      # live editor for timing and layout
npm.cmd run still       # -> out/still.png, one frame
```

At the repository root, `.venv\Scripts\python.exe tools\build_print.py --only 10` builds the printable cards from the same script.

## Structure

```
src/
  script.ts    the six scenes: time, title, situation, steps, "not this", where it lands
  Video.tsx    the renderer: paper components, caption column, the six visuals
  Root.tsx     one composition, scene durations derived from the script
  index.ts     registerRoot
  theme.ts     colours and font stack
```

**Edit words in `script.ts` only.** Every beat is a pure function of the frame number, so the video is reproducible: same source, same MP4.

## Machine notes

- Remotion 4.0.546, React 19, Node 24.
- **Use the installed Chrome** — Remotion's own browser download fails behind the corporate TLS proxy with `unable to get local issuer certificate`. The npm scripts pass `--browser-executable="C:/Program Files/Google/Chrome/Application/chrome.exe"`.
- `out/` is gitignored. The MP4 is a build artefact: publish it as a release asset, not a commit.
- The marks `⇒`, `✓`, `✗` need the Segoe UI Symbol fallback in `theme.ts`. Check one frame after any font change.
