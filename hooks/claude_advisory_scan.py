#!/usr/bin/env python3
# Area: Hooks
# PRD: plans/2026-04-05-template-enforcement-overhaul.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Claude Code PostToolUse hook: advisory scanner.

Scans files after Edit/Write for:
1. Advisory hardcoded value patterns (non-blocking warnings)
2. Line count approaching the limit (warning at 90%+)

Reads patterns from compliance_config.yaml advisory section.
"""
import json
import os
import re
import sys
import time
import yaml


CONFIG_PATH = "compliance_config.yaml"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def scan_hardcoded(file_path, warn_patterns):
    """Scan a file for advisory hardcoded value patterns.

    Returns list of (line_number, line_text, description) tuples.
    """
    matches = []
    with open(file_path, "r") as f:
        for i, line in enumerate(f, 1):
            for pattern_def in warn_patterns:
                pattern = pattern_def["pattern"]
                description = pattern_def["description"]
                if re.search(pattern, line):
                    matches.append((i, line.rstrip(), description))
    return matches


def check_line_count(file_path, max_lines):
    """Check if file is approaching line limit.

    Returns (current_count, remaining) or None if not near limit.
    """
    with open(file_path, "r") as f:
        count = sum(1 for _ in f)

    threshold = int(max_lines * 0.9)  # Warn at 90%
    if count >= threshold:
        return count, max_lines - count
    return None


def log_dismissal(dismissal_log, file_path, line_num, pattern, reason):
    """Append a dismissal to the advisory dismissals log."""
    os.makedirs(os.path.dirname(dismissal_log), exist_ok=True)

    dismissals = []
    if os.path.exists(dismissal_log):
        with open(dismissal_log, "r") as f:
            dismissals = json.load(f)

    dismissals.append({
        "file": file_path,
        "line": line_num,
        "pattern": pattern,
        "reason": reason,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })

    with open(dismissal_log, "w") as f:
        json.dump(dismissals, f, indent=2)


def main():
    """Entry point. Usage: scan <file_path> | dismiss <file>:<line> <pattern> <reason>."""
    if len(sys.argv) < 3:
        print("Usage: claude_advisory_scan.py <scan|dismiss> <args...>", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    config = load_config()

    if action == "scan":
        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            sys.exit(0)

        warn_patterns = config.get("advisory", {}).get("hardcoded_values", {}).get("warn", [])
        max_lines = config.get("pre_commit", {}).get("max_file_lines", 150)

        output_lines = []

        # Check hardcoded patterns
        matches = scan_hardcoded(file_path, warn_patterns)
        if matches:
            output_lines.append(f"⚠ ADVISORY: {file_path}")
            for line_num, line_text, description in matches:
                output_lines.append(f"  Line {line_num}: {line_text}  → {description}")
            output_lines.append("")
            output_lines.append(
                "Review each warning. Fix the violation or DISMISS before your next tool call."
            )

        # Check line count
        result = check_line_count(file_path, max_lines)
        if result:
            count, remaining = result
            output_lines.append(
                f"⚠ LINE COUNT: {file_path} is {count} lines "
                f"(limit: {max_lines}, {remaining} remaining)"
            )

        if output_lines:
            print("\n".join(output_lines))

    elif action == "dismiss":
        # Parse: dismiss <file>:<line> <pattern> <reason>
        if len(sys.argv) < 5:
            print("Usage: dismiss <file>:<line> <pattern> <reason>", file=sys.stderr)
            sys.exit(1)

        file_line = sys.argv[2]
        pattern = sys.argv[3]
        reason = sys.argv[4]

        file_path, line_num = file_line.rsplit(":", 1)
        dismissal_log = config.get("advisory", {}).get("dismissal_log", ".claude/advisory_dismissals.json")
        min_length = config.get("advisory", {}).get("min_justification_length", 20)

        if len(reason) < min_length:
            print(f"⛔ Justification too short ({len(reason)} chars, minimum {min_length})")
            sys.exit(1)

        log_dismissal(dismissal_log, file_path, int(line_num), pattern, reason)
        print(f"✓ Dismissal logged for {file_path}:{line_num}")

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
