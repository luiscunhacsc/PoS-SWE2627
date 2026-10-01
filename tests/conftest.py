import pytest
from werkzeug.security import generate_password_hash

from mercado import create_app
from mercado.db import connect, migrate


@pytest.fixture
def app(tmp_path):
    path = tmp_path / "test.sqlite3"
    db = connect(path)
    migrate(db)
    password_hash = generate_password_hash("TestPassword!", method="pbkdf2:sha256:1000")
    db.executescript("""
      INSERT INTO stores VALUES (1,'Loja A','Lisboa','Fictícia'),(2,'Loja B','Porto','Fictícia');
      INSERT INTO registers VALUES (1,1,'Caixa 1'),(2,1,'Caixa 2'),(3,2,'Caixa 1');
      INSERT INTO products VALUES (1,'SKU-1','2000000000001','Leite','Laticínios','🥛',89,6,1),
        (2,'SKU-2','2000000000002','Chocolate','Mercearia','🍫',149,23,1),
        (3,'SKU-3','2000000000003','Esgotado','Mercearia','🥫',200,13,1);
      INSERT INTO inventory VALUES (1,1,10,5),(1,2,10,5),(1,3,0,5),(2,1,10,5);
    """)
    for uid, username, role, store in [
        (1, "admin", "admin", None),
        (2, "manager", "manager", 1),
        (3, "cashier", "cashier", 1),
        (4, "other", "cashier", 2),
        (5, "second", "cashier", 1),
    ]:
        db.execute(
            "INSERT INTO users VALUES (?,?,?,?,?,?)",
            (uid, username, username, password_hash, role, store),
        )
    db.close()
    return create_app({"TESTING": True, "DATABASE": str(path)})


@pytest.fixture
def db(app):
    connection = connect(app.config["DATABASE"])
    yield connection
    connection.close()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username="cashier"):
    response = client.post("/api/login", json={"username": username, "password": "TestPassword!"})
    assert response.status_code == 200
    return {"X-CSRF-Token": response.json["csrf"]}


@pytest.fixture
def auth(client):
    return login(client)


@pytest.fixture
def shift(client, auth):
    response = client.post(
        "/api/shifts", json={"register_id": 1, "opening_cents": 10000}, headers=auth
    )
    assert response.status_code == 201
    return response.json["id"]


def sale_payload(shift, **changes):
    return {
        "shift_id": shift,
        "idempotency_key": "test-sale-0001",
        "items": [{"product_id": 1, "quantity": 2}],
        "payment": "cash",
        "tendered_cents": 200,
        **changes,
    }
