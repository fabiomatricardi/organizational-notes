"""
Inbox API router: items captured from Telegram (text and photos) before triage.
"""
import mimetypes

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from backend.database import get_data_dir, get_db
from backend.models import InboxConvertRequest
from backend.services import entries, telegram
from backend.services.config import load_config

router = APIRouter(prefix="/api/inbox", tags=["inbox"])


@router.get("")
async def list_inbox(
    processed: int = Query(0, description="0 = pending triage, 1 = already handled"),
    limit: int = Query(100, ge=1, le=500)
):
    items = await entries.get_inbox(processed=processed, limit=limit)
    return {"items": items, "total": len(items)}


@router.get("/count")
async def inbox_count():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) FROM inbox WHERE processed = 0")
        count = (await cursor.fetchone())[0]
    finally:
        await db.close()
    return {"pending": count}


@router.get("/telegram/status")
async def telegram_status():
    config = load_config().get("telegram", {}) or {}
    token = (config.get("bot_token") or "").strip()
    result = {
        "enabled": bool(config.get("enabled")),
        "configured": bool(token),
        "allowed_chat_ids": config.get("allowed_chat_ids") or [],
    }
    if not token:
        return result
    try:
        me = await telegram.get_me(token)
        result["bot"] = {"username": me.get("username"), "name": me.get("first_name")}
        result["ok"] = True
    except Exception as exc:
        result["ok"] = False
        result["error"] = str(exc)
    return result


@router.get("/{item_id}/photo")
async def inbox_photo(item_id: int):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT file_path FROM inbox WHERE id = ?", (item_id,))
        row = await cursor.fetchone()
    finally:
        await db.close()

    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="No photo for this item")

    path = get_data_dir() / row[0]
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Photo file not found")

    media_type = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    return FileResponse(str(path), media_type=media_type)


@router.post("/{item_id}/convert")
async def convert_inbox(item_id: int, request: InboxConvertRequest):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM inbox WHERE id = ?", (item_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Inbox item not found")
        item = dict(row)

        activity = (request.activity or item.get("body") or "").strip()
        if not activity:
            raise HTTPException(status_code=400, detail="Activity is empty")

        entry = await entries.create_entry({
            "activity": activity,
            "type": request.type or "LOG",
            "status": request.status,
            "follow_up": request.follow_up,
            "owner": request.owner,
            "eta": request.eta,
            "next_check": request.next_check,
            "area": request.area,
        })

        if request.delete_after:
            await db.execute("DELETE FROM inbox WHERE id = ?", (item_id,))
        else:
            await db.execute(
                "UPDATE inbox SET processed = 1, entry_id = ? WHERE id = ?",
                (entry["id"], item_id)
            )
        await db.commit()
        return {"entry": entry, "inbox_id": item_id, "deleted": request.delete_after}
    finally:
        await db.close()


@router.post("/{item_id}/attach")
async def attach_inbox(item_id: int, entry_id: int = Query(...)):
    db = await get_db()
    try:
        cursor = await db.execute(
            "UPDATE inbox SET processed = 1, entry_id = ? WHERE id = ?",
            (entry_id, item_id)
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Inbox item not found")
    finally:
        await db.close()
    return {"status": "attached", "inbox_id": item_id, "entry_id": entry_id}


@router.delete("/{item_id}")
async def discard_inbox(item_id: int):
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM inbox WHERE id = ?", (item_id,))
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Inbox item not found")
    finally:
        await db.close()
    return {"status": "discarded"}
