// Spring Animation Patterns
//
// Demonstrates:
// - Spring physics presets (snappy, gentle, stiff, bouncy)
// - AnimatePresence for enter/exit (required for exit animations)
// - layoutId for shared element transitions across list reorders
// - useReducedMotion: respects OS accessibility setting
// - Staggered list animation with delayChildren + staggerChildren
// - Gesture-driven drag with spring return

import * as React from "react";
import {
  motion,
  AnimatePresence,
  useReducedMotion,
  LayoutGroup,
  Reorder,
  useSpring,
  useTransform,
} from "motion/react";

// ─── Spring presets ───────────────────────────────────────────────────────────
//
// Use these consistently across the project for a unified motion vocabulary.

export const spring = {
  // Navigation, overlays, modals — noticeable but not bouncy
  snappy: { type: "spring" as const, stiffness: 380, damping: 40, mass: 0.8 },

  // Cards, content reveals, tooltips — smooth, professional
  gentle: { type: "spring" as const, stiffness: 260, damping: 28, mass: 1.0 },

  // Micro-interactions: button press, toggle — instant feel
  stiff:  { type: "spring" as const, stiffness: 600, damping: 50, mass: 0.6 },

  // Celebratory: success states, badge animations — playful
  bouncy: { type: "spring" as const, stiffness: 320, damping: 18, mass: 0.9 },
};

// ─── 1. AnimatePresence — mount/unmount with exit animation ──────────────────

export function PresenceDemo() {
  const [show, setShow] = React.useState(true);
  const reduceMotion = useReducedMotion();

  return (
    <div className="space-y-3 p-6">
      <button
        onClick={() => setShow(v => !v)}
        className="rounded-button bg-brand text-white px-4 py-2 text-sm hover:bg-brand-hover transition-colors"
      >
        {show ? "Hide" : "Show"}
      </button>

      {/* AnimatePresence required: renders exit animation before DOM removal */}
      <AnimatePresence mode="wait">
        {show && (
          <motion.div
            key="panel"
            initial={{ opacity: 0, y: reduceMotion ? 0 : 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{   opacity: 0, y: reduceMotion ? 0 : -8 }}
            transition={spring.gentle}
            className="rounded-card border border-border bg-surface-2 px-6 py-4"
          >
            <p className="text-sm text-content-2">This panel animates in and out.</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ─── 2. Staggered list ───────────────────────────────────────────────────────

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      delayChildren: 0.05,
      staggerChildren: 0.06,
    },
  },
};

const itemVariants = {
  hidden:  { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: spring.gentle },
};

interface ListItem { id: string; label: string }

export function StaggeredList({ items }: { items: ListItem[] }) {
  const reduceMotion = useReducedMotion();

  // When motion is reduced: skip stagger, just fade
  const container = reduceMotion
    ? { hidden: {}, visible: { transition: { staggerChildren: 0 } } }
    : containerVariants;

  const item = reduceMotion
    ? { hidden: { opacity: 0 }, visible: { opacity: 1 } }
    : itemVariants;

  return (
    <motion.ul
      variants={container}
      initial="hidden"
      animate="visible"
      className="space-y-2 p-6"
    >
      {items.map(it => (
        <motion.li
          key={it.id}
          variants={item}
          className="rounded-card border border-border bg-surface-1 px-4 py-3 text-sm text-content-1"
        >
          {it.label}
        </motion.li>
      ))}
    </motion.ul>
  );
}

// ─── 3. layoutId — shared element transition ─────────────────────────────────
//
// Same layoutId on two components causes Motion to animate between them.
// LayoutGroup scopes the IDs to prevent conflicts across multiple instances.

export function SharedLayoutDemo() {
  const [selected, setSelected] = React.useState<string | null>(null);
  const reduceMotion = useReducedMotion();

  const tabs = ["Overview", "Activity", "Settings"];

  return (
    <LayoutGroup>
      <div className="flex gap-1 rounded-full bg-surface-2 p-1 w-fit">
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setSelected(tab)}
            className="relative px-4 py-1.5 text-sm font-medium rounded-full z-10 transition-colors"
            style={{
              color: selected === tab ? "var(--color-brand)" : "var(--color-content-3)",
            }}
          >
            {/* Shared layout pill — moves smoothly between tabs */}
            {selected === tab && (
              <motion.span
                layoutId="tab-pill"
                className="absolute inset-0 rounded-full bg-surface-1 shadow-sm"
                transition={reduceMotion ? { duration: 0.01 } : spring.snappy}
              />
            )}
            <span className="relative">{tab}</span>
          </button>
        ))}
      </div>
    </LayoutGroup>
  );
}

// ─── 4. Drag with spring return ───────────────────────────────────────────────

export function DragCard() {
  const x = useSpring(0, spring.snappy);
  const y = useSpring(0, spring.snappy);

  // Subtle rotation based on horizontal drag position
  const rotate = useTransform(x, [-200, 200], [-8, 8]);

  return (
    <div className="flex items-center justify-center h-48 p-6">
      <motion.div
        drag
        dragElastic={0.15}
        dragMomentum={false}
        style={{ x, y, rotate }}
        onDragEnd={() => {
          x.set(0);
          y.set(0);
        }}
        whileDrag={{ scale: 1.04, cursor: "grabbing" }}
        className="rounded-card border border-border bg-surface-1 shadow-md px-6 py-4 cursor-grab select-none w-48 text-center"
      >
        <p className="text-sm font-medium text-content-1">Drag me</p>
        <p className="text-xs text-content-3 mt-0.5">Springs back on release</p>
      </motion.div>
    </div>
  );
}

// ─── 5. Reorderable list with layout animations ───────────────────────────────

export function ReorderableList() {
  const [items, setItems] = React.useState(["Task one", "Task two", "Task three", "Task four"]);
  const reduceMotion = useReducedMotion();

  return (
    <Reorder.Group
      axis="y"
      values={items}
      onReorder={setItems}
      className="space-y-2 p-6 w-72"
    >
      {items.map(item => (
        <Reorder.Item
          key={item}
          value={item}
          transition={reduceMotion ? { duration: 0.01 } : spring.gentle}
          className="rounded-card border border-border bg-surface-1 px-4 py-3 text-sm text-content-1 cursor-grab active:cursor-grabbing select-none"
          whileDrag={{ scale: 1.02, boxShadow: "0 8px 24px rgba(0,0,0,0.12)" }}
        >
          {item}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  );
}

// ─── 6. Reduced motion: wrapper component ────────────────────────────────────
//
// Wrap any animated component for effortless reduced motion compliance.

export function FadeIn({
  children,
  delay = 0,
}: {
  children: React.ReactNode;
  delay?: number;
}) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: reduceMotion ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={
        reduceMotion
          ? { duration: 0.01, delay: 0 }
          : { ...spring.gentle, delay }
      }
    >
      {children}
    </motion.div>
  );
}

// ─── Demo showcase ────────────────────────────────────────────────────────────

export function SpringShowcase() {
  const items = [
    { id: "a", label: "First item" },
    { id: "b", label: "Second item" },
    { id: "c", label: "Third item" },
  ];

  return (
    <div className="grid grid-cols-2 gap-6 p-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-content-3 mb-3">Presence</p>
        <PresenceDemo />
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-content-3 mb-3">Shared layout</p>
        <div className="pt-4 pl-2">
          <SharedLayoutDemo />
        </div>
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-content-3 mb-3">Staggered list</p>
        <StaggeredList items={items} />
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-content-3 mb-3">Drag spring</p>
        <DragCard />
      </div>
    </div>
  );
}
