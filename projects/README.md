# projects/

One directory per connected product: `projects/<project-name>/PROJECT_CONTEXT.md`.

Create it with `/gqa setup <project-name>` or by copying
`templates/project-context.md`. Keep it small; unknown fields stay UNKNOWN.
Never store secrets here.

Two modes (choose per project):

- **Tracked team data** — commit the profile so the team shares it.
- **Local/private data** — put the project under `projects/_local/<name>/`;
  that path is git-ignored.
