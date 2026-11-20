# Telegram capture — setup (10 minutes)

**What it does:** you send a line (or a whiteboard photo) to a Telegram bot; the app on the laptop picks it up and puts it in the **Inbox**; at 16:30 you triage the Inbox into LOG/TODO/TASK with an owner and a date.

Telegram **web** is fine — the bot is independent of the client. Web, desktop app or phone all reach the same bot.

---

## 1. Create the bot

1. In Telegram, search **@BotFather** → open it → `/newbot`.
2. Give it a name (e.g. `Fabio Notes`) and a username ending in `bot` (e.g. `fabio_notes_bot`).
3. BotFather replies with a token like `8123456789:AAH...`. That token is a password — keep it out of screenshots.

## 2. Open a chat with your bot and send one message

Click the bot link BotFather gives you, press **Start**, send `hello`.

Nothing arrives in the app yet — this step just exists so the bot has a chat with you.

## 3. Tell the app the token

In the app: **Settings → Telegram Capture**

- Tick **Enable Telegram inbox polling**
- Paste the **Bot token**
- Leave **Allowed chat IDs** empty for the first run
- **Save Settings**, then restart the app (`run-dev.bat` / the exe)

## 4. Lock it to your chat

Send `⇒ test: ignore me` to the bot. Then check the app log `personallog.log` for a line like:

```
Telegram: inbox +1 (text, chat 845123456)
```

That number is your chat id. Put it in **Allowed chat IDs**, save, restart. From now on any other chat is ignored.

(Alternative: message **@userinfobot** and it replies with your id.)

## 5. Test the grammar

Send these four lines, one message each:

```
• FIR room walkdown done 18.11, punch count started
⇒ Yernar: finish ICSS OWS datav upgrade by 21.11
? 970-NP-02 SIS/TR promised 19:00, not confirmed
@Buly asked for 2 more techs; answer by Thu
```

Open **Inbox** in the app. Each item shows up with a suggested type: `⇒` becomes TASK with the name as owner, `?` becomes TODO waiting, `•` becomes LOG. Adjust anything, then **Convert**.

## 6. Photos

Send the whiteboard photo **with a caption** — the caption becomes the line, the photo is stored in `data/inbox/YYYY-MM/`. In the Inbox you see the thumbnail next to the text.

---

## Using it during the day

- One line, one thing. No tidying on the phone.
- Do not delete the message after sending: the bot chat is your capture history.
- If the laptop is asleep, messages wait and land when it wakes. Telegram holds undelivered updates for about **24 hours** — a weekend offline is fine, a two-week leave is not (write the handover by hand).

## Troubleshooting

| Symptom | Cause |
|---|---|
| Nothing in Inbox | `enabled` off, token wrong, or app not restarted after saving |
| Log says `invalid bot token (401)` | token copied with a space, or the bot was deleted |
| Messages from a second chat ignored | `allowed_chat_ids` is set and does not include it |
| Inbox shows the item, photo missing | file was cleaned from `data/inbox/` |
| Works in web but not phone | phone has no data/roaming; it is still Telegram's problem, not the app's |

Log file: `C:\myAI\fabio-notes\better_noteTaking\personallog.log`.

## Confidentiality

Text and photos transit Telegram's cloud. Whiteboard photos of tag numbers and status are low risk but still leave the ship. If that is not acceptable for a given item, keep it on paper — the method works without Telegram; you just lose the 5-second capture.

## If you ever change laptop or reinstall

The token stays valid. Re-enter it in Settings. The `telegram_offset` in the DB means old messages are not re-imported.
