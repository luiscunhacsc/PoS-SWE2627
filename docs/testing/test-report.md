# Relatório de verificação — 2026-10-01

Baseline 0.1.0. Execução local em Windows 10.0.26200, Python 3.10.7. Sem aprovação independente ou validação de cliente implícita.

| Verificação executada | Resultado real | Evidência |
|---|---|---|
| `ruff check src tests scripts` | Sem erros | [checks.log](evidence/checks.log) |
| `ruff format --check src tests scripts` | 13 ficheiros conformes | Mesmo log |
| `pytest -q --junitxml=artifacts/tests.xml` | **44 passaram**, 0 falhas, última execução registada 11,79 s | [JUnit XML](evidence/tests.xml) |
| `python scripts/e2e.py` | **8 etapas aprovadas**, Edge headless, zero erros JavaScript capturados | [E2E JSON](evidence/e2e-report.json) |
| `python scripts/benchmark.py` | Alvo local P95 <200 ms atingido nos 3 endpoints | [Benchmark JSON](evidence/benchmark.json) |
| `python -m build --no-isolation` | Wheel e sdist construídos | [Checks/build log](evidence/checks.log), `dist/` |
| `python scripts/smoke_package.py` | Wheel importado fora de src; assets/schema presentes; 180 vendas; backup íntegro e API restaurada | [Smoke JSON](evidence/package-smoke.json) |
| `python -m mercado backup --output …` | Comando CLI executado; integridade `ok` | Backup local em `instance/backup-2026-10-01.sqlite3`; smoke reproduzível acima |
| `pip-audit --no-deps --disable-pip -r requirements.txt` | **0 vulnerabilidades conhecidas**, 9 pacotes runtime | [Audit JSON](evidence/audit.json) |
| SBOM CycloneDX | Produzida para runtime | [SBOM](evidence/sbom.cdx.json) |
| `pip check` | Sem requisitos incompatíveis | Saída local: `No broken requirements found` |

## Comportamentos verificados

Login/logout/expiração/rotação, cookie e token hash; autorização por papel/loja/turno; CSRF/origem/JSON/tamanho; brute force e SQL injection; abertura/fecho exclusivos; dinheiro/IVA/troco; preços autoritativos do servidor; quantidades inválidas; stock insuficiente/esgotado; rollback integral; retry idempotente; conflito de payload; snapshots históricos; anulação única; ajustes justificados; seed/ledger e constraints.

Dois testes usam ligações simultâneas: só uma venda consegue a última unidade; retries concorrentes criam só uma venda. Isto verifica uma propriedade transacional concreta, não capacidade distribuída.

O E2E utiliza HTTP e DOM reais: admin → dashboard → caixa → numerário/troco → anulação → cartão → fecho → ajuste/movimentos → vendas/relatórios/lojas/audit → reload → viewport mobile → logout → operador com acesso limitado. A anulação do E2E restaura o numerário esperado antes do fecho. Capturas reais: [dashboard](evidence/dashboard.png), [PoS](evidence/pos.png), [talão](evidence/receipt.png), [mobile](evidence/mobile.png) e [PoS mobile](evidence/mobile-pos.png).

## Benchmark local

Cliente Flask sequencial, base seed, cinco warm-ups e cem pedidos por endpoint; sem navegador, rede ou concorrência. Catálogo: mediana 7,789 ms, P95 9,702 ms. Dashboard: mediana 7,947 ms, P95 11,311 ms. Histórico: mediana 7,330 ms, P95 8,430 ms. Estes resultados são observações do ambiente indicado, não um SLA, throughput máximo ou previsão de uma cadeia real.

## Defeitos e correções observados

O primeiro E2E falhou ao localizar um link por nome acessível exato: a seta decorativa era incluída nesse nome. Adicionou-se `aria-hidden` e repetiu-se o cenário com sucesso. A revisão adicionou logout mobile, CSRF não ASCII tratado como rejeição e datas seed sem eventos posteriores à referência. Tentativas interrompidas ou falhadas não são contadas como aprovação.

## Por verificar

CI remota no GitHub, Linux/Chromium no pipeline, revisão independente, aceitação dos requisitos pelo cliente, múltiplos browsers/tecnologias assistivas, impressão e scanner físicos, stress prolongado, disco cheio/indisponibilidade durante commit, RTO/RPO de produção e qualquer integração fiscal/bancária. Coverage de linhas não medida. Não se afirma execução de pentest, aprovação ASVS, certificação ISO ou appraisal CMMI.

## Reproduzir e preservar evidência

Seguir o [manual de instalação](../manual-installation.md). Os scripts geram resultados novos em `artifacts/` e bases de teste isoladas; `docs/testing/evidence/` é uma fotografia da entrega. Algumas capturas do cenário E2E incluem as vendas que o próprio teste criou; não correspondem exatamente à base inicial de 180 vendas. Dados de execução e salts podem variar; não exigir igualdade binária de SQLite ou capturas.
