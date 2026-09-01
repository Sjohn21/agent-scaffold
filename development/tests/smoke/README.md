# Manual installation smoke test

This smoke test exercises the prompt-driven result that static catalog checks
cannot generate. Run it after changing the installation contract, canonical
agents, adapter translation, or native tool permissions.

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
