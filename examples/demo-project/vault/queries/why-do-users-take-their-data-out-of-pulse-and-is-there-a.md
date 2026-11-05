---
title: "Why do users take their data out of Pulse, and is there a risk they leave?"
date_created: 2026-11-04
date_modified: 2026-11-04
type: query-output
status: validated
tags: [workaround, integration, trust, pricing, churn-risk]
related: ["insights/the-weekly-management-report-is-rebuilt-by-hand-in-excel.md", "insights/after-a-wrong-figure-reached-management-numbers-are-no.md", "insights/data-is-exported-to-csv-and-moved-into-the-warehouse-to.md", "insights/a-homemade-nightly-script-works-around-the-missing-export.md", "insights/the-export-script-breaks-whenever-the-interface-changes.md", "insights/the-automated-export-depends-on-one-analysts-personal-login.md", "insights/a-real-api-or-scheduled-export-is-the-top-time-saving.md", "insights/stakeholders-without-an-account-can-only-be-shared.md", "insights/per-user-pricing-charges-for-people-who-only-view.md", "insights/dashboards-are-perceived-as-clear-once-setup-is-done.md", "insights/the-live-delivery-map-is-opened-daily-and-replaces-calling.md", "synthesis/pulse-is-valued-for-viewing-data-but-reporting-and-analysis.md", "synthesis/trust-in-pulse-numbers-depends-on-context-the-tool-does-not.md", "synthesis/per-user-pricing-restricts-sharing-dashboards-with-view-only.md", "sources/source-interview-claire-martin.md", "sources/source-interview-karim-benali.md"]
source_ref: ""
confidence: low
author: verbatim
participant: ""
company: ""
---

## Question

Why do users take their data out of Pulse, and is there a risk they leave?

## Answer

**Why the data leaves.** Both participants (2 of 2) export Pulse data to CSV and do the work that matters in another tool [[pulse-is-valued-for-viewing-data-but-reporting-and-analysis]]. Their reasons differ.

- **Claire Martin (ops lead, Lumen Logistics)** rebuilds the weekly management report in Excel, about two hours every Monday, although Pulse is meant to produce it [[the-weekly-management-report-is-rebuilt-by-hand-in-excel]]:

  > "In theory Pulse does that on its own. In practice, I export the data to CSV and redo everything in Excel. It takes me a good two hours every Monday."

  The vault links this to distrust. After a wrong figure reached her director, she cross-checks every number before trusting it [[after-a-wrong-figure-reached-management-numbers-are-no]] [[trust-in-pulse-numbers-depends-on-context-the-tool-does-not]]. Her own words about the report do not give that reason, so the link is an inference (medium confidence). She also takes figures out as screenshots emailed to a CFO who has no licence [[stakeholders-without-an-account-can-only-be-shared]].
- **Karim Benali (data analyst, Fretto)** exports because he needs Pulse data next to internal data in BigQuery, and Pulse has no API [[data-is-exported-to-csv-and-moved-into-the-warehouse-to]] [[a-homemade-nightly-script-works-around-the-missing-export]]:

  > "Pulse is good for visualizing, but as soon as we want to combine it with our internal data, I export everything to CSV and move it into our data warehouse."

  His nightly script broke twice this quarter after interface changes [[the-export-script-breaks-whenever-the-interface-changes]], and it runs on his personal login [[the-automated-export-depends-on-one-analysts-personal-login]]. His top request is *a real API or a scheduled export to a bucket* [[a-real-api-or-scheduled-export-is-the-top-time-saving]].

In short: distrust and the need to defend numbers in Claire's case (inferred), and integration in Karim's. Pulse stays the place where people *look at* data, not where they produce the output.

**Is there a risk they leave?** Neither participant said they would leave Pulse or mentioned a competitor. The vault shows signals that point to risk, all of them inferred (low confidence):

- The reporting and analysis work already happens outside Pulse, so the product's share of the job is shrinking to visualisation [[pulse-is-valued-for-viewing-data-but-reporting-and-analysis]].
- Karim's pipeline is fragile and depends on one person. The insight infers that breakages like these can erode confidence in Pulse as a data source [[the-export-script-breaks-whenever-the-interface-changes]].
- Pricing blocks expansion rather than renewal. Claire says the price is fine but that more view-only seats would be hard to justify, and she did not mention leaving [[per-user-pricing-charges-for-people-who-only-view]] [[per-user-pricing-restricts-sharing-dashboards-with-view-only]]. The 2026-11-04 Health Check flagged the *churn-risk* tag on this note as stronger than the evidence.

Counterweights: both value the visual layer. Claire finds the dashboards clear and her team opens the live delivery map every morning [[dashboards-are-perceived-as-clear-once-setup-is-done]] [[the-live-delivery-map-is-opened-daily-and-replaces-calling]]. Karim calls Pulse good for visualising.

Verdict: the evidence supports a risk of **shrinking usage and blocked expansion**. It does not show intent to churn. This rests on two interviews.

## What the vault does not cover

- No statement of switching intent, renewal dates, alternatives considered or competitors.
- Whether an API, a scheduled export or provenance would bring the reporting back into Pulse. Interview question: *If Pulse produced the Monday report with the source and sync date of each number, what would you still do in Excel?*
- How many other accounts export regularly, and why (distrust or integration).
- Whether the data warehouse could replace Pulse's dashboards for teams like Fretto. Interview question: *What would you lose if you built these dashboards directly on BigQuery?*

Sources: [[source-interview-claire-martin]], [[source-interview-karim-benali]], [[pulse-is-valued-for-viewing-data-but-reporting-and-analysis]], [[trust-in-pulse-numbers-depends-on-context-the-tool-does-not]], [[per-user-pricing-restricts-sharing-dashboards-with-view-only]]
