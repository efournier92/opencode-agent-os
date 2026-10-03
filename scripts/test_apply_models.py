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
        known = {"deepseek", "zai-coding-plan", "zai", "google", "openrouter"}
        for prefix, profile in self.profiles.items():
            for role, model in profile["roles"].items():
                if role == "photo-generator":
                    continue
                self.assertIn(
                    model.split("/", 1)[0],
                    known,
                    f"{prefix} {role} -> {model}",
                )

    def test_idempotent(self):
        _, generated, sample = apply_models.run(REPO)
        self.assertEqual(generated, 0)
        self.assertEqual(sample, 0)

    def test_third_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents" / "roles").mkdir(parents=True)
            (root / "agents" / "generated").mkdir(parents=True)
            shutil.copy(REPO / "models.yaml", root / "models.yaml")
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
                      if k != "qa"},
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


if __name__ == "__main__":
    unittest.main()
