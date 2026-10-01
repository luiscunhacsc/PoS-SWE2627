from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from conftest import login, sale_payload

from mercado.db import connect
from mercado.domain import Problem, checkout, tax_included


@pytest.mark.parametrize(
    "amount,rate,expected",
    [(89, 6, 5), (178, 6, 10), (149, 23, 28), (100, 13, 12), (1, 6, 0), (12300, 23, 2300)],
)
def test_tax_rounding(amount, rate, expected):
    assert tax_included(amount, rate) == expected


def test_sale_receipt_stock_cash_and_audit(client, auth, shift, db):
    response = client.post("/api/sales", json=sale_payload(shift), headers=auth)
    assert response.status_code == 201
    assert (
        response.json["total_cents"],
        response.json["change_cents"],
        response.json["tax_cents"],
    ) == (178, 22, 10)
    assert response.json["items"][0]["name"] == "Leite"
    assert (
        db.execute("SELECT quantity FROM inventory WHERE store_id=1 AND product_id=1").fetchone()[0]
        == 8
    )
    assert db.execute("SELECT delta FROM stock_movements").fetchone()[0] == -2
    assert db.execute("SELECT COUNT(*) FROM audit WHERE action='sale.complete'").fetchone()[0] == 1
    assert client.get("/api/shifts/current").json["expected_cents"] == 10178


def test_client_cannot_override_price(client, auth, shift):
    payload = sale_payload(shift, total_cents=1, tax_cents=0)
    payload["items"][0]["price_cents"] = 1
    assert client.post("/api/sales", json=payload, headers=auth).json["total_cents"] == 178


@pytest.mark.parametrize(
    "changes,status",
    [
        ({"items": []}, 400),
        ({"items": [{"product_id": 1, "quantity": 0}]}, 400),
        ({"items": [{"product_id": 1, "quantity": True}]}, 400),
        ({"items": [{"product_id": 1, "quantity": 1.5}]}, 400),
        ({"items": [{"product_id": 1, "quantity": 11}]}, 409),
        ({"items": [{"product_id": 999, "quantity": 1}]}, 404),
        ({"items": [{"product_id": 3, "quantity": 1}]}, 409),
        ({"items": [None]}, 400),
        ({"payment": "credit"}, 400),
        ({"tendered_cents": 100}, 400),
        ({"tendered_cents": -1}, 400),
        ({"idempotency_key": "short"}, 400),
        ({"shift_id": 999}, 403),
    ],
)
def test_invalid_sale_no_side_effects(client, auth, shift, db, changes, status):
    assert (
        client.post("/api/sales", json=sale_payload(shift, **changes), headers=auth).status_code
        == status
    )
    assert db.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0
    assert (
        db.execute("SELECT quantity FROM inventory WHERE store_id=1 AND product_id=1").fetchone()[0]
        == 10
    )


def test_all_or_nothing_on_second_line(client, auth, shift, db):
    payload = sale_payload(
        shift, items=[{"product_id": 1, "quantity": 1}, {"product_id": 3, "quantity": 1}]
    )
    assert client.post("/api/sales", json=payload, headers=auth).status_code == 409
    assert (
        db.execute("SELECT quantity FROM inventory WHERE store_id=1 AND product_id=1").fetchone()[0]
        == 10
    )
    assert db.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 0


def test_duplicate_lines_aggregate_before_stock_check(client, auth, shift):
    payload = sale_payload(
        shift, items=[{"product_id": 1, "quantity": 6}, {"product_id": 1, "quantity": 6}]
    )
    assert client.post("/api/sales", json=payload, headers=auth).status_code == 409


def test_idempotency_and_changed_payload(client, auth, shift, db):
    first = client.post("/api/sales", json=sale_payload(shift), headers=auth)
    second = client.post("/api/sales", json=sale_payload(shift), headers=auth)
    assert first.json == second.json
    assert db.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 1
    assert (
        client.post(
            "/api/sales", json=sale_payload(shift, tendered_cents=300), headers=auth
        ).status_code
        == 409
    )


@pytest.mark.parametrize("payment", ["card", "mbway"])
def test_electronic_payments_do_not_change_cash(client, auth, shift, payment):
    response = client.post(
        "/api/sales", json=sale_payload(shift, payment=payment, tendered_cents=0), headers=auth
    )
    assert response.status_code == 201
    assert response.json["change_cents"] == 0
    assert response.json["tendered_cents"] == 178
    assert client.get("/api/shifts/current").json["expected_cents"] == 10000


def test_void_once_restock_and_reporting(client, auth, shift, db):
    sale = client.post("/api/sales", json=sale_payload(shift), headers=auth).json
    assert (
        client.post(
            f"/api/sales/{sale['id']}/void", json={"reason": "Erro de operação"}, headers=auth
        ).status_code
        == 403
    )
    manager_headers = login(client, "manager")
    assert (
        client.post(
            f"/api/sales/{sale['id']}/void",
            json={"reason": "Erro de operação"},
            headers=manager_headers,
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/sales/{sale['id']}/void",
            json={"reason": "Outra tentativa"},
            headers=manager_headers,
        ).status_code
        == 409
    )
    assert (
        db.execute("SELECT quantity FROM inventory WHERE store_id=1 AND product_id=1").fetchone()[0]
        == 10
    )
    assert client.get("/api/dashboard?store_id=1").json["revenue_cents"] == 0


def test_snapshot_receipt_is_immutable(client, auth, shift, db):
    sale = client.post("/api/sales", json=sale_payload(shift), headers=auth).json
    db.execute("UPDATE products SET name='Novo nome',price_cents=999 WHERE id=1")
    saved = client.get(f"/api/sales/{sale['id']}").json
    assert saved["items"][0]["name"] == "Leite"
    assert saved["total_cents"] == 178


def test_concurrent_last_unit_not_oversold(app, db, shift):
    db.execute("UPDATE inventory SET quantity=1 WHERE store_id=1 AND product_id=1")
    user = dict(db.execute("SELECT * FROM users WHERE id=3").fetchone())
    barrier = Barrier(2)

    def buy(index):
        connection = connect(app.config["DATABASE"])
        barrier.wait()
        try:
            checkout(
                connection,
                user,
                sale_payload(
                    shift,
                    idempotency_key=f"parallel-{index}",
                    items=[{"product_id": 1, "quantity": 1}],
                ),
            )
            return 201
        except Problem as error:
            return error.status
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(buy, [1, 2]))
    assert sorted(outcomes) == [201, 409]
    assert (
        db.execute("SELECT quantity FROM inventory WHERE store_id=1 AND product_id=1").fetchone()[0]
        == 0
    )


def test_concurrent_retry_creates_one_sale(app, db, shift):
    user = dict(db.execute("SELECT * FROM users WHERE id=3").fetchone())
    barrier = Barrier(2)

    def buy(_):
        connection = connect(app.config["DATABASE"])
        barrier.wait()
        try:
            return checkout(connection, user, sale_payload(shift))["id"]
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        ids = list(pool.map(buy, [1, 2]))
    assert ids[0] == ids[1]
    assert db.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 1
