---
description: Detect the existing UI stack in a project and report framework, component library, icon system, overlays, feedback, tokens, and animation patterns. Triggers stack-detector agent.
allowed-tools: Read, Grep, Glob, LS, Bash
argument-hint: <repo-root-path>
---

Detect and map the complete UI technology stack of the specified project.

1. Load `skills/ui-engineering/references/stack-detection.md`.
2. Load the stack-detector agent.
3. If a repo-root-path argument is provided, work from that directory. Otherwise work from the current directory.
4. Run `scripts/detect_ui_stack.sh <repo-root>` to get the automated detection output.
5. Supplement the script output with deeper analysis:
   - Read `package.json` for all UI-related dependencies
   - Check for `components.json` (shadcn config), `tailwind.config.*`, `postcss.config.*`
   - Scan `src/components/` or `components/` for existing component implementations
   - Check for existing dialog, drawer, toast, and command palette implementations
   - Look for CSS custom properties or design token files
6. Produce a comprehensive stack report (see stack-detector agent for full report format).
7. Save the report as `.claude/stack-detection.json` for use by other agents.
8. End with a clear list of:
   - **USE**: libraries already in the project
   - **AVOID**: libraries that would duplicate existing functionality
   - **CONSIDER**: compatible additions that fill gaps
