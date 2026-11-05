# Note formats

Copy these shapes exactly. Values in `<angle brackets>` are placeholders. Strings are
double-quoted; dates, enums and arrays are not.

## Contents
1. transcript (raw/)
2. source (sources/)
3. insight (insights/)
4. synthesis (synthesis/)
5. query-output (queries/)
6. project (projects/)
7. canvas (graph/canvas.json)

---

## 1. transcript - `raw/<file-stem>.md`

The original document, verbatim. Never summarise or clean it: it is the evidence.

```markdown
---
title: "<file stem, e.g. interview-marie-2026-10>"
date_created: <today>
date_modified: <today>
type: transcript
status: raw
tags: []
related: []
source_ref: ""
confidence: high
author: human
participant: "<real name found in the transcript, else file stem>"
company: "<organisation or empty>"
interview_date: "<date of the interview if stated, else empty>"
original_file: "<original path or URL>"
---

<full transcript text, unchanged>
```

## 2. source - `sources/source-<file-stem>.md`

```markdown
---
title: "Source: <file stem>"
date_created: <today>
date_modified: <today>
type: source
status: validated
tags: [<2-5 taxonomy tags covering the interview>]
related: []
source_ref: "raw/<file-stem>.md"
confidence: high
author: verbatim
participant: "<real name>"
company: "<organisation or empty>"
role: "<job title if stated>"
segment: "<persona / segment if obvious, else empty>"
---

## Summary

<2-4 sentences: who, context, the main story of the interview.>

## Themes

- <theme>
- <theme>

## Participant profile

<One sentence: role, context, attitude toward the product/problem.>

## Key quote

> <the single most important verbatim quote>

## Insights

- [[<insight-slug>]]
- [[<insight-slug>]]
```

## 3. insight - `insights/<slug-of-title>.md`

The title *is* the finding ("Exports are rebuilt by hand every Friday"), not a topic
("Exports"). One finding per note - split compound observations.

```markdown
---
title: "<the insight, stated as a finding>"
date_created: <today>
date_modified: <today>
type: insight
status: validated
tags: [<taxonomy tags>]
related: []
source_ref: "sources/source-<file-stem>.md"
confidence: <high | medium | low>
author: verbatim
participant: "<real name>"
company: "<organisation or empty>"
kind: <observation | quote | signal | implicit-need>
---

<2-3 sentences explaining the finding and the evidence behind it.>

> "<verbatim quote that supports it>"
> - <participant>, [[<file-stem>]]
```

`status: validated` on Verbatim-generated notes is correct: they only reach the vault after the researcher
approved them in review. (The transcript's `confidence: high` means the record itself is exact, not that
its content is.)

Confidence guide:
- **high** - stated explicitly, with a concrete example or repeated in the interview
- **medium** - stated once, or clearly implied by behaviour described
- **low** - inferred by the analyst; plausible but not said

`kind` mirrors the four things Verbatim extracts: explicit observations, notable quotes,
recurring signals, and implicit needs or frustrations.

## 4. synthesis - `synthesis/<slug-of-title>.md`

```markdown
---
title: "<cross-interview pattern stated as a finding>"
date_created: <today>
date_modified: <today>
type: synthesis
status: validated
tags: [<taxonomy tags>]
related: ["sources/source-a.md", "sources/source-b.md", "insights/x.md"]
source_ref: ""
confidence: <high | medium | low>
author: verbatim
participant: "<every participant who supports it, comma-separated>"
company: "<their companies, comma-separated>"
evidence_count: <number of supporting sources>
---

<2-4 paragraphs of prose: the shared finding, specific evidence from several
participants (cite [[source-...]] and [[insight-slug]]), contrasts, nuances and exceptions.>

## Evidence

- [[source-a]] - <one line on what this participant said>
- [[source-b]] - <...>

## Open questions

- <what would confirm or refute this pattern>
```

## 5. query-output - `queries/<slug-of-question>.md`

```markdown
---
title: "<the question>"
date_created: <today>
date_modified: <today>
type: query-output
status: validated
tags: [<taxonomy tags touched>]
related: [<paths of every cited note>]
source_ref: ""
confidence: <high if well covered, medium if partial, low if mostly gaps>
author: verbatim
participant: ""
company: ""
---

## Question

<question>

## Answer

<prose with [[citations]]>

## What the vault does not cover

<gaps>

Sources: [[a]], [[b]]
```

## 6. project - `projects/<slug>.md`

Filters decide membership; `included` / `excluded` override them; `locked: true` freezes
membership to `snapshot`. Empty filter = no constraint. Default `filter_types` is
`["insight", "source", "query-output", "synthesis"]`.

```markdown
---
title: "<project name>"
date_created: <today>
date_modified: <today>
type: project
status: validated
tags: []
related: []
source_ref: ""
confidence: ""
author: human
participant: ""
company: ""
description: "<one line>"
color: <blue | violet | rose | amber | green | teal | orange | slate>
filter_types: ["insight", "source", "query-output", "synthesis"]
filter_tags: []
filter_participants: []
filter_companies: []
date_from: ""
date_to: ""
included: []
excluded: []
locked: false
snapshot: []
---

## Research question

<what this project is trying to learn>

## Activity

- <YYYY-MM-DD> - <event: ingest, pattern detected, saturation signal, lock...>
```

## 7. canvas - `graph/canvas.json` (or `projects/<slug>.canvas.json`)

```json
{
  "title": "Affinity map - <scope>",
  "generated": "<today>",
  "clusters": [
    {
      "label": "Onboarding friction points",
      "color": "amber",
      "rationale": "<one sentence on what ties these together>",
      "insights": ["insights/a.md", "insights/b.md"]
    }
  ]
}
```

Colors: amber, blue, green, rose, teal, orange, slate, violet.
