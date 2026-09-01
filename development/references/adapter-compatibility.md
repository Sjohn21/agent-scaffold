# Adapter compatibility references

This register is maintainer evidence for the adapter guidance in `catalog/`.
Compatibility is checked manually against vendor-owned documentation and the
TOML specification; CI remains offline and does not fetch, validate, or enforce
freshness for these sources. The adapters are the normative installation
contract. This file neither replaces their instructions nor forms a catalog
dependency.

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
  `.claude/skills/<skill>/SKILL.md` target.

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
  targets.

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
  `.agents/skills/<skill>/SKILL.md` targets.
