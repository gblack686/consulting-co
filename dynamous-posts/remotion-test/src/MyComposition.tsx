import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { zColor } from "@remotion/zod-types";
import { loadFont } from "@remotion/google-fonts/Inter";

// Load Inter at module level — blocks rendering until font is ready
const { fontFamily } = loadFont("normal", {
  weights: ["400", "700", "900"],
  subsets: ["latin"],
});

// Named spring configs from timing rules
const snappy = { damping: 20, stiffness: 200 };
const bouncy = { damping: 8 };

// ─── Zod schema — exposes props to Remotion Studio's sidebar ─────────────────

export const MyCompositionSchema = z.object({
  titleText: z.string(),
  subtitleText: z.string(),
  badgeText: z.string(),
  accentColor: zColor(),
});

type Props = z.infer<typeof MyCompositionSchema>;

// ─── Sub-components ───────────────────────────────────────────────────────────

const Title: React.FC<Pick<Props, "titleText" | "accentColor">> = ({
  titleText,
  accentColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame, fps, config: snappy, durationInFrames: 30 });
  const y = interpolate(progress, [0, 1], [60, 0]);

  return (
    <div
      style={{
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: `translate(-50%, calc(-50% + ${y}px))`,
        fontFamily,
        fontSize: 80,
        fontWeight: 900,
        color: accentColor,
        letterSpacing: -2,
        textAlign: "center",
        lineHeight: 1.1,
        whiteSpace: "nowrap",
      }}
    >
      {titleText}
    </div>
  );
};

const Subtitle: React.FC<Pick<Props, "subtitleText">> = ({ subtitleText }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, Math.round(0.7 * fps)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  return (
    <div
      style={{
        position: "absolute",
        top: "calc(50% + 64px)",
        left: "50%",
        transform: "translateX(-50%)",
        fontFamily,
        opacity,
        fontSize: 28,
        fontWeight: 400,
        color: "#a8b2d8",
        letterSpacing: 6,
        textTransform: "uppercase",
        whiteSpace: "nowrap",
      }}
    >
      {subtitleText}
    </div>
  );
};

const Badge: React.FC<Pick<Props, "badgeText" | "accentColor">> = ({
  badgeText,
  accentColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame, fps, config: bouncy, durationInFrames: 20 });
  const scale = interpolate(progress, [0, 1], [0, 1]);

  const pulseCycle = Math.round(fps * 1.5);
  const pulse = interpolate(
    frame % pulseCycle,
    [0, Math.round(pulseCycle * 0.5), pulseCycle],
    [1, 1.3, 1],
    { extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        top: "calc(50% + 130px)",
        left: "50%",
        transform: `translateX(-50%) scale(${scale})`,
        backgroundColor: `${accentColor}20`,
        border: `2px solid ${accentColor}`,
        borderRadius: 999,
        padding: "12px 32px",
        display: "flex",
        alignItems: "center",
        gap: 12,
        whiteSpace: "nowrap",
      }}
    >
      <div
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          backgroundColor: accentColor,
          transform: `scale(${pulse})`,
        }}
      />
      <span
        style={{
          fontFamily,
          color: accentColor,
          fontSize: 18,
          fontWeight: 700,
        }}
      >
        {badgeText}
      </span>
    </div>
  );
};

// ─── Root composition ─────────────────────────────────────────────────────────

export const MyComposition: React.FC<Props> = ({
  titleText,
  subtitleText,
  badgeText,
  accentColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, Math.round(0.5 * fps)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
        opacity,
      }}
    >
      <Sequence from={0} premountFor={fps}>
        <Title titleText={titleText} accentColor={accentColor} />
      </Sequence>

      <Sequence from={Math.round(0.8 * fps)} premountFor={fps}>
        <Subtitle subtitleText={subtitleText} />
      </Sequence>

      <Sequence from={Math.round(1.5 * fps)} premountFor={fps}>
        <Badge badgeText={badgeText} accentColor={accentColor} />
      </Sequence>
    </AbsoluteFill>
  );
};
