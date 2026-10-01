# ADR-001 — Monólito modular local

Estado: aceite para baseline académica 0.1.0. Data: 2026-10-01.

Contexto: pasta inicial sem código, utilizador em Windows, sem stack obrigatória; prioridade a um fluxo completo e reproduzível. Alternativas: React/Node/PostgreSQL (mais tooling e serviços); desktop (instalação por posto); microserviços (complexidade distribuída sem necessidade demonstrada).

Decisão: Flask + JavaScript sem framework + SQLite + Waitress. Domínio separado do HTTP. Dependências runtime fixadas. Waitress é documentado pelo Flask como opção compatível com Windows: [documentação oficial](https://flask.palletsprojects.com/en/stable/deploying/waitress/).

Consequências: instalação pequena, sem build frontend, teste local acessível. SQLite tem um escritor de cada vez; [documentação de transações](https://www.sqlite.org/lang_transaction.html). Adotam-se WAL, timeout e `BEGIN IMMEDIATE`. Não se assume escala de produção. PostgreSQL será a alternativa para distribuição/concor­rência real. A ausência de framework frontend facilita inspeção, mas aumenta o custo de evolução de estado e componentes.

Riscos: indisponibilidade da instância central; falta de offline; nenhum benchmark de rede de várias lojas. Mitigação presente: atomicidade, testes de concorrência e backup. Mitigação futura: PostgreSQL, observabilidade e testes de carga no ambiente alvo.
