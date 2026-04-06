#!/usr/bin/env python3
# Area: Hooks
# PRD: plans/2026-04-05-template-enforcement-overhaul.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Claude Code PreToolUse hook: read gate.

Blocks Edit/Write tool calls on module source files until the agent has:
1. Called Read on the module's CONTEXT file in this session
2. Output the structured CONTEXT READ confirmation line

Reads module_map from compliance_config.yaml.
Tracks session state in .claude/session_reads.json.
"""
import json
import os
import sys
import time
import yaml


CONFIG_PATH = "compliance_config.yaml"
DEFAULT_SESSION_STATE = ".claude/session_reads.json"
# Sessions older than 4 hours are considered stale
SESSION_TIMEOUT_SECONDS = 4 * 60 * 60


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def load_session_state(state_path):
    """Load session reads, wiping if stale."""
    if not os.path.exists(state_path):
        return {"timestamp": time.time(), "reads": {}, "confirmations": []}

    with open(state_path, "r") as f:
        state = json.load(f)

    # Wipe if stale (from prior/crashed session)
    age = time.time() - state.get("timestamp", 0)
    if age > SESSION_TIMEOUT_SECONDS:
        return {"timestamp": time.time(), "reads": {}, "confirmations": []}

    return state


def save_session_state(state_path, state):
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def find_module_for_file(file_path, module_map):
    """Return the module name and context file for a given source file."""
    for module_name, module_info in module_map.items():
        source_dir = module_info.get("source_dir", "")
        if file_path.startswith(source_dir):
            return module_name, module_info.get("context_file", "")
    return None, None


def record_read(state_path, file_path):
    """Called by PostToolUse on Read to record a file was read."""
    state = load_session_state(state_path)
    state["reads"][file_path] = time.time()
    save_session_state(state_path, state)


def check_gate(state_path, target_file, module_map):
    """Check if the read gate allows editing target_file.

    Returns None if allowed, or an error message string if blocked.
    """
    module_name, context_file = find_module_for_file(target_file, module_map)

    # File not in any mapped module — allow
    if module_name is None:
        return None

    state = load_session_state(state_path)

    # Check if CONTEXT file was read
    if context_file not in state.get("reads", {}):
        return (
            f"⛔ READ GATE: You are editing {target_file} but have not confirmed "
            f"reading {os.path.basename(context_file)}. Read the file and output:\n"
            f"CONTEXT READ: {os.path.basename(context_file)} | state: <phase> "
            f"| last change: <date+desc> | open tasks: <N>"
        )

    return None


def main():
    """Entry point for hook invocation.

    Usage:
        Pre-edit check: python3 hooks/claude_read_gate.py check <target_file>
        Record a read:  python3 hooks/claude_read_gate.py record <file_path>
    """
    if len(sys.argv) < 3:
        print("Usage: claude_read_gate.py <check|record> <file_path>", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2]

    config = load_config()
    read_gate_config = config.get("read_gate", {})
    module_map = read_gate_config.get("module_map", {}) or {}
    state_path = read_gate_config.get("session_state_file", DEFAULT_SESSION_STATE)

    if action == "record":
        record_read(state_path, file_path)
    elif action == "check":
        error = check_gate(state_path, file_path, module_map)
        if error:
            print(error)
            sys.exit(1)
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
