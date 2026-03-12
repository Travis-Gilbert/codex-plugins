---
description: Add animation to a component or flow with performance and accessibility awareness. Triggers animation-engineer agent.
allowed-tools: Read, Write, Edit, Grep, Glob, LS, Bash
argument-hint: <what-to-animate>
---

Add purposeful animation to the specified component or flow.

1. Load `skills/ui-engineering/references/animation-patterns.md` and `skills/design-theory/references/animation-and-motion-principles.md`.
2. Load the animation-engineer agent.
3. Read the target component(s) to understand what currently exists and what motion is requested.
4. Evaluate whether the requested motion is warranted:
   - Does it orient the user? (new element appearing, panel sliding in)
   - Does it provide feedback? (action confirmed, state changed)
   - Does it communicate relationship? (connected elements, hierarchy)
   - If none of the above: do not add animation; report why.
5. Select the right tool (from animation-patterns.md):
   - Simple state change (color, opacity, scale) → CSS transition
   - Layout change, reorder, enter/exit → Motion `layout` + `AnimatePresence`
   - Gesture-driven (drag, swipe) → Motion gesture system
6. Verify Motion API from `refs/motion/packages/motion/src/` before writing implementation.
7. Implement with spring physics where appropriate; avoid duration-based animations for interactive elements.
8. Always implement `prefers-reduced-motion` — this is non-negotiable.
9. Verify: only `transform` and `opacity` are animated (no layout-triggering properties).
10. Run the project's formatter and linter.

Report what motion was added, why it serves the interface, and confirm reduced-motion handling.
