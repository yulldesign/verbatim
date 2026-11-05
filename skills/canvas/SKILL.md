---
name: canvas
description: Affinity mapping of research insights - a sub-agent clusters insights into 3-8 labelled, coloured groups the way a researcher sorts post-its, saved as graph/canvas.json and rendered as an HTML board and an Obsidian canvas you can drag around; clusters can then be renamed, split, merged or reshuffled in conversation. Use for /verbatim:canvas, "affinity map", "cluster the insights", "make a sticky-note wall", "group findings", "affinity diagram", or before a synthesis workshop.
argument-hint: "[--project <name>] [--clusters N]"
---

# Verbatim canvas

Clustering is a first draft for the researcher to rework, so the output
must be easy to adjust - by chat here, or by dragging cards in Obsidian.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. Cluster

- Scope: all insights (`<script> scan --type insight`), or a project (`<script> project resolve <name>`).
  Fewer than 4 insights: say a canvas is not useful yet.
- `<script> staging new --kind canvas --label "<scope>"`.
- Build the agent's input with `<script> scan --type insight --excerpt 200` (filtered to the project's
  paths if scoped) and pass path, title, excerpt, tags and participant for each insight - titles alone
  make the agent open notes one by one.
- Spawn the `verbatim:clusterer` sub-agent with the job folder, that list, the target file (`graph/canvas.json`,
  or `projects/<slug>.canvas.json` for a project), the scope name, `output_language` (resolve `auto` to the
  language of the insights) and `--clusters N` if given. It writes the canvas JSON (format in `${CLAUDE_PLUGIN_ROOT}/skills/vault/references/note-formats.md`)
  into the job, seals, and returns the cluster summary.

## 2. Review

First `<script> canvas-check --canvas <job>/files/<target file>` (add `--project`): every insight placed once,
known colours. Then show the board as text - one block per cluster: label, colour, count, rationale, card titles with
participant. Then **verbatim:review** (it is a single file; an overwrite of an existing canvas shows as `modify`).

## 3. Render

After apply:
- `<script> canvas-html` (or `--canvas projects/<slug>.canvas.json`) -> an HTML board next to the JSON.
- `<script> canvas-obsidian` (same option) -> a `.canvas` file: open the vault in Obsidian to drag cards
  between groups. Tell the user both paths.
- Markdown backend only for Obsidian; with Notion, offer to create a page "Affinity map - <scope>" with one
  heading per cluster and page mentions under each.

## 4. Adjust

Requests like "move 'Exports rebuilt by hand' to Workarounds", "split Onboarding in two", "rename cluster 3",
"merge Trust and Data quality" -> edit the JSON in a new canvas staging job, apply, re-render. Each insight
stays in exactly one cluster. If the user edited the `.canvas` in Obsidian, the JSON is the record: read
the `.canvas` group membership back into `canvas.json` when they ask to sync.
