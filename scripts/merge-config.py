#!/usr/bin/env python3
"""Merge plugin-managed preference keys from a sample into an existing config.

Usage:

    merge-config.py <existing-config> <sample-config>

Only the leaf paths listed in MANAGED are overridden; every other key in the
existing config is preserved. The existing file is rewritten as indent-2 JSON
only when a managed value actually changes.
"""

import json
import sys

# Complete allowlist of plugin-managed leaf paths (dot notation). Extend this
# list, not the merge logic, when the plugin owns another preference key.
MANAGED = [
    "default_agent",
    "subagent_depth",
    "compaction.prune",
    "agent.build.disable",
    "agent.scout.disable",
]


def get(data, path):
    """Return (value, present) for a dot path; present is False if absent."""
    node = data
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None, False
        node = node[part]
    return node, True


def set_leaf(data, path, value):
    parts = path.split(".")
    node = data
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            # minimalist: a managed path owns its container, so a non-dict
            # value is replaced rather than merged. Widen only if a real
            # config needs a non-dict intermediate.
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


def merge(existing, sample):
    """Apply every managed sample leaf to existing in place; return changes."""
    changes = []
    for path in MANAGED:
        value, present = get(sample, path)
        if not present:
            continue
        old, had = get(existing, path)
        if had and old == value:
            continue
        set_leaf(existing, path, value)
        changes.append((path, old, value, had))
    return changes


def main(argv):
    if len(argv) != 3:
        print(
            "usage: merge-config.py <existing-config> <sample-config>",
            file=sys.stderr,
        )
        return 2

    existing_path, sample_path = argv[1], argv[2]
    try:
        with open(existing_path) as f:
            existing = json.loads(f.read())
        with open(sample_path) as f:
            sample = json.loads(f.read())
    except (OSError, ValueError) as exc:
        # minimalist: strict JSON only, no JSONC comment stripping. A config
        # with comments is left alone and merged by hand. Add a tolerant
        # parser only when JSONC configs become the norm.
        print(
            f"warning: cannot merge config ({exc}); "
            f"merge {sample_path} by hand",
            file=sys.stderr,
        )
        return 3

    changes = merge(existing, sample)
    if not changes:
        print("no changes")
        return 0

    for path, old, new, had in changes:
        print(f"set {path}: {json.dumps(old) if had else '(unset)'} -> {json.dumps(new)}")
    with open(existing_path, "w") as f:
        f.write(json.dumps(existing, indent=2) + "\n")
    print(f"wrote {existing_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
