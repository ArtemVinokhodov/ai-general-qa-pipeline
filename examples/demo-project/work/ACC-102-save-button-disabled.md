# QA Work: ACC-102 — Save button remains disabled after entering valid data

<!-- SYNTHETIC DEMO ARTIFACT. Demonstrates the no-fake-runtime-testing rule:
no live product is available, so no check gets an invented PASS/FAIL. -->

## Metadata

- Project: demo-project
- Source ref: plain text bug report (pasted below)
- Created: 2026-08-24
- Type: test

## Source

> Save button remains disabled after entering valid profile data.

## Requirements

- REQ-001: The Save button becomes enabled once the profile form contains valid data.

## Unknowns / Ambiguities

- UNKNOWN: Which fields must be valid/changed for Save to enable is NOT SPECIFIED.
- UNKNOWN: Affected browser/platform is NOT SPECIFIED.
- ASSUMPTION: "valid profile data" includes at least a valid email — assumption for reproduction only, not a requirement.

## Risks

- Users cannot save any profile change → core flow broken.
- Enable-state logic may depend on per-field validation events → may reproduce only for specific fields.

## Verification Scope

- UI: APPLICABLE
- API: N/A
- Network: ONLY_ON_FAILURE
- Logs: UNAVAILABLE
- DB: N/A

## Checks

### CHK-001: Save enables after valid input

- Requirement: REQ-001
- Oracle: After changing a profile field to a valid value, the Save button becomes enabled (clickable, not visually disabled).
- Status: NEEDS_VERIFICATION
- Evidence: -
- Notes: No live product access in this session. Human QA action requested: open profile, change email to a valid new value, report the button state. Awaiting the observed result.

### CHK-002: Reproduce with reporter's flow

- Requirement: REQ-001
- Oracle: Following the reporter's exact steps, the Save button state matches/doesn't match the reported "stays disabled" behavior.
- Status: BLOCKED
- Evidence: -
- Notes: Reporter's exact steps and environment are unknown; blocked on that information.

## Findings

## Defects

## Regression

- Scope rationale: none until the failure is reproduced.

## Retest History

## Automation Candidates

- None (behavior not confirmed yet).

## Final Verdict

- Verdict: NEEDS_VERIFICATION
- Requirements covered: 1 of 1
- Checks: PASS 0 / FAIL 0 / BLOCKED 1 / NEEDS_VERIFICATION 1
- Unique defects: 0
- Not verified: CHK-001 (awaiting human QA result), CHK-002 (blocked on reporter's steps)
- Recommendation: NEEDS_VERIFICATION
