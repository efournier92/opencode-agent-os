#!/usr/bin/env python3
"""Generate per-profile OpenCode agents and the sample config from models.yaml.

models.yaml is the single source of truth: it names the profiles and, per
profile, the concrete model each role runs on (`profiles.<name>.roles`).
Role prompts are authored once under agents/roles/; this script resolves
them into agents/generated/<profile>-<role>.md with a concrete model
injected.

It also enforces the architecture invariant:

    No role or skill file may declare model: in its YAML frontmatter.
    Model pinning lives only in the generated agent files.

If a role source still has a model: line, this script strips it. If any
skill file has a model: line, it exits non-zero so the regression is
loud rather than silent.

Run from the plugin root directory:

    python3 scripts/apply-models.py
    python3 scripts/apply-models.py --check   # report drift, write nothing
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MODELS_YAML = ROOT / "models.yaml"
MODELS_ALLOWLIST = ROOT / "models.allowlist"
ROLES_DIR = ROOT / "agents" / "roles"
GENERATED_DIR = ROOT / "agents" / "generated"
SKILLS_DIR = ROOT / "skills"
SAMPLE_CONFIG = ROOT / "opencode.json.sample"

PROFILE_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_+-]*$")
# The model segment may carry a colon for local tags (for example
# `ollama/qwen3.6:35b-a3b`); the vendor prefix may not. Exactly one slash.
MODEL_ID_RE = re.compile(
    r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+(?::[A-Za-z0-9._-]+)?$"
)

# Matches a single `model:` line. Used only against the frontmatter
# slice of a file (extracted by strip_frontmatter_model_line), never
# against the whole document.
MODEL_LINE_RE = re.compile(r"^[ \t]*model:[ \t]*\S+[ \t]*$")


def load_models(path=MODELS_YAML):
    with open(path) as f:
        data = yaml.safe_load(f)
    for key in ("profiles", "default_profile"):
        if key not in data:
            raise SystemExit(f"models.yaml missing required key: {key}")
    return data["profiles"], data["default_profile"]


def load_allowlist(path=MODELS_ALLOWLIST):
    """Return the set of permitted model ids; `#` starts a comment."""
    if not path.exists():
        raise SystemExit(f"missing model allowlist: {path}")
    allowed = set()
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            allowed.add(line)
    return allowed


def validate_model_ids(profiles, allowlist_path=MODELS_ALLOWLIST):
    """Every pinned model id must be `vendor/model` shaped and allowlisted."""
    allowed = load_allowlist(allowlist_path)
    offenders = []
    for pid, profile in profiles.items():
        for role, model in (profile.get("roles") or {}).items():
            if not isinstance(model, str) or not MODEL_ID_RE.match(model):
                offenders.append(f"{pid}.{role}: {model!r} (bad shape)")
            elif model not in allowed:
                offenders.append(f"{pid}.{role}: {model} (not in allowlist)")
    if offenders:
        for entry in offenders:
            print(f"error: invalid model id {entry}", file=sys.stderr)
        raise SystemExit(
            f"models.yaml has {len(offenders)} invalid model id(s); "
            f"fix them or add the ids to {allowlist_path.name}"
        )


def validate_models(
    profiles, default_profile, roles_dir=ROLES_DIR, allowlist_path=MODELS_ALLOWLIST
):
    """Fail loud on inconsistent models.yaml before touching any file."""
    if default_profile not in profiles:
        raise SystemExit(
            f"default_profile '{default_profile}' is not a profile; "
            f"known profiles: {sorted(profiles)}"
        )
    role_files = {p.stem for p in roles_dir.glob("*.md")}
    for pid, profile in profiles.items():
        if not PROFILE_ID_RE.match(pid):
            raise SystemExit(
                f"invalid profile id '{pid}': must match ^[A-Za-z][A-Za-z0-9_+-]*$"
            )
        if "roles" not in profile:
            raise SystemExit(f"profile '{pid}' missing required key: roles")
        options = profile.get("options")
        if options is not None and not isinstance(options, dict):
            raise SystemExit(
                f"profile '{pid}' options must be a mapping, "
                f"got {type(options).__name__}"
            )
        pinned = set(profile["roles"])
        missing = sorted(role_files - pinned)
        if missing:
            raise SystemExit(
                f"profile '{pid}' has no model for role(s): {missing}"
            )
        unknown = sorted(pinned - role_files)
        if unknown:
            raise SystemExit(
                f"profile '{pid}' pins unknown role(s): {unknown}; "
                f"known roles: {sorted(role_files)}"
            )
    validate_model_ids(profiles, allowlist_path)


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


def generate_agent(role_content, model, prefix, is_chief, profile_options=None):
    """Resolve one role file for one profile into generated-file text.

    A profile-level `options` map (models.yaml) is merged over the role's own
    options, so a profile can lower reasoning effort for every one of its
    agents without editing the shared role source.
    """
    text = role_content.replace("{{prefix}}", prefix)
    fm_lines, body_lines = split_frontmatter(text)
    fm = yaml.safe_load("\n".join(fm_lines)) or {}

    # A role source must not pin a model; the generator owns that field.
    fm.pop("model", None)
    out = {"description": fm["description"], "mode": fm["mode"], "model": model}
    merged_options = dict(fm.get("options") or {})
    merged_options.update(profile_options or {})
    if merged_options:
        out["options"] = merged_options
    permission = fm.get("permission")
    if permission is not None:
        permission = dict(permission)
        if is_chief:
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


def render_agents(profiles, roles_dir=ROLES_DIR):
    """Return {filename: content} for every expected generated agent."""
    expected = {}
    for prefix, profile in profiles.items():
        for role, model in profile["roles"].items():
            role_content = (roles_dir / f"{role}.md").read_text()
            content = generate_agent(
                role_content,
                model,
                prefix,
                role == "chief",
                profile.get("options"),
            )
            expected[f"{resolved_name(prefix, role)}.md"] = content
    return expected


def generate_agents(profiles, roles_dir=ROLES_DIR, generated_dir=GENERATED_DIR):
    """Write agents/generated/<resolved_name>.md; return count changed."""
    generated_dir.mkdir(parents=True, exist_ok=True)
    expected = render_agents(profiles, roles_dir)
    changed = 0
    for name, content in expected.items():
        path = generated_dir / name
        existing = path.read_text() if path.exists() else None
        if existing != content:
            path.write_text(content)
            changed += 1
    expected_lower = {name.lower(): name for name in expected}
    for path in generated_dir.glob("*.md"):
        if path.name in expected:
            continue
        target = expected_lower.get(path.name.lower())
        if target is not None:
            target_path = generated_dir / target
            if path.samefile(target_path):
                # Case-only mismatch on a case-insensitive filesystem: this
                # IS the expected file under a stale-case directory entry.
                # A case-only rename fixes the entry instead of losing the file.
                path.rename(target_path)
                changed += 1
                continue
        path.unlink()
        changed += 1
    return changed


def check_agents(profiles, roles_dir=ROLES_DIR, generated_dir=GENERATED_DIR):
    """Return drift problems between sources and generated files; empty = fresh."""
    expected = render_agents(profiles, roles_dir)
    problems = []
    for name, content in expected.items():
        path = generated_dir / name
        if not path.exists():
            problems.append(f"missing generated agent: {path}")
        elif path.read_text() != content:
            problems.append(f"stale generated agent: {path}")
    if generated_dir.is_dir():
        for path in sorted(generated_dir.glob("*.md")):
            if path.name not in expected:
                problems.append(f"stray generated agent: {path}")
    return problems


def render_sample_config(profiles, default_profile):
    profile = profiles[default_profile]
    return {
        "$schema": "https://opencode.ai/config.json",
        "model": profile["roles"]["chief"],
        "default_agent": resolved_name(default_profile, "chief"),
        "subagent_depth": 2,
        "permission": {
            "edit": "ask",
            "bash": "ask",
            "skill": {"*": "allow"},
            "external_directory": {"/tmp/*": "allow"},
        },
        "compaction": {"prune": True},
        "agent": {
            "build": {"disable": True},
            "scout": {"disable": True},
        },
    }


def render_sample_text(config):
    return json.dumps(config, indent=2) + "\n"


def write_sample_config(config, path=SAMPLE_CONFIG):
    """Serialize the rendered config to disk. Returns (rendered_text, changed).

    Skip the write when the rendered text already matches the file on disk,
    so re-running with no changes leaves the mtime untouched.
    """
    rendered = render_sample_text(config)
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

    profiles, default_profile = load_models(models_yaml)
    print(f"Profiles: {sorted(profiles)}")
    print(f"Default profile: {default_profile}")

    validate_models(profiles, default_profile, roles_dir, root / "models.allowlist")
    assert_no_skill_model_lines(skills_dir)
    stripped = strip_agent_model_lines(roles_dir)
    generated = generate_agents(profiles, roles_dir, generated_dir)

    rendered, sample_changed = write_sample_config(
        render_sample_config(profiles, default_profile), sample_config
    )
    if sample_changed:
        print(f"Updated {sample_config.name}")
    else:
        print(f"{sample_config.name} already up to date")

    if stripped:
        print(f"Stripped {stripped} stale role model: line(s).")
    print(f"Generated {generated} agent file(s) changed.")
    print("Done.")
    return stripped, generated, sample_changed


def run_check(root=ROOT):
    """Report drift between sources and generated files; write nothing."""
    models_yaml = root / "models.yaml"
    roles_dir = root / "agents" / "roles"
    generated_dir = root / "agents" / "generated"
    sample_config = root / "opencode.json.sample"
    profiles, default_profile = load_models(models_yaml)
    validate_models(profiles, default_profile, roles_dir, root / "models.allowlist")
    problems = check_agents(profiles, roles_dir, generated_dir)

    # Render the sample in memory and compare; a stale sample is drift too.
    expected_sample = render_sample_text(
        render_sample_config(profiles, default_profile)
    )
    existing_sample = sample_config.read_text() if sample_config.exists() else None
    if existing_sample != expected_sample:
        problems.append(f"stale sample config: {sample_config}")

    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print(
            f"generated agents stale ({len(problems)} problem(s)); "
            "run scripts/apply-models.py",
            file=sys.stderr,
        )
        return 1
    print("generated agents fresh")
    return 0


def main():
    if "--check" in sys.argv[1:]:
        sys.exit(run_check(ROOT))
    run(ROOT)


if __name__ == "__main__":
    main()
