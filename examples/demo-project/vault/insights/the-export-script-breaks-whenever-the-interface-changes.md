---
title: "The export script breaks whenever the interface changes"
date_created: 2026-11-04
date_modified: 2026-11-04
type: insight
status: validated
tags: [pain-point, workaround]
related: []
source_ref: "sources/source-interview-karim-benali.md"
confidence: high
author: verbatim
participant: "Karim Benali"
company: "Fretto"
kind: observation
---

The nightly export script depends on the Pulse interface, so any UI change breaks it; this happened twice in the current quarter. Interface updates that look harmless to Pulse silently break customers' data pipelines, which (inference) can erode confidence in Pulse as a data source.

> "When Pulse changes something in the interface, it breaks. That happened to me twice this quarter."
> - Karim Benali, [[interview-karim-benali]]

## Connections
- extends [[a-homemade-nightly-script-works-around-the-missing-export]] - the fragility of that workaround
