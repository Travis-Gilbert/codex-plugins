# Reference Source Repositories

This directory holds cloned source repos used by the `ui-design-pro` plugin for
authoritative answers about library internals. These repos are **gitignored** and
must be populated by running the installer.

## Quick Start

From the plugin root:

```bash
./install.sh
```

This runs `scripts/install_refs.sh` and clones all 11 repos listed below.

To clone manually:

```bash
cd refs/

git clone --depth=1 https://github.com/shadcn-ui/ui.git                shadcn-ui
git clone --depth=1 https://github.com/radix-ui/primitives.git          radix-primitives
git clone --depth=1 https://github.com/motiondivision/motion.git        motion
git clone --depth=1 https://github.com/radix-ui/colors.git              radix-colors
git clone --depth=1 https://github.com/tailwindlabs/tailwindcss.git     tailwindcss
git clone --depth=1 https://github.com/argyleink/open-props.git         open-props
git clone --depth=1 https://github.com/pacocoursey/cmdk.git             cmdk
git clone --depth=1 https://github.com/emilkowalski/vaul.git            vaul
git clone --depth=1 https://github.com/emilkowalski/sonner.git          sonner
git clone --depth=1 https://github.com/saadeghi/daisyui.git             daisyui
git clone --depth=1 https://github.com/cschroeter/park-ui.git           park-ui
```

`--depth=1` fetches only the latest commit, keeping clone time under 60 seconds
total on a typical connection.

---

## Repository Map

| Directory | Repo | What to grep for |
|-----------|------|-----------------|
| `shadcn-ui/` | shadcn-ui/ui | `apps/v4/registry/` — component implementations; `packages/shadcn/` — CLI |
| `radix-primitives/` | radix-ui/primitives | `packages/react/*/src/` — accessibility, focus management, ARIA |
| `motion/` | motiondivision/motion | `packages/motion/src/` — spring physics; `packages/motion-dom/` — layout |
| `radix-colors/` | radix-ui/colors | `src/` — scale construction, dark mode step mapping |
| `tailwindcss/` | tailwindlabs/tailwindcss | `packages/tailwindcss/src/` — plugin system, theme resolution, v4 internals |
| `open-props/` | argyleink/open-props | `src/props.*.css` — battle-tested spacing, type, easing, color scales |
| `cmdk/` | pacocoursey/cmdk | `src/` — keyboard navigation, filtering, command group patterns |
| `vaul/` | emilkowalski/vaul | `src/` — drawer snap points, drag gestures, mobile-first overlay |
| `sonner/` | emilkowalski/sonner | `src/` — toast queue, animation lifecycle, action handling |
| `daisyui/` | saadeghi/daisyui | `src/components/` — Tailwind-native class composition, theme tokens |
| `park-ui/` | cschroeter/park-ui | `src/components/` — Ark UI + Panda CSS patterns, alternative to shadcn |

---

## Usage Pattern

When Claude needs authoritative information about a library rather than relying
on training data (which may be stale):

```bash
# Find actual component implementation
grep -r "DialogContent" refs/shadcn-ui/apps/v4/registry/ --include="*.tsx" -l

# Find how Radix handles focus restoration
grep -r "restoreFocus\|focusTrap" refs/radix-primitives/packages/react/ -l

# Find spring easing in Motion source
grep -r "stiffness\|damping" refs/motion/packages/motion/src/ --include="*.ts" -l

# Find Radix Colors dark mode step rationale
grep -r "step-9\|step-10\|solid" refs/radix-colors/src/ --include="*.ts"
```

See `CLAUDE.md` for the full per-library grep guidance.

---

## Keeping Refs Up to Date

Pull all repos to latest:

```bash
for dir in refs/*/; do
  [ -d "$dir/.git" ] && git -C "$dir" pull --ff-only
done
```

Or re-run `./install.sh` which will skip existing repos and only clone missing ones.

---

## Disk Usage

Each repo is cloned with `--depth=1` (no history).

Approximate sizes after shallow clone:

| Repo | ~Size |
|------|-------|
| shadcn-ui | ~12 MB |
| tailwindcss | ~18 MB |
| motion | ~22 MB |
| radix-primitives | ~35 MB |
| radix-colors | ~2 MB |
| open-props | ~1 MB |
| cmdk | ~3 MB |
| vaul | ~4 MB |
| sonner | ~4 MB |
| daisyui | ~8 MB |
| park-ui | ~6 MB |
| **Total** | **~115 MB** |

These files are gitignored. Running `git status` will not show them.
