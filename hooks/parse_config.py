#!/usr/bin/env python3
# Area: Hooks
# PRD: plans/2026-04-05-template-enforcement-overhaul.md
# NOTE: After making any changes to this file, read CLAUDE.md, follow the guidelines, and update the relevant docs.
"""Parse compliance_config.yaml and output KEY=VALUE pairs for shell hooks.

Usage: python3 hooks/parse_config.py <key_path>
Example: python3 hooks/parse_config.py pre_commit.max_file_lines
         → 150

For list values, outputs one item per line.
For dict values, outputs key=value per line.
"""
import sys
import yaml


def resolve(data, path):
    """Walk a dotted path into a nested dict."""
    keys = path.split(".")
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_config.py <key_path>", file=sys.stderr)
        sys.exit(1)

    config_path = "compliance_config.yaml"
    key_path = sys.argv[1]

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    value = resolve(config, key_path)
    if value is None:
        sys.exit(1)

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"{k}={v}")
                print("---")
            else:
                print(item)
    elif isinstance(value, dict):
        for k, v in value.items():
            print(f"{k}={v}")
    else:
        print(value)


if __name__ == "__main__":
    main()
