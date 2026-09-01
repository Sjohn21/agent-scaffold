#!/usr/bin/env python3
"""Validate the prompt-driven agent catalog without third-party dependencies."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
NAME = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
PLAIN_FORBIDDEN_START = frozenset("-?,[]{}&*!|>%@`")
YAML_IMPLICIT_NON_STRING = re.compile(
    r"^(?:~|null|true|false|yes|no|y|n|on|off|"
    r"[-+]?(?:0b[01_]+|0o[0-7_]+|0x[\da-f_]+|"
    r"\d[\d_]*(?:\.(?:\d[\d_]*)?)?(?:e[-+]?\d+)?|"
    r"\.\d[\d_]*|\.inf|\.nan)|"
    r"\d{4}-\d{1,2}-\d{1,2})$",
    re.IGNORECASE,
)
FRONTMATTER_KEY = re.compile(r"^[a-z][a-z0-9_]*$")
FRONTMATTER_FIELDS = frozenset({"name", "description", "read_only"})
DOGFOOD_AGENTS = {
    Path(".claude/agents/plan-search.md"): ("claude", "plan-search"),
    Path(".claude/agents/reviewer.md"): ("claude", "reviewer"),
    Path(".codex/agents/plan-search.toml"): ("codex", "plan-search"),
    Path(".codex/agents/reviewer.toml"): ("codex", "reviewer"),
}
REPOSITORY_ONLY_CONTRACT_REFERENCES = (
    "../",
    "development/",
)
STANDALONE_CONTRACTS = ("INSTALL.md", "SKILLS.md")
CODEX_BODY_DELIMITER = '"""'
CODEX_BODY_OPENING = f"developer_instructions = {CODEX_BODY_DELIMITER}\n"
CODEX_BODY_CLOSING = CODEX_BODY_DELIMITER
CATALOG_PLACEHOLDER = re.compile(r"<[^<>]+>")
WINDOWS_DRIVE_PATH = re.compile(r"^[A-Za-z]:")
REPOSITORY_VALIDATION_SKIPPED = (
    "repository validation skipped: catalog/catalog.json could not be loaded "
    "as an object"
)


def _valid_plain_description(value: str) -> bool:
    return bool(value) and not (
        value != value.strip()
        or value[0] in PLAIN_FORBIDDEN_START
        or any(character in value for character in "'\":#")
        or YAML_IMPLICIT_NON_STRING.fullmatch(value)
    )


def _accepted_name(value: object, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not NAME.fullmatch(value):
        errors.append(f"invalid {label} name: {value!r}")
        return None
    return value


def _accepted_path(value: object, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty string: {value!r}")
        return None
    return value


def _safe_path(relative: str, catalog_root: Path) -> Path:
    path = Path(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"catalog path is not a safe relative path: {relative!r}")
    resolved = (catalog_root / path).resolve()
    try:
        resolved.relative_to(catalog_root.resolve())
    except ValueError as error:
        raise ValueError(f"catalog path escapes catalog/: {relative!r}") from error
    return resolved


def _valid_target_template(
    value: object,
    label: str,
    required_placeholder: str | None,
    errors: list[str],
) -> bool:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty string: {value!r}")
        return False

    valid = True
    if "\\" in value:
        errors.append(f"{label} uses ambiguous backslash separators: {value!r}")
        valid = False
    if value.startswith("/") or WINDOWS_DRIVE_PATH.match(value):
        errors.append(f"{label} must be repository-relative, not absolute: {value!r}")
        valid = False

    segments = value.split("/")
    if "" in segments:
        errors.append(f"{label} contains an empty path segment: {value!r}")
        valid = False
    if "." in segments:
        errors.append(f"{label} contains a current-directory segment: {value!r}")
        valid = False
    if ".." in segments:
        errors.append(f"{label} contains parent traversal: {value!r}")
        valid = False

    placeholders = CATALOG_PLACEHOLDER.findall(value)
    without_placeholders = CATALOG_PLACEHOLDER.sub("", value)
    if "<" in without_placeholders or ">" in without_placeholders:
        errors.append(f"{label} contains a malformed placeholder: {value!r}")
        valid = False
    if required_placeholder is None:
        if placeholders:
            errors.append(f"{label} must not contain placeholders: {value!r}")
            valid = False
    else:
        if placeholders.count(required_placeholder) != 1:
            errors.append(
                f"{label} must contain exactly one {required_placeholder!r} "
                f"placeholder: {value!r}"
            )
            valid = False
        unexpected = sorted(set(placeholders).difference({required_placeholder}))
        if unexpected:
            errors.append(
                f"{label} contains unsupported placeholder(s): "
                + ", ".join(unexpected)
            )
            valid = False
    return valid


def _frontmatter(
    path: Path, root: Path
) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path.relative_to(root)} must start with frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(f"{path.relative_to(root)} has unclosed frontmatter") from error
    relative = path.relative_to(root)
    field_lines = lines[1:end]
    metadata: dict[str, str] = {}
    for offset, line in enumerate(field_lines, start=2):
        if line[:1].isspace() or ": " not in line:
            raise ValueError(
                f"{relative} has invalid frontmatter field on line {offset}"
            )
        key, value = line.split(": ", 1)
        if not FRONTMATTER_KEY.fullmatch(key):
            raise ValueError(
                f"{relative} has invalid frontmatter field on line {offset}"
            )
        if key not in FRONTMATTER_FIELDS:
            raise ValueError(f"{relative} has unknown frontmatter field {key!r}")
        if key in metadata:
            raise ValueError(f"{relative} has duplicate frontmatter field {key!r}")
        metadata[key] = value

    missing = FRONTMATTER_FIELDS.difference(metadata)
    if missing:
        fields = ", ".join(sorted(missing))
        raise ValueError(f"{relative} is missing frontmatter field(s): {fields}")

    name = metadata["name"]
    if not NAME.fullmatch(name):
        raise ValueError(f"{relative} has invalid name field: {name!r}")

    description = metadata["description"]
    if not _valid_plain_description(description):
        raise ValueError(
            f"{relative} has invalid plain description field: {description!r}"
        )

    read_only = metadata["read_only"]
    if read_only not in {"true", "false"}:
        raise ValueError(
            f"{relative} read_only field must be plain true or false"
        )
    return metadata, "\n".join(lines[end + 1 :]).strip()


def _claude_agent_body(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ValueError("must start with a YAML frontmatter block")
    try:
        end = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.rstrip("\r\n") == "---"
        )
    except StopIteration as error:
        raise ValueError("has an unclosed YAML frontmatter block") from error
    return "".join(lines[end + 1 :]).strip()


def _canonical_body_source(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    delimiters = [
        index for index, line in enumerate(lines) if line.rstrip("\r\n") == "---"
    ]
    if len(delimiters) < 2 or delimiters[0] != 0:
        return ""
    return "".join(lines[delimiters[1] + 1 :])


def _codex_body_constraint_errors(agent_name: object, body: str) -> list[str]:
    prefix = (
        f"agent {agent_name} body is incompatible with the fixed Codex "
        f"{CODEX_BODY_DELIMITER} developer_instructions representation"
    )
    errors: list[str] = []
    if CODEX_BODY_DELIMITER in body:
        errors.append(f"{prefix}: contains the reserved delimiter")
    if "\\" in body:
        errors.append(f"{prefix}: contains a backslash that TOML would escape")
    controls = sorted(
        {
            ord(character)
            for character in body
            if ord(character) <= 0x08
            or 0x0B <= ord(character) <= 0x1F
            or ord(character) == 0x7F
        }
    )
    if controls:
        rendered = ", ".join(f"U+{codepoint:04X}" for codepoint in controls)
        errors.append(f"{prefix}: contains forbidden control character {rendered}")
    return errors


def _codex_agent_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if (
        text.count(CODEX_BODY_OPENING) != 1
        or text.count(CODEX_BODY_DELIMITER) != 2
    ):
        raise ValueError(
            "must contain exactly one bounded developer_instructions field"
        )
    body, suffix = text.split(CODEX_BODY_OPENING, 1)[1].split(
        CODEX_BODY_CLOSING, 1
    )
    if suffix and not suffix.startswith("\n"):
        raise ValueError(
            "must contain exactly one bounded developer_instructions field"
        )
    return body


def validate_catalog(catalog_root: Path) -> list[str]:
    catalog_root = catalog_root.resolve()
    display_root = catalog_root.parent
    errors: list[str] = []
    try:
        catalog_path = catalog_root / "catalog.json"
        license_path = catalog_root / "LICENSE"
        if not catalog_path.is_file():
            return ["missing catalog/catalog.json"]
        for contract_name in STANDALONE_CONTRACTS:
            contract_path = catalog_root / contract_name
            if not contract_path.is_file():
                errors.append(f"missing catalog/{contract_name}")
                continue
            try:
                contract = contract_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                errors.append(f"invalid catalog/{contract_name}: {error}")
                continue
            for reference in REPOSITORY_ONLY_CONTRACT_REFERENCES:
                if reference in contract:
                    errors.append(
                        f"catalog/{contract_name} references repository-only "
                        f"path: {reference}"
                    )
        if not license_path.is_file():
            errors.append("missing catalog/LICENSE")
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            return [f"invalid catalog/catalog.json: {error}"]

        if not isinstance(catalog, dict):
            return ["catalog/catalog.json must contain an object"]

        if catalog.get("schema_version") != 1:
            errors.append("catalog schema_version must be 1")

        agents = catalog.get("agents")
        adapters = catalog.get("adapters")
        if not isinstance(agents, list) or not agents:
            errors.append("catalog agents must be a non-empty list")
            agents = []
        if not isinstance(adapters, list) or not adapters:
            errors.append("catalog adapters must be a non-empty list")
            adapters = []

        agent_names: list[str] = []
        write_capable_names: set[str] = set()
        cataloged_agent_paths: set[str] = set()
        for item in agents:
            if not isinstance(item, dict) or set(item) != {"name", "definition"}:
                errors.append(f"invalid agent catalog entry: {item!r}")
                continue
            name, relative = item["name"], item["definition"]
            accepted_name = _accepted_name(name, "agent", errors)
            if accepted_name is not None:
                agent_names.append(accepted_name)
            accepted_relative = _accepted_path(
                relative, "agent definition", errors
            )
            if accepted_relative is None:
                continue
            try:
                path = _safe_path(accepted_relative, catalog_root)
                cataloged_agent_paths.add(accepted_relative)
                if not path.is_file():
                    errors.append(
                        f"missing agent definition: catalog/{accepted_relative}"
                    )
                    continue
                metadata, body = _frontmatter(path, display_root)
                if metadata["name"] != name:
                    errors.append(f"agent {name} frontmatter name does not match")
                if metadata["read_only"] == "false" and accepted_name is not None:
                    write_capable_names.add(accepted_name)
                if not body:
                    errors.append(f"agent {name} needs a body")
                else:
                    if "AGENTS.md" not in body:
                        errors.append(f"agent {name} must refer to AGENTS.md")
                    errors.extend(
                        _codex_body_constraint_errors(
                            name, _canonical_body_source(path)
                        )
                    )
            except (OSError, TypeError, ValueError) as error:
                errors.append(str(error))

        adapter_names: list[str] = []
        cataloged_adapter_paths: set[str] = set()
        targets: list[str] = []
        for item in adapters:
            required = {
                "name",
                "instructions",
                "agent_target",
                "instruction_targets",
                "skill_targets",
            }
            if not isinstance(item, dict) or set(item) != required:
                errors.append(f"invalid adapter catalog entry: {item!r}")
                continue
            name = item["name"]
            target = item["agent_target"]
            accepted_name = _accepted_name(name, "adapter", errors)
            if accepted_name is not None:
                adapter_names.append(accepted_name)
            documented_targets: list[str] = []
            ordered_skill_targets: list[str] = []
            if isinstance(target, str) and target:
                targets.append(target)
                documented_targets.append(target)
            _valid_target_template(
                target,
                f"adapter {name!r} agent_target",
                "<agent>",
                errors,
            )
            for field in ("instruction_targets", "skill_targets"):
                values = item[field]
                if not isinstance(values, list) or not values or not all(
                    isinstance(value, str) and value for value in values
                ):
                    errors.append(
                        f"adapter {name!r} {field} must be a non-empty list "
                        "of non-empty strings"
                    )
                    continue
                if len(values) != len(set(values)):
                    errors.append(f"adapter {name} has duplicate {field}")
                documented_targets.extend(values)
                if field == "skill_targets":
                    ordered_skill_targets = values
                required_placeholder = (
                    None if field == "instruction_targets" else "<skill>"
                )
                for value in values:
                    _valid_target_template(
                        value,
                        f"adapter {name!r} {field} entry",
                        required_placeholder,
                        errors,
                    )
            accepted_instructions = _accepted_path(
                item["instructions"], "adapter instructions", errors
            )
            if accepted_instructions is None:
                continue
            try:
                path = _safe_path(accepted_instructions, catalog_root)
                cataloged_adapter_paths.add(accepted_instructions)
                if not path.is_file():
                    errors.append(
                        "missing adapter instructions: "
                        f"catalog/{accepted_instructions}"
                    )
                    continue
                instructions = path.read_text(encoding="utf-8")
                for documented_target in documented_targets:
                    if documented_target not in instructions:
                        errors.append(
                            f"adapter {name} instructions do not name target "
                            f"{documented_target}"
                        )
                first_occurrences = [
                    instructions.find(value) for value in ordered_skill_targets
                ]
                if -1 not in first_occurrences and first_occurrences != sorted(
                    first_occurrences
                ):
                    errors.append(
                        f"adapter {name} instructions document skill targets "
                        "out of manifest order"
                    )
                if accepted_name is not None:
                    for agent_name in sorted(write_capable_names):
                        if agent_name not in instructions:
                            errors.append(
                                f"adapter {accepted_name} instructions do not "
                                "document write-capable agent "
                                f"{agent_name}"
                            )
            except (OSError, TypeError, ValueError) as error:
                errors.append(str(error))

        for label, values in (("agent", agent_names), ("adapter", adapter_names)):
            duplicates = sorted({value for value in values if values.count(value) > 1})
            if duplicates:
                errors.append(f"duplicate {label} names: {', '.join(duplicates)}")
        if len(targets) != len(set(targets)):
            errors.append("adapter agent targets must be unique")

        components = catalog.get("optional_components", [])
        component_names: list[str] = []
        cataloged_component_paths: set[str] = set()
        if not isinstance(components, list):
            errors.append("catalog optional_components must be a list")
            components = []
        for item in components:
            if not isinstance(item, dict) or set(item) != {"name", "path"}:
                errors.append(f"invalid optional component entry: {item!r}")
                continue
            name, relative = item["name"], item["path"]
            accepted_name = _accepted_name(name, "optional component", errors)
            if accepted_name is not None:
                component_names.append(accepted_name)
            accepted_relative = _accepted_path(
                relative, "optional component path", errors
            )
            if accepted_relative is None:
                continue
            try:
                path = _safe_path(accepted_relative, catalog_root)
                cataloged_component_paths.add(accepted_relative)
                if not path.is_dir():
                    errors.append(
                        f"missing optional component: catalog/{accepted_relative}"
                    )
            except (OSError, TypeError, ValueError) as error:
                errors.append(str(error))
        duplicate_components = sorted(
            {name for name in component_names if component_names.count(name) > 1}
        )
        if duplicate_components:
            errors.append(
                f"duplicate optional component names: {', '.join(duplicate_components)}"
            )

        actual_agent_paths = {
            path.relative_to(catalog_root).as_posix()
            for path in (catalog_root / "agents").glob("*.md")
            if path.is_file()
        }
        actual_adapter_paths = {
            path.relative_to(catalog_root).as_posix()
            for path in (catalog_root / "adapters").glob("*/ADAPTER.md")
            if path.is_file()
        }
        actual_component_paths = {
            path.relative_to(catalog_root).as_posix()
            for path in (catalog_root / "components").glob("*")
            if path.is_dir()
        }
        filesystem_coverage = (
            (
                "agent definitions",
                actual_agent_paths,
                cataloged_agent_paths,
            ),
            (
                "adapter instructions",
                actual_adapter_paths,
                cataloged_adapter_paths,
            ),
            (
                "optional components",
                actual_component_paths,
                cataloged_component_paths,
            ),
        )
        for label, actual_paths, cataloged_paths in filesystem_coverage:
            uncataloged_paths = sorted(actual_paths - cataloged_paths)
            if uncataloged_paths:
                errors.append(
                    f"uncataloged {label}: "
                    + ", ".join(f"catalog/{path}" for path in uncataloged_paths)
                )
        return errors
    except (OSError, UnicodeDecodeError) as error:
        errors.append(str(error))
        return errors


def validate_repository(repo_root: Path) -> list[str]:
    repo_root = repo_root.resolve()
    catalog_root = repo_root / "catalog"
    catalog_path = catalog_root / "catalog.json"
    errors: list[str] = []

    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return [REPOSITORY_VALIDATION_SKIPPED]
    if not isinstance(catalog, dict):
        return [REPOSITORY_VALIDATION_SKIPPED]

    license_path = repo_root / "LICENSE"
    catalog_license_path = catalog_root / "LICENSE"
    if not license_path.is_file():
        errors.append("missing LICENSE")
    elif catalog_license_path.is_file():
        try:
            if license_path.read_bytes() != catalog_license_path.read_bytes():
                errors.append("LICENSE does not match catalog/LICENSE")
        except OSError as error:
            errors.append(str(error))

    readme_path = repo_root / "README.md"
    try:
        readme = (
            readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
        )
    except (OSError, UnicodeDecodeError) as error:
        errors.append(str(error))
        readme = ""

    readme_coverage = (
        (
            "agent",
            catalog.get("agents", []),
            "definition",
            r"\]\(catalog/(agents/[^)]+\.md)\)",
        ),
        (
            "adapter",
            catalog.get("adapters", []),
            "instructions",
            r"\]\(catalog/(adapters/[^)]+/ADAPTER\.md)\)",
        ),
    )
    for label, items, path_field, link_pattern in readme_coverage:
        if not isinstance(items, list):
            continue
        documented_paths = set(re.findall(link_pattern, readme))
        expected_paths: set[str] = set()
        for item in items:
            if not isinstance(item, dict):
                continue
            name, relative = item.get("name"), item.get(path_field)
            if not isinstance(name, str) or not isinstance(relative, str):
                continue
            expected_paths.add(relative)
            if f"](catalog/{relative})" not in readme:
                errors.append(f"README does not document {label} {name}")
        unknown_paths = sorted(documented_paths - expected_paths)
        if unknown_paths:
            errors.append(
                f"README documents uncataloged {label}s: "
                + ", ".join(unknown_paths)
            )

    if "](catalog/SKILLS.md)" not in readme:
        errors.append("README does not document the skills authoring contract")

    components = catalog.get("optional_components", [])
    if isinstance(components, list):
        for item in components:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if (
                isinstance(name, str)
                and NAME.fullmatch(name)
                and f"`{name}`" not in readme
            ):
                errors.append(f"README does not document optional component {name}")

    extractors = {"claude": _claude_agent_body, "codex": _codex_agent_body}
    for native_relative, (adapter, agent_name) in DOGFOOD_AGENTS.items():
        canonical_path = catalog_root / f"agents/{agent_name}.md"
        if not canonical_path.is_file():
            continue
        native_path = repo_root / native_relative
        if not native_path.is_file():
            errors.append(f"missing dogfood agent: {native_relative.as_posix()}")
            continue
        try:
            _, canonical_body = _frontmatter(canonical_path, repo_root)
        except (OSError, ValueError):
            continue
        try:
            native_body = extractors[adapter](native_path)
        except (OSError, ValueError) as error:
            errors.append(f"{native_relative.as_posix()} {error}")
            continue
        if native_body != canonical_body:
            errors.append(
                f"{native_relative.as_posix()} body drifted from canonical agent "
                f"{agent_name}"
            )

    return errors


def main() -> int:
    errors = validate_catalog(ROOT / "catalog")
    errors.extend(validate_repository(ROOT))
    if errors:
        print("catalog/repository: invalid")
        for error in errors:
            print(f"- {error}")
        return 1
    print("catalog/repository: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
