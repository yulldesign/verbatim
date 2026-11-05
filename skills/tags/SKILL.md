---
name: tags
description: Clean up the tag taxonomy of the Verbatim research vault - list tag usage, auto-group typographic variants (ux / UX / user_experience, workflow / workflows), propose semantic clusters with a canonical name while keeping different analytical signals apart (time-waste vs time-saving), and rewrite tags across all notes after approval. Use for /verbatim:tags, "clean the tags", "harmonize the tags", "too many tags", "tag consolidation", or when queries and filters miss notes because of inconsistent tags.
argument-hint: "[--apply-typographic]"
---

# Verbatim tags

Tag consolidation works in two layers. Typographic grouping is safe and mechanical;
semantic grouping is a judgment call, so it is only ever proposed, never applied silently.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. Inventory

`<script> tags` -> usage counts and `typographic_groups` (lowercase, separators and plural normalised).
Show the top tags and the count of distinct tags; flag tags outside the config `taxonomy`.

## 2. Semantic layer

The list of tags is short, so do this inline (no sub-agent needed unless there are several hundred tags).
Group tags that a researcher could merge under one label without losing meaning. Be precise, not eager:

- Do **not** group different valence: `time-waste` (pain) vs `time-saving` (benefit).
- Do **not** group phase vs moment: `onboarding` vs `first-use`.
- Do **not** group cause vs consequence: `pricing` vs `churn-risk`.
- Safe: `ux`, `user-experience`, `user experience` -> `ux`; `price`, `pricing`, `cost` -> `pricing`;
  `sign-up`, `signup` -> `signup`; French/English twins (`tarif`, `pricing`) -> the taxonomy's spelling.

Canonical name: the taxonomy spelling if one exists, else the most used variant, else the clearest one.

## 3. Approve

Present typographic groups first (recommend accepting them all), then semantic groups one per line with
the reason. The user accepts, rejects, or renames the canonical per group (AskUserQuestion with
"accept all typographic + choose semantic" as the recommended option).

## 4. Apply

Markdown: one command stages the whole rewrite:
`<script> retag --map "user-experience=ux" --map "UX=ux" ... --label "tags <today>"`
It prints the job id; continue with **verbatim:review** (show the mapping and the number of notes touched,
not every file).

Notion: update the `Tags` property of each affected page with `notion-update-page` after approval,
then remove the obsolete select options only if the user asks.

Finally, if a canonical tag is not in `taxonomy`, offer to add it to `verbatim.config.json` so future
ingests use it.
