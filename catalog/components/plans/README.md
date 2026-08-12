# Plans

A plan is temporary working structure for a risky, multi-phase or cross-session
task. Small, self-contained changes do not need a plan directory. A reusable
example lives at `.agents/plans/_template/`; copy or rename it to
`.agents/plans/<plan-name>/` for actual work.

Use one directory per plan: `.agents/plans/<plan-name>/`. Keep the goal,
decisions, constraints and overall status in `00-context.md`; agents read that
file first and then only the active phase file. Target stable paths, symbols and
behaviour rather than relying on line numbers.

When `plan-search` or `plan-implementer` is available, delegate with the plan
directory and active phase path; each agent reads `00-context.md` first. Those
agents do not depend on this directory convention: without it, supply
equivalent plan context and the active phase in the delegation prompt or other
named files.

The context plan may begin with `Status: draft`. Phase progress uses `pending`,
`in_progress`, `verified`, `blocked`, and optionally `committed`; `draft` is not
a phase state. Verification and commit are distinct. Record a commit hash only
after the commit exists.

Move durable project knowledge to `AGENTS.md` or a genuinely reusable skill.
Archive or delete completed plans when Git history is sufficient.
