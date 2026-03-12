// Button with CVA variant system
//
// Demonstrates:
// - cva() for type-safe variant management
// - VariantProps for TypeScript inference
// - asChild / Slot for polymorphic rendering
// - Full interactive state coverage (hover, active, focus-visible, disabled, loading)

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

// ─── Variants ────────────────────────────────────────────────────────────────

const buttonVariants = cva(
  // Base classes — always applied
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-button text-sm font-medium transition-colors " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 " +
  "disabled:pointer-events-none disabled:opacity-50 " +
  "active:scale-[0.98]",
  {
    variants: {
      variant: {
        default:     "bg-brand text-white hover:bg-brand-hover",
        destructive: "bg-destructive text-white hover:bg-destructive/90",
        outline:     "border border-border bg-transparent hover:bg-surface-2 hover:text-content-1",
        ghost:       "hover:bg-surface-2 hover:text-content-1",
        link:        "text-brand underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm:      "h-8 px-3 text-xs",
        lg:      "h-12 px-8",
        icon:    "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size:    "default",
    },
  }
);

// ─── Types ────────────────────────────────────────────────────────────────────

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

// ─── Component ────────────────────────────────────────────────────────────────

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading = false, children, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        ref={ref}
        disabled={disabled || loading}
        className={cn(buttonVariants({ variant, size, className }))}
        {...props}
      >
        {loading ? (
          <>
            <svg
              className="h-4 w-4 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>Loading…</span>
          </>
        ) : (
          children
        )}
      </Comp>
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };

// ─── Usage examples ───────────────────────────────────────────────────────────

export function ButtonShowcase() {
  const [loading, setLoading] = React.useState(false);

  const handleSave = async () => {
    setLoading(true);
    await new Promise(r => setTimeout(r, 1500));
    setLoading(false);
  };

  return (
    <div className="flex flex-wrap gap-3 p-6">
      {/* Variants */}
      <Button variant="default">Save changes</Button>
      <Button variant="outline">Cancel</Button>
      <Button variant="ghost">Learn more</Button>
      <Button variant="destructive">Delete account</Button>
      <Button variant="link">View documentation</Button>

      {/* Sizes */}
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>

      {/* States */}
      <Button disabled>Disabled</Button>
      <Button loading={loading} onClick={handleSave}>Save changes</Button>

      {/* asChild: renders as <a> with button styles */}
      <Button variant="outline" asChild>
        <a href="/dashboard">Go to dashboard</a>
      </Button>
    </div>
  );
}
