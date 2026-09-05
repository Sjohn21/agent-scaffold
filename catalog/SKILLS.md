# Skills authoring contract

Author at most one new project-owned skill per run, or produce a read-only
skill recommendation report. The target repository owns every resulting file
immediately; do not add managed state, ownership markers, symlinks, helpers,
or an updater. This contract is separate from `INSTALL.md` and creates no
agents and no project guidance.

## 1. Resolve the catalog, target, and route

1. Resolve the catalog root and the target repository to absolute paths. Read
   this `SKILLS.md`, `catalog.json`, and every adapter document used later in
   this run from that same catalog root. Read adapter names and their ordered
   `skill_targets` from `catalog.json`; this document deliberately embeds no
   second target table.
2. Record the source mode: whether the catalog root is exactly the target's
   real, non-symlink `.agent-scaffold/` directory, or a sibling or other
   external path. Record whether the user explicitly requested cleanup of an
   exact staged source after success. A sibling or other external catalog is
   never a cleanup target.
3. When the catalog lies outside the active client's working directory, follow
   the read-access or approval guidance of the adapter document matching the
   active client — this rule keys on the client running this run, not on the
   skill's selected adapters, so it applies equally to Route B, which selects
   none. When the active client cannot be reliably identified or no adapter
   document covers it, request read access through the client's own native
   approval mechanism instead of assuming any adapter's caveat. If access is
   denied or cannot be established, stop and leave the catalog and target
   unchanged.
4. Choose exactly one route from the explicit request:
   - **Route A** authors one named project skill.
   - **Route B** returns read-only repository skill recommendations.

   Never execute both routes in one run and never continue from a Route B
   report into authoring. When one prompt asks both for recommendations and to
   author the best candidate immediately, execute only Route B without asking
   which route to choose, and state in the report that authoring requires a
   later, explicit Route A request that names one candidate and performs fresh
   source resolution, intake, and preflight.

## Route A — author one skill

### A1. Establish and classify one concrete use case

Require enough evidence to identify: the selected adapter or adapters; at
least two representative positive trigger prompts; the intended outcome and
important boundaries; and any required project references, scripts, or assets.
Accept a complete initial request without a confirmation question. When
material input is missing, ask at most one bundled follow-up containing at
most three material questions. Derive a nearby negative trigger from the
positive examples and scope; if its boundary stays ambiguous, fold that into
one of the three questions instead of adding a fourth.

Classify before authoring:

- stable, always-applicable project facts belong in `AGENTS.md`, not a skill;
- a repeatable, sometimes-relevant workflow, knowledge bundle, or deliberately
  invoked capability belongs in a skill;
- one-off context belongs in the active prompt or plan, not on disk.

When no concrete reusable skill use case can be established, stop with no
writes, report the classification and its reason, and retain any staged
catalog. Classification chooses the destination for new content; it does not
authorize moving or rewriting existing project guidance.

### A2. Resolve exactly one destination

Read every selected adapter document completely. Treat each adapter's
`skill_targets` as an ordered preference list: the first entry is that
adapter's native preference and later entries are compatible alternatives. For
one selected adapter, choose its first target. For several, compute the
intersection of their target lists and choose the common path with the best
declared preference.

When the intersection is empty, report the exact selected adapters and each
one's ordered targets, stop before any write, retain staging, and ask the
user to narrow the client selection. Do not duplicate the skill, create a
symlink, or invent a shared root. A later run with a different explicit
selection is a new one-time operation. Two separate runs can deliberately
create independent copies for disjoint selections; the user owns their
synchronization, and a third client may discover both locations and apply its
native precedence rules.

### A3. Draft the exact output in working context

Compose the complete intended relative file set and exact contents — the
`SKILL.md` and every justified resource — in working context before touching
the target. Every drafted path is relative to the skill root and must stay
strictly inside it; A4 rejects any escaping entry before writes. This draft
is the comparison source for every equivalence decision. Do not write yet and do not execute drafted scripts during
discovery.

Use the portable format: opening YAML frontmatter as the first bytes of the
skill's `SKILL.md`, containing exactly `name` and `description`, followed by a
non-empty Markdown body. `name` is 1-64 characters using only lowercase
`a-z`, `0-9`, and hyphens, with no leading, trailing, or consecutive hyphen,
and equals the skill directory name. `description` is 1-1024 characters
stating what the skill does and when to use it, front-loading trigger
keywords. Adapter-only frontmatter fields stay outside this contract.

### A4. Preflight every declared discovery root

Apply every native skill-name restriction documented by the selected adapters.
An adapter-specific invalid or reserved name stops all authoring writes; do not
weaken that restriction merely because the name passes the portable format.

Substitute the validated skill name into every `skill_targets` entry of every
selected adapter, not only the chosen destination. For each resulting
repository path:

- reject absolute, traversing, malformed, or symlink-escaping destinations,
  and inspect the destination and its parents for symlinks before writes;
- validate the drafted file set itself before any write: every drafted entry
  is a relative path with no absolute or parent-traversal segment, resolves
  to a regular-file location strictly inside the chosen skill directory, and
  no existing ancestor between that location and the chosen skill root is a
  symlink; one escaping draft entry stops all authoring writes;
- classify same-name content as absent, equivalent, or conflicting against
  the exact draft. Equivalent means the same relative set of regular files
  with byte-identical contents throughout the skill tree; directory metadata
  and timestamps do not participate, and any symlink disqualifies the tree;
- treat a complete equivalent tree at the chosen destination as a no-op:
  rewrite no content and no timestamp;
- treat an equivalent tree at an alternate declared root as a stop: report
  that exact root, retain staging, and create no second discoverable copy;
- treat any non-equivalent, partial, or otherwise conflicting same-name
  definition at any declared root as a conflict: report it, retain staging,
  and perform no authoring write;
- confirm the destination and its parent are writable and obtain every
  required approval before the first write.

Preserve every existing file; never merge, overwrite, rename, delete, or
shadow one. Updating an existing skill is ordinary explicit project work
outside this contract. Native personal, built-in, remote, or plugin skills
can shadow a repository skill; note what repository inspection cannot
resolve and rely on native discovery evidence for the effective result.

### A5. Write the shortest complete skill

When preflight classified the chosen destination as a complete equivalent
no-op, skip this step entirely — write nothing and rewrite no timestamp — and
continue with A6 validation and reporting. Otherwise write the drafted tree
at the chosen destination only. Keep the core workflow
in the skill's `SKILL.md`. Put non-core detail one level deep in
`references/`; add `scripts/` only for justified deterministic behavior and
`assets/` only for resources the workflow actually uses. Reference bundled
files by relative paths from the skill root. Do not add README, changelog,
install, lock, state, ownership, or update files, duplicated content, or deep
reference chains. Use the shortest complete content; always-loaded guidance
budgets for `AGENTS.md` do not apply to a skill body.

### A6. Validate and report

Re-read the authored tree — for a no-op, the existing equivalent tree at the
chosen destination. Check the portable frontmatter and name rules, the
non-empty body, the presence of every referenced resource, that only the
chosen destination changed, and the absence of unsafe or absolute references,
symlink escapes, and unresolved placeholders. Run only safe, proportionate
resource checks the user and environment permit.

Verify with the selected adapter's native guidance: discovery or listing, one
explicit invocation, the two positive triggers or the smallest representative
positive set, and the derived nearby negative. Report the prompts and the
observed activation boundary, exact changed paths, relevant command statuses,
native discovery evidence, conflict or no-op status, and otherwise unchanged
project state. Claim no managed relationship between catalog and target.

### A7. Route A cleanup

Cleanup requires all of the following: the user explicitly requested it; the
recorded source is the target's exact real, non-symlink `.agent-scaffold/`
directory; and this run completed successful authoring plus validation, or a
fully validated equivalent no-op at the chosen destination. Immediately before
removal, re-resolve the recorded path, confirm it is a real non-link
directory inside the target and not the target itself, and remove only that
exact directory. Never broaden the path.

Retain staging after a no-skill classification, empty intersection,
alternate-root equivalence, conflict, denied permission, or validation
failure. Never remove a sibling or other external catalog.

## Route B — read-only repository recommendations

### B1. Run a bounded repository inventory

Inspect the smallest useful set of project instructions, developer
documentation, task runners, CI workflows, scripts, templates, and recurring
procedure references. Do not run project code, mutate project content, access
services, or use network research to manufacture candidates.

### B2. Report at most three evidence-backed candidates

Rank only candidates supported by concrete repository evidence, such as a
repeated multi-step runbook, a recurring task sequence, a specialized
reference bundle, a consistent output template, or a fragile procedure that
is needed sometimes rather than always. Visible files ground a suggestion;
they do not prove actual usage frequency, so do not claim inferred repetition
the repository cannot show. For each ranked candidate report:

- a proposed portable name and one-sentence purpose;
- the exact repository evidence paths;
- why the material is repeatable and sometimes relevant rather than
  always-on;
- why a skill fits better than `AGENTS.md` guidance, one-off prompt or plan
  context, a custom agent, an MCP connection, or a lifecycle hook;
- two representative positive trigger prompts and a nearby negative trigger;
- the minimal likely `SKILL.md` plus any justified references, scripts, or
  assets.

When repository-native configuration clearly indicates one or more clients,
label them as detected rather than user-selected and report the current
`skill_targets` intersection consequence for that combination, including when
a later authoring request would have to narrow the selection. Report honestly
when no candidate is justified. Ask no speculative questionnaire, write
nothing, move no guidance, and do not transition to authoring: a later
explicit Route A request must name one candidate and perform its own source
resolution, adapter selection, intake, and preflight.

### B3. Finish Route B and apply its cleanup rule

Report the inspected evidence scope, the candidates or the honest
no-candidate result, detected-client caveats, the catalog source mode, and
that project content is unchanged. A successfully completed report qualifies
for cleanup even when it recommends no candidate: apply exactly the cleanup
conditions and re-resolution steps of Route A, with report success in place
of authoring success. Retain staging after denied permission, an interrupted
inventory, or a failed report. Never remove a sibling or other external
catalog.
