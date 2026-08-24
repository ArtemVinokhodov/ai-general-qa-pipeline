# Skill: verification

## Purpose

Execute the checks across applicable layers (UI, API, Network, Logs, DB) using
whatever safe access exists — directly when tooling permits, or as a QA copilot
(human-in-the-loop) when it does not — and record a status + evidence per check.

## When used

During `/gqa test` (after test-design) and during `/gqa retest` re-execution.

## Inputs

- Checks with oracles and Verification Scope
- Project Profile (QA Access section)
- Available tools in the session (browser, API client, shell, etc.)
- Evidence supplied by the human QA

## Outputs

- Per check: Status (PASS | FAIL | BLOCKED | NEEDS_VERIFICATION) + Evidence
- Evidence references recorded in the QA work artifact

## Rules

1. **Never fake runtime testing.** PASS is written only with sufficient evidence
   of conformance. "Expected behavior looks logical" is NOT evidence. No live
   access to the product → checks stay NEEDS_VERIFICATION (insufficient data) or
   BLOCKED (environment/access/data/dependency prevents execution).
2. **Human-in-the-loop mode** when direct execution is impossible: (a) give the
   QA one concrete action to perform; (b) receive the factual observed result;
   (c) record it as evidence; (d) only then set the status. Never skip (b).
3. Statuses: PASS = sufficient evidence of match; FAIL = sufficient evidence of
   mismatch; BLOCKED = cannot execute (environment/access/data/dependency);
   NEEDS_VERIFICATION = not enough data to decide. No other statuses.
4. FAIL without evidence is invalid. Evidence not sufficient → NEEDS_VERIFICATION.
5. Evidence = observed UI behavior, screenshot/video reference, network
   request/response, API request/response, console/log output, DB query result
   supplied by QA, Jira attachment, command output. Store a short description +
   reference/path/link, not binary copies.
6. Only use safe, already-existing access. Never build DB/log infrastructure.
   DB access is read-only. No destructive actions on shared environments without
   the user explicitly confirming.
7. Do not verify layers marked N/A or UNAVAILABLE; escalate to ONLY_ON_FAILURE
   layers only when a check fails and diagnosis needs them.
8. Never persist secrets seen in requests/responses (auth headers, tokens,
   cookies) into the artifact; record `<REDACTED>`.

## Failure conditions

- Tool errors or environment down → mark affected checks BLOCKED with the reason.
- Human QA provides no result for a requested action → the check stays
  NEEDS_VERIFICATION; never substitute an assumed result.

## Stop conditions

Stop when every check in scope has a status + evidence (or an explicit
BLOCKED/NEEDS_VERIFICATION reason). Analysis of failures belongs to
defect-analysis.
