# Métricas — baseline 0.1.0

Data de recolha: 2026-10-01. Ambiente Windows 10.0.26200, Python 3.10.7. Fontes e condições completas em [test-report](../testing/test-report.md).

| Métrica | Alvo | Resultado observado | Evidência |
|---|---|---|---|
| Suite automática | 100% passar | 44/44, zero falhas | `testing/evidence/tests.xml` |
| Cenário E2E | 8 etapas sem falha | 8 concluídas, zero erros JavaScript capturados | `testing/evidence/e2e-report.json` |
| Leitura catálogo P95 | <200 ms local | 9,702 ms | `testing/evidence/benchmark.json` |
| Leitura dashboard P95 | <200 ms local | 11,311 ms | Mesmo JSON |
| Leitura vendas P95 | <200 ms local | 8,430 ms | Mesmo JSON |
| Vulnerabilidades runtime conhecidas | 0 na consulta | 0 nas 9 distribuições fixadas | `testing/evidence/audit.json` |
| Stock negativo / venda duplicada | 0 nos cenários críticos | 0 nos testes última unidade/retry | Suite pytest |
| Integridade seed | 3 lojas / 48 produtos / 180 vendas | Contagens corretas e ledger reconciliado | Teste seed + SQLite checks |
| Build e análise | Sem erros | Ruff e wheel/sdist aprovados localmente | `testing/evidence/checks.log` |
| CI remoto | Passar antes de release | Não executado nesta sessão | Workflow configurado |
| Aceitação de cliente | Aprovação registada | Pendente | Guião AC-01…10 |
| Coverage de linhas | Não definida como gate isolado | Não medida | Não se infere a partir do número de testes |

O benchmark mede cliente Flask no mesmo processo, sem rede nem carga concorrente. Estes valores não são capacidade comercial ou SLA. O scan é uma fotografia do conhecimento público na data de consulta, não uma garantia de ausência de vulnerabilidades. Não há série temporal de builds, defeitos ou produtividade de uma equipa.
