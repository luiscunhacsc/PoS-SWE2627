# Threat model — STRIDE

Escopo: browser → Flask/Waitress → SQLite e backups. Uso local por contas fictícias. Revisão de design, não pentest. A classificação assume impacto alto para alterações financeiras e de stock; probabilidade de exploração não foi medida.

| Categoria | Ameaça / ativo | Controlo implementado | Evidência | Residual / futuro |
|---|---|---|---|---|
| Spoofing | Roubo/reutilização de sessão; login por força bruta | Tokens aleatórios hashed, cookie HttpOnly, expiração, logout, hash password, rate limit | `test_cookie_logout_and_expiry`, `test_login_rate_limit_and_sql_injection` | MFA/TLS real e rate limit distribuído pendentes |
| Tampering | Alterar preços, quantidades, loja ou stock via JSON | Preço no servidor, validação, RBAC, SQL parametrizado, constraints | `test_client_cannot_override_price`, `test_store_and_role_boundaries`, `test_database_constraints` | Escrita direta no disco está fora do controlo HTTP |
| Repudiation | Negar anulação/ajuste; apagar rastos | Audit de ações com utilizador e motivo, histórico conservado | `test_sale_receipt_stock_cash_and_audit`, `test_stock_adjustment_and_negative_guard` | Sem assinatura de logs/armazenamento imutável |
| Information disclosure | Ver vendas de outra loja; tokens em resposta/log | Autorização de objetos e lojas, resposta sem password hash, logs sem bodies | `test_store_and_role_boundaries`, `test_session_token_hashed_and_password_not_exposed` | Backup/disco não cifrado pela aplicação |
| Denial of service | Login caro, payload grande, contenção de writer | Limite 64 KiB, throttling de login, timeout SQL, queries limitadas | `test_payload_limit`, rate limit, benchmark | Sem load test distribuído, quota global ou alta disponibilidade |
| Elevation of privilege | Operador executar gestão; CSRF usar sessão alheia | RBAC servidor + CSRF + Origin + JSON + CSP | `test_csrf_origin_and_json`, `test_manager_scope_and_invalid_store` | Sem auditoria ASVS integral; XSS exige revisão contínua |

Casos críticos específicos: duas vendas da última unidade, retry simultâneo do mesmo pedido, anulação repetida, turno fechado e venda parcial. Os testes de concorrência usam threads e ligações SQLite distintas. Não simulam múltiplos datacenters ou adquirentes bancários.

Correspondência orientativa OWASP: broken access control → lojas/papéis; injection → queries parametrizadas; authentication failures → sessões e rate limit; insecure design → regras transacionais; security misconfiguration → headers/loopback; vulnerable components → audit; logging failures → request IDs e audit. Sem alegação de cumprir integralmente qualquer edição do ASVS/Top 10/API Top 10.
