# Skill: defect-analysis

## Purpose

Turn verification results into findings, group related manifestations into
defects only when evidence supports it, classify defects, and produce
ready-to-file bug reports on request.

## When used

During `/gqa test` after verification finds failures; during `/gqa retest` when
new failures appear; on follow-ups like "make a Jira bug from DEF-001".

## Inputs

- Check results + evidence
- Requirements / ambiguities (for expected-result grounding)
- Project Profile (bug format, severity rules — if defined)

## Outputs

- `Findings`: FIND-NNN — observed problems/deviations with evidence
- `Defects`: DEF-NNN — classified, linked to findings
- Bug report text (generic template or project-specific format) on request

## Rules

1. A finding is an observed problem; it is not automatically a separate bug.
2. **Grouping:** link findings to one defect only when evidence supports one
   root problem — same trigger, same affected area, same failing request, same
   underlying state, or one defect explaining several symptoms. Do NOT merge
   findings just because they occurred at the same time. Unclear → keep separate
   and mark UNKNOWN / NEEDS_VERIFICATION.
3. Classification set (do not extend without real need): PRODUCT_DEFECT,
   REQUIREMENT_AMBIGUITY, ENVIRONMENT, TEST_DATA, AGENT_FALSE_POSITIVE, UNKNOWN.
4. Before creating multiple bug reports, run the dedup questions from rule 2.
5. **Bug reports:** default fields per `templates/bug-report.md` (Summary,
   Description, Environment, Precondition, Steps, Actual, Expected, Evidence,
   Severity suggestion). Project Profile format overrides the default.
6. Expected Result must come from source/requirements. Not defined there →
   state the requirement ambiguity explicitly instead of inventing an ER.
7. Every defect must reference at least one finding; every FAIL-based finding
   must have evidence.

## Failure conditions

- FAIL check without evidence reaches this skill → send it back to
  NEEDS_VERIFICATION; do not build a defect on it.

## Stop conditions

Stop when findings and defects are recorded with classification and links.
Verdict math belongs to reporting.
