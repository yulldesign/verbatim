---
name: home
description: Entry point of Verbatim, the user-research knowledge base run by Claude - shows the state of the research vault (transcripts, insights, themes, people, pending reviews, health) and routes to the right Verbatim workflow. Use when the user types /verbatim:home, asks "where are we on the research", "what's in the vault", "what do we have so far", wants an overview of their interviews, or asks what Verbatim can do. Also use when a research request is vague and you need to pick which Verbatim workflow fits.
---

# Verbatim - home

Verbatim turns interview transcripts into a structured, linked research base and lets the
researcher question it in natural language. This skill is the entry point: show where
things stand, then route.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first if it is not already loaded - it defines the
config, the note types and the script used below. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. Status

If no `verbatim.config.json` is found in this folder or above, this is not a Verbatim project yet: say so in one
line and offer `/verbatim:setup` (it takes a minute). Otherwise run, in parallel:

- `<script> stats` (Markdown) - for Notion, build the cache first (backend reference) and add `--notes-json`
- `<script> staging list --status ready partial`
- the most recent `.verbatim/health/*.md`, if any (just its score line)

Present a compact dashboard - no more than ~15 lines:

```
Vault: <path or Notion>          Last ingest: <date>
Library 12 · Sources 12 · Insights 87 · Themes 6 · Saved queries 4 · Projects 2
People 11 · Companies 7 · Tags 23
Pending reviews: 2 (ingest: interview-marie, synthesis: run of 2026-11-03)
Health: 82/100 (2026-11-01)
```

Then suggest the one or two most useful next steps given the state, for example:
pending reviews -> review them first; new sources since the last synthesis -> run Themes;
health older than two weeks or many new insights -> Health Check; empty vault -> import.

## 2. Routing

| The user wants to... | Skill |
|---|---|
| set up a vault (Markdown folder or Notion), change settings | `verbatim:setup` |
| import transcripts, notes, PDFs, Notion pages, meeting recordings | `verbatim:ingest` |
| accept or refuse what Verbatim proposed | `verbatim:review` |
| ask a question about the research | `verbatim:query` |
| find cross-interview themes / patterns | `verbatim:synthesis` |
| audit the vault: orphans, stale notes, contradictions, gaps | `verbatim:health` |
| find and merge duplicate insights | `verbatim:merge` |
| clean up the tag taxonomy | `verbatim:tags` |
| affinity mapping / clustering / post-it board | `verbatim:canvas` |
| see who said what: participants, companies | `verbatim:directory` |
| scope a subset of the research (a study, a feature, a segment) | `verbatim:projects` |
| see the knowledge graph, rebuild the index, link notes | `verbatim:graph` |
| export to CSV, HTML, a readout document | `verbatim:export` |
| create or improve an Verbatim skill | `skill-creator` |

When the request maps clearly to one skill, go straight there without showing the dashboard.

## 3. Principles to keep in every workflow

- The vault is the evidence base: answers cite notes, notes cite quotes, quotes come from transcripts.
- Nothing is written to the vault without the researcher's approval (staging -> review -> apply),
  unless `skip_review` is on.
- Separate what participants said from what Verbatim infers. Confidence levels make that visible.
