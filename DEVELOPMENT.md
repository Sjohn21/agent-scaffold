# Development

This document is for maintainers of agent-scaffold. The user-facing
[README.md](README.md) explains how to select and install catalog content; it
does not describe repository internals.

## Repository boundaries

The repository separates distributable content, active dogfood, development
tooling, and technically required native entrypoints:

| Boundary | Location | Responsibility |
| --- | --- | --- |
| Catalog | `catalog/` | Complete, independently copyable distribution |
| Dogfood | `.codex/agents/`, `.claude/agents/` | Small native selection used by this repository |
| Development | `development/` | Offline validator, tests, fixtures, manual smoke guidance, and compatibility evidence |
| Native integration | Root instructions and `.github/workflows/` | Client- and platform-discovered entrypoints |

Only `catalog/` is installed or copied into target repositories. Files in the
other boundaries exist solely to develop, verify, or dogfood this project.

### Catalog

`catalog/INSTALL.md` is the prompt-driven installation contract and
`catalog/catalog.json` is its manifest. Canonical agents under
`catalog/agents/` remain adapter-neutral. Client-specific paths, tools,
instruction loading, permissions, and format translation belong under
`catalog/adapters/`.

The catalog must remain self-contained. It may not depend on `development/`,
root dogfood, repository instructions, or CI. Installation remains one-time and
selection-driven: do not add an installer, renderer, target-side helper,
managed state, ownership markers, updater, or compatibility copy of an old
source path.

### Dogfood

The followed files under `.codex/agents/` and `.claude/agents/` are native
installed outputs that make selected catalog agents available in this
repository. They remain at the root because those are the clients' discovery
paths; they are not a second canonical implementation.

Dogfood selection is intentionally explicit in the repository integration
validator. Do not replace it with a glob: locally installed agents must not
silently become followed project dogfood. Native metadata stays
adapter-specific, while each dogfood body must match its canonical agent body.

### Development tooling

`development/scripts/check_catalog.py` contains the offline validation
entrypoint:

- `validate_catalog(catalog_root)` checks the standalone distribution contract;
- `validate_repository(repo_root)` checks README coverage and explicit dogfood
  parity;
- direct CLI execution runs both and reports all errors together.

`development/references/adapter-compatibility.md` is the manual register of
official sources, checked dates, and supported adapter behavior surfaces.

Tests are split by the same boundary:

- `development/tests/test_catalog_contract.py` tests catalog content and an
  isolated copy containing no repository files;
- `development/tests/test_repository_integration.py` tests README, dogfood, and
  development-runbook integration;
- `development/tests/fixtures/` contains test-only target repositories;
- `development/tests/smoke/README.md` is the manual installation runbook.

Keep automated validation offline and free of third-party dependencies.
Automated tests exercise validator behavior and the fixture structure required
by the smoke runbook; they do not pin general wording in installation,
adapter, agent, plan, or repository documentation. Review prose changes
normally. When prose changes installation or runtime behavior, run and record
the applicable manual smoke scenarios so the rendered native configuration and
delegated behavior are checked rather than inferred from phrases.
Adapter compatibility is checked manually against the official sources in the
[compatibility register](development/references/adapter-compatibility.md) and
with the [installation smoke runbook](development/tests/smoke/README.md). The
register is maintainer evidence, not a catalog dependency; CI performs no
online compatibility checks.

### Native entrypoints

Some repository files cannot live under a neat development directory:

- `AGENTS.md` and `CLAUDE.md` configure supported clients at their native root
  paths;
- `.github/workflows/ci.yml` must remain under `.github/workflows/` for GitHub
  discovery, but contains only thin calls into `development/`;
- `.codex/agents/` and `.claude/agents/` must remain at their native dogfood
  paths.

## Verification

Run the complete offline verification from the repository root before
completing product work:

```text
python3 development/scripts/check_catalog.py
python3 -m unittest discover -s development/tests -v
git diff --check
```

The validator also works when invoked from another current working directory;
it resolves the repository root from its own file location.

Use the manual smoke matrix when changing the installation contract, canonical
agents, adapter translation, catalog selection, or native tool permissions.
The runbook defines the minimum applicable scenarios and their required
evidence.

## Working in this repository

- Preserve unrelated changes and keep catalog modifications scoped to the
  explicitly requested adapters, agents, and components.
- Update catalog contract tests for distributable behavior and repository
  integration tests for README, dogfood, fixtures, or maintainer tooling.
- Keep root-native files thin. Put reusable verification logic under
  `development/`.
- Keep `docs/plans/` as ignored local working state. Durable behavior belongs
  in the catalog, tests, README, DEVELOPMENT.md, or project instructions.
- Do not add or remove ignored `__pycache__` artifacts as product work.

Sibling installation prompts use `<checkout>/catalog/INSTALL.md`. There is no
compatibility path for the former source directory.
