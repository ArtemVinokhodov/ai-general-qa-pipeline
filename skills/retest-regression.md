# Skill: retest-regression

## Purpose

Re-verify a previously failed check after a fix, run a small risk-based
regression scope around the fix, and append the result to the SAME QA work
artifact.

## When used

`/gqa retest <query>`. Also supplies regression-scope logic to `/gqa test` for
changes with regression risk.

## Inputs

- Query (Jira ID, title, keywords, source fragment)
- Saved QA work found via `python scripts/gqa.py find <query>` (or user-provided path)

## Outputs

- A new `### Retest <date>` entry in the existing artifact's Retest History
- Updated check statuses and defect status (e.g. OPEN → VERIFIED)
- Updated Final Verdict

## Rules

1. **Find, don't duplicate.** Locate the previous QA work by Jira ID / title /
   keywords / source fragment. Exactly one confident match → use it. Several →
   show the list and ask; never guess. None → say no saved context exists and
   offer to start a fresh `/gqa test`.
2. Restore from the artifact: the original failing check, reproduction, expected
   result, actual result, evidence, related defect. Do not re-derive them from
   memory.
3. Re-execute the original failing verification via the `verification` skill
   (same evidence rules; human-in-the-loop where needed).
4. Retest statuses: FIX_VERIFIED | STILL_FAILING | BLOCKED | NEEDS_VERIFICATION.
   **FIX_VERIFIED without evidence is forbidden.**
5. On FIX_VERIFIED, update the original check to PASS (with the new evidence)
   and the defect to VERIFIED; on STILL_FAILING the check stays FAIL with fresh
   evidence.
6. **Regression scope is risk-based, small, and explained.** Derive from:
   changed behavior, affected user flow, adjacent state transitions,
   roles/permissions, shared components, integrations, validation, data
   persistence, known defect area. State in one or two lines why these checks
   were chosen. Never turn a retest into full regression.
7. Append history; never create a copy of the QA work per retest.

## Failure conditions

- Found artifact fails `validate` → tell the user; fix structure only with
  their confirmation before appending.
- Environment prevents re-execution → Retest result BLOCKED with reason.

## Stop conditions

Stop when the retest entry, updated statuses and updated verdict are saved and
the artifact validates.
