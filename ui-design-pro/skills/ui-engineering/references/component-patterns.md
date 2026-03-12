# Component Patterns

## CVA: Class Variance Authority

CVA is the standard pattern for building variant-based components with Tailwind. It replaces ad-hoc conditional class logic.

**Source:** `refs/shadcn-ui/apps/v4/registry/` (inspect how shadcn components use CVA internally)

### Basic CVA Setup

```tsx
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  // Base classes — always applied
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-button text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default:     'bg-brand text-white hover:bg-brand-hover',
        destructive: 'bg-destructive text-white hover:bg-destructive/90',
        outline:     'border border-border bg-transparent hover:bg-surface-2 hover:text-content-1',
        ghost:       'hover:bg-surface-2 hover:text-content-1',
        link:        'text-brand underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm:      'h-8 rounded-button px-3 text-xs',
        lg:      'h-12 rounded-button px-8',
        icon:    'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size:    'default',
    },
  }
)

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }
```

### The `cn` Utility

Always merge classes with `cn` (clsx + tailwind-merge):

```ts
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**Why tailwind-merge matters:** Without it, `cn('px-4', 'px-2')` produces `px-4 px-2` and the last-defined class wins (fragile). With tailwind-merge, `cn('px-4', 'px-2')` produces `px-2` — the later value always wins.

### Compound Variants

Use `compoundVariants` when a combination of variants should produce a unique style:

```tsx
const alertVariants = cva(
  'flex items-start gap-3 rounded-card border px-4 py-3 text-sm',
  {
    variants: {
      variant: {
        default:     'border-border bg-surface-2 text-content-1',
        destructive: 'border-destructive/50 bg-destructive/10 text-destructive',
        success:     'border-success/50 bg-success/10 text-success',
        warning:     'border-warning/50 bg-warning/10 text-warning',
      },
      size: {
        default: 'text-sm',
        lg:      'text-base',
      },
    },
    compoundVariants: [
      // Destructive + large → bold
      {
        variant: 'destructive',
        size: 'lg',
        class: 'font-semibold',
      },
    ],
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)
```

---

## The `asChild` / Slot Pattern

Radix provides a `<Slot>` component that merges props onto its immediate child. This enables polymorphic rendering without building your own `as` prop system.

**Source:** `refs/radix-primitives/packages/react/slot/`

```tsx
import { Slot } from '@radix-ui/react-slot'

// With asChild=false (default): renders <button>
<Button variant="outline">Click me</Button>
// Produces: <button class="...variants...">Click me</button>

// With asChild=true: renders <a> with button styles
<Button variant="outline" asChild>
  <a href="/dashboard">Go to dashboard</a>
</Button>
// Produces: <a class="...variants..." href="/dashboard">Go to dashboard</a>
```

**When to use `asChild`:**
- Navigation buttons that should render as `<a>` for correct semantics
- Wrapping a component from a router library (`<Link>` from next/navigation)
- Re-using trigger styles on arbitrary HTML elements

**How Slot merges:** Event handlers and class names from both the Slot consumer and the child element are merged. This means `className` from `buttonVariants` and `className` from the child are both applied via tailwind-merge.

---

## Compound Components

Compound components expose behavior through a parent-child API. They share state via React context, keeping each piece focused.

```tsx
// Accordion using Radix primitives
import * as Accordion from '@radix-ui/react-accordion'

function Faq({ items }: { items: { q: string; a: string }[] }) {
  return (
    <Accordion.Root type="single" collapsible className="space-y-1">
      {items.map((item, i) => (
        <Accordion.Item
          key={i}
          value={`item-${i}`}
          className="rounded-card border border-border bg-surface-2"
        >
          <Accordion.Header>
            <Accordion.Trigger className="flex w-full items-center justify-between px-4 py-3 text-sm font-medium text-content-1 hover:text-brand [&[data-state=open]>svg]:rotate-180">
              {item.q}
              <ChevronDownIcon className="h-4 w-4 text-content-3 transition-transform duration-200" />
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="overflow-hidden text-sm data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down">
            <div className="px-4 pb-3 pt-0 text-content-2">{item.a}</div>
          </Accordion.Content>
        </Accordion.Item>
      ))}
    </Accordion.Root>
  )
}
```

**The data attribute pattern:** Radix adds `data-state`, `data-disabled`, `data-orientation`, and similar attributes to elements. Style against them with `data-[state=open]:...` Tailwind syntax — never add your own `isOpen` prop when Radix already exposes it.

---

## Form Patterns

### React Hook Form + Zod

```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type FormValues = z.infer<typeof schema>

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormValues) => {
    await login(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-content-1 mb-1">
          Email
        </label>
        <input
          id="email"
          type="email"
          {...register('email')}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
          className={cn(
            'w-full rounded-input border bg-surface-3 px-3 py-2 text-sm text-content-1',
            errors.email ? 'border-destructive' : 'border-border'
          )}
        />
        {errors.email && (
          <p id="email-error" role="alert" className="mt-1 text-xs text-destructive">
            {errors.email.message}
          </p>
        )}
      </div>

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? 'Signing in…' : 'Sign in'}
      </Button>
    </form>
  )
}
```

**Rules:**
- Always set `noValidate` on the `<form>` — let React Hook Form handle validation, not browser built-ins
- Error messages need `role="alert"` for screen readers
- Tie label to input with `htmlFor`/`id`, not wrapping (wrapping breaks screen readers for complex inputs)

### Controlled vs. Uncontrolled

```tsx
// Uncontrolled with React Hook Form (preferred for most forms)
<input {...register('email')} />

// Controlled with Controller (required for Radix inputs, Select, etc.)
<Controller
  name="role"
  control={control}
  render={({ field }) => (
    <Select.Root value={field.value} onValueChange={field.onChange}>
      <Select.Trigger>
        <Select.Value placeholder="Select a role" />
      </Select.Trigger>
      <Select.Content>
        <Select.Item value="admin">Admin</Select.Item>
        <Select.Item value="member">Member</Select.Item>
      </Select.Content>
    </Select.Root>
  )}
/>
```

Use `Controller` for any custom input component that doesn't expose a native `onChange`/`value` interface.

---

## Data Table Pattern

For sortable, filterable tables with TanStack Table:

```tsx
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
  type SortingState,
} from '@tanstack/react-table'

type User = { id: string; name: string; email: string; role: string; joined: string }

const col = createColumnHelper<User>()

const columns = [
  col.accessor('name', {
    header: 'Name',
    cell: info => (
      <div className="flex items-center gap-3">
        <Avatar name={info.getValue()} size="sm" />
        <span className="text-sm font-medium text-content-1">{info.getValue()}</span>
      </div>
    ),
  }),
  col.accessor('email', {
    header: 'Email',
    cell: info => <span className="text-sm text-content-2">{info.getValue()}</span>,
  }),
  col.accessor('role', {
    header: 'Role',
    cell: info => <RoleBadge role={info.getValue()} />,
  }),
  col.accessor('joined', {
    header: 'Joined',
    cell: info => <span className="text-sm text-content-3">{info.getValue()}</span>,
  }),
]

function UserTable({ users }: { users: User[] }) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [globalFilter, setGlobalFilter] = React.useState('')

  const table = useReactTable({
    data: users,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  return (
    <div className="space-y-3">
      <input
        value={globalFilter ?? ''}
        onChange={e => setGlobalFilter(e.target.value)}
        placeholder="Search users…"
        className="rounded-input border border-border bg-surface-3 px-3 py-2 text-sm w-full max-w-xs"
      />
      <div className="rounded-card border border-border overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-surface-2 border-b border-border">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    onClick={header.column.getToggleSortingHandler()}
                    className="px-4 py-3 text-xs font-medium text-content-3 uppercase tracking-wider cursor-pointer select-none hover:text-content-1"
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    {{ asc: ' ↑', desc: ' ↓' }[header.column.getIsSorted() as string] ?? null}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-border bg-surface-1">
            {table.getRowModel().rows.map(row => (
              <tr key={row.id} className="hover:bg-surface-2 transition-colors">
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-4 py-3">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {table.getRowModel().rows.length === 0 && (
          <div className="py-12 text-center text-sm text-content-3">No users found.</div>
        )}
      </div>
    </div>
  )
}
```

**TanStack Table rules:**
- `createColumnHelper` gives type-safe column definitions
- Cell renderers receive the raw value via `info.getValue()` — never render raw strings in cells without wrapping, always apply semantic styling
- Move filtering/sorting state up if the parent needs to control it

---

## Icon Patterns

### Lucide (preferred)

```tsx
import { ArrowRight, Check, X, ChevronDown } from 'lucide-react'

// Always set size explicitly; don't rely on font-size inheritance
<ArrowRight className="h-4 w-4" />

// Icons in buttons: paired with text
<Button>
  Continue <ArrowRight className="h-4 w-4" />
</Button>

// Standalone icon button: must have aria-label
<button aria-label="Close dialog" className="rounded p-1 hover:bg-surface-2">
  <X className="h-4 w-4" aria-hidden="true" />
</button>
```

### Icon size conventions

| Context | Size |
|---------|------|
| Inline with text (sm) | `h-3.5 w-3.5` |
| Inline with text (base) | `h-4 w-4` |
| Inline with text (lg) | `h-5 w-5` |
| Standalone nav icon | `h-5 w-5` |
| Hero / feature icon | `h-8 w-8` or `h-10 w-10` |
| Avatar fallback | `h-6 w-6` |

---

## Anti-Patterns

**The `isOpen` prop instead of Radix state:**
```tsx
// WRONG: redundant state
const [open, setOpen] = useState(false)
<Dialog open={open} onOpenChange={setOpen}>

// CORRECT: let Radix control state (uncontrolled)
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>...</DialogContent>
</Dialog>

// CORRECT: controlled (when parent needs to know)
const [open, setOpen] = useState(false)
<Dialog open={open} onOpenChange={setOpen}>
```

Use uncontrolled Radix dialogs/dropdowns unless you genuinely need to control them from outside.

**Wrapping Radix components unnecessarily:**
```tsx
// WRONG: extra div breaks Radix's CSS selector targeting
function MyDialog({ children }) {
  return (
    <div> {/* breaks data-[state] selectors */}
      <Dialog.Content>{children}</Dialog.Content>
    </div>
  )
}

// CORRECT: spread props so Radix selectors work
function MyDialog({ children, className, ...props }) {
  return (
    <Dialog.Content className={cn('...base styles...', className)} {...props}>
      {children}
    </Dialog.Content>
  )
}
```

**Conditional class strings without cn:**
```tsx
// WRONG: fragile, doesn't resolve conflicts
const className = `btn ${isActive ? 'bg-brand' : ''} ${disabled ? 'opacity-50' : ''}`

// CORRECT
const className = cn('btn', isActive && 'bg-brand', disabled && 'opacity-50')
```
