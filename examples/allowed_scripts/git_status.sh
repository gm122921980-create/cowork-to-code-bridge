#!/usr/bin/env bash
# Example: git status in any repo directory.
# Usage from Cowork: call_remote("scripts/git_status.sh", args=["/path/to/repo"])
set -euo pipefail
REPO="${1:-$PWD}"
cd "$REPO"
git status --short --branch
