---
title: "Research plan: which findings hold beyond a single participant?"
date_created: 2026-11-04
date_modified: 2026-11-04
type: query-output
status: validated
tags: [onboarding, trust, pricing, integration, workaround]
related: ["sources/source-interview-claire-martin.md", "sources/source-interview-karim-benali.md", "synthesis/onboarding-speed-depends-on-whether-the-customer-has-in.md", "synthesis/trust-in-pulse-numbers-depends-on-context-the-tool-does-not.md", "synthesis/per-user-pricing-restricts-sharing-dashboards-with-view-only.md", "synthesis/pulse-is-valued-for-viewing-data-but-reporting-and-analysis.md", "insights/connecting-the-tms-took-three-weeks-during-onboarding.md", "insights/teams-with-in-house-developers-set-up-the-integration-in-one.md", "insights/the-live-delivery-map-is-opened-daily-and-replaces-calling.md", "insights/the-numbers-are-trusted-as-accurate.md", "insights/pulse-numbers-do-not-always-match-the-carriers-data.md", "insights/per-user-pricing-charges-for-people-who-only-view.md", "insights/guest-accounts-billed-as-paying-users-limit-sharing-with.md", "insights/the-export-script-breaks-whenever-the-interface-changes.md"]
source_ref: ""
confidence: low
author: verbatim
participant: ""
company: ""
---

## Question

Which findings in the vault hold beyond a single participant, and who needs to be interviewed next to find out? This is the *Fix with Verbatim* follow-up to the top gap in the 2026-11-04 Health Check: *each segment rests on a single participant*.

## Answer

The vault rests on two interviews: Claire Martin, head of operations at Lumen Logistics (about 120 people, no technical staff) [[source-interview-claire-martin]], and Karim Benali, data analyst at Fretto (about 40 people, in-house developers) [[source-interview-karim-benali]]. Every contrast the four themes rely on lines up with that one split, so role, company size, technical capacity and the kind of sharing are all confounded.

- **Onboarding.** Three weeks to connect the TMS at Lumen [[connecting-the-tms-took-three-weeks-during-onboarding]] vs one afternoon at Fretto [[teams-with-in-house-developers-set-up-the-integration-in-one]]. The theme [[onboarding-speed-depends-on-whether-the-customer-has-in]] attributes this to technical staff, but company size or the integration type could explain it just as well.
- **Trust in the numbers.** Claire saw a delay-rate gap with the carrier [[pulse-numbers-do-not-always-match-the-carriers-data]]:

  > "The director asked me where the gap came from and I had no answer. Since then, I don't trust the numbers until I've cross-checked them myself."

  Karim has never seen a discrepancy [[the-numbers-are-trusted-as-accurate]]. With one person on each side, the theme [[trust-in-pulse-numbers-depends-on-context-the-tool-does-not]] cannot say whether distrust is typical of ops leads or specific to one incident.
- **Pricing for viewers.** Both object to per-seat billing for people who only view [[per-user-pricing-charges-for-people-who-only-view]] [[guest-accounts-billed-as-paying-users-limit-sharing-with]]:

  > "The price is fine. What bothers me is paying per user when half the people only look."

  This is the best-corroborated theme [[per-user-pricing-restricts-sharing-dashboards-with-view-only]], yet the internal audience (a CFO) and the external one (customers) each have one case.
- **Work done outside Pulse.** Both export to CSV, for different reasons [[pulse-is-valued-for-viewing-data-but-reporting-and-analysis]]. The fragility of the workaround comes from Karim alone [[the-export-script-breaks-whenever-the-interface-changes]]:

  > "When Pulse changes something in the interface, it breaks."

- **Core value.** The live delivery map is the strongest positive signal, but only Claire mentions it [[the-live-delivery-map-is-opened-daily-and-replaces-calling]].

### Who to recruit (6-8 interviews)

To break the confound, each combination needs at least two people:

1. **2 ops leads at companies with in-house technical staff.** This separates role from technical capacity on trust and reporting.
2. **2 data or technical users at companies without a dedicated data team.** This separates technical capacity from company size on onboarding.
3. **1-2 more customers without technical staff, ideally of a different size than Lumen.** This tests whether long, support-dependent setup is the norm.
4. **1-2 customers who share dashboards externally with their own clients.** This tests whether customer-facing sharing is a separate use case.

Screen for the role, company size, whether there are in-house developers, the integration used (TMS or other), the number of view-only users, and any external sharing. Recruit current customers who have used Pulse for at least three months.

### Interview questions (open, non-leading)

1. Walk me through the last time you set Pulse up or connected a new data source. Who was involved, and what happened at each step?
2. Tell me about the last time you used a Pulse number outside Pulse: in a report, a meeting, or another tool. What did you do with it before passing it on?
3. Has a figure in Pulse ever surprised you? What did you do next?
4. Who in your organisation looks at Pulse data without working in it, and how does it reach them today?
5. Which screen or feature do you open first on a normal day, and what would you do if it disappeared?

## What the vault does not cover

- No second case on either side of any split, so no theme can yet be confirmed or refuted.
- Nothing on how often each pain occurs across accounts: the share of view-only seats, how many accounts cap viewers, how often export scripts break.
- No interviews with view-only stakeholders or end customers.
- The root cause of the 4% vs 7% gap: a data error, sync lag or a different definition of a *delay*. It can be settled by checking that one incident, without new interviews.

Sources: [[source-interview-claire-martin]], [[source-interview-karim-benali]]
