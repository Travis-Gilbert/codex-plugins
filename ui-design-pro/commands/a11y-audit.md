---
description: Audit a component, page, or flow for WCAG 2.2 accessibility conformance. Triggers a11y-auditor agent.
allowed-tools: Read, Grep, Glob, LS, Bash
argument-hint: <file-or-directory-to-audit>
---

Audit the specified file or directory for WCAG 2.2 accessibility conformance.

1. Load `skills/design-theory/references/accessibility.md` for the full criterion set and ARIA pattern library.
2. Load the a11y-auditor agent.
3. Read the target file(s) completely before beginning the audit.
4. Work through the WCAG checklist systematically:
   - Perceivable: text alternatives, contrast, info relationships, color independence
   - Operable: keyboard access, focus management, no traps, skip links, target sizes
   - Understandable: labels, error identification, language, predictable behavior
   - Robust: valid ARIA, custom widget patterns, status message announcements
5. For each violation, record:
   - WCAG criterion and success criterion number
   - Severity: Critical (A) / Serious (AA) / Minor (AAA)
   - Specific location in the code (file + line)
   - Concrete fix with corrected code
6. Check all interactive states: default, hover, focus, active, disabled, loading, error.
7. Verify any custom widget implements the correct ARIA pattern from the APG (Authoring Practices Guide).
8. Output a structured audit report sorted by severity.

For any animation found without `prefers-reduced-motion` handling, flag as Critical and include the fix.
