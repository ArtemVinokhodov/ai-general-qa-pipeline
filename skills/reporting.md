# Skill: reporting

## Purpose

Close a QA work: coverage review, final verdict, persistence of the artifact,
and on request — user-facing outputs (Jira comment/bug, Slack update, QA
summary, automation handoff).

## When used

Final stage of `/gqa test` and `/gqa retest`; all of `/gqa review` (read-only)
and `/gqa handoff`; follow-ups like "make a short Slack update".

## Inputs

- The in-progress or saved QA work artifact
- Project Profile (formats, terminology) — optional overrides

## Outputs

- `Final Verdict` block per `templates/qa-summary.md` (short, not a report)
- Saved artifact at `work/<project>/<ticket-or-readable-title>.md`, validated by
  `node scripts/gqa.js validate <path>`
- On request: Jira bug/comment, Slack update, QA summary, retest/regression
  summary, automation handoff at `handoffs/<project>-<task>-automation.md`

## Rules

1. **Coverage review checklist:** every confirmed requirement has ≥1 check;
   every critical risk is verified or explicitly marked not covered; failing
   checks have evidence; blocked/not-verified checks are visible; ambiguities
   are not silently turned into PASS; defects link to findings; retest did not
   lose the original failure. Coverage = QA coverage, not automation coverage.
2. Verdict values: PASS | FAIL | BLOCKED | NEEDS_VERIFICATION. Recommendation
   (READY | NOT_READY | NEEDS_VERIFICATION) only if available evidence supports
   it. Any FAIL check → verdict cannot be PASS. Open NEEDS_VERIFICATION/BLOCKED
   checks → verdict cannot be PASS.
3. One QA work = ONE small Markdown artifact. No file-per-section sprawl.
   Always run the deterministic validator after saving; fix reported errors.
4. `/gqa review` is read-only: report requirement coverage gaps, missing checks,
   weak evidence, FAIL without evidence, unresolved ambiguities, blocked items,
   duplicate/related findings, retest state, verdict consistency — without
   modifying the artifact unless the user explicitly asks.
5. **Automation candidates:** only for checks that scored well on repeatability,
   stability, regression value, deterministic oracle, execution cost, data
   dependency — never one per check. Candidates must be based on already-run,
   understood checks (manual verification result included).
6. **Automation handoff** (`templates/automation-handoff.md`): framework-
   agnostic; no Playwright/Selenium/Cypress code, no Page Objects, no framework
   structure. Include only qualifying candidates and explicitly list rejected
   ones. Handoff is optional downstream output — the pipeline never depends on
   an automation repository existing.
7. Outputs follow Project Profile formats when defined, generic templates
   otherwise. Never include secrets in any output.

## Failure conditions

- Validator rejects the artifact → fix before declaring the work saved.
- Verdict/recommendation not supported by evidence → downgrade to
  NEEDS_VERIFICATION and say why.

## Stop conditions

Stop when the artifact is saved and valid, and the requested outputs are
delivered as chat text or files.
