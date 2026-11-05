---
name: review
description: Review queue for everything Verbatim proposes - list pending staging jobs (ingests, themes, merges, tag rewrites, saved queries, fixes), show each proposal and its diff, let the researcher accept all, accept some, edit, or refuse, then apply to the vault (Markdown or Notion). Use for /verbatim:review, "show me what's pending", "approve the proposals", "accept the insights", "what did Verbatim propose", and at the end of any Verbatim workflow that staged changes.
argument-hint: "[job id] [--all]"
---

# Verbatim review

This is Verbatim's review gate. The researcher stays in control of the
knowledge base: nothing proposed by an agent reaches the vault until they say so.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. List what is pending

`<script> staging list --status ready partial draft`. A `draft` job was never sealed - seal it
(`staging seal <id>`) before showing it. If nothing is pending, say so in one line.

## 2. Present a job

For each job (or the one asked for), run `<script> staging show <id>` (add `--diff` when it has
`modify` ops) and read the staged files you need. Present it so a researcher can judge quality fast,
grouped by type, not as raw file dumps:

**Ingest job**
```
Interview - Marie Dupont @ Acme (interview-marie-2026-10)
Source: "Ops lead, rebuilds the weekly report by hand; sceptical of new tools"
Insights (9):
  1. [high]   Exports are rebuilt by hand every Friday            #workaround #pain-point
  2. [medium] Trusts numbers only after cross-checking in Excel    #trust
  ...
```
For insights, show the supporting quote on request, or right away when there are 5 or fewer.

**Synthesis job** - one card per theme: title, confidence, participants supporting it, first sentence.
**Merge job** - originals side by side, the merged note, and the notes whose links get rewritten.
**Tags job** - `old -> new` mapping and number of notes touched.
**Modify ops** - show the diff, trimmed to the changed lines.

Surface the job's `warnings` (missing frontmatter) before asking.

## 3. Ask for a decision

Use AskUserQuestion: **Accept all** (recommended when nothing looks off) / **Choose which** /
**Refuse all**. With "Choose which", list the numbered items and accept answers like
"all except 3 and 7" or "only 1-4".

Edits are welcome before applying: "rename 2 to ...", "insight 5 is low confidence", "merge 3 and 4".
Make the change in the staged file (`<job>/files/...`), keep the frontmatter valid, re-run
`staging seal <id>`, and show only what changed.

For ingest jobs, run `<script> verify-quotes <id>` before presenting and show its result line
("14/14 quotes found verbatim"). For other jobs quoting transcripts already in the vault, pass
`--transcript vault/raw/<stem>.md`. A quote that is not in the transcript must be fixed or the
insight downgraded before applying - fabricated evidence is the worst failure for a research tool.

## 4. Apply

**Markdown**: `<script> staging apply <id>` with `--only <paths>` or `--exclude <paths>` for partial
approval; `<script> staging refuse <id> --only <paths>` for explicit refusals (leftovers stay pending).
If the script reports `skipped` paths, the vault changed since staging: show the diff and ask before
re-running with `--force`.

**Notion**: follow section 4 of `${CLAUDE_PLUGIN_ROOT}/skills/vault/references/backend-notion.md`, then
`<script> staging apply <id> --mark-only` (same `--only` / `--exclude`).

Deletions (merges, health fixes) go to `.verbatim/trash/` locally or to Notion's trash - say where.

## 5. Close

One or two lines: what was written, where, how many notes now in the vault. Then the next useful
step (e.g. after an ingest of 2+ sources -> themes). If `skip_review` is off and the user keeps
accepting everything without changes, mention once that auto-apply exists (`verbatim:setup`).
