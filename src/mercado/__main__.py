import argparse
import os
import sqlite3
from pathlib import Path

from . import create_app
from .db import connect, migrate
from .seed import seed


def main():
    parser = argparse.ArgumentParser(description="Mercado PoS · demonstração académica")
    parser.add_argument("command", choices=["init", "serve", "backup"])
    parser.add_argument(
        "--database", default=os.environ.get("POS_DATABASE", "instance/mercado.sqlite3")
    )
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--output", help="Destino de backup novo (não substitui ficheiros)")
    parser.add_argument(
        "--reference-date", help="Data ISO opcional para reproduzir a carga fictícia"
    )
    args = parser.parse_args()
    path = Path(args.database).resolve()
    if args.command == "init":
        path.parent.mkdir(parents=True, exist_ok=True)
        # Seed a temporary database, then publish it only after a successful seed.
        if path.exists():
            with connect(path) as db:
                migrate(db)
            print(f"Base de dados existente preservada: {path}")
            return
        temporary = path.with_suffix(".seed-tmp")
        if temporary.exists():
            raise SystemExit(
                "Existe uma carga interrompida .seed-tmp; escolha outro caminho ou inspecione-a."
            )
        db = connect(temporary)
        try:
            migrate(db)
            seed(db, args.reference_date)
            db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        finally:
            db.close()
        temporary.rename(path)
        print(
            f"Dados fictícios criados: {path}\n7 utilizadores, 3 lojas, 6 caixas, 48 produtos, 180 vendas."
        )
    elif args.command == "backup":
        if not path.exists() or not args.output:
            raise SystemExit("Indique uma base de dados existente e --output.")
        output = Path(args.output).resolve()
        if output.exists():
            raise SystemExit("O destino já existe; escolha um novo ficheiro.")
        output.parent.mkdir(parents=True, exist_ok=True)
        source = connect(path)
        destination = sqlite3.connect(output)
        try:
            source.backup(destination)
            assert destination.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        finally:
            source.close()
            destination.close()
        print(f"Backup verificado: {output}")
    else:
        if not path.exists():
            raise SystemExit("Execute primeiro: python -m mercado init")
        from waitress import serve

        print(f"Mercado PoS em http://127.0.0.1:{args.port}", flush=True)
        serve(create_app({"DATABASE": str(path)}), host="127.0.0.1", port=args.port, threads=4)


if __name__ == "__main__":
    main()
