import sqlite3

import pytest
from conftest import login, sale_payload

from mercado.db import connect, migrate
from mercado.seed import seed


def test_shift_unique_and_reopen(client, auth, shift):
    assert (
        client.post(
            "/api/shifts", json={"register_id": 2, "opening_cents": 0}, headers=auth
        ).status_code
        == 409
    )
    second = login(client, "second")
    assert (
        client.post(
            "/api/shifts", json={"register_id": 1, "opening_cents": 0}, headers=second
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"/api/shifts/{shift}/close", json={"counted_cents": 0}, headers=second
        ).status_code
        == 403
    )
    original = login(client)
    close = client.post(
        f"/api/shifts/{shift}/close", json={"counted_cents": 9900}, headers=original
    )
    assert close.json["difference_cents"] == -100
    assert (
        client.post(
            "/api/shifts", json={"register_id": 1, "opening_cents": 0}, headers=original
        ).status_code
        == 201
    )


def test_closed_shift_blocks_sale_void_and_double_close(client, auth, shift):
    sale = client.post("/api/sales", json=sale_payload(shift), headers=auth).json
    assert (
        client.post(f"/api/shifts/{shift}/close", json={"counted_cents": 10178}, headers=auth).json[
            "difference_cents"
        ]
        == 0
    )
    assert (
        client.post(
            f"/api/shifts/{shift}/close", json={"counted_cents": 10178}, headers=auth
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/sales", json=sale_payload(shift, idempotency_key="new-after-close"), headers=auth
        ).status_code
        == 409
    )
    # Retry of the committed sale still works, even after the shift closes.
    assert (
        client.post("/api/sales", json=sale_payload(shift), headers=auth).json["id"] == sale["id"]
    )
    admin = login(client, "admin")
    assert (
        client.post(
            f"/api/sales/{sale['id']}/void", json={"reason": "Erro de teste"}, headers=admin
        ).status_code
        == 409
    )


def test_stock_adjustment_and_negative_guard(client, db):
    headers = login(client, "manager")
    body = {"store_id": 1, "product_id": 1, "delta": 20, "reason": "Receção fictícia"}
    assert client.post("/api/inventory/adjust", json=body, headers=headers).json["quantity"] == 30
    assert (
        client.post(
            "/api/inventory/adjust", json={**body, "delta": -31}, headers=headers
        ).status_code
        == 409
    )
    assert (
        client.post("/api/inventory/adjust", json={**body, "delta": 0}, headers=headers).status_code
        == 400
    )
    assert (
        client.post(
            "/api/inventory/adjust", json={**body, "reason": "x"}, headers=headers
        ).status_code
        == 400
    )
    assert db.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 1
    assert client.get("/api/inventory/movements?store_id=1").json[0]["delta"] == 20


def test_database_constraints(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE inventory SET quantity=-1")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO inventory VALUES (99,1,1,1)")


def test_seed_repeatable_counts_and_stock_ledger(tmp_path):
    db = connect(tmp_path / "seed.sqlite3")
    migrate(db)
    assert seed(db, "2026-10-01") is True
    counts = {
        table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ["stores", "registers", "products", "users", "sales"]
    }
    assert counts == {"stores": 3, "registers": 6, "products": 48, "users": 7, "sales": 180}
    assert seed(db, "2026-10-01") is False
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    mismatches = db.execute("""SELECT i.product_id FROM inventory i JOIN stock_movements m
      ON i.store_id=m.store_id AND i.product_id=m.product_id GROUP BY i.store_id,i.product_id
      HAVING i.quantity<>SUM(m.delta)""").fetchall()
    assert mismatches == []
    target = sqlite3.connect(tmp_path / "backup.sqlite3")
    db.backup(target)
    assert target.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 180
    assert target.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    target.close()
    db.close()
