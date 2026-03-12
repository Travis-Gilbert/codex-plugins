// Accessible Form — React Hook Form + Zod
//
// Demonstrates:
// - React Hook Form: register, handleSubmit, formState, watch
// - Zod schema: string validation, cross-field validation, error messages
// - Full ARIA: aria-required, aria-invalid, aria-describedby
// - role="alert" on error messages (announces on appearance)
// - Fieldset + legend for grouped inputs (radios, checkboxes)
// - Loading state: disabled form + inline spinner
// - Success state: replace form with confirmation

import * as React from "react";
import { useForm, type SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { cn } from "@/lib/utils";

// ─── Zod schema ───────────────────────────────────────────────────────────────

const signupSchema = z
  .object({
    name: z
      .string()
      .min(2, "Name must be at least 2 characters")
      .max(80, "Name must be under 80 characters"),

    email: z
      .string()
      .email("Enter a valid email address"),

    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Password must include an uppercase letter")
      .regex(/[0-9]/, "Password must include a number"),

    confirmPassword: z
      .string(),

    role: z.enum(["developer", "designer", "manager"], {
      errorMap: () => ({ message: "Select a role" }),
    }),

    termsAccepted: z
      .boolean()
      .refine(v => v === true, "You must accept the terms"),
  })
  .superRefine(({ password, confirmPassword }, ctx) => {
    if (confirmPassword !== password) {
      ctx.addIssue({
        code: "custom",
        path: ["confirmPassword"],
        message: "Passwords do not match",
      });
    }
  });

type SignupValues = z.infer<typeof signupSchema>;

// ─── Field components ──────────────────────────────────────────────────────────

interface FieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  id: string;
  label: string;
  error?: string;
}

function TextField({ id, label, error, required, className, ...props }: FieldProps) {
  return (
    <div className="space-y-1.5">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-content-1"
      >
        {label}
        {required && (
          <span aria-hidden="true" className="ml-0.5 text-destructive">*</span>
        )}
      </label>
      <input
        id={id}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        className={cn(
          "w-full rounded-input border bg-surface-3 px-3 py-2 text-sm text-content-1",
          "placeholder:text-content-3",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-0",
          "disabled:bg-surface-2 disabled:text-content-3 disabled:pointer-events-none",
          "transition-shadow",
          error ? "border-destructive" : "border-border",
          className
        )}
        {...props}
      />
      {error && (
        <p
          id={`${id}-error`}
          role="alert"
          className="text-xs text-destructive"
        >
          {error}
        </p>
      )}
    </div>
  );
}

interface SelectFieldProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  id: string;
  label: string;
  error?: string;
  options: { value: string; label: string }[];
}

function SelectField({ id, label, error, required, options, ...props }: SelectFieldProps) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-content-1">
        {label}
        {required && <span aria-hidden="true" className="ml-0.5 text-destructive">*</span>}
      </label>
      <select
        id={id}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        className={cn(
          "w-full rounded-input border bg-surface-3 px-3 py-2 text-sm text-content-1",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand",
          "disabled:bg-surface-2 disabled:pointer-events-none",
          error ? "border-destructive" : "border-border"
        )}
        {...props}
      >
        <option value="">Select…</option>
        {options.map(o => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
      {error && (
        <p id={`${id}-error`} role="alert" className="text-xs text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}

// ─── Main form ─────────────────────────────────────────────────────────────────

export function SignupForm() {
  const [status, setStatus] = React.useState<"idle" | "loading" | "success">("idle");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    mode: "onBlur",          // Validate on blur — not on every keystroke
    reValidateMode: "onChange", // Re-validate on change after first submit
  });

  const onSubmit: SubmitHandler<SignupValues> = async (_data) => {
    setStatus("loading");
    // Simulate API call
    await new Promise(r => setTimeout(r, 1400));
    setStatus("success");
  };

  if (status === "success") {
    return (
      <div
        role="status"
        aria-live="polite"
        className="rounded-card border border-border bg-surface-2 px-6 py-10 text-center"
      >
        <p className="text-base font-semibold text-content-1">Account created!</p>
        <p className="mt-1 text-sm text-content-3">Check your email to verify your address.</p>
      </div>
    );
  }

  const disabled = status === "loading";

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      noValidate  /* Disable native validation — let RHF + Zod handle it */
      aria-label="Sign up"
      className="space-y-5 rounded-card border border-border bg-surface-1 p-6"
    >
      {/* Announce loading to screen readers */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {status === "loading" && "Creating your account…"}
      </div>

      <TextField
        id="name"
        label="Full name"
        placeholder="Alex Johnson"
        autoComplete="name"
        required
        disabled={disabled}
        error={errors.name?.message}
        {...register("name")}
      />

      <TextField
        id="email"
        type="email"
        label="Email address"
        placeholder="alex@example.com"
        autoComplete="email"
        inputMode="email"
        required
        disabled={disabled}
        error={errors.email?.message}
        {...register("email")}
      />

      <TextField
        id="password"
        type="password"
        label="Password"
        placeholder="Min. 8 characters"
        autoComplete="new-password"
        required
        disabled={disabled}
        error={errors.password?.message}
        {...register("password")}
      />

      <TextField
        id="confirmPassword"
        type="password"
        label="Confirm password"
        placeholder="Repeat password"
        autoComplete="new-password"
        required
        disabled={disabled}
        error={errors.confirmPassword?.message}
        {...register("confirmPassword")}
      />

      <SelectField
        id="role"
        label="Role"
        required
        disabled={disabled}
        error={errors.role?.message}
        options={[
          { value: "developer", label: "Developer" },
          { value: "designer",  label: "Designer"  },
          { value: "manager",   label: "Manager"   },
        ]}
        {...register("role")}
      />

      {/* Checkbox with explicit label association */}
      <div className="flex items-start gap-2.5">
        <input
          id="termsAccepted"
          type="checkbox"
          aria-required="true"
          aria-invalid={!!errors.termsAccepted}
          aria-describedby={errors.termsAccepted ? "terms-error" : undefined}
          disabled={disabled}
          className="mt-0.5 h-4 w-4 rounded border-border text-brand focus-visible:ring-brand"
          {...register("termsAccepted")}
        />
        <div className="flex-1 min-w-0">
          <label htmlFor="termsAccepted" className="text-sm text-content-2">
            I agree to the{" "}
            <a href="/terms" className="text-brand hover:underline">Terms of Service</a>
            {" "}and{" "}
            <a href="/privacy" className="text-brand hover:underline">Privacy Policy</a>
          </label>
          {errors.termsAccepted && (
            <p id="terms-error" role="alert" className="mt-0.5 text-xs text-destructive">
              {errors.termsAccepted.message}
            </p>
          )}
        </div>
      </div>

      <button
        type="submit"
        disabled={disabled}
        className={cn(
          "inline-flex w-full items-center justify-center gap-2",
          "rounded-button bg-brand text-white px-4 py-2.5 text-sm font-medium",
          "hover:bg-brand-hover",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2",
          "disabled:opacity-50 disabled:pointer-events-none",
          "transition-colors",
        )}
      >
        {disabled ? (
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
            <span>Creating account…</span>
          </>
        ) : (
          "Create account"
        )}
      </button>
    </form>
  );
}
