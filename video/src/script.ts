/**
 * The script.
 *
 * This is the single place the tutorial's content lives — the equivalent of
 * PEOPLE inside tools/build_week_pack.py. Edit words here, not in the renderer.
 * Each scene mirrors one card in docs/10-scenarios.md.
 */

export const FPS = 30;
export const sec = (s: number) => Math.round(s * FPS);

export type Visual =
  | { kind: "pack" }
  | { kind: "grid-open" }
  | { kind: "idea" }
  | { kind: "target" }
  | { kind: "three" }
  | { kind: "report" };

export interface Scene {
  id: string;
  n: number;
  time: string;
  title: string;
  situation: string;
  steps: string[];
  notThis: string;
  lands: string;
  visual: Visual;
}

/** When each beat appears, relative to the start of a scene. */
export const TIMING = {
  title: sec(0.15),
  situation: sec(1.4),
  firstStep: sec(5),
  stepGap: sec(5),
  notThisGap: sec(2),
  landsGap: sec(3.2),
  tail: sec(2),
};

export const stepAt = (i: number) => TIMING.firstStep + i * TIMING.stepGap;

export const sceneFrames = (s: Scene) =>
  TIMING.firstStep +
  s.steps.length * TIMING.stepGap +
  TIMING.notThisGap +
  TIMING.landsGap +
  TIMING.tail;

export const INTRO = { frames: sec(4.5) };
export const OUTRO = { frames: sec(9) };

export const SCENES: Scene[] = [
  {
    id: "monday",
    n: 1,
    time: "MONDAY 06:55",
    title: "The week is already printed",
    situation:
      "Coffee, desk, and the old reflex arrives: build the week from a blank page.",
    steps: [
      "Take the pack from Sunday — one OPEN sheet, five Kick-off grids, already dated.",
      "Write the week's 3 targets at the top of the OPEN sheet, each with a date.",
      "Put the fixed points in TODAY'S 3 — TBT Tue, SHI Thu, Thierry Fri 14:00.",
      "Stop at ten minutes.",
    ],
    notThis: "Write the eleven names again. Build a second calendar.",
    lands: "Targets → OPEN sheet · Appointments → TODAY'S 3",
    visual: { kind: "pack" },
  },
  {
    id: "ptw",
    n: 2,
    time: "07:20",
    title: "\u201CPTW, still waiting\u201D",
    situation:
      "The board ends. Khang says the FIR PTW is still not issued — and he has no date.",
    steps: [
      "On today's Kick-off grid, beside Khang: \u21D2 Khang: PTW FIR room \u2014 date TBC.",
      "Before the walkdown, one row on the OPEN sheet. You set the date: 26.11.",
      "On the power-up path? Add ! and circle the date.",
    ],
    notThis: "Leave it on the grid and hope to remember it.",
    lands: "Grid = what he said · OPEN sheet = what he owes",
    visual: { kind: "grid-open" },
  },
  {
    id: "idea",
    n: 3,
    time: "10:40",
    title: "The idea in the corridor",
    situation:
      "A 5S campaign in the ECC room would end the cable mess. No date. Nobody owes anything.",
    steps: [
      "Back page of the Notebook: 24.11 IDEA 5S campaign, ECC room.",
      "It does not touch the OPEN sheet.",
      "Friday 13:00 it gets one fate: dead, \u2192 me with a date, or ROADMAP.md.",
    ],
    notThis: "Start a second list. Put an undated idea in the DUE column.",
    lands: "Ideas page, until Friday decides",
    visual: { kind: "idea" },
  },
  {
    id: "target",
    n: 4,
    time: "MONDAY 13:10",
    title: "The target that moves",
    situation:
      "Target 3 was AIR LWN ready and signed, 26.11. The power-up is cancelled: conditions not met.",
    steps: [
      "Strike through target 3. Do not reword it quietly.",
      "Write the new outcome beside it, with the date and the reason.",
      "One \u2022 line on the Notebook: the decision, and who took it.",
      "Update the OPEN sheet rows that depended on that date.",
    ],
    notThis: "Rewrite it clean so the change disappears.",
    lands: "OPEN sheet keeps both versions · Notebook keeps the decision",
    visual: { kind: "target" },
  },
  {
    id: "three",
    n: 5,
    time: "16:30",
    title: "Three lines, not an essay",
    situation:
      "Eight things happened. None of them are on paper, and the temptation is to write the day down properly.",
    steps: [
      "Three \u2022 lines on the Notebook: done, moved, blocked.",
      "Tomorrow's appointments into tomorrow's TODAY'S 3.",
      "Send the nudges for everything due today, before the laptop closes.",
    ],
    notThis: "Retell the day. Write a page. Leave the nudges for tomorrow.",
    lands: "Notebook = the day's record · OPEN sheet = what is still owed",
    visual: { kind: "three" },
  },
  {
    id: "friday",
    n: 6,
    time: "FRIDAY 13:00",
    title: "The report writes itself",
    situation:
      "Thierry at 14:00. The old panic: what did we actually achieve this week?",
    steps: [
      "OPEN sheet: tick what closed, mark what did not, read the struck targets.",
      "Notebook: the week's \u2022 and ! lines. Three lines: done, blocked, risk.",
      "Assemble the report from those lines. Fifteen minutes.",
      "Close the laptop. 14:00 is a meeting, not a reconstruction.",
    ],
    notThis: "Rely on memory. Invent a new format.",
    lands: "The report is generated, not reconstructed",
    visual: { kind: "report" },
  },
];

export const TOTAL_FRAMES =
  INTRO.frames + SCENES.reduce((a, s) => a + sceneFrames(s), 0) + OUTRO.frames;
