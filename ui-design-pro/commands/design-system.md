---
description: Plan or extend a design token system with spacing, color, type, and component variant matrices. Triggers visual-architect agent with design-systems reference.
allowed-tools: Read, Write, Edit, Grep, Glob, LS
argument-hint: <scope-of-design-system-work>
---

Plan or extend the design token system for the current project.

1. Load `skills/design-theory/references/design-systems.md` for token hierarchy and scale principles.
2. Load the visual-architect agent to audit or plan the system.
3. Run /detect-stack to map what tokens already exist (Tailwind theme, CSS custom properties, open-props scales).
4. For each token layer (color, spacing, type, radius, shadow, easing), evaluate:
   - Does a scale exist? Is it consistent?
   - Does it follow a modular ratio or step function?
   - Are semantic aliases defined on top of primitives?
   - Does dark mode work through semantic tokens, not hardcoded values?
5. Produce a token architecture document covering:
   - Primitive scales (raw values)
   - Semantic aliases (purpose-mapped tokens)
   - Component-level tokens (if component library is involved)
   - Missing scales that need to be defined
6. If extending: write the new tokens into `tailwind.config.*` or CSS custom properties, following the existing pattern.
7. If starting fresh: propose a token system using Open Props scales as the primitive layer, with Tailwind config as the semantic layer.

Output a token matrix and migration notes for any deprecated values.
