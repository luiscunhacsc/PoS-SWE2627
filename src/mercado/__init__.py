import hashlib
import json
import logging
import os
import secrets
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

from . import domain
from .db import close_db, get_db, rows, transaction


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.environ.get("POS_DATABASE", str(Path.cwd() / "instance" / "mercado.sqlite3")),
        COOKIE_SECURE=os.environ.get("POS_COOKIE_SECURE", "0") == "1",
        MAX_CONTENT_LENGTH=64 * 1024,
        TRUSTED_HOSTS=os.environ.get("POS_TRUSTED_HOSTS", "localhost,127.0.0.1,[::1]").split(","),
    )
    if config:
        app.config.update(config)
    app.json.ensure_ascii = False
    app.teardown_appcontext(close_db)
    dummy_hash = generate_password_hash(secrets.token_hex(24))

    @app.before_request
    def authentication():
        g.started = time.perf_counter()
        g.request_id = secrets.token_hex(8)
        g.user = None
        if not request.path.startswith("/api/"):
            return
        if request.method != "GET":
            origin = request.headers.get("Origin")
            if origin and origin != request.host_url.rstrip("/"):
                raise domain.Problem("Origem do pedido não autorizada.", 403)
            if not request.is_json:
                raise domain.Problem("Utilize um pedido JSON.", 415)
        if request.path == "/api/login":
            return
        token = request.cookies.get("pos_session", "")
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = (
            get_db()
            .execute(
                """SELECT u.id,u.name,u.username,u.role,u.store_id,s.csrf FROM sessions s
            JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>?""",
                (token_hash, int(time.time())),
            )
            .fetchone()
        )
        if not session:
            raise domain.Problem("Inicie sessão para continuar.", 401)
        g.user = dict(session)
        g.token_hash = token_hash
        if request.method != "GET" and not secrets.compare_digest(
            request.headers.get("X-CSRF-Token", "").encode(), session["csrf"].encode()
        ):
            raise domain.Problem("Sessão de segurança inválida. Atualize a página.", 403)

    @app.after_request
    def headers(response):
        response.headers.update(
            {
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "same-origin",
                "Cache-Control": "no-store",
                "X-Request-ID": getattr(g, "request_id", ""),
            }
        )
        if app.config["COOKIE_SECURE"]:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        app.logger.info(
            json.dumps(
                {
                    "event": "http",
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "request_id": getattr(g, "request_id", ""),
                    "duration_ms": round(
                        (time.perf_counter() - getattr(g, "started", time.perf_counter())) * 1000, 2
                    ),
                }
            )
        )
        return response

    @app.errorhandler(domain.Problem)
    def business_error(error):
        return jsonify(error=error.message), error.status

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(
            error="Pedido inválido ou recurso indisponível.", status=error.code
        ), error.code

    @app.errorhandler(sqlite3.OperationalError)
    def database_error(error):
        app.logger.exception("database_error")
        return jsonify(
            error="Base de dados indisponível. Tente novamente.", request_id=g.request_id
        ), 503

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.exception("unexpected_error")
        return jsonify(
            error="Erro interno. Consulte o identificador nos registos.", request_id=g.request_id
        ), 500

    def body():
        data = request.get_json()
        if not isinstance(data, dict):
            raise domain.Problem("O pedido deve ser um objeto JSON.")
        return data

    def store_arg():
        value = request.args.get("store_id", str(g.user["store_id"] or 1))
        try:
            store_id = int(value)
        except (ValueError, TypeError):
            raise domain.Problem("Loja inválida.") from None
        domain.authorize_store(g.user, store_id)
        if not get_db().execute("SELECT id FROM stores WHERE id=?", (store_id,)).fetchone():
            raise domain.Problem("Loja não encontrada.", 404)
        return store_id

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        get_db().execute("SELECT version FROM schema_version").fetchone()
        return {"status": "ok", "version": "0.1.0"}

    @app.post("/api/login")
    def login():
        data = body()
        username = domain.text(data.get("username"), "Utilizador", 1, 80).lower()
        password = domain.text(data.get("password"), "Palavra-passe", 1, 200)
        db = get_db()
        timestamp = int(time.time())
        bucket = hashlib.sha256(f"{request.remote_addr}:{username}".encode()).hexdigest()
        with transaction(db):
            db.execute("DELETE FROM login_attempts WHERE expires_at<=?", (timestamp,))
            attempt = db.execute(
                "SELECT attempts FROM login_attempts WHERE bucket=?", (bucket,)
            ).fetchone()
            if attempt and attempt["attempts"] >= 5:
                raise domain.Problem("Demasiadas tentativas. Aguarde 5 minutos.", 429)
            db.execute(
                "INSERT INTO login_attempts VALUES (?,1,?) ON CONFLICT(bucket) DO UPDATE SET attempts=attempts+1",
                (bucket, timestamp + 300),
            )
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        valid = check_password_hash(user["password_hash"] if user else dummy_hash, password)
        if not user or not valid:
            raise domain.Problem("Utilizador ou palavra-passe incorretos.", 401)
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        with transaction(db):
            db.execute("DELETE FROM login_attempts WHERE bucket=?", (bucket,))
            db.execute("DELETE FROM sessions WHERE expires_at<=?", (timestamp,))
            old_token = request.cookies.get("pos_session", "")
            db.execute(
                "DELETE FROM sessions WHERE token_hash=?",
                (hashlib.sha256(old_token.encode()).hexdigest(),),
            )
            db.execute(
                "INSERT INTO sessions VALUES (?,?,?,?)",
                (
                    hashlib.sha256(token.encode()).hexdigest(),
                    user["id"],
                    csrf,
                    timestamp + 8 * 3600,
                ),
            )
            domain.audit(db, user["id"], "auth.login", "user", user["id"], {})
        response = jsonify(csrf=csrf)
        response.set_cookie(
            "pos_session",
            token,
            httponly=True,
            secure=app.config["COOKIE_SECURE"],
            samesite="Strict",
            max_age=8 * 3600,
        )
        return response

    @app.post("/api/logout")
    def logout():
        db = get_db()
        with transaction(db):
            db.execute("DELETE FROM sessions WHERE token_hash=?", (g.token_hash,))
            domain.audit(db, g.user["id"], "auth.logout", "user", g.user["id"], {})
        response = jsonify(ok=True)
        response.delete_cookie("pos_session")
        return response

    @app.get("/api/me")
    def me():
        return g.user

    @app.get("/api/stores")
    def stores():
        db = get_db()
        result = rows(
            db.execute(
                "SELECT * FROM stores WHERE ?='admin' OR id=?", (g.user["role"], g.user["store_id"])
            )
        )
        for store in result:
            store["registers"] = rows(
                db.execute(
                    """SELECT r.*,sh.id shift_id,u.name operator FROM registers r
                LEFT JOIN shifts sh ON sh.register_id=r.id AND sh.closed_at IS NULL
                LEFT JOIN users u ON u.id=sh.user_id WHERE r.store_id=?""",
                    (store["id"],),
                )
            )
        return jsonify(result)

    @app.get("/api/products")
    def products():
        store_id = store_arg()
        return jsonify(
            rows(
                get_db().execute(
                    "SELECT p.*,i.quantity,i.minimum FROM products p JOIN inventory i ON p.id=i.product_id WHERE i.store_id=? AND p.active=1 ORDER BY p.name",
                    (store_id,),
                )
            )
        )

    @app.get("/api/shifts/current")
    def current_shift():
        db = get_db()
        row = db.execute(
            "SELECT sh.*,r.store_id,r.name register_name FROM shifts sh JOIN registers r ON r.id=sh.register_id WHERE sh.user_id=? AND sh.closed_at IS NULL",
            (g.user["id"],),
        ).fetchone()
        if not row:
            return jsonify(None)
        result = dict(row)
        result.update(domain.shift_totals(db, row["id"]))
        result["expected_cents"] = row["opening_cents"] + result["cash_cents"]
        return result

    @app.post("/api/shifts")
    def shift_open():
        return jsonify(id=domain.open_shift(get_db(), g.user, body())), 201

    @app.post("/api/shifts/<int:shift_id>/close")
    def shift_close(shift_id):
        return domain.close_shift(get_db(), g.user, shift_id, body().get("counted_cents"))

    @app.post("/api/sales")
    def sale_create():
        return jsonify(domain.checkout(get_db(), g.user, body())), 201

    @app.get("/api/sales/<int:sale_id>")
    def sale_receipt(sale_id):
        return domain.receipt(get_db(), g.user, sale_id)

    @app.post("/api/sales/<int:sale_id>/void")
    def sale_void(sale_id):
        return domain.void_sale(get_db(), g.user, sale_id, body().get("reason"))

    @app.get("/api/sales")
    def sales():
        store_id = store_arg()
        return jsonify(
            rows(
                get_db().execute(
                    """SELECT s.id,s.created_at,s.total_cents,s.tax_cents,s.payment,s.status,u.name operator,
            sh.closed_at FROM sales s JOIN users u ON u.id=s.user_id JOIN shifts sh ON sh.id=s.shift_id
            WHERE s.store_id=? ORDER BY s.id DESC LIMIT 200""",
                    (store_id,),
                )
            )
        )

    @app.post("/api/inventory/adjust")
    def stock_adjust():
        return domain.adjust_stock(get_db(), g.user, body())

    @app.get("/api/inventory/movements")
    def movements():
        domain.manager(g.user)
        return jsonify(
            rows(
                get_db().execute(
                    """SELECT m.*,p.name product,u.name operator FROM stock_movements m JOIN products p ON p.id=m.product_id
            JOIN users u ON u.id=m.user_id WHERE m.store_id=? ORDER BY m.id DESC LIMIT 200""",
                    (store_arg(),),
                )
            )
        )

    @app.get("/api/dashboard")
    def dashboard():
        domain.manager(g.user)
        store_id = store_arg()
        db = get_db()
        today = datetime.now(timezone.utc).date()
        first = (today - timedelta(days=6)).isoformat()
        stats = dict(
            db.execute(
                """SELECT COUNT(*) transactions,COALESCE(SUM(total_cents),0) revenue_cents,
            COALESCE(SUM(tax_cents),0) tax_cents FROM sales WHERE store_id=? AND status='completed' AND substr(created_at,1,10)=?""",
                (store_id, today.isoformat()),
            ).fetchone()
        )
        stats["low_stock"] = db.execute(
            "SELECT COUNT(*) FROM inventory WHERE store_id=? AND quantity<=minimum", (store_id,)
        ).fetchone()[0]
        stats["series"] = rows(
            db.execute(
                "SELECT substr(created_at,1,10) day,SUM(total_cents) total FROM sales WHERE store_id=? AND status='completed' AND substr(created_at,1,10)>=? GROUP BY day ORDER BY day",
                (store_id, first),
            )
        )
        stats["top_products"] = rows(
            db.execute(
                "SELECT i.name,SUM(i.quantity) quantity,SUM(i.total_cents) total FROM sale_items i JOIN sales s ON s.id=i.sale_id WHERE s.store_id=? AND s.status='completed' AND substr(s.created_at,1,10)>=? GROUP BY i.product_id,i.name ORDER BY quantity DESC LIMIT 5",
                (store_id, first),
            )
        )
        stats["payments"] = rows(
            db.execute(
                "SELECT payment,COUNT(*) transactions,SUM(total_cents) total FROM sales WHERE store_id=? AND status='completed' AND substr(created_at,1,10)>=? GROUP BY payment",
                (store_id, first),
            )
        )
        return stats

    @app.get("/api/audit")
    def audit_list():
        if g.user["role"] != "admin":
            raise domain.Problem("Apenas o administrador pode consultar a auditoria global.", 403)
        return jsonify(
            rows(
                get_db().execute(
                    "SELECT a.*,u.name operator FROM audit a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT 200"
                )
            )
        )

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    return app
