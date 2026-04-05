import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  TransitionSeries,
  linearTiming,
  springTiming,
} from "@remotion/transitions";
import { wipe } from "@remotion/transitions/wipe";
import { fade } from "@remotion/transitions/fade";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

// ─── Fonts (loaded at module level — blocks render until ready) ───────────────

const { fontFamily: serif } = loadPlayfair("normal", {
  weights: ["400", "700"],
  subsets: ["latin"],
});

const { fontFamily: sans } = loadInter("normal", {
  weights: ["400", "600", "700"],
  subsets: ["latin"],
});

// ─── Brand tokens ─────────────────────────────────────────────────────────────

const C = {
  cream: "#F3F1E7",
  terracotta: "#D97757",
  dark: "#191919",
  muted: "#5C5C5C",
  border: "#D6D4C8",
  white: "#FFFFFF",
};

// ─── Spring configs ───────────────────────────────────────────────────────────

const snappy = { damping: 20, stiffness: 200 };
const smooth = { damping: 200 };

// ─── Timing constants (in frames at 30fps) ───────────────────────────────────

const TRANSITION_FRAMES = 18;

export const INTRO_DURATION = 90;    // 3s
export const AGENTS_DURATION = 120;  // 4s
export const ITEMS_DURATION = 105;   // 3.5s
export const CTA_DURATION = 75;      // 2.5s

// Total: 90 + 120 + 105 + 75 - (3 × 18) = 336 frames = 11.2s
export const GB_VIDEO_DURATION =
  INTRO_DURATION + AGENTS_DURATION + ITEMS_DURATION + CTA_DURATION -
  TRANSITION_FRAMES * 3;

// ─── Helpers ──────────────────────────────────────────────────────────────────

const fadeIn = (frame: number, fps: number, durationSecs = 0.5, delaySecs = 0) => {
  const start = Math.round(delaySecs * fps);
  const end = start + Math.round(durationSecs * fps);
  return interpolate(frame, [start, end], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
};

const slideUp = (frame: number, fps: number, delaySecs = 0) => {
  const p = spring({
    frame: frame - Math.round(delaySecs * fps),
    fps,
    config: snappy,
    durationInFrames: 25,
  });
  return interpolate(p, [0, 1], [40, 0]);
};

// ─── Scene 1: Brand Intro ─────────────────────────────────────────────────────

const IntroScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = fadeIn(frame, fps, 0.4);
  const titleY = slideUp(frame, fps);

  const taglineOpacity = fadeIn(frame, fps, 0.5, 0.4);
  const taglineY = slideUp(frame, fps, 0.4);

  const pillsOpacity = fadeIn(frame, fps, 0.5, 0.9);
  const pillsY = slideUp(frame, fps, 0.9);

  const accentProgress = spring({ frame, fps, config: smooth, durationInFrames: 35 });
  const accentWidth = interpolate(accentProgress, [0, 1], [0, 180]);

  const pills = ["3 Claude Agents", "RAG + Knowledge Graph", "AWS CloudFormation", "20+ hrs/week"];

  return (
    <AbsoluteFill style={{ backgroundColor: C.cream, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 80 }}>
      {/* Eyebrow label */}
      <div style={{ opacity: titleOpacity, transform: `translateY(${titleY}px)`, marginBottom: 12, display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: C.terracotta }} />
        <span style={{ fontFamily: sans, fontSize: 13, fontWeight: 600, color: C.terracotta, letterSpacing: 3, textTransform: "uppercase" }}>
          90-Day Agentic Systems Program
        </span>
      </div>

      {/* Brand name */}
      <div style={{ opacity: titleOpacity, transform: `translateY(${titleY}px)`, textAlign: "center" }}>
        <h1 style={{ fontFamily: serif, fontSize: 96, fontWeight: 700, color: C.dark, lineHeight: 1, margin: 0 }}>
          GB Automation
        </h1>
      </div>

      {/* Terracotta accent line */}
      <div style={{ width: accentWidth, height: 3, backgroundColor: C.terracotta, borderRadius: 99, margin: "20px 0" }} />

      {/* Tagline */}
      <div style={{ opacity: taglineOpacity, transform: `translateY(${taglineY}px)`, textAlign: "center", maxWidth: 700 }}>
        <p style={{ fontFamily: sans, fontSize: 26, fontWeight: 400, color: C.muted, margin: 0, lineHeight: 1.4 }}>
          Build Smarter and Faster with an AI Developer<br />
          <span style={{ color: C.dark, fontWeight: 600 }}>That Codes in Your Vibe</span>
        </p>
      </div>

      {/* Deliverable pills */}
      <div style={{ opacity: pillsOpacity, transform: `translateY(${pillsY}px)`, display: "flex", gap: 10, marginTop: 36, flexWrap: "wrap", justifyContent: "center" }}>
        {pills.map((label) => (
          <span key={label} style={{ fontFamily: sans, fontSize: 13, fontWeight: 600, color: C.dark, backgroundColor: C.white, border: `1.5px solid ${C.border}`, borderRadius: 999, padding: "7px 16px" }}>
            {label}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ─── Scene 2: 3 Agents ───────────────────────────────────────────────────────

type AgentCard = { title: string; description: string; icon: string };

const AgentCardItem = ({ agent, delayFrames }: { agent: AgentCard; delayFrames: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delayFrames,
    fps,
    config: snappy,
    durationInFrames: 28,
  });
  const y = interpolate(progress, [0, 1], [50, 0]);
  const opacity = interpolate(progress, [0, 0.3], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={{
      opacity,
      transform: `translateY(${y}px)`,
      flex: 1,
      backgroundColor: C.white,
      border: `1.5px solid ${C.border}`,
      borderRadius: 24,
      padding: 36,
    }}>
      <div style={{ width: 44, height: 44, borderRadius: 12, backgroundColor: C.cream, border: `1.5px solid ${C.border}`, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20, fontSize: 22 }}>
        {agent.icon}
      </div>
      <h3 style={{ fontFamily: serif, fontSize: 24, fontWeight: 700, color: C.dark, margin: "0 0 10px 0" }}>
        {agent.title}
      </h3>
      <p style={{ fontFamily: sans, fontSize: 14, color: C.muted, margin: 0, lineHeight: 1.6 }}>
        {agent.description}
      </p>
    </div>
  );
};

const AgentsScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headerOpacity = fadeIn(frame, fps, 0.4);
  const headerY = slideUp(frame, fps);

  const agents: AgentCard[] = [
    { icon: "🔀", title: "Orchestrator Agent", description: "Manages workflows, integrations, and deployments across your entire system." },
    { icon: "💻", title: "Developer Agent", description: "Codes, tests, and ships features through vibe coding. Rapidly iterates on your products." },
    { icon: "🎯", title: "Specialized Agent", description: "Custom agent tuned to your domain with deep knowledge graph access." },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: C.cream, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "60px 80px" }}>
      {/* Section header */}
      <div style={{ opacity: headerOpacity, transform: `translateY(${headerY}px)`, textAlign: "center", marginBottom: 48 }}>
        <p style={{ fontFamily: sans, fontSize: 12, fontWeight: 600, color: C.terracotta, letterSpacing: 3, textTransform: "uppercase", margin: "0 0 10px 0" }}>
          Your Autonomous Team
        </p>
        <h2 style={{ fontFamily: serif, fontSize: 52, fontWeight: 700, color: C.dark, margin: 0 }}>
          Three Agents. One System.
        </h2>
      </div>

      {/* Cards row */}
      <div style={{ display: "flex", gap: 24, width: "100%", alignItems: "stretch" }}>
        {agents.map((agent, i) => (
          <AgentCardItem key={agent.title} agent={agent} delayFrames={12 + i * 18} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ─── Scene 3: Deliverables ────────────────────────────────────────────────────

const DeliverablesScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headerOpacity = fadeIn(frame, fps, 0.4);
  const headerY = slideUp(frame, fps);

  const deliverables = [
    { title: "Internal AI Application", desc: "Custom internal app built around your workflows." },
    { title: "External AI Product", desc: "Customer-facing interface with ChatGPT-style chat." },
    { title: "RAG + Knowledge Graph", desc: "Private data embeddings + relational graph DB." },
    { title: "AWS CloudFormation Kit", desc: "Full infrastructure-as-code deployment." },
    { title: "CI/CD Integration", desc: "GitHub Actions + Claude Code." },
    { title: "Interface Options", desc: "Slack, Telegram, or Microsoft Teams." },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: C.cream, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "60px 80px" }}>
      {/* Header */}
      <div style={{ opacity: headerOpacity, transform: `translateY(${headerY}px)`, textAlign: "center", marginBottom: 48 }}>
        <p style={{ fontFamily: sans, fontSize: 12, fontWeight: 600, color: C.terracotta, letterSpacing: 3, textTransform: "uppercase", margin: "0 0 10px 0" }}>
          Complete System
        </p>
        <h2 style={{ fontFamily: serif, fontSize: 52, fontWeight: 700, color: C.dark, margin: 0 }}>
          Everything Included
        </h2>
      </div>

      {/* Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "18px 32px", width: "100%" }}>
        {deliverables.map((item, i) => {
          const progress = spring({
            frame: frame - (12 + i * 10),
            fps,
            config: snappy,
            durationInFrames: 22,
          });
          const opacity = interpolate(progress, [0, 0.4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const y = interpolate(progress, [0, 1], [20, 0]);

          return (
            <div key={item.title} style={{ opacity, transform: `translateY(${y}px)`, display: "flex", alignItems: "flex-start", gap: 14, backgroundColor: C.white, border: `1.5px solid ${C.border}`, borderRadius: 16, padding: "18px 22px" }}>
              <div style={{ width: 20, height: 20, borderRadius: "50%", backgroundColor: C.terracotta, flexShrink: 0, marginTop: 2, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                  <path d="M2 5L4 7L8 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div>
                <div style={{ fontFamily: sans, fontSize: 14, fontWeight: 700, color: C.dark, marginBottom: 3 }}>{item.title}</div>
                <div style={{ fontFamily: sans, fontSize: 12, color: C.muted, lineHeight: 1.5 }}>{item.desc}</div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ─── Scene 4: CTA ─────────────────────────────────────────────────────────────

const CTAScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = fadeIn(frame, fps, 0.5);
  const titleY = slideUp(frame, fps);

  const subtitleOpacity = fadeIn(frame, fps, 0.5, 0.4);
  const subtitleY = slideUp(frame, fps, 0.4);

  const btnProgress = spring({
    frame: frame - Math.round(0.9 * fps),
    fps,
    config: { damping: 10, stiffness: 150 },
    durationInFrames: 22,
  });
  const btnScale = interpolate(btnProgress, [0, 1], [0.85, 1]);
  const btnOpacity = interpolate(btnProgress, [0, 0.3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      background: `linear-gradient(135deg, ${C.terracotta} 0%, #c4633d 100%)`,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: 80,
    }}>
      {/* Eyebrow */}
      <Sequence from={0} premountFor={fps}>
        <div style={{ opacity: titleOpacity, transform: `translateY(${titleY}px)`, marginBottom: 16 }}>
          <span style={{ fontFamily: sans, fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.7)", letterSpacing: 3, textTransform: "uppercase" }}>
            Ready to Build?
          </span>
        </div>
      </Sequence>

      {/* Main CTA */}
      <Sequence from={0} premountFor={fps}>
        <div style={{ opacity: titleOpacity, transform: `translateY(${titleY}px)`, textAlign: "center", marginBottom: 16 }}>
          <h2 style={{ fontFamily: serif, fontSize: 72, fontWeight: 700, color: C.white, margin: 0, lineHeight: 1.1 }}>
            Let's Build Your<br />AI System
          </h2>
        </div>
      </Sequence>

      {/* Subtitle */}
      <Sequence from={0} premountFor={fps}>
        <div style={{ opacity: subtitleOpacity, transform: `translateY(${subtitleY}px)`, textAlign: "center", marginBottom: 48 }}>
          <p style={{ fontFamily: sans, fontSize: 20, color: "rgba(255,255,255,0.85)", margin: 0 }}>
            90 days to a fully autonomous AI development team
          </p>
        </div>
      </Sequence>

      {/* Button */}
      <Sequence from={0} premountFor={fps}>
        <div style={{ opacity: btnOpacity, transform: `scale(${btnScale})` }}>
          <div style={{
            fontFamily: sans,
            fontSize: 18,
            fontWeight: 700,
            color: C.terracotta,
            backgroundColor: C.white,
            borderRadius: 12,
            padding: "18px 48px",
            letterSpacing: 0.5,
          }}>
            Schedule Discovery Call
          </div>
        </div>
      </Sequence>
    </AbsoluteFill>
  );
};

// ─── Root export ──────────────────────────────────────────────────────────────

export const GBAutomationVideo = () => {
  const transitionTiming = linearTiming({ durationInFrames: TRANSITION_FRAMES });

  return (
    <AbsoluteFill>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={INTRO_DURATION}>
          <IntroScene />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={wipe({ direction: "from-right" })}
          timing={transitionTiming}
        />

        <TransitionSeries.Sequence durationInFrames={AGENTS_DURATION}>
          <AgentsScene />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={wipe({ direction: "from-right" })}
          timing={transitionTiming}
        />

        <TransitionSeries.Sequence durationInFrames={ITEMS_DURATION}>
          <DeliverablesScene />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={springTiming({ config: smooth, durationInFrames: TRANSITION_FRAMES })}
        />

        <TransitionSeries.Sequence durationInFrames={CTA_DURATION}>
          <CTAScene />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
