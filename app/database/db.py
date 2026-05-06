import aiosqlite
import asyncio
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    _db_path: Optional[str] = None
    _conn: Optional[aiosqlite.Connection] = None
    _lock = asyncio.Lock()

    @classmethod
    async def init(cls, db_path: str):
        cls._db_path = db_path
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        cls._conn = await aiosqlite.connect(db_path)
        await cls._conn.execute('PRAGMA foreign_keys = ON')
        await cls._create_tables()
        await cls._conn.commit()
        logger.info('Database initialized at %s', db_path)

    @classmethod
    async def _create_tables(cls):
        await cls._conn.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            regex_mode INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        await cls._conn.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY,
            title TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        await cls._conn.execute('CREATE INDEX IF NOT EXISTS idx_keywords_group ON keywords(group_id)')
        await cls._conn.execute('CREATE INDEX IF NOT EXISTS idx_keywords_user ON keywords(user_id)')
        await cls._conn.execute('CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword)')
        await cls._conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_keyword ON keywords(group_id, user_id, keyword)')

    @classmethod
    def get_conn(cls) -> aiosqlite.Connection:
        if cls._conn is None:
            raise RuntimeError('Database not initialized')
        return cls._conn
