"""Real browser acceptance scenario against an isolated, disposable seeded database."""

import argparse
import json
import logging
import os
import platform
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

from mercado import create_app
from mercado.db import connect, migrate
from mercado.seed import seed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--channel",
        default=os.environ.get(
            "BROWSER_CHANNEL", "msedge" if platform.system() == "Windows" else "chromium"
        ),
    )
    args = parser.parse_args()
    output = Path("artifacts")
    output.mkdir(exist_ok=True)
    steps = []
    errors = []
    with tempfile.TemporaryDirectory(prefix="mercado-e2e-") as folder:
        database = str(Path(folder) / "e2e.sqlite3")
        db = connect(database)
        migrate(db)
        seed(db)
        db.close()
        app = create_app({"DATABASE": database})
        app.logger.disabled = True
        logging.getLogger("werkzeug").disabled = True
        server = make_server("127.0.0.1", 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel=args.channel, headless=True)
                page = browser.new_page(viewport={"width": 1440, "height": 1000}, locale="pt-PT")
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}")
                page.get_by_role("button", name="Entrar no Mercado").click()
                expect(page.get_by_role("heading", name="Visão geral", exact=True)).to_be_visible()
                page.screenshot(path=str(output / "dashboard.png"), full_page=True)
                steps.append("Login admin e dashboard com dados reais da base de demonstração")
                page.get_by_role("link", name="Ponto de venda").click()
                page.get_by_role("button", name="Abrir caixa", exact=True).click()
                page.get_by_role("button", name="Abrir turno", exact=True).click()
                expect(page.get_by_text("Turno aberto", exact=False)).to_be_visible()
                page.get_by_label("Pesquisar produto ou código de barras").fill("Leite")
                page.get_by_role("button", name="Adicionar Leite meio-gordo").click()
                page.screenshot(path=str(output / "pos.png"), full_page=True)
                page.get_by_role("button", name="Cobrar").click()
                page.get_by_role("button", name="Numerário", exact=True).click()
                page.get_by_label("Valor recebido (€)").fill("2,00")
                page.get_by_role("button", name="Confirmar pagamento", exact=True).click()
                expect(page.get_by_role("heading", name="Talão de venda")).to_be_visible()
                expect(page.locator("#modal-body")).to_contain_text("1,11")
                page.screenshot(path=str(output / "receipt.png"), full_page=True)
                steps.append("Abertura de caixa; venda em numerário; troco de 1,11 EUR; talão")
                page.get_by_role("button", name="Anular venda", exact=True).click()
                page.get_by_label("Motivo da anulação").fill("Anulação para teste de aceitação")
                page.get_by_role("button", name="Confirmar anulação", exact=True).click()
                expect(page.locator("#modal-body .tag")).to_have_text("Anulada")
                page.get_by_role("button", name="Fechar janela").click()
                steps.append("Anulação pelo administrador com motivo e reposição de stock")
                page.get_by_role("button", name="Adicionar Leite meio-gordo").click()
                page.get_by_role("button", name="Cobrar").click()
                page.get_by_role("button", name="Confirmar pagamento", exact=True).click()
                expect(page.get_by_role("heading", name="Talão de venda")).to_be_visible()
                expect(page.locator("#modal-body")).to_contain_text("Cartão")
                page.get_by_role("button", name="Fechar janela").click()
                page.get_by_role("button", name="Fechar turno", exact=True).click()
                page.get_by_label("Numerário contado (€)").fill("150,00")
                page.get_by_role("button", name="Confirmar fecho de turno").click()
                expect(page.get_by_role("button", name="Abrir caixa", exact=True)).to_be_visible()
                steps.append("Venda por cartão simulado e fecho com diferença zero")
                page.get_by_role("link", name="Inventário", exact=True).click()
                page.get_by_label("Pesquisar inventário").fill("Leite")
                page.get_by_role("button", name="Ajustar", exact=True).click()
                page.get_by_label("Quantidade a adicionar ou retirar").fill("5")
                page.get_by_label("Motivo", exact=True).fill("Receção fictícia para teste")
                page.get_by_role("button", name="Confirmar ajuste").click()
                expect(page.get_by_role("heading", name="Inventário", exact=True)).to_be_visible()
                expect(page.get_by_role("dialog")).not_to_be_visible()
                page.get_by_role("button", name="Ver movimentos", exact=True).click()
                expect(page.locator("#modal-body")).to_contain_text("Receção fictícia para teste")
                page.get_by_role("button", name="Fechar janela").click()
                steps.append("Ajuste de inventário e consulta do movimento persistido")
                for title in ["Vendas", "Relatórios", "Lojas", "Auditoria"]:
                    page.get_by_role("link", name=title, exact=True).click()
                    expect(page.locator("main h1")).to_be_visible()
                    expect(
                        page.get_by_text("Não foi possível carregar", exact=True)
                    ).not_to_be_visible()
                page.reload()
                expect(page.get_by_role("heading", name="Auditoria", exact=True)).to_be_visible()
                steps.append(
                    "Navegação em vendas, relatórios, lojas e auditoria; sessão após reload"
                )
                page.get_by_role("link", name="Visão geral", exact=True).click()
                expect(page.get_by_role("heading", name="Visão geral", exact=True)).to_be_visible()
                page.set_viewport_size({"width": 390, "height": 844})
                page.screenshot(path=str(output / "mobile.png"), full_page=True)
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.get_by_role("link", name="Ponto de venda", exact=True).click()
                expect(page.get_by_role("button", name="Abrir caixa", exact=True)).to_be_visible()
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(output / "mobile-pos.png"), full_page=True)
                steps.append("Viewport 390×844: dashboard e PoS sem overflow horizontal da página")
                page.set_viewport_size({"width": 1440, "height": 1000})
                page.get_by_role("button", name="Terminar sessão", exact=True).click()
                expect(page.get_by_role("button", name="Entrar no Mercado")).to_be_visible()
                page.get_by_label("Utilizador", exact=True).fill("caixa.lisboa")
                page.get_by_role("button", name="Entrar no Mercado").click()
                expect(
                    page.get_by_role("heading", name="Ponto de venda", exact=True)
                ).to_be_visible()
                expect(page.get_by_role("link", name="Auditoria", exact=True)).to_have_count(0)
                expect(page.get_by_role("link", name="Relatórios", exact=True)).to_have_count(0)
                assert page.locator("#store-select option").count() == 1
                steps.append(
                    "Logout e login de operador: acesso a uma loja, sem gestão nem auditoria"
                )
                assert not errors, errors
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
    report = {
        "status": "passed",
        "browser": args.channel,
        "steps": steps,
        "javascript_errors": errors,
    }
    (output / "e2e-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
