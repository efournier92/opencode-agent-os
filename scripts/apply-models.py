#!/usr/bin/env python3
"""Generate per-profile OpenCode agents and the sample config from models.yaml.

models.yaml is the single source of truth: it names the profiles, the
tier-to-model map per profile, and which tier each role runs on. Role
prompts are authored once under agents/roles/; this script resolves them
into agents/generated/<profile>-<role>.md with a concrete model injected.

It also enforces the architecture invariant:

    No role or skill file may declare model: in its YAML frontmatter.
    Model pinning lives only in the generated agent files.

If a role source still has a model: line, this script strips it. If any
skill file has a model: line, it exits non-zero so the regression is
loud rather than silent.

Run from the plugin root directory:

    python3 scripts/apply-models.py
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MODELS_YAML = ROOT / "models.yaml"
ROLES_DIR = ROOT / "agents" / "roles"
GENERATED_DIR = ROOT / "agents" / "generated"
SKILLS_DIR = ROOT / "skills"
SAMPLE_CONFIG = ROOT / "opencode.json.sample"

PROFILE_ID_RE = re.compile(r"^[a-z][a-z0-9]*$")

# Matches a single `model:` line. Used only against the frontmatter
# slice of a file (extracted by strip_frontmatter_model_line), never
# against the whole document.
MODEL_LINE_RE = re.compile(r"^[ \t]*model:[ \t]*\S+[ \t]*$")


def load_models(path=MODELS_YAML):
    with open(path) as f:
        data = yaml.safe_load(f)
    for key in ("profiles", "agent_tiers", "default_profile"):
        if key not in data:
            raise SystemExit(f"models.yaml missing required key: {key}")
    return data["profiles"], data["agent_tiers"], data["default_profile"]


def validate_models(profiles, agent_tiers, default_profile, roles_dir=ROLES_DIR):
    """Fail loud on inconsistent models.yaml before touching any file."""
    if default_profile not in profiles:
        raise SystemExit(
            f"default_profile '{default_profile}' is not a profile; "
            f"known profiles: {sorted(profiles)}"
        )
    for pid, profile in profiles.items():
        if not PROFILE_ID_RE.match(pid):
            raise SystemExit(
                f"invalid profile id '{pid}': must match ^[a-z][a-z0-9]*$"
            )
        if "tiers" not in profile:
            raise SystemExit(f"profile '{pid}' missing required key: tiers")
        for name, tier in agent_tiers.items():
            if tier not in profile["tiers"]:
                raise SystemExit(
                    f"profile '{pid}' missing tier '{tier}' required by agent "
                    f"'{name}'; known tiers: {sorted(profile['tiers'])}"
                )
    for name in agent_tiers:
        if not (roles_dir / f"{name}.md").is_file():
            raise SystemExit(
                f"agent_tiers entry '{name}' has no agents/roles/{name}.md"
            )


def strip_frontmatter_model_line(content):
    """Strip `model:` lines from the YAML frontmatter only; body untouched.

    Returns (new_content, n_stripped). Idempotent.
    """
    if not content.startswith("---"):
        return content, 0
    end = content.find("\n---", 3)
    if end == -1:
        return content, 0
    fm = content[3:end + 1]
    lines = fm.splitlines(keepends=True)
    kept = []
    n = 0
    for line in lines:
        if MODEL_LINE_RE.match(line.rstrip("\n")):
            n += 1
        else:
            kept.append(line)
    if n == 0:
        return content, 0
    new_fm = "".join(kept)
    return content[:3] + new_fm + content[end + 1:], n


def strip_agent_model_lines(roles_dir=ROLES_DIR):
    """Remove any `model:` line from agents/roles/*.md frontmatter.

    The generated files are the source of truth for model pins; role
    sources must not pin one. Idempotent: no-op when absent.
    """
    if not roles_dir.is_dir():
        return 0
    changed = 0
    for path in sorted(roles_dir.glob("*.md")):
        content = path.read_text()
        new_content, n = strip_frontmatter_model_line(content)
        if n:
            path.write_text(new_content)
            print(f"Stripped model: line from {path.name}")
            changed += 1
    return changed


def assert_no_skill_model_lines(skills_dir=SKILLS_DIR):
    """Skill frontmatter must never pin a model. Fail loud if one does."""
    if not skills_dir.is_dir():
        return
    offenders = []
    for path in sorted(skills_dir.rglob("SKILL.md")):
        content = path.read_text()
        if strip_frontmatter_model_line(content)[1] > 0:
            offenders.append(path)
    if offenders:
        for p in offenders:
            print(f"error: skill frontmatter pins a model: {p}", file=sys.stderr)
        raise SystemExit(
            "skills must not declare model: in frontmatter; "
            "model pinning belongs in generated agent files"
        )


def split_frontmatter(content):
    """Return (frontmatter_lines, body_lines) for a role file."""
    lines = content.split("\n")
    if not lines or lines[0] != "---":
        raise SystemExit("role file missing YAML frontmatter")
    end = lines.index("---", 1)
    return lines[1:end], lines[end + 1:]


def generate_agent(role_content, model, prefix, is_chief):
    """Resolve one role file for one profile into generated-file text."""
    text = role_content.replace("{{prefix}}", prefix)
    fm_lines, body_lines = split_frontmatter(text)
    fm = yaml.safe_load("\n".join(fm_lines)) or {}

    # A role source must not pin a model; the generator owns that field.
    fm.pop("model", None)
    out = {"description": fm["description"], "mode": fm["mode"], "model": model}
    if "options" in fm:
        out["options"] = fm["options"]
    permission = fm.get("permission")
    if permission is not None:
        if is_chief:
            permission = dict(permission)
            permission["task"] = {"*": "deny", f"*-{prefix}": "allow"}
        out["permission"] = permission

    rendered = "---\n"
    rendered += yaml.safe_dump(out, sort_keys=False, default_flow_style=False)
    rendered += "---\n"
    rendered += "\n".join(body_lines)
    if "{{" in rendered:
        raise SystemExit("unresolved {{ token in generated agent")
    return rendered


def resolved_name(prefix, role):
    """Every agent is `<role>-<prefix>` (for example `builder-ds`)."""
    return f"{role}-{prefix}"


def generate_agents(profiles, agent_tiers, roles_dir=ROLES_DIR,
                    generated_dir=GENERATED_DIR):
    """Write agents/generated/<resolved_name>.md; return count changed."""
    generated_dir.mkdir(parents=True, exist_ok=True)
    changed = 0
    for prefix, profile in profiles.items():
        for role, tier in agent_tiers.items():
            role_content = (roles_dir / f"{role}.md").read_text()
            content = generate_agent(
                role_content, profile["tiers"][tier], prefix, role == "chief"
            )
            path = generated_dir / f"{resolved_name(prefix, role)}.md"
            existing = path.read_text() if path.exists() else None
            if existing != content:
                path.write_text(content)
                changed += 1
    expected = {
        f"{resolved_name(prefix, role)}.md"
        for prefix in profiles
        for role in agent_tiers
    }
    for path in generated_dir.glob("*.md"):
        if path.name not in expected:
            path.unlink()
            changed += 1
    return changed


def render_sample_config(profiles, agent_tiers, default_profile):
    profile = profiles[default_profile]
    return {
        "$schema": "https://opencode.ai/config.json",
        "model": profile["tiers"][agent_tiers["chief"]],
        "default_agent": resolved_name(default_profile, "chief"),
        "permission": {
            "edit": "ask",
            "bash": "ask",
            "skill": {"*": "allow"},
        },
        "agent": {
            "build": {"disable": True},
            "scout": {"disable": True},
        },
    }


def write_sample_config(config, path=SAMPLE_CONFIG):
    """Serialize the rendered config to disk. Returns (rendered_text, changed).

    Skip the write when the rendered text already matches the file on disk,
    so re-running with no changes leaves the mtime untouched.
    """
    rendered = json.dumps(config, indent=2) + "\n"
    existing = path.read_text() if path.exists() else None
    if existing == rendered:
        return rendered, False
    with open(path, "w") as f:
        f.write(rendered)
    return rendered, True


def run(root=ROOT):
    models_yaml = root / "models.yaml"
    roles_dir = root / "agents" / "roles"
    generated_dir = root / "agents" / "generated"
    skills_dir = root / "skills"
    sample_config = root / "opencode.json.sample"

    profiles, agent_tiers, default_profile = load_models(models_yaml)
    print(f"Profiles: {sorted(profiles)}")
    print(f"Default profile: {default_profile}")
    print(f"Agent tiers: {agent_tiers}")

    validate_models(profiles, agent_tiers, default_profile, roles_dir)
    assert_no_skill_model_lines(skills_dir)
    stripped = strip_agent_model_lines(roles_dir)
    generated = generate_agents(profiles, agent_tiers, roles_dir, generated_dir)

    rendered, sample_changed = write_sample_config(
        render_sample_config(profiles, agent_tiers, default_profile), sample_config
    )
    if sample_changed:
        print(f"Updated {sample_config.name}")
    else:
        print(f"{sample_config.name} already up to date")

    on_disk = sample_config.read_text()
    if on_disk != rendered:
        raise SystemExit(
            "internal: opencode.json.sample on disk does not match in-memory render"
        )

    if stripped:
        print(f"Stripped {stripped} stale role model: line(s).")
    print(f"Generated {generated} agent file(s) changed.")
    print("Done.")
    return stripped, generated, sample_changed


def main():
    run(ROOT)


if __name__ == "__main__":
    main()
