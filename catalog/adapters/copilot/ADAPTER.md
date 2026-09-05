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

For a separately requested project skill governed by `SKILLS.md`, the
compatible targets in preference order are `.github/skills/<skill>/SKILL.md`,
`.agents/skills/<skill>/SKILL.md` and `.claude/skills/<skill>/SKILL.md`. This
installation does not create skills. The first target is Copilot-specific;
the other two can be deliberate shared native locations when another selected
client supports them. Copilot CLI documents first-found-wins precedence between
these roots in this order. The general documentation for other Copilot surfaces
does not establish their precedence, so preflight must still treat a same-name
definition at any declared root as significant. Reading a catalog outside the
working directory follows the CLI's normal directory-access approval. Verify
natively with `/skills list`, `/skills reload` after adding a skill mid-session,
and an explicit `/<skill>` invocation in a prompt.
