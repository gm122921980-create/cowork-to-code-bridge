#!/usr/bin/env bash
# uninstall.sh — remove the Mac-side daemon, plist, and bridge directory.
# Does NOT uninstall the Python package; run `python3 -m pip uninstall cowork-to-code-bridge` for that.
#
# Usage:
#   bash daemon/uninstall.sh             # prompts before deleting
#   bash daemon/uninstall.sh --yes       # no prompt

set -euo pipefail

BRIDGE_ROOT="${BRIDGE_ROOT:-$HOME/.cowork-to-code-bridge}"
PLIST="$HOME/Library/LaunchAgents/dev.cowork-to-code-bridge.daemon.plist"

confirm() {
  if [[ "${1:-}" == "--yes" ]]; then return 0; fi
  read -r -p "$2 [y/N] " response
  [[ "$response" =~ ^[Yy]$ ]]
}

if launchctl list 2>/dev/null | grep -q "dev.cowork-to-code-bridge.daemon"; then
  echo "→ unloading launchd agent"
  launchctl unload "$PLIST" 2>/dev/null || true
fi

if [[ -f "$PLIST" ]]; then
  echo "→ removing $PLIST"
  rm -f "$PLIST"
fi

if [[ -d "$BRIDGE_ROOT" ]]; then
  if confirm "${1:-}" "Delete $BRIDGE_ROOT (contains your bridge token and processed-command history)?"; then
    rm -rf "$BRIDGE_ROOT"
    echo "✓ removed $BRIDGE_ROOT"
  else
    echo "  kept $BRIDGE_ROOT"
  fi
fi

echo "✓ daemon uninstalled."
echo "  To also remove the Python package:"
echo "    python3 -m pip uninstall cowork-to-code-bridge"
