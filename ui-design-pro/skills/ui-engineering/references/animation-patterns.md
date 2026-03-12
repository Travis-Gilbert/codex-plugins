# Animation Patterns

## When to Animate vs. When Not To

CSS handles transitions. Motion handles everything else.

### Use CSS transitions for:
- Color changes on hover/focus
- Opacity fades on simple show/hide
- Border and shadow changes
- Text color shifts

```css
/* CSS is correct here — instant, no JS overhead */
.button {
  transition: background-color 150ms ease, box-shadow 150ms ease;
}
.button:hover {
  background-color: var(--color-brand-hover);
}
```

### Use Motion (`motion/react`) for:
- Enter/exit animations (AnimatePresence)
- Layout changes (items reordering, expanding)
- Drag gestures
- Choreographed sequences
- Spring-physics animations that feel physical

**Source:** `refs/motion/packages/motion/` and `refs/motion/packages/motion-dom/`

---

## Import Conventions

```tsx
// Always import from 'motion/react' (not 'framer-motion')
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform, LayoutGroup } from 'motion/react'
```

`motion` and `framer-motion` are the same package. Use `motion/react` — it is the current canonical import.

---

## Spring Physics

A spring animation is defined by three parameters, not a duration:

| Parameter | Effect | Typical range |
|-----------|--------|---------------|
| `stiffness` | How fast the spring moves | 100–600 |
| `damping` | How much it resists bouncing | 10–50 |
| `mass` | How heavy it feels | 0.5–2.0 |

```tsx
// Snappy UI interaction — high stiffness, medium damping
const snappy = { type: 'spring', stiffness: 400, damping: 30 }

// Bouncy/playful — lower damping allows overshoot
const bouncy = { type: 'spring', stiffness: 300, damping: 20 }

// Smooth/heavy — lower stiffness, higher damping
const smooth = { type: 'spring', stiffness: 150, damping: 25, mass: 1.5 }

// No bounce — critically damped (use for menus, dropdowns)
const noBounce = { type: 'spring', stiffness: 400, damping: 40 }
```

**Rule:** UI elements (dropdowns, modals, cards) should use no-bounce or minimal-bounce springs. Playful/decorative elements can use bouncy springs. Never use a bounce on destructive confirmations.

---

## Enter / Exit: AnimatePresence

`AnimatePresence` is required for exit animations. Without it, React unmounts immediately and the exit animation never runs.

```tsx
// Fade in/out
function Toast({ message, visible }: { message: string; visible: boolean }) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          key="toast"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 8 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
          className="fixed bottom-4 right-4 rounded-card bg-surface-4 px-4 py-3 shadow-toast text-sm text-content-1"
        >
          {message}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
```

**AnimatePresence rules:**
1. `AnimatePresence` must wrap the conditional element — not be inside it
2. The animated child must have a `key` prop
3. The animated child must have an `exit` prop

### Staggered list entrance

```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,    // 50ms between items
    },
  },
}

const item = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0 },
}

function List({ items }: { items: string[] }) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show" className="space-y-2">
      {items.map((text, i) => (
        <motion.li key={i} variants={item} className="rounded-card bg-surface-2 px-4 py-3 text-sm text-content-1">
          {text}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

**Variants pattern:** Define animation states as named variants (`hidden`, `show`) rather than inline objects. Parent variants automatically propagate to children — children only need `variants={item}`.

---

## Layout Animations

Layout animations animate between two DOM positions automatically using the FLIP technique. This is the correct approach for reordering, expanding, and collapsing elements.

```tsx
// Items that reorder should have layout prop
function SortableList({ items }: { items: { id: string; title: string }[] }) {
  return (
    <ul>
      {items.map(item => (
        <motion.li key={item.id} layout className="border-b border-border py-3 px-4 text-sm">
          {item.title}
        </motion.li>
      ))}
    </ul>
  )
}
```

### Shared layout: `layoutId`

`layoutId` animates an element between two different DOM positions — perfect for selected state indicators, expanding cards, and hero-to-detail transitions.

```tsx
// Tab underline that slides between tabs
function Tabs({ tabs, active, onSelect }: {
  tabs: string[]
  active: string
  onSelect: (tab: string) => void
}) {
  return (
    <div className="flex gap-1 border-b border-border">
      {tabs.map(tab => (
        <button
          key={tab}
          onClick={() => onSelect(tab)}
          className="relative px-4 py-2 text-sm font-medium"
        >
          <span className={cn(active === tab ? 'text-brand' : 'text-content-3')}>
            {tab}
          </span>
          {active === tab && (
            <motion.div
              layoutId="tab-indicator"   // Must match across all tabs
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand"
              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            />
          )}
        </button>
      ))}
    </div>
  )
}
```

**`layoutId` rules:**
- The `layoutId` must be unique within the closest `LayoutGroup` (or globally if no group)
- The `key` must NOT match the `layoutId` — they serve different purposes
- Both mount and unmount positions must be in the DOM for the animation to work

---

## Gesture Animations

### Hover and tap states

```tsx
// Physical button press
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: 'spring', stiffness: 400, damping: 20 }}
  className="rounded-button bg-brand px-4 py-2 text-sm font-medium text-white"
>
  Submit
</motion.button>
```

**Scale values for button press:**
- Hover: `1.01` to `1.03` (subtle)
- Tap: `0.96` to `0.99` (noticeable but not jarring)
- Never scale up on tap — physical buttons press in, not out

### Drag

```tsx
function DraggableCard({ title }: { title: string }) {
  return (
    <motion.div
      drag
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}  // Snap back
      dragElastic={0.1}
      whileDrag={{ scale: 1.05, cursor: 'grabbing' }}
      className="cursor-grab rounded-card bg-surface-2 px-4 py-3 shadow-card"
    >
      {title}
    </motion.div>
  )
}
```

---

## useMotionValue and useTransform

For scroll-driven animations and connecting motion values:

```tsx
function ParallaxHero() {
  const { scrollY } = useScroll()
  const y = useTransform(scrollY, [0, 500], [0, -150])  // Input → Output range
  const opacity = useTransform(scrollY, [0, 300], [1, 0])

  return (
    <div className="relative h-screen overflow-hidden">
      <motion.div style={{ y, opacity }} className="absolute inset-0">
        <img src="/hero.jpg" alt="" className="h-full w-full object-cover" />
      </motion.div>
    </div>
  )
}
```

`useTransform` maps one motion value range to another. This is more performant than re-rendering because it operates outside React's render cycle.

---

## Respecting Reduced Motion

Always respect `prefers-reduced-motion`. Motion provides a hook:

```tsx
import { useReducedMotion } from 'motion/react'

function AnimatedCard({ children }: { children: React.ReactNode }) {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={
        shouldReduceMotion
          ? { duration: 0.01 }
          : { type: 'spring', stiffness: 400, damping: 30 }
      }
    >
      {children}
    </motion.div>
  )
}
```

**Rule:** When `shouldReduceMotion` is true, keep the opacity transition (communicates state change) but eliminate spatial movement. Never remove all transitions — opacity change still communicates that something appeared.

---

## Performance Rules

**Layout thrashing:** `layout` prop triggers getBoundingClientRect. Use sparingly. Never put `layout` on every element in a long list.

**Transform-only:** Always animate `x`, `y`, `scale`, `rotate` — not `left`, `top`, `width`, `height`. Non-transform properties trigger layout recalculation.

```tsx
// WRONG: animates non-GPU-composited property
<motion.div animate={{ width: 200 }}>

// CORRECT: use scale instead
<motion.div animate={{ scaleX: 1.5 }} style={{ transformOrigin: 'left' }}>

// ALSO CORRECT: position with transform
<motion.div animate={{ x: 200 }}>
```

**Variants over per-element:** Define animation state as variants on a parent and propagate. Avoids duplicate transition objects on every child.

---

## Common Patterns Reference

| Pattern | Implementation |
|---------|---------------|
| Modal enter/exit | `AnimatePresence` + `initial={{opacity:0, scale:0.95}}` + spring |
| Menu open/close | `AnimatePresence` + `initial={{opacity:0, y:-8}}` + no-bounce spring |
| Tab indicator | `layoutId` on the underline/background element |
| Card expand | `layout` on card + `AnimatePresence` for expanded content |
| List reorder | `layout` on each `<motion.li>` |
| Staggered entrance | `staggerChildren` on parent variants |
| Scroll parallax | `useScroll` + `useTransform` |
| Physical button | `whileHover={{ scale: 1.02 }}` + `whileTap={{ scale: 0.98 }}` |
