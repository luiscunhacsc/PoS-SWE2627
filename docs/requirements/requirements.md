# Requisitos e contexto — baseline 0.1.0

## 1. Visão e pressupostos

A cadeia **Mercado**, fictícia, pretende centralizar a operação das lojas e registar as vendas sem divergências de stock ou de caixa. A necessidade foi expressa pelo utilizador: criar um PoS de supermercados com dados falsos, seguindo a prompt incluída. O processo anterior não foi fornecido; a utilização de caixas isoladas é apenas uma hipótese de análise, não um facto sobre um cliente real.

Stakeholders: operador (rapidez e clareza), gerente (stock e fechos), administração (visibilidade global), manutenção (diagnóstico e recuperação) e avaliador académico (reprodutibilidade e evidências). Não foram indicadas tecnologias obrigatórias, equipa, orçamento ou data de entrega. Decisão técnica: aplicação web local, uma instância central, EUR, unidades inteiras de produtos embalados, pagamentos simulados. A instalação remota e a conformidade fiscal não fazem parte desta baseline.

Uma **necessidade** é evitar divergências; um **requisito** é rejeitar vendas sem stock; uma **regra** é que o stock nunca pode ficar negativo; uma **decisão técnica** é serializar escritas com SQLite `BEGIN IMMEDIATE`.

## 2. Requisitos funcionais

Origem U = pedido direto do utilizador; P = prompt base; A = pressuposto de domínio adotado, ainda sem validação por cliente. Prioridades Must / Should. Verificação automática refere os testes identificados na matriz.

| ID | Descrição | Prioridade / origem | Critério de aceitação | Verificação |
|---|---|---|---|---|
| REQ-F-001 | Autenticar por conta e terminar sessão | Must / P,A | Credenciais válidas dão acesso; inválidas 401; logout revoga o token | API, E2E |
| REQ-F-002 | Segregar lojas e perfis | Must / U,A | Operador/gerente só acedem à loja atribuída; admin a todas; 403 no acesso indevido | API, E2E |
| REQ-F-003 | Consultar e pesquisar catálogo | Must / U,A | Nome, SKU e código interno encontram o produto; mostra preço e stock da loja | API, E2E; pesquisa por scanner manual |
| REQ-F-004 | Abrir e fechar caixa | Must / A | Um turno aberto por operador e por caixa; fundo ≥0; fecho guarda esperado, contado e diferença | API, E2E |
| REQ-F-005 | Concluir uma venda | Must / U | Carrinho não vazio; preços do servidor; talão e redução de stock persistem juntos | API, E2E |
| REQ-F-006 | Simular pagamentos e calcular troco | Must / A | Numerário suficiente; troco exato; cartão/MB WAY não aumentam numerário esperado | API, E2E |
| REQ-F-007 | Consultar e imprimir talão | Must / A | Talão conserva nome/preço/IVA à data da compra e identifica ausência de valor fiscal | API, E2E; impressão física pendente |
| REQ-F-008 | Anular integralmente uma venda | Must / A | Gerente/admin, motivo ≥5 caracteres e turno aberto; reposição única; histórico conservado | API, E2E |
| REQ-F-009 | Ajustar stock com justificação | Must / A | Gerente/admin; delta inteiro não nulo; stock final ≥0; movimento e auditoria persistidos | API, E2E |
| REQ-F-010 | Mostrar vendas e relatórios | Should / U,A | Até 200 vendas recentes; dashboard diário e série de 7 dias; exclui anuladas dos agregados | API, E2E |
| REQ-F-011 | Consultar auditoria | Must / P | Admin vê até 200 eventos; outros perfis recebem 403 | API, E2E |
| REQ-F-012 | Criar base de demonstração | Must / U | 3 lojas, 6 caixas, 48 produtos, 7 utilizadores, 180 vendas; sem duplicação no segundo seed | Integração |
| REQ-F-013 | Fazer backup consistente | Must / P | Novo ficheiro SQLite com integridade válida e dados preservados | Integração, CLI |

## 3. Qualidade, segurança e restrições

| ID | Requisito / origem P | Alvo e critério | Método |
|---|---|---|---|
| REQ-NF-001 | Integridade transacional | Zero vendas parciais; zero stock negativo; duas compras da última unidade dão um sucesso | Teste concorrente com ligações independentes |
| REQ-NF-002 | Idempotência | Repetição da mesma chave e conteúdo produz o mesmo ID; conteúdo diferente dá 409 | API e teste concorrente |
| REQ-NF-003 | Desempenho local | P95 <200 ms em 100 leituras sequenciais por endpoint, dados seed, cliente Flask sem rede | `scripts/benchmark.py`; não é um SLA de produção |
| REQ-NF-004 | Reprodutibilidade | Instalação documentada, dependências fixadas, 100% da suite passar, wheel construível | `scripts/check.py`, manuais, CI configurado |
| REQ-NF-005 | Utilização responsiva e teclado | PoS e dashboard sem overflow de página a 390 px; formulários rotulados e diálogos com foco | E2E e inspeção; auditoria WCAG integral pendente |
| REQ-NF-006 | Observabilidade | Health endpoint verifica schema; pedidos registam duração/status/request_id sem passwords | API e inspeção de logs |
| REQ-SEC-001 | Sessão e passwords | Hash adaptativo scrypt no seed; token aleatório só guardado como hash; expiração em 8h; logout revoga | Testes e inspeção |
| REQ-SEC-002 | Proteção de escritas | JSON + CSRF + verificação Origin; SQL parametrizado; CSP e escape de texto | Testes de CSRF, origem, SQL injection e headers |
| REQ-SEC-003 | Limitar abuso de login | 5 tentativas por par IP/utilizador em 5 minutos; tentativa seguinte 429 | API |
| REQ-SEC-004 | Minimização de dados | Sem identificação de clientes ou dados de cartão; apenas perfis fictícios no seed | Inspeção do schema/seed |

## 4. Regras de negócio

| ID | Regra |
|---|---|
| RN-001 | Dinheiro em cêntimos inteiros. Preço inclui IVA demonstrativo. IVA por linha com arredondamento half-up; soma das linhas forma o talão. |
| RN-002 | Quantidade inteira de 1 a 999 por produto, até 100 linhas de entrada. Linhas repetidas agregadas antes de validar o stock. |
| RN-003 | Stock é por loja e nunca negativo. Uma venda, linhas, movimentos e auditoria formam uma transação. |
| RN-004 | Venda pertence ao turno aberto do operador autenticado. Um operador não pode usar o turno de outro. |
| RN-005 | Numerário esperado = fundo inicial + total das vendas em numerário não anuladas. O troco já foi descontado através do total líquido da venda. |
| RN-006 | Turno fechado é terminal. Anulação após fecho, anulação repetida e fecho repetido são rejeitados. |
| RN-007 | Anulação integral mantém a venda original, exige motivo e repõe todas as unidades; não cria um reembolso bancário. |
| RN-008 | Cada (operador, chave de idempotência) identifica uma tentativa lógica de venda. Repetições com conteúdo diferente não são aceites. |
| RN-009 | Gerente limita-se à sua loja; só o admin consulta auditoria global. Operadores consultam o histórico de vendas da sua loja. |
| RN-010 | Produtos são unidades/embalagens; produtos vendidos a peso ficam fora de âmbito. Valores e taxas seed não são um catálogo fiscal validado. |

## 5. Casos de uso e backlog

| Caso | História / fluxo principal | Alternativas / erros | Incremento |
|---|---|---|---|
| UC-01 | Como operador entro, abro caixa com fundo e escolho artigos | Login inválido, caixa ocupada, produto esgotado | I1/I2 |
| UC-02 | Como operador cobro, entrego troco e consulto talão | Falta de stock, numerário insuficiente, repetição de pedido | I2 |
| UC-03 | Como gerente anulo um erro e justifico | Perfil sem permissão, turno fechado, venda já anulada | I2 |
| UC-04 | Como operador conto numerário e fecho o meu turno | Diferença registada; não pode fechar turno alheio | I2 |
| UC-05 | Como gerente registo uma reposição e consulto movimentos | Ajuste negativo excessivo, motivo curto | I3 |
| UC-06 | Como administrador comparo lojas e consulto eventos | Loja inexistente, acesso indevido de outro perfil | I3 |
| UC-07 | Como avaliador crio dados seed, executo testes e recupero backup | DB já existe: preservar; destino backup já existe: rejeitar | I4 |

Musts implementados na baseline. Should F-010 implementado. Backlog futuro por ordem: qualificar requisitos fiscais/pagamentos; administração de contas e catálogo; devoluções com documento próprio; PostgreSQL e migrações; integração de periféricos; promoções e fidelização; offline e sincronização. Ver dívida técnica para justificação.

Glossário: **PoS** = ponto de venda; **caixa** = posto físico representado por register; **turno** = sessão de operação e apuramento; **talão** = comprovativo demonstrativo; **SKU** = código interno de artigo; **anulação** = reversão integral dentro de turno aberto; **seed** = carga inicial fictícia.
