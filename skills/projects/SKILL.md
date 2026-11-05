---
name: projects
description: Projects in the Verbatim research vault - named, filtered subsets of the research (by note type, tags, participants, companies, dates, plus manual include/exclude) with an overview, insights, themes, sources, saved queries, a board and a graph per project, a lock/snapshot for frozen studies, and an activity feed (ingests, cross-participant patterns, saturation, confidence upgrades). Use for /verbatim:projects, "create a project for the onboarding study", "new research project", "show project X", "lock the Q3 study", "what's new in project X", or to scope any other Verbatim workflow to a subset.
argument-hint: "[list | new | show <name> | edit <name> | lock <name> | unlock <name> | activity <name>]"
---

# Verbatim projects

A project answers one research question with a slice of the vault. Membership is computed
from filters each time (so new interviews flow in), unless the project is locked to a snapshot.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.
The project note format (filters in frontmatter, research question and Activity in the body) is in
`${CLAUDE_PLUGIN_ROOT}/skills/vault/references/note-formats.md` section 6. Notion: the Verbatim Projects database (backend reference).

## list
`<script> project list` -> name, note count, locked. Add the research question line from each note.

## new
Ask for: name, the research question, and filters - offer the existing values to pick from
(`<script> tags`, `<script> people`, `<script> companies`), all optional. Stage `projects/<slug>.md`
(`staging new --kind project`), apply via **verbatim:review**, then show the resulting count with
`<script> project resolve <slug>`.

## show
`<script> project resolve <name>`, then an overview:
- counts by type, participants and companies covered (comma-split), date range
- **Themes**: vault-wide synthesis notes relevant to the project (they describe the whole corpus, as in
  Verbatim - show those whose evidence overlaps the project's sources), then project insights grouped by tag
  or confidence
- sources, saved queries, and whether a project canvas exists (`projects/<slug>.canvas.json`)
Offer the project-scoped actions: query, synthesis, canvas, health, graph, export - each skill takes
`--project <name>`.

## edit
Change filters, add to `included` / `excluded` ("exclude the pilot interviews"), rename, recolour.
Always a staged `modify` of the project note; show the membership delta (before/after counts) before applying.

## lock / unlock
Lock freezes the study: `<script> project snapshot <name>` prints the current member paths; stage the note
with `locked: true` and `snapshot: [...]`, plus an Activity line. Unlock clears both. Use lock when a study
is reported, so later imports do not change what the report was based on.

## activity
The feed of what changed, in Verbatim's terms:
- **Ingest** - new sources/insights entering the project since the last Activity entry (compare dates)
- **Pattern** - `<script> patterns` restricted to project members: a tag shared by 2+ participants
- **Saturation** - `<script> patterns --since <date of last ingest>`: a ratio above 0.6 means new interviews
  mostly repeat what is known - a signal to stop recruiting or change the questions
- **Confidence upgrade** - insights whose confidence rose (corroborated by new sources)
- **Contradiction** - tensions from the latest `.verbatim/health/` report touching project notes
Show the feed newest first; offer to append the new entries to the project's `## Activity` section (staged).
