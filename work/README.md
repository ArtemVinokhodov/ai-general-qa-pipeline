# work/

Saved QA work artifacts: `work/<project>/<ticket-or-readable-title>.md`,
one file per QA work, format `templates/qa-work.md`.

Validate: `node scripts/gqa.js validate`
Search:   `node scripts/gqa.js find <query>`
List:     `node scripts/gqa.js list [--open]`

Binary evidence (screenshots, videos, HAR files) is git-ignored here —
artifacts store references, not binaries. For private work use
`work/_local/…` (git-ignored).
