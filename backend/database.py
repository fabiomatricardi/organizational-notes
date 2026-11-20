"""
SQLite database connection & schema management.
"""
import aiosqlite
import os
import sys
from pathlib import Path

DATABASE_PATH = None

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS log_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activity TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('LOG', 'TODO', 'TASK')),
    follow_up TEXT,
    status TEXT NOT NULL DEFAULT 'LOG',
    reference_id INTEGER,
    eta DATETIME,
    owner TEXT,
    next_check DATE,
    area TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reference_id) REFERENCES log_entries(id)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT DEFAULT '#3b82f6'
);

CREATE TABLE IF NOT EXISTS entry_tags (
    entry_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (entry_id, tag_id),
    FOREIGN KEY (entry_id) REFERENCES log_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    period_start DATE,
    period_end DATE,
    content TEXT NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL DEFAULT 'telegram',
    kind TEXT NOT NULL DEFAULT 'text',
    body TEXT,
    file_path TEXT,
    chat_id TEXT,
    message_id INTEGER,
    processed INTEGER NOT NULL DEFAULT 0,
    entry_id INTEGER
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_log_entries_type ON log_entries(type);
CREATE INDEX IF NOT EXISTS idx_log_entries_status ON log_entries(status);
CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_log_entries_reference_id ON log_entries(reference_id);
CREATE INDEX IF NOT EXISTS idx_inbox_processed ON inbox(processed);
"""

# Columns added after the first release. Applied to existing databases on startup.
MIGRATIONS = [
    ("log_entries", "owner", "TEXT"),
    ("log_entries", "next_check", "DATE"),
    ("log_entries", "area", "TEXT"),
]


def _get_app_base_dir() -> Path:
    """Get the app base directory (next to executable or project root)."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable - use exe directory
        return Path(os.path.dirname(sys.executable))
    else:
        # Running in development - use project root (parent of backend/)
        return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """Directory that holds the database, inbox attachments and conversations."""
    data_dir = _get_app_base_dir() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_db_path() -> str:
    global DATABASE_PATH
    if DATABASE_PATH:
        return DATABASE_PATH

    DATABASE_PATH = str(get_data_dir() / "personal_log.db")
    return DATABASE_PATH


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(get_db_path())
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def _ensure_column(db: aiosqlite.Connection, table: str, column: str, decl: str):
    cursor = await db.execute(f"PRAGMA table_info({table})")
    existing = [row[1] for row in await cursor.fetchall()]
    if column not in existing:
        await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")


async def init_db():
    db = await get_db()
    try:
        await db.executescript(SCHEMA_SQL)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            rag_used INTEGER DEFAULT 0,
            entry_ids TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
        for table, column, decl in MIGRATIONS:
            await _ensure_column(db, table, column, decl)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_log_entries_owner ON log_entries(owner)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_log_entries_next_check ON log_entries(next_check)")
        await db.commit()
    finally:
        await db.close()


async def close_db(db: aiosqlite.Connection):
    await db.close()
