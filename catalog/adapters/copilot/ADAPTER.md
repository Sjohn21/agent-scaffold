# GitHub Copilot adapter

Install each selected agent at `.github/agents/<agent>.agent.md`. Use YAML
frontmatter followed by the canonical body:

```markdown
---
name: <agent>
description: <canonical plain description copied without quotes>
tools: ["read", "search", "execute"]
---

<canonical body unchanged>
```

The restricted tools list applies to canonical `read_only: true` agents.
`execute` is required for bounded Git inspection and efficient repository
search; `edit` remains absent. `execute` can still mutate files or state, so
this list is neither filesystem-read-only nor command-level isolation; the
canonical no-state-change rule remains behavioural. For write-capable agents,
derive the smallest combination of portable aliases from the canonical body.
Roles that only run commands or Git operations, including `test-runner` and
`plan-committer`, use `read`, `search`, and `execute` without `edit`. An
implementation role such as `plan-implementer` may additionally use `edit`. Do
not add `agent` unless the role genuinely needs nested delegation.

Translate the model choice already resolved by the installation contract. For
explicit inheritance, omit `model`; for an exact model, add
`model: <resolved model>` only to that adapter-agent pair.

Copilot uses root `AGENTS.md` directly, so no import or base configuration is
needed.

Preserve all existing files below `.github/`, especially workflows,
instructions and unrelated custom agents.

For a later, separately requested project skill, the compatible targets are
`.github/skills/<skill>/SKILL.md`, `.agents/skills/<skill>/SKILL.md` and
`.claude/skills/<skill>/SKILL.md`. This metadata is informational; this
installation does not create skills. The first target is Copilot-specific; the
other two can be deliberate shared native locations when another client
supports them.

Last manually verified: 2026-08-07 against the official custom-agent
<https://docs.github.com/en/copilot/reference/custom-agents-configuration>
format reference and
<https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli>
project-target guide.

References:

- <https://docs.github.com/en/copilot/reference/custom-agents-configuration>
- <https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli>
- <https://docs.github.com/en/copilot/concepts/agents/about-agent-skills>
