from typing import List, Tuple, Optional
from .db import Database
import aiosqlite
import logging

logger = logging.getLogger(__name__)


async def add_keywords(group_id: int, user_id: int, keywords: List[Tuple[str, int]]) -> int:
    """Add keywords. keywords: list of (keyword, regex_mode)"""
    conn = Database.get_conn()
    count = 0
    for kw, regex_mode in keywords:
        try:
            cur = await conn.execute('SELECT 1 FROM keywords WHERE group_id = ? AND user_id = ? AND keyword = ?', (group_id, user_id, kw))
            exists = await cur.fetchone()
            if exists:
                continue
            await conn.execute(
                'INSERT INTO keywords (group_id, user_id, keyword, regex_mode) VALUES (?, ?, ?, ?)',
                (group_id, user_id, kw, int(bool(regex_mode)))
            )
            count += 1
        except aiosqlite.Error as e:
            logger.exception('DB error adding keyword %s: %s', kw, e)
    await conn.commit()
    return count


async def remove_keyword(group_id: int, user_id: int, keyword: str) -> int:
    conn = Database.get_conn()
    cur = await conn.execute('DELETE FROM keywords WHERE group_id = ? AND user_id = ? AND keyword = ?', (group_id, user_id, keyword))
    await conn.commit()
    return cur.rowcount


async def clear_keywords(group_id: int, user_id: int) -> int:
    conn = Database.get_conn()
    cur = await conn.execute('DELETE FROM keywords WHERE group_id = ? AND user_id = ?', (group_id, user_id))
    await conn.commit()
    return cur.rowcount


async def list_keywords_for_user(user_id: int) -> List[aiosqlite.Row]:
    conn = Database.get_conn()
    cur = await conn.execute('SELECT group_id, keyword, regex_mode, created_at FROM keywords WHERE user_id = ? ORDER BY group_id', (user_id,))
    rows = await cur.fetchall()
    return rows


async def get_group_title(group_id: int) -> Optional[str]:
    conn = Database.get_conn()
    cur = await conn.execute('SELECT title FROM groups WHERE group_id = ?', (group_id,))
    row = await cur.fetchone()
    return row[0] if row else None


async def get_keywords_for_group(group_id: int):
    conn = Database.get_conn()
    cur = await conn.execute('SELECT user_id, keyword, regex_mode FROM keywords WHERE group_id = ?', (group_id,))
    rows = await cur.fetchall()
    return rows


async def upsert_group(group_id: int, title: str):
    conn = Database.get_conn()
    await conn.execute('INSERT INTO groups (group_id, title) VALUES (?, ?) ON CONFLICT(group_id) DO UPDATE SET title = excluded.title, updated_at = CURRENT_TIMESTAMP', (group_id, title))
    await conn.commit()


async def find_group_by_title(title: str):
    """Find a group by its title, case-insensitive. Returns (group_id, title) or None."""
    conn = Database.get_conn()
    # Primary: exact match (case-insensitive)
    cur = await conn.execute('SELECT group_id, title FROM groups WHERE LOWER(title) = LOWER(?)', (title,))
    row = await cur.fetchone()
    if row:
        return row
    # Fallback: try partial match (safe, case-insensitive)
    try:
        cur2 = await conn.execute('SELECT group_id, title FROM groups WHERE title LIKE ?', ('%' + title + '%',))
        row2 = await cur2.fetchone()
        return row2
    except Exception:
        return None
