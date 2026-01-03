from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .deps import get_tma_user
from app.db.repos_users import upsert_user, get_role
from app.db.repos_orders import create_order, list_orders_for_role

router = APIRouter(prefix="/api")


class RegisterIn(BaseModel):
    role: str
    phone: str | None = None


@router.get("/me")
async def me(ctx=Depends(get_tma_user)):
    role = await get_role(ctx["tg_id"])
    return {"tg_id": ctx["tg_id"], "role": role, "user": ctx["user"]}


@router.post("/auth/register")
async def register(data: RegisterIn, ctx=Depends(get_tma_user)):
    await upsert_user(ctx["tg_id"], phone=data.phone, role=data.role)
    return {"ok": True}


class OrderCreateIn(BaseModel):
    from_address: str
    shop_contact: str
    to_address: str
    to_apt: str | None = ""
    client_name: str | None = ""
    client_phone: str | None = ""
    price: float


@router.get("/orders")
async def orders(ctx=Depends(get_tma_user)):
    role = await get_role(ctx["tg_id"])
    if not role:
        return {"items": []}
    items = await list_orders_for_role(ctx["tg_id"], role)
    return {"items": items}


@router.post("/orders")
async def create(data: OrderCreateIn, ctx=Depends(get_tma_user)):
    role = await get_role(ctx["tg_id"])
    if role != "shop":
        return {"ok": False, "error": "Только магазин может создавать заказы"}

    oid = await create_order({
        "shop_tg_id": ctx["tg_id"],
        "from_address": data.from_address,
        "shop_contact": data.shop_contact,
        "to_address": data.to_address,
        "to_apt": data.to_apt or "",
        "client_name": data.client_name or "",
        "client_phone": data.client_phone or "",
        "price": data.price,
    })
    return {"ok": True, "order_id": oid}