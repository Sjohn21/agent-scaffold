# Adapter compatibility references

This register is maintainer evidence for the adapter guidance in `catalog/`.
Compatibility is checked manually against vendor-owned documentation, the TOML
specification, and the Agent Skills specification; CI remains offline and does
not fetch, validate, or enforce freshness for these sources. The adapters are
the normative installation contract. This file neither replaces their
instructions nor forms a catalog dependency.

## Agent Skills specification

Checked 2026-09-01 against the open Agent Skills standard. Its numeric limits
are recorded here as the portable authoring subset because every claimed
adapter either requires them or accepts them; adapter sections below record
what each client itself documents.

- [Specification](https://agentskills.io/specification) supports the `SKILL.md`
  format: opening YAML frontmatter followed by a Markdown body; required
  `name` of 1-64 characters using only lowercase `a-z`, `0-9` and hyphens,
  with no leading, trailing, or consecutive hyphen, and equal to the parent
  directory name; required non-empty `description` of at most 1024 characters;
  optional `license`, `compatibility`, `metadata`, and experimental
  `allowed-tools` fields, which stay outside the portable subset; optional
  `scripts/`, `references/`, and `assets/` directories with relative
  references kept one level deep from the skill root; and progressive
  disclosure that always loads only `name` and `description` and loads the
  body and resources on demand.

## Codex

Checked 2026-09-01 against the current Codex documentation. The custom-agent
format is documented as evolving, so compatibility is tied to the documented
surface on that date rather than to a pinned client version.

- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
  supports project-scoped `.codex/agents/*.toml` files, their required fields
  and configuration-layer behavior; default enablement; sandbox and live
  permission precedence; and model, reasoning-effort, and omitted-setting
  inheritance.
- [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
  supports root `AGENTS.md` discovery and the applicable project-instruction
  loading order.
- [Build skills](https://learn.chatgpt.com/docs/build-skills) supports the
  repository `.agents/skills/<skill>/SKILL.md` target and its discovery scope.
  Rechecked 2026-09-01 for skills authoring: `.agents/skills/` is the only
  documented repository root, scanned in every directory from the working
  directory up to the repository root, alongside the user
  (`$HOME/.agents/skills`), admin (`/etc/codex/skills`), and bundled system
  locations; the page documents no precedence order between those scopes. No `.claude/` or `.github/` root is documented. Same-name skills are
  not merged and can both appear in skill selectors. Required frontmatter is `name` and `description`;
  optional `scripts/`, `references/`, and `assets/` directories match the open
  standard. Native checks are `/skills` listing and `$`-mention explicit
  invocation in the CLI; skill changes are detected automatically with restart
  as the fallback. Authoring guidance favors concise descriptions that
  front-load the key use case and trigger words. Reading a catalog outside the
  working directory is subject to the active sandbox; approval follows the
  documented sandbox and live permission precedence recorded above.
- [TOML 1.0 strings](https://toml.io/en/v1.0.0#string) supports the multiline
  basic-string delimiter, whitespace preservation, escaping, and forbidden
  control-character constraints used to preserve canonical agent bodies.

## Claude Code

Accepted 2026-09-01 subagent and skill evidence from commit `cad2a14`; those
adapter mappings are unchanged in this relocation. Instruction loading was
additionally checked against the current Claude Code documentation on
2026-09-01.

- [Subagents](https://code.claude.com/docs/en/sub-agents) supports project
  `.claude/agents/*.md` files, Markdown with YAML frontmatter, tool filtering,
  permission inheritance and precedence, `model: inherit`, and normal loading
  of project `CLAUDE.md` instructions.
- [Project memory](https://code.claude.com/docs/en/memory) supports root
  `CLAUDE.md` loading and the `@AGENTS.md` import used to share existing project
  instructions without replacing them.
- [Agent skills](https://code.claude.com/docs/en/skills) supports the project
  `.claude/skills/<skill>/SKILL.md` target. Rechecked 2026-09-01 for skills
  authoring: the documented skill locations are enterprise, personal
  `~/.claude/skills/`, project `.claude/skills/` (including parent and nested
  directories), and plugins; `.agents/skills/` is not documented as a Claude
  discovery root, so the Codex + Claude and Claude + Gemini repository
  intersections stay empty. On duplicate names, enterprise overrides personal
  and personal overrides project; a project skill replaces a same-name bundled
  skill. Claude Code follows the open Agent Skills standard and treats every
  frontmatter field as optional with `description` recommended; the invocation
  command comes from the skill directory name, so the portable
  name-equals-directory rule stays compatible. Native checks are the `/skills`
  menu, `/<skill-name>` explicit invocation, and live change detection without
  a restart (a newly created top-level skills directory needs one). An
  external catalog outside the working directory is readable through
  `--add-dir`/`/add-dir` or a per-read approval.
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview)
  supports the classification boundary used for skill recommendations:
  always-applicable conventions belong in `CLAUDE.md`, on-demand reference
  material and repeatable invocable workflows belong in skills, and isolation,
  external connections, and guaranteed event automation belong to subagents,
  MCP, and hooks respectively.

## GitHub Copilot

Checked 2026-09-01 against the current GitHub Copilot documentation. The
portable tool aliases are checked for the Copilot CLI/custom-agent surface;
environment-specific agents can expose additional tools or properties.

- [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
  supports Markdown agent profiles with YAML frontmatter and instruction
  bodies, the `read`, `search`, `execute`, `edit`, and `agent` tool aliases,
  explicit tool filtering, and default-model inheritance when `model` is
  omitted.
- [Creating custom agents for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
  supports repository `.github/agents/*.agent.md` files and project-level
  discovery by the CLI.
- [Custom instruction support](https://docs.github.com/en/copilot/reference/custom-instructions-support)
  supports root `AGENTS.md` instructions in Copilot CLI.
- [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
  supports the project `.github/skills/<skill>/SKILL.md`,
  `.agents/skills/<skill>/SKILL.md`, and `.claude/skills/<skill>/SKILL.md`
  targets. Rechecked 2026-09-01: all three project roots remain documented for
  the Copilot cloud agent, code review, CLI, app, and IDE agent-mode surfaces,
  with no documented precedence or duplicate-name rule between them; the
  manifest's ordering is this catalog's own preference policy with the
  Copilot-specific root first.
- [Adding agent skills for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
  supports required lowercase hyphenated `name` and required `description`
  frontmatter with optional `license`; bundled scripts and resources that are
  discovered when the skill is invoked; and the native `/skills list`,
  `/skills reload`, and explicit `/<skill-name>` invocation checks. It carries
  the trust caveat that `allowed-tools` pre-approval of shell tools removes
  the confirmation step and requires a fully trusted source.
- [Comparing CLI features](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/comparing-cli-features)
  supports the recommendation boundary: guidance that applies to everything
  belongs in custom instructions, a repeatable task-scoped capability belongs
  in a skill, and guidance-only needs do not justify a custom agent or MCP
  server.

## Gemini CLI

Checked 2026-09-01 against the current Gemini CLI documentation.

- [Subagents](https://geminicli.com/docs/core/subagents/) supports project
  `.gemini/agents/*.md` files, Markdown with YAML frontmatter, explicit and
  inherited tool sets, model inheritance when `model` is omitted, and default
  subagent enablement.
- [Provide context with GEMINI.md](https://geminicli.com/docs/cli/gemini-md/)
  supports root `GEMINI.md` context and relative `@file.md` imports such as
  `@./AGENTS.md`.
- The former [Tools API](https://geminicli.com/docs/reference/tools-api/) URL
  redirects to the canonical [Tools reference](https://geminicli.com/docs/reference/tools/),
  which supports the `glob`, `grep_search`, `list_directory`, `read_file`,
  `read_many_files`, `run_shell_command`, `replace`, and `write_file` names and
  their read, shell, and write behavior surfaces.
- [Managing agent skills](https://geminicli.com/docs/cli/using-agent-skills/)
  supports the workspace `.gemini/skills/<skill>/SKILL.md` and
  `.agents/skills/<skill>/SKILL.md` targets. Rechecked 2026-09-01:
  `.agents/skills/` is a documented alias of the workspace root, with
  precedence workspace over user over extension over built-in and the
  higher-precedence copy winning a duplicate name. Native checks are
  `/skills list`, `/skills reload`, per-skill `enable`/`disable`, and
  `/skills link`. Each in-session skill activation asks for permission, and a
  remote install confirms its source; a catalog outside the workspace needs
  the standard workspace-boundary approval.
- [Skill best practices](https://geminicli.com/docs/cli/skills-best-practices/)
  supports three-level progressive disclosure (always-loaded metadata, a
  triggered body under roughly five thousand words, on-demand resources) and
  description guidance requiring specific keywords, an explicit trigger
  condition, and non-overlapping scope — the criteria used for evidence-backed
  skill recommendations.
