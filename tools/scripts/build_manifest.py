#!/usr/bin/env python3
"""
Builds anchors.json (and optional index.html) from a folder of Obsidian Markdown anchor files.

Usage:
  python build_manifest.py --src ./anchors --out ./anchors.json --vault "ThreadVault" [--html ./index.html]

Rules:
- Expects files named like: Continuity_Anchor_XX_Title_UID.md (UID anywhere is fine).
- Reads frontmatter-style lines like `UID:: abcd1234` and `Date:: 2025-08-27` if present.
- Title priority: first H1 (# ...), then "Title:" line, else filename (without .md and UID).
- Excerpt: first non-empty paragraph after metadata lines.
- sha256: computed from the file's raw bytes.
- Obsidian URI: obsidian://open?vault=<vault>&file=<filename_without_ext>

This script is read-only. It does not modify your notes.
"""
import argparse, pathlib, hashlib, json, re, html

H1 = re.compile(r'^\s*#\s+(.*)\s*$')
UIDLINE = re.compile(r'^\s*UID::\s*([A-Za-z0-9_-]+)\s*$')
DATELINE = re.compile(r'^\s*Date::\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$')

def sha256_path(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def infer_title(name: str) -> str:
    # Strip extension and UID-ish suffixes
    base = name.rsplit('.', 1)[0]
    # remove trailing _UID if looks like 6-12 hex/word chars
    base = re.sub(r'_[A-Za-z0-9_-]{6,12}$', '', base)
    return base.replace('_', ' ')

def parse_file(p: pathlib.Path):
    uid = None
    date = None
    title = None
    excerpt_lines = []
    meta_done = False

    with p.open('r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if uid is None:
            m = UIDLINE.match(line)
            if m: uid = m.group(1).strip()
        if date is None:
            m = DATELINE.match(line)
            if m: date = m.group(1).strip()
        if title is None:
            m = H1.match(line)
            if m: title = m.group(1).strip()

    # find first non-empty paragraph as excerpt (skip meta-like lines)
    buf = []
    for line in lines:
        if UIDLINE.match(line) or DATELINE.match(line) or H1.match(line):
            if buf: break
            continue
        if line.strip() == '':
            if buf:
                break
            else:
                continue
        buf.append(line.rstrip())

    excerpt = ' '.join(buf).strip()
    if not title:
        title = infer_title(p.name)

    # try to glean number from filename
    number = None
    m = re.search(r'Anchor[ _-]*([0-9]{1,3})', p.name, flags=re.IGNORECASE)
    if m:
        try:
            number = int(m.group(1))
        except:
            pass

    # fallback UID: derive from filename if missing
    if not uid:
        m = re.search(r'([A-Fa-f0-9]{6,12})', p.name)
        if m:
            uid = m.group(1)
        else:
            uid = hashlib.sha1(p.name.encode('utf-8')).hexdigest()[:8]

    return {
        "uid": uid,
        "title": title,
        "number": number,
        "date": date,
        "file": p.name,
        "sha256": sha256_path(p),
        "excerpt": excerpt
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Folder containing anchor .md files")
    ap.add_argument("--out", required=True, help="Output anchors.json path")
    ap.add_argument("--vault", required=True, help="Your Obsidian vault name (case sensitive as in Obsidian)")
    ap.add_argument("--html", default=None, help="Optional index.html output path")
    args = ap.parse_args()

    src = pathlib.Path(args.src)
    files = sorted([p for p in src.glob("*.md") if p.is_file()], key=lambda p: p.name.lower())
    anchors = []
    for p in files:
        a = parse_file(p)
        # add Obsidian URI
        file_no_ext = a["file"].rsplit('.', 1)[0]
        a["obsidian_uri"] = f"obsidian://open?vault={args.vault}&file={file_no_ext}"
        anchors.append(a)

    manifest = {
        "version": pathlib.Path(args.out).stat().st_mtime_ns if pathlib.Path(args.out).exists() else None,
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "vault": args.vault,
        "count": len(anchors),
        "anchors": anchors
    }

    outp = pathlib.Path(args.out)
    outp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.html:
        # very small static page
        rows = []
        for a in anchors:
            title = html.escape(a["title"] or "")
            uid = html.escape(a["uid"] or "")
            date = html.escape(a.get("date") or "")
            uri = html.escape(a["obsidian_uri"])
            excerpt = html.escape(a.get("excerpt") or "")
            rows.append(f'<li><a href="{uri}">{title}</a> <code>{uid}</code> <small>{date}</small><br><em>{excerpt}</em></li>')
        html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>Thread Anchors</title></head>
<body>
<h1>Thread Anchors</h1>
<ul>
{''.join(rows)}
</ul>
</body></html>
"""
        pathlib.Path(args.html).write_text(html_doc, encoding="utf-8")

    print(f"Wrote {args.out} with {len(anchors)} anchors.")
    if args.html:
        print(f"Wrote {args.html}.")

if __name__ == "__main__":
    main()
