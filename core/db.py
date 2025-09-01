import asyncpg
import contextlib
from typing import AsyncIterator, Optional

from core.config import CONFIG

# --- Lifecycle --------------------------------------------------------------

async def create_pool(min_size: int = 1, max_size: int = 5) -> asyncpg.Pool:
    """
    Create and return a global asyncpg pool.
    Uses CONFIG.database_url.
    """
    pool = await asyncpg.create_pool(
        dsn=CONFIG.database_url,
        min_size=min_size,
        max_size=max_size,
    )
    print("[db] connection pool created")
    return pool

async def close_pool(pool: Optional[asyncpg.Pool]) -> None:
    if pool is not None:
        await pool.close()
        print("[db] connection pool closed")

def attach_pool(bot, pool: asyncpg.Pool) -> None:
    """
    Convenience: attach the pool to your bot instance as `bot.db`.
    """
    bot.db = pool

# --- Convenience API --------------------------------------------------------

@contextlib.asynccontextmanager
async def acquire(pool: asyncpg.Pool) -> AsyncIterator[asyncpg.Connection]:
    """
    Async context manager:
        async with acquire(pool) as conn:
            await conn.execute("...")
    """
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)

async def fetchrow(pool: asyncpg.Pool, query: str, *args):
    async with acquire(pool) as conn:
        return await conn.fetchrow(query, *args)

async def fetch(pool: asyncpg.Pool, query: str, *args):
    async with acquire(pool) as conn:
        return await conn.fetch(query, *args)

async def execute(pool: asyncpg.Pool, query: str, *args):
    async with acquire(pool) as conn:
        return await conn.execute(query, *args)
