#!/usr/bin/env python3
"""Tests for scripts/apply-models.py. Run with:

    python3 -m unittest scripts/test_apply_models.py -v
"""

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve().parent / "apply-models.py"
ROLES_DIR = REPO / "agents" / "roles"
GENERATED_DIR = REPO / "agents" / "generated"
SAMPLE = REPO / "opencode.json.sample"
ALLOWLIST = REPO / "models.allowlist"

_spec = importlib.util.spec_from_file_location("apply_models", SCRIPT)
apply_models = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(apply_models)


def read_frontmatter(path):
    lines = path.read_text().split("\n")
    end = lines.index("---", 1)
    return yaml.safe_load("\n".join(lines[1:end]))


class TestApplyModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles, cls.default_profile = apply_models.load_models(
            REPO / "models.yaml"
        )

    def test_generates_all_resolved_agents(self):
        for prefix, profile in self.profiles.items():
            for role in profile["roles"]:
                path = GENERATED_DIR / f"{apply_models.resolved_name(prefix, role)}.md"
                self.assertTrue(path.is_file(), f"missing {path}")

    def test_model_resolution(self):
        for prefix, profile in self.profiles.items():
            for role, model in profile["roles"].items():
                fm = read_frontmatter(
                    GENERATED_DIR / f"{apply_models.resolved_name(prefix, role)}.md"
                )
                self.assertEqual(fm["model"], model)

    def test_role_sources_have_no_model(self):
        for path in sorted(ROLES_DIR.glob("*.md")):
            _, stripped = apply_models.strip_frontmatter_model_line(path.read_text())
            self.assertEqual(stripped, 0, f"{path.name} pins a model")

    def test_no_unresolved_tokens(self):
        for path in sorted(GENERATED_DIR.glob("*.md")):
            self.assertNotIn("{{", path.read_text(), f"{path.name} has a token")

    def test_chief_task_scope(self):
        for prefix in self.profiles:
            fm = read_frontmatter(
                GENERATED_DIR / f"{apply_models.resolved_name(prefix, 'chief')}.md"
            )
            self.assertEqual(
                fm["permission"]["task"],
                {"*": "deny", f"*-{prefix}": "allow"},
            )

    def test_only_chief_has_task_scope(self):
        for prefix, profile in self.profiles.items():
            for role in profile["roles"]:
                fm = read_frontmatter(
                    GENERATED_DIR / f"{apply_models.resolved_name(prefix, role)}.md"
                )
                has_task = "task" in (fm.get("permission") or {})
                self.assertEqual(
                    has_task, role == "chief", f"{prefix}-{role} task scope"
                )

    def test_chief_is_primary(self):
        for prefix, profile in self.profiles.items():
            for role in profile["roles"]:
                fm = read_frontmatter(
                    GENERATED_DIR / f"{apply_models.resolved_name(prefix, role)}.md"
                )
                expected = "primary" if role == "chief" else "subagent"
                self.assertEqual(fm["mode"], expected, f"{prefix}-{role}")

    def test_sample_config_shape(self):
        config = json.loads(SAMPLE.read_text())
        self.assertEqual(
            config["default_agent"],
            apply_models.resolved_name(self.default_profile, "chief"),
        )
        self.assertTrue(config["agent"]["build"]["disable"])
        self.assertTrue(config["agent"]["scout"]["disable"])
        self.assertEqual(
            config["permission"]["external_directory"], {"/tmp/*": "allow"}
        )

    def test_role_models_use_known_providers(self):
        # Profiles may mix providers per seat, so no single-provider
        # assertion can hold. Keep the typo-catching spirit: every pinned
        # model must use a known provider prefix.
        known = {"deepseek", "zai-coding-plan", "zai", "google", "openrouter", "ollama"}
        for prefix, profile in self.profiles.items():
            for role, model in profile["roles"].items():
                self.assertIn(
                    model.split("/", 1)[0],
                    known,
                    f"{prefix} {role} -> {model}",
                )

    def test_model_ids_allowlisted(self):
        # The shipped models.yaml must pass shape + allowlist validation.
        apply_models.validate_models(self.profiles, self.default_profile, ROLES_DIR)

    def test_bad_model_shape_fails(self):
        bad = {"ds": {"roles": {"chief": "noshape"}}}
        with self.assertRaises(SystemExit):
            apply_models.validate_model_ids(bad)

    def test_model_not_in_allowlist_fails(self):
        bad = {"ds": {"roles": {"chief": "vendor/unlisted-model"}}}
        with self.assertRaises(SystemExit):
            apply_models.validate_model_ids(bad)

    def test_colon_model_id_allowed(self):
        # An Ollama tag carries a colon in the model segment; the allowlist
        # (not the regex) remains the gate.
        apply_models.validate_model_ids(
            {"local": {"roles": {"chief": "ollama/qwen3.6:35b-a3b"}}}
        )

    def test_profile_options_merge(self):
        chief = read_frontmatter(GENERATED_DIR / "chief-local.md")
        self.assertEqual(chief["options"], {"reasoningEffort": "low"})
        builder = read_frontmatter(GENERATED_DIR / "builder-local.md")
        self.assertEqual(builder["options"], {"reasoningEffort": "low"})
        ds_chief = read_frontmatter(GENERATED_DIR / "chief-ds.md")
        self.assertNotIn("num_ctx", ds_chief.get("options", {}))

    def test_profile_options_bad_type_fails(self):
        profiles = dict(self.profiles)
        profiles["zz"] = {
            "label": "Bad",
            "options": "nope",
            "roles": dict(self.profiles["ds"]["roles"]),
        }
        with self.assertRaises(SystemExit):
            apply_models.validate_models(profiles, self.default_profile, ROLES_DIR)

    def test_all_local_agents_pinned_and_tuned(self):
        local_roles = self.profiles["local"]["roles"]
        self.assertEqual(len(local_roles), 14)
        for role in local_roles:
            fm = read_frontmatter(GENERATED_DIR / f"{role}-local.md")
            self.assertEqual(fm["model"], "ollama/qwen3.6:35b-a3b", role)
            self.assertEqual(fm["options"], {"reasoningEffort": "low"}, role)

    def test_malformed_model_ids_fail(self):
        for bad_id in ("ollama/", "a/b/c", "noshape", "ollama/qwen3:v2:extra"):
            with self.assertRaises(SystemExit):
                apply_models.validate_model_ids(
                    {"x": {"roles": {"chief": bad_id}}}
                )

    def test_idempotent(self):
        _, generated, sample = apply_models.run(REPO)
        self.assertEqual(generated, 0)
        self.assertEqual(sample, 0)

    def test_check_reports_clean(self):
        self.assertEqual(apply_models.run_check(REPO), 0)

    def test_check_detects_missing_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents" / "roles").mkdir(parents=True)
            (root / "agents" / "generated").mkdir(parents=True)
            shutil.copy(REPO / "models.yaml", root / "models.yaml")
            shutil.copy(ALLOWLIST, root / "models.allowlist")
            for path in ROLES_DIR.glob("*.md"):
                shutil.copy(path, root / "agents" / "roles" / path.name)
            self.assertNotEqual(apply_models.run_check(root), 0)

    def test_check_clean_after_generate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents" / "roles").mkdir(parents=True)
            (root / "agents" / "generated").mkdir(parents=True)
            shutil.copy(REPO / "models.yaml", root / "models.yaml")
            shutil.copy(ALLOWLIST, root / "models.allowlist")
            for path in ROLES_DIR.glob("*.md"):
                shutil.copy(path, root / "agents" / "roles" / path.name)
            apply_models.run(root)
            self.assertEqual(apply_models.run_check(root), 0)

    def test_check_detects_stale_sample(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents" / "roles").mkdir(parents=True)
            (root / "agents" / "generated").mkdir(parents=True)
            shutil.copy(REPO / "models.yaml", root / "models.yaml")
            shutil.copy(ALLOWLIST, root / "models.allowlist")
            for path in ROLES_DIR.glob("*.md"):
                shutil.copy(path, root / "agents" / "roles" / path.name)
            apply_models.run(root)
            self.assertEqual(apply_models.run_check(root), 0)
            (root / "opencode.json.sample").write_text("{}\n")
            self.assertNotEqual(apply_models.run_check(root), 0)

    def test_third_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents" / "roles").mkdir(parents=True)
            (root / "agents" / "generated").mkdir(parents=True)
            shutil.copy(REPO / "models.yaml", root / "models.yaml")
            shutil.copy(ALLOWLIST, root / "models.allowlist")
            for path in ROLES_DIR.glob("*.md"):
                shutil.copy(path, root / "agents" / "roles" / path.name)

            data = yaml.safe_load((root / "models.yaml").read_text())
            data["profiles"]["zz"] = {
                "label": "Temp",
                "roles": dict(data["profiles"]["ds"]["roles"]),
            }
            (root / "models.yaml").write_text(yaml.safe_dump(data))

            stale = root / "agents" / "generated" / "zz-stale.md"
            stale.write_text("stale")

            apply_models.run(root)

            for role in data["profiles"]["zz"]["roles"]:
                path = (
                    root
                    / "agents"
                    / "generated"
                    / f"{apply_models.resolved_name('zz', role)}.md"
                )
                self.assertTrue(path.is_file(), f"missing {path}")
            self.assertFalse(stale.exists(), "stale generated file not pruned")

    def test_validation_errors(self):
        profiles, default_profile = (self.profiles, self.default_profile)

        with self.assertRaises(SystemExit):
            apply_models.validate_models(profiles, "nope", ROLES_DIR)

        bad_profiles = dict(profiles)
        bad_profiles["bad!id"] = profiles["ds"]
        with self.assertRaises(SystemExit):
            apply_models.validate_models(bad_profiles, default_profile, ROLES_DIR)

        missing_role = dict(profiles)
        missing_role["ds"] = {
            "label": "DeepSeek",
            "roles": {k: v for k, v in profiles["ds"]["roles"].items()
                      if k != "verifier"},
        }
        with self.assertRaises(SystemExit):
            apply_models.validate_models(missing_role, default_profile, ROLES_DIR)

        unknown_role = dict(profiles)
        unknown_role["ds"] = dict(profiles["ds"])
        unknown_role["ds"]["roles"] = dict(profiles["ds"]["roles"])
        unknown_role["ds"]["roles"]["ghost"] = "deepseek/deepseek-flash"
        with self.assertRaises(SystemExit):
            apply_models.validate_models(unknown_role, default_profile, ROLES_DIR)

        no_roles = dict(profiles)
        no_roles["zz"] = {"label": "Empty"}
        with self.assertRaises(SystemExit):
            apply_models.validate_models(no_roles, default_profile, ROLES_DIR)

    def test_no_skill_model_lines(self):
        apply_models.assert_no_skill_model_lines()

    def test_nonlocal_generated_agent_unchanged(self):
        fm = read_frontmatter(GENERATED_DIR / "chief-ds+glm.md")
        self.assertEqual(
            fm["permission"]["task"], {"*": "deny", "*-ds+glm": "allow"}
        )
        self.assertEqual(fm["permission"]["skill"], "allow")
        self.assertEqual(fm["permission"]["bash"], "allow")
        self.assertEqual(fm["permission"]["webfetch"], "allow")
        self.assertEqual(fm["permission"]["websearch"], "allow")


if __name__ == "__main__":
    unittest.main()
