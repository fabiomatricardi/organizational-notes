import type { ReactNode } from "react";
import { AbsoluteFill, Composition, Sequence } from "remotion";
import {
  FPS,
  INTRO,
  OUTRO,
  SCENES,
  TOTAL_FRAMES,
  sceneFrames,
} from "./script";
import { C } from "./theme";
import { Intro, Outro, Progress, SceneView } from "./Video";

/**
 * One composition, six scenes, no audio.
 * Scene durations derive from the script, so editing a step adds time instead
 * of desynchronising the picture.
 */
const Tutorial = () => {
  const blocks: { from: number; dur: number; node: ReactNode }[] = [];
  let at = 0;

  blocks.push({ from: at, dur: INTRO.frames, node: <Intro /> });
  at += INTRO.frames;

  for (const scene of SCENES) {
    const dur = sceneFrames(scene);
    blocks.push({ from: at, dur, node: <SceneView scene={scene} /> });
    at += dur;
  }

  blocks.push({ from: at, dur: OUTRO.frames, node: <Outro /> });

  return (
    <AbsoluteFill style={{ backgroundColor: C.desk }}>
      {blocks.map((b, i) => (
        <Sequence key={i} from={b.from} durationInFrames={b.dur}>
          {b.node}
        </Sequence>
      ))}
      <Progress />
    </AbsoluteFill>
  );
};

export const Root = () => (
  <Composition
    id="Tutorial"
    component={Tutorial}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={1920}
    height={1080}
  />
);
