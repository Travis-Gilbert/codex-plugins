#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"

find_package_json() {
  if [[ -f "$root/package.json" ]]; then
    printf '%s\n' "$root/package.json"
    return
  fi
  local found
  found="$(find "$root" -maxdepth 3 -name package.json -not -path '*/node_modules/*' | head -n 1 || true)"
  if [[ -n "$found" ]]; then
    printf '%s\n' "$found"
  fi
}

has_file() {
  find "$root" -maxdepth 4 -name "$1" -not -path '*/node_modules/*' | grep -q .
}

has_path() {
  find "$root" -maxdepth 5 -path "$1" -not -path '*/node_modules/*' | grep -q .
}

pkg="$(find_package_json || true)"

echo "=== UI Stack Report ==="
echo "Root: $(cd "$root" && pwd)"

if [[ -z "${pkg:-}" ]]; then
  echo "package.json: not found"
  echo "RECOMMENDATION: Cannot detect UI stack without package.json."
  exit 0
fi

echo "package.json: $pkg"

# Framework detection
if grep -q '"next"' "$pkg" 2>/dev/null; then
  echo "Framework: Next.js"
  if has_path "*/app" || has_path "*/src/app"; then
    echo "Router: App Router"
  elif has_path "*/pages" || has_path "*/src/pages"; then
    echo "Router: Pages Router"
  fi
elif grep -q '"react"' "$pkg" 2>/dev/null; then
  echo "Framework: React (no Next.js)"
elif grep -q '"vue"' "$pkg" 2>/dev/null; then
  echo "Framework: Vue"
elif grep -q '"svelte"' "$pkg" 2>/dev/null; then
  echo "Framework: Svelte"
else
  echo "Framework: Unknown"
fi

# CSS approach
if has_file "tailwind.config.*" || has_file "tailwind.css"; then
  echo "CSS: Tailwind CSS"
  # Check Tailwind version
  if grep -q '"tailwindcss": ".*4\.' "$pkg" 2>/dev/null; then
    echo "Tailwind version: v4 (CSS-first config)"
  elif grep -q '"tailwindcss": ".*3\.' "$pkg" 2>/dev/null; then
    echo "Tailwind version: v3 (JS config)"
  fi
fi

# Component library
check_dep() {
  local label="$1"
  local pattern="$2"
  if grep -q "$pattern" "$pkg" 2>/dev/null; then
    echo "$label: yes"
    return 0
  else
    echo "$label: no"
    return 1
  fi
}

echo ""
echo "--- Dependencies ---"
check_dep "shadcn/ui (components.json)" "" || true
if has_file "components.json"; then
  echo "shadcn config: present"
fi

check_dep "Radix UI"        '@radix-ui/'
check_dep "Sonner"          '"sonner"'
check_dep "Vaul"            '"vaul"'
check_dep "cmdk"            '"cmdk"'
check_dep "DaisyUI"         '"daisyui"'
check_dep "Motion"          '"motion"\|"framer-motion"'
check_dep "CVA"             '"class-variance-authority"'
check_dep "tailwind-merge"  '"tailwind-merge"'
check_dep "clsx"            '"clsx"'

echo ""
echo "--- Icons ---"
check_dep "Lucide"          '"lucide-react"'
check_dep "Iconoir"         '"iconoir-react"\|"iconoir"'
check_dep "Heroicons"       '"@heroicons/"'

echo ""
echo "--- Component Directories ---"
for dir in "components/ui" "src/components/ui" "app/components" "src/app/components" "components" "src/components"; do
  if [[ -d "$root/$dir" ]]; then
    count=$(find "$root/$dir" -maxdepth 1 -name "*.tsx" -o -name "*.jsx" 2>/dev/null | wc -l | tr -d ' ')
    echo "Found: $dir/ ($count component files)"
  fi
done

echo ""
echo "--- Design Tokens ---"
if find "$root" -maxdepth 3 -name "*.css" -not -path '*/node_modules/*' -exec grep -l '\-\-' {} \; 2>/dev/null | head -1 | grep -q .; then
  echo "CSS custom properties: detected"
fi
if has_file "theme.ts" || has_file "theme.js" || has_file "theme.config.*"; then
  echo "Theme config file: detected"
fi

echo ""
echo "=== Recommendations ==="
echo "USE:     Libraries already in the project (extend, do not replace)"
echo "DETECT:  Run /design-review after inspecting existing component patterns"
echo "AVOID:   Adding a second dialog/drawer/toast stack if one exists"
