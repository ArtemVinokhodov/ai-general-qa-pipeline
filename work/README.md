# work/

Saved QA work artifacts: `work/<project>/<ticket-or-readable-title>.md`,
one file per QA work, format `templates/qa-work.md`.

Validate: `python scripts/gqa.py validate`
Search:   `python scripts/gqa.py find <query>`
List:     `python scripts/gqa.py list [--open]`

Binary evidence (screenshots, videos, HAR files) is git-ignored here —
artifacts store references, not binaries. For private work use
`work/_local/…` (git-ignored).
