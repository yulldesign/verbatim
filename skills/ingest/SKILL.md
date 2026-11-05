---
name: ingest
description: Import user-research material into the Verbatim vault - interview transcripts (.txt, .md, .pdf, .vtt, .srt, .docx text), folders of files, Notion pages, meeting notes from a connected tool, or pasted text - and extract a source summary plus atomic insights with verbatim quotes, confidence and tags, one parallel sub-agent per transcript. Use for /verbatim:ingest, "import this interview", "analyze these transcripts", "process my user interviews", "add these calls to the research", "extract insights from", or whenever the user drops interview files, even if they don't mention Verbatim.
argument-hint: "<files, folder, Notion URL or pasted text> [--skip-review]"
---

# Verbatim ingest

Turns each transcript into: a verbatim copy (`raw/`), a source summary (`sources/`), and
5-15 insight notes (`insights/`), all staged for review. The
per-file analysis runs in parallel sub-agents so a batch of ten interviews takes the time of one.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. Collect the inputs

Accept any mix of:
- **Files / folders** - expand folders to `.txt .md .pdf .vtt .srt .docx`. PDFs are read with the
  Read tool (use `pages` for long ones). For `.docx`, extract text with a short Python call
  (`zipfile` + strip XML of `word/document.xml`) - no dependency needed.
- **Notion pages** - `notion-fetch` each URL, use the page content as the transcript.
- **Meeting tools** (Granola, Gong... if their connector is available) - fetch the full transcript,
  not the summary: insights need the participant's own words.
- **Pasted text** - save it to `.verbatim/inbox/<slug>.md` first so every transcript has a path.

Then, for each input, decide the file stem (`interview-marie-2026-10`, from the file name or the
first lines) and check `raw/<stem>.md` does not already exist (`<script> scan --type transcript`).
If it does, ask whether to skip or re-import under a new stem - re-importing silently duplicates
every insight.

Subtitle formats: keep speaker labels, drop timestamps and cue numbers.

## 2. Gather shared context once

Before spawning agents, collect what every analyst needs, so they produce consistent notes:
- config: `output_language`, `taxonomy`
- today's date
- known participants and companies: `<script> people` and `<script> companies` (names only), so a
  returning participant is spelled the same way
- the vault index excerpt: first ~150 lines of `graph/index.md`, for the connections pass

## 3. One staging job and one analyst per transcript

For each transcript: `<script> staging new --kind ingest --label "<stem>"` -> job folder.

Spawn one `verbatim:transcript-analyst` sub-agent per transcript, **all in the same message** so they
run in parallel (for more than 8 files, run waves of 8). Brief each with:

```
Transcript: <absolute path>      (or: the Notion page URL + its fetched text saved to <path>)
Stem: <stem>
Staging job: <absolute job folder>
Original file: <original path or URL>
Output language: <auto|fr|en>    Taxonomy: <list>
Today: <YYYY-MM-DD>
Known participants: <names>      Known companies: <names>
Vault index excerpt: <excerpt or "empty vault">
```

Each analyst writes `files/raw/`, `files/sources/`, `files/insights/` into its job, seals it, and
returns a short report (participant, company, insight count, confidence mix, notable quote, any
problem). While they run, tell the user what is happening in one line.

## 4. Review, then apply

- If `skip_review` is true in the config or the user passed `--skip-review`: apply each sealed job
  (`<script> staging apply <id>`), then show what was written.
- Otherwise hand over to the **verbatim:review** workflow for these jobs: summarise each job
  (participant, N insights with titles and confidence), and let the user accept all, pick, edit or refuse.

## 5. After apply

1. `<script> patterns --since <today>` - report in two or three lines: tags now shared by several
   participants, and the saturation signal (`saturated: true` means most new insights echo
   existing ones: a hint that this research question is close to saturation).
2. If projects exist, tell the user which ones the new notes fall into
   (`<script> project resolve <project>` and compare paths) and offer to log the ingest in their Activity.
3. Suggest the natural next step: with 2+ new sources, `verbatim:synthesis`; with a large batch, `verbatim:merge`.

## Failure handling

If an analyst fails or returns nothing usable for a file, keep the other jobs, report the file and
the reason, and offer to retry it alone. A transcript with no identifiable participant still gets
ingested - the participant falls back to the file stem, flagged in the report.
