"""
Database compaction service - AI-powered duplicate detection and merge.
"""
import json
import os
import re
import shutil
from datetime import datetime
from backend.database import get_db, get_db_path
from backend.services.llm_service import call_llm
from backend.services.entries import get_all_entries, get_entry, update_entry, delete_entry


def _create_backup() -> str:
    """Create a timestamped backup of the database before merge."""
    db_path = get_db_path()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.path.dirname(db_path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"personal_log_backup_pre_merge_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


async def get_compaction_stats() -> dict:
    """Get database statistics for compaction view."""
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

        cursor = await db.execute("SELECT MIN(timestamp), MAX(timestamp) FROM log_entries")
        date_range = await cursor.fetchone()
        stats["date_range_earliest"] = date_range[0] if date_range[0] else None
        stats["date_range_latest"] = date_range[1] if date_range[1] else None

        return stats
    finally:
        await db.close()


async def detect_duplicates(date_from=None, date_to=None, entry_type=None) -> dict:
    """AI-powered duplicate detection using LLM in 3-week batches."""
    entries = await get_all_entries(
        entry_type=entry_type,
        date_from=date_from,
        date_to=date_to,
        limit=5000
    )

    if not entries:
        return {
            "groups": [],
            "total_entries_analyzed": 0,
            "batch_info": "No entries found for the specified filters."
        }

    all_groups = []
    batch_size = 50
    batch_count = 0

    for i in range(0, len(entries), batch_size):
        batch = entries[i:i + batch_size]
        batch_count += 1

        entries_text = "\n".join([
            f"- ID:{e['id']} | Type:{e['type']} | Date:{e.get('timestamp', 'N/A')[:10]} | "
            f"Activity: {e['activity'][:200]}" +
            (f" | Follow-up: {e['follow_up'][:100]}" if e.get('follow_up') else "")
            for e in batch
        ])

        system_prompt = """You are a database compaction assistant. Analyze these log entries and identify 
groups of entries that are duplicates or cover the same topic.

Consider entries as duplicates if they:
- Describe the same event or task with slightly different wording
- Are sequential updates on the same ongoing task
- Have overlapping content that could be consolidated

Return ONLY a valid JSON array of duplicate groups. Each group object must have:
- "entry_ids": array of entry IDs that are duplicates (minimum 2)
- "confidence": decimal between 0.0 and 1.0
- "reason": brief explanation of why these are duplicates

Only include groups with confidence >= 0.6.
If no duplicates are found, return an empty array: []

Do NOT include any text before or after the JSON array."""

        user_prompt = f"""Analyze these {len(batch)} entries for duplicates:

{entries_text}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response = await call_llm(messages)
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                groups_raw = json.loads(json_match.group())
                for idx, group in enumerate(groups_raw):
                    entry_ids = group.get("entry_ids", [])
                    valid_entries = [e for e in batch if e["id"] in entry_ids]
                    if len(valid_entries) >= 2:
                        all_groups.append({
                            "group_id": len(all_groups) + 1,
                            "confidence": group.get("confidence", 0.0),
                            "entry_ids": [e["id"] for e in valid_entries],
                            "entries": valid_entries,
                            "reason": group.get("reason", "Potential duplicates detected")
                        })
        except Exception:
            pass

    return {
        "groups": all_groups,
        "total_entries_analyzed": len(entries),
        "batch_info": f"Analyzed {len(entries)} entries in {batch_count} batches. Found {len(all_groups)} potential duplicate groups."
    }


async def merge_entries(primary_id: int, secondary_ids: list[int]) -> dict:
    """Merge multiple entries into one with LLM-generated summary."""
    backup_path = _create_backup()

    primary = await get_entry(primary_id)
    if not primary:
        raise ValueError(f"Primary entry {primary_id} not found")

    secondaries = []
    for sid in secondary_ids:
        entry = await get_entry(sid)
        if entry:
            secondaries.append(entry)

    all_entries = [primary] + secondaries

    entries_text = "\n\n".join([
        f"Entry #{e['id']} (Type: {e['type']}, Date: {e.get('timestamp', 'N/A')[:10]}):\n"
        f"Activity: {e['activity']}\n"
        + (f"Follow-up: {e['follow_up']}\n" if e.get('follow_up') else "")
        + (f"Status: {e['status']}\n" if e.get('status') else "")
        + (f"ETA: {e['eta']}\n" if e.get('eta') else "")
        for e in all_entries
    ])

    system_prompt = """You are a database compaction assistant. Merge these entries into a single 
comprehensive entry. Combine the activity descriptions, preserve all key details, 
and create a clear, consolidated summary.

Rules:
- Preserve all important information from all entries
- Remove redundancy and duplication
- Maintain chronological context if present
- Keep technical details accurate
- Write in a clear, professional style
- Do NOT include entry IDs, dates, or metadata in the output
- Return ONLY the merged activity text"""

    user_prompt = f"""Merge these {len(all_entries)} entries into one:

{entries_text}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        merged_activity = await call_llm(messages)
    except Exception:
        activities = [e['activity'] for e in all_entries]
        merged_activity = "\n\n".join(activities)

    combined_follow_ups = []
    for e in all_entries:
        if e.get('follow_up') and e['follow_up'] not in combined_follow_ups:
            combined_follow_ups.append(e['follow_up'])
    merged_follow_up = "\n\n".join(combined_follow_ups) if combined_follow_ups else None

    all_tag_ids = set()
    for e in all_entries:
        for tag in e.get('tags', []):
            all_tag_ids.add(tag['id'])

    await update_entry(primary_id, {
        "activity": merged_activity,
        "follow_up": merged_follow_up,
        "tags": list(all_tag_ids)
    })

    deleted_ids = []
    for sid in secondary_ids:
        success = await delete_entry(sid)
        if success:
            deleted_ids.append(sid)

    merged_entry = await get_entry(primary_id)

    return {
        "merged_entry": merged_entry,
        "deleted_ids": deleted_ids,
        "backup_path": backup_path
    }
