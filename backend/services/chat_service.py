"""
Chat service - manages conversations, LLM calls, and markdown persistence.
"""
import json
import os
import re
import uuid
from datetime import datetime
from backend.services.llm_service import call_llm
from backend.services.bm25_search import search_entries
from backend.services.config import load_config
from backend.services.entries import get_entry


def _get_conversations_dir() -> str:
    config = load_config()
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base, config["app"].get("data_dir", "./data"))
    conv_dir = os.path.join(data_dir, "conversations")
    os.makedirs(conv_dir, exist_ok=True)
    return conv_dir


def _conversation_path(conversation_id: str) -> str:
    return os.path.join(_get_conversations_dir(), f"{conversation_id}.md")


def _generate_title(user_message: str) -> str:
    title = user_message.strip()[:60]
    if len(user_message.strip()) > 60:
        title = title.rsplit(" ", 1)[0] + "..."
    return title


SYSTEM_PROMPT_WITH_RAG = """You are a helpful assistant for an instrumentation engineer working on a FLNG project.
You have access to relevant log entries from the engineer's database. Use them to provide accurate, contextual answers.
When referencing entries, mention their IDs (e.g., [Entry #12]).
Be concise and technical. Format responses in markdown when appropriate."""

SYSTEM_PROMPT_NO_RAG = """You are a helpful assistant for an instrumentation engineer working on a FLNG project.
Be concise and technical. Format responses in markdown when appropriate."""


def _build_rag_context(rag_entries: list[dict]) -> str:
    if not rag_entries:
        return ""
    lines = ["The following log entries were retrieved from the database:\n"]
    for entry in rag_entries:
        parts = [f"[Entry #{entry['id']}]"]
        if entry.get("type"):
            parts.append(f"Type: {entry['type']}")
        if entry.get("status"):
            parts.append(f"Status: {entry['status']}")
        if entry.get("timestamp"):
            parts.append(f"Date: {entry['timestamp'][:10]}")
        lines.append(" | ".join(parts))
        lines.append(f"  {entry.get('activity', '')}")
        if entry.get("follow_up"):
            lines.append(f"  Follow-up: {entry['follow_up']}")
        lines.append("")
    return "\n".join(lines)


def _build_messages(
    history: list[dict],
    user_message: str,
    rag_entries: list[dict] | None = None,
) -> list[dict]:
    system_prompt = SYSTEM_PROMPT_WITH_RAG if rag_entries else SYSTEM_PROMPT_NO_RAG

    messages = [{"role": "system", "content": system_prompt}]

    if rag_entries:
        rag_context = _build_rag_context(rag_entries)
        messages.append({"role": "system", "content": f"Context from database:\n\n{rag_context}"})

    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": user_message})
    return messages


def _format_markdown(
    title: str,
    history: list[dict],
    rag_used: bool,
    entry_ids: list[int] | None,
) -> str:
    lines = [
        f"# Chat: {title}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**RAG Used:** {'Yes' if rag_used else 'No'}",
    ]
    if rag_used and entry_ids:
        lines.append(f"**References:** Entries #{', #'.join(str(i) for i in entry_ids)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for turn in history:
        role_label = "User" if turn["role"] == "user" else "Assistant"
        lines.append(f"## {role_label}")
        lines.append("")
        lines.append(turn["content"])
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def _parse_conversation(filepath: str) -> dict | None:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (FileNotFoundError, IOError):
        return None

    filename = os.path.basename(filepath)
    conversation_id = filename.replace(".md", "")

    title = ""
    rag_used = False
    entry_ids = []
    created_at = ""
    history = []

    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("# Chat: "):
            title = line[8:].strip()
        elif line.startswith("**Date:**"):
            created_at = line.split(":", 1)[1].strip().strip("*")
        elif line.startswith("**RAG Used:**"):
            rag_used = "Yes" in line
        elif line.startswith("**References:**"):
            id_str = line.split(":", 1)[1].strip()
            id_str = id_str.replace("Entries #", "").replace("#", "")
            entry_ids = [int(x.strip()) for x in id_str.split(",") if x.strip().isdigit()]

        i += 1

    pattern = re.compile(r'^## (User|Assistant)\n\n(.*?)(?=\n---|\Z)', re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(content):
        role = "user" if match.group(1) == "User" else "assistant"
        history.append({"role": role, "content": match.group(2).strip()})

    return {
        "id": conversation_id,
        "title": title,
        "rag_used": rag_used,
        "entry_ids": entry_ids,
        "created_at": created_at,
        "history": history,
    }


async def send_message(
    conversation_id: str | None,
    user_message: str,
    rag_entry_ids: list[int] | None = None,
) -> dict:
    config = load_config()
    history = []

    if conversation_id:
        filepath = _conversation_path(conversation_id)
        parsed = _parse_conversation(filepath)
        if parsed:
            history = parsed["history"]
            title = parsed["title"]
            if parsed["entry_ids"] and not rag_entry_ids:
                rag_entry_ids = parsed["entry_ids"]
        else:
            conversation_id = None

    if not conversation_id:
        conversation_id = str(uuid.uuid4())[:8]
        title = _generate_title(user_message)

    rag_entries = []
    if rag_entry_ids:
        for eid in rag_entry_ids:
            entry = await get_entry(eid)
            if entry:
                rag_entries.append(entry)

    messages = _build_messages(history, user_message, rag_entries if rag_entries else None)
    assistant_response = await call_llm(messages)

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": assistant_response})

    rag_used = len(rag_entries) > 0
    md_content = _format_markdown(title, history, rag_used, rag_entry_ids)

    filepath = _conversation_path(conversation_id)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    return {
        "conversation_id": conversation_id,
        "assistant_message": assistant_response,
        "rag_entries": [
            {"id": e["id"], "activity": e["activity"], "type": e["type"], "status": e.get("status"), "timestamp": e.get("timestamp")}
            for e in rag_entries
        ],
    }


def list_conversations() -> list[dict]:
    conv_dir = _get_conversations_dir()
    conversations = []
    for filename in os.listdir(conv_dir):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(conv_dir, filename)
        parsed = _parse_conversation(filepath)
        if parsed:
            conversations.append({
                "id": parsed["id"],
                "title": parsed["title"],
                "rag_used": parsed["rag_used"],
                "created_at": parsed["created_at"],
                "message_count": len(parsed["history"]),
            })
    conversations.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    return conversations


def get_conversation(conversation_id: str) -> dict | None:
    filepath = _conversation_path(conversation_id)
    return _parse_conversation(filepath)


def delete_conversation(conversation_id: str) -> bool:
    filepath = _conversation_path(conversation_id)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


async def search_entries_by_date(date_from: str, date_to: str, limit: int = 50) -> list[dict]:
    """Search entries by date range, sorted by timestamp DESC."""
    from backend.services.entries import get_all_entries
    entries = await get_all_entries(date_from=date_from, date_to=date_to, limit=limit)
    return [
        {
            "id": e["id"],
            "activity": e["activity"],
            "type": e["type"],
            "status": e.get("status"),
            "timestamp": e.get("timestamp"),
            "follow_up": e.get("follow_up"),
            "score": None
        }
        for e in entries
    ]
