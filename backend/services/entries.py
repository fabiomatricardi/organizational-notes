"""
Log entries CRUD service.
"""
from backend.database import get_db
from datetime import datetime
from typing import Optional

FIELDS = ["timestamp", "activity", "type", "follow_up", "status", "reference_id",
          "eta", "owner", "next_check", "area"]

OPEN_STATUSES = ("PENDING", "ASSIGNED", "ONGOING", "LOG")


async def get_all_entries(
    entry_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    owner: Optional[str] = None,
    area: Optional[str] = None,
    open_only: bool = False,
    limit: int = 100,
    offset: int = 0
) -> list[dict]:
    db = await get_db()
    try:
        query = "SELECT * FROM log_entries WHERE 1=1"
        params = []

        if entry_type:
            query += " AND type = ?"
            params.append(entry_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        if search:
            query += " AND (activity LIKE ? OR follow_up LIKE ? OR owner LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        if date_from:
            query += " AND timestamp >= ?"
            params.append(date_from)

        if date_to:
            query += " AND timestamp <= ?"
            params.append(date_to + "T23:59:59")

        if owner:
            query += " AND owner = ?"
            params.append(owner)

        if area:
            query += " AND area = ?"
            params.append(area)

        if open_only:
            query += " AND type IN ('TODO', 'TASK') AND status != 'COMPLETED'"

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        entries = []
        for row in rows:
            entry = dict(row)
            entry["tags"] = await _get_entry_tags(db, entry["id"])
            entries.append(entry)
        return entries
    finally:
        await db.close()


async def get_entry(entry_id: int) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM log_entries WHERE id = ?", (entry_id,))
        row = await cursor.fetchone()
        if row:
            entry = dict(row)
            entry["tags"] = await _get_entry_tags(db, entry["id"])
            return entry
        return None
    finally:
        await db.close()


async def create_entry(data: dict) -> dict:
    db = await get_db()
    try:
        now = datetime.now().isoformat()
        timestamp = data.get("timestamp") or now
        status = data.get("status") or ("LOG" if data.get("type") == "LOG" else "PENDING")

        cursor = await db.execute(
            """INSERT INTO log_entries
                   (timestamp, activity, type, follow_up, status, reference_id, eta,
                    owner, next_check, area, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                timestamp,
                data["activity"],
                data["type"],
                data.get("follow_up"),
                status,
                data.get("reference_id"),
                data.get("eta"),
                data.get("owner"),
                data.get("next_check"),
                data.get("area"),
                now,
                now
            )
        )
        await db.commit()
        entry_id = cursor.lastrowid

        if "tags" in data:
            for tag_id in data["tags"]:
                await db.execute(
                    "INSERT INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
                    (entry_id, tag_id)
                )
            await db.commit()

        return await get_entry(entry_id)
    finally:
        await db.close()


async def update_entry(entry_id: int, data: dict) -> Optional[dict]:
    db = await get_db()
    try:
        existing = await get_entry(entry_id)
        if not existing:
            return None

        updates = []
        params = []

        for field in FIELDS:
            if field in data and data[field] is not None and data[field] != "":
                updates.append(f"{field} = ?")
                params.append(data[field])

        # Explicitly allow clearing these optional fields with an empty string
        for field in ["owner", "next_check", "area", "eta", "follow_up"]:
            if field in data and data[field] == "":
                updates.append(f"{field} = ?")
                params.append(None)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(entry_id)

            query = f"UPDATE log_entries SET {', '.join(updates)} WHERE id = ?"
            await db.execute(query, params)
            await db.commit()

        if "tags" in data:
            await db.execute("DELETE FROM entry_tags WHERE entry_id = ?", (entry_id,))
            for tag_id in data["tags"]:
                await db.execute(
                    "INSERT INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
                    (entry_id, tag_id)
                )
            await db.commit()

        return await get_entry(entry_id)
    finally:
        await db.close()


async def delete_entry(entry_id: int) -> bool:
    db = await get_db()
    try:
        await db.execute("DELETE FROM entry_tags WHERE entry_id = ?", (entry_id,))
        cursor = await db.execute("DELETE FROM log_entries WHERE id = ?", (entry_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


def _decorate_open_item(row: dict) -> dict:
    """Add age / due / overdue / stale / orphan flags to an open item."""
    item = dict(row)
    now = datetime.now()
    today = now.date().isoformat()

    item["tags"] = item.get("tags") or []
    try:
        item["age_days"] = (now - datetime.fromisoformat(str(item["timestamp"]).replace("Z", "+00:00").split("+")[0])).days
    except (ValueError, TypeError):
        item["age_days"] = None

    nxt = (item.get("next_check") or "")[:10]
    due = nxt or (item.get("eta") or "")[:10]

    item["due"] = due or None
    item["overdue"] = bool(nxt and nxt < today)
    item["stale"] = bool(
        (nxt and nxt < today)
        or (not nxt and item.get("age_days") is not None and item["age_days"] > 7)
    )
    item["orphan"] = not (item.get("owner") or "").strip()
    item["waiting"] = (item.get("follow_up") or "").lower().startswith("waiting")

    if not item["overdue"] and item.get("eta"):
        item["overdue"] = (item["eta"][:10] < today) and item.get("status") != "COMPLETED"

    return item


async def get_open_items() -> list[dict]:
    """All TODO/TASK that are not completed, decorated and sorted by urgency."""
    rows = await get_all_entries(open_only=True, limit=2000)
    items = [_decorate_open_item(row) for row in rows]

    def sort_key(it):
        return (
            0 if it["overdue"] else 1,
            0 if it["stale"] else 1,
            it["due"] or "9999-99-99",
            -(it["age_days"] or 0),
        )

    items.sort(key=sort_key)
    return items


async def get_follow_up() -> dict:
    items = await get_open_items()

    counts = {
        "open": len(items),
        "overdue": sum(1 for i in items if i["overdue"]),
        "stale": sum(1 for i in items if i["stale"]),
        "orphan": sum(1 for i in items if i["orphan"]),
        "waiting": sum(1 for i in items if i["waiting"]),
    }

    groups: dict[str, list[dict]] = {}
    for item in items:
        name = (item.get("owner") or "").strip() or "Unassigned"
        groups.setdefault(name, []).append(item)

    ordered = dict(sorted(groups.items(), key=lambda kv: (kv[0] == "Unassigned", kv[0].lower())))
    return {"items": items, "groups": ordered, "counts": counts}


async def get_today() -> dict:
    today = datetime.now().date().isoformat()
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM log_entries WHERE timestamp LIKE ? ORDER BY timestamp ASC",
            (f"{today}%",)
        )
        rows = [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()

    for row in rows:
        row["tags"] = []

    open_items = await get_open_items()
    due = [
        i for i in open_items
        if (i["due"] == today) or i["overdue"] or i["stale"]
    ]

    return {
        "date": today,
        "entries": rows,
        "due": due,
        "counts": {
            "entries": len(rows),
            "due": len(due),
            "open": len(open_items),
        },
    }


async def get_dashboard_stats() -> dict:
    open_items = await get_open_items()
    db = await get_db()
    try:
        stats = {}

        cursor = await db.execute("SELECT COUNT(*) FROM log_entries")
        stats["total_entries"] = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM log_entries WHERE type = 'LOG'")
        stats["total_logs"] = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM log_entries WHERE type = 'TODO'")
        stats["total_todos"] = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM log_entries WHERE type = 'TASK'")
        stats["total_tasks"] = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM log_entries WHERE type = 'TASK' AND status = 'PENDING'")
        stats["pending_tasks"] = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM log_entries WHERE type = 'TASK' AND status = 'ASSIGNED'")
        stats["assigned_tasks"] = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM log_entries WHERE type = 'TASK' AND status = 'ONGOING'")
        stats["ongoing_tasks"] = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM log_entries WHERE type = 'TASK' AND status = 'COMPLETED'")
        stats["completed_tasks"] = (await cursor.fetchone())[0]

        now = datetime.now().isoformat()
        cursor = await db.execute(
            "SELECT COUNT(*) FROM log_entries WHERE type IN ('TODO', 'TASK') AND eta < ? AND status != 'COMPLETED'",
            (now,)
        )
        stats["overdue_tasks"] = (await cursor.fetchone())[0]

        stats["open_items"] = len(open_items)
        stats["overdue_items"] = sum(1 for i in open_items if i["overdue"])
        stats["stale_items"] = sum(1 for i in open_items if i["stale"])
        stats["orphan_items"] = sum(1 for i in open_items if i["orphan"])

        return stats
    finally:
        await db.close()


async def get_inbox(processed: int = 0, limit: int = 100) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM inbox WHERE processed = ? ORDER BY received_at DESC LIMIT ?",
            (processed, limit)
        )
        return [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()


async def _get_entry_tags(db, entry_id: int) -> list[dict]:
    cursor = await db.execute(
        """SELECT t.id, t.name, t.color FROM tags t
           JOIN entry_tags et ON t.id = et.tag_id
           WHERE et.entry_id = ?""",
        (entry_id,)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
