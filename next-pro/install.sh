#!/bin/bash
set -euo pipefail

# Next-Pro installer
# Clones selective Next.js source into the plugin structure

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${1:-$SCRIPT_DIR}"
NEXT_REPO="https://github.com/vercel/next.js.git"
NEXT_REF="${2:-canary}"  # Default to canary branch

BOLD='\033[1m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BOLD}Installing Next-Pro...${NC}"
echo "  Target: $INSTALL_DIR"
echo "  Next.js ref: $NEXT_REF"

# 1. Create directory structure
mkdir -p "$INSTALL_DIR"/{refs,errors,references}

# 2. Sparse clone Next.js (only what we need)
TEMP_DIR=$(mktemp -d)
echo ""
echo "Cloning Next.js (sparse)..."

cd "$TEMP_DIR"
git init next-js-sparse
cd next-js-sparse
git remote add origin "$NEXT_REPO"
git config core.sparseCheckout true

cat > .git/info/sparse-checkout << 'EOF'
# Server source (selective)
packages/next/src/server/base-server.ts
packages/next/src/server/next-server.ts
packages/next/src/server/config.ts
packages/next/src/server/config-shared.ts
packages/next/src/server/config-schema.ts
packages/next/src/server/load-components.ts
packages/next/src/server/render.tsx
packages/next/src/server/patch-error-inspect.ts
packages/next/src/server/app-render/
packages/next/src/server/dev/
packages/next/src/server/route-modules/
packages/next/src/server/diagnostics/

# Server additions (from references guide)
packages/next/src/server/lib/router-server.ts
packages/next/src/server/lib/start-server.ts
packages/next/src/server/lib/render-server.ts
packages/next/src/server/lib/patch-fetch.ts
packages/next/src/server/lib/source-maps.ts
packages/next/src/server/lib/find-page-file.ts
packages/next/src/server/stream-utils/
packages/next/src/server/response-cache/

# Development track: Request APIs (v15 async changes)
packages/next/src/server/request/

# Development track: "use cache" implementation
packages/next/src/server/use-cache/

# Development track: after() API
packages/next/src/server/after/

# Client source (selective)
packages/next/src/client/app-index.tsx
packages/next/src/client/app-bootstrap.ts
packages/next/src/client/flight-data-helpers.ts
packages/next/src/client/link.tsx
packages/next/src/client/image-component.tsx
packages/next/src/client/form.tsx
packages/next/src/client/script.tsx
packages/next/src/client/router.ts
packages/next/src/client/dev/
packages/next/src/client/components/

# DevTools
packages/next/src/next-devtools/

# Shared
packages/next/src/shared/lib/router/
packages/next/src/shared/lib/constants.ts
packages/next/src/shared/lib/app-router-context.shared-runtime.ts
packages/next/src/shared/lib/dynamic.tsx
packages/next/src/shared/lib/utils.ts

# Build (selective)
packages/next/src/build/index.ts
packages/next/src/build/webpack-config.ts
packages/next/src/build/define-env.ts
packages/next/src/build/entries.ts
packages/next/src/build/handle-externals.ts
packages/next/src/build/compiler.ts
packages/next/src/build/create-compiler-aliases.ts
packages/next/src/build/print-build-errors.ts
packages/next/src/build/segment-config/
packages/next/src/build/static-paths/
packages/next/src/build/route-bundle-stats.ts
packages/next/src/build/validate-app-paths.ts
packages/next/src/build/load-jsconfig.ts
packages/next/src/build/type-check.ts

# Development track: Build templates
packages/next/src/build/templates/

# Lib (selective)
packages/next/src/lib/is-serializable-props.ts
packages/next/src/lib/verify-root-layout.ts
packages/next/src/lib/turbopack-warning.ts
packages/next/src/lib/metadata/
packages/next/src/lib/generate-interception-routes-rewrites.ts

# Errors (all)
errors/

# Internal debugging skills
.agents/skills/

# Diagnostics
packages/next/src/diagnostics/
EOF

git pull --depth=1 origin "$NEXT_REF"

# 3. Copy into plugin structure
echo "Copying source files..."

# Server refs
cp -r packages/next/src/server/ "$INSTALL_DIR/refs/next-server/" 2>/dev/null || true

# Client refs
mkdir -p "$INSTALL_DIR/refs/next-client"
for f in app-index.tsx app-bootstrap.ts flight-data-helpers.ts link.tsx \
         image-component.tsx form.tsx script.tsx router.ts; do
  cp "packages/next/src/client/$f" "$INSTALL_DIR/refs/next-client/" 2>/dev/null || true
done
cp -r packages/next/src/client/dev/ "$INSTALL_DIR/refs/next-client/dev/" 2>/dev/null || true
cp -r packages/next/src/client/components/ "$INSTALL_DIR/refs/next-client/components/" 2>/dev/null || true

# DevTools refs
cp -r packages/next/src/next-devtools/ "$INSTALL_DIR/refs/next-devtools/" 2>/dev/null || true

# Shared refs
mkdir -p "$INSTALL_DIR/refs/next-shared"
cp -r packages/next/src/shared/lib/router/ "$INSTALL_DIR/refs/next-shared/router/" 2>/dev/null || true
for f in constants.ts app-router-context.shared-runtime.ts dynamic.tsx utils.ts; do
  cp "packages/next/src/shared/lib/$f" "$INSTALL_DIR/refs/next-shared/" 2>/dev/null || true
done

# Build refs
mkdir -p "$INSTALL_DIR/refs/next-build"
for f in index.ts webpack-config.ts define-env.ts entries.ts handle-externals.ts \
         compiler.ts create-compiler-aliases.ts print-build-errors.ts \
         route-bundle-stats.ts validate-app-paths.ts load-jsconfig.ts type-check.ts; do
  cp "packages/next/src/build/$f" "$INSTALL_DIR/refs/next-build/" 2>/dev/null || true
done
cp -r packages/next/src/build/segment-config/ "$INSTALL_DIR/refs/next-build/segment-config/" 2>/dev/null || true
cp -r packages/next/src/build/static-paths/ "$INSTALL_DIR/refs/next-build/static-paths/" 2>/dev/null || true
cp -r packages/next/src/build/templates/ "$INSTALL_DIR/refs/next-build/templates/" 2>/dev/null || true

# Lib refs
mkdir -p "$INSTALL_DIR/refs/next-lib"
for f in is-serializable-props.ts verify-root-layout.ts turbopack-warning.ts \
         generate-interception-routes-rewrites.ts; do
  cp "packages/next/src/lib/$f" "$INSTALL_DIR/refs/next-lib/" 2>/dev/null || true
done
cp -r packages/next/src/lib/metadata/ "$INSTALL_DIR/refs/next-lib/metadata/" 2>/dev/null || true

# Errors (complete)
cp -r errors/ "$INSTALL_DIR/errors/" 2>/dev/null || true

# 4. Copy internal debugging skills as references
echo "Extracting Next.js team debugging skills..."
if [ -d ".agents/skills" ]; then
  for skill_dir in .agents/skills/*/; do
    skill_name=$(basename "$skill_dir")
    if [ -f "$skill_dir/SKILL.md" ]; then
      cp "$skill_dir/SKILL.md" "$INSTALL_DIR/references/nextjs-skill-${skill_name}.md"
    fi
  done
fi

# 5. Cleanup
cd /
rm -rf "$TEMP_DIR"

# 6. Report
echo ""
echo -e "${BOLD}${GREEN}Installation Summary${NC}"
echo "  Location:    $INSTALL_DIR"
echo "  Next.js ref: $NEXT_REF"
echo "  Refs dirs:   $(find "$INSTALL_DIR/refs/" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
echo "  Errors:      $(find "$INSTALL_DIR/errors/" -name '*.mdx' 2>/dev/null | wc -l | tr -d ' ')"
echo "  References:  $(find "$INSTALL_DIR/references/" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo -e "${GREEN}Next-Pro installed.${NC}"
echo ""
echo "To update to a different Next.js version:"
echo "  bash install.sh $INSTALL_DIR v15.2.0"
