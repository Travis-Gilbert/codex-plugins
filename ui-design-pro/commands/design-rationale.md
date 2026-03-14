---
description: Generate a structured design rationale for a screen or component, grounded in design-theory references and concrete tradeoffs. Use when you need to document WHY a design works, justify decisions for PR review, or analyze an existing screen before making changes.
allowed-tools: Read, Grep, Glob, LS
argument-hint: <file-or-description-of-ui>
---

Generate a structured design rationale for the specified screen, component,
or described UI.

## Process

1. Load all relevant design-theory references:
   - `skills/design-theory/references/visual-fundamentals.md`
   - `skills/design-theory/references/layout-composition.md`
   - `skills/design-theory/references/interaction-design.md`
   - `skills/design-theory/references/behavioral-design.md`
   - `skills/design-theory/references/object-rendering.md`
   - `skills/design-theory/references/accessibility.md`

2. Examine the target UI (code, description, or both) and identify:
   - **Screen archetype**: monitoring, triage, authoring, configuration,
     or exploration. Each archetype carries different density expectations,
     interaction patterns, and state priorities.
   - **Density level**: low (marketing, onboarding), medium (detail views,
     forms), or high (dashboards, admin). Density should match user task
     frequency and expertise.
   - **Primary user task(s)**: what the user came to this screen to do.
     This determines what gets the most visual weight.
   - **Key objects being represented**: list each content type and whether
     they are homogeneous or heterogeneous. Heterogeneous collections
     should trigger polymorphic rendering analysis.

3. Synthesize a structured rationale with these sections:

   **Intent**
   What the screen is for and who it serves. One clear paragraph that
   names the primary task and the user context.

   **Hierarchy**
   How visual weight and placement support the primary task. Name the
   specific elements that carry primary, secondary, and tertiary weight.
   Reference layout-composition.md principles (Gestalt, scanning patterns,
   whitespace-as-structure). Call out any hierarchy failures: equal-weight
   elements competing, decoration without purpose, or buried primary actions.

   **Object Model**
   How different object types are represented. If the screen displays
   mixed content types, evaluate whether polymorphic rendering is used
   and whether it should be. Reference object-rendering.md. Name each
   content type and describe its visual identity: density, chrome, orientation,
   and emphasis level. Flag uniform card grids for heterogeneous data.

   **Interaction Model**
   How users move through the flow. Apply Fitts's Law (are primary actions
   large and near the focus?), Hick's Law (are choices manageable?), and
   progressive disclosure (are advanced controls behind disclosure?).
   Reference interaction-design.md. Name the primary, secondary, and
   tertiary actions and evaluate their placement.

   **Behavior and States**
   How loading, empty, error, success, and disabled states support
   real-world use. Reference state coverage expectations. For each missing
   state, describe the user experience when that state is encountered.
   Prioritize: empty and error states matter most (users encounter them
   when something goes wrong, which is when they need the most guidance).

   **Accessibility**
   How contrast, focus management, semantics, and motion support different
   users. Reference accessibility.md. Check: color-only communication,
   focus-visible styles, keyboard navigation, ARIA roles on custom controls,
   touch targets, heading hierarchy, and reduced-motion respect.

   **Tradeoffs**
   What this design deliberately optimizes for and what it chose not to
   optimize. Every design decision has a cost. Name it explicitly.
   Examples: "Optimized for scan speed at the expense of information density"
   or "Prioritized mobile ergonomics over desktop data density." This
   section prevents vague "it should be better" feedback.

4. Tie each section explicitly to named principles from the references.
   Do not write "the hierarchy could be improved." Write "the hierarchy
   fails Gestalt proximity: the filter controls are spatially distant from
   the data they affect, breaking the grouping signal." Name the principle,
   name the violation, name the consequence.

5. Output both:

   **Full rationale**: 1-2 concise paragraphs per section. Not a textbook
   essay. Each paragraph should contain a claim, the principle that supports
   it, and the implication for implementation.

   **For PRs summary**: 3-5 bullet points explaining the most important
   design decisions for someone reviewing the implementation. These should
   be specific enough that a reviewer can verify them: "Primary action
   (Save) is pinned bottom-right at 48px height, satisfying Fitts's Law
   for the most common task" rather than "Good button placement."
