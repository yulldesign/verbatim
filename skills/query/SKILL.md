---
name: query
description: Answer natural-language questions about the user-research vault with cited evidence - "what do users say about onboarding?", "who complains about pricing?", "which companies mention integrations?", "what do we know about churn and what's missing?" - grounded only in Verbatim notes, with [[citations]], contradictions surfaced, and gaps stated; optional save as a query-output note. Use for /verbatim:query and whenever the user asks anything about their interviews, participants, findings or research corpus, including follow-up questions in a conversation.
argument-hint: "<question> [--project <name>] [--save]"
---

# Verbatim query

The flow: question -> find relevant notes -> answer from the vault only, with
citations. A researcher uses this to brief a PM, prepare a workshop, or check a hunch, so the
answer must be traceable to evidence and honest about what is not covered.

Read `${CLAUDE_PLUGIN_ROOT}/skills/vault/SKILL.md` first. `<script>` = `python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py"`.

## 1. Scope

Default: the whole vault. With `--project <name>` or "in project X": `<script> project resolve <name>`
and restrict to those paths. Notion: build the cache, or use `notion-search` scoped to the Notes database.

## 2. Retrieve - inline or delegated

- **Small vault (< ~60 notes) or a narrow question** - do it yourself (section 3).
- **Larger vault, broad question, or several questions** - spawn the `verbatim:researcher` sub-agent with the
  question, the scope (paths or "whole vault"), and the backend. It reads widely and returns the
  answer with citations, keeping raw notes out of this conversation. For a multi-part question,
  one researcher per part, in parallel.

## 3. How to retrieve (inline, or what the researcher does)

1. Read `graph/index.md` - the map of sources, insights and themes.
2. Expand the question into keywords in both French and English plus synonyms
   (e.g. onboarding -> onboarding, first use, setup, prise en main, premiere utilisation).
3. `<script> scan --grep "<kw1|kw2|...>"` and Grep the vault bodies; also match tags from the taxonomy.
4. Read in full the 5-20 best notes. Prefer synthesis notes for "patterns" questions, insights for
   specifics, sources for "who / which company" questions, transcripts (`raw/`) only to verify a quote.
5. People/company questions: `<script> people` / `<script> companies --name X` are exact; use them.
6. If retrieval finds nothing, do not stop: read all insights' titles (`<script> scan --type insight`)
   and reason from what is adjacent. Gap questions ("what don't we know about X?") need this.

## 4. Answer

- Use only what the notes say. Cite every claim with `[[slug]]` (Notion: page link).
- Prefer evidence that spans participants: "3 of 11 participants (...) describe ..." beats one vivid quote.
  Say how many participants support a claim when you can count them.
- Quote verbatim sparingly - one or two short quotes that carry the point.
- Surface tensions: if notes disagree, show both sides and the context that might explain it.
- Never answer "I cannot answer". Summarise what the vault does contain that is relevant, then a short
  **Not covered** paragraph with what is missing - and, when useful, the interview question that would fill it.
- Keep it proportionate: a short question gets a short answer.
- End with `Sources: [[a]], [[b]], ...`

Follow-ups ("and for enterprise customers?", "say more") reuse the previous retrieval and widen it only as needed.

## 5. Verify before showing

An answer is evidence handed to someone who will act on it, so check it before the user sees it -
every time the answer quotes a participant or cites three or more notes. (Skip this for one-line facts
straight from the script: a count, a list of names.)

1. `<script> staging new --kind query --label "<question>"`.
2. Write the answer to `<job>/files/queries/<slug>.md` per the query-output template
   (`${CLAUDE_PLUGIN_ROOT}/skills/vault/references/note-formats.md`), `related` = every cited note's path. When the `verbatim:researcher` agent
   produced the answer, write its text there unchanged and use its `Notes read:` line for `related`.
3. `<script> verify-quotes <job-id>` - checks every quote (blockquotes, « », " " of 4+ words) against all
   transcripts in `vault/raw/` **and** every `[[citation]]` against the vault. Fix anything reported
   `NOT FOUND` or `BROKEN LINK` in the file, re-run until it passes. Exit 2 only means there were no
   quotes - fine if the answer quotes no one.
4. Show the answer from the verified file, then one line with the check result
   ("4/4 quotes found verbatim · 30/30 citations resolve").

Quotation marks are for participants' words only; terms and titles go in *italics*, or the check flags them.

## 6. Save or discard

Ask whether to keep the answer in the vault (it is already staged). Yes -> `<script> staging seal <id>` and
`staging apply <id>`. No -> `staging refuse <id>`: nothing reaches the vault, and the job stays in
`.verbatim/staging/` as a record of what was answered. With `--save` (or `skip_review: true`), apply without asking.
