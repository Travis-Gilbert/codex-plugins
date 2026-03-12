# Visual Fundamentals

## Color Theory

### Hue, Saturation, Value

Color has three independent axes:
- **Hue**: the wavelength (red, blue, yellow, etc.)
- **Saturation**: the intensity/purity of the color
- **Value**: the lightness/darkness

Designers rarely manipulate all three simultaneously. Most UI decisions operate on saturation and value while keeping hue stable — creating a scale within a single hue family.

### Perceptual Uniformity

Not all color scales are perceptually uniform. A scale that looks mathematically even (e.g., HSL 10%, 20%, 30%...) does not look visually even. Radix Colors and Open Props are designed around **perceptual uniformity** — each step looks equally distant from the next.

Use these scales rather than generating your own with HSL arithmetic.

### Semantic Color Roles

| Role | Purpose | Example |
|------|---------|---------|
| **Surface** | Page and card backgrounds | `--color-surface-1` through `--color-surface-4` |
| **Content** | Text and icons | `--color-content-1` (primary) through `--color-content-3` (muted) |
| **Brand** | Primary interactive color | `--color-brand` |
| **Accent** | Secondary emphasis | `--color-accent` |
| **Destructive** | Danger, delete, error | `--color-destructive` |
| **Success** | Positive confirmation | `--color-success` |
| **Warning** | Caution state | `--color-warning` |
| **Border** | Dividers, outlines | `--color-border` |

**Rule:** Never use raw color values (hex, HSL) in component code. Always use semantic tokens that can be overridden in dark mode.

### Color Contrast Requirements (WCAG 2.2)

| Text type | Minimum ratio | Enhanced ratio |
|-----------|--------------|----------------|
| Normal text (< 18pt) | 4.5:1 (AA) | 7:1 (AAA) |
| Large text (≥ 18pt bold or ≥ 24pt) | 3:1 (AA) | 4.5:1 (AAA) |
| UI components and focus indicators | 3:1 (AA) | — |

### Color Independence

**Never convey information through color alone.** Every color-coded element needs a second signal:
- Status dot (red/green) → add label: "Error" / "Active"
- Chart line colors → add pattern or label
- Required field (red asterisk) → add "Required" text
- Form error highlight (red border) → add error message text

---

## Typography

### Type Scale Principles

The **measure** (line length) determines readability. Optimal: 45–75 characters per line. At screen widths that exceed this, constrain the content container, not the font size.

A **modular scale** uses a constant ratio to generate harmonious sizes. Common ratios:
- **Minor Third (1.200)**: Compact, information-dense
- **Major Third (1.250)**: Balanced for most UIs
- **Perfect Fourth (1.333)**: Clear hierarchy, editorial

Example at 1rem base with Major Third:
```
xs:   0.640rem (10px)
sm:   0.800rem (12.8px)
base: 1.000rem (16px)
md:   1.250rem (20px)
lg:   1.563rem (25px)
xl:   1.953rem (31px)
2xl:  2.441rem (39px)
3xl:  3.052rem (48px)
```

### Type Weight Hierarchy

Use weight to establish hierarchy, not size alone. A bold body text competes with a larger heading.

| Hierarchy level | Weight |
|-----------------|--------|
| Display heading | 700–900 |
| Section heading | 600–700 |
| Label / caption | 500–600 |
| Body text | 400 |
| Muted / secondary | 400, reduced opacity |

### Letter Spacing

- Uppercase labels benefit from `tracking-wide` (0.05em) or `tracking-widest` (0.1em)
- Headings at display sizes benefit from slightly negative tracking (`-0.01em` to `-0.02em`)
- Body text: leave at default (0)

### Line Height

| Context | Line height |
|---------|-------------|
| Display headings | 1.0–1.2 |
| Subheadings | 1.2–1.35 |
| Body text | 1.5–1.65 |
| Compact UI (tables, lists) | 1.25–1.4 |

---

## Spacing Systems

### The 4px Grid

Most UI frameworks (Tailwind, Open Props) use a 4px base unit. Every spacing value should be a multiple of 4px:
- `4px` (1 unit): micro gaps, icon padding
- `8px` (2 units): inner padding, tight spacing
- `12px` (3 units): compact component padding
- `16px` (4 units): standard content padding
- `24px` (6 units): section breathing room
- `32px` (8 units): large section gaps
- `48px` (12 units): major section separation
- `64px` (16 units): page-level white space

**Breaking the grid** should be intentional — for optical corrections (icon optical centering, border radius relationships).

### Density Levels

| Density | Use case | Padding example |
|---------|----------|-----------------|
| **Tight** | Tables, data-dense dashboards, code | 4px–8px |
| **Default** | Forms, cards, navigation | 12px–16px |
| **Comfortable** | Marketing, landing pages, reading | 24px–48px |

Mixing density levels within a single component creates visual inconsistency. Choose one density level per component, then be consistent.

### Proximity and Grouping (Gestalt)

Items closer together are perceived as related. Use spacing to communicate relationships:
- Elements in the same group: tight spacing (4–8px)
- Related groups: medium spacing (16–24px)
- Separate sections: large spacing (32–64px)

A label is closer to its input than to the previous input's label. If it is not, the form feels broken.

---

## Visual Hierarchy Signals

Hierarchy is communicated through six properties, in rough order of strength:

1. **Size**: Larger = more important
2. **Weight**: Bolder = more important
3. **Color/Value**: Higher contrast = more prominent
4. **Position**: Top-left = reads first (LTR cultures)
5. **Spacing**: More surrounding space = more prominent
6. **Motion**: Moving elements attract attention first

**Rule:** A page where everything has the same size, weight, and position has no hierarchy. The user cannot identify what to do next.

### F-Pattern and Z-Pattern Reading

- **F-Pattern**: Dense text pages — users read the first line, then scan left margins
- **Z-Pattern**: Sparse pages with clear sections — eyes travel Z across top, then down, then across bottom

For web applications: follow the F-pattern. Primary actions go in the left column or top-left of a content area.
