# Skill: task-context

## Purpose

Turn a raw source (Jira text/ID, Slack message, plain text, local file, requirement
fragment, bug description) into a faithful, structured task context: source record,
atomic requirements, unknowns, ambiguities.

## When used

First step of every `/gqa plan`, `/gqa test`. Also when a follow-up message adds new
source information to an active QA work.

## Inputs

- Raw source (text, file path, or ticket reference)
- Active Project Profile (`projects/<project>/PROJECT_CONTEXT.md`), may be minimal

## Outputs

- `Source` section: original text preserved or faithfully referenced
- `Requirements`: REQ-NNN list — atomic, verifiable, traceable to the source
- `Unknowns / Ambiguities`: UNKNOWN / AMBIGUITY / ASSUMPTION entries

## Rules

1. **Source fidelity is mandatory.** Preserve exactly: numbers, limits, roles,
   permissions, states, platforms, environments, conditions, acceptance criteria,
   expected behavior, exclusions. Never "improve" product requirements.
2. Missing information → `UNKNOWN / NOT SPECIFIED`. Never fill gaps from general
   product knowledge.
3. Two source parts contradict each other → `AMBIGUITY` (quote both). Never pick
   one interpretation silently.
4. QA assumptions are labeled `ASSUMPTION` and never promoted to requirements.
5. Requirements must be few and real. 3 confirmed requirements + 2 unknowns beats
   15 invented ones. Weak source → few requirements, more unknowns.
6. **Fidelity self-check (short, not a document):** before handing off to test
   design, re-read the source once and answer: "Did any requirement change the
   source's meaning? Did I add a detail the source does not contain?" Fix or
   demote to ASSUMPTION anything that fails.
7. If the source contains potential secrets (tokens, passwords, keys, cookies,
   auth headers), do NOT copy them into any persistent artifact; replace with
   `<REDACTED>` and warn the user.

## Failure conditions

- Source is empty or cannot be read → report it; do not proceed on guesses.
- Ticket ID given but no access to the tracker → ask the user to paste the text.

## Stop conditions

Stop when Source, Requirements and Unknowns/Ambiguities are recorded and the
fidelity self-check passed. Do not design tests here.
