# QA Work: <short readable title>

<!--
One QA work = one file. Path: work/<project>/<ticket-or-readable-title>.md
Keep it small. Machine-validated by: node scripts/gqa.js validate
Section headers, ID formats (REQ-/CHK-/FIND-/DEF-NNN) and "- Key: value" lines
are part of the contract — do not rename them.
-->

## Metadata

- Project: <project-name>
- Source ref: <Jira ID / link / "plain text" / file path>
- Created: <YYYY-MM-DD>
- Type: <plan | test | retest>

## Source

<Original source text or a faithful reference to it. Do not rewrite meaning.>

## Requirements

- REQ-001: <atomic, verifiable requirement taken from the source>
- REQ-002: <...>

## Unknowns / Ambiguities

- UNKNOWN: <what is not specified by the source>
- AMBIGUITY: <which parts of the source conflict and how>
- ASSUMPTION: <QA assumption; never treated as a product requirement>

## Risks

- <risk> — <why it matters for this task>

## Verification Scope

- UI: <APPLICABLE | N/A | ONLY_ON_FAILURE | UNAVAILABLE>
- API: <...>
- Network: <...>
- Logs: <...>
- DB: <...>

## Checks

### CHK-001: <one atomic verification>

- Requirement: REQ-001
- Oracle: <how PASS vs FAIL is decided>
- Status: <PASS | FAIL | BLOCKED | NEEDS_VERIFICATION>
- Evidence: <short description + reference/path/link; required for PASS and FAIL>
- Notes: <optional>

## Findings

### FIND-001: <observed problem or notable deviation>

- Observed: <what actually happened>
- Evidence: <reference>
- Related checks: CHK-001

## Defects

### DEF-001: <defect title>

- Classification: <PRODUCT_DEFECT | REQUIREMENT_AMBIGUITY | ENVIRONMENT | TEST_DATA | AGENT_FALSE_POSITIVE | UNKNOWN>
- Findings: FIND-001
- Status: <OPEN | FIXED_PENDING_RETEST | VERIFIED | REJECTED>
- Notes: <root-cause reasoning, dedup reasoning>

## Regression

- Scope rationale: <why these regression checks, one or two lines>
- <regression check> — <status>

## Retest History

### Retest <YYYY-MM-DD>

- Trigger: <e.g. "dev reports DEF-001 fixed">
- Rechecked: CHK-001
- Result: <FIX_VERIFIED | STILL_FAILING | BLOCKED | NEEDS_VERIFICATION>
- Evidence: <required for FIX_VERIFIED and STILL_FAILING>
- Regression: <what was rechecked around the fix, results>

## Automation Candidates

- <check reference + why it is a good candidate + recommended layer> (or "None")

## Final Verdict

- Verdict: <PASS | FAIL | BLOCKED | NEEDS_VERIFICATION>
- Requirements covered: <N of M>
- Checks: PASS <n> / FAIL <n> / BLOCKED <n> / NEEDS_VERIFICATION <n>
- Unique defects: <n>
- Not verified: <list or "none">
- Recommendation: <READY | NOT_READY | NEEDS_VERIFICATION>
