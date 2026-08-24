# AI General QA Pipeline (V1)

A standalone, portable AI-assisted workspace for General QA engineering.
Plug it into any project and run a repeatable QA workflow with Claude Code:
requirements → risks → checks → verification → findings → defects → retest →
regression → coverage → verdict → optional automation handoff.

**Prerequisite:** Python 3.10+ — required for the deterministic tooling
(`scripts/gqa.py validate | find | list`). Standard library only, no packages
to install.

## 1. Problem

Using an AI assistant for QA usually means re-explaining the rules every time:
how to treat requirements, when a check may be called PASS, how to write bugs,
how to retest. Results are inconsistent and nothing persists between sessions.

## 2. What this pipeline is

- An explicit entry point (`/gqa`) into a fixed, repeatable QA workflow.
- Internal skill contracts (`skills/*.md`) that govern every stage.
- One small Markdown artifact per QA work, searchable weeks later.
- Deterministic guardrails in code (`scripts/gqa.py`) that validate artifacts,
  find saved work, and list open work.
- Project-agnostic core + per-project profiles (`projects/<name>/PROJECT_CONTEXT.md`).

## 3. What it is NOT

Not an automation framework, not a Playwright/Selenium/Cypress wrapper, not a
reporting platform, not CI/CD, not a product-specific tool, not a replacement
for existing QA processes. It never writes automation tests — at most it hands
off framework-agnostic automation candidates.

## 4. Architecture

```
.claude/commands/gqa.md   ← single entry point, subcommand dispatcher
skills/                   ← 6 internal stage contracts (not user-invoked)
templates/                ← artifact / profile / bug / summary / handoff formats
scripts/gqa.py            ← deterministic validate | find | list (stdlib Python)
projects/<name>/          ← Project Profile (the only project-specific input)
work/<project>/           ← one Markdown artifact per QA work
handoffs/                 ← optional automation handoffs
examples/demo-project/    ← synthetic demo (Account Portal)
docs/USAGE.md             ← practical guide
```

AI reasoning (understanding requirements, risks, checks, findings) and
deterministic validation (structure, statuses, references, evidence presence,
secret patterns) are strictly separated.

## 5. General QA workflow

`/gqa test <source>` runs: task context (source fidelity, requirements,
unknowns/ambiguities) → risk-based test design (checks with oracles,
verification scope UI/API/Network/Logs/DB) → verification (direct where tools
allow, human-in-the-loop otherwise) → defect analysis (findings → grouped
defects) → coverage review → final verdict → saved artifact.

## 6. Project onboarding

`/gqa setup <project>` creates `projects/<project>/PROJECT_CONTEXT.md` from a
template, asking only the minimum (name, purpose, environments, QA access).
Everything else starts as UNKNOWN and grows while you work. The core never
hardcodes URLs, ticket prefixes, roles, endpoints or bug formats — the profile
supplies them.

## 7. /gqa commands

Daily: `/gqa plan <source>`, `/gqa test <source>`, `/gqa retest <query>`.
Advanced: `/gqa review <query>`, `/gqa handoff <query>`, `/gqa setup <project>`.
Plain chat never activates the pipeline; follow-ups inside an active QA work do
not need repeated `/gqa`.

## 8. Persistence

One QA work = one file: `work/<project>/<ticket-or-readable-title>.md`
(format: `templates/qa-work.md`). Internal IDs (REQ/CHK/FIND/DEF-NNN) exist for
traceability, but you search by Jira ID, title, keywords or source fragment:
`python scripts/gqa.py find payment timeout`.

Scope note: `find` and `list` search only real QA work under `work/`.
`examples/` is covered by `validate` but intentionally excluded from
operational search, so demo artifacts never appear in retest lookups or open
work lists.

## 9. Evidence rules

Statuses: PASS, FAIL, BLOCKED, NEEDS_VERIFICATION. PASS and FAIL require
evidence (observed behavior, screenshot/network/log/DB references). FAIL
without evidence is invalid — the validator rejects it. No live product access
→ NEEDS_VERIFICATION or BLOCKED, never an invented PASS.

## 10. Retest

`/gqa retest <query>` finds the saved work, restores the original failing
check, re-verifies it, runs a small regression scope around the fix, and
appends a Retest History entry to the SAME artifact. FIX_VERIFIED requires
evidence.

## 11. Regression

Regression scope is risk-based (changed behavior, affected flow, adjacent
states, roles, shared components, integrations, validation, persistence, known
defect area) and always briefly justified. A retest is never full regression.

## 12. Defect analysis

Findings (observed problems) are grouped into defects only when evidence
supports one root problem. Classification: PRODUCT_DEFECT,
REQUIREMENT_AMBIGUITY, ENVIRONMENT, TEST_DATA, AGENT_FALSE_POSITIVE, UNKNOWN.
Bug reports use the project's format or the generic template; Expected Result
is never invented.

## 13. Automation handoff

`/gqa handoff <query>` writes a framework-agnostic Markdown handoff with only
qualifying candidates (deterministic oracle, regression value, stability). No
framework code, no Page Objects. The automation repository decides everything
about implementation. The pipeline works fine if no automation repo exists.

## 14. Security

No secrets in any persistent file — that is the primary rule. The validator
additionally scans artifacts for common secret patterns (tokens, keys, JWTs,
passwords) and rejects matches, but this regex detection is a **best-effort
guardrail, NOT a security boundary**: it will miss secrets it has no pattern
for. Never rely on it — simply do not put secrets into QA artifacts. Private
project data can live under `projects/_local/`, `work/_local/`,
`handoffs/_local/` — all git-ignored. Binary evidence under `work/` is
git-ignored; artifacts store references.

## 15. Known V1 limitations

- Search is keyword scoring, not semantic; very short queries can be noisy.
- The validator checks structure/consistency, not the truth of evidence.
- Secret-pattern scanning is best-effort only, not a security boundary; the
  real protection is the rule that secrets are never written into artifacts.
- Jira/Slack integration is manual (paste text in, copy output back) unless the
  session has connectors.
- Retest depends on the artifact being saved and reasonably titled.
- Verdict consistency rules are strict (any open check blocks a PASS verdict) —
  intentional, but occasionally requires explicitly closing checks as N/A by
  removing them with justification.
