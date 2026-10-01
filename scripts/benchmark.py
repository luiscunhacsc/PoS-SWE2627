"""Local sequential API benchmark; not a production load certification."""

import json
import platform
import statistics
import tempfile
import time
from pathlib import Path

from mercado import create_app
from mercado.db import connect, migrate
from mercado.seed import seed


def main():
    with tempfile.TemporaryDirectory(prefix="mercado-bench-") as folder:
        path = str(Path(folder) / "benchmark.sqlite3")
        db = connect(path)
        migrate(db)
        seed(db)
        db.close()
        app = create_app({"DATABASE": path, "TESTING": True})
        app.logger.disabled = True
        client = app.test_client()
        assert (
            client.post(
                "/api/login", json={"username": "admin", "password": "Demo2026!"}
            ).status_code
            == 200
        )
        results = {}
        for endpoint in [
            "/api/products?store_id=1",
            "/api/dashboard?store_id=1",
            "/api/sales?store_id=1",
        ]:
            for _ in range(5):
                assert client.get(endpoint).status_code == 200
            samples = []
            for _ in range(100):
                start = time.perf_counter()
                assert client.get(endpoint).status_code == 200
                samples.append((time.perf_counter() - start) * 1000)
            results[endpoint] = {
                "requests": 100,
                "median_ms": round(statistics.median(samples), 3),
                "p95_ms": round(sorted(samples)[94], 3),
            }
        report = {
            "environment": platform.platform(),
            "python": platform.python_version(),
            "method": "Flask test client, sequential, 5 warm-ups then 100 reads, demo database",
            "target_p95_ms": 200,
            "results": results,
        }
        Path("artifacts").mkdir(exist_ok=True)
        Path("artifacts/benchmark.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
