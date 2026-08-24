# Skill: test-design

## Purpose

From requirements + risks produce a small, risk-based set of atomic checks with
oracles, decide the verification scope (UI/API/Network/Logs/DB applicability),
and decide whether formal test cases are justified.

## When used

After `task-context`, in both `/gqa plan` and `/gqa test`.

## Inputs

- Requirements, unknowns, ambiguities (from task-context)
- Project Profile (available access, known risks, modules, roles)

## Outputs

- `Risks`: each with a one-line "why it matters for this task"
- `Checks`: CHK-NNN list, each with Requirement link and Oracle
- `Verification Scope`: UI/API/Network/Logs/DB each set to
  APPLICABLE | N/A | ONLY_ON_FAILURE | UNAVAILABLE
- Formal test cases only when policy (below) demands them
- Regression considerations (for plan) / regression notes

## Rules

1. Risk-based, not generic. Use only relevant design ideas: positive/negative
   flows, boundaries, validation, state transitions, roles/permissions, data
   variations, error handling, integration behavior, retry, concurrency (only if
   relevant), regression risk, external-service dependency, persistence/refresh.
2. Every check must answer: "Why does this matter for THIS task?" Cut any check
   that only exists for completeness.
3. One check = one atomic verification with an explicit oracle ("how do I know
   PASS vs FAIL"). Bad: "Check campaign functionality." Good: "After selecting a
   valid campaign and saving, the selection persists after page refresh."
4. No near-duplicate checks for volume.
5. **Test case policy:** small bug/fix → checklist only. Medium change →
   requirements + risks + checklist. Large feature → add formal test cases only
   where they improve repeatability, traceability or communication. A formal
   test case has: Title, Preconditions, Test data, Steps, Expected result,
   Priority, Related requirement.
6. **Verification scope:** decide per layer from the nature of the change, not
   "all layers for completeness". Access missing per Project Profile →
   UNAVAILABLE. Layer useful only for diagnosis → ONLY_ON_FAILURE.
7. Checks for AMBIGUITY items are allowed only as "clarify with owner" items,
   never as checks with an invented expected result.

## Failure conditions

- No confirmed requirements and no clear observed-bug statement → produce
  clarification questions instead of a checklist.

## Stop conditions

Stop when checks + scope are recorded. Do not execute anything here.
