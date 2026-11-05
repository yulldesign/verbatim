---
name: synthesis
description: Cross-interview synthesis (themes) - reads every source summary and its insights, finds patterns supported by at least two participants, and proposes synthesis notes with evidence, contrasts, confidence and open questions, without duplicating themes already in the vault. Use for /verbatim:synthesis, "find the themes", "what are the patterns", "synthesise the interviews", "what's common across participants", "top findings", after importing several interviews, or when preparing a research readout.
argument-hint: "[--project <name>] [--focus <topic>]"
---

# Verbatim synthesis (Themes)

A synthesis note is a claim about the population, not about one
person, so it must rest on several sources and say who supports it and who does not.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. Prepare the input

- Scope: whole vault, or `<script> project resolve <name>` for a project. `--focus` narrows to a topic.
- Sources: `<script> scan --type source --full` (participant, company, summary, themes, key quote).
- Insights: `<script> scan --type insight` (titles, tags, participant, confidence) - they give finer
  evidence than summaries.
- Existing themes: `<script> scan --type synthesis` titles - passed to the agent so a re-run proposes
  only what is new (Verbatim's duplicate guard).
- Fewer than 2 sources in scope: stop and say synthesis needs at least two interviews.

## 2. Delegate to the synthesizer

`<script> staging new --kind synthesis --label "<scope> <today>"`, then spawn the `verbatim:synthesizer`
sub-agent with: the job folder, the scope (list of source and insight paths), existing theme titles,
focus if any, output language, taxonomy, today. It writes 3-8 notes to `files/synthesis/`, seals the
job, and returns a summary. With a very large corpus (> ~40 sources), split by segment or company
into parallel synthesizers, then de-duplicate their themes yourself before review.

## 3. Review card by card

Present each proposed theme as a card:

```
1. Teams trust exported numbers only after a manual cross-check     [high · 6/11 participants]
   Marie (Acme), Jon (Globex), ... - exception: Lea (Initech) automates it fully
   "<first sentence of the body>"
```

Then use the **verbatim:review** workflow (Save all / choose / refuse; edits allowed). Slug collisions with
existing synthesis files are a duplicate signal - flag them rather than overwrite.

## 4. After apply

Offer the natural follow-ups: an affinity board of the insights (`verbatim:canvas`), a readout document
(`verbatim:export`), or a Health Check for gaps the themes reveal (`verbatim:health`).
