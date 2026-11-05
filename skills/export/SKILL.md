---
name: export
description: Export Verbatim research out of the vault - insights or any note type to CSV (Excel-friendly), the knowledge graph or affinity canvas to standalone HTML / Obsidian canvas, and a research readout document (themes, key insights with quotes, participants, gaps) for stakeholders, for the whole vault or a project. Use for /verbatim:export, "export to CSV", "export the insights", "make a research report", "readout for the PM", "share the findings", "download the canvas".
argument-hint: "[csv | graph | canvas | readout] [--project <name>]"
---

# Verbatim export

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.
Exports go to `exports/` at the project root (outside the vault, so they never pollute the evidence base).
Notion backend: build the cache and add `--notes-json` to script commands.

## csv
`<script> export-csv --out exports/insights-<today>.csv` (add `--type source --type synthesis`, `--project <name>`).
Columns: title, type, participant, company, confidence, status, tags, date_created, source, path, body.
UTF-8 with BOM so Excel opens accents correctly. Report the row count and path.

## graph
`<script> graph-html --out exports/graph-<today>.html [--project <name>]` - a self-contained page (loads D3
from cdnjs). Works offline except for that script.

## canvas
`<script> canvas-html --out exports/canvas-<today>.html` and/or `<script> canvas-obsidian`. For an image,
open the HTML in a browser and print to PDF; if the built-in browser tools are available, take a screenshot
of the page instead.

## readout
A stakeholder document built only from vault content - the researcher's voice, not marketing.

1. Gather: synthesis notes (scope), top insights by confidence and participant spread, `<script> people`,
   the latest `.verbatim/health/` gaps, project research question if any.
2. Structure:
   - Context: research question, method, N participants / companies, dates
   - Key findings: one section per theme - claim, how many participants, 1-2 quotes, implications
   - Tensions and open questions
   - Gaps and recommended next research
   - Appendix: participant table, list of sources
3. Every finding cites its notes (`[[slug]]` in the Markdown version). Ask whether participant names should
   be pseudonymised (P1, P2...) before writing - readouts often leave the research team.
4. Write `exports/readout-<scope>-<today>.md`, then check it before handing it over:
   `<script> verify-quotes exports/readout-<scope>-<today>.md` (quotes verbatim, citations resolve), and when
   pseudonymised, Grep the file for every participant and company name (`<script> people` / `companies`) and for
   tools that would identify them - none may remain. Do not cite source or transcript slugs in a pseudonymised
   readout: they contain the participant's name. Cite insights and themes instead. If the user wants a shareable page or doc, offer to turn it
   into one with the tools available (a Notion page under the Verbatim parent page with the Notion backend).
