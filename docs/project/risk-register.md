# Registo de riscos

Escalas de probabilidade (P) e impacto (I): 1 baixo, 2 médio, 3 alto. Exposição E=P×I é avaliação qualitativa, não frequência estatística. Responsáveis abaixo são funções a atribuir pela equipa, não pessoas ficticiamente nomeadas.

| ID | Descrição / causa | P | I | E | Responsável | Estratégia e mitigação | Contingência | Estado |
|---|---|---|---|---|---|---|---|---|
| R-01 | Uso real de simulação sem faturação/pagamento apropriado | 2 | 3 | 6 | Dono de produto | Evitar: delimitação, talão sem valor fiscal, sem cobrança | Suspender uso e integrar solução validada | Aberto, fora do âmbito real |
| R-02 | Perda de dados por falha do disco central | 2 | 3 | 6 | Operação | Reduzir: backup consistente verificado | Servir cópia íntegra e reconciliar vendas | Parcialmente mitigado; backup remoto pendente |
| R-03 | Venda repetida ou overselling por concorrência | 2 | 3 | 6 | Backend | Reduzir: locks, transações, idempotência, testes simultâneos | Consultar histórico antes de nova tentativa manual | Mitigado nos cenários testados |
| R-04 | Conta seed exposta fora de loopback | 2 | 3 | 6 | Segurança | Evitar: listener local e aviso demo; não reutilizar passwords | Parar serviço e revogar sessões | Aberto para deployment externo |
| R-05 | Cliente falsificar loja/preço/quantidade | 2 | 3 | 6 | Backend | Reduzir: autorização e cálculo servidor | Audit e correção de defeito | Mitigado por testes |
| R-06 | Instalação falhar sem rede ou Python compatível | 2 | 2 | 4 | Manutenção | Reduzir: versões fixadas e manuais | Preparar wheelhouse offline | Rede necessária na primeira instalação |
| R-07 | Contenção SQLite sob carga não medida | 2 | 3 | 6 | Arquitetura | Aceitar no protótipo: timeout/WAL, benchmark delimitado | Migrar para PostgreSQL | Aberto para produção |
| R-08 | Requisitos presumidos não refletirem trabalho real | 3 | 2 | 6 | Dono de produto | Reduzir: pressupostos, guião AC, backlog | Rever baseline após entrevistas | Validação de cliente pendente |
| R-09 | Falta de acessibilidade/periféricos no balcão | 2 | 2 | 4 | UX/QA | Reduzir: labels, foco, responsive, E2E | Testar hardware e tecnologia assistiva | Parcialmente mitigado |
| R-10 | Dependência ou action comprometida | 2 | 3 | 6 | Manutenção | Reduzir: pins, audit, SBOM, Dependabot | Bloquear release, corrigir pin e rebuild | Hashes/actions SHA pendentes |
| R-11 | Alteração direta da BD adulterar auditoria | 2 | 3 | 6 | Operação | Reduzir: acesso SO restrito, não publicar DB | Preservar backup e investigar | Logs imutáveis futuros |

Rever riscos a cada alteração de contexto, integração, deployment ou entrada de dados reais. Sem reunião de aprovação ou aceitação formal inventada.
