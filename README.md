# Verbatim

**User research with Claude.** · [github.com/yulldesign/verbatim](https://github.com/yulldesign/verbatim)

Verbatim is a Claude Code plugin that turns interview transcripts into a structured, linked and
verifiable knowledge base. You get atomic insights with exact quotes, participant profiles,
cross-interview themes, a health audit, an affinity map, natural-language questions and readouts for
stakeholders.

Your data stays **with you**: a local Markdown folder (readable in Obsidian) or a **Notion** database.
Nothing enters the knowledge base without your approval, and every quote is checked word for word against
the original transcript. Hence the name.

```
/verbatim:ingest interviews/        ->  ~13 insights per interview, quotes verified, waiting for review
/verbatim:review                    ->  you accept, edit or refuse
/verbatim:query what undermines trust in the numbers?
                                    ->  a cited answer, plus what the research does not cover
```

---

## Contents

1. [What Verbatim does](#1-what-verbatim-does)
2. [Requirements](#2-requirements)
3. [Installation](#3-installation)
4. [Get started in 5 minutes](#4-get-started-in-5-minutes)
5. [Try the demo project](#5-try-the-demo-project)
6. [Command reference](#6-command-reference)
7. [How it works](#7-how-it-works)
8. [The data](#8-the-data)
9. [Markdown, Obsidian or Notion](#9-markdown-obsidian-or-notion)
10. [Configuration](#10-configuration)
11. [The `verbatim.py` script](#11-the-verbatimpy-script)
12. [Privacy](#12-privacy)
13. [Permissions and cost](#13-permissions-and-cost)
14. [Troubleshooting](#14-troubleshooting)
15. [Developing the plugin](#15-developing-the-plugin)
16. [License](#license)

---

## 1. What Verbatim does

| What the researcher needs | Command | What happens |
|---|---|---|
| Import interviews | `/verbatim:ingest` | One subagent per transcript, in parallel: verbatim copy, source summary, 5 to 15 insights with quote, confidence and tags |
| Stay in control | `/verbatim:review` | Every proposal waits for your approval; diffs for changes; partial approval |
| Ask a question | `/verbatim:query` | An answer drawn only from the knowledge base, cited, with participant counts and blind spots |
| Find the themes | `/verbatim:synthesis` | Patterns backed by at least two interviews, with evidence, counter-examples and open questions |
| Audit the research | `/verbatim:health` | A score out of 100: orphans, broken links, altered quotes, tensions between insights, gaps |
| Remove duplicates | `/verbatim:merge` | Semantic detection of real duplicates; merges keep every participant and every quote |
| Clean up tags | `/verbatim:tags` | Typographic and semantic variants, notes rewritten after approval |
| Affinity map | `/verbatim:canvas` | Sticky notes grouped into clusters; HTML board and a draggable Obsidian canvas |
| Who said what | `/verbatim:directory` | Participants and companies, interview dates, profiles, quotes |
| Scope a study | `/verbatim:projects` | Filtered subsets, locking, activity feed (saturation, patterns) |
| See the links | `/verbatim:graph` | Interactive graph, index, typed connection pass between insights |
| Share | `/verbatim:export` | CSV, graph, canvas, readout with optional pseudonymisation |
| Overview | `/verbatim:home` | Project dashboard and the recommended next step |

Three guarantees hold across every workflow:

- **Nothing is written without you.** Every proposal goes through a staging area (`.verbatim/staging/`)
  before it enters the knowledge base.
- **The evidence can be checked.** Every quote must appear word for word in the transcript, and every link
  must point to an existing note. A script checks this before anything is approved.
- **What was said stays separate from what was inferred.** Analyst inferences carry `low` or `medium`
  confidence and are flagged as such.

## 2. Requirements

- **Claude Code** with plugin support (desktop app, CLI or IDE extension). Tested with version 2.1.300.
- **Python 3.9 or later**, available as `python` or `python3`. The script uses only the standard library:
  nothing to install.
- **Optional**: the **Notion** connector, to store the research in Notion. Add it in Claude with `/mcp` or in
  the app's connectors.
- **Optional**: [Obsidian](https://obsidian.md), to browse the Markdown vault, its graph and the affinity map.

## 3. Installation

This repository is itself the plugin, and it carries a marketplace manifest (`.claude-plugin/marketplace.json`)
that lists it. Pick one of three methods.

### A. From GitHub (recommended)

In a Claude Code session, one command:

```
/plugin install verbatim --marketplace yulldesign/verbatim
```

Or in two steps:

```
/plugin marketplace add yulldesign/verbatim
/plugin install verbatim@verbatim
```

From a terminal, the same operations are:

```bash
claude plugin marketplace add yulldesign/verbatim
```

```bash
claude plugin install verbatim@verbatim
```

### B. From a local clone

Point the marketplace at the folder that holds this README:

```
/plugin marketplace add "/path/to/verbatim"
/plugin install verbatim@verbatim
```

Add `--scope project` to `claude plugin install` to enable the plugin for one project only, instead of for all
your projects (the default `user` scope).

### C. Try it without installing

```bash
claude --plugin-dir /path/to/verbatim
```

The plugin is loaded for this session only. Point `--plugin-dir` at the repository folder: it is the plugin.

### Check, update, uninstall

| Action | In Claude Code | In a terminal |
|---|---|---|
| List installed plugins | `/plugin` | `claude plugin list` |
| Show components and their cost | | `claude plugin details verbatim` |
| Update | `/plugin` | `claude plugin marketplace update verbatim`, then `claude plugin update verbatim` |
| Disable / enable | `/plugin` | `claude plugin disable verbatim` / `claude plugin enable verbatim` |
| Uninstall | `/plugin` | `claude plugin uninstall verbatim` |

Once installed, type `/verbatim:` and the 14 commands appear in the menu.

## 4. Get started in 5 minutes

1. **Create a folder for your study** and open it in Claude Code. One folder per study or per product is the
   simplest model.

2. **Set up the project**:

   ```
   /verbatim:setup
   ```

   Three questions: storage (local Markdown or Notion), language of the notes, review mode. Verbatim writes
   `verbatim.config.json` and creates the vault.

3. **Import interviews** as files, a folder, pasted text or Notion pages:

   ```
   /verbatim:ingest interviews/
   ```

   Accepted formats: `.txt`, `.md`, `.pdf`, `.docx`, `.vtt`, `.srt`, Notion pages, and notes from a connected
   meeting tool. One subagent analyses each transcript, in parallel.

4. **Review** what was proposed:

   ```
   /verbatim:review
   ```

   For each interview, Verbatim shows the source summary, the insights with their confidence, and the result of
   the quote check ("14/14 quotes found verbatim"). Accept everything, part of it, or edit before applying.

5. **Put it to work**:

   ```
   /verbatim:query which pain points come up with several participants?
   /verbatim:synthesis
   /verbatim:health
   ```

You don't need to remember the commands: describe what you want ("analyse these three interviews", "what is
missing from my research?") and Claude picks the right skill.

## 5. Try the demo project

`examples/demo-project/` is a complete project that the plugin generated from two fictional interviews about a
logistics reporting tool (`examples/transcripts/`). It contains:

- 2 transcripts, 2 source summaries and 23 insights (one of them a merge of two duplicates);
- 4 cross-interview themes, 2 saved queries (an answer and a research plan from the Health Check);
- a project, "Trust in the data";
- an affinity map with 6 clusters (HTML and Obsidian) and a Health Check report scored 75/100;
- exports: CSVs, graphs, and a pseudonymised readout.

Every quote in it is found word for word in the transcripts, and every link resolves. The whole demo was
generated by the plugin itself, run non-interactively with `skip_review` on; the config is back to review mode.

Open `examples/demo-project/` in Claude Code with the plugin installed, then:

```
/verbatim:home
/verbatim:query what do we know about the risk of customers leaving?
/verbatim:health
```

To start from scratch with the two transcripts, create an empty folder, run `/verbatim:setup`, then
`/verbatim:ingest <path>/examples/transcripts/`.

## 6. Command reference

Every command accepts free text after its name. Options in brackets are optional.

### `/verbatim:home`
Dashboard: number of notes by type, participants, companies, tags, pending reviews, last health score, then
the one or two most useful next steps. Outside a Verbatim project, it offers `/verbatim:setup`.

### `/verbatim:setup`
Creates or changes the configuration: Markdown or Notion storage, vault path, language of the notes, tag
taxonomy, review mode. For Notion, it creates the *Verbatim Notes* and *Verbatim Projects* databases with
their relations. An existing Obsidian folder of Markdown notes can be used as the vault.

### `/verbatim:ingest <files | folder | Notion URL | text> [--skip-review]`
Imports interviews. For each one:

- `raw/`: a byte-for-byte verbatim copy;
- `sources/`: a participant summary (summary, themes, profile, key quote);
- `insights/`: 5 to 15 atomic findings, each with its quote, its confidence (`high` / `medium` / `low`), its
  kind (`observation`, `quote`, `signal`, `implicit-need`) and its tags.

Quotes are checked before review. A transcript that was already imported is flagged, not duplicated.
After approval, Verbatim reports tags shared by several participants and the saturation signal.

```
/verbatim:ingest interviews/wave-2/
/verbatim:ingest https://www.notion.so/... --skip-review
```

### `/verbatim:review [job id]`
The review queue: lists pending proposals (imports, themes, merges, tags, answers, fixes), presents them by
type with their diffs, checks the quotes, then applies or refuses. Partial approval ("everything except 3 and
7"), edits before applying ("rename 2"). Deletions go to `.verbatim/trash/`, never a permanent delete.

### `/verbatim:query <question> [--project <name>] [--save]`
Answers from the knowledge base only:

- every claim is cited;
- it counts the participants who support each claim;
- it shows tensions between notes;
- it ends with a **Not covered** section, with the interview questions that would fill the gap.

Every answer is checked (quotes and links) before you see it; you then decide whether to keep it in `queries/`.
On a large knowledge base, a subagent does the research to keep the conversation light.

```
/verbatim:query who complains about pricing, and why?
/verbatim:query what do non-technical customers say about onboarding? --project onboarding
```

### `/verbatim:synthesis [--project <name>] [--focus <topic>]`
Cross-interview themes: a subagent looks for patterns present in at least two interviews, including splits
between segments. Each theme names its participants, its cited evidence, its exceptions and its open
questions. A new run does not repeat themes already in the knowledge base. Confidence is capped at `medium`
below four sources.

### `/verbatim:health [--project <name>] [--structural-only]`
An audit scored out of 100. Mechanical part (script): orphan insights, old `raw` notes, broken links, invalid
frontmatter, duplicate titles, altered quotes. Analytical part (subagent): tensions between insights and gaps in
the research. The report is kept in `.verbatim/health/`. Actions per finding:

- **Compare** two notes;
- **Query** the knowledge base;
- **Link** an orphan;
- **Validate** an old note;
- **Fix with Verbatim**: interview questions and participant profiles to recruit to close a gap.

### `/verbatim:merge [--project <name>]`
Duplicates: a subagent finds insights that really say the same thing, ruling out cause-and-effect pairs and
corroboration between participants. Word-overlap similarity (Jaccard) is the fallback. Group by group: merge,
keep one, keep both, skip. A merge keeps every participant and every quote, rewrites the links that pointed to
the originals, and moves the originals to the trash.

### `/verbatim:tags`
Tag inventory. Typographic variants (`UX`, `user_experience`) are grouped automatically. Semantic groupings are
only proposed, with safeguards: `time-waste` and `time-saving` stay separate. Once approved, the rewrite goes
through review.

### `/verbatim:canvas [--project <name>] [--clusters N]`
Affinity map: a subagent sorts the insights into 3 to 8 named, coloured clusters, each insight in exactly one
cluster. After approval:

- an HTML board (`graph/canvas.html`);
- an Obsidian canvas (`graph/affinity.canvas`) where the sticky notes can be dragged around.

Adjust it in conversation: "move X to Y", "split this cluster".

### `/verbatim:directory [name]`
Participants and companies: number of notes, interview dates, profiles, key quotes, themes they support.
Navigation from a company to its participants. Handles the multi-name fields that merges produce.

### `/verbatim:projects [list | new | show | edit | lock | unlock | activity] [name]`
A project is a research question plus a filtered subset of the knowledge base: types, tags, participants,
companies, dates, and manual inclusions and exclusions. `lock` freezes the scope of a delivered study.
`activity` gives the event feed: imports, shared patterns, saturation, confidence upgrades, tensions. Every
other command accepts `--project <name>`.

### `/verbatim:graph [view | index | connect] [--project <name>]`
- `view`: interactive HTML graph (colour by type, click to open a note), hubs and orphans.
- `index`: rebuilds `graph/index.md`.
- `connect`: proposes typed links between insights (`supports`, `contradicts`, `extends`, `contextualizes`).

### `/verbatim:export [csv | graph | canvas | readout] [--project <name>]`
Everything goes to `exports/`:

- **CSV**: Excel-compatible, accents included.
- **Graph and canvas**: standalone HTML pages.
- **Readout**: a document for stakeholders, with context, findings and quotes, tensions, gaps and the next
  step. It can be pseudonymised (P1, P2…). Its quotes and links are checked, and it is checked again so that no
  name or company remains.

### Internal skill: `verbatim:vault`
This is not a command. The skill holds the data model, the review protocol and the script reference; every
other skill and every subagent relies on it.

## 7. How it works

```
             you ──► /verbatim:ingest a.md b.md c.md
                         │
         ┌───────────────┼───────────────┐      one subagent per transcript, in parallel
         ▼               ▼               ▼
  transcript-analyst  transcript-analyst  transcript-analyst
         │  writes to .verbatim/staging/<job>/files/ ... then verify-quotes + seal
         ▼
  /verbatim:review ──► you approve ──► verbatim.py staging apply ──► vault/ (or Notion)
                                                                    + index rebuilt
```

**Skills** (`skills/`): one per workflow. They describe the method, the questions to ask and
the checks to run.

**Subagents** (`agents/`): they do the heavy work outside the main conversation, often in
parallel. They only propose; only the main conversation applies, after your approval.

| Agent | Role | Started by |
|---|---|---|
| `verbatim:transcript-analyst` | Turns one transcript into a source summary and insights, quotes verified | ingest |
| `verbatim:researcher` | Evidence retrieval and a cited answer, read-only | query |
| `verbatim:synthesizer` | Cross-interview themes from 2 or more sources | synthesis |
| `verbatim:auditor` | Tensions and gaps, read-only | health |
| `verbatim:curator` | Duplicates, merges, typed connections | merge, graph |
| `verbatim:clusterer` | Affinity map | canvas |

**Script** (`skills/vault/scripts/verbatim.py`): everything that must be exact rather than
plausible. It counts, checks links and frontmatter, finds duplicates by similarity, groups tags, applies staging
jobs, verifies quotes and exports. It runs instantly and uses no tokens.

**Review.** A staging *job* is a folder:

```
.verbatim/staging/20261104-101500-ingest-interview-marie/
├── job.json      create / modify / delete operations and the state of each
├── files/        the proposed notes, at the path they will have in the vault
└── delete.txt    proposed deletions (optional)
```

On apply, the script checks that the vault has not changed since the proposal (otherwise it asks), copies the
files, moves deletions to the trash and rebuilds the index.

## 8. The data

### The Markdown vault

```
vault/
├── raw/          transcripts, verbatim
├── sources/      one summary per interview
├── insights/     atomic findings
├── synthesis/    cross-interview themes
├── queries/      saved answers, research plans
├── projects/     project definitions (+ per-project affinity maps)
├── graph/
│   ├── index.md          map of the knowledge base, rebuilt automatically
│   ├── canvas.json       affinity map (the record)
│   ├── canvas.html       HTML board
│   └── affinity.canvas   Obsidian canvas
└── VERBATIM.md   vault marker (stable identifier)
```

### Frontmatter

```yaml
---
title: "Exports are rebuilt by hand every Friday"
date_created: 2026-11-04
date_modified: 2026-11-04
type: insight            # transcript | source | insight | synthesis | query-output | project
status: validated        # raw | processing | validated | final
tags: ["workaround", "pain-point"]
related: []
source_ref: "sources/source-interview-marie.md"
confidence: high         # high | medium | low
author: verbatim         # human | verbatim
participant: "Marie Dupont"
company: "Acme"
kind: observation        # observation | quote | signal | implicit-need
---
```

Conventions that matter:

- **An insight's title is the finding itself** ("exports are rebuilt by hand"), not a topic ("exports"). It does
  not contain the participant's name.
- **Quotation marks are reserved for participants' words.** Titles and terms go in *italics*. This is what makes
  every quote checkable.
- **Links** are written `[[slug]]`, Obsidian-compatible. The slug is the file name without `.md`.
- **After a merge, `participant` and `company` can hold several names**, separated by commas.
- **Confidence**: `high` = stated explicitly and backed up (a concrete example or repetition), `medium` = stated
  once or clearly implied, `low` = the analyst's inference.

Full templates for every note type are in `skills/vault/references/note-formats.md`.

## 9. Markdown, Obsidian or Notion

**Markdown (default).** The `vault/` folder is the source of truth: plain text files, private, usable offline,
easy to version. Open it in **Obsidian** for the graph view, backlinks and the draggable canvas. No database to
maintain.

**Notion.** For teams that already work in Notion. `/verbatim:setup` creates, under a page of your choice:

- **Verbatim Notes**: every note, with the *Source*, *Derived notes* and *Related* relations;
- **Verbatim Projects**: the projects, with *Included*, *Excluded* and *Snapshot*.

Proposals are still staged locally, then written to Notion after your approval. For analysis, Verbatim exports
the database to a local cache (`.verbatim/cache/notes.json`) that the script can read.

What changes with Notion:

- quotes are checked on the local job, before anything is written;
- deletions go through the Notion trash;
- there is no Obsidian canvas; it is replaced by one page per cluster.

Technical details are in `skills/vault/references/backend-notion.md`.

## 10. Configuration

`verbatim.config.json`, at the root of the project. It is created by `/verbatim:setup` or by `verbatim.py init`.

```json
{
  "backend": "markdown",
  "vault_path": "vault",
  "output_language": "auto",
  "skip_review": false,
  "stale_days": 30,
  "taxonomy": ["pain-point", "feature-request", "workaround", "onboarding", "pricing", "performance", "ux",
               "integration", "trust", "churn-risk", "delight", "job-to-be-done", "process", "expectation-gap"],
  "notion": { "notes_data_source": "", "projects_data_source": "", "parent_page": "" }
}
```

| Key | Role |
|---|---|
| `backend` | `markdown` or `notion` |
| `vault_path` | Vault folder, relative to the config. With Notion, it is used for local exports |
| `output_language` | `auto` (the language of each transcript), `en`, `fr`… Quotes always stay in their original language |
| `skip_review` | `true`: proposals are applied without review, with a summary of what was written |
| `stale_days` | Age after which a `raw` note is flagged by the Health Check |
| `taxonomy` | Allowed tags. Adapt it to your domain; a tag outside the list is flagged |
| `notion.*` | IDs of the two databases and of the parent page, filled in by `/verbatim:setup` |

Several studies: one folder, and therefore one config, per study. Or several vaults through `vault_path`.

## 11. The `verbatim.py` script

The skills call it for you, but you can also run it by hand from a project:

```bash
python "<plugin>/skills/vault/scripts/verbatim.py" --help
```

`<plugin>` is the installed plugin's folder; `claude plugin details verbatim` tells you where it is.

| Command | Role |
|---|---|
| `init [vault]` | Creates the config if missing, the folders, `VERBATIM.md` and the index |
| `stats [--json]` | Counts by type, participants, companies, tags, pending reviews |
| `scan [--type T …] [--grep REGEX] [--full] [--excerpt N]` | Notes as JSON |
| `people [--name X]` / `companies [--name X]` | Directory, interview dates, notes per person |
| `links` | Derived links and broken references |
| `lint [--stale-days N]` | Structural check |
| `verify-quotes <job \| file \| folder>` | Quotes found word for word and links resolving; `verify-quotes vault` audits the whole knowledge base |
| `dedup [--threshold 0.22]` | Near-duplicates by similarity |
| `tags` / `retag --map old=new` | Tag usage, staged rewrite |
| `staging new \| seal \| list \| show \| apply \| refuse` | The review queue (`--only`, `--exclude`, `--diff`, `--force`, `--mark-only`) |
| `stage-raw <job> <file> --stem S …` | Copies a transcript unchanged into a job |
| `index` | Rebuilds `graph/index.md` |
| `patterns [--since DATE]` | Tags shared across participants, saturation signal |
| `project list \| resolve \| snapshot` | A project's scope |
| `canvas-check` / `canvas-html` / `canvas-obsidian` | Validate and render the affinity map |
| `export-csv` / `graph-html` | Exports |
| `notion-cache <rows.json …>` | Notion backend: turns a database export into the local cache |
| `session-context` | The project rules and a one-line status, on demand |
| `slug "<title>"` | File name for a note |

The global option `--notes-json <file>` runs the read commands on the Notion cache.

## 12. Privacy

Interviews contain personal data. Verbatim sends them nowhere except where you work: your disk, and Claude
during the session.

Two things do leave the machine, both because you asked for them. If you choose the **Notion** backend, your
notes are written to your own Notion workspace, through the connector you authorized in Claude. And the page
produced by `graph-html` loads the d3 library from `cdnjs.cloudflare.com` when you open it in a browser: that
is a library download, nothing of your research is sent with it. The Python script itself opens no network
connection, ever. For a study versioned with git, add to its `.gitignore`:

```gitignore
.verbatim/
vault/raw/
vault/sources/
vault/insights/
vault/synthesis/
vault/queries/
exports/
```

The readout offers to **pseudonymise** participants (P1, P2…) before it leaves the team. It then checks that
no name or company remains, including in links.

The full policy - what Verbatim reads, what it stores and where, what it never sends - is in
[PRIVACY.md](PRIVACY.md).

## 13. Permissions and cost

**Permissions.** Claude asks for permission before running the script and writing to `.verbatim/`. To stop the
prompts in a study project, add to its `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(python *verbatim.py*)",
      "Bash(python3 *verbatim.py*)",
      "Write(./.verbatim/**)",
      "Write(./exports/**)"
    ]
  }
}
```

**Cost.** The descriptions of the skills and agents take about 3,400 tokens in every session where the plugin is
enabled. The full content of a skill is only loaded when it is used. An import costs one subagent per
transcript. Disable the plugin (`claude plugin disable verbatim`) in projects that don't need it.

## 14. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `/verbatim:` shows nothing | Plugin not installed or disabled: `/plugin`, then `/reload-plugins` |
| "python not found" | Install Python 3.9+, or check that `python3` is on the PATH (macOS/Linux) |
| "vault not found" | No config in this folder or above: `/verbatim:setup` |
| A quote is reported `NOT FOUND` | The text differs from the transcript (paraphrase, adapted words). Fix the quote or remove the quotation marks |
| `BROKEN LINK` | The `[[link]]` points to a missing note, often after a merge or a rename. `/verbatim:health` proposes the fix |
| `apply` skips files | The note changed in the vault since the proposal. Read the diff, then rerun with `--force` if that is intended |
| Notion: tools missing | Connect the Notion connector (`/mcp`), then rerun `/verbatim:setup` |

## 15. Developing the plugin

```
verbatim/                        repository root = the plugin, and its marketplace
├── .claude-plugin/
│   ├── plugin.json              plugin manifest
│   └── marketplace.json         marketplace manifest (source: "./")
├── skills/                      14 commands + vault (model, references, script)
├── agents/                      6 subagents
├── PRIVACY.md                   privacy policy
├── examples/
│   ├── transcripts/             fictional interviews, useful as test cases
│   └── demo-project/            a full project generated by the plugin
└── LICENSE                      MIT
```

Development loop:

```bash
claude plugin validate .
```

```bash
claude --plugin-dir .
```

In the session, `/reload-plugins` reloads the plugin after a change. The transcripts in `examples/transcripts/`
make good test cases for `verbatim:ingest`.

Design rules to keep:

- a skill stays under 500 lines, and the detail goes into `references/`;
- anything that must be exact goes through the script;
- paths use `${CLAUDE_PLUGIN_ROOT}`;
- the contract of the `verbatim:vault` skill stays stable, since every other component depends on it.

## License

Verbatim is released under the **MIT** license: see [LICENSE](LICENSE).
