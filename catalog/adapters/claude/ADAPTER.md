# Claude Code adapter

Install each selected agent at `.claude/agents/<agent>.md`. Use YAML
frontmatter followed by the canonical body:

```markdown
---
name: <agent>
description: <canonical plain description copied without quotes>
tools: Read, Grep, Glob, Bash
---

<canonical body unchanged>
```

The `tools` line above applies to canonical `read_only: true` agents. Bash is
required for bounded Git inspection and efficient repository search; the
absence of `Edit` and `Write` prevents native file-edit calls. Bash itself can
still mutate files or state, so this allowlist is neither filesystem-read-only
nor command-level isolation; the canonical no-state-change rule remains
behavioural. Do not set `permissionMode: plan`: it changes the agent's workflow
toward plan approval and is not needed for these reporting roles. For
write-capable agents, set an explicit allowlist derived from the canonical body.
Roles that only run commands or Git operations, including `test-runner` and
`plan-committer`, use
`Read, Bash, Grep, Glob` without `Edit` or `Write`. An implementation role such
as `plan-implementer` may additionally receive `Edit` and `Write`. Preserve
stricter existing project permissions.

Translate the model choice already resolved by the installation contract. For
explicit inheritance, omit `model`; for an exact model, add
`model: <resolved model>` only to that adapter-agent pair.

Claude subagents load project `CLAUDE.md` instructions. Ensure shared guidance
is reachable without replacing existing content: when root `CLAUDE.md` does not
already include equivalent shared guidance, append a small section containing
`@AGENTS.md`. Preserve every existing instruction. Do not create or modify
`.claude/settings.json` unless the requested installation needs a setting not
expressible in the agent file.

When a project-specific skill passes the installation contract's selection
criteria, its project location is `.claude/skills/<skill>/SKILL.md`. Do not
create a symlink to another adapter's skill tree.

Last manually verified: 2026-08-07 against
<https://code.claude.com/docs/en/sub-agents> for the project target and Markdown
frontmatter format.

References:

- <https://code.claude.com/docs/en/sub-agents>
- <https://code.claude.com/docs/en/skills>
