# Markdown backend

The vault is a plain folder of `.md` files. It is the source of truth; nothing else
needs to be kept in sync. It opens as-is in Obsidian (graph view, backlinks, search),
which makes a good visual companion to this kit.

```
vault/
├── raw/          transcripts, verbatim (Library)
├── sources/      one summary per transcript
├── insights/     atomic findings
├── synthesis/    cross-interview themes
├── queries/      saved answers
├── projects/     project definitions (+ *.canvas.json boards)
├── graph/
│   ├── index.md      rebuilt by verbatim.py after every apply
│   └── canvas.json   vault-wide affinity map
└── VERBATIM.md       vault marker with a stable vault_id
```

## Reading

- Overview: `verbatim.py stats`
- Lists and filters: `verbatim.py scan --type insight --grep "export|csv"` (JSON, excerpts)
- Full text of a few notes: the Read tool on the paths returned
- Keyword search across bodies: the Grep tool on `vault/` (fast, no tokens spent on reading)
- Relationships: `verbatim.py links`, or read `graph/index.md`

Read `graph/index.md` first when you need a map of the vault: it groups insights under their
source and lists themes, queries and projects.

## Writing

Always through the staging protocol (SKILL.md section 4). Write each proposed file with the
Write tool into `<job>/files/<vault-relative-path>`. Never edit files in `vault/` directly,
except `graph/index.md` which the script owns.

Editing an existing note (e.g. marking an insight validated, adding a `related` link): copy the
current file into the job folder at the same relative path, edit the copy, seal. The manifest
records it as `modify` and `staging show --diff` displays the change.

## Multiple workspaces

One vault per research effort is the simplest model (one workspace per study). To switch, change
`vault_path` in `verbatim.config.json`, or pass `--vault <path>` to the script for a one-off.
