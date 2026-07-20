"""邻里小店 FastAPI：商品 / 购物车 / 订单 / 模拟支付 / 简易后台。"""
import os
import secrets
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import models
from .db import Base, SessionLocal, engine, get_db
from .seed import seed_if_empty

load_dotenv()

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-admin")
SESSION_COOKIE = "shop_sid"

app = FastAPI(title="邻里小店")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


def _session_id(request: Request) -> str:
    sid = request.cookies.get(SESSION_COOKIE) or request.headers.get("X-Session-Id")
    if not sid:
        sid = secrets.token_hex(16)
    request.state.sid = sid
    return sid


def _set_session_cookie(response, sid: str):
    response.set_cookie(
        SESSION_COOKIE,
        sid,
        httponly=True,
        samesite="lax",
        max_age=86400 * 30,
        path="/",
    )


class CartAdd(BaseModel):
    product_id: int
    qty: int = Field(ge=1, le=99)


class CartQty(BaseModel):
    qty: int = Field(ge=0, le=99)


class CreateOrder(BaseModel):
    pickup_point_id: int
    buyer_name: str = Field(min_length=1, max_length=64)
    buyer_phone: str = Field(min_length=5, max_length=32)


class StatusBody(BaseModel):
    status: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    rows = db.query(models.Product).filter(models.Product.on_sale == 1).all()
    return [_public_product(p) for p in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.get(models.Product, product_id)
    if not p or not p.on_sale:
        raise HTTPException(404, "商品不存在")
    return _public_product(p)


def _public_product(p: models.Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "desc": p.desc,
        "price_cents": p.price_cents,
        "stock": p.stock,
        "cover_url": p.cover_url or "",
    }


@app.get("/api/pickup-points")
def list_pickups(db: Session = Depends(get_db)):
    rows = db.query(models.PickupPoint).order_by(models.PickupPoint.id).all()
    return [{"id": p.id, "name": p.name, "address": p.address} for p in rows]

@app.get("/api/cart")
def get_cart(request: Request, db: Session = Depends(get_db)):
    sid = _session_id(request)
    items = (
        db.query(models.CartItem)
        .filter(models.CartItem.session_id == sid)
        .all()
    )
    out = []
    total = 0
    for it in items:
        p = it.product
        line = p.price_cents * it.qty
        total += line
        out.append(
            {
                "id": it.id,
                "product_id": p.id,
                "name": p.name,
                "price_cents": p.price_cents,
                "qty": it.qty,
                "line_cents": line,
                "cover_url": p.cover_url or "",
            }
        )
    from fastapi.responses import JSONResponse

    resp = JSONResponse({"items": out, "total_cents": total})
    _set_session_cookie(resp, sid)
    return resp


@app.post("/api/cart/items")
def add_cart(body: CartAdd, request: Request, db: Session = Depends(get_db)):
    sid = _session_id(request)
    product = db.get(models.Product, body.product_id)
    if not product or not product.on_sale:
        raise HTTPException(404, "商品不存在")
    item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.session_id == sid,
            models.CartItem.product_id == body.product_id,
        )
        .first()
    )
    if item:
        item.qty += body.qty
    else:
        item = models.CartItem(session_id=sid, product_id=body.product_id, qty=body.qty)
        db.add(item)
    db.commit()
    from fastapi.responses import JSONResponse

    resp = JSONResponse({"ok": True})
    _set_session_cookie(resp, sid)
    return resp


@app.patch("/api/cart/items/{item_id}")
def update_cart_item(item_id: int, body: CartQty, request: Request, db: Session = Depends(get_db)):
    sid = _session_id(request)
    item = db.get(models.CartItem, item_id)
    if not item or item.session_id != sid:
        raise HTTPException(404, "购物车项不存在")
    if body.qty <= 0:
        db.delete(item)
    else:
        if item.product and body.qty > item.product.stock:
            raise HTTPException(400, f"{item.product.name} 库存不足")
        item.qty = body.qty
    db.commit()
    from fastapi.responses import JSONResponse

    resp = JSONResponse({"ok": True})
    _set_session_cookie(resp, sid)
    return resp


@app.delete("/api/cart/items/{item_id}")
def delete_cart_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    sid = _session_id(request)
    item = db.get(models.CartItem, item_id)
    if not item or item.session_id != sid:
        raise HTTPException(404, "购物车项不存在")
    db.delete(item)
    db.commit()
    from fastapi.responses import JSONResponse

    resp = JSONResponse({"ok": True})
    _set_session_cookie(resp, sid)
    return resp


def _order_dict(o: models.Order) -> dict:
    return {
        "id": o.id,
        "status": o.status,
        "total_cents": o.total_cents,
        "buyer_name": o.buyer_name,
        "buyer_phone": o.buyer_phone,
        "pickup_point_id": o.pickup_point_id,
        "pickup_point": {
            "id": o.pickup_point.id,
            "name": o.pickup_point.name,
            "address": o.pickup_point.address,
        }
        if o.pickup_point
        else None,
        "items": [
            {
                "product_id": i.product_id,
                "product_name": i.product_name,
                "price_cents": i.price_cents,
                "qty": i.qty,
            }
            for i in o.items
        ],
        "created_at": o.created_at.isoformat() + "Z",
    }


@app.get("/api/orders")
def list_my_orders(request: Request, db: Session = Depends(get_db)):
    sid = _session_id(request)
    rows = (
        db.query(models.Order)
        .filter(models.Order.session_id == sid)
        .order_by(models.Order.id.desc())
        .all()
    )
    from fastapi.responses import JSONResponse

    resp = JSONResponse([_order_dict(o) for o in rows])
    _set_session_cookie(resp, sid)
    return resp


@app.post("/api/orders/{order_id}/cancel")
def cancel_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    sid = _session_id(request)
    order = db.get(models.Order, order_id)
    if not order or order.session_id != sid:
        raise HTTPException(404, "订单不存在")
    if order.status != "pending_pay":
        raise HTTPException(400, f"当前状态不可取消: {order.status}")
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return _order_dict(order)


@app.post("/api/orders")
def create_order(body: CreateOrder, request: Request, db: Session = Depends(get_db)):
    sid = _session_id(request)
    pickup = db.get(models.PickupPoint, body.pickup_point_id)
    if not pickup:
        raise HTTPException(400, "自提点无效")
    cart_items = (
        db.query(models.CartItem).filter(models.CartItem.session_id == sid).all()
    )
    if not cart_items:
        raise HTTPException(400, "购物车为空")

    order = models.Order(
        session_id=sid,
        status="pending_pay",
        pickup_point_id=pickup.id,
        buyer_name=body.buyer_name.strip(),
        buyer_phone=body.buyer_phone.strip(),
    )
    total = 0
    for it in cart_items:
        p = it.product
        if p.stock < it.qty:
            raise HTTPException(400, f"{p.name} 库存不足")
        total += p.price_cents * it.qty
        order.items.append(
            models.OrderItem(
                product_id=p.id,
                product_name=p.name,
                price_cents=p.price_cents,
                qty=it.qty,
            )
        )
    order.total_cents = total
    db.add(order)
    for it in cart_items:
        db.delete(it)
    db.commit()
    db.refresh(order)
    from fastapi.responses import JSONResponse

    resp = JSONResponse(_order_dict(order))
    _set_session_cookie(resp, sid)
    return resp


@app.get("/api/orders/{order_id}")
def get_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    sid = _session_id(request)
    order = db.get(models.Order, order_id)
    if not order or order.session_id != sid:
        # admin can still use admin list; buyer only own session
        raise HTTPException(404, "订单不存在")
    return _order_dict(order)


@app.post("/api/orders/{order_id}/mock-pay")
def mock_pay(order_id: int, request: Request, db: Session = Depends(get_db)):
    """模拟支付：演示用。接单时可替换为微信支付。"""
    sid = _session_id(request)
    order = db.get(models.Order, order_id)
    if not order or order.session_id != sid:
        raise HTTPException(404, "订单不存在")
    if order.status != "pending_pay":
        raise HTTPException(400, f"当前状态不可支付: {order.status}")
    for it in order.items:
        product = db.get(models.Product, it.product_id)
        if product:
            if product.stock < it.qty:
                raise HTTPException(400, f"{product.name} 库存不足")
            product.stock -= it.qty
    order.status = "paid"
    db.commit()
    db.refresh(order)
    return _order_dict(order)


def _require_admin(token: Optional[str]) -> None:
    if token != ADMIN_TOKEN:
        raise HTTPException(401, "无效的管理员令牌")


@app.get("/api/admin/orders")
def admin_orders(
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    rows = db.query(models.Order).order_by(models.Order.id.desc()).all()
    return [_order_dict(o) for o in rows]


@app.get("/api/admin/products")
def admin_products(
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    rows = db.query(models.Product).order_by(models.Product.id).all()
    return [_product_dict(p) for p in rows]


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    price_cents: Optional[int] = None
    stock: Optional[int] = None
    on_sale: Optional[bool] = None
    cover_url: Optional[str] = None


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    desc: str = ""
    price_cents: int = Field(ge=1)
    stock: int = Field(default=100, ge=0)
    on_sale: bool = True
    cover_url: str = ""


def _product_dict(p: models.Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "desc": p.desc,
        "price_cents": p.price_cents,
        "stock": p.stock,
        "on_sale": bool(p.on_sale),
        "cover_url": p.cover_url,
    }


@app.post("/api/admin/products")
def admin_create_product(
    body: ProductCreate,
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    p = models.Product(
        name=body.name.strip(),
        desc=(body.desc or "").strip(),
        price_cents=body.price_cents,
        stock=body.stock,
        on_sale=1 if body.on_sale else 0,
        cover_url=(body.cover_url or "").strip(),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _product_dict(p)


@app.patch("/api/admin/products/{product_id}")
def admin_patch_product(
    product_id: int,
    body: ProductUpdate,
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    p = db.get(models.Product, product_id)
    if not p:
        raise HTTPException(404, "商品不存在")
    if body.name is not None:
        p.name = body.name
    if body.desc is not None:
        p.desc = body.desc
    if body.price_cents is not None:
        p.price_cents = body.price_cents
    if body.stock is not None:
        p.stock = body.stock
    if body.on_sale is not None:
        p.on_sale = 1 if body.on_sale else 0
    if body.cover_url is not None:
        p.cover_url = body.cover_url.strip()
    db.commit()
    return _product_dict(p)


@app.delete("/api/admin/products/{product_id}")
def admin_delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    p = db.get(models.Product, product_id)
    if not p:
        raise HTTPException(404, "商品不存在")
    db.query(models.CartItem).filter(models.CartItem.product_id == product_id).delete()
    db.delete(p)
    db.commit()
    return {"ok": True}


class PickupBody(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    address: str = Field(min_length=1, max_length=255)


@app.get("/api/admin/pickup-points")
def admin_pickups(
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    rows = db.query(models.PickupPoint).order_by(models.PickupPoint.id).all()
    return [{"id": p.id, "name": p.name, "address": p.address} for p in rows]


@app.post("/api/admin/pickup-points")
def admin_create_pickup(
    body: PickupBody,
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    p = models.PickupPoint(name=body.name.strip(), address=body.address.strip())
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "name": p.name, "address": p.address}


@app.patch("/api/admin/pickup-points/{point_id}")
def admin_patch_pickup(
    point_id: int,
    body: PickupBody,
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    p = db.get(models.PickupPoint, point_id)
    if not p:
        raise HTTPException(404, "自提点不存在")
    p.name = body.name.strip()
    p.address = body.address.strip()
    db.commit()
    return {"id": p.id, "name": p.name, "address": p.address}


@app.delete("/api/admin/pickup-points/{point_id}")
def admin_delete_pickup(
    point_id: int,
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    p = db.get(models.PickupPoint, point_id)
    if not p:
        raise HTTPException(404, "自提点不存在")
    used = db.query(models.Order).filter(models.Order.pickup_point_id == point_id).count()
    if used:
        raise HTTPException(400, "已有订单使用该自提点，无法删除")
    total = db.query(models.PickupPoint).count()
    if total <= 1:
        raise HTTPException(400, "至少保留一个自提点")
    db.delete(p)
    db.commit()
    return {"ok": True}


@app.post("/api/admin/orders/{order_id}/status")
def admin_order_status(
    order_id: int,
    body: StatusBody,
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_token)
    allowed = {"pending_pay", "paid", "ready", "completed", "cancelled"}
    if body.status not in allowed:
        raise HTTPException(400, "非法状态")
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(404, "订单不存在")
    order.status = body.status
    db.commit()
    db.refresh(order)
    return _order_dict(order)
