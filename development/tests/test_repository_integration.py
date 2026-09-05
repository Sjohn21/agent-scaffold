from __future__ import annotations

import importlib.util
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


def _copy_repository_inputs(destination: Path) -> None:
    shutil.copytree(ROOT / "catalog", destination / "catalog")
    shutil.copy2(ROOT / "LICENSE", destination / "LICENSE")
    shutil.copy2(ROOT / "README.md", destination / "README.md")
    for native_path in CHECK_CATALOG.DOGFOOD_AGENTS:
        target = destination / native_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / native_path, target)


class RepositoryIntegrationTests(unittest.TestCase):
    def test_repository_integration_is_valid(self) -> None:
        self.assertEqual([], CHECK_CATALOG.validate_repository(ROOT))

    def test_repository_validation_reports_unloadable_manifest_as_skipped(
        self,
    ) -> None:
        cases = {
            "missing": None,
            "malformed JSON": b"{not JSON}\n",
            "malformed UTF-8": b"\xff\n",
            "non-object": b"[]\n",
        }
        for label, content in cases.items():
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory() as temporary:
                    repo_root = Path(temporary)
                    _copy_repository_inputs(repo_root)
                    catalog_path = repo_root / "catalog/catalog.json"
                    if content is None:
                        catalog_path.unlink()
                    else:
                        catalog_path.write_bytes(content)

                    self.assertEqual(
                        [CHECK_CATALOG.REPOSITORY_VALIDATION_SKIPPED],
                        CHECK_CATALOG.validate_repository(repo_root),
                    )

    def test_invalid_utf8_readme_reports_error_and_continues(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            _copy_repository_inputs(repo_root)
            (repo_root / "README.md").write_bytes(b"\xff\n")

            errors = CHECK_CATALOG.validate_repository(repo_root)

            self.assertTrue(
                any("utf-8" in error.lower() for error in errors), errors
            )
            self.assertNotIn(
                CHECK_CATALOG.REPOSITORY_VALIDATION_SKIPPED, errors
            )
            self.assertIn("README does not document agent reviewer", errors)

    def test_repository_license_must_match_catalog_license(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            _copy_repository_inputs(repo_root)
            catalog_license = repo_root / "catalog/LICENSE"
            catalog_license.write_text(
                catalog_license.read_text(encoding="utf-8") + "drift\n",
                encoding="utf-8",
            )

            self.assertIn(
                "LICENSE does not match catalog/LICENSE",
                CHECK_CATALOG.validate_repository(repo_root),
            )

    def test_readme_cannot_document_uncataloged_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            _copy_repository_inputs(repo_root)
            readme_path = repo_root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8")
                + "\n[unknown](catalog/agents/unknown.md)\n",
                encoding="utf-8",
            )

            errors = CHECK_CATALOG.validate_repository(repo_root)

            self.assertIn(
                "README documents uncataloged agents: agents/unknown.md", errors
            )
            self.assertEqual(
                [], CHECK_CATALOG.validate_catalog(repo_root / "catalog")
            )

    def test_missing_readme_link_only_fails_repository_integration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            _copy_repository_inputs(repo_root)
            readme_path = repo_root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "[reviewer](catalog/agents/reviewer.md)", "reviewer"
                ),
                encoding="utf-8",
            )

            self.assertIn(
                "README does not document agent reviewer",
                CHECK_CATALOG.validate_repository(repo_root),
            )
            self.assertEqual(
                [], CHECK_CATALOG.validate_catalog(repo_root / "catalog")
            )

    def test_readme_must_link_the_skills_authoring_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            _copy_repository_inputs(repo_root)
            readme_path = repo_root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "](catalog/SKILLS.md)", "]"
                ),
                encoding="utf-8",
            )

            self.assertIn(
                "README does not document the skills authoring contract",
                CHECK_CATALOG.validate_repository(repo_root),
            )
            self.assertEqual(
                [], CHECK_CATALOG.validate_catalog(repo_root / "catalog")
            )

    def test_missing_canonical_agent_only_fails_catalog_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            _copy_repository_inputs(repo_root)
            (repo_root / "catalog/agents/reviewer.md").unlink()

            self.assertIn(
                "missing agent definition: catalog/agents/reviewer.md",
                CHECK_CATALOG.validate_catalog(repo_root / "catalog"),
            )
            self.assertEqual([], CHECK_CATALOG.validate_repository(repo_root))

    def test_each_tracked_dogfood_body_is_checked_explicitly(self) -> None:
        expected_mapping = {
            Path(".claude/agents/plan-search.md"): ("claude", "plan-search"),
            Path(".claude/agents/reviewer.md"): ("claude", "reviewer"),
            Path(".codex/agents/plan-search.toml"): ("codex", "plan-search"),
            Path(".codex/agents/reviewer.toml"): ("codex", "reviewer"),
        }
        self.assertEqual(expected_mapping, CHECK_CATALOG.DOGFOOD_AGENTS)

        for native_path, (_, agent_name) in expected_mapping.items():
            with self.subTest(native_path=native_path.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    repo_root = Path(temporary)
                    _copy_repository_inputs(repo_root)
                    path = repo_root / native_path
                    original = path.read_text(encoding="utf-8")
                    drifted = original.replace(
                        "Follow applicable project guidance already supplied",
                        "Follow drifted project guidance already supplied",
                        1,
                    )
                    self.assertNotEqual(original, drifted)
                    path.write_text(drifted, encoding="utf-8")

                    self.assertIn(
                        f"{native_path.as_posix()} body drifted from canonical "
                        f"agent {agent_name}",
                        CHECK_CATALOG.validate_repository(repo_root),
                    )

    def test_codex_read_only_dogfood_requires_read_only_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            _copy_repository_inputs(repo_root)
            relative = Path(".codex/agents/reviewer.toml")
            path = repo_root / relative
            source = path.read_text(encoding="utf-8")
            path.write_text(
                source.replace(
                    'sandbox_mode = "read-only"',
                    'sandbox_mode = "workspace-write"',
                    1,
                ),
                encoding="utf-8",
            )

            self.assertIn(
                f'{relative.as_posix()} must keep read-only sandbox_mode = '
                '"read-only"',
                CHECK_CATALOG.validate_repository(repo_root),
            )

    def test_claude_read_only_dogfood_rejects_edit_tools(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            _copy_repository_inputs(repo_root)
            relative = Path(".claude/agents/reviewer.md")
            path = repo_root / relative
            source = path.read_text(encoding="utf-8")
            path.write_text(
                source.replace(
                    "tools: Read, Grep, Glob, Bash",
                    "tools: Read, Grep, Glob, Bash, Edit",
                    1,
                ),
                encoding="utf-8",
            )

            self.assertIn(
                f"{relative.as_posix()} must keep read-only tools: "
                "Read, Grep, Glob, Bash",
                CHECK_CATALOG.validate_repository(repo_root),
            )

    def test_claude_body_allows_markdown_frontmatter_delimiter_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            _copy_repository_inputs(repo_root)
            canonical_path = repo_root / "catalog/agents/reviewer.md"
            native_path = repo_root / ".claude/agents/reviewer.md"
            codex_path = repo_root / ".codex/agents/reviewer.toml"
            marker = "---\nA body delimiter remains Markdown content.\n"
            canonical_path.write_text(
                canonical_path.read_text(encoding="utf-8") + marker,
                encoding="utf-8",
            )
            native_path.write_text(
                native_path.read_text(encoding="utf-8") + marker,
                encoding="utf-8",
            )
            codex_source = codex_path.read_text(encoding="utf-8")
            codex_prefix, delimiter, codex_suffix = codex_source.rpartition('"""')
            self.assertEqual('"""', delimiter)
            codex_path.write_text(
                codex_prefix + "\n" + marker.rstrip("\n") + delimiter + codex_suffix,
                encoding="utf-8",
            )

            self.assertEqual([], CHECK_CATALOG.validate_repository(repo_root))

    def test_claude_body_rejects_unclosed_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "reviewer.md"
            path.write_text("---\nname: reviewer\nbody\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "unclosed YAML frontmatter"):
                CHECK_CATALOG._claude_agent_body(path)

    def test_smoke_fixture_structure_is_preserved(self) -> None:
        fixture = ROOT / "development/tests/fixtures/install-smoke"
        guidance = (fixture / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("existing-guidance-must-survive", guidance)
        self.assertTrue((fixture / "README.md").is_file())
        self.assertTrue((fixture / "pyproject.toml").is_file())


if __name__ == "__main__":
    unittest.main()
