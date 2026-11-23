"""
Render the method documents to a print-ready A4 PDF.

No third-party dependencies: a small Markdown subset renderer (headings,
paragraphs, tables, lists, task lists, blockquotes, rules) plus a dedicated
print stylesheet (tools/print.css).

Usage
-----
    python tools/build_print.py            # build both documents + PDFs
    python tools/build_print.py --only 02  # one document
    python tools/build_print.py --no-pdf   # HTML only

Requires Microsoft Edge (used headless for the PDF). Output goes to
docs/print/<name>.html and docs/print/<name>.pdf.
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
OUT_DIR = DOCS_DIR / "print"
CSS_FILE = ROOT / "tools" / "print.css"

EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

VERSION = "1.2"
TODAY = date.today().isoformat()

DOCS = [
    {
        "key": "00",
        "src": DOCS_DIR / "00-how-it-works.md",
        "out": "00-how-it-works",
        "kicker": "Organizational notes · Pin this above the desk",
        "deck": "You keep one page that says what is still open and who owes it. Everything else exists to keep that page true.",
        "footer": "How it works",
        "breaks": [],
        "notes": 0,
        "onepager": True,
        "bignum": "",
    },
    {
        "key": "02",
        "src": DOCS_DIR / "02-legend-and-examples.md",
        "out": "02-legend-and-examples",
        "kicker": "Organizational notes · Reference 02",
        "deck": "Six marks, three real boards, and the anti-patterns that create ghosts.",
        "footer": "Legend and worked examples",
        "breaks": [],
        "notes": 18,
    },
    {
        "key": "03",
        "src": DOCS_DIR / "03-first-two-weeks.md",
        "out": "03-first-two-weeks",
        "kicker": "Organizational notes · Rollout 03",
        "deck": "Week 1 is capture and the sheet. Nothing else. The rest waits.",
        "footer": "First two weeks, step by step",
        "breaks": [],
        "notes": 15,
    },
]

# --------------------------------------------------------------------------
# inline formatting
# --------------------------------------------------------------------------

CODE_RE = re.compile(r"`([^`]+)`")


def inline(text: str) -> str:
    """Escape HTML and apply the inline Markdown subset, protecting code spans."""
    spans: list[str] = []

    def stash(match: re.Match) -> str:
        spans.append(match.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = CODE_RE.sub(stash, text)
    text = html.escape(text)

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)

    def unstash(match: re.Match) -> str:
        body = html.escape(spans[int(match.group(1))])
        return f"<code>{body}</code>"

    return re.sub(r"\x00(\d+)\x00", unstash, text)


# --------------------------------------------------------------------------
# block parsing
# --------------------------------------------------------------------------

LIST_RE = re.compile(r"^(- \[[ xX]\]\s+|[-*]\s+)")
ORDERED_RE = re.compile(r"^\d+\.\s+")
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")


def parse_blocks(text: str):
    lines = text.splitlines()
    blocks = []
    i, n = 0, len(lines)

    while i < n:
        raw = lines[i]
        s = raw.strip()

        if not s:
            i += 1
            continue

        if s.startswith("```"):
            i += 1
            body = []
            while i < n and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            blocks.append(("pre", "\n".join(body)))
            continue

        if set(s) <= {"-", "*", "_"} and len(s) >= 3:
            blocks.append(("hr", ""))
            i += 1
            continue

        m = HEADING_RE.match(s)
        if m:
            blocks.append((f"h{len(m.group(1))}", m.group(2).strip()))
            i += 1
            continue

        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            blocks.append(("table", rows))
            continue

        if s.startswith(">"):
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            blocks.append(("quote", " ".join(quote)))
            continue

        if LIST_RE.match(s) or ORDERED_RE.match(s):
            items = []
            ordered = bool(ORDERED_RE.match(s))
            while i < n:
                t = lines[i].strip()
                if not t:
                    nxt = lines[i + 1].strip() if i + 1 < n else ""
                    if LIST_RE.match(nxt) or ORDERED_RE.match(nxt):
                        i += 1
                        continue
                    break
                mt = re.match(r"^- \[([ xX])\]\s+(.*)$", t)
                if mt:
                    items.append(("task", mt.group(2), mt.group(1).lower() == "x"))
                    i += 1
                    continue
                ml = re.match(r"^[-*]\s+(.*)$", t)
                if ml:
                    items.append(("li", ml.group(1), False))
                    i += 1
                    continue
                mo = re.match(r"^\d+\.\s+(.*)$", t)
                if mo:
                    ordered = True
                    items.append(("li", mo.group(1), False))
                    i += 1
                    continue
                break
            blocks.append(("ol" if ordered else "ul", items))
            continue

        para = []
        while i < n:
            t = lines[i].strip()
            if not t:
                break
            if (
                t.startswith(("#", "|", ">", "```"))
                or (set(t) <= {"-", "*", "_"} and len(t) >= 3)
                or LIST_RE.match(t)
                or ORDERED_RE.match(t)
            ):
                break
            para.append(t)
            i += 1
        blocks.append(("p", " ".join(para)))

    return blocks


def split_row(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def drop_redundant_rules(blocks):
    """A thematic break immediately before a section heading is noise."""
    out = []
    for index, block in enumerate(blocks):
        if block[0] == "hr":
            following = next((b for b in blocks[index + 1:] if b[0] != "hr"), None)
            if following and following[0] == "h2":
                continue
        out.append(block)
    return out


def table_class(header: list[str]) -> str:
    h = [cell.strip().lower() for cell in header]
    if h[:2] == ["on the board", "written as"] or h[:2] == ["log line (today)", "better"]:
        return "map"
    if h and h[0] == "mark" and len(h) > 1 and "write it when" in h[1]:
        return "marks"
    if h and h[0] == "mark" and "type" in h:
        return "app"
    return "plain"


def render_table(rows: list[str]) -> str:
    parsed = [split_row(r) for r in rows]
    header = parsed[0]
    body = [r for r in parsed[1:] if not all(re.fullmatch(r":?-{2,}:?", c or "-") for c in r)]

    width = len(header)
    cls = table_class(header)

    out = [f'<table class="{cls}">', "<thead><tr>"]
    for cell in header:
        out.append(f"<th>{inline(cell)}</th>")
    out.append("</tr></thead><tbody>")

    for row in body:
        row = (row + [""] * width)[:width]
        out.append("<tr>")
        for cell in row:
            out.append(f"<td>{inline(cell)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def render_blocks(blocks, breaks: list[str]) -> str:
    out: list[str] = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>" if in_list == "ul" else "</ol>")
            in_list = False

    for kind, value, *rest in blocks:
        if kind not in ("ul", "ol"):
            close_list()

        if kind == "h1":
            continue  # the masthead carries the title

        if kind == "h2":
            forced = any(value.startswith(prefix) for prefix in breaks)
            cls = ' class="newpage"' if forced else ""
            out.append(f"<h2{cls}>{inline(value)}</h2>")

        elif kind == "h3":
            out.append(f"<h3>{inline(value)}</h3>")

        elif kind == "p":
            text = value
            if text.startswith("**Test for a good line:**"):
                out.append(f'<div class="callout">{inline(text)}</div>')
            elif text.startswith("Print this and keep it"):
                out.append(f'<p class="note">{inline(text)}</p>')
            else:
                out.append(f"<p>{inline(text)}</p>")

        elif kind in ("ul", "ol"):
            if not in_list:
                out.append("<ul>" if kind == "ul" else "<ol>")
                in_list = kind
            for item_kind, item_text, checked in value:
                if item_kind == "task":
                    out.append(
                        f'<li class="task"><span class="box"></span>'
                        f"{'<s>' if checked else ''}{inline(item_text)}"
                        f"{'</s>' if checked else ''}</li>"
                    )
                else:
                    out.append(f"<li>{inline(item_text)}</li>")

        elif kind == "table":
            out.append(render_table(value))

        elif kind == "quote":
            out.append(f"<blockquote><p>{inline(value)}</p></blockquote>")

        elif kind == "hr":
            out.append("<hr>")

        elif kind == "pre":
            out.append(f"<pre><code>{html.escape(value)}</code></pre>")

    close_list()
    return "\n".join(out)


# --------------------------------------------------------------------------
# page assembly
# --------------------------------------------------------------------------


def build_html(doc: dict) -> str:
    source = doc["src"].read_text(encoding="utf-8-sig")
    blocks = drop_redundant_rules(parse_blocks(source))
    css = CSS_FILE.read_text(encoding="utf-8-sig").lstrip("\ufeff")
    body = render_blocks(blocks, doc.get("breaks", []))
    notes_count = int(doc.get("notes", 0))
    notes_block = ""
    if notes_count:
        lines = "\n".join('<div class="rule-line"></div>' for _ in range(notes_count))
        notes_block = (
            '<div class="notes">\n'
            '<div class="notes-label">Notes</div>\n'
            f"{lines}\n"
            "</div>"
        )

    body_class = ' class="onepager"' if doc.get("onepager") else ""
    bignum = doc.get("bignum", doc["key"])
    bignum_html = f'<div class="bignum">{bignum}</div>' if bignum else ""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(doc['footer'])}</title>
<style>
{css}
</style>
</head>
<body{body_class}>
<header class="masthead">
  <div>
    <div class="kicker">{html.escape(doc['kicker'])}</div>
    <h1>{html.escape(doc['footer'])}</h1>
    <p class="deck">{html.escape(doc['deck'])}</p>
  </div>
  {bignum_html}
</header>
<div class="meta">
  <span>v{VERSION} · {TODAY} · A4 · black &amp; white</span>
  <span>organizational-notes · fabiomatricardi</span>
</div>

{body}

{notes_block}
<div class="colophon">
  <span>Organizational notes · {html.escape(doc['footer'])}</span>
  <span>v{VERSION} · {TODAY} · A4</span>
</div>
</body>
</html>
"""

def find_edge() -> Path | None:
    for candidate in EDGE_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def make_pdf(edge: Path, html_path: Path, pdf_path: Path) -> bool:
    pdf_path.unlink(missing_ok=True)

    for _attempt in range(2):
        profile = Path(tempfile.mkdtemp(prefix="print-profile-"))
        try:
            subprocess.run(
                [
                    str(edge),
                    "--headless",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--no-first-run",
                    "--virtual-time-budget=3000",
                    f"--user-data-dir={profile}",
                    "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}",
                    html_path.as_uri(),
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=90,
            )
        except subprocess.TimeoutExpired:
            pass
        finally:
            shutil.rmtree(profile, ignore_errors=True)

        if pdf_path.is_file() and pdf_path.stat().st_size > 1000:
            return True

    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=[d["key"] for d in DOCS])
    parser.add_argument("--no-pdf", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    edge = find_edge()

    for doc in DOCS:
        if args.only and doc["key"] != args.only:
            continue

        if not doc["src"].is_file():
            print(f"missing source: {doc['src']}", file=sys.stderr)
            return 1

        html_path = OUT_DIR / f"{doc['out']}.html"
        html_path.write_text(build_html(doc), encoding="utf-8")
        print(f"html  {html_path.relative_to(ROOT)}")

        if args.no_pdf:
            continue
        if not edge:
            print("Edge not found - HTML only", file=sys.stderr)
            continue

        pdf_path = OUT_DIR / f"{doc['out']}.pdf"
        if make_pdf(edge, html_path, pdf_path):
            print(f"pdf   {pdf_path.relative_to(ROOT)}")
        else:
            print(f"pdf failed: {pdf_path}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
