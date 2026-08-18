# Installation contract

Install selected catalog parts into a target repository once. The target owns
every installed file; do not add managed state, ownership markers or an updater.

## 1. Resolve

1. Resolve the catalog root and target to absolute paths; read `catalog.json`.
   Reject unknown or duplicate names. Require at least one adapter; zero agents
   and zero optional components are valid. For agent selection only, the sole
   keyword `all` expands to every agent in `catalog.json`; expand it before
   model resolution and destination preflight. Do not combine `all` with named
   agents. Adapters and optional components have no `all` shorthand.
2. Record whether the source is exactly `<target>/.agent-scaffold/`. Only that
   directory can later be removed; never remove a sibling or other source.
3. With zero selected agents, ask no model question. Otherwise require a
   user-confirmed model choice for every selected adapter-agent pair before any
   write. A complete choice in the initial prompt needs no second question. If
   any choices are missing, ask one bundled question for all missing pairs and
   offer these routes:
   - **Recommended mapping:** show an exact available model or explicit
     inheritance for each pair, with a short role- and project-specific reason.
   - **Inherit all:** show explicit inheritance for every pair.
   - **Custom mapping:** accept one exact model per adapter or an exact
     adapter-agent mapping; validate that it covers every pair.

   Mark one mapping as recommended, but do not select or apply it without the
   user's explicit confirmation. Use an exact slug only when the active client
   or environment, or other already available reliable provider information,
   supports that exact name; model memory alone is not evidence. Where no exact
   slug is supported, recommend inheritance for that pair, state the desired
   profile such as `fast/cost-efficient` or `stronger review reasoning`, and
   allow a user-supplied exact slug.

   When the orchestrator model is known, compare quality, speed and cost with
   it. Bounded search, test or mechanical roles may merit a cheaper or faster
   model; implementation, review or other quality-critical roles may merit a
   stronger model. Make this judgment per role and project, not from a fixed
   provider ranking. If a custom mapping is partial, ask again once for all
   missing pairs. Do not guess slugs or fill gaps silently. Write only after
   the user confirms a route and every resulting value.

## 2. Inspect and preflight

Use this ordered discovery funnel:

1. Inventory relevant filenames without opening broad file sets.
2. Read applicable root and nested project instructions for the selected
   destinations.
3. Inspect selected adapters' native configuration and the exact destination
   parents.
4. Read the smallest set of root manifests, task runners or CI files needed to
   establish concise project guidance and one proportionate verification
   command.
5. Read developer docs, entrypoints, containers or representative tests only
   to resolve a named ambiguity left by the earlier steps.

Stop discovery when all destinations, conflicts, writability, guidance facts
and verification evidence are resolved. Derive command candidates statically.
For each relevant command whose invocation must be confirmed, run at most one
trusted candidate, and only when user authority, sandboxing and expected side
effects permit it. Do not try an alternative candidate after a failure; leave
that command unconfirmed. Do not otherwise execute project code, mutate state,
download, use services or access the network for discovery.

Keep one status per relevant command. An invocation is confirmed when it reaches
the intended runner or task, even if checks then fail. Unknown targets, bad CLI
syntax, or missing dependencies, services, credentials or permission leave it
unconfirmed. Never guess a command or hide its status.

Calculate every destination for the selected guidance, adapter-agent pairs,
components and imports. Substitute only validated catalog names into native
target templates. Reject an absolute or traversing path, or any destination or
parent symlink that resolves outside the target repository, before any write.
Classify each destination as new, equivalent, safely mergeable or conflicting.
A conflict is any case where preserving both meanings needs a user decision.
Report all conflicts and stop before every installation write. Also confirm
every destination and parent is writable under the current policy. Obtain every
required approval during preflight, before changing any destination. A denied
preflight permission means approval is unavailable: stop all installation
writes rather than continuing with other destinations. Never silently replace,
rename or delete existing project files.

## 3. Write project guidance

Preserve existing root `AGENTS.md` text byte-for-byte and retain its structure.
Add a fact when recording it compactly is cheaper than deriving it again in
every session, or when a wrong guess would be unsafe. Preserve explicit user
instructions even when they do not pass this filter. Do not repeat obvious
commands or layout. Typical categories are stack/layout, commands, verification,
invariants and gotchas. Include a concrete, evidenced command or check that
should pass before completion; mark an unconfirmed check as such and invent
nothing.

For a new file, use a short title and only headings with useful content. Add
`Delegation` only when agents were selected, with one concise project-specific
trigger per selected agent and none for unselected agents. Bound each trigger by
the canonical role; keep small or tightly coupled work with the parent. Do not
claim delegation guarantees lower total token use.

Keep added or materially rewritten guidance as short as possible; 600
whitespace-separated words is a hard ceiling, not a target. Preserved text is
excluded and is never shortened for this budget. Keep existing `CLAUDE.md` and
`GEMINI.md` content. Add the adapter's safe root `AGENTS.md` import only when
required.

## 4. Translate selections

Read each selected `ADAPTER.md` and canonical agent completely. Translate only
selected pairs to their exact native targets. Preserve name, description, full
behaviour, write boundary and the canonical statement that project guidance
cannot weaken read-only safety. Use least privilege and the adapter's documented
shell caveat; do not claim stronger isolation. Explicit inheritance omits the
native model field; an exact model is applied only to its named adapter-agent
pair. Preserve unrelated native configuration and do not copy canonical
sources, renderers or overlays.

Install `plan-examples` only when selected, at `.agents/plans/_template/`. The
target owns the examples. Never invent an active plan name.

This installation creates no skills. A later, separate user request must
explicitly ask for any project-skill work.

## 5. Validate, report and clean up

Re-read changed files and inspect the diff. Confirm every changed path follows
from guidance, a selected pair/component, a required import or allowed cleanup.
Verify unselected combinations are absent and unrelated agents remain. Parse
JSON/TOML with standard tooling and validate required Markdown frontmatter.
Check included guidance facts against evidence and the filter above. Search for
unresolved catalog placeholders. Confirm no installer, renderer, target helper,
state, lock or hash manifest was added. Run safe, proportionate checks and
report evidence, execution, invocation status and outcome separately.

For new guidance run `wc -w "<absolute-target>/AGENTS.md"`; for a merge, first
measure the added/rewritten draft with `wc -w "<absolute-draft>"`. Require that
result to be at most 600. Preserved text is not part of that limit and must not
be shortened.

Only after all validation succeeds, if the recorded source was exactly the
target's `.agent-scaffold/`, resolve it again and verify it is a real, non-link
directory inside the target and not the target itself; remove only that exact
directory. Never broaden cleanup after failure. Report selections, each exact
model choice and each explicit inheritance, changed files, command statuses,
the guidance draft word count, conflicts, validation, and whether cleanup
occurred.
