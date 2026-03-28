#!/bin/bash
# post-build-warnings.sh
# Parse build output for Swift 6 concurrency warnings and surface them.
# Pipe XcodeBuildMCP build output through this script.

set -euo pipefail

BUILD_OUTPUT="${1:-/dev/stdin}"

CONCURRENCY_WARNINGS=0
OTHER_WARNINGS=0

echo "=== Swift 6 Concurrency Warning Report ==="
echo ""

while IFS= read -r line; do
    # Match concurrency-related warnings
    if echo "$line" | grep -qiE "(sendable|actor.isolated|concurrency|@MainActor|data race|non-isolated|capture.*non-Sendable).*warning"; then
        echo "CONCURRENCY: $line"
        CONCURRENCY_WARNINGS=$((CONCURRENCY_WARNINGS + 1))
    elif echo "$line" | grep -q "warning:"; then
        OTHER_WARNINGS=$((OTHER_WARNINGS + 1))
    fi
done < "$BUILD_OUTPUT"

echo ""
echo "=== Summary ==="
echo "Concurrency warnings: $CONCURRENCY_WARNINGS"
echo "Other warnings:       $OTHER_WARNINGS"
echo ""

if [ "$CONCURRENCY_WARNINGS" -gt 0 ]; then
    echo "ACTION REQUIRED: Load concurrency-specialist agent to fix concurrency warnings."
    echo "Read references/swift6-concurrency.md for resolution patterns."
    exit 1
fi

if [ "$OTHER_WARNINGS" -gt 0 ]; then
    echo "Non-critical warnings found. Review and fix if appropriate."
fi

exit 0
