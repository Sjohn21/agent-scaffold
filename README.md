# Agent-scaffold

Agent-scaffold installs reusable specialist agents and concise project guidance
into an existing repository. You choose which supported coding client and which
roles you want; your coding agent reads the catalog, inspects the target
repository, asks any missing model question, and writes only that selection in
the client's native format.

This is a one-time installation, not a package manager. There is no installer
program, generated lockfile, managed state, ownership marker, synchronization,
or updater. Once installed, the target repository owns the resulting files.

Supported clients are Codex, Claude Code, GitHub Copilot, and Gemini CLI. A
practical first setup is your client's adapter with `reviewer` and
`test-runner`.

## Contents

- [Quick start](#quick-start)
- [Choose what to install](#choose-what-to-install)
- [More copy-paste installation recipes](#more-copy-paste-installation-recipes)
- [One-off catalog copy](#one-off-catalog-copy)
- [What installation does](#what-installation-does)
- [Use and maintain installed agents](#use-and-maintain-installed-agents)
- [Development](#development)
- [License](#license)

## Quick start

The simplest reusable setup is to keep agent-scaffold next to the repository
you want to configure:

```text
workspace/
|-- agent-scaffold/
`-- your-project/
```

1. Replace the two paths below and verify that you have the right source and
   target:

   ```bash
   (
     AGENT_SCAFFOLD="/absolute/path/to/agent-scaffold"
     TARGET_REPOSITORY="/absolute/path/to/your-project"

     if [ ! -f "$AGENT_SCAFFOLD/catalog/INSTALL.md" ]; then
       printf 'catalog not found: %s\n' "$AGENT_SCAFFOLD/catalog" >&2
       exit 1
     fi
     if [ ! -d "$TARGET_REPOSITORY" ]; then
       printf 'target directory not found: %s\n' "$TARGET_REPOSITORY" >&2
       exit 1
     fi
     printf 'catalog: %s\ntarget:  %s\n' \
       "$AGENT_SCAFFOLD/catalog" "$TARGET_REPOSITORY"
   )
   ```

2. Open the repository at the `target:` path printed by step 1 in the supported
   coding client you want to configure.

3. For the Codex quick-start selection, copy the `catalog:` value printed by
   step 1 into this prompt in place of the single absolute-path placeholder,
   then send it:

   > Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install
   > into this repository. Install only the Codex adapter with the `reviewer`
   > and `test-runner` agents; install no optional components. Use explicit
   > model inheritance for both agents. Preserve and merge existing project
   > instructions and native configuration, stop before every write if any
   > destination conflicts or is not writable, validate the installed TOML and
   > selected-file scope, and leave the sibling catalog in place.

   Recipes for the exact `claude`, `copilot`, and `gemini` adapter selections
   follow below. Native target paths are selected automatically by the adapter.

4. Review the agent's preflight and final report. A normal Codex result for the
   prompt above is:

   ```text
   your-project/
   |-- AGENTS.md
   `-- .codex/agents/
       |-- reviewer.toml
       `-- test-runner.toml
   ```

Existing instructions must remain intact. Unselected clients, agents, optional
components, and skills must remain absent.

## Choose what to install

Every installation selects at least one adapter, any number of agents, and
optionally `plan-examples`.

### Adapters

Choose the adapter for each coding client that should use the installed agents:

| Adapter | Client | Native agent target | Guidance |
| --- | --- | --- | --- |
| `codex` | Codex | `.codex/agents/<agent>.toml` | [Codex adapter](catalog/adapters/codex/ADAPTER.md) |
| `claude` | Claude Code | `.claude/agents/<agent>.md` | [Claude adapter](catalog/adapters/claude/ADAPTER.md) |
| `copilot` | GitHub Copilot | `.github/agents/<agent>.agent.md` | [Copilot adapter](catalog/adapters/copilot/ADAPTER.md) |
| `gemini` | Gemini CLI | `.gemini/agents/<agent>.md` | [Gemini adapter](catalog/adapters/gemini/ADAPTER.md) |

Selecting an adapter with zero agents is valid when you only want shared
project guidance. Selecting an adapter never implicitly selects another one.

### Agents

| Agent | Use it for | Definition |
| --- | --- | --- |
| `reviewer` | A fresh, read-only review of a bounded diff | [reviewer](catalog/agents/reviewer.md) |
| `test-runner` | Long or noisy checks with a compact result | [test-runner](catalog/agents/test-runner.md) |
| `plan-search` | Broad read-only inventory for one plan phase | [plan-search](catalog/agents/plan-search.md) |
| `plan-implementer` | Implementing one approved plan phase | [plan-implementer](catalog/agents/plan-implementer.md) |
| `plan-committer` | An exact, already verified commit within a plan workflow; not for routine commits | [plan-committer](catalog/agents/plan-committer.md) |

Use `all` as the complete agent selection when you want every cataloged agent.
Do not combine `all` with individual agent names. The optional
`plan-examples` component adds a reusable `.agents/plans/_template/`; planning
agents do not require it.

### Models

Every selected adapter-agent pair needs either an exact model or explicit
inheritance:

- Add `Use explicit model inheritance for every selected adapter-agent pair`
  for the most portable, no-follow-up prompt.
- Omit the model choice when you want the installation agent to recommend a
  role-specific mapping. It will present one bundled question before writing.
- Supply exact model names only when your active client confirms those names.
  The catalog deliberately contains no fixed provider ranking.

## More copy-paste installation recipes

Each prompt below is complete except for the absolute path to this checkout.
Open the target repository in the named client before sending it.

### Claude Code: review and test helpers

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install only the Claude adapter with the `reviewer` and
> `test-runner` agents; install no optional components. Use explicit model
> inheritance for both agents. Preserve and merge existing `AGENTS.md`,
> `CLAUDE.md`, and native agent configuration, stop before every write if any
> destination conflicts or is not writable, validate the result, and leave the
> sibling catalog in place.

Expected native agents:

```text
.claude/agents/reviewer.md
.claude/agents/test-runner.md
```

### Copilot: read-only planning and review

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install only the Copilot adapter with the `plan-search` and
> `reviewer` agents; install no optional components. Use explicit model
> inheritance for both agents. Preserve and merge existing project instructions
> and native configuration, stop before every write if any destination
> conflicts or is not writable, validate the result, and leave the sibling
> catalog in place.

Expected native agents:

```text
.github/agents/plan-search.agent.md
.github/agents/reviewer.agent.md
```

### Gemini: phased planning

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install only the Gemini adapter with the `plan-search`,
> `plan-implementer`, and `reviewer` agents, plus the optional `plan-examples`
> component. Use explicit model inheritance for every selected agent. Preserve
> and merge existing `AGENTS.md`, `GEMINI.md`, and native configuration, stop
> before every write if any destination conflicts or is not writable, validate
> the result, and leave the sibling catalog in place.

Expected additions include:

```text
.gemini/agents/plan-search.md
.gemini/agents/plan-implementer.md
.gemini/agents/reviewer.md
.agents/plans/_template/
```

### Shared guidance without specialist agents

This requires no model choice:

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install only the Claude adapter, with no agents and no
> optional components. Preserve and merge existing project instructions and
> native configuration, stop before every write if any destination conflicts
> or is not writable, validate the result, and leave the sibling catalog in
> place.

### Everything

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install the Codex, Claude, Copilot, and Gemini adapters with
> `all` agents, plus the optional `plan-examples` component. Use explicit model
> inheritance for every selected adapter-agent pair. Preserve and merge all
> existing project instructions and native configuration, stop before every
> write if any destination conflicts or is not writable, validate every native
> format and the selected-file scope, and leave the sibling catalog in place.

## One-off catalog copy

Use this method when you do not want to keep the agent-scaffold checkout next
to the target. Replace both paths, then copy only the standalone `catalog/`
distribution:

```bash
(
  AGENT_SCAFFOLD="/absolute/path/to/agent-scaffold"
  TARGET_REPOSITORY="/absolute/path/to/your-project"
  TEMPORARY_CATALOG="$TARGET_REPOSITORY/.agent-scaffold"

  if [ ! -f "$AGENT_SCAFFOLD/catalog/INSTALL.md" ]; then
    printf 'catalog not found: %s\n' "$AGENT_SCAFFOLD/catalog" >&2
    exit 1
  fi
  if [ ! -d "$TARGET_REPOSITORY" ]; then
    printf 'target directory not found: %s\n' "$TARGET_REPOSITORY" >&2
    exit 1
  fi
  if [ -e "$TEMPORARY_CATALOG" ] || [ -L "$TEMPORARY_CATALOG" ]; then
    printf '%s already exists; stop and inspect it\n' "$TEMPORARY_CATALOG"
  else
    cp -R "$AGENT_SCAFFOLD/catalog" "$TEMPORARY_CATALOG"
  fi
)
```

Open the target repository in your coding client and use this prompt:

> Read `.agent-scaffold/INSTALL.md` and install into this repository. Install
> only the Codex adapter with the `reviewer` and `test-runner` agents; install
> no optional components. Use explicit model inheritance for both agents.
> Preserve and merge existing project instructions and native configuration,
> stop before every write if any destination conflicts or is not writable,
> validate the result, then remove only this target's exact `.agent-scaffold`
> directory after validation succeeds.

The installation agent may remove only that exact temporary copy, only after
successful validation, and only because the prompt explicitly requests it. It
must never remove a sibling checkout or another source path.

## What installation does

Before writing, the installation agent:

- reads the target's existing guidance and relevant project files;
- resolves every selected native destination;
- asks one bundled question if model choices are incomplete;
- reports conflicts or unwritable destinations and stops all writes;
- preserves existing instructions and unrelated native configuration.

After writing, it validates native formats and selected-file scope, checks for
unresolved placeholders, runs safe relevant checks, and reports changed files,
model choices, command status, guidance size, conflicts, and cleanup status.

Only explicitly selected adapters, agents, and optional components are
installed. No renderer, helper, state file, lock, hash manifest, or update
relationship is copied into the target.

## Use and maintain installed agents

Invoke an installed agent by name and give it a bounded task, for example:

> Use `reviewer` to review the working tree.

> Use `test-runner` to run the full unit-test suite and summarize failures.

> Use `plan-search` to inventory the authentication phase in
> `.agents/plans/authentication/`.

The exact invocation UI depends on the client. Canonical roles define behavior;
adapters translate paths, permissions, tools, instruction loading, and model
configuration.

Installed files are ordinary project files. Review, commit, edit, or remove
them like any other repository content. Re-running the catalog is a new
one-time installation operation, not an update or synchronization workflow.

The full execution rules live in [catalog/INSTALL.md](catalog/INSTALL.md), and
the machine-readable selection is in
[catalog/catalog.json](catalog/catalog.json).

## Development

Repository maintenance and verification are documented in
[DEVELOPMENT.md](DEVELOPMENT.md).

## License

Licensed under [MIT-0](LICENSE).
