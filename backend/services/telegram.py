"""
Telegram -> inbox poller.

Uses long polling (getUpdates) so no public URL or port forwarding is needed:
the desktop app is the only thing that talks to Telegram.
"""
import asyncio
import datetime
import logging
import os

import httpx

from backend.database import get_data_dir, get_db
from backend.services.config import load_config

logger = logging.getLogger("personallog.telegram")

API_ROOT = "https://api.telegram.org"

_poller_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None


async def _get_meta(key: str, default: str | None = None) -> str | None:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT value FROM meta WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else default
    finally:
        await db.close()


async def _set_meta(key: str, value: str):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value)
        )
        await db.commit()
    finally:
        await db.close()


async def get_me(token: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"{API_ROOT}/bot{token}/getMe")
        response.raise_for_status()
        return response.json().get("result", {})


async def _download_photo(client: httpx.AsyncClient, token: str, file_id: str, message_id: int) -> str:
    response = await client.get(f"{API_ROOT}/bot{token}/getFile", params={"file_id": file_id})
    response.raise_for_status()
    remote_path = response.json()["result"]["file_path"]
    ext = os.path.splitext(remote_path)[1] or ".jpg"

    relative = f"inbox/{datetime.datetime.now().strftime('%Y-%m')}/{message_id}{ext}"
    destination = get_data_dir() / relative
    destination.parent.mkdir(parents=True, exist_ok=True)

    download = await client.get(f"{API_ROOT}/file/bot{token}/{remote_path}")
    download.raise_for_status()
    destination.write_bytes(download.content)
    return relative.replace("\\", "/")


async def _handle_update(client: httpx.AsyncClient, token: str, update: dict, allowed: list):
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = str(message.get("chat", {}).get("id", ""))
    if allowed and chat_id not in {str(item) for item in allowed}:
        logger.info("Telegram: ignoring chat %s (not in allowed_chat_ids)", chat_id)
        return

    text = (message.get("text") or message.get("caption") or "").strip()
    if text.startswith("/"):
        return

    kind = "text"
    file_path = None
    photos = message.get("photo") or []
    if photos:
        kind = "photo"
        file_path = await _download_photo(client, token, photos[-1]["file_id"], message.get("message_id"))

    if not text and not file_path:
        return

    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO inbox (received_at, source, kind, body, file_path, chat_id, message_id, processed)
               VALUES (?, 'telegram', ?, ?, ?, ?, ?, 0)""",
            (datetime.datetime.now().isoformat(), kind, text or None, file_path, chat_id, message.get("message_id"))
        )
        await db.commit()
    finally:
        await db.close()

    logger.info("Telegram: inbox +1 (%s, chat %s)", kind, chat_id)


async def _run():
    config = load_config().get("telegram", {}) or {}
    token = (config.get("bot_token") or "").strip()
    if not token:
        logger.info("Telegram polling: no bot_token configured")
        return

    allowed = config.get("allowed_chat_ids") or []
    poll_timeout = int(config.get("poll_timeout") or 25)
    offset = int(await _get_meta("telegram_offset", "0") or 0)

    logger.info("Telegram polling started (timeout %ss)", poll_timeout)

    async with httpx.AsyncClient(timeout=poll_timeout + 20) as client:
        while not _stop_event.is_set():
            try:
                response = await client.get(
                    f"{API_ROOT}/bot{token}/getUpdates",
                    params={
                        "offset": offset + 1,
                        "timeout": poll_timeout,
                        "allowed_updates": '["message"]',
                    }
                )
                if response.status_code == 401:
                    logger.warning("Telegram: invalid bot token (401) - polling stopped")
                    return
                if response.status_code != 200:
                    logger.warning("Telegram: getUpdates HTTP %s", response.status_code)
                    await asyncio.sleep(10)
                    continue

                updates = response.json().get("result", [])
                for update in updates:
                    try:
                        await _handle_update(client, token, update, allowed)
                    except Exception:
                        logger.exception("Telegram: failed to handle update %s", update.get("update_id"))
                    offset = max(offset, int(update.get("update_id", 0)))
                    await _set_meta("telegram_offset", str(offset))

            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("Telegram poll error: %s", exc)
                await asyncio.sleep(5)


async def start_poller():
    global _poller_task, _stop_event
    config = load_config().get("telegram", {}) or {}
    if not config.get("enabled"):
        logger.info("Telegram polling disabled in config")
        return None
    if not (config.get("bot_token") or "").strip():
        logger.info("Telegram enabled but no token yet")
        return None

    _stop_event = asyncio.Event()
    _poller_task = asyncio.create_task(_run())
    return _poller_task


async def stop_poller():
    global _poller_task
    if _stop_event:
        _stop_event.set()
    if _poller_task:
        _poller_task.cancel()
        try:
            await _poller_task
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.debug("Telegram poller stopped with: %s", exc)
        _poller_task = None
