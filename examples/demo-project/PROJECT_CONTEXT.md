# Project Context: Account Portal (SYNTHETIC DEMO)

<!-- Fully synthetic demo project. No real company, product or user data. -->

## Product

- Name: Account Portal
- Purpose: A demo web portal where a user manages their account profile.

## Environments

- demo: https://account-portal.example.test — synthetic, not a real deployment

## Areas / Modules

- Profile — view and edit profile fields (email, name)
- Auth — login/logout (out of demo scope)

## User Roles

- User — manages own profile
- Admin — UNKNOWN

## Integrations

- Email delivery service — confirmation emails (behavior UNKNOWN in demo)

## Business Rules That Matter for QA

- Email must be a valid email address.
- Behavior for duplicate email: NOT SPECIFIED (intentional demo gap).

## QA Access

- UI access: YES (synthetic)
- API access: UNKNOWN
- Network inspection: YES (browser DevTools)
- Logs: NO
- DB: NO
- Test data: synthetic demo accounts; credentials live in the team secret store (never here)

## Conventions

- Jira project / ticket prefix: ACC-
- Bug report format: use pipeline default
- Severity rules: use pipeline default
- Slack/report style: use pipeline default

## Known Risks / Constraints

- Demo environment is synthetic; no real runtime verification is possible.
