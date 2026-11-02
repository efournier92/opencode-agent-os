#!/usr/bin/env python3
"""Archive a model profile to configs/archive/<stamp>_<profile>.yaml and drop it from models.yaml.

With --copy, write a reference snapshot of an active profile to
configs/snapshots/<stamp>_<profile>.yaml without changing models.yaml or generated agents.
"""

import argparse
import importlib.util
import re
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
HEADER = (
    "# Archived model profile: {profile} (archive month {stamp}).\n"
    "# Retired from models.yaml; not generated or installed.\n"
    "# Restore: re-indent under `profiles:` in models.yaml, then run\n"
    "# python3 scripts/apply-models.py\n"
    "\n"
)
SNAPSHOT_HEADER = (
    "# Snapshot of active model profile: {profile} (snapshot month {stamp}).\n"
    "# Kept active in models.yaml and installed; this is a reference copy.\n"
    "\n"
)


def _load_apply():
    path = Path(__file__).resolve().parent / "apply-models.py"
    spec = importlib.util.spec_from_file_location("apply_models", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def extract(text, profile):
    """Return (block_lines, all_lines, start, end) for a profile block."""
    lines = text.splitlines(keepends=True)
    start = next(
        (i for i, line in enumerate(lines) if re.match(rf"^  {re.escape(profile)}:", line)),
        None,
    )
    if start is None:
        raise SystemExit(f"profile '{profile}' not found under profiles:")
    end = start + 1
    while end < len(lines) and not re.match(r"^(  [A-Za-z0-9]|\S)", lines[end]):
        end += 1
    return lines[start:end], lines, start, end


def _standalone(text, profile, profiles, header, stamp):
    """Return the profile block as a standalone, dedented, role-checked YAML document."""
    block, lines, start, end = extract(text, profile)
    document = header.format(profile=profile, stamp=stamp) + "".join(
        line[2:] if line.startswith("  ") else line for line in block
    )
    parsed = yaml.safe_load(document)
    if parsed.get(profile, {}).get("roles") != profiles[profile]["roles"]:
        raise SystemExit(f"standalone text for '{profile}' is invalid; aborting")
    return document, lines, start, end


def snapshot(root, profile, stamp, dry_run=False):
    models_path = root / "models.yaml"
    text = models_path.read_text()
    profiles = yaml.safe_load(text).get("profiles", {})
    if profile not in profiles:
        raise SystemExit(f"profile '{profile}' not found under profiles:")

    document, _, _, _ = _standalone(text, profile, profiles, SNAPSHOT_HEADER, stamp)
    out = root / "configs" / "snapshots" / f"{stamp}_{profile}.yaml"
    if dry_run:
        print(f"Would snapshot '{profile}' to {out}")
        return out

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(document)
    print(f"Snapshotted '{profile}' to {out}")
    return out


def archive(root, profile, stamp, dry_run=False):
    models_path = root / "models.yaml"
    text = models_path.read_text()
    data = yaml.safe_load(text)
    profiles = data.get("profiles", {})
    if profile not in profiles:
        raise SystemExit(f"profile '{profile}' not found under profiles:")
    if profile == data.get("default_profile"):
        raise SystemExit(f"refusing to archive default_profile '{profile}'")

    archived, lines, start, end = _standalone(text, profile, profiles, HEADER, stamp)

    out = root / "configs" / "archive" / f"{stamp}_{profile}.yaml"
    if dry_run:
        print(f"Would archive '{profile}' to {out}")
        print(f"Would remove '{profile}' from {models_path}")
        return out

    rest = lines[:start] + lines[end:]
    if start and start < len(rest) and not rest[start - 1].strip() and not rest[start].strip():
        del rest[start]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(archived)
    models_path.write_text("".join(rest))
    _, generated, _ = _load_apply().run(root)
    print(f"Archived '{profile}' to {out}")
    print(f"Generated files changed: {generated}")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile")
    parser.add_argument("--stamp", default=date.today().strftime("%Y-%m"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--copy", action="store_true", help="snapshot an active profile")
    args = parser.parse_args(argv)
    if args.copy:
        snapshot(ROOT, args.profile, args.stamp, args.dry_run)
    else:
        archive(ROOT, args.profile, args.stamp, args.dry_run)


if __name__ == "__main__":
    main()
