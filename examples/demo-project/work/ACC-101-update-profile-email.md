# QA Work: ACC-101 — User can update profile email

<!-- SYNTHETIC DEMO ARTIFACT. All evidence below is fabricated for workflow
demonstration and does not represent real testing. -->

## Metadata

- Project: demo-project
- Source ref: ACC-101 (synthetic ticket text pasted below)
- Created: 2026-08-20
- Type: test

## Source

> Authenticated user can update their profile email. The new email must be a
> valid email address. After save, the profile page shows the updated email.
> Note A: "the email change applies immediately after save".
> Note B: "the email change takes effect only after the user confirms it via a
> confirmation link".
> Duplicate email behavior: not described.

## Requirements

- REQ-001: An authenticated user can update their profile email.
- REQ-002: The new email must be a valid email address.
- REQ-003: After save, the profile page shows the updated email.

## Unknowns / Ambiguities

- UNKNOWN: Behavior when the new email already belongs to another account is NOT SPECIFIED.
- AMBIGUITY: Note A says the change applies immediately after save; Note B says it takes effect only after confirmation via link. These conflict — needs owner clarification before an expected result can exist for "when the change takes effect".

## Risks

- Invalid email accepted → broken notifications/login recovery for the user.
- Email update not persisted after refresh → silent data loss.
- Duplicate email allowed → account identity conflicts (unspecified area).

## Verification Scope

- UI: APPLICABLE
- API: UNAVAILABLE
- Network: APPLICABLE
- Logs: UNAVAILABLE
- DB: UNAVAILABLE

## Checks

### CHK-001: Valid email update persists

- Requirement: REQ-001, REQ-003
- Oracle: After entering a valid new email and saving, the profile page shows the new email, and it is still shown after page refresh.
- Status: PASS
- Evidence: SYNTHETIC — observed UI: profile shows new email after save and after refresh; network tab shows save request completed with HTTP 200 (screenshot ref: evidence/acc-101-chk001.png).

### CHK-002: Invalid email is rejected

- Requirement: REQ-002
- Oracle: Saving "not-an-email" is rejected with a validation message and the stored email does not change.
- Status: PASS
- Evidence: SYNTHETIC — retest 2026-08-24: validation message shown, save request not sent, stored email unchanged after refresh (screenshot ref: evidence/acc-101-chk002-retest.png). Originally FAILED on 2026-08-20 — see DEF-001 and Retest History.

### CHK-003: Duplicate email behavior

- Requirement: -
- Oracle: NOT SPECIFIED by source — cannot define PASS/FAIL until the owner clarifies expected behavior for duplicate emails.
- Status: NEEDS_VERIFICATION
- Evidence: -
- Notes: Clarification question sent to product owner; not a testable check yet.

## Findings

### FIND-001: Invalid email was accepted and saved

- Observed: On 2026-08-20, entering "not-an-email" and saving showed no validation error; profile displayed "not-an-email" after refresh.
- Evidence: SYNTHETIC — screenshot ref: evidence/acc-101-find001.png; save request returned HTTP 200 with the invalid value.
- Related checks: CHK-002

## Defects

### DEF-001: Email validation missing on profile save

- Classification: PRODUCT_DEFECT
- Findings: FIND-001
- Status: VERIFIED
- Notes: Single root problem — client/server validation absent for the email field. Fixed by dev on 2026-08-23; fix verified on retest 2026-08-24.

## Regression

- Scope rationale: fix touched profile-save validation, so adjacent save behavior (valid email flow) was rechecked.
- Valid email update still persists (re-ran CHK-001 flow) — PASS (SYNTHETIC evidence: evidence/acc-101-regression.png)

## Retest History

### Retest 2026-08-24

- Trigger: developer reported DEF-001 fixed in build 1.4.2
- Rechecked: CHK-002
- Result: FIX_VERIFIED
- Evidence: SYNTHETIC — validation message now shown for "not-an-email", no save request issued, stored email unchanged (screenshot ref: evidence/acc-101-chk002-retest.png).
- Regression: re-ran valid-email save flow (CHK-001) — PASS.

## Automation Candidates

- CHK-002 (invalid email rejected): deterministic oracle, stable regression scenario, low data dependency. Recommended layer: API if it becomes available, otherwise UI. CHK-003 is NOT a candidate (expected behavior unspecified).

## Final Verdict

- Verdict: NEEDS_VERIFICATION
- Requirements covered: 3 of 3
- Checks: PASS 2 / FAIL 0 / BLOCKED 0 / NEEDS_VERIFICATION 1
- Unique defects: 1 (verified fixed)
- Not verified: CHK-003 (duplicate email — requirement not specified); timing-of-change ambiguity unresolved
- Recommendation: NEEDS_VERIFICATION
