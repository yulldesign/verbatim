---
name: graph
description: Knowledge graph of the research vault - rebuild graph/index.md, render an interactive force graph (HTML, colour by note type, synthesis in fuchsia), report hubs, isolated notes and broken links, and run a connection pass that proposes typed links (supports, contradicts, extends, contextualizes) between insights. Use for /verbatim:graph, "show the graph", "visualise the research", "rebuild the index", "connect the insights", "link the notes", "what's connected to X", or when notes look isolated.
argument-hint: "[view | index | connect] [--project <name>]"
---

# Verbatim graph

The graph is the vault's links made visible: insight -> source -> transcript via `source_ref`,
synthesis -> evidence via `related`, and `[[wikilinks]]` in bodies.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## view (default)
1. `<script> graph-html --out exports/graph.html` (add `--project <name>`; Notion: `--notes-json`).
2. Open it for the user: on Windows `start "" exports/graph.html`, macOS `open`, Linux `xdg-open` -
   or give the path. Nodes: blue transcript, amber source, green insight, fuchsia synthesis, slate query;
   size grows with connections; click opens the note.
3. Summarise from `<script> links`: number of edges, the 5 most connected notes (hubs), insights with no
   edges, broken references. Mention that Obsidian's graph view works on the same vault.

## index
`<script> index` rebuilds `graph/index.md` (sources with their insights, themes, queries, projects).
It is derived data, regenerated after every apply - run it by hand only after editing notes outside Verbatim.

## connect
The connection pass, for vaults whose insights were never linked to each other:
1. Pick the insights with no `## Connections` section (`<script> scan --type insight --grep "Connections"`
   gives the ones that have it), or the ones the user names.
2. Spawn the `verbatim:curator` sub-agent in *connect* mode with those insights and the index. For each one it
   proposes links to existing insights with a relationship - `supports`, `contradicts`, `extends`,
   `contextualizes` - and a one-line reason, only where the link is meaningful.
3. It stages modified copies that add a section at the end of the body:
   ```
   ## Connections
   - supports [[other-insight]] - both describe manual export rework
   - contradicts [[x]] - Lea automates it fully
   ```
   and adds the targets to `related`. Apply through **verbatim:review**; `contradicts` links are worth flagging
   to the user, they feed the Health Check.
