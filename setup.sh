#!/usr/bin/env bash
# Area: Setup
# PRD: docs/superpowers/plans/2026-04-05-template-enforcement-overhaul.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
# setup.sh — Set up ClaudeTemplates enforcement infrastructure in a project.
# Safe: checks for existing hooks, merges settings, deduplicates .gitignore entries.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }

echo ""
echo "ClaudeTemplates Setup"
echo "====================="
echo ""

# --- 1. Prerequisites ---
echo "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    error "Python 3 is required but not found."
    exit 1
fi
info "Python 3 found"

if [ ! -d ".git" ]; then
    error "Not a git repository. Run 'git init' first."
    exit 1
fi
info "Git repository found"

if command -v yq &>/dev/null; then
    info "yq found (preferred YAML parser)"
else
    warn "yq not found — will use Python fallback parser"
    echo "  Install yq for faster hook execution: brew install yq"
fi

echo ""

# --- 2. Copy template files ---
echo "Copying template files..."

copy_if_missing() {
    local src="$1"
    local dest="$2"
    if [ -f "$dest" ]; then
        warn "Skipping $dest (already exists)"
    else
        cp "$src" "$dest"
        info "Created $dest"
    fi
}

copy_if_missing "${SCRIPT_DIR}/CLAUDE.md" "CLAUDE.md"
copy_if_missing "${SCRIPT_DIR}/CONTEXT.md" "CONTEXT.md"
copy_if_missing "${SCRIPT_DIR}/CONTEXT_MODULE.md" "CONTEXT_MODULE.md"
copy_if_missing "${SCRIPT_DIR}/compliance_config.yaml" "compliance_config.yaml"

mkdir -p hooks agents
for hook_file in parse_config.py pre-commit claude_read_gate.py claude_advisory_scan.py claude_subagent_gate.py claude_token_monitor.py run_provenance_check.py provenance_io.py provenance_reverse.py; do
    if [ -f "${SCRIPT_DIR}/hooks/${hook_file}" ]; then
        cp "${SCRIPT_DIR}/hooks/${hook_file}" "hooks/${hook_file}"
        chmod +x "hooks/${hook_file}"
        info "Copied hooks/${hook_file}"
    fi
done

if [ -f "${SCRIPT_DIR}/agents/compliance_monitor.md" ]; then
    cp "${SCRIPT_DIR}/agents/compliance_monitor.md" "agents/compliance_monitor.md"
    info "Copied agents/compliance_monitor.md"
fi

if [ -f "${SCRIPT_DIR}/templates/PROJECT_README.md" ]; then
    copy_if_missing "${SCRIPT_DIR}/templates/PROJECT_README.md" "README.md"
fi

echo ""

# --- 3. Create directories ---
echo "Creating directories..."

for dir in ContextModuleDocumentation plans docs/superpowers/specs .claude; do
    mkdir -p "$dir"
    info "Directory: $dir/"
done

echo ""

# Copy decisions/ directory (ADR discipline) — created by deliverable-provenance feature
mkdir -p decisions
for adr_file in README.md 0001-cut-script-registry.md; do
    if [ -f "${SCRIPT_DIR}/decisions/${adr_file}" ]; then
        copy_if_missing "${SCRIPT_DIR}/decisions/${adr_file}" "decisions/${adr_file}"
    fi
done

# Copy parsers/ directory + CHANGELOG — created by deliverable-provenance feature
mkdir -p parsers
for parser_file in __init__.py narrative_md.py CHANGELOG.md; do
    if [ -f "${SCRIPT_DIR}/parsers/${parser_file}" ]; then
        copy_if_missing "${SCRIPT_DIR}/parsers/${parser_file}" "parsers/${parser_file}"
    fi
done

# Seed/migrate the deliverable-to-code provenance file.
DRY_RUN_FLAG=""
for arg in "$@"; do
    [ "$arg" = "--dry-run" ] && DRY_RUN_FLAG="yes"
done

if [ -f "docs/SCRIPT_PURPOSES.md" ] && [ ! -f "docs/DELIVERABLE_PROVENANCE.md" ]; then
    info "Detected legacy docs/SCRIPT_PURPOSES.md — migrating to DELIVERABLE_PROVENANCE.md"

    # Refuse to migrate over a dirty git tree
    if [ -n "$(git status --porcelain docs/SCRIPT_PURPOSES.md 2>/dev/null)" ]; then
        error "docs/SCRIPT_PURPOSES.md has unstaged changes. Stash or commit first."
        exit 1
    fi

    # Detect strip target
    if ! grep -q '^## Script Registry\s*$' docs/SCRIPT_PURPOSES.md; then
        error "docs/SCRIPT_PURPOSES.md present but no '## Script Registry' heading found."
        error "The file may have been customized (e.g., section retitled). Manual review required."
        exit 1
    fi

    # Print the diff that would be applied
    info "Migration would: rename docs/SCRIPT_PURPOSES.md → docs/DELIVERABLE_PROVENANCE.md"
    info "                 strip section from '## Script Registry' to next '---' or EOF"

    if [ -n "$DRY_RUN_FLAG" ]; then
        info "--dry-run set; no changes made"
    else
        echo ""
        read -rp "  Proceed with migration? [y/N]: " choice
        if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
            # Strip Script Registry section
            python3 - <<'PYEOF'
from pathlib import Path
src = Path("docs/SCRIPT_PURPOSES.md")
text = src.read_text()
lines = text.splitlines(keepends=True)
out = []
in_strip = False
for line in lines:
    if line.strip() == "## Script Registry":
        in_strip = True
        continue
    if in_strip and line.strip() == "---":
        in_strip = False
        continue
    if not in_strip:
        out.append(line)
dst = Path("docs/DELIVERABLE_PROVENANCE.md")
dst.write_text("".join(out).replace("SCRIPT_PURPOSES.md", "DELIVERABLE_PROVENANCE.md"))
src.unlink()
PYEOF
            info "Migration complete: docs/DELIVERABLE_PROVENANCE.md"
            warn "Next steps:"
            warn "  1. Add 'ID' column to existing rows in docs/DELIVERABLE_PROVENANCE.md"
            warn "  2. Populate compliance_config.yaml deliverable_inventory section"
            warn "  3. Re-run compliance_monitor to verify CHECK 7 passes"
        else
            warn "Migration skipped"
        fi
    fi
elif [ ! -f "docs/DELIVERABLE_PROVENANCE.md" ]; then
    if [ -f "${SCRIPT_DIR}/templates/DELIVERABLE_PROVENANCE.md" ]; then
        copy_if_missing "${SCRIPT_DIR}/templates/DELIVERABLE_PROVENANCE.md" "docs/DELIVERABLE_PROVENANCE.md"
    fi
fi

echo ""

# --- 4. Git hook installation ---
echo "Installing git hooks..."

HOOK_TARGET=".git/hooks/pre-commit"
HOOK_SOURCE="hooks/pre-commit"

if [ -f "$HOOK_TARGET" ]; then
    warn "Existing pre-commit hook found at $HOOK_TARGET"
    echo ""
    echo "  Options:"
    echo "    1) Chain — rename existing to pre-commit.local, run it before template checks"
    echo "    2) Append — add template checks to end of existing hook"
    echo "    3) Skip — don't install, show manual instructions"
    echo ""
    read -rp "  Choose [1/2/3]: " choice

    case "$choice" in
        1)
            mv "$HOOK_TARGET" "${HOOK_TARGET}.local"
            info "Renamed existing hook to pre-commit.local"
            cat > "$HOOK_TARGET" << 'CHAINED_HOOK'
#!/usr/bin/env bash
# Chained pre-commit: runs existing hook first, then template checks.
HOOK_DIR="$(dirname "$0")"

if [ -x "${HOOK_DIR}/pre-commit.local" ]; then
    "${HOOK_DIR}/pre-commit.local" || exit $?
fi

exec "$(git rev-parse --show-toplevel)/hooks/pre-commit"
CHAINED_HOOK
            chmod +x "$HOOK_TARGET"
            info "Installed chained pre-commit hook"
            ;;
        2)
            echo "" >> "$HOOK_TARGET"
            echo "# --- ClaudeTemplates enforcement ---" >> "$HOOK_TARGET"
            echo "exec \"\$(git rev-parse --show-toplevel)/hooks/pre-commit\"" >> "$HOOK_TARGET"
            info "Appended template checks to existing hook"
            ;;
        3)
            warn "Skipped git hook installation"
            echo "  Manual: copy hooks/pre-commit to .git/hooks/pre-commit and chmod +x"
            ;;
        *)
            warn "Invalid choice — skipping git hook installation"
            ;;
    esac
else
    cp "$HOOK_SOURCE" "$HOOK_TARGET"
    chmod +x "$HOOK_TARGET"
    info "Installed pre-commit hook"
fi

echo ""

# --- 5. Claude Code settings ---
echo "Configuring Claude Code hooks..."

SETTINGS_FILE=".claude/settings.json"
HOOKS_CONFIG='{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 hooks/claude_read_gate.py check \"$FILE_PATH\""
          }
        ]
      },
      {
        "matcher": "Agent",
        "hooks": [
          {
            "type": "command",
            "command": "python3 hooks/claude_subagent_gate.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "python3 hooks/claude_read_gate.py record \"$FILE_PATH\""
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 hooks/claude_advisory_scan.py scan \"$FILE_PATH\""
          },
          {
            "type": "command",
            "command": "python3 hooks/claude_token_monitor.py \"$FILE_PATH\""
          }
        ]
      }
    ]
  }
}'

if [ -f "$SETTINGS_FILE" ]; then
    warn "Existing $SETTINGS_FILE found — please merge hooks manually:"
    echo "$HOOKS_CONFIG"
else
    mkdir -p .claude
    echo "$HOOKS_CONFIG" > "$SETTINGS_FILE"
    info "Created $SETTINGS_FILE with hook configuration"
fi

echo ""

# --- 6. Update .gitignore ---
echo "Updating .gitignore..."

add_gitignore() {
    local entry="$1"
    if [ -f ".gitignore" ] && grep -qF "$entry" ".gitignore"; then
        return  # Already present
    fi
    echo "$entry" >> ".gitignore"
    info "Added $entry to .gitignore"
}

# If the project has no .gitignore yet, seed it from the baseline template
# (Python + Claude session files + IDE + OS + commented Unity section).
if [ ! -f ".gitignore" ] && [ -f "${SCRIPT_DIR}/templates/gitignore" ]; then
    cp "${SCRIPT_DIR}/templates/gitignore" ".gitignore"
    info "Seeded .gitignore from templates/gitignore"
fi

# Idempotent backstop: ensure the Claude session files are ignored even
# if the project already had a .gitignore that didn't include them.
add_gitignore ".claude/session_reads.json"
add_gitignore ".claude/advisory_dismissals.json"
add_gitignore ".claude/last_compliance_report.json"

echo ""

# --- 7. Summary ---
echo "Setup complete!"
echo "==============="
echo ""
echo "Next steps:"
echo "  1. Fill in README.md placeholders (project name, pitch, tech stack, getting-started)"
echo "  2. Fill in CLAUDE.md placeholders (project name, description)"
echo "  3. Fill in CONTEXT.md placeholders (architecture, terminology)"
echo "  4. In docs/DELIVERABLE_PROVENANCE.md, fill in 'What \"deliverable\" means in this project'"
echo "  5. Add module entries to compliance_config.yaml read_gate.module_map"
echo "  6. Run your first Claude Code session"
echo ""
