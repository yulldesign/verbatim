# Readout: Trust in the data

*Verbatim project readout, 2026-11-04. Participants are pseudonymised (P1, P2).*

## Context

**Research question.** What makes people lose or gain trust in Pulse's numbers, and what must be shown so a manager can defend a number to leadership?

**Method.** Two semi-structured interviews with Pulse customers in October 2026. Each was analysed into atomic insights with verbatim quotes, then synthesised across participants. The project covers every note tagged *trust*: 7 insights and 1 theme.

| | Role | Company | Technical staff |
|---|---|---|---|
| P1 | Head of operations, accountable to management for delivery metrics | Logistics company, mid-size | None |
| P2 | Data analyst, builds dashboards for ops teams and customers | Last-mile delivery startup, small | In-house developers |

With two participants who differ on role, size and technical capacity, every finding below is a strong signal, not an established pattern.

## Key findings

### 1. Trust is lost through one visible incident, not through a pattern of errors (P1)

P1 saw a Pulse delay rate diverge from the carrier's figure [[pulse-numbers-do-not-always-match-the-carriers-data]]:

> "Because the numbers in Pulse don't always match the carrier's. Last time, I presented a 4% delay rate when it was actually 7%."

The cost was personal credibility in front of leadership, and it changed P1's behaviour for good [[after-a-wrong-figure-reached-management-numbers-are-no]]:

> "The director asked me where the gap came from and I had no answer. Since then, I don't trust the numbers until I've cross-checked them myself."

**Implication.** For a manager, one unexplained number in front of leadership costs more than many correct ones earn. After that, every figure is checked by hand.

### 2. The accuracy of the numbers is disputed; their meaning is the shared problem (P1, P2)

P2 checks Pulse data against their own warehouse and has never seen a discrepancy [[the-numbers-are-trusted-as-accurate]]. What P2 lacks is a shared definition of the metrics [[unclear-metric-definitions-lead-each-team-to-interpret-them]]:

> "But the definitions aren't clear. A "delay", is that relative to the promised slot or to the estimated time? It's not written anywhere. So each team interprets it its own way."

Both participants have a problem with what the numbers *mean*. They disagree on whether the data itself is wrong [[trust-in-pulse-numbers-depends-on-context-the-tool-does-not]]. Analyst inference, not stated by either participant: both cases involve the *delay* metric, so P1's 4% vs 7% gap may come from a definition or sync mismatch rather than bad data.

### 3. To defend a number, a manager needs its context, not perfect data (P1, P2)

The fixes requested match each diagnosis, and both are about transparency inside the tool:

- **Provenance and freshness** (P1) [[users-want-to-see-where-each-number-comes-from-and-when-data]]:

  > "Honestly, seeing where each number comes from. Just a link to the source, or the date of the last sync."

  The underlying job is explaining figures to management [[ops-leads-need-to-be-able-to-explain-every-number-to]]:

  > "If I know the data is from last night, I can explain it."

- **A glossary of metric definitions in the product** (P2) [[users-want-a-glossary-of-metrics-inside-the-tool]].

**Implication.** What a manager needs next to each number is where it comes from, when it was last synced, and how it is defined. With those three things, a number can be defended even when it surprises someone.

### 4. Distrust likely pushes reporting out of Pulse (P1, inferred)

P1 rebuilds the weekly management report in Excel, about two hours every Monday [[the-weekly-management-report-is-rebuilt-by-hand-in-excel]]. The vault connects this to P1's cross-checking habit, but P1's own words about the report do not give a reason. Treat the link as an inference (medium confidence). P2 also exports, but for integration rather than distrust [[why-do-users-take-their-data-out-of-pulse-and-is-there-a]].

## Tensions and open questions

- **Accuracy.** P1 found a real gap; P2 never has. They check against different references (the carrier's data vs a warehouse fed by Pulse) [[pulse-numbers-do-not-always-match-the-carriers-data]] [[the-numbers-are-trusted-as-accurate]].
- **Explain vs accuracy.** The insight says P1 asks for context rather than perfect data, yet P1's story centres on a real error [[ops-leads-need-to-be-able-to-explain-every-number-to]].
- Do users who cannot cross-check in a warehouse lose trust more easily than data analysts?
- Would provenance and a glossary be enough for ops leads to stop rebuilding reports by hand?

## Gaps and recommended next research

1. **Root cause of the 4% vs 7% gap**: a data error, sync lag or a different definition of *delay*? This decides whether the fix is provenance, a glossary or the data itself. It can be settled by investigating that one incident, without new interviews.
2. **Each side rests on one participant.** Recruit at least 2 ops leads at companies *with* technical staff, and 2 data users at companies *without*, to separate role from technical capacity [[research-plan-which-findings-hold-beyond-a-single]].
3. **What leadership asks.** Nobody on the receiving end (directors, CFOs) has been interviewed. Suggested question: *When a team presents a delivery figure to you, what makes you believe it?*
4. **Prototype test.** Show a number with its source, last-sync date and definition, and ask: *Could you present this to your director as it is? What would you still check?*

## Appendix

**Participants**

| | Interview | Insights in this project |
|---|---|---|
| P1 | 2026-10-14 | 4 |
| P2 | 2026-10-17 | 3 |

**Notes cited**

- Theme: [[trust-in-pulse-numbers-depends-on-context-the-tool-does-not]]
- Insights: [[pulse-numbers-do-not-always-match-the-carriers-data]], [[after-a-wrong-figure-reached-management-numbers-are-no]], [[the-numbers-are-trusted-as-accurate]], [[unclear-metric-definitions-lead-each-team-to-interpret-them]], [[users-want-to-see-where-each-number-comes-from-and-when-data]], [[ops-leads-need-to-be-able-to-explain-every-number-to]], [[users-want-a-glossary-of-metrics-inside-the-tool]], [[the-weekly-management-report-is-rebuilt-by-hand-in-excel]]
- Saved queries: [[why-do-users-take-their-data-out-of-pulse-and-is-there-a]], [[research-plan-which-findings-hold-beyond-a-single]]
