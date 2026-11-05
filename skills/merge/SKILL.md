---
name: merge
description: Find and consolidate duplicate or near-duplicate insights in the Verbatim vault - semantic detection by a sub-agent with a Jaccard similarity fallback, then per group keep one, merge into a richer insight that preserves every participant, company and quote, keep both, or skip; links pointing at the originals are rewritten. Use for /verbatim:merge, "dedupe the insights", "find duplicates", "merge similar insights", "the vault has repeats", after several imports, or when the Health Check reports duplicate titles.
argument-hint: "[--project <name>] [--threshold 0.22]"
---

# Verbatim merge (Consolidate)

Interviews repeat each other, which is good evidence - but the
same finding written five times hides how strong it is. Merging turns five weak notes into one
strong note that lists every supporting participant.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. Detect

Need at least 2 insights in scope (vault or `<script> project resolve <name>`).

- **Primary - semantic**: spawn the `verbatim:curator` sub-agent in *dedup* mode with the scope. It reads
  titles + excerpts and returns groups of genuinely redundant insights (same finding, not merely same
  topic) with a reason and a similarity estimate.
  Corroboration across participants is linked, not merged: the agent lists those pairs separately - offer
  them to `verbatim:graph connect`. Merge them only if the user asks.
- **Fallback - Jaccard**: if the agent fails or finds nothing, run `<script> dedup` (title weighted 2x
  + body tokens, threshold 0.22). Say which method produced the groups, and check each Jaccard group
  yourself: shared words also bring together notes that contradict each other.

No groups: say so in one line, done.

## 2. Review one group at a time

Show "Group 2 of 7", the similarity, Verbatim's rationale, and the notes side by side:

```
A  Exports are rebuilt by hand every Friday        Marie (Acme) · high · #workaround
   > "Every Friday I redo the export in Excel..."
B  Users recreate reports manually in spreadsheets Jon (Globex) · medium · #workaround
   > "We copy everything into a sheet..."
```

Ask (AskUserQuestion): **Merge** (recommended for true duplicates) / **Keep A** / **Keep B** /
**Keep both** / **Skip**. Collect all decisions first, then stage once.

## 3. Build the proposals

`<script> staging new --kind merge --label "consolidate <today>"`.

- **Merge** - ask the curator (*merge* mode, or do it inline for a single group) to write the merged
  insight: one coherent finding, the strongest evidence, every distinct quote with its speaker, more
  complete than any original. Frontmatter rules:
  - `participant` / `company`: every distinct value from all originals, comma-separated
  - `source_ref`: the first original's source; the other sources go into `related`
  - `related`: union of the originals' `related` and their sources - **not** the originals themselves
    (they are being deleted)
  - `confidence`: at least the highest original; raise it when the finding now spans 3+ participants
  - `tags`: union, trimmed to what fits
  Write it to `files/insights/<slug>.md`; list every original in `delete.txt`.
- **Keep one** - list the others in `delete.txt`; copy the kept note into the job and add the deleted
  notes' participants/companies/quotes to it if they add evidence.
- **Rewrite inbound links** - `<script> links`, find every note whose `source_ref`, `related` or
  `[[wikilink]]` points to a deleted note, and stage a modified copy pointing to the merged/kept note.

`<script> staging seal <id>`, then the **verbatim:review** workflow (show the merged note next to its
originals). Deleted originals go to `.verbatim/trash/`, so a merge can be undone.
