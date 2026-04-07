# Area: Hooks
# PRD: plans/template-enforcement.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""
Claude Code PreToolUse hook for Agent tool.
Injects CLAUDE.md compliance requirements into every subagent dispatch.
Ensures subagents cannot begin work without reading project rules.

Usage (in .claude/settings.json):
  PreToolUse Agent: python3 hooks/claude_subagent_gate.py
"""
import json
import os
import sys


def get_project_root():
    """Find project root by looking for CLAUDE.md."""
    path = os.getcwd()
    while path != os.path.dirname(path):
        if os.path.exists(os.path.join(path, "CLAUDE.md")):
            return path
        path = os.path.dirname(path)
    return os.getcwd()


def build_reminder():
    """Build the compliance reminder message."""
    return """
=== MANDATORY SUBAGENT COMPLIANCE (from PreToolUse hook) ===

HARD REQUIREMENT: Do NOT begin writing any code until you have completed
ALL of the following steps. This is enforced by project policy (CLAUDE.md).

1. READ `/CLAUDE.md` — contains all project rules (TDD, 150-line limit,
   no hardcoded values, file headers). Output confirmation after reading.

2. READ `CONTEXT.md` — project architecture, file maps, interface contracts.
   Output: CONTEXT READ: CONTEXT.md | state: <phase> | last change: <date> | open tasks: <N>

3. READ the `ContextModuleDocumentation/CONTEXT_*.md` for every module you
   will touch. Output CONTEXT READ for each BEFORE any Edit or Write calls.

4. If creating a new module, create its CONTEXT_*.md FIRST using the
   template at CONTEXT_MODULE.md.

5. BEFORE REPORTING DONE: Run the Pre-Completion Compliance Checklist
   from CLAUDE.md Tier 3. Verify:
   - Every source file has a corresponding test file (TDD)
   - All files under 150 lines
   - No hardcoded values (use config/constants)
   - Every file has Area/PRD/NOTE header
   - All new files registered in CONTEXT.md and module CONTEXT_*.md
   - Line counts in docs match actual wc -l

Failure to follow these steps will result in compliance violations that
must be fixed in a separate pass. Do the work right the first time.

=== END MANDATORY COMPLIANCE ===
"""


def main():
    """Emit advisory reminder for Agent tool calls."""
    # Read tool input from environment
    tool_input = os.environ.get("TOOL_INPUT", "{}")

    try:
        data = json.loads(tool_input)
    except (json.JSONDecodeError, TypeError):
        data = {}

    prompt = data.get("prompt", "")

    # Check if the prompt already contains CLAUDE.md compliance language
    compliance_markers = [
        "CLAUDE.md",
        "CONTEXT READ:",
        "Pre-Completion Compliance",
        "MANDATORY FIRST STEPS",
    ]

    has_compliance = any(marker in prompt for marker in compliance_markers)

    if has_compliance:
        # Already has compliance instructions — pass through
        sys.exit(0)

    # Emit advisory reminder
    reminder = build_reminder()
    print(reminder, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
