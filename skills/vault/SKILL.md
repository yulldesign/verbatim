---
name: vault
description: Shared data model and storage rules for the Verbatim research vault (Markdown folder or Notion) - note types, frontmatter schema, staging/review protocol, and the verbatim.py helper script. Load this before reading or writing any Verbatim note, and whenever another verbatim:* skill or agent needs to know where research data lives or how to propose a change. Not meant to be invoked on its own by the user.
user-invocable: false
---

# Verbatim vault - data model and storage protocol

Verbatim turns interview transcripts into a linked research knowledge base. Every other
verbatim:* skill relies on the rules below, so they stay consistent whichever backend
holds the data.

## 1. Find the configuration first

Read `verbatim.config.json` at the project root (walk up from the current directory).

```json
{
  "backend": "markdown",          // "markdown" or "notion"
  "vault_path": "vault",          // markdown only, relative to the config file
  "output_language": "auto",      // "auto" = language of the source, or "fr", "en"...
  "skip_review": false,           // true = apply proposals without asking (skip-review mode)
  "stale_days": 30,
  "taxonomy": ["pain-point", "feature-request", "..."],
  "notion": { "notes_data_source": "", "projects_data_source": "", "parent_page": "" }
}
```

If the file is missing, tell the user and suggest `/verbatim:setup`. Then read the
backend reference that applies - only that one:

- Markdown -> [references/backend-markdown.md](references/backend-markdown.md)
- Notion -> [references/backend-notion.md](references/backend-notion.md)

Exact note templates for every type are in [references/note-formats.md](references/note-formats.md).
Read it before you write a note.

## 2. Note types

| type | folder (markdown) | what it is | author |
|---|---|---|---|
| `transcript` | `raw/` | Original document, kept verbatim (the Library) | human |
| `source` | `sources/` | One summary per transcript: participant, company, profile, themes, key quote | verbatim |
| `insight` | `insights/` | One atomic finding with evidence quote, confidence, tags | verbatim |
| `synthesis` | `synthesis/` | Cross-interview pattern backed by 2+ sources (Themes) | verbatim |
| `query-output` | `queries/` | A saved answer from Query, with citations | verbatim |
| `project` | `projects/` | A filtered subset of the vault + activity log | human |

Links that make the graph:
- insight `source_ref` -> its source note; source `source_ref` -> its raw transcript
- `related: []` -> any other notes (synthesis -> supporting sources/insights, merged insight -> originals)
- `[[slug]]` wikilinks in the body (Obsidian-compatible; the slug is the file name without `.md`)

## 3. Frontmatter schema

```yaml
---
title: "Note title"
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
type: transcript | insight | source | query-output | synthesis | project
status: raw | processing | validated | final
tags: []
related: []
source_ref: ""
confidence: high | medium | low
author: human | verbatim
participant: ""
company: ""
---
```

Rules that prevent the bugs Verbatim hit in production:
- **Comma-separated people.** After a merge, `participant` and `company` may hold
  `"Alice Martin, Bob Dupont"`. Whenever you read these fields, split on `,` and trim.
- **Forward slashes only** in every path you store (`insights/foo.md`, never `insights\foo.md`).
- **Slugs** come from `verbatim.py slug "<title>"` (ASCII, lowercase, hyphens, 60 chars max). If the
  target file already exists, append `-2`, `-3`...
- **Tags** come from the `taxonomy` in the config. Add a new tag only when nothing fits, and say so.
- **Dates** are ISO `YYYY-MM-DD`, today's date for new notes.
- Write notes in `output_language` (or the language of the source when `auto`). Quotes stay verbatim
  in the participant's language.

## 4. Never write to the vault directly - stage, review, apply

Verbatim's core promise is that the AI never changes the knowledge base without the
researcher's consent. The staging area is that gate.

1. `python <script> staging new --kind <ingest|synthesis|merge|tags|query|health|canvas|project> --label "<label>"`
   prints a job folder such as `.verbatim/staging/20261104-101500-ingest-interview-marie/`.
2. Write every proposed note into `<job>/files/<vault-relative-path>` (e.g. `files/insights/slow-export.md`),
   exactly as it should land in the vault. To propose a deletion, add the vault-relative
   path as a line in `<job>/delete.txt`.
3. `python <script> staging seal <job-id>` builds the manifest (create / modify / delete) and warns about
   missing frontmatter.
4. Present the proposal (see the `verbatim:review` skill), then `staging apply <job-id>` with
   optional `--only` / `--exclude` paths, or `staging refuse`.

Deletions are never hard deletes: `apply` moves the files to `.verbatim/trash/<timestamp>/`.
After an apply the script rebuilds `graph/index.md`, which is derived data: regenerated, never edited by hand.

When `skip_review` is `true` in the config, or the user explicitly said to skip review for this run,
you may apply right after sealing - still show a summary of what was written.

Subagents only stage. Applying is the main conversation's job, because only it can ask the user.

## 5. The helper script

`<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"` (run from the project root, or
anywhere below it - it finds `verbatim.config.json` itself; on macOS/Linux use `python3` if `python` is not
found). Python 3.9+, standard library only. Prefer it to doing these by hand: it is
exact, fast and does not spend tokens.

| Command | Use it for |
|---|---|
| `init [path]` | Create the vault folders, `VERBATIM.md` (stable vault_id) and `graph/index.md` |
| `stats [--json]` | Counts by type, people, companies, tags, pending reviews |
| `scan [--type T ...] [--grep REGEX] [--full] [--excerpt N]` | Notes as JSON (excerpt or full body); `--type` repeats |
| `people [--name X]` / `companies [--name X]` | Directory rows, comma-split aware; `--name` adds the notes |
| `links` | Derived edges + broken references |
| `lint [--stale-days N]` | Structural health check: orphans, stale, broken links, schema, duplicate titles |
| `dedup [--threshold 0.22]` | Jaccard near-duplicates (fallback for Merge) |
| `tags` | Tag usage + typographic groups |
| `retag --map old=new ...` | Stage a tag rewrite across all notes |
| `staging new/seal/list/show/apply/refuse` | Review queue (takes the job id, a unique part of it, or the folder path) |
| `stage-raw <job> <file> --stem S --participant P ...` | Copy a transcript into a job verbatim, with its frontmatter |
| `verify-quotes <job \| file \| folder> [--transcript F ...]` | Check every staged quote (blockquotes and inline « », " ") appears verbatim in the job's transcript, else in all `vault/raw/`, and every `[[citation]]` resolves; exit 1 on a missing quote or broken link, 2 if there was no quote to check. `verify-quotes vault` audits the whole vault; a file path checks an export |
| `index` | Rebuild `graph/index.md` |
| `patterns [--min 2] [--since DATE]` | Tags shared by 2+ participants, saturation signal |
| `project list/resolve/snapshot <project>` | Project membership from its filters |
| `export-csv [--type T] [--project P] --out F` | CSV export (Excel-friendly) |
| `graph-html --out F [--project P]` | Standalone D3 graph page |
| `canvas-check [--canvas F] [--project P]` | Validate a canvas: JSON, colours, every insight in scope exactly once |
| `canvas-html` | Render `graph/canvas.json` as an affinity board |
| `slug "<title>"` | File-name slug |
| `notion-cache rows.json ... [--bodies F]` | Notion backend: turn raw `rows` query results into `.verbatim/cache/notes.json` |

With the Notion backend, the read-only commands (`stats`, `scan`, `people`, `companies`, `links`,
`lint`, `dedup`, `tags`, `patterns`, `export-csv`, `graph-html`) work on a JSON export passed with
`--notes-json .verbatim/cache/notes.json` - see the Notion reference for how to build it.

## 6. Citing notes

Every claim drawn from the vault cites its note: `[[slug]]` in Markdown, the page link in Notion.
A researcher must be able to click through to the evidence; uncited claims are the main way an
AI research tool loses trust.

Quotation marks are reserved for participants' words. In note bodies, « ... », "..." and `>` blockquotes
mean "said verbatim by a participant", and `verbatim.py verify-quotes` checks every one of 4+ words against the
transcripts. Put titles, terms and paraphrases in *italics* instead, so the check stays meaningful.
