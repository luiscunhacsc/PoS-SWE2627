# Dívida técnica e evolução

| ID | Problema e razão para adiamento | Impacto / prioridade | Estratégia futura |
|---|---|---|---|
| TD-001 | Integração fiscal/bancária sem requisitos ou credenciais | Impede uso comercial real / P0 | Elicitar e validar obrigações e contratos; estados de pagamento e reconciliação; solução de faturação adequada |
| TD-002 | Credenciais públicas seed; falta de gestão de identidades | Impede utilizadores reais / P0 | Provisioning, política de password, reset, MFA, desativação e audit |
| TD-003 | HTTP local e ficheiro DB sem cifragem aplicacional | Exposição se indevidamente publicado / P0 | TLS, controlo de rede/disco, vault, monitorização e backups protegidos |
| TD-004 | SQLite central e um escritor; sem alta disponibilidade | Limita distribuição/concorrência / P1 | PostgreSQL, migrations, testes de carga/falha e plano de continuidade |
| TD-005 | Carrinho e chave retry apenas em memória do browser | Reload perde intenção; nova tentativa manual pode ser nova venda / P1 | Draft persistente por caixa, recuperação de transação incerta e UX de reconciliação |
| TD-006 | Sem produtos a peso, promoções, devoluções parciais ou pagamentos repartidos | Limita domínio de supermercado real / P1 | Novos requisitos, unidades decimais, documentos de devolução, regras e testes |
| TD-007 | Dias dos relatórios em UTC | Fronteira do dia pode diferir de Portugal / P1 | Calendário comercial configurável, DST e testes de fronteira Europe/Lisbon |
| TD-008 | Histórico/movimentos/audit limitados a 200 sem paginação/exportação | Navegação antiga limitada / P2 | Paginação por cursor, filtros e exportação controlada |
| TD-009 | Catálogo/utilizadores definidos na carga inicial | Administração fora da UI / P1 | CRUD validado, desativação e preços versionados auditados |
| TD-010 | Esquema v1 sem migrações incrementais | Dificulta evolução segura / P1 | Migrações ordenadas, testes de upgrade/rollback e backup automático |
| TD-011 | Auditoria modificável por acesso direto ao disco | Não resiste a administrador malicioso / P1 | Logs externos, retenção e mecanismos de deteção de alteração |
| TD-012 | Frontend único app.js, sem suíte unitária JS | Custo de evolução do estado / P2 | Extrair módulos quando crescer; preservar E2E e adicionar testes de estado críticos |
| TD-013 | Sem auditoria WCAG integral ou validação com operadores reais | Usabilidade real não demonstrada / P1 | Testes assistivos, contraste/touch targets e ensaios com utilizadores |
| TD-014 | CI não executada remotamente; actions por tags, locks sem hashes | Evidência remota/supply chain incompleta / P1 | Publicar, fixar actions por SHA, hashes de pacotes, revisão de dependências de desenvolvimento |
| TD-015 | Sem Docker nesta baseline | Ambiente alvo contentorizado não reproduzido / P2 | Criar imagem após escolha de deployment; instalação venv/wheel já documentada |
| TD-016 | Simulação histórica usa um turno consolidado por loja | Não reproduz escalas reais de operadores / P2 | Gerador de turnos diários; dados atuais mantêm ledger consistente |

P0 deve ser resolvido antes de dados/recebimentos reais. A ordenação não é uma promessa de implementação. Nenhum item é ocultado sob uma alegação de produto pronto para produção.
