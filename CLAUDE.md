# AI General QA Pipeline — agent instructions

This repository is a standalone, portable AI-assisted General QA workspace.
It is NOT an automation framework and NOT tied to any product.

## Entry point

The pipeline activates ONLY via the `/gqa` command
(`.claude/commands/gqa.md`): `plan | test | retest | review | handoff | setup`.
Ordinary chat messages must NOT start QA work. After `/gqa` activates a QA
work, normal follow-ups continue it.

## Binding contracts

- Skills in `skills/*.md` are binding contracts, not suggestions:
  task-context, test-design, verification, defect-analysis,
  retest-regression, reporting.
- Artifact format: `templates/qa-work.md`. One QA work = one file at
  `work/<project>/<ticket-or-readable-title>.md`.
- Deterministic guardrails: `python scripts/gqa.py validate|find|list`.
  Always validate an artifact after saving it.

## Non-negotiable rules

1. **Source fidelity** — never "improve" requirements; missing info =
   UNKNOWN / NOT SPECIFIED; conflicts = AMBIGUITY; assumptions = ASSUMPTION.
2. **Never fake runtime testing** — PASS/FAIL only with evidence; no live
   access → NEEDS_VERIFICATION or BLOCKED.
3. **No secrets** in any persistent file (passwords, tokens, keys, cookies,
   auth headers). Redact and warn.
4. **Core stays portable** — no product URLs, Jira prefixes, roles, endpoints
   or company names in skills/templates/commands; project specifics live only
   in `projects/<name>/PROJECT_CONTEXT.md`.
5. Statuses: checks PASS|FAIL|BLOCKED|NEEDS_VERIFICATION; retests
   FIX_VERIFIED|STILL_FAILING|BLOCKED|NEEDS_VERIFICATION. Do not extend.
6. No destructive actions on shared environments; DB access read-only.
