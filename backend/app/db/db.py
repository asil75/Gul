import asyncpg

_pool: asyncpg.Pool | None = None


async def init_pool(dsn: str):
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn)


async def close_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized")
    return _pool