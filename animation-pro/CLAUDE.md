# Animation-Pro Plugin

You have access to a curated library of animation framework source code,
four specialized skills, and agent definitions for every animation domain.
Use them.

## Skills

This plugin has four skills. Each covers a distinct animation domain:

| Skill | Domain | When to load |
|-------|--------|-------------|
| motion-craft | UI transitions, gestures, micro-interactions | Any component-level animation work |
| creative-animation | Generative art, canvas, particle systems | Interactive/artistic/data-viz animation |
| 3d-animation | WebGL, Three.js, R3F scene animation | Any 3D rendering with motion |
| production-motion | Programmatic video, explainers | Remotion/Motion Canvas video composition |

Load the relevant skill's SKILL.md before starting work. For cross-domain
tasks (e.g., a 3D scene with spring-physics camera and scroll-driven
navigation), load multiple skills.

## The Purpose Test

Before adding ANY animation, verify it passes at least one:

1. **Orientation**: Does this motion help the user understand where
   something came from or where it went?
2. **Feedback**: Does this motion confirm that an action was received?
3. **Relationship**: Does this motion reveal how elements are connected?

If the answer is "no" to all three, do not add animation.

## The Tool Selection Framework

| Motion need | Tool | Skill |
|-------------|------|-------|
| Color/opacity/simple state change | CSS transition | motion-craft |
| Layout animation, enter/exit | Motion (motion/react) | motion-craft |
| Gesture-driven (drag, swipe) | Motion gesture system | motion-craft |
| Spring physics (any context) | Motion or react-spring | motion-craft |
| Scroll-triggered reveals | Locomotive Scroll or CSS | motion-craft |
| Designer handoff (After Effects) | Lottie | motion-craft |
| Staggered multi-element sequences | anime.js timeline | motion-craft |
| Generative art, creative coding | p5.js | creative-animation |
| High-performance 2D (sprites, particles) | PixiJS | creative-animation |
| 2D physics simulation | Matter.js | creative-animation |
| SVG stroke drawing | Vivus | creative-animation |
| D3 data transitions | d3-transition | creative-animation |
| 3D scene, model animation | Three.js / R3F | 3d-animation |
| 3D helpers (Float, useAnimations) | Drei | 3d-animation |
| 3D physics | Rapier | 3d-animation |
| Visual timeline sequencing | Theatre.js | 3d-animation / production-motion |
| Programmatic video (React) | Remotion | production-motion |
| Programmatic animation (generators) | Motion Canvas | production-motion |

## When to use reference source code

Do NOT rely on training data for animation library internals. Instead:

- **Motion questions**: grep `refs/motion/packages/motion/src/` for spring
  physics, AnimatePresence, layout animation, gesture handlers.
- **Three.js questions**: grep `refs/threejs/src/` for AnimationMixer,
  KeyframeTrack, morph targets, camera, geometry.
- **R3F questions**: grep `refs/react-three-fiber/packages/fiber/src/` for
  useFrame, reconciler, events.
- **Drei questions**: grep `refs/drei/src/` for Float, useAnimations,
  ScrollControls, Html, and other animation helpers.
- **Remotion questions**: grep `refs/remotion/packages/core/src/` for
  useCurrentFrame, Sequence, Composition, interpolate.
- **p5.js questions**: grep `refs/p5js/src/` for draw loop, createCanvas,
  noise, vector math.
- **PixiJS questions**: grep `refs/pixijs/src/` for Application, Ticker,
  Sprite, Container, filters.
- **react-spring questions**: grep `refs/react-spring/packages/` for
  useSpring, useTrail, useChain, animated.

## Rules

1. Always verify animation library APIs against source code in refs/ before
   writing code that depends on them. Training data may be outdated.

2. Every animation must pass the Purpose Test (orientation, feedback, or
   relationship). If it fails, do not implement it.

3. Every animation must implement prefers-reduced-motion. Non-negotiable.
   Load `skills/motion-craft/references/reduced-motion.md` for patterns.

4. CSS transitions for simple state changes. JavaScript animation libraries
   for layout, gesture, and physics-driven motion. Never reach for Motion
   when CSS `transition` will do. Never reach for CSS when you need spring
   physics or AnimatePresence.

5. Only animate `transform` and `opacity` in CSS/JS. Never animate `width`,
   `height`, `top`, `left`, or other layout-triggering properties directly.

6. Spring physics over duration-based animation for interactive elements.
   Duration-based animations feel robotic because they move at a fixed speed
   regardless of distance. Springs adapt.

7. When writing Three.js code, verify geometry and material APIs against
   `refs/threejs/src/`. Three.js deprecates APIs across versions.

8. For 3D work, always specify a performance budget (triangles, draw calls,
   texture memory) and a fallback strategy (WebGL detection + 2D fallback).

## Epistemic Knowledge System

This plugin maintains structured, evolving knowledge in `knowledge/`. Claims carry confidence scores, evidence tracking, and domain tags. Over time, accepted claims strengthen and rejected claims weaken through Bayesian updates.

### Session Start Protocol

1. Read `knowledge/manifest.json` for current state and last update time.
2. Read `knowledge/claims.jsonl` and filter for `status: "active"`.
3. Sort active claims by confidence (descending) and load the top 15-20 into working context.
4. Check `knowledge/tensions.jsonl` for unresolved tensions in the domains relevant to the current task. If the task touches a tension, surface it to the user BEFORE making a decision.
5. Check `knowledge/preferences.jsonl` for user-specific defaults that may override generic best practices.

### During Work

6. When your reasoning draws on a specific claim, note its ID internally.
7. When you make a suggestion informed by a claim, track which claims influenced the decision.
8. When the user accepts, modifies, or rejects a suggestion, note the outcome.

### Session End Protocol

9. Run `/session-save` to write session observations to `knowledge/session_log/{timestamp}.jsonl`. This captures agents invoked, claims consulted, suggestions made, and their outcomes.
10. If you discovered something that contradicts an existing claim, flag it as a HIGH-PRIORITY tension signal in the session log.
11. If you noticed a recurring pattern the knowledge base doesn't cover, note it as a candidate claim in the session log.

### Knowledge Priority Rules

- Active claims with confidence > 0.8 take precedence over static prose when they conflict.
- Draft claims are informational only — they never override static agent instructions.
- Preferences defer to explicit user instructions in the current session. Preferences inform defaults, not mandates.
- When two active claims conflict, check `knowledge/tensions.jsonl` for a resolution. If none exists, surface the conflict to the user and let them decide.
- Tensions are information, not blockers. Surface them, let the user decide, log the decision.

### Commands

- `/knowledge-status` — View claim counts, confidence distribution, tensions, questions
- `/knowledge-review` — Activate draft claims, resolve tensions, triage questions
- `/knowledge-update` — Run between-session learning pipeline (all 8 stages)
- `/session-save` — Flush session observations to the session log
