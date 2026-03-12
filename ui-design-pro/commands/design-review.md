---
description: Review a UI component or page for design principle violations, accessibility issues, and polymorphic rendering opportunities. Triggers design-critic and a11y-auditor agents.
allowed-tools: Read, Grep, Glob, LS
argument-hint: <file-or-directory-to-review>
---

Review the specified file or directory for design quality.

1. Load the design-critic agent.
2. Load the a11y-auditor agent.
3. Run both reviews on the target.
4. Combine findings, deduplicate, and sort by severity.
5. For each Critical finding, propose a specific fix.
