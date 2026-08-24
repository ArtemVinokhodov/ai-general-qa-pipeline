# Project Context: <product name>

<!--
Minimal viable profile = Product name + Purpose + Environments + Available QA access.
Everything else can start as UNKNOWN and be filled in gradually while working.
Never store secrets here (passwords, tokens, keys, cookies).
-->

## Product

- Name: <name>
- Purpose: <one or two sentences>

## Environments

- <env name>: <URL or "UNKNOWN"> — <notes: test data, resets, restrictions>

## Areas / Modules

- <module> — <one line> (or UNKNOWN)

## User Roles

- <role> — <what it can do> (or UNKNOWN)

## Integrations

- <external system> — <what it is used for> (or UNKNOWN)

## Business Rules That Matter for QA

- <rule> (or UNKNOWN)

## QA Access

- UI access: <YES / NO / notes>
- API access: <YES / NO / how — e.g. Postman collection, Swagger>
- Network inspection: <YES / NO / how — e.g. browser DevTools>
- Logs: <YES / NO / where>
- DB: <YES read-only / NO / how>
- Test data: <how to get accounts/data; no credentials here — reference the team's secret store instead>

## Conventions

- Jira project / ticket prefix: <e.g. ABC- or UNKNOWN>
- Bug report format: <link/notes or "use pipeline default">
- Severity rules: <notes or "use pipeline default">
- Slack/report style: <notes or "use pipeline default">

## Known Risks / Constraints

- <project-specific risk or constraint> (or UNKNOWN)
