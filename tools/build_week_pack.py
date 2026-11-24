"""
Build the weekly paper pack.

Produces, from the two HTML templates:

    templates/03-OPEN-SHEET-A4-wk<NN>.pdf   one OPEN sheet, week + dates + names
    templates/04-KICKOFF-GRID-A4-wk<NN>.pdf five kick-off grids, pre-dated Mon-Fri

The five daily pages are printed **blank but dated**, so the stack for the week
is ready before Monday. `TODAY'S 3` on each kick-off grid is then written in
advance for anything already fixed (a TBT, a gate, a review) and completed at
07:20 — that is the calendar. No side calendar is needed.

Names are printed, never handwritten: one canonical spelling per person, the
same list on the OPEN sheet and on every kick-off grid.

Usage
-----
    python tools/build_week_pack.py                  # the configured week
    python tools/build_week_pack.py --week 50 --monday 2026-12-07

Requires Microsoft Edge (headless, used for the PDF), like tools/build_print.py.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

OPEN_TEMPLATE = TEMPLATES / "03-OPEN-SHEET-A4.html"
GRID_TEMPLATE = TEMPLATES / "04-KICKOFF-GRID-A4.html"

EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

# --------------------------------------------------------------------------
# the week
# --------------------------------------------------------------------------

WEEK = 49
MONDAY = date(2026, 11, 30)

# One canonical spelling per person. Vendors are not people: they appear as
# owners on the OPEN sheet, never as rows here.
PEOPLE = [
    ("HJ Lee", "LQ/IA"),
    ("JH Lee", "Helper"),
    ("YZ", "ICSS"),
    ("Khang", "Mat+PTW"),
    ("Chang", "FIR"),
    ("Kim", "IA"),
    ("Chor Lee", "Helper"),
    ("Antonello", "AIR"),
    ("Seong Lee", "AIR"),
    ("Aras", "Lead"),
    ("Syukri", "Deputy"),
]

GRID_ROWS = 22
COMMIT_ROWS = 12
PEOPLE_ROWS = 22

DAY_NAMES = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def read_template(path: Path) -> tuple[str, str]:
    """Return (style, sheet) — the CSS block and the printable sheet markup."""
    html = path.read_text(encoding="utf-8-sig")
    style = re.search(r"<style>(.*?)</style>", html, re.S)
    sheet = re.search(r"(<div class=\"sheet\">.*?</div>)\s*<script>", html, re.S)
    if not style or not sheet:
        raise SystemExit(f"template shape changed: {path}")
    return style.group(1), sheet.group(1)


def replace_once(text: str, needle: str, repl: str, label: str) -> str:
    if needle not in text:
        raise SystemExit(f"template changed, cannot find: {label}")
    return text.replace(needle, repl, 1)


def num(n: int) -> str:
    return f"{n:02d}"


def grid_rows(people: list[tuple[str, str]], total: int = GRID_ROWS) -> str:
    out = []
    for i in range(1, total + 1):
        name = people[i - 1][0] if i <= len(people) else ""
        out.append(
            f'<tr><td class="num">{num(i)}</td><td>{name}</td><td></td></tr>'
        )
    return "\n".join(out)


def people_rows(people: list[tuple[str, str]], total: int = PEOPLE_ROWS) -> str:
    out = []
    for i in range(total):
        name, role = people[i] if i < len(people) else ("", "")
        out.append(
            f"<tr><td>{name}</td><td>{role}</td><td></td><td></td><td></td></tr>"
        )
    return "\n".join(out)


def commit_rows(total: int = COMMIT_ROWS) -> str:
    out = []
    for i in range(1, total + 1):
        out.append(
            f'<tr><td class="num">{num(i)}</td>'
            "<td></td><td></td><td></td><td></td><td></td></tr>"
        )
    return "\n".join(out)


BASE_CSS = """
.pre { font-size: 10pt; font-weight: 700; letter-spacing: .02em; padding: 0 1mm; }
.noprint, .tools, .hint { display: none !important; }
@media print {
  body { background: #fff; }
  .sheet { margin: 0; }
}
"""

PAGED_CSS = """
@media print {
  .sheet { break-after: page; }
  .sheet:last-of-type { break-after: auto; }
}
"""


def page(title: str, style: str, sheets: list[str], extra_css: str = "") -> str:
    body = "\n".join(sheets)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{style}
{BASE_CSS}
{extra_css}
</style>
</head>
<body>
{body}
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
        profile = Path(tempfile.mkdtemp(prefix="pack-profile-"))
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


# --------------------------------------------------------------------------
# the two documents
# --------------------------------------------------------------------------


def build_open_sheet(week: int, monday: date) -> str:
    style, sheet = read_template(OPEN_TEMPLATE)
    friday = monday + timedelta(days=4)

    sheet = replace_once(
        sheet,
        '<span class="lbl">WK</span><span class="u" style="width:10mm"></span>',
        f'<span class="lbl">WK</span><span class="pre">{week}</span>',
        "week box",
    )

    date_blank = (
        '<span class="u" style="width:8mm"></span>'
        '<span class="sl">/</span>'
        '<span class="u" style="width:8mm"></span>'
    )
    sheet = replace_once(
        sheet,
        date_blank,
        f'<span class="pre">{monday:%d/%m}</span>',
        "start date",
    )
    sheet = replace_once(
        sheet,
        date_blank,
        f'<span class="pre">{friday:%d/%m}</span>',
        "end date",
    )

    sheet = replace_once(
        sheet,
        '<tbody id="peopleRows"></tbody>',
        f'<tbody id="peopleRows">\n{people_rows(PEOPLE)}\n</tbody>',
        "people rows",
    )
    sheet = replace_once(
        sheet,
        '<tbody id="commitRows"></tbody>',
        f'<tbody id="commitRows">\n{commit_rows()}\n</tbody>',
        "commitment rows",
    )

    return page(f"OPEN sheet — week {week}", style, [sheet])


def build_kickoff_pack(week: int, monday: date) -> str:
    style, base = read_template(GRID_TEMPLATE)
    sheets = []

    for offset, day_name in enumerate(DAY_NAMES):
        day = monday + timedelta(days=offset)
        sheet = base

        sheet = replace_once(
            sheet,
            '<div class="cap">Week <span class="u" style="width: 12mm"></span></div>',
            f'<div class="cap">Week <span class="pre">{week}</span></div>',
            "week",
        )
        sheet = replace_once(
            sheet,
            '<span class="u" style="width: 11mm"></span>'
            '<span class="sl">/</span>'
            '<span class="u" style="width: 11mm"></span>',
            f'<span class="pre">{day:%d/%m}</span>',
            "date",
        )
        sheet = replace_once(
            sheet,
            '<span class="u" style="width: 38mm"></span>',
            f'<span class="pre">{day_name}</span>',
            "day name",
        )
        sheet = replace_once(
            sheet,
            '<tbody id="gridRows"></tbody>',
            f'<tbody id="gridRows">\n{grid_rows(PEOPLE)}\n</tbody>',
            "grid rows",
        )
        sheets.append(sheet)

    return page(f"Kick-off grids — week {week}", style, sheets, PAGED_CSS)


# --------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", type=int, default=WEEK)
    parser.add_argument(
        "--monday",
        type=date.fromisoformat,
        default=MONDAY,
        help="Monday of the week, YYYY-MM-DD",
    )
    parser.add_argument("--no-pdf", action="store_true")
    args = parser.parse_args()

    if args.monday.weekday() != 0:
        print("--monday must be a Monday", flush=True)
        return 1

    edge = find_edge()
    jobs = [
        (build_open_sheet(args.week, args.monday), f"03-OPEN-SHEET-A4-wk{args.week}"),
        (build_kickoff_pack(args.week, args.monday), f"04-KICKOFF-GRID-A4-wk{args.week}"),
    ]

    for html, stem in jobs:
        html_path = TEMPLATES / f"{stem}.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"html  {html_path.relative_to(ROOT)}")

        if args.no_pdf:
            continue
        if not edge:
            print("Edge not found - HTML only", flush=True)
            continue

        pdf_path = TEMPLATES / f"{stem}.pdf"
        if make_pdf(edge, html_path, pdf_path):
            print(f"pdf   {pdf_path.relative_to(ROOT)}")
        else:
            print(f"pdf failed: {pdf_path}", flush=True)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
