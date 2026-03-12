# Interaction Design

## Fitts's Law

**Targets that are larger and closer are faster to click.**

The formal model: `T = a + b × log₂(2D/W)` — time to click a target is proportional to distance (D) and inversely proportional to target width (W).

### Practical Implications

**Size primary actions generously.** The primary CTA button should be 44–56px tall. Secondary actions can be 32–40px. Tertiary links can be smaller.

**Place frequent actions near the cursor.** Context menus, right-click menus, and hover actions reduce travel distance. Toolbar actions should be in the top-left where the eye lands first.

**Corner and edge targets are infinitely wide.** A button flush with the screen edge can be clicked without precise aim — the edge stops the cursor. Use this for persistent navigation items at screen edges.

**Expand click targets beyond visual bounds.** A 16px icon does not need a 16px tap area. Expand the hit zone with padding while keeping the visual size small:

```css
.icon-button {
  padding: 10px; /* 16px icon + 20px invisible padding = 36px tap target */
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

### WCAG 2.5.8 Target Size

Minimum 24×24px for non-inline interactive controls (WCAG 2.2 Level AA). Recommended: 44×44px for primary actions (Apple Human Interface Guidelines).

---

## Hick's Law

**More choices = longer decision time.**

`T = b × log₂(n + 1)` — reaction time grows logarithmically with number of options.

### Reducing Choice Paralysis

**Progressive disclosure:** Show fewer options by default; reveal more on demand. A navigation menu with 5 top-level items performs better than one with 12.

**Default selection:** Pre-select the most common option. The user's job becomes confirming, not choosing.

**Chunking:** Group related options so the user scans groups, not individual items. A menu of 9 items organized into 3 groups of 3 loads faster cognitively than a flat list of 9.

**Eliminate options, don't hide them:** If an option is rarely used, remove it from the primary flow entirely. Hidden options are still options — they create uncertainty.

### Applied to Navigation

- Primary navigation: max 5–7 items
- Dropdown menus: max 7–10 items before needing groups
- Forms: one question per page for high-stakes flows (onboarding, checkout)
- Settings: group settings by category; don't show all settings on one page

---

## Affordances and Signifiers

An **affordance** is what an element can do (a button can be pressed). A **signifier** is what communicates that affordance visually.

Bad design: affordances without signifiers. The user cannot tell what is clickable.

### Visual Signifiers by Control Type

| Control type | Signifiers |
|-------------|-----------|
| Button | Elevated surface (shadow or border), filled background, cursor: pointer |
| Link | Color contrast, underline (or hover underline), cursor: pointer |
| Input | Border with clear inset, visible focus ring, label |
| Toggle/checkbox | Clear checked vs unchecked visual states, not just color |
| Drag handle | ⠿ icon, dashed border, cursor: grab |
| Sortable item | Drag handle visible on hover/focus |
| Expandable | Caret/chevron pointing in direction of expansion |

### The Hover State

Hover states are signifiers for interactive elements. They confirm "you can click this."

- Buttons: slightly lighter/darker background on hover
- Links: underline appears on hover (if not always shown)
- Cards (if clickable): slight shadow increase or border color change
- Table rows (if clickable): background tint on hover

**If an element is not interactive, it should not change on hover.** Hover reactions on static elements confuse users into clicking something inert.

---

## Feedback Loops

### Immediate Feedback (< 100ms)

Visual state change that happens faster than the eye perceives a gap. Button press down state, input focus ring, toggle flip. These must happen synchronously on the user gesture — no waiting for an API call.

### Short-term Feedback (100ms–1s)

Loading indicators, progress bars, skeleton screens. Span the gap between user action and system response.

**Under 400ms:** No loading indicator needed. Anything faster than ~400ms feels instantaneous. Show it immediately if the response might exceed 400ms.

**400ms–1s:** Show a subtle spinner or pulse. Full skeleton screens are overkill.

**Over 1s:** Use a skeleton screen that matches the content layout. Show real progress if available.

### Completion Feedback

Tells the user their action succeeded. Use toast notifications for background operations. Use inline success states (green checkmark, success banner) for form submissions.

**Rules:**
- Success feedback should auto-dismiss (3–5 seconds for toasts)
- Error feedback should NOT auto-dismiss — the user needs to read and act on it
- Don't say "Success!" — say what specifically succeeded: "Profile updated", "File saved"

---

## Error Design

### Error Prevention vs. Error Recovery

Prevention is better than recovery. Before designing error messages, ask: could this error have been prevented?

| Prevention strategy | Example |
|--------------------|---------|
| Disable actions that can't succeed | Disable "Submit" if required fields are empty |
| Inline validation | Show format hints as user types |
| Confirm destructive actions | "Delete 12 items?" confirmation dialog |
| Smart defaults | Pre-fill with last-used value |
| Undo instead of confirm | Let user undo, remove confirmation step |

### Error Message Quality

Every error message must answer: **What went wrong, and what can the user do about it?**

| Bad | Good |
|-----|------|
| "Error occurred" | "Email already in use. Sign in instead, or use a different email." |
| "Invalid input" | "Password must be at least 8 characters and include a number." |
| "Request failed" | "Couldn't save. Check your connection and try again." |
| "403 Forbidden" | "You don't have permission to view this. Ask an admin for access." |

### Inline vs. Summary Errors

- **Inline errors** (below the field): for field-specific validation failures
- **Summary errors** (at top of form): for multi-field validation failures or server errors
- Never show both for the same error — pick one placement per error type

---

## Mental Models

Users approach software with a mental model built from prior experience. When the system model diverges from the mental model, confusion results.

### Matching Mental Models

**Use familiar metaphors.** A "Trash" or "Recycle Bin" leverages the physical world mental model — items can be recovered before final deletion.

**Respect platform conventions.** On mobile, swiping right typically means "back." Changing this creates disorientation.

**Confirm destructive divergence.** When the system does something the user didn't expect (auto-save, batch operations), explain it proactively.

### Progressive Disclosure and Mental Model Building

Show features as users need them, not all at once. This lets users build a mental model of the software incrementally:

1. **Novice view**: Core operations only
2. **Intermediate view**: Power features revealed after first successful use
3. **Expert view**: Keyboard shortcuts, batch operations, API access

---

## Gestalt Laws in Interface Design

| Law | Description | UI Application |
|-----|-------------|----------------|
| **Proximity** | Close objects are perceived as related | Labels closer to their inputs than to other labels |
| **Similarity** | Similar objects are perceived as related | All buttons share the same visual style |
| **Closure** | Open shapes are perceived as closed | Rounded corners on cards complete a visual boundary |
| **Continuity** | Eyes follow lines | Alignment grid creates implied lines across columns |
| **Figure/Ground** | Objects perceived as foreground or background | Modal backdrop creates clear figure (modal) vs ground (page) |
| **Common Fate** | Objects moving together are related | Accordion items that expand together are grouped |

---

## Quick Decision Framework

Before designing an interaction pattern, answer:

1. **What is the user trying to accomplish?** — Primary task, not the button's function
2. **How often will they do this?** — Frequent tasks get prominent placement; rare tasks can be buried
3. **What is the cost of error?** — High cost → confirm; Low cost → allow undo; Trivial → no friction
4. **What does the user already know?** — Leverage existing platform conventions before inventing new ones
5. **What feedback is required?** — Immediate state change, loading state, completion, and error all need distinct treatments
