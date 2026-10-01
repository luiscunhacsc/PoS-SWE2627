"""Verify that the built wheel runs outside src, and a restored backup can serve requests."""

import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def main():
    wheel = next(Path("dist").glob("mercado_pos-*.whl"))
    with tempfile.TemporaryDirectory(prefix="mercado-wheel-") as temporary:
        package = Path(temporary) / "package"
        with zipfile.ZipFile(wheel) as archive:
            archive.extractall(package)
        # Run a fresh process: imports must resolve the unpacked wheel first.
        code = """
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import mercado
from mercado.db import connect, migrate
from mercado.seed import seed
assert Path(mercado.__file__).resolve().is_relative_to(Path(sys.argv[1]).resolve())
path = str(Path(sys.argv[2])/'fresh.sqlite3')
db = connect(path)
migrate(db)
seed(db, '2026-10-01')
backup = str(Path(sys.argv[2])/'restored.sqlite3')
target = connect(backup)
db.backup(target)
assert target.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
assert target.execute('PRAGMA foreign_key_check').fetchall() == []
assert target.execute('SELECT COUNT(*) FROM sales').fetchone()[0] == 180
target.close()
db.close()
app = mercado.create_app({'DATABASE':backup})
app.logger.disabled = True
client = app.test_client()
assert client.get('/health').status_code == 200
assert client.get('/').status_code == 200
assert client.get('/static/app.js').status_code == 200
assert client.get('/static/app.css').status_code == 200
assert client.post('/api/login',json={'username':'admin','password':'Demo2026!'}).status_code == 200
assert len(client.get('/api/stores').json) == 3
assert len(client.get('/api/products?store_id=1').json) == 48
assert len(client.get('/api/sales?store_id=1').json) == 60
print(json.dumps({'status':'passed','wheel_import':'isolated from src','seed_sales':180,'backup_integrity':'ok','restored_api':'passed','bundled_assets':'passed'}))
"""
        result = subprocess.run(
            [sys.executable, "-c", code, str(package), temporary],
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(result.stdout)
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/package-smoke.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
