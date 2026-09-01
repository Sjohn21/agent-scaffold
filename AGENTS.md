# Agent-scaffold guidance

## Invariants

- Preserve unrelated user changes and existing project instructions.
- Keep installation one-time and prompt-driven. Do not add an installer,
  renderer, target-side helper, managed state, ownership markers or updater.
- Install only explicitly selected adapters, agents and optional components.
- Keep canonical roles adapter-neutral; native paths, tools, instruction loading
  and permission caveats belong in adapter guidance.
- Read-only agents may use shell inspection but receive no native file-edit
  tools. A general shell is not command-level or filesystem-read-only isolation.
- Keep CI offline. Adapter compatibility is manually checked against the
  official sources recorded in
  `development/references/adapter-compatibility.md`.
- Keep `catalog/` the complete distribution boundary; development tooling and
  native dogfood must not become catalog dependencies.

## Delegation

- Delegate `plan-search` only for a named plan phase whose broad read-only
  inventory would materially crowd the main context. Supply the phase and
  expected evidence; keep small or tightly coupled searches local.
- Delegate `reviewer` for a substantive diff that benefits from fresh context.
  Supply an exact selector; let the reviewer retrieve the diff.

## Gotchas

- `docs/plans/` is ignored local working state. Durable behavior belongs in the
  catalog, tests, README or this file.
- Do not add or delete ignored `__pycache__` artifacts as product work.

## Verification

Before completing product work, run:

```text
python3 development/scripts/check_catalog.py
python3 -m unittest discover -s development/tests -v
git diff --check
```
