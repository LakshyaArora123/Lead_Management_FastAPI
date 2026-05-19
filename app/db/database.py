import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "leads.db"

CREATE_LEADS_TABLE = """
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    company TEXT,
    phone TEXT,
    source TEXT,
    status TEXT NOT NULL DEFAULT 'new'
                CHECK(status IN ('new', 'contacted', 'qualified', 'lost', 'converted')),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
"""

CREATE_UPDATED_AT_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS leads_updated_at
    AFTER UPDATE ON leads
    FOR EACH ROW
    BEGIN
        UPDATE leads
        SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
        WHERE id = OLD.id;
    END;
"""

async def get_db() -> aiosqlite.Connection:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA foreign_keys=ON;")
        yield db

async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_LEADS_TABLE)
        await db.execute(CREATE_UPDATED_AT_TRIGGER)
        await db.commit()