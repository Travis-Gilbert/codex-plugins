#!/bin/bash
# pre-commit-swiftlint.sh
# Run SwiftLint on staged .swift files before commit.
# Usage: Add to git hooks or call from Claude Code hook.

set -euo pipefail

if ! command -v swiftlint &> /dev/null; then
    echo "SwiftLint not installed. Install with: brew install swiftlint"
    exit 0  # Don't block commit if SwiftLint isn't installed
fi

# Get staged Swift files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM -- '*.swift')

if [ -z "$STAGED_FILES" ]; then
    echo "No staged Swift files to lint."
    exit 0
fi

echo "Running SwiftLint on staged files..."

LINT_ERRORS=0
while IFS= read -r file; do
    if [ -f "$file" ]; then
        if ! swiftlint lint --quiet --path "$file"; then
            LINT_ERRORS=$((LINT_ERRORS + 1))
        fi
    fi
done <<< "$STAGED_FILES"

if [ "$LINT_ERRORS" -gt 0 ]; then
    echo ""
    echo "SwiftLint found issues in $LINT_ERRORS file(s)."
    echo "Fix issues or run: swiftlint --fix"
    exit 1
fi

echo "SwiftLint passed."
exit 0
