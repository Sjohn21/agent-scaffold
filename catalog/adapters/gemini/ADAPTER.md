# Gemini CLI adapter

Install each selected agent at `.gemini/agents/<agent>.md`. Use YAML frontmatter
followed by the canonical body:

```markdown
---
name: <agent>
description: <canonical plain description copied without quotes>
tools:
  - glob
  - grep_search
  - list_directory
  - read_file
  - read_many_files
  - run_shell_command
---

<canonical body unchanged>
```

The restricted tools list applies to canonical `read_only: true` agents.
`run_shell_command` is required for bounded Git inspection and efficient
repository search; `replace` and `write_file` remain absent. The shell tool can
still mutate files or state, so this list is neither filesystem-read-only nor
command-level isolation; the canonical no-state-change rule remains
behavioural. For write-capable agents, keep an explicit list derived from the
canonical body. Roles that only run commands or Git operations, including
`test-runner` and `plan-committer`, use the same list. An implementation role
such as `plan-implementer` may
additionally receive `replace` and `write_file`. Do not omit `tools` to inherit a
broader parent toolset.

Translate the model choice already resolved by the installation contract. For
explicit inheritance, omit `model`; for an exact model, add
`model: <resolved model>` only to that adapter-agent pair.

Gemini subagents are enabled by default in current releases. Do not create or
modify `.gemini/settings.json` merely to enable them. Ensure shared guidance is
reachable without replacing existing content: when root `GEMINI.md` does not
already include equivalent shared guidance, append a small section containing
`@./AGENTS.md`. Preserve every existing instruction and setting.

For a later, separately requested project skill, the compatible targets are
`.gemini/skills/<skill>/SKILL.md` and `.agents/skills/<skill>/SKILL.md`. This
metadata is informational; this installation does not create skills. The first
target is Gemini-specific; the second can be a deliberate shared native
location with Codex or Copilot. Do not use a symlink between locations.

Last manually verified: 2026-08-07 against
<https://geminicli.com/docs/core/subagents/> for the project target and Markdown
frontmatter format.

References:

- <https://geminicli.com/docs/core/subagents/>
- <https://geminicli.com/docs/reference/tools-api/>
- <https://geminicli.com/docs/cli/using-agent-skills/>
