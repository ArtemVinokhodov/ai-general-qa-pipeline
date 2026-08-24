---
description: AI-assisted General QA Pipeline — plan | test | retest | review | handoff | setup
argument-hint: <plan|test|retest|review|handoff|setup> <source or query>
---

# /gqa — General QA Pipeline entry point

Arguments: `$ARGUMENTS`

You are now operating the General QA Pipeline. This is a controlled, repeatable
QA workflow — not ad-hoc chat assistance. Parse the first word of the arguments
as the subcommand; the rest is the source/query. No recognizable subcommand →
show the short usage below and stop.

## Global contract (applies to every subcommand)

1. Read the relevant `skills/*.md` files listed per subcommand and follow them
   as binding contracts.
2. Resolve the active project: explicit in the request → use it; exactly one
   profile in `projects/` → use it; several → ask which; none → offer
   `/gqa setup`. Load `projects/<project>/PROJECT_CONTEXT.md`. Missing profile
   info = UNKNOWN, never invented.
3. Source fidelity, evidence rules, statuses (PASS/FAIL/BLOCKED/
   NEEDS_VERIFICATION) and the no-fake-runtime-testing rule from the skills are
   non-negotiable.
4. Once a subcommand activates a QA work, normal follow-up messages continue
   that work ("make a Jira bug from DEF-001", "here is the screenshot", "make a
   Slack update") — no repeated `/gqa` needed.
5. Persistence: one artifact per QA work at
   `work/<project>/<ticket-or-readable-title>.md`, format `templates/qa-work.md`.
   After saving, run `python scripts/gqa.py validate <path>` and fix errors.
6. Never store secrets (passwords, tokens, keys, cookies, auth headers) in any
   artifact; redact and warn.

## Subcommands

### /gqa plan <source>
Preparation only — no runtime verification.
Skills: `task-context` → `test-design` → `reporting` (persist as Type: plan).
Deliver: source record, requirements, unknowns/ambiguities, risks, checklist
(+ formal test cases only if policy demands), expected verification layers,
regression considerations, automation candidates if any.

### /gqa test <source>
Full QA workflow.
Skills: `task-context` → `test-design` → `verification` → `defect-analysis`
(if failures) → `reporting`.
Where direct execution is impossible, run human-in-the-loop verification per
`skills/verification.md`. End with the short QA VERDICT block and save the
artifact.

### /gqa retest <query>
Skills: `retest-regression` (+ `verification`, `reporting`).
Find the saved work with `python scripts/gqa.py find <query>` — one confident
match: use it; several: list, don't guess; none: say so. Append Retest History
to the SAME artifact; never duplicate it.

### /gqa review <query>
Read-only. Skill: `reporting` (rule 4). Locate the work (find script), report
coverage gaps, weak evidence, inconsistencies. Do not modify the artifact.

### /gqa handoff <query>
Skill: `reporting` (rules 5–6). Locate the work, select qualifying automation
candidates only, write `handoffs/<project>-<task>-automation.md` from
`templates/automation-handoff.md`.

### /gqa setup <project>
1. If `projects/<project>/PROJECT_CONTEXT.md` exists — show a short summary and
   offer to extend it.
2. Otherwise create it from `templates/project-context.md`, asking only for the
   minimum (product name, purpose, environments, QA access); everything else
   starts as UNKNOWN and grows over time.
3. Never store secrets; point test-credential fields at the team's secret store.

## Usage (show on unknown/missing subcommand)

```
/gqa plan <source>      prepare testing (no runtime verification)
/gqa test <source>      full QA workflow with verification
/gqa retest <query>     re-verify a previous failure + small regression
/gqa review <query>     read-only review of a QA work
/gqa handoff <query>    framework-agnostic automation handoff
/gqa setup <project>    create/extend a Project Profile
```
