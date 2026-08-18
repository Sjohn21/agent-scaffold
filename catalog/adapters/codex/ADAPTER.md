# Codex adapter

Install each selected agent at `.codex/agents/<agent>.toml`. A standalone
project-scoped agent is TOML with these required keys:

```toml
name = "<agent>"
description = "<canonical description>"
developer_instructions = """
<canonical body unchanged>"""
```

For a canonical `read_only: true` agent, add:

```toml
sandbox_mode = "read-only"
```

Codex custom-agent files are configuration layers. When `sandbox_mode` is
omitted, the agent inherits the parent sandbox. Live runtime permission choices
are reapplied and can override a custom-agent default; always preserve stricter
parent and project permissions.

For a canonical `read_only: false` role whose intended work needs workspace
writes, use the smallest supported write-capable default:

```toml
sandbox_mode = "workspace-write"
```

`plan-implementer` needs that boundary for implementation. The command-only
`test-runner` and `plan-committer` may also need it for normal test output or Git
state, but their canonical no-product-edit boundary remains behavioural. Codex
custom-agent TOML has no per-agent `Edit`/`Write` tool allowlist, and general
shell access does not isolate individual shell commands. `workspace-write`
limits writes to allowed workspace roots; it does not prevent unrelated edits
inside those roots. Keep an inherited stricter sandbox whenever it still
supports the delegated operation.

Translate the model choice already resolved by the installation contract. For
explicit inheritance, omit `model`; for an exact model, add
`model = "<resolved model>"` only to that adapter-agent pair. Add
`model_reasoning_effort` only when separately requested. Escape values as valid
TOML. Use exactly the triple double-quoted multiline basic string shown above
for `developer_instructions`, with the canonical body unchanged. Canonical
bodies may not contain the reserved `"""` delimiter, a backslash, or control
characters forbidden by TOML other than newline and tab. Do not substitute
another multiline delimiter. Keep the closing delimiter directly after the
final body character; placing it on its own line would add that preceding
newline to the parsed instructions.

No `.codex/config.toml` is required: current Codex releases enable subagents by
default. If the target already has that file, preserve it. Change `[agents]`
settings such as concurrency only when explicitly requested.

Shared project instructions stay in root `AGENTS.md`; do not duplicate them in
`.codex/config.toml` or in every agent. Codex loads applicable `AGENTS.md`
guidance before work begins.

For a later, separately requested project skill, the compatible repository
location is `.agents/skills/<skill>/SKILL.md`. This target is informational;
this installation does not create skills.

Last manually verified: 2026-08-12 against
<https://learn.chatgpt.com/docs/agent-configuration/subagents> for the project
target and documented triple double-quoted TOML agent format. The catalog's
narrower unchanged-body restrictions follow TOML 1.0 basic-string semantics.

References:

- <https://learn.chatgpt.com/docs/agent-configuration/subagents>
- <https://learn.chatgpt.com/docs/build-skills>
- <https://toml.io/en/v1.0.0#string>
