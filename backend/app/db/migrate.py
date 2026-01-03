from .db import pool
from .schema import SCHEMA_SQL


async def migrate():
    async with pool().acquire() as con:
        await con.execute(SCHEMA_SQL)