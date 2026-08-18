from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_catalog", ROOT / "development/scripts/check_catalog.py"
)
assert SPEC and SPEC.loader
CHECK_CATALOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_CATALOG)


class CatalogContractTests(unittest.TestCase):
    def test_isolated_catalog_copy_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            isolated_catalog = Path(temporary) / "catalog"
            shutil.copytree(ROOT / "catalog", isolated_catalog)

            self.assertEqual(
                [], CHECK_CATALOG.validate_catalog(isolated_catalog)
            )
            self.assertFalse((Path(temporary) / "README.md").exists())
            self.assertFalse((Path(temporary) / "development").exists())
            self.assertFalse((Path(temporary) / ".codex").exists())
            self.assertFalse((Path(temporary) / ".claude").exists())

    def test_isolated_catalog_requires_a_license(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            isolated_catalog = Path(temporary) / "catalog"
            shutil.copytree(ROOT / "catalog", isolated_catalog)
            (isolated_catalog / "LICENSE").unlink()

            self.assertIn(
                "missing catalog/LICENSE",
                CHECK_CATALOG.validate_catalog(isolated_catalog),
            )

    def test_install_contract_rejects_repository_only_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            isolated_catalog = Path(temporary) / "catalog"
            shutil.copytree(ROOT / "catalog", isolated_catalog)
            install_path = isolated_catalog / "INSTALL.md"
            install_path.write_text(
                install_path.read_text(encoding="utf-8")
                + "\nRead ../development/tests/smoke/README.md and "
                "../.codex/agents/reviewer.toml before installation.\n",
                encoding="utf-8",
            )

            errors = CHECK_CATALOG.validate_catalog(isolated_catalog)

            self.assertIn(
                "catalog/INSTALL.md references repository-only path: ../", errors
            )
            self.assertIn(
                "catalog/INSTALL.md references repository-only path: development/",
                errors,
            )

    def test_install_contract_allows_native_target_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            isolated_catalog = Path(temporary) / "catalog"
            shutil.copytree(ROOT / "catalog", isolated_catalog)
            install_path = isolated_catalog / "INSTALL.md"
            install_path.write_text(
                install_path.read_text(encoding="utf-8")
                + "\nCreate `.codex/agents/reviewer.toml` in the target.\n",
                encoding="utf-8",
            )

            self.assertEqual(
                [], CHECK_CATALOG.validate_catalog(isolated_catalog)
            )

    def test_duplicate_agent_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "catalog/agents").mkdir(parents=True)
            (root / "catalog/adapters/example").mkdir(parents=True)
            (root / "catalog/INSTALL.md").write_text("contract\n", encoding="utf-8")
            (root / "catalog/LICENSE").write_text("license\n", encoding="utf-8")
            definition = (
                "---\nname: worker\ndescription: Worker\nread_only: false\n---\n\n"
                "AGENTS.md is already in context; follow it.\n"
            )
            (root / "catalog/agents/worker.md").write_text(definition, encoding="utf-8")
            target = ".example/agents/<agent>.md"
            (root / "catalog/adapters/example/ADAPTER.md").write_text(
                f"Install at {target}.\n", encoding="utf-8"
            )
            catalog = {
                "schema_version": 1,
                "agents": [
                    {"name": "worker", "definition": "agents/worker.md"},
                    {"name": "worker", "definition": "agents/worker.md"},
                ],
                "adapters": [
                    {
                        "name": "example",
                        "instructions": "adapters/example/ADAPTER.md",
                        "agent_target": target,
                        "instruction_targets": ["AGENTS.md"],
                        "skill_targets": [".example/skills/<skill>/SKILL.md"],
                    }
                ],
            }
            (root / "catalog/catalog.json").write_text(
                json.dumps(catalog), encoding="utf-8"
            )
            (root / "README.md").write_text(
                "](catalog/agents/worker.md)\n](catalog/adapters/example/ADAPTER.md)\n",
                encoding="utf-8",
            )

            errors = CHECK_CATALOG.validate_catalog(root / "catalog")
            self.assertTrue(
                any("duplicate agent names: worker" in error for error in errors), errors
            )

    def test_duplicated_non_string_names_return_validation_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            catalog_path = root / "catalog/catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["agents"][0]["name"] = ["invalid"]
            catalog["agents"][1]["name"] = ["invalid"]
            catalog["adapters"][0]["name"] = {"invalid": True}
            catalog["adapters"][1]["name"] = {"invalid": True}
            component = dict(catalog["optional_components"][0])
            component["name"] = ["invalid"]
            catalog["optional_components"][0]["name"] = ["invalid"]
            catalog["optional_components"].append(component)
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

            errors = CHECK_CATALOG.validate_catalog(root / "catalog")

            self.assertIn("invalid agent name: ['invalid']", errors)
            self.assertIn("invalid adapter name: {'invalid': True}", errors)
            self.assertIn("invalid optional component name: ['invalid']", errors)

    def test_non_string_paths_and_targets_return_validation_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            catalog_path = root / "catalog/catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["agents"][0]["definition"] = ["agents/plan-search.md"]
            catalog["adapters"][0]["instructions"] = {
                "path": "adapters/codex/ADAPTER.md"
            }
            catalog["adapters"][0]["agent_target"] = [
                ".codex/agents/<agent>.toml"
            ]
            catalog["adapters"][0]["instruction_targets"] = [["AGENTS.md"]]
            catalog["optional_components"][0]["path"] = {"path": "components/plans"}
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

            errors = CHECK_CATALOG.validate_catalog(root / "catalog")

            self.assertIn(
                "agent definition must be a non-empty string: "
                "['agents/plan-search.md']",
                errors,
            )
            self.assertTrue(
                any(
                    "agent_target must be a non-empty string" in error
                    for error in errors
                ),
                errors,
            )
            self.assertIn(
                "adapter 'codex' instruction_targets must be a non-empty list "
                "of non-empty strings",
                errors,
            )
            self.assertIn(
                "adapter instructions must be a non-empty string: "
                "{'path': 'adapters/codex/ADAPTER.md'}",
                errors,
            )
            self.assertIn(
                "optional component path must be a non-empty string: "
                "{'path': 'components/plans'}",
                errors,
            )

    def test_catalog_paths_must_stay_within_the_catalog(self) -> None:
        cases = {
            "absolute": ("/tmp/agent.md", "not a safe relative path"),
            "parent traversal": ("../agent.md", "not a safe relative path"),
            "resolved symlink escape": ("escaped-agent.md", "escapes catalog/"),
        }
        for label, (definition, expected_error) in cases.items():
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    catalog_root = root / "catalog"
                    shutil.copytree(ROOT / "catalog", catalog_root)
                    if label == "resolved symlink escape":
                        outside = root / "outside-agent.md"
                        outside.write_text("outside\n", encoding="utf-8")
                        try:
                            (catalog_root / definition).symlink_to(outside)
                        except OSError as error:
                            self.skipTest(f"symlinks unavailable: {error}")
                    catalog_path = catalog_root / "catalog.json"
                    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
                    catalog["agents"][0]["definition"] = definition
                    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

                    errors = CHECK_CATALOG.validate_catalog(catalog_root)

                    self.assertTrue(
                        any(expected_error in error for error in errors), errors
                    )

    def test_native_target_templates_enforce_safe_paths_and_placeholders(
        self,
    ) -> None:
        cases = {
            "agent_target": {
                "absolute": ("/native/<agent>.md", "not absolute"),
                "Windows drive path": ("C:native/<agent>.md", "not absolute"),
                "parent traversal": ("../native/<agent>.md", "parent traversal"),
                "missing placeholder": (
                    ".native/agents/worker.md",
                    "exactly one '<agent>'",
                ),
                "duplicate placeholder": (
                    ".native/<agent>/<agent>.md",
                    "exactly one '<agent>'",
                ),
                "wrong placeholder": (
                    ".native/agents/<skill>.md",
                    "unsupported placeholder",
                ),
                "backslash": (
                    r".native\agents\<agent>.md",
                    "backslash separators",
                ),
                "valid nested": (".native/nested/agents/<agent>.md", None),
            },
            "instruction_targets": {
                "absolute": ("/AGENTS.md", "not absolute"),
                "parent traversal": ("../AGENTS.md", "parent traversal"),
                "placeholder": ("docs/<agent>/AGENTS.md", "must not contain"),
                "backslash": (r"docs\AGENTS.md", "backslash separators"),
                "empty segment": ("docs//AGENTS.md", "empty path segment"),
                "valid nested": ("docs/agents/AGENTS.md", None),
            },
            "skill_targets": {
                "absolute": ("/skills/<skill>/SKILL.md", "not absolute"),
                "parent traversal": (
                    "../skills/<skill>/SKILL.md",
                    "parent traversal",
                ),
                "missing placeholder": (
                    ".native/skills/worker/SKILL.md",
                    "exactly one '<skill>'",
                ),
                "duplicate placeholder": (
                    ".native/<skill>/<skill>/SKILL.md",
                    "exactly one '<skill>'",
                ),
                "wrong placeholder": (
                    ".native/skills/<agent>/SKILL.md",
                    "unsupported placeholder",
                ),
                "backslash": (
                    r".native\skills\<skill>\SKILL.md",
                    "backslash separators",
                ),
                "valid nested": (".native/nested/<skill>/SKILL.md", None),
            },
        }

        for field, field_cases in cases.items():
            for label, (replacement, expected_category) in field_cases.items():
                with self.subTest(field=field, label=label):
                    with tempfile.TemporaryDirectory() as temporary:
                        catalog_root = Path(temporary) / "catalog"
                        shutil.copytree(ROOT / "catalog", catalog_root)
                        catalog_path = catalog_root / "catalog.json"
                        catalog = json.loads(
                            catalog_path.read_text(encoding="utf-8")
                        )
                        adapter = catalog["adapters"][0]
                        if field == "agent_target":
                            original = adapter[field]
                            adapter[field] = replacement
                        else:
                            original = adapter[field][0]
                            adapter[field][0] = replacement
                        catalog_path.write_text(
                            json.dumps(catalog), encoding="utf-8"
                        )
                        instructions_path = catalog_root / adapter["instructions"]
                        instructions = instructions_path.read_text(encoding="utf-8")
                        self.assertIn(original, instructions)
                        instructions_path.write_text(
                            instructions.replace(original, replacement, 1),
                            encoding="utf-8",
                        )

                        errors = CHECK_CATALOG.validate_catalog(catalog_root)
                        template_errors = [
                            error
                            for error in errors
                            if f"adapter {adapter['name']!r} {field}" in error
                        ]
                        if expected_category is None:
                            self.assertEqual([], template_errors, errors)
                        else:
                            self.assertTrue(
                                any(
                                    expected_category in error
                                    for error in template_errors
                                ),
                                errors,
                            )

    def test_frontmatter_accepts_the_managed_plain_format(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "agent.md"
            path.write_text(
                "---\n"
                "name: reviewer\n"
                "description: Reviews a bounded diff carefully.\n"
                "read_only: true\n"
                "---\nbody\n",
                encoding="utf-8",
            )

            metadata, body = CHECK_CATALOG._frontmatter(path, root)

            self.assertEqual(
                {
                    "name": "reviewer",
                    "description": "Reviews a bounded diff carefully.",
                    "read_only": "true",
                },
                metadata,
            )
            self.assertEqual("body", body)

    def test_frontmatter_rejects_non_plain_descriptions(self) -> None:
        invalid_descriptions = {
            "empty": "",
            "single quoted": "'reviewer'",
            "double quoted": '"reviewer"',
            "embedded apostrophe": "reviewer's bounded diff",
            "embedded quote": 'reviews the "bounded" diff',
            "colon": "Reviewer: bounded diff review",
            "hash": "reviewer # broader than parsed",
            "boolean": "true",
            "short boolean": "y",
            "null": "null",
            "decimal": "123",
            "float": "1.",
            "binary": "0b10",
            "date": "2026-08-12",
            "alias": "*missing",
            "tag": "!text reviewer",
            "collection": "[reviewer]",
            "mapping": "{role reviewer}",
            "block scalar": "|",
            "leading whitespace": " reviewer",
            "trailing whitespace": "reviewer ",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "agent.md"
            for label, description in invalid_descriptions.items():
                with self.subTest(label=label):
                    path.write_text(
                        "---\n"
                        "name: reviewer\n"
                        f"description: {description}\n"
                        "read_only: true\n"
                        "---\nbody\n",
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(
                        ValueError, r"agent\.md.*description field"
                    ):
                        CHECK_CATALOG._frontmatter(path, root)

    def test_frontmatter_rejects_out_of_contract_fields_and_styles(self) -> None:
        invalid_fields = {
            "quoted name": 'name: "reviewer"',
            "trailing hyphen name": "name: worker-",
            "empty name segment": "name: worker--review",
            "quoted read_only": 'read_only: "true"',
            "indented field": " description: reviewer",
            "unknown field": "summary: reviewer",
            "duplicate field": "name: reviewer",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "agent.md"
            for label, replacement in invalid_fields.items():
                with self.subTest(label=label):
                    fields = [
                        "name: reviewer",
                        "description: Reviews a bounded diff.",
                        "read_only: true",
                    ]
                    if label in {
                        "quoted name",
                        "trailing hyphen name",
                        "empty name segment",
                    }:
                        fields[0] = replacement
                    elif label == "quoted read_only":
                        fields[2] = replacement
                    else:
                        fields[1] = replacement
                    path.write_text(
                        "---\n" + "\n".join(fields) + "\n---\nbody\n",
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(ValueError, r"agent\.md"):
                        CHECK_CATALOG._frontmatter(path, root)

    def test_frontmatter_requires_exactly_three_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "agent.md"
            invalid_frontmatter = {
                "extra": (
                    "name: reviewer\n"
                    "description: Reviews a bounded diff.\n"
                    "read_only: true\n"
                    "extra: value",
                    r"unknown frontmatter field 'extra'",
                ),
                "missing": (
                    "name: reviewer\nread_only: true",
                    r"missing frontmatter field\(s\): description",
                ),
            }
            for label, (fields, expected_error) in invalid_frontmatter.items():
                with self.subTest(label=label):
                    path.write_text(
                        f"---\n{fields}\n---\nbody\n",
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(
                        ValueError, rf"agent\.md.*{expected_error}"
                    ):
                        CHECK_CATALOG._frontmatter(path, root)

    def test_validate_rejects_quoted_canonical_description(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            path = root / "catalog/agents/reviewer.md"
            definition = path.read_text(encoding="utf-8").replace(
                "description: Fresh read-only review of a substantive diff when "
                "isolated context improves correctness.",
                'description: "Reviews a diff: correctness first."',
            )
            path.write_text(definition, encoding="utf-8")

            errors = CHECK_CATALOG.validate_catalog(root / "catalog")

            self.assertTrue(
                any(
                    "catalog/agents/reviewer.md" in error
                    and "description field" in error
                    for error in errors
                ),
                errors,
            )

    def test_validate_reports_a_single_specific_error_for_an_empty_body(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            path = root / "catalog/agents/reviewer.md"
            metadata, _ = CHECK_CATALOG._frontmatter(path, root)
            path.write_text(
                "---\n"
                f"name: {metadata['name']}\n"
                f"description: {metadata['description']}\n"
                f"read_only: {metadata['read_only']}\n"
                "---\n",
                encoding="utf-8",
            )

            self.assertEqual(
                ["agent reviewer needs a body"],
                CHECK_CATALOG.validate_catalog(root / "catalog"),
            )

    def test_codex_representation_rejects_unsafe_canonical_body_content(
        self,
    ) -> None:
        cases = {
            "reserved delimiter": ('reserved """ delimiter', "reserved delimiter"),
            "invalid escape": (r"invalid \d escape", "backslash"),
            "transforming escape": (r"transforming \n escape", "backslash"),
            "control character": (
                "forbidden control \x0b character",
                "forbidden control character U+000B",
            ),
        }
        for label, (unsafe_content, expected_category) in cases.items():
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory() as temporary:
                    catalog_root = Path(temporary) / "catalog"
                    shutil.copytree(ROOT / "catalog", catalog_root)
                    path = catalog_root / "agents/reviewer.md"
                    path.write_text(
                        path.read_text(encoding="utf-8")
                        + f"\nunsafe marker: {unsafe_content} remains literal\n",
                        encoding="utf-8",
                    )

                    errors = CHECK_CATALOG.validate_catalog(catalog_root)

                    self.assertTrue(
                        any(
                            "agent reviewer body is incompatible with the fixed "
                            "Codex" in error
                            and expected_category in error
                            for error in errors
                        ),
                        errors,
                    )

    def test_catalog_names_reject_trailing_hyphens_and_empty_segments(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            catalog_path = root / "catalog/catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["agents"][0]["name"] = "worker-"
            catalog["adapters"][0]["name"] = "worker--review"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

            errors = CHECK_CATALOG.validate_catalog(root / "catalog")

            self.assertIn("invalid agent name: 'worker-'", errors)
            self.assertIn("invalid adapter name: 'worker--review'", errors)

    def test_uncataloged_agent_definition_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            (root / "catalog/agents/unknown.md").write_text(
                "uncataloged\n", encoding="utf-8"
            )

            errors = CHECK_CATALOG.validate_catalog(root / "catalog")

            self.assertIn(
                "uncataloged agent definitions: catalog/agents/unknown.md", errors
            )

    def test_uncataloged_adapter_instructions_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            path = root / "catalog/adapters/unknown/ADAPTER.md"
            path.parent.mkdir()
            path.write_text("uncataloged\n", encoding="utf-8")

            errors = CHECK_CATALOG.validate_catalog(root / "catalog")

            self.assertIn(
                "uncataloged adapter instructions: "
                "catalog/adapters/unknown/ADAPTER.md",
                errors,
            )

    def test_uncataloged_optional_component_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            (root / "catalog/components/unknown").mkdir()

            errors = CHECK_CATALOG.validate_catalog(root / "catalog")

            self.assertIn(
                "uncataloged optional components: catalog/components/unknown", errors
            )

    def test_adapter_must_document_each_write_capable_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "catalog", root / "catalog")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            path = root / "catalog/adapters/claude/ADAPTER.md"
            instructions = path.read_text(encoding="utf-8")
            path.write_text(
                instructions.replace("plan-implementer", "implementation-role", 1),
                encoding="utf-8",
            )

            errors = CHECK_CATALOG.validate_catalog(root / "catalog")

            self.assertIn(
                "adapter claude instructions do not document write-capable agent "
                "plan-implementer",
                errors,
            )

if __name__ == "__main__":
    unittest.main()
