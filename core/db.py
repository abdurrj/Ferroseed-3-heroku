import asyncpg, contextlib
from typing import AsyncIterator, Optional
from core.config import CONFIG

async def create_pool(min_size: int = 1, max_size: int = 5) -> asyncpg.Pool:
    pool = await asyncpg.create_pool(dsn=CONFIG.database_url, min_size=min_size, max_size=max_size)
    print("[db] connection pool created")
    return pool

async def close_pool(pool: Optional[asyncpg.Pool]) -> None:
    if pool is not None:
        await pool.close()
        print("[db] connection pool closed")

def attach_pool(bot, pool: asyncpg.Pool) -> None:
    bot.db = pool
