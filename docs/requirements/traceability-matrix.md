# Matriz de rastreabilidade

Resultado local da baseline: testes da suite e cenário E2E aprovados, conforme [relatório](../testing/test-report.md). “Inspeção” não significa teste automático; pendências são explícitas. Os nomes abaixo são pesquisáveis em `tests/` com `rg`.

| Requisito / regra | Caso | Componente / implementação | Evidência / teste | Estado |
|---|---|---|---|---|
| F-001, SEC-001 | UC-01 | `__init__.py`: login/authentication/logout | `test_authentication_and_security_headers`, `test_cookie_logout_and_expiry`, `test_relogin_revokes_previous_token`, E2E | Verificado |
| F-002, RN-009 | UC-01/06 | `domain.py`: authorize_store/manager; endpoints | `test_store_and_role_boundaries`, `test_manager_scope_and_invalid_store`, E2E operador | Verificado |
| F-003 | UC-01 | products endpoint; `app.js`: renderProducts | E2E pesquisa/adicionar leite; API catálogo; scanner físico pendente | Parcialmente validado |
| F-004, RN-004/005/006 | UC-01/04 | open_shift/close_shift/shift_totals; índices SQL | `test_shift_unique_and_reopen`, `test_closed_shift_blocks_sale_void_and_double_close`, E2E | Verificado |
| F-005, RN-001/002/003 | UC-02 | checkout/tax_included; sale_items/inventory | `test_sale_receipt_stock_cash_and_audit`, `test_tax_rounding`, `test_invalid_sale_no_side_effects`, `test_duplicate_lines_aggregate_before_stock_check` | Verificado |
| F-006 | UC-02 | checkout; paymentModal | `test_electronic_payments_do_not_change_cash`, teste cash, E2E troco | Verificado; integração real excluída |
| F-007 | UC-02 | receipt/displayReceipt, CSS print | `test_snapshot_receipt_is_immutable`; captura real receipt | Talão verificado; impressão física pendente |
| F-008, RN-007 | UC-03 | void_sale | `test_void_once_restock_and_reporting`, teste turno fechado, E2E | Verificado |
| F-009, RN-003 | UC-05 | adjust_stock; movements | `test_stock_adjustment_and_negative_guard`, E2E ajuste/movimento | Verificado |
| F-010 | UC-06 | dashboard/sales endpoints; renderReports | Exclusão de anuladas em teste; navegação E2E; benchmark leituras | Verificado no âmbito dos cenários |
| F-011 | UC-06 | audit/audit_list | teste stock/audit, acesso por papéis, E2E | Verificado |
| F-012 | UC-07 | seed.py, CLI init | `test_seed_repeatable_counts_and_stock_ledger`; execução CLI inicial | Verificado |
| F-013 | UC-07 | CLI backup; SQLite backup API | teste seed/backup e backup CLI restaurado em smoke | Verificado localmente |
| NF-001 | UC-02 | transaction, BEGIN IMMEDIATE, SQL constraints | `test_all_or_nothing_on_second_line`, `test_concurrent_last_unit_not_oversold`, `test_database_constraints` | Verificado |
| NF-002, RN-008 | UC-02 | unique key + fingerprint; frontend pendingSale | `test_idempotency_and_changed_payload`, `test_concurrent_retry_creates_one_sale` | Verificado API; recuperação pós-reload futura |
| NF-003 | UC-06 | queries de leitura, índices | `scripts/benchmark.py`, `evidence/benchmark.json` | Verificado no ambiente local |
| NF-004 | UC-07 | requirements*, setup, build, CI | `scripts/check.py`, wheel, manuais | Local verificado; CI remoto pendente |
| NF-005 | Todos | HTML labels/dialogs, CSS responsive | E2E 390 px e screenshots; correção do nome acessível da navegação | Parcial; WCAG integral pendente |
| NF-006 | Operação | health, after_request logging | Teste health + logs E2E inspecionados | Verificado localmente |
| SEC-002 | Escritas | authentication, body, parameterized SQL | `test_csrf_origin_and_json`, injection, headers | Verificado nos ataques testados |
| SEC-003 | UC-01 | login_attempts | `test_login_rate_limit_and_sql_injection` | Verificado |
| SEC-004 | Seed | schema e seed sem clientes/cartões | Inspeção de schema/seed; security.md | Verificado por inspeção |
| RN-010 | UC-02 | integer + catálogo embalado | Validações zero/float/bool e declaração de âmbito | Verificado |

Prefixos F-, NF- e SEC- nesta tabela correspondem a REQ-F-, REQ-NF- e REQ-SEC-. Para impacto de alteração: começar pelo requisito, localizar regra/domínio/schema, atualizar teste associado, API/interface e manual, e registar ADR se mudar a arquitetura. Resultados são verificações do código, não aprovação de requisitos por cliente.
