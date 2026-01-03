from typing import Optional
from .db import pool


async def upsert_user(tg_id: int, phone: str | None = None, role: str | None = None):
    async with pool().acquire() as con:
        await con.execute(
            """
            INSERT INTO users (tg_id, phone, role)
            VALUES ($1, $2, $3)
            ON CONFLICT (tg_id) DO UPDATE
              SET phone = COALESCE(EXCLUDED.phone, users.phone),
                  role  = COALESCE(EXCLUDED.role,  users.role);
            """,
            tg_id, phone, role,
        )


async def set_role(tg_id: int, role: Optional[str]):
    async with pool().acquire() as con:
        await con.execute(
            """
            INSERT INTO users (tg_id, role)
            VALUES ($1, $2)
            ON CONFLICT (tg_id) DO UPDATE SET role = EXCLUDED.role;
            """,
            tg_id, role,
        )


async def get_role(tg_id: int) -> Optional[str]:
    async with pool().acquire() as con:
        row = await con.fetchrow("SELECT role FROM users WHERE tg_id=$1", tg_id)
        return row["role"] if row else None


async def save_phone(tg_id: int, phone: str):
    await upsert_user(tg_id, phone=phone)


async def check_phone_exists(tg_id: int) -> bool:
    async with pool().acquire() as con:
        row = await con.fetchrow("SELECT phone FROM users WHERE tg_id=$1", tg_id)
        return bool(row and row["phone"])


async def is_blocked(tg_id: int) -> bool:
    async with pool().acquire() as con:
        row = await con.fetchrow("SELECT is_blocked FROM users WHERE tg_id=$1", tg_id)
        return bool(row and int(row["is_blocked"]) == 1)


async def get_couriers() -> list[int]:
    async with pool().acquire() as con:
        rows = await con.fetch("SELECT tg_id FROM users WHERE role='courier'")
        return [int(r["tg_id"]) for r in rows]