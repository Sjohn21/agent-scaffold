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
- [Installation recipes](#installation-recipes)
- [One-off catalog copy](#one-off-catalog-copy)
- [Author a project skill](#author-a-project-skill)
- [What installation does](#what-installation-does)
- [Use and maintain installed agents](#use-and-maintain-installed-agents)
- [Development](#development)
- [License](#license)

## Quick start

### 1. Get agent-scaffold

Clone the checkout next to the repository you want to configure:

```bash
cd /absolute/path/to/workspace
git clone https://github.com/Sjohn21/agent-scaffold.git
```

```text
workspace/
|-- agent-scaffold/
`-- your-project/
```

Update an existing checkout with `git pull` in it. If you would rather not keep
the checkout next to the target, use the
[one-off catalog copy](#one-off-catalog-copy) instead.

### 2. Open the target repository

Open `your-project` in the coding client you want to configure: Codex, Claude
Code, GitHub Copilot, or Gemini CLI.

### 3. Send the installation prompt

Replace the placeholder with the absolute path to your checkout, then send the
prompt. This example selects Codex; for another client use one of the
[installation recipes](#installation-recipes). Native target paths are selected
automatically by the adapter.

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install only the Codex adapter with the `reviewer` and
> `test-runner` agents; install no optional components. Preserve and merge
> existing project instructions and native configuration, stop before every
> write if any destination conflicts or is not writable, validate the result,
> and leave the sibling catalog in place.

### 4. Answer the model question

The prompt names no model, so the agent asks one bundled question before it
writes anything. Choose the recommended role-specific mapping, explicit
inheritance for every agent, or your own exact model names. To decide up front
and skip this question, see [Models](#models).

### 5. Review the preflight and report

Nothing is written until destinations, conflicts, and your model choice are
resolved. A normal Codex result for the prompt above is:

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
inheritance. By default you do not decide this up front: a prompt that names no
model makes the installation agent ask one bundled question before any write,
offering a recommended role-specific mapping, explicit inheritance for every
pair, or your own exact names. Nothing is written until you confirm.

Model choice is a deliberate quality, latency, and cost lever, so asking is the
default. Add one of these lines only when you want to skip the question:

| Add this line to the prompt | Effect |
| --- | --- |
| `Use explicit model inheritance for every selected adapter-agent pair` | Every installed agent runs on the client's inherited or default model. The most portable choice. |
| `Use <exact model> for <agent>`, once per pair or per adapter | Pins exact names. Supply names only when your active client confirms them; the catalog contains no fixed provider ranking and never guesses a name. |

Selecting an adapter with zero agents needs no model choice at all, and no
question is asked.

## Installation recipes

Each prompt below is complete except for the absolute path to this checkout.
Open the target repository in the named client before sending it. None of them
names a model, so every recipe that selects at least one agent ends in the
bundled model question described under [Models](#models).

### Adjust any recipe

| To change | Edit the prompt like this |
| --- | --- |
| Skip the model question | Add `Use explicit model inheritance for every selected adapter-agent pair` |
| Install every cataloged agent | Replace the agent list with `all` agents |
| Install for several clients at once | Name each one: `the Claude and Codex adapters` |
| Add the reusable plan template | Add `plus the optional plan-examples component` |
| Install shared guidance only | Ask for the adapter `with no agents` |
| Work from a staged copy instead of a sibling checkout | Use the [one-off catalog copy](#one-off-catalog-copy) |

### Claude Code: review and test helpers

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install only the Claude adapter with the `reviewer` and
> `test-runner` agents; install no optional components. Preserve and merge
> existing `AGENTS.md`, `CLAUDE.md`, and native agent configuration, stop
> before every write if any destination conflicts or is not writable, validate
> the result, and leave the sibling catalog in place.

Expected native agents:

```text
.claude/agents/reviewer.md
.claude/agents/test-runner.md
```

### Copilot: read-only planning and review

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install only the Copilot adapter with the `plan-search` and
> `reviewer` agents; install no optional components. Preserve and merge
> existing project instructions and native configuration, stop before every
> write if any destination conflicts or is not writable, validate the result,
> and leave the sibling catalog in place.

Expected native agents:

```text
.github/agents/plan-search.agent.md
.github/agents/reviewer.agent.md
```

### Gemini: phased planning

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install only the Gemini adapter with the `plan-search`,
> `plan-implementer`, and `reviewer` agents, plus the optional `plan-examples`
> component. Preserve and merge existing `AGENTS.md`, `GEMINI.md`, and native
> configuration, stop before every write if any destination conflicts or is not
> writable, validate the result, and leave the sibling catalog in place.

Expected additions include:

```text
.gemini/agents/plan-search.md
.gemini/agents/plan-implementer.md
.gemini/agents/reviewer.md
.agents/plans/_template/
```

### Shared guidance without specialist agents

This selects zero agents, so no model question is asked:

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install only the Claude adapter, with no agents and no
> optional components. Preserve and merge existing project instructions and
> native configuration, stop before every write if any destination conflicts
> or is not writable, validate the result, and leave the sibling catalog in
> place.

### Everything

> Read `/absolute/path/to/agent-scaffold/catalog/INSTALL.md` and install into
> this repository. Install the Codex, Claude, Copilot, and Gemini adapters with
> `all` agents, plus the optional `plan-examples` component. Preserve and merge
> all existing project instructions and native configuration, stop before every
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
> no optional components. Preserve and merge existing project instructions and
> native configuration, stop before every write if any destination conflicts or
> is not writable, validate the result, then remove only this target's exact
> `.agent-scaffold` directory after validation succeeds.

The installation contract removes only that exact temporary copy after
successful validation; the prompt repeats that automatic behavior explicitly.
It must never remove a sibling checkout or another source path.

## Author a project skill

Skills authoring is a separate, explicit operation from agent installation:
[catalog/SKILLS.md](catalog/SKILLS.md) governs it, and each run authors at
most one new skill. Installation never creates skills, and a staged catalog
that an earlier installation cleaned up is gone; make the catalog available
again first, either as a readable sibling checkout or by staging a fresh copy
with the [one-off catalog copy](#one-off-catalog-copy) recipe above.

With a staged copy at the target's `.agent-scaffold/`, open the target in the
client you want the skill for and send a complete request like:

> Read `.agent-scaffold/SKILLS.md` and author one new project skill for the
> Codex client only. The skill should walk through our release checklist in
> `docs/releasing.md`. Positive trigger examples: "prepare the next release"
> and "walk me through cutting a release". Preserve all existing files, stop
> before writing if the selected clients share no skill location or a
> same-name skill already exists anywhere, and after successful validation
> remove only this target's exact `.agent-scaffold` directory.

Name every client that should discover the skill, give two representative
trigger prompts, and point at any project files the skill needs. The
authoring agent reads the ordered `skill_targets` from the staged
`catalog.json`, writes to exactly one common native location, and stops
before writing when the selected clients share none. Codex + Claude is
currently such a combination: Codex discovers repository skills only under
`.agents/skills/` and Claude Code only under `.claude/skills/`, so that
selection reports both target lists and asks you to narrow it.

You can deliberately run authoring twice for disjoint selections — for
example once for Codex and once for Claude. The results are independent,
target-owned copies with no synchronization; you maintain both, and a third
client such as Copilot may discover both locations and apply its own native
precedence.

### Ask for skill recommendations

A separate read-only request proposes at most three evidence-backed skill
candidates from the repository without writing anything. Prefer a readable
sibling checkout for this, so the target stays untouched:

> Read `/absolute/path/to/agent-scaffold/catalog/SKILLS.md` and recommend at
> most three skill candidates for this repository, backed by exact repository
> evidence paths. Make no changes to this project's content.

If you stage the catalog for this instead, you may add: "after the
recommendation report succeeds, remove only this target's exact
`.agent-scaffold` directory." But when you expect to pick a candidate and
author it next, keep the staged catalog or use a sibling source — a cleaned
staging copy is not persistent, and the later authoring run would have to
stage the catalog again. Recommendations never turn into authoring in the
same run: pick one candidate and send a new explicit authoring request.

## What installation does

Before writing, the installation agent:

- reads the target's existing guidance and relevant project files;
- resolves every selected native destination;
- asks one bundled model question unless the prompt already names every choice;
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
