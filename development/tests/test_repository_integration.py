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
                    path.write_text(
                        path.read_text(encoding="utf-8").replace(
                            "Follow applicable project guidance",
                            "Follow drifted project guidance",
                            1,
                        ),
                        encoding="utf-8",
                    )

                    self.assertIn(
                        f"{native_path.as_posix()} body drifted from canonical "
                        f"agent {agent_name}",
                        CHECK_CATALOG.validate_repository(repo_root),
                    )

    def test_smoke_fixture_structure_is_preserved(self) -> None:
        fixture = ROOT / "development/tests/fixtures/install-smoke"
        guidance = (fixture / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("existing-guidance-must-survive", guidance)
        self.assertTrue((fixture / "README.md").is_file())
        self.assertTrue((fixture / "pyproject.toml").is_file())


if __name__ == "__main__":
    unittest.main()
