"""Repeatable demo business data. Password salts and session tokens remain random."""

import random
from datetime import datetime, timedelta, timezone

from werkzeug.security import generate_password_hash

from .db import transaction
from .domain import audit, checkout, close_shift, open_shift

PRODUCTS = [
    ("Banana da Madeira", "Fruta e legumes", "🍌", 189, 6),
    ("Maçã Royal Gala · 1 kg", "Fruta e legumes", "🍎", 229, 6),
    ("Laranja do Algarve · 1 kg", "Fruta e legumes", "🍊", 179, 6),
    ("Abacate · unidade", "Fruta e legumes", "🥑", 149, 6),
    ("Tomate redondo · 500 g", "Fruta e legumes", "🍅", 139, 6),
    ("Cenoura · 1 kg", "Fruta e legumes", "🥕", 99, 6),
    ("Brócolos · unidade", "Fruta e legumes", "🥦", 169, 6),
    ("Batata branca · 2 kg", "Fruta e legumes", "🥔", 249, 6),
    ("Pão de mistura", "Padaria", "🍞", 125, 6),
    ("Croissant de manteiga", "Padaria", "🥐", 110, 23),
    ("Baguete de trigo", "Padaria", "🥖", 89, 6),
    ("Pastel de nata", "Padaria", "🥧", 120, 23),
    ("Leite meio-gordo · 1 L", "Laticínios e ovos", "🥛", 89, 6),
    ("Iogurte natural · 4 un.", "Laticínios e ovos", "🥣", 169, 6),
    ("Queijo flamengo · 200 g", "Laticínios e ovos", "🧀", 239, 6),
    ("Ovos do campo · 6 un.", "Laticínios e ovos", "🥚", 199, 6),
    ("Manteiga com sal · 250 g", "Laticínios e ovos", "🧈", 219, 6),
    ("Peito de frango · 500 g", "Talho e peixaria", "🍗", 399, 6),
    ("Salmão · 2 lombos", "Talho e peixaria", "🐟", 649, 6),
    ("Carne picada · 500 g", "Talho e peixaria", "🥩", 459, 6),
    ("Arroz agulha · 1 kg", "Mercearia", "🍚", 129, 6),
    ("Massa esparguete · 500 g", "Mercearia", "🍝", 89, 6),
    ("Azeite virgem · 750 ml", "Mercearia", "🫒", 599, 6),
    ("Atum ao natural · 120 g", "Mercearia", "🥫", 149, 6),
    ("Feijão encarnado · 500 g", "Mercearia", "🫘", 99, 6),
    ("Cereais de aveia · 500 g", "Mercearia", "🌾", 189, 23),
    ("Café moído · 250 g", "Mercearia", "☕", 329, 23),
    ("Bolachas Maria · 200 g", "Mercearia", "🍪", 99, 23),
    ("Chocolate negro · 100 g", "Mercearia", "🍫", 149, 23),
    ("Sal marinho · 1 kg", "Mercearia", "🧂", 59, 6),
    ("Água mineral · 1,5 L", "Bebidas", "💧", 39, 13),
    ("Sumo de laranja · 1 L", "Bebidas", "🧃", 179, 23),
    ("Chá verde · 20 saquetas", "Bebidas", "🍵", 159, 23),
    ("Água com gás · 1 L", "Bebidas", "🫧", 79, 13),
    ("Pizza margarita", "Congelados", "🍕", 299, 23),
    ("Ervilhas · 750 g", "Congelados", "🫛", 159, 6),
    ("Gelado de baunilha · 1 L", "Congelados", "🍨", 349, 23),
    ("Pescada · 400 g", "Congelados", "🐟", 379, 6),
    ("Detergente da roupa · 30 doses", "Casa e higiene", "🧴", 699, 23),
    ("Papel higiénico · 12 rolos", "Casa e higiene", "🧻", 399, 23),
    ("Sabonete de mãos · 500 ml", "Casa e higiene", "🧼", 189, 23),
    ("Pasta de dentes · 75 ml", "Casa e higiene", "🪥", 249, 23),
    ("Esponjas de cozinha · 3 un.", "Casa e higiene", "🧽", 99, 23),
    ("Sacos do lixo · 20 un.", "Casa e higiene", "🗑️", 149, 23),
    ("Alface fresca", "Fruta e legumes", "🥬", 119, 6),
    ("Morangos · 250 g", "Fruta e legumes", "🍓", 249, 6),
    ("Mel multifloral · 500 g", "Mercearia", "🍯", 389, 6),
    ("Pão de sementes", "Padaria", "🍞", 179, 6),
]


def seed(db, reference_date=None):
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        return False
    rng = random.Random(20261001)
    base = (
        datetime.fromisoformat(reference_date).replace(tzinfo=timezone.utc)
        if reference_date
        else datetime.now(timezone.utc)
    )
    stamp = (base - timedelta(days=30)).isoformat(timespec="seconds")
    with transaction(db):
        db.executemany(
            "INSERT INTO stores VALUES (?,?,?,?)",
            [
                (1, "Mercado · Lisboa Centro", "Lisboa", "Rua da Horta, 12 · endereço fictício"),
                (
                    2,
                    "Mercado · Porto Boavista",
                    "Porto",
                    "Avenida do Pomar, 48 · endereço fictício",
                ),
                (
                    3,
                    "Mercado · Coimbra Solum",
                    "Coimbra",
                    "Praça da Colheita, 7 · endereço fictício",
                ),
            ],
        )
        for sid in range(1, 4):
            for number in range(1, 3):
                db.execute(
                    "INSERT INTO registers(store_id,name) VALUES (?,?)", (sid, f"Caixa {number:02}")
                )
        users = [
            (1, "Alex Martins", "admin", "admin", None),
            (2, "Inês Duarte", "gerente.lisboa", "manager", 1),
            (3, "Sofia Costa", "caixa.lisboa", "cashier", 1),
            (4, "Miguel Rocha", "gerente.porto", "manager", 2),
            (5, "Tiago Melo", "caixa.porto", "cashier", 2),
            (6, "Leonor Reis", "gerente.coimbra", "manager", 3),
            (7, "Rita Santos", "caixa.coimbra", "cashier", 3),
        ]
        for uid, name, username, role, sid in users:
            db.execute(
                "INSERT INTO users VALUES (?,?,?,?,?,?)",
                (uid, name, username, generate_password_hash("Demo2026!"), role, sid),
            )
        for pid, (name, category, emoji, price, rate) in enumerate(PRODUCTS, 1):
            # Internal test barcode, deliberately not a claim of a valid GS1 identifier.
            db.execute(
                "INSERT INTO products(id,sku,barcode,name,category,emoji,price_cents,tax_rate) VALUES (?,?,?,?,?,?,?,?)",
                (pid, f"MRC-{pid:04}", f"20000000{pid:05}", name, category, emoji, price, rate),
            )
            for sid in range(1, 4):
                qty = rng.randint(150, 280)
                db.execute("INSERT INTO inventory VALUES (?,?,?,10)", (sid, pid, qty))
                db.execute(
                    "INSERT INTO stock_movements(store_id,product_id,user_id,delta,reason,created_at) VALUES (?,?,1,?,?,?)",
                    (sid, pid, qty, "Carga inicial fictícia", stamp),
                )
    for sid, uid in [(1, 3), (2, 5), (3, 7)]:
        user = dict(db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone())
        shift = open_shift(db, user, {"register_id": 2 * sid - 1, "opening_cents": 15000})
        db.execute("UPDATE shifts SET opened_at=? WHERE id=?", (stamp, shift))
        for index in range(60):
            day = base - timedelta(days=29 - index // 2)
            timestamp = min(
                day.replace(hour=8 + index % 2, minute=rng.randint(0, 59), second=0), base
            ).isoformat(timespec="seconds")
            result = checkout(
                db,
                user,
                {
                    "shift_id": shift,
                    "idempotency_key": f"seed-{sid}-{index:04}",
                    "items": [
                        {"product_id": pid, "quantity": rng.randint(1, 3)}
                        for pid in rng.sample(range(1, 49), rng.randint(2, 6))
                    ],
                    "payment": rng.choice(["cash", "card", "card", "mbway"]),
                    "tendered_cents": 10000,
                },
            )
            db.execute("UPDATE sales SET created_at=? WHERE id=?", (timestamp, result["id"]))
            db.execute(
                "UPDATE stock_movements SET created_at=? WHERE sale_id=?", (timestamp, result["id"])
            )
            db.execute(
                "UPDATE audit SET created_at=? WHERE entity='sale' AND entity_id=?",
                (timestamp, result["id"]),
            )
        cash = (
            db.execute(
                "SELECT SUM(total_cents) FROM sales WHERE shift_id=? AND payment='cash'", (shift,)
            ).fetchone()[0]
            or 0
        )
        close_shift(db, user, shift, 15000 + cash)
    with transaction(db):
        for sid in range(1, 4):
            for pid, target in [(4, 4), (12, 7), (18, 0), (23, 3), (39, 8)]:
                qty = db.execute(
                    "SELECT quantity FROM inventory WHERE store_id=? AND product_id=?", (sid, pid)
                ).fetchone()[0]
                db.execute(
                    "UPDATE inventory SET quantity=? WHERE store_id=? AND product_id=?",
                    (target, sid, pid),
                )
                db.execute(
                    "INSERT INTO stock_movements(store_id,product_id,user_id,delta,reason,created_at) VALUES (?,?,1,?,?,?)",
                    (
                        sid,
                        pid,
                        target - qty,
                        "Cenário fictício: stock baixo",
                        base.isoformat(timespec="seconds"),
                    ),
                )
        audit(
            db, 1, "demo.seed", "database", None, {"seed": 20261001, "products": 48, "sales": 180}
        )
    return True
