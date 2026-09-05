# Manual installation smoke test

This smoke test exercises the prompt-driven result that static catalog checks
cannot generate. Run it after changing the installation contract, canonical
agents, adapter translation, or native tool permissions. The
[skills authoring smoke](#skills-authoring-smoke) below applies after changing
`catalog/SKILLS.md`, `skill_targets` metadata, or adapter skill guidance.

Use this matrix to choose the minimum manual scope for a focused change. Run
the full scenario set for broad releases or changes spanning multiple adapters.

| Change | Minimum manual scenarios |
| --- | --- |
| Installation contract, model question, shared preflight, or guidance | Codex, Claude, and zero-agent |
| Canonical agent | A scenario that installs and actually delegates that agent |
| One adapter | That adapter's scenario, plus the shared baseline when the contract also changed |
| Catalog selection, `all`, or model matrix | All-agent and zero-agent, plus the Codex baseline |
| Native permissions or tools | Every affected adapter |

The matrix narrows execution scope only. Every selected scenario retains all of
its checks and evidence requirements below.

The host must allow writes to the selected native configuration directory.
Managed environments may mount `.codex/` read-only or require a separate
approval for `.claude/`. Run Claude in the foreground so such an approval can be
granted. If the approval is unavailable, the expected result is a blocked
preflight with no target changes; do not count that as a successful install.

## Prepare an isolated target

From the agent-scaffold repository root:

```bash
CATALOG_ROOT="$(pwd)/catalog"
SMOKE_ROOT="$(mktemp -d)"
PRESERVED_PREFIX="$(mktemp)"
cp -R development/tests/fixtures/install-smoke/. "${SMOKE_ROOT:?}/"
awk 'BEGIN { for (i = 1; i <= 1210; i++) print "preserved-guidance-" i }' \
  >> "${SMOKE_ROOT:?}/AGENTS.md"
cp "${SMOKE_ROOT:?}/AGENTS.md" "${PRESERVED_PREFIX:?}"
git -C "${SMOKE_ROOT:?}" init
git -C "${SMOKE_ROOT:?}" add .
git -C "${SMOKE_ROOT:?}" -c user.name=Smoke -c user.email=smoke@example.invalid commit -m fixture
printf 'catalog: %s\ntarget: %s\npreserved prefix: %s\n' \
  "$CATALOG_ROOT" "$SMOKE_ROOT" "$PRESERVED_PREFIX"
```

Keep the printed paths. The temporary target and prefix copy may be removed
after inspection.

## Codex scenario

Open the temporary target in Codex and give it the printed catalog path:

> Read `<catalog>/INSTALL.md` and install into this repository. Install only
> the Codex adapter with the `reviewer` and `test-runner` agents. Preserve
> existing instructions, validate the result, and do not remove the sibling
> catalog checkout.

Because the prompt omits the model choice, the installer must ask one bundled
question before writing. Confirm `git status --short` is still empty at that
point. Record the offered recommended mapping and its role-specific reasons,
then deliberately choose that mapping exactly as shown. If the client cannot
support any exact slug from available evidence, the recommendation must use
explicit inheritance for that pair; choose that fallback and record the
availability limitation.

When the installer needs a local discovery command that is not already known,
also record its preflight evidence. Confirm it tries at most one trusted
candidate and, after a failed or unavailable command, tries no alternative and
leaves that command unconfirmed. Confirm no discovery command changes the
target.

After installation, compare the entire preserved prefix:

```bash
PREFIX_BYTES="$(wc -c < "${PRESERVED_PREFIX:?}")"
head -c "$PREFIX_BYTES" AGENTS.md | cmp - "${PRESERVED_PREFIX:?}"
```

Check that:

- `AGENTS.md` still contains `existing-guidance-must-survive`;
- the prefix comparison succeeds, proving the entire existing text stayed
  byte-for-byte unchanged;
- the added or materially rewritten guidance measurement is at most 600 words
  while remaining as short as possible, and includes concrete verification;
- no total-guidance word limit or warning is required for the preserved prefix;
- `.codex/agents/reviewer.toml` and `.codex/agents/test-runner.toml` exist and
  both parse as TOML;
- after parsing, each `developer_instructions` value exactly equals its
  canonical body after frontmatter removal, with no added final newline, and
  the closing `"""` directly follows the final body character;
- no other `.codex/agents/*.toml` or adapter directories were created;
- no skill path was created or reported;
- each native `model` field exactly matches the recorded chosen slug for its
  adapter-agent pair, while every chosen inheritance omits that field;
- the native reviewer has `sandbox_mode = "read-only"` and follows project
  guidance supplied in context without rereading it;
- the native test-runner uses the smallest usable Codex sandbox and preserves
  the canonical command-only and no-production-edit boundary;
- a read-only or protected `.codex/` destination is detected before `AGENTS.md`
  or any other target file changes;
- an absolute, traversing or symlink-escaping resolved destination is rejected
  before any target file changes;
- with several optional metadata sources present, discovery stops once all
  destinations, conflicts, writability, guidance facts and verification
  evidence are resolved.

Append a harmless line to the tracked fixture README and create a small,
non-ignored untracked source or test file. Record `git status --short`, then
open a fresh Codex invocation so the installed native files are loaded and
delegate `reviewer` with selector `working tree`. Confirm it inspects the
tracked diff, status, and new file content; treats both files as in scope;
returns only review findings; does not ask for the diff to be pasted; does not
read `AGENTS.md` again; and leaves `git status --short` unchanged. If an
untracked file cannot reasonably be inspected, confirm the reviewer reports
that limitation rather than silently omitting it.

## Claude scenario

Prepare a fresh target copy and request only the Claude adapter with
`reviewer`, explicitly choosing model inheritance in the initial prompt. Check
that root `CLAUDE.md` imports `@AGENTS.md`, the native tools are exactly `Read,
Grep, Glob, Bash`, `model: inherit` is present, and `permissionMode` is absent.
Confirm the agent file loads natively. Run the same working-tree review and
confirm the agent uses `git diff` without an extra `AGENTS.md` read or any file
mutation. This verifies the persisted inheritance choice; it does not prevent a
later explicit per-invocation model override. If `.claude/` needs approval,
confirm the agent requests it before changing `CLAUDE.md` or `AGENTS.md`.

## Copilot and Gemini scenarios

For separate fresh targets, request `plan-search` and `reviewer` with explicit
inheritance. Copilot must create only the two `.github/agents/*.agent.md` files
with tools `read`, `search`, `execute` and no `edit`; it uses root `AGENTS.md`
without another import. Gemini must create the two `.gemini/agents/*.md` files,
whose `tools` block includes read/search/shell tools but neither `replace` nor
`write_file`, and root `GEMINI.md` must import `@./AGENTS.md`. Neither adapter's
agents may have a `model` field. In both cases, delegate a bounded read-only
task and confirm Git and filesystem state do not change.

## Zero-agent scenario

Prepare two more fresh targets and select one adapter but no agents in each.
Keep the fixture's `AGENTS.md` in one; remove it and commit that fixture change
before installation in the other. Confirm both installers ask no model question
and create no native agent file. The existing guidance stays intact, while the
new `AGENTS.md` has no empty `Delegation` heading.

## All-agent scenario

Prepare a fresh target and request one adapter with `all` agents and explicit
model inheritance. Confirm `all` is expanded from `catalog.json` before model
and destination preflight, and that it is not treated as an agent named `all`.
Every cataloged agent for the selected adapter must be created, with no
unselected adapter or optional component. Repeat with `all` combined with one
named agent and confirm the installer rejects the mixed selection before every
write.

For the installed `plan-committer`, first delegate a commit without an exact
file path list, then with only a directory scope; confirm both block without
staging. Next supply exact file paths but leave a staged change outside them,
and confirm it still blocks without altering the index. Finally use an isolated
target with an exact path list, explicit confirmation that all changes in those
files are task-owned, and supplied successful verification; confirm it creates
one commit containing only those files and does not push, amend, or rebase.

## Skills authoring smoke

Run this matrix after changing `catalog/SKILLS.md`, any adapter's
`skill_targets`, or adapter skill guidance. It proves prompt-driven authoring
output and native client behavior that offline tests deliberately do not
simulate. Do not add authored dogfood skills to this repository to make it
repeatable; use isolated disposable targets and record exact client versions
and paths.

| Change | Minimum scenarios |
| --- | --- |
| `SKILLS.md` shared resolve or cleanup rules | One staged-source authoring scenario, the staged-catalog lifecycle checks, and one Route B run |
| Route A steps | Every adapter claimed as supported, plus the preflight boundary scenarios |
| Route B steps | The recommendation run, the combined-request scenario, and the thin-repository scenario |
| One adapter's skill guidance or targets | That adapter's authoring scenario plus the boundary scenarios its targets participate in |
| Portable format rules | One authoring scenario per adapter, checking frontmatter acceptance natively |

### Prepare an authoring target

Reuse the isolated-target preparation above, then add the small project
resource the example use case needs, stage only the catalog, and capture a
baseline so target writes are distinguishable from the known source copy:

```bash
mkdir -p "${SMOKE_ROOT:?}/docs"
printf '# Release checklist\n\n1. Run the full test suite.\n2. Update the changelog.\n3. Tag and publish the release.\n' \
  > "${SMOKE_ROOT:?}/docs/releasing.md"
git -C "${SMOKE_ROOT:?}" add docs/releasing.md
git -C "${SMOKE_ROOT:?}" -c user.name=Smoke -c user.email=smoke@example.invalid commit -m 'authoring resource'
cp -R "${CATALOG_ROOT:?}" "${SMOKE_ROOT:?}/.agent-scaffold"
git -C "${SMOKE_ROOT:?}" status --short > "${SMOKE_ROOT:?}/../authoring-baseline.txt"
```

The baseline is deliberately captured after staging, so it records the
untracked `.agent-scaffold/` entry. In the final comparison, exactly two
differences from this baseline are permitted: the authored skill paths at the
selected destination, and — only when cleanup was explicitly requested and
performed — the disappearance of the recorded `.agent-scaffold/` entry. Any
other difference fails the scenario.

Where an adapter supports a sibling source, also record its documented
external-working-directory read-access or approval caveat in at least one run;
this does not replace the required successful staged-source scenario.

### Successful authoring scenarios

For every adapter claimed as supported in v1 — Codex, Claude Code, GitHub
Copilot, and Gemini CLI — use a fresh isolated target and one concrete
instruction-only use case. The request supplies the selected adapter, two
representative positive trigger prompts, and required project references up
front; allow at most one bundled follow-up of at most three material
questions. A staged-source example:

> Read `.agent-scaffold/SKILLS.md` and author one new project skill for the
> Codex client only. The skill should walk through the release checklist in
> `docs/releasing.md`. Positive triggers: "prepare the next release" and
> "walk me through cutting a release". Preserve all existing files, stop before writing
> on an empty intersection or any same-name skill, and after successful
> validation remove only this target's exact `.agent-scaffold` directory.

Each scenario must record:

- client name and exact version, checked official sources, catalog source
  mode, and whether cleanup was explicitly requested and performed;
- selected adapters and the calculated target intersection;
- that exactly one skill was authored at the adapter's verified selected
  target and only selected clients were considered;
- native evidence that frontmatter and resources load: discovery/listing
  (`/skills` in Codex and Claude, `/skills list` in Copilot and Gemini,
  reload where the adapter documents it), one explicit invocation, both
  positive triggers activating, and the derived nearby negative trigger not
  activating (Gemini's per-activation permission prompt is expected trigger
  evidence, not a failure);
- exact changed paths, no managed-relationship claim, and Git state matching
  the recorded baseline except for the authored skill paths and any
  explicitly authorized `.agent-scaffold/` removal, as defined in the
  preparation step above.

When verified intersections permit, a shared `.agents/skills/` scenario may
cover a Codex + Copilot + Gemini selection and a shared `.claude/skills/`
scenario may cover Claude + Copilot; a shared scenario satisfies an adapter's
successful scenario only when the evidence still clearly proves that
adapter's own discovery and trigger behavior.

### Recommendation (Route B) scenarios

At least one successful read-only run is mandatory. From a readable sibling
catalog where possible:

> Read `<catalog>/SKILLS.md` and recommend at most three skill candidates for
> this repository, backed by exact repository evidence paths. Make no changes
> to this project's content.

Confirm the report contains between one and three candidates with exact
evidence paths and classification rationale, route-specific reporting, no
project-content change, and — when the fixture exposes native client
configuration — clients labeled as detected rather than selected with their
target-intersection consequence. When an explicitly cleanup-authorized exact
staged copy is used instead, confirm the staged source is removed only after
the report succeeds.

Also run both Route B boundary scenarios on fresh targets:

- a combined "recommend and author the best candidate" request executes only
  Route B, asks no route-choice question, changes nothing, and directs the
  user to a later explicit Route A request;
- a deliberately thin repository produces an honest no-candidate report,
  changes nothing, and still applies the successful-report cleanup rule when
  exact staged-source cleanup was explicitly requested.

### Preflight boundary scenarios

Use fresh targets to prove each stop changes nothing and retains staging:

- a representative empty intersection — at minimum Codex + Claude while it
  remains empty — reports both exact ordered target lists;
- the all-four selection changes nothing while its intersection stays empty;
- an equivalent skill at the selected destination is a no-op with no rewritten
  content or timestamp;
- an equivalent same-name skill at an alternate declared root reports that
  exact root and creates no preferred-path duplicate;
- a non-equivalent same-name skill at the selected or an alternate declared
  root reports a conflict and stops every authoring write;
- an unsafe, traversing, unwritable, denied, or symlink-escaping destination
  stops before all writes;
- a Claude selection using the reserved skill name `synced` reports the native
  restriction, stops before all writes, and retains staging;
- no symlink or second copy is offered as an automatic workaround.

### Staged-catalog lifecycle checks

Prove that cleanup stays exact and explicit:

- explicit cleanup after successful authoring removes only the re-resolved
  exact staged `.agent-scaffold/`;
- an explicitly cleanup-authorized chosen-destination no-op removes only that
  exact staged source after equivalence and validation succeed;
- a successful Route B report removes only its explicitly cleanup-authorized
  exact staged source;
- no-skill classification, empty intersection, alternate-root equivalence,
  conflict, denied permission, and validation failure all retain staging;
- a sibling or other external catalog is never removed;
- a cleanup request aimed at a symlink, the target itself, or any non-exact
  source is rejected without broadening cleanup.

A blocked permission check or empty-intersection run is boundary evidence,
not a replacement for successful authoring and native triggering. Record
client or trust limitations separately from product passes.
