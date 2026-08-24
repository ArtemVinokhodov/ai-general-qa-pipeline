# Automation Handoff: <project> — <task>

<!--
Path: handoffs/<project>-<task>-automation.md
Framework-agnostic. No Playwright/Selenium/Cypress code, no Page Objects,
no test framework structure. The automation repository decides implementation.
Only include checks that qualify as automation candidates — not every check.
-->

## Source

- Task: <Jira ID / title>
- QA work: <path to the QA work artifact>

## Confirmed Requirements (relevant to automation)

- REQ-00X: <requirement>

## Automation Candidates

### Candidate 1: <check title>

- Check: <the verification, in one sentence>
- Oracle: <deterministic PASS/FAIL condition>
- Reason: <why automate — repeatability / regression value / stability>
- Recommended layer: <API | UI | other>
- Priority: <Regression | Smoke | ...>
- Manual verification: <PASS/FAIL + date>
- Evidence: <reference>

## Test Data Assumptions

- <data the scenario depends on; UNKNOWN where not specified>

## Risks / Notes

- <flakiness risks, environment dependencies, out-of-scope notes>

## Explicitly NOT Included

- <checks reviewed but rejected as candidates, with one-line reason>
