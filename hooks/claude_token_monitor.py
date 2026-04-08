#!/usr/bin/env python3
# Area: Hooks
# PRD: plans/2026-04-05-template-enforcement-overhaul.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Claude Code PostToolUse hook: token size monitor.

Checks if edited .md files exceed a token threshold that would prevent
subagents from reading them. Warns before the file becomes unreadable.

Token estimation: ~1.3 tokens per word (conservative for structured text).
Subagent read limit: 10000 tokens.
Warning threshold: 8000 tokens (80% of limit).
"""
import os
import sys

WARNING_THRESHOLD_TOKENS = 8000
HARD_LIMIT_TOKENS = 10000
TOKENS_PER_WORD = 1.3

# Only monitor these critical files that subagents must read
MONITORED_PATTERNS = [
    "CLAUDE.md",
    "CONTEXT.md",
    "CONTEXT_FILEMAP.md",
    "ContextModuleDocumentation/CONTEXT_",
]


def estimate_tokens(text):
    """Estimate token count from text content."""
    words = len(text.split())
    return int(words * TOKENS_PER_WORD)


def is_monitored(file_path):
    """Check if the file matches a monitored pattern."""
    for pattern in MONITORED_PATTERNS:
        if pattern in file_path:
            return True
    return False


def check_file(file_path):
    """Check if a .md file exceeds the token threshold."""
    if not file_path.endswith(".md"):
        return None
    if not is_monitored(file_path):
        return None
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        content = f.read()

    tokens = estimate_tokens(content)
    lines = len(content.splitlines())

    if tokens >= HARD_LIMIT_TOKENS:
        return (
            f"TOKEN LIMIT: {os.path.basename(file_path)} has ~{tokens} tokens "
            f"({lines} lines) — EXCEEDS the 10000-token subagent read limit. "
            f"Subagents will fail to read this file. "
            f"Extract content to a separate file immediately."
        )
    if tokens >= WARNING_THRESHOLD_TOKENS:
        return (
            f"TOKEN WARNING: {os.path.basename(file_path)} has ~{tokens} tokens "
            f"({lines} lines) — approaching the 10000-token subagent read limit. "
            f"Consider extracting large sections to separate files."
        )
    return None


def main():
    """Entry point: python3 hooks/claude_token_monitor.py <file_path>"""
    if len(sys.argv) < 2:
        sys.exit(0)

    file_path = sys.argv[1]
    warning = check_file(file_path)
    if warning:
        print(warning)
        # Non-blocking — exit 0 so it's advisory, not a gate
    sys.exit(0)


if __name__ == "__main__":
    main()
