"""邻里小店 API 测试：商品、购物车、下单、模拟支付。"""
import pytest
from fastapi.testclient import TestClient

from app.main import app, reset_db


@pytest.fixture()
def client():
    reset_db()
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_products_seeded(client):
    r = client.get("/api/products")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    assert "id" in items[0] and "name" in items[0] and "price_cents" in items[0]


def test_cart_add_and_get(client):
    products = client.get("/api/products").json()
    pid = products[0]["id"]
    r = client.post("/api/cart/items", json={"product_id": pid, "qty": 2})
    assert r.status_code == 200
    cart = client.get("/api/cart").json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["qty"] == 2
    assert cart["total_cents"] == products[0]["price_cents"] * 2


def test_create_order_and_mock_pay(client):
    products = client.get("/api/products").json()
    pid = products[0]["id"]
    client.post("/api/cart/items", json={"product_id": pid, "qty": 1})
    r = client.post(
        "/api/orders",
        json={"pickup_point_id": 1, "buyer_name": "测试用户", "buyer_phone": "13800000000"},
    )
    assert r.status_code == 200
    order = r.json()
    assert order["status"] == "pending_pay"
    assert order["total_cents"] > 0
    oid = order["id"]

    # cart cleared
    cart = client.get("/api/cart").json()
    assert cart["items"] == []

    pay = client.post(f"/api/orders/{oid}/mock-pay")
    assert pay.status_code == 200
    assert pay.json()["status"] == "paid"

    detail = client.get(f"/api/orders/{oid}").json()
    assert detail["status"] == "paid"


def test_admin_list_orders(client):
    products = client.get("/api/products").json()
    client.post("/api/cart/items", json={"product_id": products[0]["id"], "qty": 1})
    order = client.post(
        "/api/orders",
        json={"pickup_point_id": 1, "buyer_name": "A", "buyer_phone": "13900000000"},
    ).json()
    client.post(f"/api/orders/{order['id']}/mock-pay")

    r = client.get("/api/admin/orders", headers={"X-Admin-Token": "dev-admin"})
    assert r.status_code == 200
    assert any(o["id"] == order["id"] for o in r.json())


def test_admin_mark_ready(client):
    products = client.get("/api/products").json()
    client.post("/api/cart/items", json={"product_id": products[0]["id"], "qty": 1})
    order = client.post(
        "/api/orders",
        json={"pickup_point_id": 1, "buyer_name": "A", "buyer_phone": "13900000000"},
    ).json()
    client.post(f"/api/orders/{order['id']}/mock-pay")
    r = client.post(
        f"/api/admin/orders/{order['id']}/status",
        json={"status": "ready"},
        headers={"X-Admin-Token": "dev-admin"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


def test_admin_create_product(client):
    r = client.post(
        "/api/admin/products",
        json={
            "name": "新鲜菠菜 1 斤",
            "desc": "当日采摘",
            "price_cents": 680,
            "stock": 30,
            "on_sale": True,
        },
        headers={"X-Admin-Token": "dev-admin"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "新鲜菠菜 1 斤"
    assert body["price_cents"] == 680
    assert body["id"] > 0

    listed = client.get("/api/products").json()
    assert any(p["id"] == body["id"] for p in listed)


def test_cart_update_and_orders_list(client):
    products = client.get("/api/products").json()
    pid = products[0]["id"]
    client.post("/api/cart/items", json={"product_id": pid, "qty": 1})
    cart = client.get("/api/cart").json()
    item_id = cart["items"][0]["id"]

    r = client.patch(f"/api/cart/items/{item_id}", json={"qty": 3})
    assert r.status_code == 200
    cart = client.get("/api/cart").json()
    assert cart["items"][0]["qty"] == 3

    order = client.post(
        "/api/orders",
        json={"pickup_point_id": 1, "buyer_name": "B", "buyer_phone": "13700000000"},
    ).json()
    listed = client.get("/api/orders").json()
    assert any(o["id"] == order["id"] for o in listed)

    cancel = client.post(f"/api/orders/{order['id']}/cancel")
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"


def test_product_detail_and_pickup_admin(client):
    products = client.get("/api/products").json()
    pid = products[0]["id"]
    detail = client.get(f"/api/products/{pid}")
    assert detail.status_code == 200
    assert detail.json()["id"] == pid

    headers = {"X-Admin-Token": "dev-admin"}
    created = client.post(
        "/api/admin/pickup-points",
        json={"name": "测试驿站", "address": "测试路 1 号"},
        headers=headers,
    )
    assert created.status_code == 200
    point_id = created.json()["id"]

    patched = client.patch(
        f"/api/admin/pickup-points/{point_id}",
        json={"name": "测试驿站改", "address": "测试路 2 号"},
        headers=headers,
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "测试驿站改"

    deleted = client.delete(f"/api/admin/pickup-points/{point_id}", headers=headers)
    assert deleted.status_code == 200
