# Privacy Policy

Last updated: 2026-11-05

Verbatim is a Claude Code plugin made of skills, agents, reference files, a local Python script and a
session-start hook. It has no server, no account, no telemetry and no analytics. The author receives no data
from people who use it.

## What the plugin reads

- The transcript files you hand to `/verbatim:ingest`, wherever they are on your disk, and text you paste
  into the conversation (saved to `.verbatim/inbox/` so every transcript has a path). Interview material
  contains personal data: names, job titles, employers, and whatever participants said about themselves.
- Your vault: the Markdown files in your project folder (Markdown backend) or the Notion pages and databases
  you set up (Notion backend).
- `verbatim.config.json`, which holds your backend choice, vault path, output language, tag taxonomy, review
  mode and Notion ids.
- The plugin's own working folders under `.verbatim/`: staged proposals (`staging/`), the Notion cache
  (`cache/`), health reports (`health/`) and deleted notes (`trash/`).

Claude reads these files during your Claude Code session, under the terms that apply to your use of Claude.
The session-start hook runs the local script and prints a short status line into the session; it sends
nothing anywhere.

## What the plugin stores, and where

- **Markdown backend:** notes are written as Markdown files in your vault folder, on your machine.
- **Notion backend:** notes are written to your own Notion workspace through the Notion connector you
  installed and authorized. Notion's own privacy policy applies to that data. Verbatim never handles a Notion
  token or any other credential: it calls the connector you have already authorized in Claude.
- Exports (CSV, HTML graph, affinity map, readouts) are written where you ask, typically `exports/`.

**Verbatim keeps the record identifiable by design.** A transcript note in `vault/raw/` holds the full
transcript text, unchanged, and insight and source notes carry the real `participant` and `company` names in
their frontmatter. That is what makes quote verification and citation possible: the point of the tool is that
every claim can be traced back to who said it. Nothing is pseudonymised on the way in.

Pseudonymisation happens on the way out. When a readout leaves the research team, `/verbatim:export` offers
to replace participants with codes (P1, P2…) and then checks that no name, company or identifying detail
remains, including in links.

## What the plugin sends elsewhere

Nothing, apart from the Notion backend described above, which you choose and authorize yourself. The plugin
declares no connector of its own and calls no other external service. There is no network access in the
Python script.

## Retention and deletion

The plugin retains nothing on its own. Your data lives in your project folder or your Notion workspace, and
you can edit or delete it at any time. The plugin itself never hard-deletes a note: it moves it to
`.verbatim/trash/`, which you empty yourself.

If you version a study with git, keep the research data out of the repository. The suggested `.gitignore` is
in section 12 of the [documentation](https://github.com/yulldesign/verbatim#12-privacy).

## Children

The plugin is a professional research tool and is not intended for people under 18.

## Contact

Questions or concerns: open an issue at https://github.com/yulldesign/verbatim/issues.
