# ADR-002 — Dinheiro, transações e fronteira de demonstração

Estado: aceite, 2026-10-01.

Contexto: vendas implicam stock, dinheiro e um talão consistente. Duplicar uma cobrança após timeout seria um erro grave. Não foram fornecidas credenciais bancárias nem requisitos de faturação.

Alternativas: floats (simples, introduzem erros de arredondamento); Decimal (adequado, mais conversões); cêntimos inteiros (adequado a EUR e unidades inteiras). Para pagamentos: integração real, mocks externos ou simulação local explícita.

Decisão: cêntimos inteiros e IVA inclusivo half-up por linha; preço sempre no servidor; transação única com locks SQLite; idempotência por operador/chave/hash. Cartão e MB WAY são simulações locais. Talões identificados como sem valor fiscal. Anulações apenas em turnos abertos, preservando o histórico.

Consequências: cálculo exato e rollback verificável. Sem taxas cambiais, produtos a peso ou pagamento repartido. Não há certificação fiscal nem evidência de conformidade tributária. Integrar um banco exigirá estados pendente/confirmado/falhado, reconciliação, callbacks autenticados e tratamento de falhas parciais fora da transação SQL. Não se promete que a atual API seja um adaptador bancário pronto.
