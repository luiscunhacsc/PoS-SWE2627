"""Business rules. Money is integer cents; prices include the demonstration tax."""

import hashlib
import json
from datetime import datetime, timezone

from .db import transaction


class Problem(Exception):
    def __init__(self, message, status=400):
        self.message = message
        self.status = status


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def integer(value, label, minimum=0, maximum=100_000_000):
    if type(value) is not int or not minimum <= value <= maximum:
        raise Problem(f"{label}: indique um inteiro entre {minimum} e {maximum}.")
    return value


def text(value, label, minimum=1, maximum=200):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise Problem(f"{label}: utilize entre {minimum} e {maximum} caracteres.")
    return value.strip()


def authorize_store(user, store_id):
    if user["role"] != "admin" and user["store_id"] != store_id:
        raise Problem("Não tem acesso a esta loja.", 403)


def manager(user):
    if user["role"] not in ("admin", "manager"):
        raise Problem("Esta operação exige um gerente ou administrador.", 403)


def audit(db, user_id, action, entity, entity_id, details, timestamp=None):
    db.execute(
        "INSERT INTO audit(user_id,action,entity,entity_id,details,created_at) VALUES (?,?,?,?,?,?)",
        (
            user_id,
            action,
            entity,
            entity_id,
            json.dumps(details, ensure_ascii=False),
            timestamp or now(),
        ),
    )


def tax_included(total_cents, rate):
    # Exact positive half-up division, once per line (not per unit).
    denominator = 100 + rate
    return (total_cents * rate * 2 + denominator) // (2 * denominator)


def open_shift(db, user, data):
    register_id = integer(data.get("register_id"), "Caixa", 1)
    opening = integer(data.get("opening_cents"), "Fundo de caixa")
    with transaction(db):
        register = db.execute("SELECT * FROM registers WHERE id=?", (register_id,)).fetchone()
        if not register:
            raise Problem("Caixa não encontrada.", 404)
        authorize_store(user, register["store_id"])
        if db.execute(
            "SELECT id FROM shifts WHERE closed_at IS NULL AND (register_id=? OR user_id=?)",
            (register_id, user["id"]),
        ).fetchone():
            raise Problem("A caixa ou o operador já tem um turno aberto.", 409)
        shift_id = db.execute(
            "INSERT INTO shifts(register_id,user_id,opened_at,opening_cents) VALUES (?,?,?,?)",
            (register_id, user["id"], now(), opening),
        ).lastrowid
        audit(db, user["id"], "shift.open", "shift", shift_id, {"opening_cents": opening})
    return shift_id


def shift_totals(db, shift_id):
    row = db.execute(
        """SELECT COUNT(*) transactions, COALESCE(SUM(total_cents),0) total_cents,
        COALESCE(SUM(CASE WHEN payment='cash' THEN total_cents ELSE 0 END),0) cash_cents
        FROM sales WHERE shift_id=? AND status='completed'""",
        (shift_id,),
    ).fetchone()
    return dict(row)


def close_shift(db, user, shift_id, counted):
    counted = integer(counted, "Numerário contado")
    with transaction(db):
        shift = db.execute("SELECT * FROM shifts WHERE id=?", (shift_id,)).fetchone()
        if not shift:
            raise Problem("Turno não encontrado.", 404)
        if shift["user_id"] != user["id"]:
            raise Problem("Só pode fechar o seu próprio turno.", 403)
        if shift["closed_at"]:
            raise Problem("Este turno já está fechado.", 409)
        expected = shift["opening_cents"] + shift_totals(db, shift_id)["cash_cents"]
        db.execute(
            "UPDATE shifts SET closed_at=?,counted_cents=?,expected_cents=?,difference_cents=? WHERE id=?",
            (now(), counted, expected, counted - expected, shift_id),
        )
        audit(
            db,
            user["id"],
            "shift.close",
            "shift",
            shift_id,
            {
                "counted_cents": counted,
                "expected_cents": expected,
                "difference_cents": counted - expected,
            },
        )
    return {
        "expected_cents": expected,
        "counted_cents": counted,
        "difference_cents": counted - expected,
    }


def receipt(db, user, sale_id):
    sale = db.execute(
        """SELECT s.*,st.name store_name,st.address,u.name operator,r.name register_name
        FROM sales s JOIN stores st ON st.id=s.store_id JOIN users u ON u.id=s.user_id
        JOIN shifts sh ON sh.id=s.shift_id JOIN registers r ON r.id=sh.register_id WHERE s.id=?""",
        (sale_id,),
    ).fetchone()
    if not sale:
        raise Problem("Venda não encontrada.", 404)
    authorize_store(user, sale["store_id"])
    result = dict(sale)
    result.pop("request_hash")
    result.pop("idempotency_key")
    result["items"] = [
        dict(x) for x in db.execute("SELECT * FROM sale_items WHERE sale_id=?", (sale_id,))
    ]
    return result


def checkout(db, user, data):
    key = text(data.get("idempotency_key"), "Identificador da venda", 8, 100)
    shift_id = integer(data.get("shift_id"), "Turno", 1)
    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise Problem("A venda deve conter entre 1 e 100 linhas.")
    quantities = {}
    for item in items:
        if not isinstance(item, dict):
            raise Problem("Linha de venda inválida.")
        pid = integer(item.get("product_id"), "Produto", 1)
        qty = integer(item.get("quantity"), "Quantidade", 1, 999)
        quantities[pid] = integer(quantities.get(pid, 0) + qty, "Quantidade acumulada", 1, 999)
    payment = data.get("payment")
    if payment not in ("cash", "card", "mbway"):
        raise Problem("Meio de pagamento inválido.")
    tendered = integer(data.get("tendered_cents", 0), "Valor recebido")
    fingerprint = hashlib.sha256(
        json.dumps(
            [shift_id, sorted(quantities.items()), payment, tendered], separators=(",", ":")
        ).encode()
    ).hexdigest()
    with transaction(db):
        previous = db.execute(
            "SELECT id,request_hash FROM sales WHERE user_id=? AND idempotency_key=?",
            (user["id"], key),
        ).fetchone()
        if previous:
            if previous["request_hash"] != fingerprint:
                raise Problem("O identificador já foi usado para outra venda.", 409)
            return receipt(db, user, previous["id"])
        shift = db.execute(
            "SELECT sh.*,r.store_id FROM shifts sh JOIN registers r ON r.id=sh.register_id WHERE sh.id=?",
            (shift_id,),
        ).fetchone()
        if not shift or shift["user_id"] != user["id"]:
            raise Problem("Abra o seu turno para registar uma venda.", 403)
        if shift["closed_at"]:
            raise Problem("O turno já está fechado.", 409)
        store_id = shift["store_id"]
        authorize_store(user, store_id)
        lines = []
        for pid, qty in sorted(quantities.items()):
            product = db.execute(
                "SELECT p.*,i.quantity FROM products p JOIN inventory i ON i.product_id=p.id WHERE p.id=? AND i.store_id=? AND p.active=1",
                (pid, store_id),
            ).fetchone()
            if not product:
                raise Problem("Produto indisponível nesta loja.", 404)
            if product["quantity"] < qty:
                raise Problem(
                    f"Stock insuficiente: {product['name']} (disponível: {product['quantity']}).",
                    409,
                )
            total = product["price_cents"] * qty
            lines.append(
                (
                    pid,
                    product["name"],
                    qty,
                    product["price_cents"],
                    product["tax_rate"],
                    tax_included(total, product["tax_rate"]),
                    total,
                )
            )
        total = sum(line[6] for line in lines)
        tax = sum(line[5] for line in lines)
        if payment == "cash" and tendered < total:
            raise Problem("O valor recebido é inferior ao total da venda.")
        tendered = tendered if payment == "cash" else total
        timestamp = now()
        sale_id = db.execute(
            """INSERT INTO sales(store_id,shift_id,user_id,created_at,total_cents,tax_cents,payment,
            tendered_cents,change_cents,idempotency_key,request_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                store_id,
                shift_id,
                user["id"],
                timestamp,
                total,
                tax,
                payment,
                tendered,
                tendered - total,
                key,
                fingerprint,
            ),
        ).lastrowid
        for line in lines:
            db.execute(
                "INSERT INTO sale_items(sale_id,product_id,name,quantity,price_cents,tax_rate,tax_cents,total_cents) VALUES (?,?,?,?,?,?,?,?)",
                (sale_id, *line),
            )
            db.execute(
                "UPDATE inventory SET quantity=quantity-? WHERE store_id=? AND product_id=?",
                (line[2], store_id, line[0]),
            )
            db.execute(
                "INSERT INTO stock_movements(store_id,product_id,user_id,sale_id,delta,reason,created_at) VALUES (?,?,?,?,?,?,?)",
                (store_id, line[0], user["id"], sale_id, -line[2], "Venda", timestamp),
            )
        audit(
            db,
            user["id"],
            "sale.complete",
            "sale",
            sale_id,
            {"total_cents": total, "payment": payment},
        )
    return receipt(db, user, sale_id)


def void_sale(db, user, sale_id, reason):
    manager(user)
    reason = text(reason, "Motivo", 5)
    with transaction(db):
        sale = receipt(db, user, sale_id)
        if sale["status"] != "completed":
            raise Problem("A venda já está anulada.", 409)
        shift = db.execute(
            "SELECT closed_at FROM shifts WHERE id=?", (sale["shift_id"],)
        ).fetchone()
        if shift["closed_at"]:
            raise Problem("Não é possível anular uma venda de um turno fechado.", 409)
        timestamp = now()
        for item in sale["items"]:
            db.execute(
                "UPDATE inventory SET quantity=quantity+? WHERE store_id=? AND product_id=?",
                (item["quantity"], sale["store_id"], item["product_id"]),
            )
            db.execute(
                "INSERT INTO stock_movements(store_id,product_id,user_id,sale_id,delta,reason,created_at) VALUES (?,?,?,?,?,?,?)",
                (
                    sale["store_id"],
                    item["product_id"],
                    user["id"],
                    sale_id,
                    item["quantity"],
                    "Anulação: " + reason,
                    timestamp,
                ),
            )
        db.execute(
            "UPDATE sales SET status='voided',void_reason=?,voided_at=? WHERE id=?",
            (reason, timestamp, sale_id),
        )
        audit(db, user["id"], "sale.void", "sale", sale_id, {"reason": reason})
    return receipt(db, user, sale_id)


def adjust_stock(db, user, data):
    manager(user)
    store_id = integer(data.get("store_id"), "Loja", 1)
    authorize_store(user, store_id)
    pid = integer(data.get("product_id"), "Produto", 1)
    delta = integer(data.get("delta"), "Variação de stock", -10000, 10000)
    if delta == 0:
        raise Problem("A variação não pode ser zero.")
    reason = text(data.get("reason"), "Motivo", 5)
    with transaction(db):
        item = db.execute(
            "SELECT quantity FROM inventory WHERE store_id=? AND product_id=?", (store_id, pid)
        ).fetchone()
        if not item:
            raise Problem("Stock não encontrado.", 404)
        if item["quantity"] + delta < 0:
            raise Problem("O ajuste deixaria o stock negativo.", 409)
        db.execute(
            "UPDATE inventory SET quantity=quantity+? WHERE store_id=? AND product_id=?",
            (delta, store_id, pid),
        )
        db.execute(
            "INSERT INTO stock_movements(store_id,product_id,user_id,delta,reason,created_at) VALUES (?,?,?,?,?,?)",
            (store_id, pid, user["id"], delta, reason, now()),
        )
        audit(
            db,
            user["id"],
            "stock.adjust",
            "product",
            pid,
            {"store_id": store_id, "delta": delta, "reason": reason},
        )
    return {"quantity": item["quantity"] + delta}
