# Notion backend

The vault lives in two Notion databases: **Verbatim Notes** (every note type) and
**Verbatim Projects**. Proposals are still staged as local Markdown files under
`.verbatim/staging/`, so the review step is identical to the Markdown backend; only
"apply" differs: you write the pages through the Notion MCP tools.

The Notion tools are named `notion-search`, `notion-fetch`, `notion-create-database`,
`notion-update-data-source`, `notion-query-data-sources`, `notion-create-pages`,
`notion-update-page`, `notion-delete-pages` (the MCP prefix varies per install). If they
are not available, tell the user the Notion connector must be connected (`/mcp`) and stop.

## Contents
1. Schema (created by /verbatim:setup)
2. Property mapping
3. Reading: build the notes cache
4. Applying a staging job
5. Citations

---

## 1. Schema

**Verbatim Notes** - create with `notion-create-database` under `notion.parent_page`:

```sql
CREATE TABLE (
  "Title" TITLE,
  "Type" SELECT('transcript':blue, 'source':yellow, 'insight':green, 'synthesis':pink, 'query-output':gray),
  "Status" SELECT('raw':gray, 'processing':orange, 'validated':green, 'final':purple),
  "Tags" MULTI_SELECT('pain-point':red, 'feature-request':blue, 'workaround':orange, 'onboarding':yellow,
                      'pricing':green, 'performance':purple, 'ux':pink, 'integration':brown, 'trust':gray,
                      'churn-risk':red, 'delight':green, 'job-to-be-done':blue, 'process':gray, 'expectation-gap':orange),
  "Confidence" SELECT('high':green, 'medium':yellow, 'low':red),
  "Author" SELECT('human':default, 'verbatim':brown),
  "Participant" RICH_TEXT,
  "Company" RICH_TEXT,
  "Kind" SELECT('observation':default, 'quote':blue, 'signal':purple, 'implicit-need':orange),
  "Date created" DATE,
  "Slug" RICH_TEXT,
  "Vault path" RICH_TEXT
)
```

Use the taxonomy from `verbatim.config.json` for the Tags options. Then, with the returned data
source id, add the graph relations with `notion-update-data-source`:

- `"Source" RELATION('<notes_ds>', DUAL 'Derived notes' 'derived_notes')` - insight -> source, source -> transcript
- `"Related" RELATION('<notes_ds>')` - synthesis -> evidence, merged insight -> originals

**Verbatim Projects**:

```sql
CREATE TABLE (
  "Name" TITLE,
  "Description" RICH_TEXT,
  "Color" SELECT('blue':blue, 'violet':purple, 'rose':pink, 'amber':yellow, 'green':green, 'teal':blue, 'orange':orange, 'slate':gray),
  "Filter types" MULTI_SELECT('insight':green, 'source':yellow, 'query-output':gray, 'synthesis':pink, 'transcript':blue),
  "Filter tags" RICH_TEXT COMMENT 'comma-separated tags',
  "Filter participants" RICH_TEXT,
  "Filter companies" RICH_TEXT,
  "Date from" DATE,
  "Date to" DATE,
  "Locked" CHECKBOX
)
```

Then add `"Included" RELATION('<notes_ds>')`, `"Excluded" RELATION('<notes_ds>')`,
`"Snapshot" RELATION('<notes_ds>')`. The project page body holds the research question and the
Activity log (same sections as the Markdown project template).

Store both data source ids (`collection://...`) in `verbatim.config.json` under `notion`.

## 2. Property mapping

| Frontmatter | Notion property | Notes |
|---|---|---|
| title | Title | |
| type | Type | |
| status | Status | |
| tags | Tags | add missing options only if the user agreed to a new tag |
| confidence | Confidence | |
| author | Author | |
| participant / company | Participant / Company | keep comma-separated text as-is |
| kind | Kind | insights only |
| date_created | `date:Date created:start` | `date:Date created:is_datetime` = 0 |
| slug (file name) | Slug | lets `[[slug]]` citations resolve |
| vault-relative path | Vault path | **without `.md`**, e.g. `insights/slow-export` - Notion turns `x.md` into a link to the domain `x.md`. Used to match staging ops |
| source_ref | Source (relation) | page URL of the target |
| related | Related (relation) | page URLs |
| body | page content | Notion-flavoured Markdown; read `notion://docs/notion-flavored-markdown-spec` once before writing |

`date_modified` is Notion's own last-edited time.

## 3. Reading: build the notes cache

The helper script cannot call Notion, so export the database to `.verbatim/cache/` once per task and pass
`--notes-json .verbatim/cache/notes.json` to the read-only commands.

1. `notion-query-data-sources` in **rows** mode on the notes data source (`limit: 100`). Use rows, not SQL:
   SQL leaves out relation columns (Source, Related), so every link would be lost, and returns page URLs
   in another form. Above 100 notes, run one query per `Type` (filter `enum_is`) - rows mode has no cursor.
2. Save each raw result, unchanged, with the Write tool: `.verbatim/cache/rows-<n>.json`.
3. `verbatim.py notion-cache .verbatim/cache/rows-*.json --out .verbatim/cache/notes.json` - decodes Tags and relations
   (they arrive as JSON text), strips the link Notion may have added around `Vault path`, restores `.md`,
   and normalises URLs so `source_ref` / `related` resolve.
4. Bodies are not in the rows. When a task needs text (dedup, synthesis, query), `notion-fetch` only the pages
   it needs and pass them as `--bodies bodies.json` (`{"<page url or slug>": "<text>"}`); for search over
   bodies, `notion-search` with `data_source_url` scoped to the Notes database is cheaper.

Tested: stats, people, companies, links, lint, tags, patterns, export-csv and graph-html all run on the cache
(graph nodes open the Notion pages).

## 4. Applying a staging job

Check the job **before** writing anything: `verbatim.py verify-quotes <job-id>` runs on the local staged files
(the transcript is staged in `files/raw/`). Notion bodies are not local, so this is the only point where
quotes can be checked mechanically.

After the user approves (see `verbatim:review`):

1. Order the ops so targets exist before anything points to them: transcripts, then sources,
   then insights / synthesis / queries. Use `allow_async: false` on each batch: the next one needs its URLs.
2. **create** -> `notion-create-pages` with parent `{"data_source_id": "<notes_ds>"}`, up to 100 pages per
   call, properties mapped per section 2 (`Source` / `Related` = arrays of page URLs from earlier batches),
   content = the Markdown body. `>` blockquotes work as-is. Convert `[[slug]]` to
   `<mention url="<page url>">Title</mention>` when the target page already exists. Keep a local map
   `{slug: {url, title}}` (e.g. `.verbatim/notion-map.json`) as pages are created.
   The `Source` relation is two-way: the source automatically lists its insights in `Derived notes`.
3. **Second pass for forward links** - a `[[slug]]` whose page did not exist yet is stored escaped as
   `\[\[slug\]\]`. Once every page exists, `notion-update-page` with `update_content` on the pages that
   contain them: `old_str` = `\[\[slug\]\]` (escaped exactly like that), `new_str` = the mention.
   Typical case: the source note's `## Insights` list.
4. **modify** -> find the page by `Vault path` (or `notion_page_id` in the staged frontmatter), then
   `notion-update-page`: `update_properties` for frontmatter changes, `update_content` for body edits.
   Make the smallest edit.
5. **delete** -> confirm with the user in this conversation first, then `notion-delete-pages`
   (Notion moves pages to its trash).
6. Mark the job done locally: `verbatim.py staging apply <job-id> --mark-only` (add `--only` /
   `--exclude` for partial approvals). It writes nothing to the local folder. Report any Notion warnings.

Index page: instead of `graph/index.md`, keep a page "Verbatim Index" under the parent page with a
linked view of the Notes database grouped by Type; nothing to rebuild.

## 5. Citations

In answers, cite Notion notes with their page link (`[Title](url)`) or a page mention when writing
into Notion. Keep `[[slug]]` only when writing Markdown files.
