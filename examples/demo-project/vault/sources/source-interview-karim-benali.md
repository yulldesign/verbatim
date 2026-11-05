---
title: "Source: interview-karim-benali"
date_created: 2026-11-04
date_modified: 2026-11-04
type: source
status: validated
tags: [integration, workaround, trust, pricing, feature-request]
related: []
source_ref: "raw/interview-karim-benali.md"
confidence: high
author: verbatim
participant: "Karim Benali"
company: "Fretto"
role: "Data analyst"
segment: "Technical user / data team at a small startup"
---

## Summary

Karim Benali is a data analyst at Fretto, a last-mile delivery startup of about forty people, interviewed on 2026-10-17 about the Pulse reporting tool. He builds dashboards for ops teams and customers, but relies on CSV exports and a fragile homemade nightly script to get Pulse data into BigQuery because there is no API. He trusts the numbers but finds metric definitions unclear, and guest-account pricing forces Fretto to limit customer access to dashboards.

## Themes

- Missing API pushes users to brittle export workarounds
- Unclear metric definitions, not inaccurate numbers, undermine shared understanding
- Fast setup for teams with developers
- Guest-account pricing limits sharing with customers

## Participant profile

Technical, self-sufficient data analyst who values Pulse for visualisation but works around its limits for data integration and customer sharing.

## Key quote

> "When Pulse changes something in the interface, it breaks. That happened to me twice this quarter."

## Insights

- [[data-is-exported-to-csv-and-moved-into-the-warehouse-to]]
- [[a-homemade-nightly-script-works-around-the-missing-export]]
- [[the-export-script-breaks-whenever-the-interface-changes]]
- [[the-automated-export-depends-on-one-analysts-personal-login]]
- [[a-real-api-or-scheduled-export-is-the-top-time-saving]]
- [[the-numbers-are-trusted-as-accurate]]
- [[unclear-metric-definitions-lead-each-team-to-interpret-them]]
- [[users-want-a-glossary-of-metrics-inside-the-tool]]
- [[teams-with-in-house-developers-set-up-the-integration-in-one]]
- [[setup-is-expected-to-be-harder-for-companies-without-a]]
- [[guest-accounts-billed-as-paying-users-limit-sharing-with]]
- [[dashboard-access-is-what-customers-value-most]]
