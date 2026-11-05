---
title: "Pulse is valued for viewing data, but reporting and analysis are rebuilt outside it from CSV exports"
date_created: 2026-11-04
date_modified: 2026-11-04
type: synthesis
status: validated
tags: [workaround, integration, process, delight]
related: ["sources/source-interview-claire-martin.md", "sources/source-interview-karim-benali.md", "insights/the-weekly-management-report-is-rebuilt-by-hand-in-excel.md", "insights/data-is-exported-to-csv-and-moved-into-the-warehouse-to.md", "insights/a-homemade-nightly-script-works-around-the-missing-export.md", "insights/the-export-script-breaks-whenever-the-interface-changes.md", "insights/the-automated-export-depends-on-one-analysts-personal-login.md", "insights/a-real-api-or-scheduled-export-is-the-top-time-saving.md", "insights/dashboards-are-perceived-as-clear-once-setup-is-done.md", "insights/the-live-delivery-map-is-opened-daily-and-replaces-calling.md"]
source_ref: ""
confidence: medium
author: verbatim
participant: "Claire Martin, Karim Benali"
company: "Lumen Logistics, Fretto"
evidence_count: 2
---

Both participants like Pulse as a place to *look at* data, yet neither treats it as the place where the real output is produced. In both interviews the data leaves Pulse as a CSV export and the work that matters (the management report, the combined analysis) is done in another tool. The two participants differ in profile and in where the data goes, but the exit point is the same.

Claire Martin, head of operations at Lumen Logistics, rebuilds the weekly management report by hand even though Pulse is supposed to produce it [[source-interview-claire-martin]] [[the-weekly-management-report-is-rebuilt-by-hand-in-excel]]:

> "In theory Pulse does that on its own. In practice, I export the data to CSV and redo everything in Excel. It takes me a good two hours every Monday."

Karim Benali, data analyst at Fretto, exports to CSV whenever Pulse data must be combined with internal data, and has automated this with a nightly script feeding BigQuery [[source-interview-karim-benali]] [[data-is-exported-to-csv-and-moved-into-the-warehouse-to]] [[a-homemade-nightly-script-works-around-the-missing-export]]:

> "Pulse is good for visualizing, but as soon as we want to combine it with our internal data, I export everything to CSV and move it into our data warehouse."

The reasons differ, and that is the main nuance. Claire's export is driven by distrust: she rebuilds the report so she can cross-check the figures (see [[trust-in-pulse-numbers-depends-on-context-the-tool-does-not]]). Karim's export is driven by integration: he trusts the numbers but needs them next to other data, and Pulse offers no API. His workaround is also fragile: it broke twice this quarter after interface changes and runs on his personal login [[the-export-script-breaks-whenever-the-interface-changes]] [[the-automated-export-depends-on-one-analysts-personal-login]]. His top request is *a real API or a scheduled export to a bucket* [[a-real-api-or-scheduled-export-is-the-top-time-saving]]. The positive side is consistent too: Claire finds the dashboards really clear and her team opens the live delivery map every morning [[dashboards-are-perceived-as-clear-once-setup-is-done]] [[the-live-delivery-map-is-opened-daily-and-replaces-calling]], and Karim calls Pulse *good for visualizing*.

This matters because the time spent outside the tool (two hours every Monday for one participant, a self-maintained pipeline for the other) is effort Pulse does not capture, and it moves the reporting and analysis work elsewhere. With only two participants this is a strong signal rather than an established pattern.

## Evidence

- [[source-interview-claire-martin]] - exports to CSV and rebuilds the weekly management report in Excel, about two hours every Monday; values the dashboards and the live map.
- [[source-interview-karim-benali]] - exports everything to CSV for the BigQuery warehouse through a fragile nightly script; calls Pulse good for visualising; wants an API.

## Open questions

- How many other customers export to CSV regularly, and is the reason mostly distrust (Claire) or integration (Karim)?
- Would a scheduled export or API remove Claire's Excel rebuild, or would she still rebuild it until the trust issue is solved?
- Is the management report a job Pulse's built-in reports could take back with provenance and custom layouts?
