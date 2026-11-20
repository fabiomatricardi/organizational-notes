"""
Import/Export API router.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, PlainTextResponse
from backend.services import excel_parser, database, entries as entries_service
from backend.database import get_db
import tempfile
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/import/excel")
async def import_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Must be .xlsx or .xls")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = await excel_parser.import_excel(tmp_path)
        os.unlink(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/excel")
async def export_excel():
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp_path = tmp.name

        result = await excel_parser.export_excel(tmp_path)
        return FileResponse(
            tmp_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="personal_log_export.xlsx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backup")
async def backup_database():
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            tmp_path = tmp.name

        result = await database.backup_database(tmp_path)
        if result["success"]:
            return FileResponse(
                tmp_path,
                media_type="application/octet-stream",
                filename=f"personal_log_backup_{result['timestamp'][:10]}.db"
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore")
async def restore_database(file: UploadFile = File(...)):
    if not file.filename.endswith('.db'):
        raise HTTPException(status_code=400, detail="Invalid file format. Must be .db file")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = await database.restore_database(tmp_path)
        os.unlink(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_database_info():
    return await database.get_database_info()


@router.get("/export/handover")
async def export_handover(days: int = 7):
    """Markdown handover note generated from the open register (for leave / back-to-back)."""
    follow = await entries_service.get_follow_up()
    items = follow["items"]
    counts = follow["counts"]

    today = datetime.now()
    week = today.isocalendar()[1]

    lines = [
        f"# Handover — {today.strftime('%Y-%m-%d')} (Week {week})",
        "",
        f"Generated from the open register: **{counts['open']} open**, "
        f"**{counts['overdue']} overdue**, **{counts['stale']} stale**, "
        f"**{counts['orphan']} without owner**.",
        "",
        "## By owner",
        "",
    ]

    if not follow["groups"]:
        lines.append("_No open items._")
    for owner, owner_items in follow["groups"].items():
        lines.append(f"### {owner}")
        for item in owner_items:
            flags = []
            if item.get("overdue"):
                flags.append("OVERDUE")
            if item.get("stale"):
                flags.append("STALE")
            if item.get("orphan"):
                flags.append("NO OWNER")
            flag_text = f" — **{', '.join(flags)}**" if flags else ""
            lines.append(
                f"- #{item['id']} [{item.get('area') or '-'}] {item.get('activity', '')[:300]} "
                + f"— due {item.get('due') or 'TBC'}, age {item.get('age_days')}d{flag_text}"
            )
        lines.append("")

    overdue = [i for i in items if i["overdue"] or i["stale"]]
    if overdue:
        lines += ["## Chase first", ""]
        for item in overdue[:12]:
            lines.append(
                f"- #{item['id']} {item.get('owner') or 'unassigned'} — "
                f"{item.get('activity', '')[:160]} — due {item.get('due') or 'TBC'}"
            )
        lines.append("")

    waiting = [i for i in items if i.get("waiting")]
    if waiting:
        lines += ["## Waiting on others", ""]
        for item in waiting:
            lines.append(f"- #{item['id']} {item.get('follow_up') or ''} — {item.get('activity', '')[:160]}")
        lines.append("")

    cutoff = (today - timedelta(days=days)).isoformat()
    recent = await entries_service.get_all_entries(limit=200)
    risks = [
        e for e in recent
        if e.get("type") == "LOG" and str(e.get("timestamp", "")) >= cutoff
        and ("!" in str(e.get("activity", ""))[:400])
    ]
    if risks:
        lines += [f"## Risks flagged in the last {days} days", ""]
        for entry in risks[:10]:
            first = str(entry.get("activity", "")).strip().splitlines()
            lines.append(f"- #{entry['id']} {first[0][:220] if first else ''}")
        lines.append("")

    lines += [
        "## Notes for my back-to-back",
        "",
        "- _Add 3 lines here: what must not stop, who to speak to first, what can wait._",
        "",
    ]

    content = "\n".join(lines)

    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO analysis_reports (report_type, period_start, period_end, content, generated_at)
               VALUES ('handover', ?, ?, ?, ?)""",
            (today.date().isoformat(), today.date().isoformat(), content, today.isoformat())
        )
        await db.commit()
    finally:
        await db.close()

    return PlainTextResponse(content, media_type="text/markdown")
