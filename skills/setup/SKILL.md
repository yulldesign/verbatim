---
name: setup
description: Set up or reconfigure the Verbatim research vault - choose local Markdown or Notion as storage, create the folder structure or the Notion databases, set output language, tag taxonomy and review mode, or point Verbatim at an existing vault (such as an Obsidian folder). Use for /verbatim:setup, "configure Verbatim", "use Notion for my research", "change vault", "new workspace", "switch workspace", or whenever verbatim.config.json is missing.
---

# Verbatim setup

Goal: a valid `verbatim.config.json` at the project root and an initialised vault.
Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` for the schema. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. Ask only what you cannot infer

If a config exists, show it and ask what to change. Otherwise ask, in one AskUserQuestion call:

1. **Storage** - Local Markdown folder (recommended: private, works offline, opens in Obsidian) or Notion (shared with a team).
2. **Language of generated notes** - same as each transcript (auto), French, English.
3. **Review mode** - review every proposal (recommended) or auto-apply ("skip review").

Defaults for the rest: `vault_path: "vault"`, `stale_days: 30`, Verbatim's taxonomy:
`pain-point, feature-request, workaround, onboarding, pricing, performance, ux, integration,
trust, churn-risk, delight, job-to-be-done, process, expectation-gap`. Offer to adapt the
taxonomy to their domain (e.g. B2B SaaS vs. consumer health) but do not force it.

## 2. Markdown backend

1. Ask for the vault path if they have one already (an existing Obsidian
   folder of Markdown notes works too). Otherwise use `vault`.
2. From the project folder, run `<script> init` (or `<script> init <vault path>`): with no config yet, it writes
   a default `verbatim.config.json` (below), then creates the vault. Edit the config with the user's answers.
   The default config:

```json
{
  "backend": "markdown",
  "vault_path": "vault",
  "output_language": "auto",
  "skip_review": false,
  "stale_days": 30,
  "taxonomy": ["pain-point", "feature-request", "workaround", "onboarding", "pricing", "performance", "ux", "integration", "trust", "churn-risk", "delight", "job-to-be-done", "process", "expectation-gap"],
  "notion": {"notes_data_source": "", "projects_data_source": "", "parent_page": ""}
}
```

3. Re-running `<script> init` is safe: it only creates missing folders, `VERBATIM.md` and `graph/index.md`,
   never touching existing notes or an existing config.
4. For an existing vault: `<script> lint` and report schema problems in one line each; offer
   `/verbatim:health` rather than fixing silently.

## 3. Notion backend

1. Check the Notion tools are available (search for `notion-create-database`). If not, tell the
   user to connect the Notion connector with `/mcp` and stop.
2. Ask where to put Verbatim: a parent page (search it with `notion-search`) - or create a private
   page "Verbatim Research" if they have no preference.
3. Create **Verbatim Notes** and **Verbatim Projects** exactly as in
   `${CLAUDE_PLUGIN_ROOT}/skills/vault/references/backend-notion.md` section 1, then add the relations.
4. Create an "Verbatim Index" page under the parent with a short explanation.
5. Write `verbatim.config.json` with `"backend": "notion"` and the two `collection://` ids + parent page id.
   Keep `vault_path` - it is still used for local staging and HTML exports.
6. Run `<script> init` anyway: the local folder holds exports, and `.verbatim/` holds staging.

## 4. Finish

Show the resulting config, then the three things to try first:
`/verbatim:ingest <file or folder>`, `/verbatim:query <question>`, `/verbatim:home`.

Remind them, once, that `.verbatim/` (staging, trash, caches) and the vault can contain personal
interview data - keep them out of public git repos (`.gitignore` already covers `.verbatim/`).
