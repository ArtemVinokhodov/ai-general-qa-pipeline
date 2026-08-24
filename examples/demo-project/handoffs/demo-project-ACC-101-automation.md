# Automation Handoff: demo-project — ACC-101 (SYNTHETIC DEMO)

## Source

- Task: ACC-101 — User can update profile email
- QA work: examples/demo-project/work/ACC-101-update-profile-email.md

## Confirmed Requirements (relevant to automation)

- REQ-002: The new email must be a valid email address.
- REQ-003: After save, the profile page shows the updated email.

## Automation Candidates

### Candidate 1: Invalid email is rejected

- Check: Saving an invalid email ("not-an-email") is rejected with a validation message and the stored email does not change.
- Oracle: Validation message shown; no save request issued; stored email unchanged after refresh.
- Reason: Deterministic result, stable regression scenario (regressed once already — DEF-001), low data dependency.
- Recommended layer: API if it becomes available; otherwise UI.
- Priority: Regression
- Manual verification: PASS (retest 2026-08-24)
- Evidence: SYNTHETIC — evidence/acc-101-chk002-retest.png

## Test Data Assumptions

- One authenticated demo user with an editable profile. Duplicate-email data behavior: UNKNOWN (requirement not specified).

## Risks / Notes

- Timing-of-change ambiguity (immediate vs confirmation link) is unresolved; do not automate the "when the change takes effect" behavior until clarified.

## Explicitly NOT Included

- CHK-003 (duplicate email): expected behavior NOT SPECIFIED — no deterministic oracle.
- Exploratory re-check of reporter flows: manual-only, non-deterministic steps.
