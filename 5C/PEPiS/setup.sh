#!/usr/bin/env bash
# setup.sh — bootstrap a fresh macOS machine for this repository.
#
# Installs Homebrew packages, clones the external tool/skill repositories that
# opencode.jsonc references, builds the KiCad MCP server, and prepares the
# kicad-harness skill venv. Idempotent: re-running skips finished steps.
#
# Usage: ./setup.sh
set -euo pipefail

log()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mWARN:\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- preflight --
[[ "$(uname -s)" == "Darwin" ]] || die "This script targets macOS only (found: $(uname -s))."

# -------------------------------------------------------------- homebrew --
if ! command -v brew >/dev/null 2>&1; then
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  else
    log "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
  fi
fi
log "Homebrew: $(brew --version | head -1)"

log "Installing brew packages (git, node, python@3.13, uv, librsvg, kicad cask)..."
brew install git node python@3.13 uv librsvg
brew install --cask kicad   # KiCad 10; provides kicad-cli + bundled Python

# ------------------------------------------------------- kiCad bundled py --
KICAD_PY="/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
[[ -x "$KICAD_PY" ]] || die "KiCad bundled python not found at $KICAD_PY — is the kicad cask installed?"
log "KiCad bundled python: $($KICAD_PY --version)"

# ------------------------------------------------------------ repositories --
clone_or_pull() {
  local url="$1" dest="$2"
  if [[ -d "$dest/.git" ]]; then
    log "Updating $(basename "$dest")..."
    git -C "$dest" pull --ff-only
  elif [[ -e "$dest" ]]; then
    warn "$dest exists but is not a git repo — leaving it alone."
  else
    log "Cloning $url -> $dest"
    mkdir -p "$(dirname "$dest")"
    git clone "$url" "$dest"
  fi
}

# 1. KiCad MCP server (referenced by opencode.jsonc mcp.kicad)
clone_or_pull https://github.com/mixelpixx/KiCAD-MCP-Server.git "$HOME/KiCAD-MCP-Server"
# 2. kicad-happy skill family (referenced by opencode.jsonc skills.paths)
clone_or_pull https://github.com/aklofas/kicad-happy.git "$HOME/github/agentic/kicad-happy"
# 3. kicad-harness skill (referenced by opencode.jsonc skills.paths)
clone_or_pull https://github.com/zxkmm/kicad-harness "$HOME/github/zxkmm/kicad-harness"

# -------------------------------------------------------- kicad MCP server --
MCP_DIR="$HOME/KiCAD-MCP-Server"
if [[ ! -f "$MCP_DIR/dist/index.js" ]] || [[ "$MCP_DIR/src" -nt "$MCP_DIR/dist" ]]; then
  log "Building KiCAD-MCP-Server (npm ci + build)..."
  (cd "$MCP_DIR" && npm ci && npm run build)
else
  log "KiCAD-MCP-Server dist/ already built — skipping."
fi

log "Installing MCP server python deps into KiCad's bundled python..."
"$KICAD_PY" -m pip install -r "$MCP_DIR/requirements.txt"

# ----------------------------------------------------------- kicad-harness --
# macOS notes (see AGENTS.md): do NOT run the repo's setup.sh — it is
# Linux-oriented. Build the venv from KiCad's bundled python (3.9) with
# --system-site-packages so pcbnew/cairosvg are visible; pyproject declares
# >=3.10 so pip needs --ignore-requires-python.
KH_DIR="$HOME/github/zxkmm/kicad-harness"
if [[ ! -x "$KH_DIR/.venv/bin/kh" ]]; then
  log "Creating kicad-harness venv from KiCad's bundled python..."
  (cd "$KH_DIR" \
    && "$KICAD_PY" -m venv --system-site-packages .venv \
    && ./.venv/bin/pip install -e . --ignore-requires-python)
else
  log "kicad-harness venv exists — skipping."
fi

# rsvg-convert: prefer the real one from brew (librsvg); otherwise install a
# cairosvg-backed shim into the venv so kicad-harness rendering works.
if command -v rsvg-convert >/dev/null 2>&1; then
  log "rsvg-convert found on PATH ($(command -v rsvg-convert))."
else
  SHIM="$KH_DIR/.venv/bin/rsvg-convert"
  log "Installing cairosvg-backed rsvg-convert shim -> $SHIM"
  cat > "$SHIM" << 'EOF'
#!/usr/bin/env python3
"""rsvg-convert shim backed by cairosvg, for macOS without librsvg.
Translates the subset of flags used by kicad-harness:
    rsvg-convert -w <px> -b <color> <input.svg> -o <output.png>
"""
import os
import sys

import cairosvg


def main(argv):
    width = None
    background = None
    out = None
    inp = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "-w":
            i += 1
            width = int(argv[i])
        elif a.startswith("-w") and len(a) > 2:
            width = int(a[2:])
        elif a == "-b":
            i += 1
            background = argv[i]
        elif a == "-o":
            i += 1
            out = argv[i]
        elif a in ("-h", "--help"):
            print("rsvg-convert shim (cairosvg). Supports: -w <px> -b <color> <in.svg> -o <out.png>")
            return 0
        elif a.startswith("-") and a[1:].isdigit():
            width = int(a[1:])
        elif not a.startswith("-"):
            inp = a
        i += 1
    if not inp or not out:
        print("usage: rsvg-convert -w <px> -b <color> <in.svg> -o <out.png>", file=sys.stderr)
        return 2
    kwargs = {"url": "file://" + os.path.abspath(inp), "write_to": out}
    if width:
        kwargs["output_width"] = width
    if background:
        kwargs["background_color"] = background
    cairosvg.svg2png(**kwargs)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
EOF
  chmod +x "$SHIM"
fi

# ------------------------------------------------------------- verification --
log "Verifying..."
ok=true
check() { if eval "$2"; then printf '  ok   %s\n' "$1"; else printf '  FAIL %s\n' "$1"; ok=false; fi; }
check "kicad-cli"            "command -v kicad-cli >/dev/null"
check "node >= 20"           "node -e 'process.exit(process.versions.node.split(\".\")[0] >= 20 ? 0 : 1)'"
check "KiCAD-MCP-Server dist" "test -f '$MCP_DIR/dist/index.js'"
check "kicad-happy skills"    "test -f '$HOME/github/agentic/kicad-happy/skills/kicad/SKILL.md'"
check "kicad-harness skill"   "test -f '$KH_DIR/SKILL.md'"
check "kh CLI"                "test -x '$KH_DIR/.venv/bin/kh'"
check "rsvg-convert (real or shim)" "command -v rsvg-convert >/dev/null || test -x '$KH_DIR/.venv/bin/rsvg-convert'"
$ok || die "Some checks failed — see output above."

cat << 'EOF'

Setup complete. Reminders:
- opencode.jsonc uses {env:HOME} paths — no per-machine edits needed.
- To use kicad-harness commands, put its venv bin on PATH:
    export PATH="$HOME/github/zxkmm/kicad-harness/.venv/bin:$PATH"
- KiCad GUI writes conflict with MCP schematic writes — see AGENTS.md.
EOF
