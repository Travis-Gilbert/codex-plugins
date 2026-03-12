// Radix Dialog with Motion animation
//
// Demonstrates:
// - Radix Dialog primitives (Root, Trigger, Portal, Overlay, Content, Title, Description, Close)
// - AnimatePresence for exit animation (critical: must wrap conditional render)
// - Spring physics transition on overlay and panel
// - Focus management via Radix (automatic trap + restore)
// - Controlled and uncontrolled usage patterns
// - Full ARIA: DialogTitle, DialogDescription, close button

import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { AnimatePresence, motion } from "motion/react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

// ─── Spring presets ───────────────────────────────────────────────────────────

const OVERLAY_SPRING = { type: "spring" as const, stiffness: 300, damping: 35, mass: 0.8 };
const PANEL_SPRING   = { type: "spring" as const, stiffness: 380, damping: 40, mass: 0.9 };

// ─── Animated subcomponents ───────────────────────────────────────────────────

// Overlay: fade in/out
const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay ref={ref} asChild {...props}>
    <motion.div
      className={cn(
        "fixed inset-0 z-50 bg-black/50 backdrop-blur-sm",
        className
      )}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={OVERLAY_SPRING}
    />
  </DialogPrimitive.Overlay>
));
DialogOverlay.displayName = "DialogOverlay";

// Content: slide up + fade
const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPrimitive.Content ref={ref} asChild {...props}>
    <motion.div
      className={cn(
        "fixed left-1/2 top-1/2 z-50 w-full max-w-md",
        "rounded-dialog border border-border bg-surface-1 p-6 shadow-xl",
        "focus:outline-none",
        className
      )}
      initial={{ opacity: 0, y: 24, x: "-50%", translateY: "-46%" }}
      animate={{ opacity: 1, y: 0,  x: "-50%", translateY: "-50%" }}
      exit={{    opacity: 0, y: 12, x: "-50%", translateY: "-46%" }}
      transition={PANEL_SPRING}
    >
      {/* Close button */}
      <DialogPrimitive.Close
        className={cn(
          "absolute right-4 top-4 rounded-sm p-1",
          "text-content-3 hover:text-content-1 transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2",
        )}
        aria-label="Close"
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </DialogPrimitive.Close>

      {children}
    </motion.div>
  </DialogPrimitive.Content>
));
DialogContent.displayName = "DialogContent";

// ─── Dialog wrapper with AnimatePresence ─────────────────────────────────────
//
// Key insight: AnimatePresence MUST be outside the conditional, but INSIDE
// DialogPrimitive.Portal so Radix controls the DOM lifecycle.

interface DialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  trigger: React.ReactNode;
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function Dialog({
  open: controlledOpen,
  onOpenChange,
  trigger,
  title,
  description,
  children,
  className,
}: DialogProps) {
  const [internalOpen, setInternalOpen] = React.useState(false);

  // Support both controlled and uncontrolled usage
  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? controlledOpen : internalOpen;
  const setOpen = isControlled
    ? (onOpenChange ?? (() => {}))
    : setInternalOpen;

  return (
    <DialogPrimitive.Root open={open} onOpenChange={setOpen}>
      <DialogPrimitive.Trigger asChild>
        {trigger}
      </DialogPrimitive.Trigger>

      <DialogPrimitive.Portal>
        <AnimatePresence>
          {open && (
            <>
              <DialogOverlay />
              <DialogContent className={className}>
                <DialogPrimitive.Title className="text-lg font-semibold text-content-1 pr-8">
                  {title}
                </DialogPrimitive.Title>
                {description && (
                  <DialogPrimitive.Description className="mt-1 text-sm text-content-3">
                    {description}
                  </DialogPrimitive.Description>
                )}
                <div className="mt-4">{children}</div>
              </DialogContent>
            </>
          )}
        </AnimatePresence>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}

// ─── Usage examples ───────────────────────────────────────────────────────────

export function DialogShowcase() {
  const [deleteOpen, setDeleteOpen] = React.useState(false);
  const [saving, setSaving]         = React.useState(false);

  const handleSave = async () => {
    setSaving(true);
    await new Promise(r => setTimeout(r, 1200));
    setSaving(false);
    setDeleteOpen(false);
  };

  return (
    <div className="flex flex-wrap gap-3 p-6">
      {/* Uncontrolled: simplest usage */}
      <Dialog
        trigger={<button className="rounded-button bg-brand text-white px-4 py-2 text-sm font-medium hover:bg-brand-hover transition-colors">Open settings</button>}
        title="Settings"
        description="Manage your account preferences."
      >
        <p className="text-sm text-content-2">Settings content goes here.</p>
        <div className="mt-4 flex justify-end gap-2">
          <DialogPrimitive.Close className="rounded-button border border-border px-4 py-2 text-sm hover:bg-surface-2 transition-colors">
            Cancel
          </DialogPrimitive.Close>
          <button className="rounded-button bg-brand text-white px-4 py-2 text-sm hover:bg-brand-hover transition-colors">
            Save
          </button>
        </div>
      </Dialog>

      {/* Controlled: delete confirmation with loading state */}
      <Dialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        trigger={
          <button
            className="rounded-button bg-destructive text-white px-4 py-2 text-sm font-medium hover:bg-destructive/90 transition-colors"
            onClick={() => setDeleteOpen(true)}
          >
            Delete account
          </button>
        }
        title="Are you absolutely sure?"
        description="This action cannot be undone. Your account and all associated data will be permanently deleted."
      >
        <div className="flex justify-end gap-2">
          <button
            onClick={() => setDeleteOpen(false)}
            className="rounded-button border border-border px-4 py-2 text-sm hover:bg-surface-2 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-button bg-destructive text-white px-4 py-2 text-sm hover:bg-destructive/90 disabled:opacity-50 disabled:pointer-events-none transition-colors"
          >
            {saving ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span>Deleting…</span>
              </>
            ) : (
              "Yes, delete account"
            )}
          </button>
        </div>
      </Dialog>
    </div>
  );
}
