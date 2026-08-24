# Usage Guide

Practical, end-to-end. All examples use the synthetic demo product
(Account Portal) — see `examples/demo-project/`.

## New project

```
/gqa setup demo
```

Claude checks `projects/demo/PROJECT_CONTEXT.md`. If missing, it creates a
minimal profile and asks only for: product name, purpose, environments, what QA
access exists (UI/API/network/logs/DB). Answer "unknown" freely — fields stay
UNKNOWN and get filled in later during real work. Credentials never go into the
profile; reference your team's secret store instead.

## Small bug

```
/gqa test Save button remains disabled after entering valid profile data.
```

Expected behavior: Claude records the source verbatim, extracts the one real
requirement, lists unknowns (which fields? which browser?), produces 2–3 atomic
checks with oracles, sets verification scope (UI: APPLICABLE, API: N/A, ...),
and — because it cannot invent runtime results — either drives your browser (if
tooling is connected) or switches to human-in-the-loop. No formal test cases
for a small bug; a checklist is enough.

## Feature planning

```
/gqa plan Authenticated user can update their profile email. The new email must be a valid email address. After save, the profile page shows the updated email.
```

Paste the ticket/requirement text directly, or pass a path to a local .md/.txt
file containing it (the synthetic version of this source is quoted in
`examples/demo-project/work/ACC-101-update-profile-email.md`). You get: requirements, unknowns/ambiguities,
risks, a checklist, expected verification layers, regression considerations —
but **no runtime verification**. Later run `/gqa test ACC-101` to execute.

## Runtime testing (human-in-the-loop)

When Claude has no direct access to the product:

1. Claude: "Action: open the profile page, change the email to
   `qa.demo+1@example.test`, press Save. What do you observe? Does the button
   enable? What does the Network tab show for the save request?"
2. You reply with the factual result (and optionally paste a screenshot path or
   response body — strip auth headers).
3. Claude records it as evidence and only then sets PASS/FAIL.

If you don't supply a result, the check stays NEEDS_VERIFICATION. Claude never
writes PASS because the expected behavior "looks logical".

## Retest

```
/gqa retest ACC-101
```

or by keywords: `/gqa retest email validation`. Claude finds the saved work
(`python scripts/gqa.py find ...` under the hood), restores the failing check and
its reproduction, re-verifies it, runs a small justified regression scope, and
appends a `### Retest <date>` entry to the same artifact. One confident match →
used; several → you pick from a list; none → it says so.

## Review

```
/gqa review ACC-101
```

Read-only audit of a QA work: requirement coverage, missing checks, weak
evidence, FAIL without evidence, unresolved ambiguities, blocked items,
duplicate findings, retest state, verdict consistency. Nothing is modified.

## Automation handoff

```
/gqa handoff ACC-101
```

Writes `handoffs/demo-ACC-101-automation.md`: confirmed requirements, only the
checks that qualify as automation candidates (deterministic oracle, regression
value, manual verification result, evidence refs), test-data assumptions, and
an explicit "not included" list. No framework code — the automation repo
decides implementation.

## Follow-ups inside an active QA work

After `/gqa test` or `/gqa review` you can just type:

- "Сделай Jira bug из DEF-001."
- "Make a short Slack update."
- "Подготовь verification comment."

No new `/gqa` call needed.

## Deterministic tooling

```bash
python scripts/gqa.py validate
```

```bash
python scripts/gqa.py find payment timeout
```

```bash
python scripts/gqa.py list --open
```

The validator rejects: invalid statuses, PASS/FAIL without evidence, duplicate
IDs, defects referencing missing findings, invalid retest results, verdicts
inconsistent with check counts, and secret-looking strings.
