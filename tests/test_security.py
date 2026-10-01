from conftest import login, sale_payload


def test_authentication_and_security_headers(client):
    assert client.get("/api/products?store_id=1").status_code == 401
    response = client.get("/")
    assert response.status_code == 200
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert client.get("/health").json["status"] == "ok"
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/app.css").status_code == 200


def test_csrf_origin_and_json(client, auth):
    data = {"register_id": 1, "opening_cents": 0}
    assert client.post("/api/shifts", json=data).status_code == 403
    assert (
        client.post("/api/shifts", json=data, headers={"X-CSRF-Token": "inválido"}).status_code
        == 403
    )
    assert (
        client.post(
            "/api/shifts", json=data, headers={**auth, "Origin": "https://evil.test"}
        ).status_code
        == 403
    )
    assert client.post("/api/login", data="username=admin").status_code == 415
    assert client.post("/api/shifts", json=[], headers=auth).status_code == 400
    assert (
        client.post("/api/shifts", json={**data, "opening_cents": False}, headers=auth).status_code
        == 400
    )


def test_cookie_logout_and_expiry(client, db):
    response = client.post("/api/login", json={"username": "cashier", "password": "TestPassword!"})
    assert "HttpOnly" in response.headers["Set-Cookie"]
    assert "SameSite=Strict" in response.headers["Set-Cookie"]
    assert (
        client.post(
            "/api/logout", json={}, headers={"X-CSRF-Token": response.json["csrf"]}
        ).status_code
        == 200
    )
    assert client.get("/api/me").status_code == 401
    login(client)
    db.execute("UPDATE sessions SET expires_at=0")
    assert client.get("/api/me").status_code == 401


def test_login_rate_limit_and_sql_injection(client):
    for _ in range(5):
        assert (
            client.post(
                "/api/login", json={"username": "admin' OR 1=1 --", "password": "wrong"}
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/api/login", json={"username": "admin' OR 1=1 --", "password": "wrong"}
        ).status_code
        == 429
    )


def test_store_and_role_boundaries(client, auth, shift):
    assert len(client.get("/api/stores").json) == 1
    for endpoint in ["products", "sales"]:
        assert client.get(f"/api/{endpoint}?store_id=2").status_code == 403
    for endpoint in ["dashboard?store_id=1", "audit", "inventory/movements?store_id=1"]:
        assert client.get("/api/" + endpoint).status_code == 403
    assert (
        client.post(
            "/api/inventory/adjust",
            json={"store_id": 1, "product_id": 1, "delta": 1, "reason": "Test stock"},
            headers=auth,
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/shifts", json={"register_id": 3, "opening_cents": 0}, headers=auth
        ).status_code
        == 403
    )
    sale = client.post("/api/sales", json=sale_payload(shift), headers=auth).json
    other = login(client, "other")
    assert client.get(f"/api/sales/{sale['id']}").status_code == 403
    assert client.post("/api/sales", json=sale_payload(shift), headers=other).status_code == 403
    admin = login(client, "admin")
    assert len(client.get("/api/stores").json) == 2
    assert client.get("/api/audit").status_code == 200
    assert (
        client.post(
            "/api/shifts", json={"register_id": 3, "opening_cents": 0}, headers=admin
        ).status_code
        == 201
    )


def test_manager_scope_and_invalid_store(client):
    login(client, "manager")
    assert client.get("/api/dashboard?store_id=2").status_code == 403
    assert client.get("/api/audit").status_code == 403
    assert client.get("/api/products?store_id=abc").status_code == 400
    login(client, "admin")
    assert client.get("/api/products?store_id=999").status_code == 404


def test_session_token_hashed_and_password_not_exposed(client, db):
    login(client)
    me = client.get("/api/me").json
    assert "password_hash" not in me
    cookie = client.get_cookie("pos_session")
    stored = db.execute("SELECT token_hash FROM sessions").fetchone()[0]
    assert cookie.value != stored and len(stored) == 64


def test_payload_limit(client, auth):
    assert (
        client.post("/api/shifts", json={"padding": "x" * 70000}, headers=auth).status_code == 413
    )


def test_relogin_revokes_previous_token(client, db):
    login(client)
    first = client.get_cookie("pos_session").value
    login(client)
    assert client.get_cookie("pos_session").value != first
    assert db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 1
