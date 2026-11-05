---
title: "A homemade nightly script works around the missing export API"
date_created: 2026-11-04
date_modified: 2026-11-04
type: insight
status: validated
tags: [workaround, integration]
related: []
source_ref: "sources/source-interview-karim-benali.md"
confidence: high
author: verbatim
participant: "Karim Benali"
company: "Fretto"
kind: observation
---

Because Pulse has no API, the participant wrote a script that downloads the CSV export every night and pushes it into BigQuery. He calls it *a bit of a hack* himself. A user investing engineering time to automate around the product is a strong signal of an unmet integration need.

> "I even wrote a script that pulls the export every night, because there's no API for it."
> - Karim Benali, [[interview-karim-benali]]

## Connections
- contextualizes [[a-real-api-or-scheduled-export-is-the-top-time-saving]] - the workaround this request would replace
