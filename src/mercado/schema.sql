CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY);
INSERT OR IGNORE INTO schema_version VALUES (1);
CREATE TABLE IF NOT EXISTS stores (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL, address TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS registers (
 id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL REFERENCES stores(id), name TEXT NOT NULL,
 UNIQUE(store_id, name)
);
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','manager','cashier')),
 store_id INTEGER REFERENCES stores(id), CHECK(role='admin' OR store_id IS NOT NULL)
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
 csrf TEXT NOT NULL, expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS login_attempts (
 bucket TEXT PRIMARY KEY, attempts INTEGER NOT NULL, expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
 id INTEGER PRIMARY KEY, sku TEXT NOT NULL UNIQUE, barcode TEXT NOT NULL UNIQUE,
 name TEXT NOT NULL, category TEXT NOT NULL, emoji TEXT NOT NULL,
 price_cents INTEGER NOT NULL CHECK(price_cents>0),
 tax_rate INTEGER NOT NULL CHECK(tax_rate IN (6,13,23)), active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
);
CREATE TABLE IF NOT EXISTS inventory (
 store_id INTEGER NOT NULL REFERENCES stores(id), product_id INTEGER NOT NULL REFERENCES products(id),
 quantity INTEGER NOT NULL CHECK(quantity>=0), minimum INTEGER NOT NULL DEFAULT 10 CHECK(minimum>=0),
 PRIMARY KEY(store_id, product_id)
);
CREATE TABLE IF NOT EXISTS shifts (
 id INTEGER PRIMARY KEY, register_id INTEGER NOT NULL REFERENCES registers(id),
 user_id INTEGER NOT NULL REFERENCES users(id), opened_at TEXT NOT NULL, closed_at TEXT,
 opening_cents INTEGER NOT NULL CHECK(opening_cents>=0), counted_cents INTEGER,
 expected_cents INTEGER, difference_cents INTEGER
);
CREATE UNIQUE INDEX IF NOT EXISTS one_shift_register ON shifts(register_id) WHERE closed_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS one_shift_user ON shifts(user_id) WHERE closed_at IS NULL;
CREATE TABLE IF NOT EXISTS sales (
 id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL REFERENCES stores(id),
 shift_id INTEGER NOT NULL REFERENCES shifts(id), user_id INTEGER NOT NULL REFERENCES users(id),
 created_at TEXT NOT NULL, total_cents INTEGER NOT NULL CHECK(total_cents>0),
 tax_cents INTEGER NOT NULL CHECK(tax_cents>=0), payment TEXT NOT NULL CHECK(payment IN ('cash','card','mbway')),
 tendered_cents INTEGER NOT NULL, change_cents INTEGER NOT NULL CHECK(change_cents>=0),
 status TEXT NOT NULL DEFAULT 'completed' CHECK(status IN ('completed','voided')),
 idempotency_key TEXT NOT NULL, request_hash TEXT NOT NULL, void_reason TEXT, voided_at TEXT,
 UNIQUE(user_id, idempotency_key)
);
CREATE INDEX IF NOT EXISTS sales_store_date ON sales(store_id, created_at);
CREATE TABLE IF NOT EXISTS sale_items (
 id INTEGER PRIMARY KEY, sale_id INTEGER NOT NULL REFERENCES sales(id),
 product_id INTEGER NOT NULL REFERENCES products(id), name TEXT NOT NULL,
 quantity INTEGER NOT NULL CHECK(quantity>0), price_cents INTEGER NOT NULL CHECK(price_cents>0),
 tax_rate INTEGER NOT NULL, tax_cents INTEGER NOT NULL, total_cents INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS stock_movements (
 id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL REFERENCES stores(id),
 product_id INTEGER NOT NULL REFERENCES products(id), user_id INTEGER NOT NULL REFERENCES users(id),
 sale_id INTEGER REFERENCES sales(id), delta INTEGER NOT NULL CHECK(delta<>0),
 reason TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit (
 id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), action TEXT NOT NULL,
 entity TEXT NOT NULL, entity_id INTEGER, details TEXT NOT NULL, created_at TEXT NOT NULL
);
