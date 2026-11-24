import type { CSSProperties, ReactNode } from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, FONT } from "./theme";
import {
  FPS,
  SCENES,
  TIMING,
  TOTAL_FRAMES,
  sceneFrames,
  stepAt,
  type Scene,
} from "./script";

/* ------------------------------------------------------------------ */
/* motion helpers — every value is a pure function of the frame        */
/* ------------------------------------------------------------------ */

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const ease = (f: number, at: number, dur = 14) =>
  interpolate(f, [at, at + dur], [0, 1], CLAMP);

const rise = (f: number, at: number, dur = 14): CSSProperties => {
  const p = ease(f, at, dur);
  return { opacity: p, transform: `translateY(${(1 - p) * 18}px)` };
};

const typed = (text: string, f: number, at: number, cps = 26) => {
  const n = Math.floor((Math.max(0, f - at) / FPS) * cps);
  return text.slice(0, Math.max(0, Math.min(text.length, n)));
};

const strikeScale = (f: number, at: number, dur = 12) =>
  interpolate(f, [at, at + dur], [0, 1], CLAMP);

/* ------------------------------------------------------------------ */
/* paper components                                                    */
/* ------------------------------------------------------------------ */

const Sheet = ({
  w,
  h,
  title,
  sub,
  children,
  style,
}: {
  w: number;
  h: number;
  title: string;
  sub: string;
  children: ReactNode;
  style?: CSSProperties;
}) => (
  <div
    style={{
      width: w,
      height: h,
      background: C.paper,
      boxShadow: "0 24px 50px rgba(0,0,0,.18)",
      padding: "28px 26px",
      display: "flex",
      flexDirection: "column",
      boxSizing: "border-box",
      ...style,
    }}
  >
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-end",
        borderBottom: `3px solid ${C.ink}`,
        paddingBottom: 9,
      }}
    >
      <div style={{ fontSize: 18, fontWeight: 700, letterSpacing: 1.3 }}>
        {title}
      </div>
      <div style={{ fontSize: 14, color: C.grey, whiteSpace: "nowrap" }}>
        {sub}
      </div>
    </div>
    <div style={{ marginTop: 18, flex: 1, minHeight: 0 }}>{children}</div>
  </div>
);

const Cap = ({ children, style }: { children: ReactNode; style?: CSSProperties }) => (
  <div
    style={{
      fontSize: 12,
      fontWeight: 700,
      letterSpacing: 2.2,
      textTransform: "uppercase",
      color: C.grey,
      ...style,
    }}
  >
    {children}
  </div>
);

/** A line of text with the drawn strikethrough used for changed targets. */
const Struck = ({
  children,
  progress,
  style,
}: {
  children: ReactNode;
  progress: number;
  style?: CSSProperties;
}) => (
  <span style={{ position: "relative", display: "inline-block", ...style }}>
    <span style={{ opacity: 0.55 }}>{children}</span>
    <span
      style={{
        position: "absolute",
        left: 0,
        top: "54%",
        height: 2,
        width: "100%",
        background: C.ink,
        transform: `scaleX(${progress})`,
        transformOrigin: "left center",
      }}
    />
  </span>
);

/* ------------------------------------------------------------------ */
/* the six visuals                                                     */
/* ------------------------------------------------------------------ */

const PackVisual = ({ f }: { f: number }) => {
  const targets: [string, string, string][] = [
    ["1", "BICC walkdown complete", "26.11"],
    ["2", "FIR punch list closed", "27.11"],
    ["3", "AIR LWN ready & signed", "26.11"],
  ];
  const at = stepAt(1);

  return (
    <div
      style={{
        position: "relative",
        width: 1060,
        height: 780,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {[4, 3, 2, 1].map((i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            width: 980,
            height: 693,
            background: C.paper,
            boxShadow: "0 12px 26px rgba(0,0,0,.10)",
            transform: `translate(${i * -11}px, ${i * -11}px)`,
          }}
        />
      ))}

      <Sheet
        w={980}
        h={693}
        title="OPEN SHEET"
        sub="WK 48 · 23/11 → 27/11"
        style={{ position: "relative" }}
      >
        <Cap>Targets · the week's 3</Cap>
        <div style={{ marginTop: 10 }}>
          {targets.map(([n, text, due], i) => (
            <div
              key={n}
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: 14,
                padding: "11px 0",
                borderBottom: `1px solid ${C.line}`,
                ...rise(f, at + i * 22, 12),
              }}
            >
              <span style={{ fontSize: 17, color: C.grey, width: 16 }}>{n}</span>
              <span style={{ fontSize: 25, flex: 1 }}>
                {typed(text, f, at + i * 22)}
              </span>
              <span style={{ fontSize: 20 }}>{typed(due, f, at + i * 22 + 12, 9)}</span>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 22, ...rise(f, stepAt(2), 14) }}>
          <Cap>Fixed this week</Cap>
          <div style={{ fontSize: 19, marginTop: 8, color: C.body }}>
            TBT Tue · SHI Thu · Thierry Fri 14:00
          </div>
        </div>
      </Sheet>
    </div>
  );
};

const GridOpenVisual = ({ f }: { f: number }) => {
  const names = ["Aras", "Chang", "Khang", "HJ Lee", "Kim", "YZ", "Antonello", "Syukri"];
  const gridAt = stepAt(0);
  const lineAt = gridAt + 18;
  const openAt = stepAt(1);
  const flagAt = stepAt(2);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 34,
        width: 1120,
        height: 780,
      }}
    >
      <Sheet w={430} h={608} title="KICK-OFF GRID" sub="23/11 MON">
        <div style={{ fontSize: 15, color: C.grey, marginBottom: 8 }}>
          Only what is new
        </div>
        {names.map((name, i) => (
          <div
            key={name}
            style={{
              display: "flex",
              gap: 8,
              alignItems: "baseline",
              padding: "7px 0",
              borderBottom: `1px solid ${C.line}`,
              fontSize: 15,
            }}
          >
            <span style={{ color: C.grey, width: 16 }}>{String(i + 1).padStart(2, "0")}</span>
            <span style={{ width: 62, fontWeight: name === "Khang" ? 700 : 400 }}>
              {name}
            </span>
            <span style={{ flex: 1, fontSize: 13, color: C.body }}>
              {name === "Khang" ? typed("⇒ PTW FIR room — TBC", f, lineAt, 22) : ""}
            </span>
          </div>
        ))}
      </Sheet>

      <div style={{ fontSize: 40, color: C.grey, ...rise(f, openAt - 12) }}>→</div>

      <Sheet w={540} h={372} title="OPEN SHEET" sub="WK 48">
        <div style={{ display: "flex", fontSize: 11, letterSpacing: 1.6, color: C.grey, paddingBottom: 8, borderBottom: `2px solid ${C.ink}` }}>
          <span style={{ flex: 1 }}>WHAT</span>
          <span style={{ width: 90 }}>WHO</span>
          <span style={{ width: 60, textAlign: "right" }}>DUE</span>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            padding: "14px 0",
            borderBottom: `1px solid ${C.line}`,
            fontSize: 16,
            ...rise(f, openAt, 14),
          }}
        >
          <span style={{ flex: 1 }}>{typed("PTW FIR room", f, openAt + 6, 24)}</span>
          <span style={{ width: 90 }}>
            <b>{typed("Khang", f, openAt + 20, 10)}</b>
          </span>
          <span style={{ width: 60, textAlign: "right", fontWeight: 700 }}>
            {typed("26.11", f, openAt + 30, 8)}
          </span>
        </div>
        <div style={{ marginTop: 22, display: "flex", alignItems: "center", gap: 10, ...rise(f, flagAt) }}>
          <span style={{ fontSize: 22, fontWeight: 700 }}>!</span>
          <span style={{ fontSize: 14, color: C.body }}>
            on the power-up path — circle the date
          </span>
        </div>
      </Sheet>
    </div>
  );
};

const IdeaVisual = ({ f }: { f: number }) => {
  const at = stepAt(0);
  const fateAt = stepAt(2);
  const fates = [
    "struck out — it died",
    "→ me, with a date",
    "→ ROADMAP.md",
  ];

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 46,
        width: 1120,
        height: 780,
      }}
    >
      <div
        style={{
          width: 500,
          height: 710,
          background: C.paper,
          boxShadow: "0 24px 50px rgba(0,0,0,.18)",
          padding: "30px 26px 26px 58px",
          position: "relative",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 26,
            top: 0,
            bottom: 0,
            width: 1,
            background: C.line,
          }}
        />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
          <b style={{ fontSize: 20 }}>TUE 24.11</b>
          <span style={{ fontSize: 12, letterSpacing: 2, color: C.grey }}>NOTEBOOK</span>
        </div>
        <div
          style={{
            marginTop: 26,
            height: 600,
            backgroundImage: `repeating-linear-gradient(to bottom, transparent 0 39px, ${C.line} 39px 40px)`,
            backgroundPosition: "0 6px",
          }}
        >
          <div
            style={{
              fontSize: 23,
              fontStyle: "italic",
              height: 40,
              lineHeight: "40px",
              ...rise(f, at, 12),
            }}
          >
            {typed("24.11 IDEA 5S campaign, ECC room", f, at + 4, 20)}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 14, width: 520 }}>
        <Cap>Friday 13:00 · one fate</Cap>
        {fates.map((t, i) => (
          <div
            key={t}
            style={{
              border: `2px solid ${C.ink}`,
              padding: "14px 18px",
              fontSize: 21,
              background: i === 0 ? C.faint : C.paper,
              ...rise(f, fateAt + i * 16, 12),
            }}
          >
            {t}
          </div>
        ))}
        <div style={{ fontSize: 15, color: C.grey, marginTop: 8, ...rise(f, fateAt + 55) }}>
          Until Friday it holds no date and no owner — so it never touches the OPEN sheet.
        </div>
      </div>
    </div>
  );
};

const TargetVisual = ({ f }: { f: number }) => {
  const strikeAt = stepAt(0);
  const newAt = stepAt(1);
  const noteAt = stepAt(2);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 22,
        width: 1080,
        height: 780,
      }}
    >
      <Sheet w={980} h={560} title="OPEN SHEET" sub="WK 48 · power-up week">
        <Cap>Targets · the week's 3</Cap>
        <div style={{ marginTop: 6 }}>
          <div style={{ padding: "10px 0", fontSize: 21, color: C.body }}>
            <span style={{ color: C.grey, marginRight: 12 }}>1</span>
            970-NP-03 / 980-NP-01 energised
          </div>
          <div style={{ padding: "10px 0", fontSize: 21, color: C.body }}>
            <span style={{ color: C.grey, marginRight: 12 }}>2</span>
            FIR punch list closed
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 12,
              padding: "12px 0",
              borderTop: `1px solid ${C.line}`,
              borderBottom: `1px solid ${C.line}`,
            }}
          >
            <span style={{ color: C.grey }}>3</span>
            <Struck progress={strikeScale(f, strikeAt)} style={{ fontSize: 22 }}>
              AIR LWN ready &amp; signed
            </Struck>
            <span style={{ marginLeft: "auto", fontSize: 18, opacity: 0.55 }}>
              26.11
            </span>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 12,
              padding: "12px 0",
              fontSize: 19,
              color: C.body,
              ...rise(f, newAt, 14),
            }}
          >
            <span style={{ color: C.grey }}>3</span>
            {typed("AIR LWN readiness check", f, newAt + 4, 24)}
            <span style={{ marginLeft: "auto", fontSize: 16 }}>
              {typed("27.11", f, newAt + 26, 10)}
            </span>
          </div>
        </div>
        <div style={{ fontSize: 14, color: C.grey, marginTop: 6, ...rise(f, newAt + 30) }}>
          23.11 — power-up off (conditions)
        </div>
      </Sheet>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          width: 980,
          background: C.paper,
          boxShadow: "0 10px 24px rgba(0,0,0,.10)",
          padding: "14px 20px",
          boxSizing: "border-box",
          ...rise(f, noteAt, 14),
        }}
      >
        <span style={{ fontSize: 11, letterSpacing: 2, color: C.grey }}>NOTEBOOK</span>
        <span style={{ fontSize: 18 }}>
          • power-up off — decision taken, 23.11
        </span>
      </div>
    </div>
  );
};

const ThreeVisual = ({ f }: { f: number }) => {
  const at = stepAt(0);
  const tomAt = stepAt(1);
  const nudgeAt = stepAt(2);
  const lines = [
    ["done", "BICC walkdown, 3 rooms"],
    ["moved", "PTW row to 26.11"],
    ["blocked", "LER cold SAT date"],
  ];

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 46,
        width: 1120,
        height: 780,
      }}
    >
      <div
        style={{
          width: 500,
          height: 710,
          background: C.paper,
          boxShadow: "0 24px 50px rgba(0,0,0,.18)",
          padding: "30px 26px 26px 58px",
          position: "relative",
          boxSizing: "border-box",
        }}
      >
        <div style={{ position: "absolute", left: 26, top: 0, bottom: 0, width: 1, background: C.line }} />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
          <b style={{ fontSize: 20 }}>TUE 24.11</b>
          <span style={{ fontSize: 12, letterSpacing: 2, color: C.grey }}>NOTEBOOK</span>
        </div>
        <div
          style={{
            marginTop: 26,
            height: 600,
            backgroundImage: `repeating-linear-gradient(to bottom, transparent 0 39px, ${C.line} 39px 40px)`,
            backgroundPosition: "0 6px",
          }}
        >
          {lines.map(([label, text], i) => (
            <div
              key={label}
              style={{
                fontSize: 20,
                height: 40,
                lineHeight: "40px",
                ...rise(f, at + i * 20, 12),
              }}
            >
              <span style={{ fontWeight: 700 }}>{label}</span>
              <span style={{ color: C.body }}> · {text}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 20, width: 520 }}>
        <div
          style={{
            border: `2px solid ${C.ink}`,
            padding: "16px 18px",
            ...rise(f, tomAt, 14),
          }}
        >
          <Cap>Tomorrow · TODAY'S 3</Cap>
          <div style={{ fontSize: 18, marginTop: 8, color: C.body }}>
            WED 25.11 · 07:20 kick-off
            <br />
            10:00 LUN walkdown
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            fontSize: 20,
            ...rise(f, nudgeAt, 14),
          }}
        >
          <span style={{ fontSize: 24 }}>✓</span>
          <span>nudges sent — all due today</span>
        </div>

        <div style={{ fontSize: 15, color: C.grey, ...rise(f, nudgeAt + 30) }}>
          The three lines are the raw material for Friday. If Tuesday is not a line, Friday is fiction.
        </div>
      </div>
    </div>
  );
};

const ReportVisual = ({ f }: { f: number }) => {
  const tickAt = stepAt(0);
  const bulletsAt = stepAt(1);
  const tagAt = stepAt(3);
  const rows = [
    ["✓", "BICC walkdown — 3 rooms"],
    ["✓", "AIR LWN readiness check"],
    ["✗", "FIR punch list"],
    ["✓", "AMS test run"],
    ["✗", "PTW FIR room"],
    ["✗", "LER cold SAT date"],
  ];
  const bullets = [
    ["done", "BICC walkdown closed, 3 rooms"],
    ["blocked", "PTW vendor form — 4 days"],
    ["risk", "LER cold SAT — Feb readiness"],
  ];

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: 1120,
        height: 780,
      }}
    >
      <Sheet w={1000} h={650} title="WEEKLY REPORT" sub="WK 48 · Thierry format">
        <div style={{ display: "flex", gap: 40, height: "100%" }}>
          <div style={{ width: 430 }}>
            <Cap>Open sheet · closed</Cap>
            <div style={{ marginTop: 8 }}>
              {rows.map(([mark, text], i) => (
                <div
                  key={text}
                  style={{
                    display: "flex",
                    gap: 10,
                    alignItems: "baseline",
                    fontSize: 16,
                    padding: "8px 0",
                    borderBottom: `1px solid ${C.line}`,
                    opacity: mark === "✗" ? 0.55 : 1,
                    ...rise(f, tickAt + i * 10, 10),
                  }}
                >
                  <span style={{ width: 16, fontWeight: 700 }}>{mark}</span>
                  <span>{text}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ flex: 1, borderLeft: `1px solid ${C.line}`, paddingLeft: 34 }}>
            <Cap>Three lines</Cap>
            <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 18 }}>
              {bullets.map(([label, text], i) => (
                <div key={label} style={{ ...rise(f, bulletsAt + i * 16, 12) }}>
                  <div style={{ fontSize: 12, letterSpacing: 2, color: C.grey }}>{label}</div>
                  <div style={{ fontSize: 21 }}>{text}</div>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 26, fontSize: 15, color: C.grey, ...rise(f, tagAt) }}>
              ← written from Tuesday 16:30, not from memory
            </div>
          </div>
        </div>
      </Sheet>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* scene chrome                                                        */
/* ------------------------------------------------------------------ */

const SceneView = ({ scene }: { scene: Scene }) => {
  const f = useCurrentFrame();
  const n = scene.steps.length;
  const notThisAt = stepAt(n) + TIMING.notThisGap;
  const landsAt = notThisAt + TIMING.landsGap;
  const zoom = interpolate(f, [0, sceneFrames(scene)], [1, 1.022], CLAMP);

  const visual = (() => {
    switch (scene.visual.kind) {
      case "pack":
        return <PackVisual f={f} />;
      case "grid-open":
        return <GridOpenVisual f={f} />;
      case "idea":
        return <IdeaVisual f={f} />;
      case "target":
        return <TargetVisual f={f} />;
      case "three":
        return <ThreeVisual f={f} />;
      case "report":
        return <ReportVisual f={f} />;
    }
  })();

  return (
    <AbsoluteFill style={{ backgroundColor: C.desk, fontFamily: FONT, color: C.ink }}>
      <Sequence from={6}>
        <Audio src={staticFile(`audio/${scene.id}-lead.mp3`)} />
      </Sequence>
      {scene.steps.map((_, i) => (
        <Sequence key={i} from={stepAt(i)}>
          <Audio
            src={staticFile(
              `audio/${scene.id}-step-${String(i + 1).padStart(2, "0")}.mp3`,
            )}
          />
        </Sequence>
      ))}
      <Sequence from={landsAt}>
        <Audio src={staticFile(`audio/${scene.id}-lands.mp3`)} />
      </Sequence>

      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: 1180,
          height: 1080,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div style={{ transform: `scale(${zoom})` }}>
          <div style={rise(f, 0, 18)}>{visual}</div>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 1220,
          top: 0,
          width: 660,
          height: 1080,
          padding: "96px 40px 120px 0",
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div
          style={{
            fontSize: 18,
            fontWeight: 700,
            letterSpacing: 3.2,
            color: C.grey,
            ...rise(f, TIMING.title, 12),
          }}
        >
          SCENE {scene.n} · {scene.time}
        </div>

        <div
          style={{
            fontSize: 54,
            lineHeight: 1.06,
            fontWeight: 700,
            letterSpacing: -0.6,
            marginTop: 16,
            ...rise(f, TIMING.title + 6, 16),
          }}
        >
          {scene.title}
        </div>

        <div
          style={{
            fontSize: 26,
            lineHeight: 1.36,
            color: C.body,
            marginTop: 22,
            ...rise(f, TIMING.situation, 16),
          }}
        >
          {scene.situation}
        </div>

        <div style={{ marginTop: 34, display: "flex", flexDirection: "column", gap: 16 }}>
          {scene.steps.map((step, i) => (
            <div
              key={step}
              style={{
                display: "flex",
                gap: 14,
                alignItems: "baseline",
                ...rise(f, stepAt(i), 14),
              }}
            >
              <span style={{ fontSize: 20, color: C.grey, width: 18, flexShrink: 0 }}>
                {i + 1}
              </span>
              <span style={{ fontSize: 24, lineHeight: 1.32 }}>{step}</span>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 30, ...rise(f, notThisAt, 14) }}>
          <Cap>Not this</Cap>
          <div
            style={{
              fontSize: 22,
              lineHeight: 1.3,
              color: C.grey,
              marginTop: 6,
              textDecoration: "line-through",
              textDecorationColor: C.ghost,
            }}
          >
            {scene.notThis}
          </div>
        </div>

        <div
          style={{
            marginTop: "auto",
            ...rise(f, landsAt, 16),
          }}
        >
          <Cap>Where it lands</Cap>
          <div style={{ fontSize: 21, lineHeight: 1.3, marginTop: 6, fontWeight: 700 }}>
            {scene.lands}
          </div>
        </div>

        <div
          style={{
            position: "absolute",
            right: 40,
            bottom: 54,
            fontSize: 15,
            letterSpacing: 2,
            color: C.grey,
          }}
        >
          {scene.n} / {SCENES.length}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/* intro, outro, progress                                              */
/* ------------------------------------------------------------------ */

const Intro = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.desk,
        fontFamily: FONT,
        color: C.ink,
        padding: "120px 140px",
        justifyContent: "center",
      }}
    >
      <Sequence from={8}>
        <Audio src={staticFile("audio/intro.mp3")} />
      </Sequence>
      <div style={{ fontSize: 18, letterSpacing: 4, color: C.grey, ...rise(f, 0, 12) }}>
        ORGANIZATIONAL NOTES · TUTORIAL
      </div>
      <div style={{ fontSize: 96, fontWeight: 700, letterSpacing: -2, marginTop: 22, ...rise(f, 10, 16) }}>
        Six scenes, one week
      </div>
      <div style={{ fontSize: 30, color: C.body, marginTop: 24, maxWidth: 1100, ...rise(f, 24, 16) }}>
        How to run the paper system, one situation at a time.
      </div>
      <div style={{ display: "flex", gap: 18, marginTop: 54, ...rise(f, 44, 16) }}>
        {["Kick-off grid", "OPEN sheet", "Notebook"].map((t) => (
          <div
            key={t}
            style={{ border: `2px solid ${C.ink}`, padding: "14px 22px", fontSize: 22, fontWeight: 700 }}
          >
            {t}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const Outro = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.desk,
        fontFamily: FONT,
        color: C.ink,
        padding: "130px 140px",
        justifyContent: "center",
      }}
    >
      <Sequence from={10}>
        <Audio src={staticFile("audio/outro.mp3")} />
      </Sequence>
      <div style={{ fontSize: 18, letterSpacing: 4, color: C.grey, ...rise(f, 0, 12) }}>
        IF ONLY ONE THING SURVIVES
      </div>
      <div style={{ fontSize: 54, lineHeight: 1.32, marginTop: 26, maxWidth: 1400 }}>
        <div style={{ ...rise(f, 12, 14) }}>
          The <b>Kick-off grid</b> is what they said.
        </div>
        <div style={{ ...rise(f, 34, 14) }}>
          The <b>OPEN sheet</b> is what they owe.
        </div>
        <div style={{ ...rise(f, 56, 14) }}>
          The <b>Notebook</b> is what happened.
        </div>
      </div>
      <div style={{ fontSize: 24, color: C.grey, marginTop: 46, ...rise(f, 86, 14) }}>
        The rules are in docs/01-method.md · the cards are in docs/10-scenarios.md
      </div>
    </AbsoluteFill>
  );
};

const Progress = () => {
  const f = useCurrentFrame();
  const p = Math.min(1, Math.max(0, f / (TOTAL_FRAMES - 1)));
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 0,
        height: 6,
        background: C.line,
      }}
    >
      <div style={{ width: `${p * 100}%`, height: "100%", background: C.ink }} />
    </div>
  );
};

export { Intro, Outro, Progress, SceneView, Sheet, Cap };
