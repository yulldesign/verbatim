---
title: "Trust in Pulse numbers depends on context the tool does not show"
date_created: 2026-11-04
date_modified: 2026-11-04
type: synthesis
status: validated
tags: [trust, feature-request, pain-point, job-to-be-done]
related: ["sources/source-interview-claire-martin.md", "sources/source-interview-karim-benali.md", "insights/pulse-numbers-do-not-always-match-the-carriers-data.md", "insights/after-a-wrong-figure-reached-management-numbers-are-no.md", "insights/users-want-to-see-where-each-number-comes-from-and-when-data.md", "insights/ops-leads-need-to-be-able-to-explain-every-number-to.md", "insights/the-numbers-are-trusted-as-accurate.md", "insights/unclear-metric-definitions-lead-each-team-to-interpret-them.md", "insights/users-want-a-glossary-of-metrics-inside-the-tool.md"]
source_ref: ""
confidence: medium
author: verbatim
participant: "Claire Martin, Karim Benali"
company: "Lumen Logistics, Fretto"
evidence_count: 2
---

Both participants have a problem with what Pulse numbers *mean*, and both ask for the same kind of fix: context shown next to the number inside the tool. They disagree about accuracy, though, and that contrast is the core of this theme.

Claire Martin does not trust the numbers. Pulse figures have diverged from the carrier's, and one wrong figure reached her director [[source-interview-claire-martin]] [[pulse-numbers-do-not-always-match-the-carriers-data]] [[after-a-wrong-figure-reached-management-numbers-are-no]]:

> "Because the numbers in Pulse don't always match the carrier's. Last time, I presented a 4% delay rate when it was actually 7%."

> "The director asked me where the gap came from and I had no answer. Since then, I don't trust the numbers until I've cross-checked them myself."

Karim Benali, who cross-checks Pulse data in his own warehouse, trusts accuracy but not definitions [[source-interview-karim-benali]] [[the-numbers-are-trusted-as-accurate]] [[unclear-metric-definitions-lead-each-team-to-interpret-them]]:

> "The numbers are right, on my side I've never seen a discrepancy. But the definitions aren't clear."

> "It's not written anywhere. So each team interprets it its own way."

The requested fixes match each diagnosis. Claire asks for provenance, a link to the source or the date of the last sync, because her job is to explain figures to management [[users-want-to-see-where-each-number-comes-from-and-when-data]] [[ops-leads-need-to-be-able-to-explain-every-number-to]]: « If I know the data is from last night, I can explain it. » Karim asks for a glossary of the metrics inside the tool [[users-want-a-glossary-of-metrics-inside-the-tool]]. Both are about transparency rather than new analytics. One analyst inference, not stated by either participant: the metric involved in both cases is *delay*. Claire's 4% vs 7% gap may come partly from a definition mismatch (promised slot vs estimated time, Karim's example) or from sync timing, not only from wrong data. That would link the two diagnoses, but it is unverified.

This matters because distrust is what drives the costly Excel rebuild (see [[pulse-is-valued-for-viewing-data-but-reporting-and-analysis]]) and puts the user's credibility with management at risk. Confidence is medium: both sources support the need for context, but there are only two of them and they differ on whether the data itself is wrong.

## Evidence

- [[source-interview-claire-martin]] - numbers diverged from the carrier's (4% vs 7%), no longer trusted until cross-checked; asks for source links or last-sync date.
- [[source-interview-karim-benali]] - never seen a discrepancy, but metric definitions such as *delay* are undocumented and interpreted differently by each team; asks for an in-tool glossary.

## Open questions

- Did Claire's 4% vs 7% gap come from data errors, sync lag, or a different definition of *delay* from the carrier's? Checking that specific case would confirm or refute the link between the two diagnoses.
- Do non-technical users who cannot cross-check in a warehouse lose trust more easily than data analysts?
- Would provenance and a glossary together be enough for ops leads to stop rebuilding reports by hand?
