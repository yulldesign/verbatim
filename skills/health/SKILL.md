---
name: health
description: Health Check of the research vault - structural checks (orphan insights, stale raw notes, broken links, bad frontmatter, duplicate titles) plus an AI pass for tensions between insights and research gaps, a 0-100 score, findings grouped by severity, and fixes (validate, link, compare, query, draft interview questions for a gap). Use for /verbatim:health, "audit the vault", "check my research", "contradictions?", "what's missing from the research", "research gaps", before a readout, or after big imports or merges.
argument-hint: "[--project <name>] [--structural-only]"
---

# Verbatim health check

Two halves: the script finds what is mechanically wrong, an agent finds
what a senior researcher would question. Findings persist in `.verbatim/health/` so they survive
the conversation.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. Run both halves in parallel

- Structural: `<script> lint` (Notion: with `--notes-json`). Gives `orphan`, `stale`, `broken-link`,
  `schema`, `duplicate-title`. It always scans the whole vault; with `--project`, keep only findings
  whose paths are in `<script> project resolve <name>`.
- Evidence: `<script> verify-quotes vault` - every quote verbatim in a transcript, every citation resolving.
  Each `NOT FOUND` quote is a **Warning** (`altered-quote`), each `BROKEN LINK` counts as a broken link.
- Analytical (skip with `--structural-only`): spawn the `verbatim:auditor` sub-agent with the scope (all
  insights, or a project's), output language, today. It returns JSON-like findings:
  tensions (pairs of insights pointing different ways on the same topic) and gaps (important,
  under-explored topics given what is present), each with affected paths and a reason.

## 2. Score and report

Severity buckets:
- **Issues** - tensions (high)
- **Warnings** - orphans, broken links, duplicate titles, gaps (medium)
- **Suggestions** - stale notes, schema problems (low)

The score measures the health of the vault, so structural defects weigh more than research signals.
A tension between two participants or a gap is something to investigate, not a fault in the vault, and the
auditor is told to be generous - uncapped, they would sink the score of a perfectly clean vault.

```
score = 100 - 5 x (broken links + orphans + duplicate titles + altered quotes) - 1 x (stale + schema)
            - min(15, 3 x tensions) - min(10, 2 x gaps)          (floor 0)
```

Add one sentence of narrative ("Structurally clean; the sample is too thin to settle the pricing tension.").

Write the report to `.verbatim/health/<today>.md` (score, counts, every finding with its paths) -
this is derived output, not vault content, so it needs no review. Show the user the score line,
counts, and findings grouped by bucket, numbered, one line each.

## 3. Act on findings

Offer per-finding actions (the user picks by number):

| Finding | Actions |
|---|---|
| tension | **Compare** - the two notes side by side (title, participant, quote, confidence) and what could reconcile them; **Query** the vault on the topic (`verbatim:query`) |
| gap | **Fix with Verbatim** - draft 3-5 open, non-leading interview questions and the profile of participants to recruit; optionally save as a note in `queries/` via staging |
| orphan | **Link** - find the likely source or related notes and stage a `related` / `source_ref` edit |
| stale | **Mark validated** - stage a `status: validated` edit (or `final`) |
| broken-link | stage a fix to the right target, or remove the link |
| schema | stage the missing fields |
| duplicate-title | hand off to `verbatim:merge` |
| altered-quote | stage the verbatim wording from the transcript, or move the words out of quotation marks |
| any | **Open** - show the note |

Group fixes into one staging job (`--kind health`) and apply through **verbatim:review**.
After applying, re-run `<script> lint` and report the new score.
