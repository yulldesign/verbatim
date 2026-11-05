#!/usr/bin/env python3
"""
verbatim.py - deterministic helpers for the Verbatim plugin (Claude Code).

Everything an LLM should NOT do by hand lives here: parsing frontmatter,
deriving links, counting people/companies, structural lint, Jaccard dedup,
typographic tag grouping, the staging area (the review gate), index
rebuild, CSV export and HTML views.

Python 3.9+, standard library only. Run from anywhere inside the project:

    python "${CLAUDE_PLUGIN_ROOT}/skills/vault/scripts/verbatim.py" <command> [options]

Data source:
  * Markdown backend (default): the vault folder from verbatim.config.json
    (or --vault PATH).
  * Notion backend: read-only analysis commands accept --notes-json PATH,
    a JSON array of notes exported from Notion (see references/backend-notion.md).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import difflib
import hashlib
import html
import io
import json
import os
import re
import shutil
import sys
import unicodedata
import uuid
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# --------------------------------------------------------------------------- #
# Schema
# --------------------------------------------------------------------------- #

FIELD_ORDER = [
    "title", "date_created", "date_modified", "type", "status", "tags",
    "related", "source_ref", "confidence", "author", "participant", "company",
]
REQUIRED = ["title", "date_created", "type", "status"]
ENUMS = {
    "type": {"transcript", "insight", "source", "query-output", "synthesis", "project"},
    "status": {"raw", "processing", "validated", "final"},
    "confidence": {"high", "medium", "low", ""},
    "author": {"human", "verbatim", ""},
}
VAULT_DIRS = ["raw", "insights", "sources", "queries", "synthesis", "projects", "graph"]
SKIP_FILES = {"VERBATIM.md", "graph/index.md"}
CONFIG_NAMES = ("verbatim.config.json",)
TYPE_COLORS = {
    "transcript": "#3b82f6", "source": "#f59e0b", "insight": "#10b981",
    "query-output": "#64748b", "synthesis": "#d946ef", "project": "#8b5cf6",
}
D3_URL = "https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"

STOP_WORDS = set("""
the a an is are of in for to with and or that this it be have has was were their they we
our your how what when where why which who from by on at but not do does did can will would
should could may might must as so if then than more also just into use used users user need needs
le la les un une des de du et ou en au aux ce cet cette ces qui que quoi dont ou pour par sur
dans avec sans pas plus est sont ete etre avoir ont il elle ils elles nous vous on leur leurs
son sa ses mon ma mes ton ta tes notre votre se ne y tres aussi mais donc car comme si tout
tous toute toutes faire fait utilisateur utilisateurs besoin besoins
""".split())


# --------------------------------------------------------------------------- #
# Config & paths
# --------------------------------------------------------------------------- #

def find_config(start: Path) -> Path | None:
    for d in [start, *start.parents]:
        for name in CONFIG_NAMES:
            p = d / name
            if p.is_file():
                return p
    return None


class Ctx:
    def __init__(self, args):
        cfg_path = find_config(Path.cwd())
        self.config: dict = {}
        self.root = Path.cwd()
        if cfg_path:
            self.root = cfg_path.parent
            try:
                self.config = json.loads(cfg_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                die(f"{cfg_path.name} is not valid JSON: {e}")
        vault = getattr(args, "vault", None) or self.config.get("vault_path") or "vault"
        vp = Path(vault)
        self.vault = vp if vp.is_absolute() else (self.root / vp)
        self.notes_json = getattr(args, "notes_json", None)
        self.cfg_path = cfg_path
        self.work_dir = self.root / ".verbatim"
        self.staging = self.work_dir / "staging"
        self.stale_days = int(self.config.get("stale_days", 30))

    def rel(self, p: Path) -> str:
        return p.relative_to(self.vault).as_posix()


def die(msg: str, code: int = 1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def today() -> str:
    return dt.date.today().isoformat()


def out_json(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


# --------------------------------------------------------------------------- #
# Frontmatter
# --------------------------------------------------------------------------- #

FM_RE = re.compile(r"^﻿?---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)(.*)$", re.S)


def unquote(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v[1:-1]
    if len(v) >= 2 and v[0] == "'" and v[-1] == "'":
        return v[1:-1].replace("''", "'")
    return v


def parse_inline_list(v: str) -> list:
    try:
        r = json.loads(v)
        if isinstance(r, list):
            return [str(x) for x in r]
    except json.JSONDecodeError:
        pass
    inner = v.strip()[1:-1] if v.strip().endswith("]") else v.strip()[1:]
    return [unquote(x) for x in inner.split(",") if x.strip()]


def parse_frontmatter(text: str):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm: dict = {}
    key = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if key and re.match(r"^\s*-\s+", line) and not re.match(r"^[A-Za-z0-9_\-]+:", line):
            if not isinstance(fm.get(key), list):
                fm[key] = []
            fm[key].append(unquote(re.sub(r"^\s*-\s+", "", line)))
            continue
        mm = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", line)
        if not mm:
            continue
        key, val = mm.group(1), mm.group(2).strip()
        if val.startswith("["):
            fm[key] = parse_inline_list(val)
        elif val in ("", "null", "~"):
            fm[key] = ""
        else:
            fm[key] = unquote(val)
    return fm, m.group(2)


def yaml_value(v) -> str:
    if isinstance(v, list):
        return "[" + ", ".join(json.dumps(str(x), ensure_ascii=False) for x in v) + "]"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = "" if v is None else str(v)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s) or s in ENUMS["type"] | ENUMS["status"] | {"high", "medium", "low", "human", "verbatim"}:
        return s
    return json.dumps(s, ensure_ascii=False)


def serialize_frontmatter(fm: dict, body: str) -> str:
    keys = [k for k in FIELD_ORDER if k in fm] + [k for k in fm if k not in FIELD_ORDER]
    lines = [f"{k}: {yaml_value(fm[k])}" for k in keys]
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body.lstrip("\n")


def as_list(v) -> list:
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def split_names(v) -> list:
    """participant/company may hold comma-separated values after a merge."""
    names = []
    for item in as_list(v):
        names += [x.strip() for x in item.split(",") if x.strip()]
    return names


# --------------------------------------------------------------------------- #
# Notes loading
# --------------------------------------------------------------------------- #

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def slugify(text: str, limit: int = 60) -> str:
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9\s-]", "", t.lower()).strip()
    t = re.sub(r"[\s-]+", "-", t).strip("-")
    if len(t) > limit:  # cut at the last word boundary, never mid-word
        cut = t[:limit + 1].rfind("-")
        t = t[:cut] if cut > limit // 2 else t[:limit]
    return t.strip("-") or "untitled"


def make_note(path: str, fm: dict, body: str) -> dict:
    stem = path.rsplit("/", 1)[-1]
    stem = stem[:-3] if stem.endswith(".md") else stem
    return {
        "path": path,
        "slug": stem,
        "title": str(fm.get("title") or stem),
        "type": str(fm.get("type") or ""),
        "status": str(fm.get("status") or ""),
        "tags": as_list(fm.get("tags")),
        "related": as_list(fm.get("related")),
        "source_ref": str(fm.get("source_ref") or ""),
        "confidence": str(fm.get("confidence") or ""),
        "author": str(fm.get("author") or ""),
        "participant": str(fm.get("participant") or ""),
        "company": str(fm.get("company") or ""),
        "date_created": str(fm.get("date_created") or ""),
        "date_modified": str(fm.get("date_modified") or ""),
        "body": body or "",
        "wikilinks": [w.strip() for w in WIKILINK_RE.findall(body or "")],
        "fm": fm,
    }


def load_notes(ctx: Ctx) -> list[dict]:
    if ctx.notes_json:
        data = json.loads(Path(ctx.notes_json).read_text(encoding="utf-8"))
        notes = []
        for d in data:
            fm = {k: d.get(k, "") for k in FIELD_ORDER if k in d}
            notes.append(make_note(str(d.get("path") or d.get("id") or d.get("url")), fm, d.get("body", "")))
            notes[-1]["url"] = d.get("url", "")
        return notes
    if not ctx.vault.is_dir():
        die(f"vault not found: {ctx.vault} (run `verbatim.py init` or fix vault_path in verbatim.config.json)")
    notes = []
    for p in sorted(ctx.vault.rglob("*.md")):
        rel = ctx.rel(p)
        if rel in SKIP_FILES or any(part.startswith(".") for part in Path(rel).parts):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        fm, body = parse_frontmatter(text)
        notes.append(make_note(rel, fm, body))
    return notes


def build_resolver(notes: list[dict]):
    idx: dict[str, dict] = {}
    for n in notes:
        for k in (n["path"], n["path"][:-3] if n["path"].endswith(".md") else n["path"], n["slug"]):
            idx.setdefault(k.lower(), n)
        idx.setdefault(n["title"].lower(), n)
        if n.get("url"):
            idx.setdefault(n["url"].lower(), n)
            idx.setdefault(notion_url(n["url"]).lower(), n)

    def resolve(ref: str):
        if not ref:
            return None
        r = ref.strip().replace("\\", "/")
        if "notion." in r and notion_url(r).lower() in idx:
            return idx[notion_url(r).lower()]
        for cand in (r, r.lstrip("./"), r.split("/")[-1], r.split("/")[-1][:-3] if r.endswith(".md") else None):
            if cand and cand.lower() in idx:
                return idx[cand.lower()]
        return None

    return resolve


def derive_links(notes: list[dict]):
    """Edges from source_ref, related[] and [[wikilinks]]. Returns (edges, broken)."""
    resolve = build_resolver(notes)
    edges, broken, seen = [], [], set()
    for n in notes:
        refs = []
        if n["source_ref"]:
            refs.append(("source", n["source_ref"]))
        refs += [("related", r) for r in n["related"]]
        refs += [("wikilink", w) for w in n["wikilinks"]]
        for kind, ref in refs:
            target = resolve(ref)
            if target is None:
                broken.append({"from": n["path"], "ref": ref, "kind": kind})
                continue
            if target["path"] == n["path"]:
                continue
            key = (n["path"], target["path"])
            if key in seen:
                continue
            seen.add(key)
            edges.append({"from": n["path"], "to": target["path"], "kind": kind})
    return edges, broken


def public(n: dict, full: bool = False, excerpt: int = 200) -> dict:
    d = {k: v for k, v in n.items() if k not in ("fm", "body", "wikilinks")}
    if full:
        d["body"] = n["body"]
    else:
        d["excerpt"] = re.sub(r"\s+", " ", n["body"]).strip()[:excerpt]
    return d


# --------------------------------------------------------------------------- #
# Commands: vault
# --------------------------------------------------------------------------- #

DEFAULT_TAXONOMY = ["pain-point", "feature-request", "workaround", "onboarding", "pricing", "performance", "ux",
                    "integration", "trust", "churn-risk", "delight", "job-to-be-done", "process", "expectation-gap"]


def cmd_init(ctx: Ctx, args):
    if not ctx.cfg_path:  # new project: write verbatim.config.json where we run
        vault_rel = args.path or "vault"
        cfg = {"backend": "markdown", "vault_path": vault_rel, "output_language": "auto", "skip_review": False,
               "stale_days": 30, "taxonomy": DEFAULT_TAXONOMY,
               "notion": {"notes_data_source": "", "projects_data_source": "", "parent_page": ""}}
        cfg_file = Path.cwd() / "verbatim.config.json"
        cfg_file.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"config written: {cfg_file.as_posix()}")
        ctx.vault = Path.cwd() / vault_rel
    v = Path(args.path) if args.path and ctx.cfg_path else ctx.vault
    v.mkdir(parents=True, exist_ok=True)
    for d in VAULT_DIRS:
        (v / d).mkdir(exist_ok=True)
    marker = v / "VERBATIM.md"
    if not marker.exists():
        marker.write_text(serialize_frontmatter(
            {"vault_id": str(uuid.uuid4()), "date_created": today()},
            "# Verbatim vault\n\nResearch knowledge base managed by the Verbatim plugin for Claude Code.\n"
            "Markdown is the source of truth. Open this folder in Obsidian to browse it.\n"), encoding="utf-8")
    idx = v / "graph" / "index.md"
    if not idx.exists():
        idx.write_text("# Knowledge Graph Index\n\nNo notes yet.\n", encoding="utf-8")
    print(f"vault ready: {v}")


def cmd_slug(ctx: Ctx, args):
    print(slugify(" ".join(args.text)))


def cmd_scan(ctx: Ctx, args):
    notes = load_notes(ctx)
    if args.type:
        types = set(args.type)
        notes = [n for n in notes if n["type"] in types]
    if args.grep:
        rx = re.compile(args.grep, re.I)
        notes = [n for n in notes if rx.search(n["title"]) or rx.search(n["body"]) or any(rx.search(t) for t in n["tags"])]
    out_json([public(n, full=args.full, excerpt=args.excerpt) for n in notes])


def cmd_stats(ctx: Ctx, args):
    notes = load_notes(ctx)
    by_type: dict[str, int] = {}
    for n in notes:
        by_type[n["type"] or "(none)"] = by_type.get(n["type"] or "(none)", 0) + 1
    people = {p for n in notes for p in split_names(n["participant"])}
    companies = {c for n in notes for c in split_names(n["company"])}
    tags = {t for n in notes for t in n["tags"]}
    last = max((n["date_created"] for n in notes if n["type"] == "source"), default="-")
    jobs = list_jobs(ctx)
    pending = [j for j in jobs if j["status"] in ("ready", "partial")]
    data = {"vault": str(ctx.vault) if not ctx.notes_json else ctx.notes_json, "notes": len(notes),
            "by_type": by_type, "participants": len(people), "companies": len(companies),
            "tags": len(tags), "last_ingest": last, "pending_reviews": len(pending)}
    if args.json:
        return out_json(data)
    print(f"Vault: {data['vault']}")
    print(f"Notes: {len(notes)}  " + "  ".join(f"{k}={v}" for k, v in sorted(by_type.items())))
    print(f"Participants: {len(people)}  Companies: {len(companies)}  Tags: {len(tags)}")
    print(f"Last ingest: {last}  Pending reviews: {len(pending)}")


def directory(notes, field: str, other: str, other_key: str):
    """Rows per person or company. Merged notes hold comma-separated names; when both
    fields have the same number of names they are paired by position."""
    rows: dict[str, dict] = {}
    for n in notes:
        if n["type"] == "project":
            continue
        names, others = split_names(n[field]), split_names(n[other])
        for i, name in enumerate(names):
            r = rows.setdefault(name, {"name": name, other_key: set(), "counts": {}, "notes": [],
                                       "interviews": [], "first_seen": "", "last_seen": ""})
            if n["type"] == "transcript":  # the interview date, when the transcript states it
                r["interviews"].append(str(n["fm"].get("interview_date") or n["date_created"]))
            if len(others) == len(names):
                r[other_key].add(others[i])
            else:
                r[other_key].update(others)
            r["counts"][n["type"]] = r["counts"].get(n["type"], 0) + 1
            r["notes"].append({"path": n["path"], "title": n["title"], "type": n["type"]})
            if n["date_created"]:
                r["first_seen"] = min(filter(None, [r["first_seen"], n["date_created"]]))
                r["last_seen"] = max(r["last_seen"], n["date_created"])
    for r in rows.values():
        r[other_key] = sorted(r[other_key])
        r["interviews"] = sorted(set(filter(None, r["interviews"])))
        r["total"] = len(r["notes"])
    return sorted(rows.values(), key=lambda r: (-r["total"], r["name"].lower()))


def cmd_people(ctx: Ctx, args):
    rows = directory(load_notes(ctx), "participant", "company", "companies")
    emit_directory(rows, args)


def cmd_companies(ctx: Ctx, args):
    rows = directory(load_notes(ctx), "company", "participant", "participants")
    emit_directory(rows, args)


def emit_directory(rows, args):
    if args.name:
        q = args.name.lower()
        rows = [r for r in rows if q in r["name"].lower()]
        return out_json(rows)
    out_json([{k: v for k, v in r.items() if k != "notes"} for r in rows])


def cmd_links(ctx: Ctx, args):
    notes = load_notes(ctx)
    edges, broken = derive_links(notes)
    out_json({"edges": edges, "broken": broken})


# --------------------------------------------------------------------------- #
# Lint (structural half of Health Check)
# --------------------------------------------------------------------------- #

def cmd_lint(ctx: Ctx, args):
    notes = load_notes(ctx)
    edges, broken = derive_links(notes)
    linked = {e["from"] for e in edges} | {e["to"] for e in edges}
    cutoff = (dt.date.today() - dt.timedelta(days=args.stale_days or ctx.stale_days)).isoformat()
    findings = []

    def add(kind, severity, title, desc, paths):
        findings.append({"type": kind, "severity": severity, "title": title, "description": desc, "paths": paths})

    for n in notes:
        if n["type"] == "insight" and n["path"] not in linked and not n["related"] and not n["source_ref"]:
            add("orphan", "medium", n["title"], "No links to other notes and no source reference.", [n["path"]])
        if n["type"] in ("insight", "synthesis") and n["status"] == "raw" and n["date_created"] and n["date_created"] < cutoff:
            add("stale", "low", n["title"], f'In "raw" status since {n["date_created"]}. Review and validate it.', [n["path"]])
        missing = [f for f in REQUIRED if not n["fm"].get(f)] if not ctx.notes_json else []
        bad = [f"{k}={n[k]!r}" for k in ENUMS if n.get(k) and n[k] not in ENUMS[k]]
        if missing or bad:
            add("schema", "low", n["title"], "Frontmatter issues: " + ", ".join(
                ([f"missing {', '.join(missing)}"] if missing else []) + bad), [n["path"]])
    for b in broken:
        add("broken-link", "medium", f'Unresolved {b["kind"]}: {b["ref"]}', "Reference points to a note that does not exist.", [b["from"]])
    titles: dict[str, list] = {}
    for n in notes:
        if n["type"] == "insight":
            titles.setdefault(n["title"].strip().lower(), []).append(n["path"])
    for t, paths in titles.items():
        if len(paths) > 1:
            add("duplicate-title", "medium", t, "Several insights share the exact same title.", paths)

    insights = [n for n in notes if n["type"] == "insight"]
    data = {"generated": today(), "insights": len(insights), "findings": findings,
            "counts": {k: sum(1 for f in findings if f["type"] == k) for k in sorted({f["type"] for f in findings})}}
    out_json(data)


# --------------------------------------------------------------------------- #
# Dedup (Jaccard fallback of Merge)
# --------------------------------------------------------------------------- #

def tokenize(text: str) -> set[str]:
    t = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return {w for w in re.findall(r"[a-z0-9]+", t) if len(w) > 2 and w not in STOP_WORDS}


def jaccard(a: set, b: set) -> float:
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def cmd_dedup(ctx: Ctx, args):
    notes = [n for n in load_notes(ctx) if n["type"] in set(args.type)]
    toks = [(tokenize(n["title"]), tokenize(n["body"][:600])) for n in notes]
    assigned, groups = set(), []
    for i, a in enumerate(notes):
        if a["path"] in assigned:
            continue
        group, scores = [a], []
        for j in range(i + 1, len(notes)):
            b = notes[j]
            if b["path"] in assigned:
                continue
            s = (jaccard(toks[i][0], toks[j][0]) * 2 + jaccard(toks[i][1], toks[j][1])) / 3
            if s >= args.threshold:
                group.append(b)
                scores.append(round(s, 3))
        if len(group) >= 2:
            assigned.update(n["path"] for n in group)
            common = set.intersection(*[tokenize(n["title"]) for n in group])
            groups.append({
                "reason": f"Similar content - both cover: {', '.join(sorted(common)[:4])}" if common else "Overlapping content detected",
                "similarity": max(scores),
                "notes": [{"path": n["path"], "title": n["title"], "participant": n["participant"]} for n in group],
            })
    out_json({"method": "jaccard", "threshold": args.threshold, "groups": groups})


# --------------------------------------------------------------------------- #
# Tags
# --------------------------------------------------------------------------- #

def tag_key(tag: str) -> str:
    t = re.sub(r"[-_\s]+", " ", tag.lower().strip())
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return " ".join(w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w for w in t.split())


def tag_usage(notes) -> dict[str, list]:
    usage: dict[str, list] = {}
    for n in notes:
        for t in n["tags"]:
            usage.setdefault(t, []).append(n["path"])
    return usage


def cmd_tags(ctx: Ctx, args):
    notes = load_notes(ctx)
    usage = tag_usage(notes)
    buckets: dict[str, list] = {}
    for t in usage:
        buckets.setdefault(tag_key(t), []).append(t)
    groups = []
    for variants in buckets.values():
        if len(variants) > 1:
            taxonomy = set(ctx.config.get("taxonomy", []))
            variants.sort(key=lambda v: (v not in taxonomy, -len(usage[v]),
                                         v != re.sub(r"[_\s]+", "-", v.lower()), v))
            groups.append({"kind": "typographic", "canonical": variants[0],
                           "tags": [{"tag": v, "count": len(usage[v])} for v in variants]})
    out_json({"tags": sorted(({"tag": t, "count": len(p)} for t, p in usage.items()), key=lambda x: (-x["count"], x["tag"])),
              "typographic_groups": groups})


def cmd_retag(ctx: Ctx, args):
    mapping = {}
    for m in args.map:
        if "=" not in m:
            die(f"bad --map {m!r}, expected old=new")
        old, new = m.split("=", 1)
        mapping[old.strip()] = new.strip()
    job = new_job(ctx, "tags", args.label or "Tag consolidation")
    changed = 0
    for p in sorted(ctx.vault.rglob("*.md")):
        rel = ctx.rel(p)
        if rel in SKIP_FILES:
            continue
        fm, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        tags = as_list(fm.get("tags"))
        if not any(t in mapping for t in tags):
            continue
        new_tags = []
        for t in tags:
            nt = mapping.get(t, t)
            if nt not in new_tags:
                new_tags.append(nt)
        fm["tags"] = new_tags
        fm["date_modified"] = today()
        dest = job / "files" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(serialize_frontmatter(fm, body), encoding="utf-8")
        changed += 1
    seal_job(ctx, job)
    print(f"{job.name}  ({changed} notes to rewrite)")


# --------------------------------------------------------------------------- #
# Staging area (the review gate / queue)
# --------------------------------------------------------------------------- #

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def new_job(ctx: Ctx, kind: str, label: str) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    job = ctx.staging / f"{stamp}-{kind}-{slugify(label, 30)}"
    n = 1
    while job.exists():
        n += 1
        job = ctx.staging / f"{stamp}-{kind}-{slugify(label, 30)}-{n}"
    (job / "files").mkdir(parents=True)
    (job / "job.json").write_text(json.dumps({
        "id": job.name, "kind": kind, "label": label, "created": dt.datetime.now().isoformat(timespec="seconds"),
        "status": "draft", "ops": []}, indent=2, ensure_ascii=False), encoding="utf-8")
    return job


def read_job(ctx: Ctx, job_id: str) -> tuple[Path, dict]:
    direct = Path(job_id)  # a job folder path, relative to the cwd or absolute
    job = direct if (direct / "job.json").exists() else ctx.staging / Path(job_id).name
    if not (job / "job.json").exists():
        job_id = Path(job_id).name
        matches = [p for p in ctx.staging.glob(f"*{job_id}*") if (p / "job.json").exists()] if ctx.staging.exists() else []
        if len(matches) != 1:
            die(f"staging job not found or ambiguous: {job_id}")
        job = matches[0]
    return job, json.loads((job / "job.json").read_text(encoding="utf-8"))


def write_job(job: Path, meta: dict):
    (job / "job.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def seal_job(ctx: Ctx, job: Path) -> dict:
    meta = json.loads((job / "job.json").read_text(encoding="utf-8"))
    ops, warnings = [], []
    files = job / "files"
    for p in sorted(files.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(files).as_posix()
        target = ctx.vault / rel
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        if rel.endswith(".md") and rel not in SKIP_FILES:
            missing = [f for f in REQUIRED if not fm.get(f)]
            if missing:
                warnings.append(f"{rel}: missing {', '.join(missing)}")
        ops.append({"op": "modify" if target.exists() else "create", "path": rel,
                    "title": str(fm.get("title") or rel), "type": str(fm.get("type") or ""),
                    "base_sha": sha(target), "state": "pending"})
    dl = job / "delete.txt"
    if dl.exists():
        for line in dl.read_text(encoding="utf-8").splitlines():
            rel = line.strip().replace("\\", "/")
            if not rel or rel.startswith("#"):
                continue
            target = ctx.vault / rel
            if not target.exists():
                warnings.append(f"delete target missing: {rel}")
                continue
            fm, _ = parse_frontmatter(target.read_text(encoding="utf-8", errors="replace"))
            ops.append({"op": "delete", "path": rel, "title": str(fm.get("title") or rel),
                        "type": str(fm.get("type") or ""), "base_sha": sha(target), "state": "pending"})
    meta.update(ops=ops, status="ready", warnings=warnings)
    write_job(job, meta)
    return meta


def list_jobs(ctx: Ctx) -> list[dict]:
    if not ctx.staging.exists():
        return []
    jobs = []
    for p in sorted(ctx.staging.iterdir()):
        if (p / "job.json").exists():
            jobs.append(json.loads((p / "job.json").read_text(encoding="utf-8")))
    return jobs


def cmd_staging(ctx: Ctx, args):
    a = args.action
    if a == "new":
        job = new_job(ctx, args.kind, args.label or args.kind)
        print(job.as_posix())
    elif a == "seal":
        job, _ = read_job(ctx, args.id)
        meta = seal_job(ctx, job)
        print(f"{meta['id']}: {len(meta['ops'])} ops ready")
        for w in meta.get("warnings", []):
            print(f"  warning: {w}")
    elif a == "list":
        jobs = list_jobs(ctx)
        if args.status:
            jobs = [j for j in jobs if j["status"] in args.status]
        if args.json:
            return out_json(jobs)
        if not jobs:
            print("No staging jobs.")
        for j in jobs:
            c = {}
            for o in j.get("ops", []):
                c[o["op"]] = c.get(o["op"], 0) + 1
            print(f"{j['status']:<8} {j['id']}  [{j['kind']}] {j['label']}  " + " ".join(f"{k}:{v}" for k, v in c.items()))
    elif a == "show":
        job, meta = read_job(ctx, args.id)
        print(f"# {meta['label']}  ({meta['id']}, {meta['kind']}, {meta['status']})")
        for w in meta.get("warnings", []):
            print(f"warning: {w}")
        for o in meta["ops"]:
            print(f"- [{o['state']}] {o['op'].upper():<6} {o['path']}  - {o['title']} ({o['type']})")
            if args.diff and o["op"] == "modify":
                old = (ctx.vault / o["path"]).read_text(encoding="utf-8").splitlines()
                new = (job / "files" / o["path"]).read_text(encoding="utf-8").splitlines()
                for line in difflib.unified_diff(old, new, "vault/" + o["path"], "proposed/" + o["path"], lineterm="", n=2):
                    print("    " + line)
    elif a in ("apply", "refuse"):
        job, meta = read_job(ctx, args.id)
        if meta["status"] == "draft":
            meta = seal_job(ctx, job)
        only = {p.replace("\\", "/") for p in (args.only or [])}
        exclude = {p.replace("\\", "/") for p in (args.exclude or [])}
        trash = ctx.work_dir / "trash" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        done, skipped = 0, []
        for o in meta["ops"]:
            if o["state"] != "pending" or (only and o["path"] not in only) or o["path"] in exclude:
                continue
            if a == "refuse":
                o["state"] = "refused"
                continue
            if args.mark_only:  # Notion backend: Claude already wrote the pages via MCP
                o["state"] = "applied"
                done += 1
                continue
            target = ctx.vault / o["path"]
            if o["op"] in ("modify", "delete") and sha(target) != o["base_sha"] and not args.force:
                skipped.append(o["path"])
                continue
            if o["op"] == "delete":
                dest = trash / o["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(dest))
            else:
                if o["op"] == "create" and target.exists() and not args.force:
                    skipped.append(o["path"])
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(job / "files" / o["path"], target)
            o["state"] = "applied"
            done += 1
        states = {o["state"] for o in meta["ops"]}
        meta["status"] = ("refused" if states == {"refused"} else "applied" if "pending" not in states else "partial")
        meta["resolved"] = dt.datetime.now().isoformat(timespec="seconds")
        write_job(job, meta)
        if a == "apply" and done and not args.mark_only and (ctx.vault / "graph").exists():
            rebuild_index(ctx)
        print(f"{meta['id']}: {a} -> {done} ops {'applied' if a == 'apply' else ''}, status={meta['status']}")
        if skipped:
            print("skipped (vault changed since staging or file exists; re-run with --force to overwrite):")
            for s in skipped:
                print(f"  {s}")
        if a == "apply" and trash.exists():
            print(f"deleted notes moved to {trash.as_posix()} (recoverable)")


# --------------------------------------------------------------------------- #
# Evidence helpers: verbatim transcript copy, quote verification
# --------------------------------------------------------------------------- #

def norm_text(t: str) -> str:
    t = unicodedata.normalize("NFC", t)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("«", '"'), ("»", '"'), (" ", " "), (" ", " ")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip().lower()


INLINE_QUOTE_RE = re.compile(r"«\s*([^»]+?)\s*»|“([^”]+)”|(?<![\w=])\"([^\"\n]+)\"")


def extract_quotes(body: str) -> list[str]:
    """Blockquote lines (minus attribution lines '> - Name, [[stem]]') and inline
    quotes in prose: « ... », “ ... ”, "..." of at least four words."""
    quotes = []
    for line in body.splitlines():
        ln = line.strip()
        if ln.startswith(">"):
            q = ln.lstrip(">").strip()
            if q and q[0] not in "-—–":
                quotes.append(q.strip().strip('"').strip("«»“” ").strip())
            continue
        for m in INLINE_QUOTE_RE.finditer(ln):
            q = next(g for g in m.groups() if g).strip()
            if len(q.split()) >= 4:
                quotes.append(q)
    return quotes


def cmd_verify_quotes(ctx: Ctx, args):
    target = Path(args.id)
    if target.is_file() or (target.is_dir() and not (target / "job.json").exists()):
        job = None  # a plain note, an export (readout) or a whole folder such as the vault
        base = target.parent if target.is_file() else target
        files_list = [target] if target.is_file() else sorted(target.rglob("*.md"))
    else:
        job, _ = read_job(ctx, args.id)
        base = job / "files"
        files_list = sorted(base.rglob("*.md"))
    files_list = [p for p in files_list if p.name != "VERBATIM.md"]
    raws = [Path(t) for t in (args.transcript or [])] or (sorted((base / "raw").glob("*.md")) if job else [])
    if not raws and ctx.vault.is_dir():  # synthesis, merge...: check against every transcript in the vault
        raws = sorted((ctx.vault / "raw").glob("*.md"))
    corpus = ""
    for r in raws:
        _, body = parse_frontmatter(r.read_text(encoding="utf-8", errors="replace"))
        corpus += " " + norm_text(body)
    if not corpus.strip():
        die("no transcript to check against (pass --transcript PATH)")
    results, missing = [], 0
    for p in files_list:
        rel = p.relative_to(base).as_posix()
        if rel.startswith("raw/"):
            continue
        _, body = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        for q in extract_quotes(body):
            frags = [norm_text(f).strip(" .,;:") for f in re.split(r"\s*(?:\.\.\.|…|\[\.\.\.\])\s*", q)]
            frags = [f for f in frags if len(f) >= 8]
            ok = all(f in corpus for f in frags) if frags else True
            missing += not ok
            results.append({"file": rel, "quote": q, "found": ok})
    bad = [r for r in results if not r["found"]]
    for r in bad:
        print(f"NOT FOUND  {r['file']}: {r['quote'][:100]}")

    # Citations: every [[link]] in a staged note must resolve to a vault note or a note of this job.
    known = {n["slug"].lower() for n in load_notes(ctx)} | {n["title"].lower() for n in load_notes(ctx)} \
        if ctx.vault.is_dir() else set()
    known |= {p.stem.lower() for p in files_list}
    dl = job / "delete.txt" if job else None  # notes this job deletes are no longer valid targets
    if dl and dl.exists():
        known -= {Path(l.strip()).stem.lower() for l in dl.read_text(encoding="utf-8").splitlines() if l.strip()}
    links, broken = 0, []
    for p in files_list:
        rel = p.relative_to(base).as_posix()
        if rel.startswith("raw/"):
            continue
        _, body = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        for w in WIKILINK_RE.findall(body):
            links += 1
            if w.strip().lower() not in known:
                broken.append((rel, w.strip()))
    for rel, w in sorted(set(broken)):
        print(f"BROKEN LINK  {rel}: [[{w}]]")

    if results:
        print(f"{len(results) - len(bad)}/{len(results)} quotes found verbatim in {', '.join(r.name for r in raws)}")
    else:
        print("WARNING: no quotes found to check (blockquotes, « », “ ” or \"...\" of 4+ words) - no quote was verified")
    print(f"{links - len(broken)}/{links} citations resolve")
    if bad or broken:
        sys.exit(1)
    sys.exit(0 if results else 2)


def portable_ref(ctx: Ctx, ref: str) -> str:
    """Never store an absolute local path (it leaks the user's machine layout): keep URLs, make paths
    relative to the project root when inside it, else keep the file name only."""
    if re.match(r"^[a-z]+://", ref):
        return ref
    path = Path(ref)
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.resolve().relative_to(ctx.root.resolve()).as_posix()
    except ValueError:
        return path.name


def cmd_stage_raw(ctx: Ctx, args):
    """Copy a transcript into a staging job byte-for-byte, with transcript frontmatter in front."""
    job, _ = read_job(ctx, args.id)
    src = Path(args.source)
    text = src.read_text(encoding="utf-8-sig", errors="replace")
    fm0, body = parse_frontmatter(text)
    body = body if fm0 else text
    stem = args.stem or slugify(src.stem)
    fm = {"title": stem, "date_created": today(), "date_modified": today(), "type": "transcript",
          "status": "raw", "tags": [], "related": [], "source_ref": "", "confidence": "high",
          "author": "human", "participant": args.participant or stem, "company": args.company or "",
          "interview_date": args.interview_date or "", "original_file": portable_ref(ctx, args.original or src.as_posix())}
    dest = job / "files" / "raw" / f"{stem}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(serialize_frontmatter(fm, "") + body.lstrip("﻿"), encoding="utf-8")
    print(f"raw/{stem}.md staged ({len(body)} chars, body unchanged)")


# --------------------------------------------------------------------------- #
# Notion backend: turn raw query rows into the notes cache
# --------------------------------------------------------------------------- #

MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((?:https?://)?[^)]*\)")
TYPE_DIRS = {"transcript": "raw", "source": "sources", "insight": "insights", "synthesis": "synthesis",
             "query-output": "queries", "project": "projects"}


def json_list(v) -> list:
    if isinstance(v, list):
        return [str(x) for x in v]
    if isinstance(v, str) and v.strip().startswith("["):
        try:
            return [str(x) for x in json.loads(v)]
        except json.JSONDecodeError:
            pass
    return as_list(v)


def notion_url(u: str) -> str:
    """Normalise page URLs: app.notion.com/<id> and app.notion.com/p/<id>?pvs=.. -> app.notion.com/p/<id>."""
    u = str(u or "").split("?")[0].rstrip("/")
    m = re.search(r"([0-9a-f]{32})$", u.replace("-", ""))
    return f"https://app.notion.com/p/{m.group(1)}" if m else u


def cmd_notion_cache(ctx: Ctx, args):
    rows = []
    for f in args.inputs:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        rows += data.get("results", data) if isinstance(data, dict) else data
    bodies = json.loads(Path(args.bodies).read_text(encoding="utf-8")) if args.bodies else {}
    notes, seen = [], set()
    for r in rows:
        url = notion_url(r.get("url", ""))
        if url in seen:
            continue
        seen.add(url)
        ntype = r.get("Type") or ""
        slug = r.get("Slug") or slugify(r.get("Title", ""))
        vp = MD_LINK_RE.sub(lambda m: m.group(1), str(r.get("Vault path") or "")).strip()
        vp = vp or f"{TYPE_DIRS.get(ntype, 'notes')}/{slug}"
        if not vp.endswith(".md"):
            vp += ".md"
        src = [notion_url(x) for x in json_list(r.get("Source"))]
        notes.append({
            "id": url.rsplit("/", 1)[-1], "url": url, "path": vp, "title": r.get("Title", ""), "type": ntype,
            "status": r.get("Status") or "", "tags": json_list(r.get("Tags")), "confidence": r.get("Confidence") or "",
            "author": r.get("Author") or "", "participant": r.get("Participant") or "", "company": r.get("Company") or "",
            "date_created": r.get("date:Date created:start") or "", "source_ref": src[0] if src else "",
            "related": [notion_url(x) for x in json_list(r.get("Related"))],
            "body": bodies.get(url, bodies.get(slug, "")),
        })
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(notes, ensure_ascii=False, indent=1), encoding="utf-8")
    by = {}
    for n in notes:
        by[n["type"]] = by.get(n["type"], 0) + 1
    print(f"{len(notes)} notes -> {out.as_posix()}  " + " ".join(f"{k}={v}" for k, v in sorted(by.items()))
          + f"  (bodies: {sum(1 for n in notes if n['body'])})")


# --------------------------------------------------------------------------- #
# Index (graph/index.md) - derived data, rebuilt after every apply
# --------------------------------------------------------------------------- #

def rebuild_index(ctx: Ctx) -> Path:
    notes = load_notes(ctx)
    resolve = build_resolver(notes)
    by_type: dict[str, list] = {}
    for n in notes:
        by_type.setdefault(n["type"], []).append(n)

    def line(n):
        extra = [x for x in (n["participant"], n["confidence"]) if x]
        return f"- [[{n['slug']}]] - {n['title']}" + (f" ({', '.join(extra)})" if extra else "")

    out = ["# Knowledge Graph Index", "",
           f"_Rebuilt {today()} by verbatim.py - do not edit by hand._", "",
           "| Type | Count |", "|---|---|"]
    out += [f"| {t or '(none)'} | {len(v)} |" for t, v in sorted(by_type.items())]
    if by_type.get("synthesis"):
        out += ["", "## Themes (synthesis)", ""] + [line(n) for n in sorted(by_type["synthesis"], key=lambda n: n["title"])]
    children: dict[str, list] = {}
    unsourced = []
    for n in by_type.get("insight", []):
        src = resolve(n["source_ref"])
        if src:
            children.setdefault(src["path"], []).append(n)
        else:
            unsourced.append(n)
    if by_type.get("source"):
        out += ["", "## Sources and their insights"]
        for s in sorted(by_type["source"], key=lambda n: n["date_created"], reverse=True):
            out += ["", f"### [[{s['slug']}]] - {s['participant'] or s['title']}"
                    + (f" @ {s['company']}" if s["company"] else "") + f" ({s['date_created']})", ""]
            out += [line(i) for i in sorted(children.get(s["path"], []), key=lambda n: n["title"])] or ["_No insights._"]
    if unsourced:
        out += ["", "## Insights without source", ""] + [line(n) for n in unsourced]
    if by_type.get("query-output"):
        out += ["", "## Saved queries", ""] + [line(n) for n in by_type["query-output"]]
    if by_type.get("project"):
        out += ["", "## Projects", ""] + [line(n) for n in by_type["project"]]
    path = ctx.vault / "graph" / "index.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return path


def cmd_index(ctx: Ctx, args):
    print(f"index rebuilt: {rebuild_index(ctx).as_posix()}")


# --------------------------------------------------------------------------- #
# Patterns / saturation (Activity feed signals)
# --------------------------------------------------------------------------- #

def cmd_patterns(ctx: Ctx, args):
    notes = load_notes(ctx)
    insights = [n for n in notes if n["type"] == "insight"]
    tag_people: dict[str, set] = {}
    for n in insights:
        for p in split_names(n["participant"]):
            for t in n["tags"]:
                tag_people.setdefault(t, set()).add(p)
    patterns = sorted(({"tag": t, "participant_count": len(ps), "participants": sorted(ps)}
                       for t, ps in tag_people.items() if len(ps) >= args.min), key=lambda x: -x["participant_count"])
    sat = None
    if args.since:
        old = [n for n in insights if n["date_created"] and n["date_created"] < args.since]
        new = [n for n in insights if n["date_created"] and n["date_created"] >= args.since]
        words = {w for n in old for w in n["title"].lower().split() if len(w) > 4}
        overlaps = sum(1 for n in new if any(w in words for w in n["title"].lower().split() if len(w) > 4))
        ratio = overlaps / len(new) if new and old else 0.0
        sat = {"since": args.since, "new_insights": len(new), "ratio": round(ratio, 2), "saturated": ratio > 0.6}
    out_json({"patterns": patterns, "saturation": sat})


# --------------------------------------------------------------------------- #
# Projects
# --------------------------------------------------------------------------- #

def project_notes(notes, project: dict) -> list[dict]:
    fm = project["fm"]
    if str(fm.get("locked", "")).lower() == "true" and as_list(fm.get("snapshot")):
        snap = set(as_list(fm.get("snapshot")))
        return [n for n in notes if n["path"] in snap]
    types = set(as_list(fm.get("filter_types"))) or {"insight", "source", "query-output", "synthesis"}
    tags = set(as_list(fm.get("filter_tags")))
    people = set(as_list(fm.get("filter_participants")))
    comps = set(as_list(fm.get("filter_companies")))
    d_from, d_to = str(fm.get("date_from") or ""), str(fm.get("date_to") or "")
    included, excluded = set(as_list(fm.get("included"))), set(as_list(fm.get("excluded")))
    out = []
    for n in notes:
        if n["path"] == project["path"] or n["path"] in excluded:
            continue
        if n["path"] in included:
            out.append(n)
            continue
        if n["type"] not in types:
            continue
        if d_from and n["date_created"] and n["date_created"] < d_from:
            continue
        if d_to and n["date_created"] and n["date_created"] > d_to:
            continue
        if people and not any(p in people for p in split_names(n["participant"])):
            continue
        if comps and not any(c in comps for c in split_names(n["company"])):
            continue
        if tags and not any(t in tags for t in n["tags"]):
            continue
        out.append(n)
    return out


def find_project(notes, ref: str) -> dict:
    resolve = build_resolver(notes)
    p = resolve(ref) or resolve("projects/" + slugify(ref))
    if not p or p["type"] != "project":
        die(f"project not found: {ref}")
    return p


def cmd_project(ctx: Ctx, args):
    notes = load_notes(ctx)
    if args.action == "list":
        projects = [n for n in notes if n["type"] == "project"]
        return out_json([{"path": p["path"], "title": p["title"], "count": len(project_notes(notes, p)),
                          "locked": str(p["fm"].get("locked", "")).lower() == "true"} for p in projects])
    p = find_project(notes, args.ref)
    members = project_notes(notes, p)
    if args.action == "resolve":
        out_json({"project": p["title"], "count": len(members), "notes": [public(n) for n in members]})
    elif args.action == "snapshot":
        print(json.dumps([n["path"] for n in members], ensure_ascii=False))


# --------------------------------------------------------------------------- #
# Export & HTML views
# --------------------------------------------------------------------------- #

def scoped_notes(ctx: Ctx, args) -> list[dict]:
    notes = load_notes(ctx)
    if getattr(args, "project", None):
        notes = project_notes(notes, find_project(notes, args.project))
    return notes


def cmd_export_csv(ctx: Ctx, args):
    notes = [n for n in scoped_notes(ctx, args) if n["type"] in set(args.type)]
    resolve = build_resolver(load_notes(ctx))
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["title", "type", "participant", "company", "confidence", "status", "tags",
                "date_created", "source", "path", "body"])
    for n in notes:
        src = resolve(n["source_ref"])
        w.writerow([n["title"], n["type"], n["participant"], n["company"], n["confidence"], n["status"],
                    "; ".join(n["tags"]), n["date_created"], src["title"] if src else n["source_ref"],
                    n["path"], re.sub(r"\s+", " ", n["body"]).strip()])
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text("﻿" + buf.getvalue(), encoding="utf-8")  # BOM for Excel
        print(f"{len(notes)} rows -> {args.out}")
    else:
        sys.stdout.write(buf.getvalue())


PAGE_CSS = """
:root{--bg:#faf8f5;--fg:#1c1917;--muted:#78716c;--card:#fff;--line:#e7e5e4}
@media (prefers-color-scheme:dark){:root{--bg:#1c1917;--fg:#f5f5f4;--muted:#a8a29e;--card:#292524;--line:#44403c}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
header{padding:16px 20px;border-bottom:1px solid var(--line);display:flex;gap:16px;align-items:center;flex-wrap:wrap}
h1{font-size:16px;margin:0}.muted{color:var(--muted)}.pill{display:inline-flex;gap:6px;align-items:center;margin-right:10px;font-size:12px}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block}
"""


def cmd_graph_html(ctx: Ctx, args):
    notes = [n for n in scoped_notes(ctx, args) if n["type"] != "project"]
    edges, _ = derive_links(notes)
    nodes = [{"id": n["path"], "title": n["title"], "type": n["type"], "participant": n["participant"],
              "href": os.path.relpath(ctx.vault / n["path"], Path(args.out).parent).replace("\\", "/") if not ctx.notes_json else n.get("url", "")}
             for n in notes]
    legend = "".join(f'<span class="pill"><span class="dot" style="background:{c}"></span>{t}</span>' for t, c in TYPE_COLORS.items() if t != "project")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Verbatim Graph</title><style>{PAGE_CSS}
svg{{width:100vw;height:calc(100vh - 58px);display:block;background-image:radial-gradient(var(--line) 1px,transparent 1px);background-size:18px 18px}}
#tip{{position:fixed;pointer-events:none;background:var(--card);border:1px solid var(--line);padding:6px 9px;border-radius:6px;font-size:12px;display:none;max-width:280px}}
</style></head><body><header><h1>Verbatim Graph</h1><span class="muted">{len(nodes)} notes · {len(edges)} links · click a node to open it</span><div>{legend}</div></header>
<svg></svg><div id="tip"></div><script src="{D3_URL}"></script><script>
const nodes={json.dumps(nodes, ensure_ascii=False)};const links={json.dumps([{"source": e["from"], "target": e["to"], "kind": e["kind"]} for e in edges], ensure_ascii=False)};
const colors={json.dumps(TYPE_COLORS)};const svg=d3.select("svg"),W=innerWidth,H=innerHeight-58,g=svg.append("g");
svg.call(d3.zoom().scaleExtent([.2,4]).on("zoom",e=>g.attr("transform",e.transform)));
const deg={{}};links.forEach(l=>{{deg[l.source]=(deg[l.source]||0)+1;deg[l.target]=(deg[l.target]||0)+1}});
const sim=d3.forceSimulation(nodes).force("link",d3.forceLink(links).id(d=>d.id).distance(60)).force("charge",d3.forceManyBody().strength(-140)).force("center",d3.forceCenter(W/2,H/2)).force("collide",d3.forceCollide(14));
const link=g.append("g").attr("stroke","#a8a29e").attr("stroke-opacity",.5).selectAll("line").data(links).join("line").attr("stroke-dasharray",d=>d.kind==="wikilink"?"3 3":null);
const tip=document.getElementById("tip");
const node=g.append("g").selectAll("circle").data(nodes).join("circle").attr("r",d=>5+Math.min(10,(deg[d.id]||0)*1.2)).attr("fill",d=>colors[d.type]||"#a8a29e").attr("stroke","var(--bg)").attr("stroke-width",1.5).style("cursor","pointer")
.on("mousemove",(e,d)=>{{tip.style.display="block";tip.style.left=(e.clientX+12)+"px";tip.style.top=(e.clientY+12)+"px";tip.textContent=d.title+" · "+d.type+(d.participant?" · "+d.participant:"")}})
.on("mouseout",()=>tip.style.display="none").on("click",(e,d)=>{{if(d.href)window.open(d.href,"_blank")}})
.call(d3.drag().on("start",(e,d)=>{{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y}}).on("drag",(e,d)=>{{d.fx=e.x;d.fy=e.y}}).on("end",(e,d)=>{{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null}}));
sim.on("tick",()=>{{link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);node.attr("cx",d=>d.x).attr("cy",d=>d.y)}});
</script></body></html>"""
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(page, encoding="utf-8")
    print(f"graph ({len(nodes)} nodes, {len(edges)} links) -> {args.out}")


CLUSTER_COLORS = {"amber": "#fef3c7", "blue": "#dbeafe", "green": "#dcfce7", "rose": "#ffe4e6",
                  "teal": "#ccfbf1", "orange": "#ffedd5", "slate": "#e2e8f0", "violet": "#ede9fe"}


def cmd_canvas_html(ctx: Ctx, args):
    src = Path(args.canvas) if args.canvas else ctx.vault / "graph" / "canvas.json"
    if not src.exists():
        die(f"canvas not found: {src}")
    canvas = json.loads(src.read_text(encoding="utf-8"))
    notes = {n["path"]: n for n in load_notes(ctx)}
    cols = []
    for c in canvas.get("clusters", []):
        bg = CLUSTER_COLORS.get(c.get("color", "slate"), "#e2e8f0")
        cards = []
        for p in c.get("insights", []):
            n = notes.get(p)
            title = n["title"] if n else p
            meta = " · ".join(x for x in ((n or {}).get("participant", ""), (n or {}).get("confidence", "")) if x)
            cards.append(f'<div class="card" style="background:{bg}"><div>{html.escape(title)}</div><div class="meta">{html.escape(meta)}</div></div>')
        why = f'<p class="muted">{html.escape(c.get("rationale", ""))}</p>' if c.get("rationale") else ""
        cols.append(f'<section><h2>{html.escape(c.get("label", "Cluster"))} <span class="muted">{len(cards)}</span></h2>{why}{"".join(cards)}</section>')
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(canvas.get("title", "Affinity Canvas"))}</title><style>{PAGE_CSS}
main{{display:flex;gap:16px;padding:20px;overflow-x:auto;align-items:flex-start}}section{{flex:0 0 260px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}
h2{{font-size:13px;margin:0 0 6px}}.card{{color:#1c1917;border-radius:6px;padding:9px 10px;margin-top:8px;box-shadow:0 1px 2px rgba(0,0,0,.08)}}.meta{{font-size:11px;opacity:.7;margin-top:4px}}
@media (max-width:640px){{main{{flex-direction:column}}section{{flex-basis:auto;width:100%}}}}
</style></head><body><header><h1>{html.escape(canvas.get("title", "Affinity Canvas"))}</h1><span class="muted">{html.escape(canvas.get("generated", ""))} · {sum(len(c.get("insights", [])) for c in canvas.get("clusters", []))} insights</span></header>
<main>{"".join(cols)}</main></body></html>"""
    out = Path(args.out) if args.out else src.with_suffix(".html")
    out.write_text(page, encoding="utf-8")
    print(f"canvas -> {out.as_posix()}")


def cmd_canvas_check(ctx: Ctx, args):
    """Validate a canvas JSON: parses, known colours, every insight of the scope exactly once."""
    src = Path(args.canvas) if args.canvas else ctx.vault / "graph" / "canvas.json"
    if not src.exists():
        die(f"canvas not found: {src}")
    try:
        canvas = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"invalid JSON: {e}")
    notes = load_notes(ctx)
    scope = project_notes(notes, find_project(notes, args.project)) if args.project else notes
    expected = {n["path"] for n in scope if n["type"] == "insight"}
    existing = {n["path"] for n in notes}
    problems, seen = [], {}
    for c in canvas.get("clusters", []):
        label = c.get("label", "?")
        if not c.get("label"):
            problems.append("cluster without label")
        if c.get("color") not in CLUSTER_COLORS:
            problems.append(f"{label}: unknown colour {c.get('color')!r} (use {', '.join(CLUSTER_COLORS)})")
        for p in c.get("insights", []):
            if p in seen:
                problems.append(f"{p}: in two clusters ({seen[p]} / {label})")
            seen[p] = label
            if p not in existing:
                problems.append(f"{p}: not a note in the vault")
    for p in sorted(expected - set(seen)):
        problems.append(f"{p}: insight missing from the canvas")
    for p in problems:
        print("PROBLEM  " + p)
    sizes = ", ".join(f"{c.get('label')} ({len(c.get('insights', []))})" for c in canvas.get("clusters", []))
    print(f"{len(canvas.get('clusters', []))} clusters, {len(seen)}/{len(expected)} insights placed: {sizes}")
    sys.exit(1 if problems else 0)


OBSIDIAN_COLORS = {"rose": "1", "orange": "2", "amber": "3", "green": "4", "teal": "5", "blue": "5", "violet": "6"}


def cmd_canvas_obsidian(ctx: Ctx, args):
    """Write an Obsidian JSON Canvas (.canvas) so clusters can be dragged around in Obsidian."""
    src = Path(args.canvas) if args.canvas else ctx.vault / "graph" / "canvas.json"
    if not src.exists():
        die(f"canvas not found: {src}")
    canvas = json.loads(src.read_text(encoding="utf-8"))
    nodes, W, H, GAP, PAD = [], 320, 140, 60, 30
    for i, c in enumerate(canvas.get("clusters", [])):
        items = c.get("insights", [])
        gx = i * (W + 2 * PAD + GAP)
        gh = PAD * 2 + 40 + len(items) * (H + 20)
        group = {"id": f"g{i}", "type": "group", "label": c.get("label", "Cluster"),
                 "x": gx, "y": 0, "width": W + 2 * PAD, "height": max(gh, 200)}
        if c.get("color") in OBSIDIAN_COLORS:
            group["color"] = OBSIDIAN_COLORS[c["color"]]
        nodes.append(group)
        for j, p in enumerate(items):
            node = {"id": f"n{i}-{j}", "type": "file", "file": p,
                    "x": gx + PAD, "y": PAD + 40 + j * (H + 20), "width": W, "height": H}
            if c.get("color") in OBSIDIAN_COLORS:
                node["color"] = OBSIDIAN_COLORS[c["color"]]
            nodes.append(node)
    base = src.name[:-5] if src.name.endswith(".json") else src.stem
    base = base[:-7] if base.endswith(".canvas") else base
    out = Path(args.out) if args.out else src.with_name(("affinity" if base == "canvas" else base + ".affinity") + ".canvas")
    out.write_text(json.dumps({"nodes": nodes, "edges": []}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"obsidian canvas -> {out.as_posix()}")


def cmd_session_context(ctx: Ctx, args):
    """The project rules + a one-line status. Silent outside a Verbatim project."""
    if not ctx.cfg_path:
        return
    backend = ctx.config.get("backend", "markdown")
    where = "Notion" if backend == "notion" else ctx.vault.as_posix()
    pending = [j for j in list_jobs(ctx) if j["status"] in ("ready", "partial", "draft")]
    counts = "see /verbatim:home"
    if backend != "notion" and ctx.vault.is_dir():
        by = {}
        for n in load_notes(ctx):
            by[n["type"]] = by.get(n["type"], 0) + 1
        counts = ", ".join(f"{v} {k}" for k, v in sorted(by.items())) or "empty vault"
    print("\n".join([
        f"This folder is a Verbatim user-research project (config: {ctx.cfg_path.name}, backend: {backend}, vault: {where}).",
        f"Status: {counts}; pending reviews: {len(pending)}.",
        "Rules for any work on this research data:",
        "- Never write to the vault directly: stage proposals under .verbatim/staging/ and apply only after the user approves"
        " (verbatim:review), unless skip_review is true. Subagents stage; only the main conversation applies.",
        "- Quotes are verbatim and checked with verbatim.py verify-quotes; every answer cites its notes; quotation marks are"
        " for participants' words only (terms and titles in italics); inferences carry low or medium confidence.",
        "- participant/company fields may be comma-separated: split on commas. Deletions go to .verbatim/trash/, never hard deletes.",
        "- Load the verbatim:vault skill before reading or writing notes. Start with /verbatim:home.",
    ]))


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv=None):
    ap = argparse.ArgumentParser(prog="verbatim.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", help="vault folder (default: vault_path from verbatim.config.json)")
    ap.add_argument("--notes-json", help="read notes from a JSON export instead of the vault (Notion backend)")
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("init", help="create the vault folder structure"); p.add_argument("path", nargs="?"); p.set_defaults(fn=cmd_init)
    p = sp.add_parser("session-context", help="the project rules + status (silent outside a project)")
    p.set_defaults(fn=cmd_session_context)
    p = sp.add_parser("slug", help="slugify a title"); p.add_argument("text", nargs="+"); p.set_defaults(fn=cmd_slug)
    p = sp.add_parser("scan", help="list notes as JSON")
    p.add_argument("--type", action="append"); p.add_argument("--grep"); p.add_argument("--full", action="store_true")
    p.add_argument("--excerpt", type=int, default=200); p.set_defaults(fn=cmd_scan)
    p = sp.add_parser("stats", help="vault overview"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=cmd_stats)
    for name, fn in (("people", cmd_people), ("companies", cmd_companies)):
        p = sp.add_parser(name, help=f"{name} directory (comma-split aware)"); p.add_argument("--name"); p.set_defaults(fn=fn)
    p = sp.add_parser("links", help="derived links + broken refs"); p.set_defaults(fn=cmd_links)
    p = sp.add_parser("lint", help="structural health check"); p.add_argument("--stale-days", type=int); p.set_defaults(fn=cmd_lint)
    p = sp.add_parser("dedup", help="Jaccard near-duplicate detection")
    p.add_argument("--threshold", type=float, default=0.22); p.add_argument("--type", action="append", default=None); p.set_defaults(fn=cmd_dedup)
    p = sp.add_parser("tags", help="tag usage + typographic groups"); p.set_defaults(fn=cmd_tags)
    p = sp.add_parser("retag", help="stage a tag rewrite (old=new ...)")
    p.add_argument("--map", action="append", required=True); p.add_argument("--label"); p.set_defaults(fn=cmd_retag)
    p = sp.add_parser("staging", help="review queue: new | seal | list | show | apply | refuse")
    p.add_argument("action", choices=["new", "seal", "list", "show", "apply", "refuse"]); p.add_argument("id", nargs="?")
    p.add_argument("--kind", default="manual"); p.add_argument("--label"); p.add_argument("--diff", action="store_true")
    p.add_argument("--only", nargs="*"); p.add_argument("--exclude", nargs="*"); p.add_argument("--force", action="store_true")
    p.add_argument("--mark-only", action="store_true", help="mark ops applied without touching files (Notion)")
    p.add_argument("--status", nargs="*"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=cmd_staging)
    p = sp.add_parser("index", help="rebuild graph/index.md"); p.set_defaults(fn=cmd_index)
    p = sp.add_parser("notion-cache", help="convert raw Notion rows (query rows mode) into the notes cache")
    p.add_argument("inputs", nargs="+", help="JSON files holding the query results")
    p.add_argument("--bodies", help="optional JSON {page url or slug: page text}")
    p.add_argument("--out", default=".verbatim/cache/notes.json"); p.set_defaults(fn=cmd_notion_cache)
    p = sp.add_parser("verify-quotes", help="check every staged quote appears verbatim in the transcript")
    p.add_argument("id", help="staging job id or folder, a note or export file, or a folder such as vault/")
    p.add_argument("--transcript", action="append", help="repeatable; default: the job's raw/ files, else every vault/raw transcript")
    p.set_defaults(fn=cmd_verify_quotes)
    p = sp.add_parser("stage-raw", help="copy a transcript verbatim into a staging job (raw/<stem>.md)")
    p.add_argument("id", help="staging job id or folder"); p.add_argument("source"); p.add_argument("--stem")
    p.add_argument("--participant"); p.add_argument("--company"); p.add_argument("--interview-date"); p.add_argument("--original")
    p.set_defaults(fn=cmd_stage_raw)
    p = sp.add_parser("patterns", help="cross-participant tag patterns + saturation")
    p.add_argument("--min", type=int, default=2); p.add_argument("--since"); p.set_defaults(fn=cmd_patterns)
    p = sp.add_parser("project", help="list | resolve | snapshot"); p.add_argument("action", choices=["list", "resolve", "snapshot"])
    p.add_argument("ref", nargs="?"); p.set_defaults(fn=cmd_project)
    p = sp.add_parser("export-csv", help="export notes to CSV")
    p.add_argument("--type", action="append", default=None); p.add_argument("--project"); p.add_argument("--out"); p.set_defaults(fn=cmd_export_csv)
    p = sp.add_parser("graph-html", help="standalone D3 graph page")
    p.add_argument("--out", default="exports/graph.html"); p.add_argument("--project"); p.set_defaults(fn=cmd_graph_html)
    p = sp.add_parser("canvas-html", help="render graph/canvas.json as an affinity board")
    p.add_argument("--canvas"); p.add_argument("--out"); p.set_defaults(fn=cmd_canvas_html)
    p = sp.add_parser("canvas-check", help="validate a canvas JSON (colours, every insight exactly once)")
    p.add_argument("--canvas"); p.add_argument("--project"); p.set_defaults(fn=cmd_canvas_check)
    p = sp.add_parser("canvas-obsidian", help="write graph/canvas.json as an Obsidian .canvas board")
    p.add_argument("--canvas"); p.add_argument("--out"); p.set_defaults(fn=cmd_canvas_obsidian)

    args = ap.parse_args(argv)
    if args.cmd in ("dedup", "export-csv") and args.type is None:
        args.type = ["insight"]
    ctx = Ctx(args)
    if args.cmd == "staging" and args.action not in ("new", "list") and not args.id:
        die("staging " + args.action + " needs a job id")
    if args.cmd == "project" and args.action != "list" and not args.ref:
        die("project " + args.action + " needs a project path or name")
    args.fn(ctx, args)


if __name__ == "__main__":
    main()
