---
title: "The automated export depends on one analyst's personal login"
date_created: 2026-11-04
date_modified: 2026-11-04
type: insight
status: validated
tags: [workaround, integration]
related: []
source_ref: "sources/source-interview-karim-benali.md"
confidence: medium
author: verbatim
participant: "Karim Benali"
company: "Fretto"
kind: implicit-need
---

The participant states that the script logs in with his own account to download the CSV. He did not raise this as a problem; the inference is that the pipeline is tied to one person's credentials, which points to an unspoken need for service accounts or token-based access for automated jobs.

> "It logs in with my account, downloads the CSV and pushes it into BigQuery."
> - Karim Benali, [[interview-karim-benali]]

## Connections
- extends [[a-homemade-nightly-script-works-around-the-missing-export]] - how the workaround authenticates
