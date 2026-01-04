import time
from typing import Optional
from .db import pool

PAYMENT_STATUS_UNPAID = 0
PAYMENT_STATUS_MARKED_PAID = 1
PAYMENT_STATUS_CONFIRMED = 2


async def create_order(data: dict) -> int:
    created_at = str(int(time.time()))
    log_text = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Заказ создан."
    initial_status = "taken" if data.get("return_for") else "new"

    async with pool().acquire() as con:
        row = await con.fetchrow(
            """
            INSERT INTO orders(
              shop_tg_id, courier_tg_id,
              from_address, shop_contact,
              to_address, to_apt, client_name, client_phone,
              price, status, log, created_at, return_for, paid_to_courier, paid_at
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,NULL)
            RETURNING id;
            """,
            int(data["shop_tg_id"]),
            int(data.get("courier_tg_id") or 0) or None,
            data["from_address"],
            data["shop_contact"],
            data["to_address"],
            data.get("to_apt", ""),
            data.get("client_name", ""),
            data.get("client_phone", ""),
            float(data["price"]),
            initial_status,
            log_text,
            created_at,
            data.get("return_for"),
            PAYMENT_STATUS_UNPAID,
        )
        return int(row["id"])


async def get_order(order_id: int) -> Optional[dict]:
    async with pool().acquire() as con:
        row = await con.fetchrow("SELECT * FROM orders WHERE id=$1", order_id)
        return dict(row) if row else None


async def list_orders_for_role(tg_id: int, role: str, statuses: list[str] | None = None) -> list[dict]:
    statuses = statuses or []
    async with pool().acquire() as con:
        if statuses:
            if role == "courier":
                rows = await con.fetch(
                    "SELECT * FROM orders WHERE courier_tg_id=$1 AND status = ANY($2::text[]) ORDER BY created_at DESC",
                    tg_id, statuses
                )
            else:
                rows = await con.fetch(
                    "SELECT * FROM orders WHERE shop_tg_id=$1 AND status = ANY($2::text[]) ORDER BY created_at DESC",
                    tg_id, statuses
                )
        else:
            if role == "courier":
                rows = await con.fetch("SELECT * FROM orders WHERE courier_tg_id=$1 ORDER BY created_at DESC", tg_id)
            else:
                rows = await con.fetch("SELECT * FROM orders WHERE shop_tg_id=$1 ORDER BY created_at DESC", tg_id)
    return [dict(r) for r in rows]


async def update_order(
    order_id: int,
    *,
    status: str | None = None,
    courier_tg_id: int | None = None,
    paid_to_courier: int | None = None,
    log_add: str | None = None
):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    parts = []
    vals = []
    i = 1

    if status is not None:
        parts.append(f"status=${i}"); vals.append(status); i += 1
    if courier_tg_id is not None:
        parts.append(f"courier_tg_id=${i}"); vals.append(courier_tg_id if courier_tg_id != 0 else None); i += 1
    if paid_to_courier is not None:
        parts.append(f"paid_to_courier=${i}"); vals.append(paid_to_courier); i += 1
        if paid_to_courier == PAYMENT_STATUS_CONFIRMED:
            parts.append(f"paid_at=${i}"); vals.append(ts); i += 1
        elif paid_to_courier == PAYMENT_STATUS_UNPAID:
            parts.append("paid_at=NULL")

    if log_add:
    parts.append(f"log = COALESCE(log,'') || ${i}")
    vals.append(f"[{ts}] {log_add}
")
    i += 1

    if not parts:
        return

    vals.append(order_id)
    q = f"UPDATE orders SET {', '.join(parts)} WHERE id=${i}"

    async with pool().acquire() as con:
        await con.execute(q, *vals)
