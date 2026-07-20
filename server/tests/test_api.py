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
