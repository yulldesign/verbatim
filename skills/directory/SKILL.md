---
name: directory
description: People and Companies directory of the research vault - who was interviewed, from which company and role, how many notes reference them, first/last seen, and a profile view with their source summary, key quotes, insights and the themes they support; navigates between a company and its participants. Use for /verbatim:directory, "who did we interview", "list the participants", "what did Marie say", "everything from Acme", "which companies", or any who-said-what question about a person or organisation.
argument-hint: "[person or company name]"
---

# Verbatim directory

The who-said-what view. Counts and memberships come from the script, so they are exact;
Claude adds the reading of the notes.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.
Remember: `participant` and `company` can hold comma-separated names (merged notes) - the script already
splits them; do the same if you read frontmatter yourself.

## List view

`<script> people` or `<script> companies` -> a table sorted by number of notes:

```
| Participant  | Company | Interviewed | Notes | Insights |
|--------------|---------|-------------|-------|----------|
| Marie Dupont | Acme    | 2026-10-21  | 12    | 9        |
```

`interviews` holds the interview dates from the transcripts (`interview_date`, else the import date);
`first_seen` / `last_seen` are import dates of the notes - use `interviews` when the user asks "when".

Offer sorting by name or date on request. Mention near-duplicate names ("Marie D." vs "Marie Dupont") -
they usually mean the same person; fixing them is a staged frontmatter edit through **verbatim:review**.

## Profile view - a person

`<script> people --name "<name>"` gives the notes. Then read the source note(s) and present:

1. Header: name, company, role/segment, number of interviews, first/last seen.
2. Profile: the source's "Participant profile" and summary.
3. Key quotes: the source's key quote plus 2-3 from their insights.
4. Insights: titles with confidence and tags, `[[cited]]`.
5. Themes they support: synthesis notes whose `participant` includes them.

## Profile view - a company

`<script> companies --name "<name>"`: participants (each one a pointer to their profile - "say a name to
open it"), number of notes, the company's recurring tags (count tags across its insights), main insights,
themes it supports.

## Useful extras

- "Compare Acme and Globex" -> two company profiles side by side, then shared and diverging tags.
- "Who hasn't been asked about pricing?" -> participants with no insight tagged `pricing`.
- A proto-persona from a set of participants is a reasonable follow-up; keep every trait cited.
