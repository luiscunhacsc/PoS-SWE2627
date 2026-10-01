# Arquitetura

## Contexto e responsabilidades

Monólito modular com frontend HTML/CSS/JavaScript servido pela mesma aplicação que expõe a API JSON. Não há CDN nem serviço externo necessário durante a utilização. A consulta de dependências ocorre apenas na instalação/auditoria.

| Camada | Ficheiro | Responsabilidade |
|---|---|---|
| Interface | `src/mercado/templates/index.html`, `static/app.js`, `static/app.css` | Navegação, carrinho transitório, formulários, confirmação e feedback |
| HTTP / segurança | `src/mercado/__init__.py` | Contratos, sessão, CSRF, papéis, headers, erros, consultas agregadas |
| Domínio | `src/mercado/domain.py` | Dinheiro, turno, venda, anulação e ajuste; regras independentes da interface |
| Persistência | `src/mercado/db.py`, `schema.sql` | Ligações por pedido, chaves estrangeiras, WAL, transações, constraints |
| Operação | `src/mercado/__main__.py` | Init, servir via Waitress, backup consistente |
| Fixtures | `src/mercado/seed.py` | Catálogo fictício e histórico gerado através do domínio |

## Modelos editáveis

- [Contexto, containers, componentes e deployment](diagrams/system.mmd).
- [Modelo relacional](diagrams/data.mmd).
- [Sequência de venda](diagrams/checkout.mmd).
- [Estados e atividade](diagrams/states.mmd).
- [Atores e casos de uso](diagrams/use-cases.mmd).

São fontes Mermaid. Podem ser renderizadas por um editor compatível ou copiadas para uma ferramenta Mermaid; não são imagens fechadas.

## Fronteiras e invariantes

O navegador é não confiável. O servidor determina identidade e loja a partir da sessão e valida preços, quantidades, dinheiro e transições. Nenhum total enviado pelo cliente é aceite como autoridade. Uma sessão tem cookie HttpOnly e um CSRF devolvido ao seu próprio cliente; a base guarda SHA-256 do token aleatório, não o token utilizável.

Cada pedido usa uma ligação SQLite com foreign keys e timeout de 10 s. Escritas do domínio abrem `BEGIN IMMEDIATE`; conflitos aguardam o escritor anterior antes de ler o stock. Após validação, venda, linhas, stock, movimentos e audit ficam na mesma transação. Exceções fazem rollback. As duas constraints parciais de turnos reforçam exclusividade por operador e por caixa. Não há chamadas bancárias dentro da transação: os pagamentos são sempre simulações.

Chave idempotente única por utilizador e hash do conteúdo normalizado evitam duplicação em retries. Linhas repetidas são agregadas. Uma repetição idêntica devolve a venda persistida mesmo que o turno entretanto feche. Uma chave com conteúdo diferente devolve 409. O frontend conserva a chave para retry enquanto o carrinho/pagamento não mudarem, mas não conserva o carrinho após reload: ver TD-005.

As linhas do talão copiam nome, preço e taxa do catálogo no momento da venda. Alterar posteriormente o catálogo não muda talões antigos. Uma anulação não apaga a venda; altera o estado, repõe stock e acrescenta eventos. A base tem `schema_version=1`; o mecanismo atual inicializa o schema, não implementa futuras migrações incrementais.

## Dados e limites

Entidades: loja → caixa → turno → venda → linhas; utilizadores ligados a loja (exceto admin); produto ↔ loja via inventário; movimentos referem produto, loja, operador e venda opcional; audit guarda eventos; sessions e login_attempts suportam segurança.

Catálogo seed central comum às três lojas. Reposição independente por loja. Quantidades inteiras, valores monetários inteiros, sem IEEE float na contabilidade do backend. Cálculo de IVA inclusivo por linha: `round_half_up(total * taxa / (100 + taxa))` usando divisão inteira.

Datas de eventos armazenadas em ISO 8601 UTC. A interface apresenta a hora local do navegador. Os relatórios diários desta versão agrupam o dia UTC; definir calendário comercial Europe/Lisbon é uma evolução explícita antes de produção.

Consultas de histórico e audit limitadas às 200 entradas mais recentes; dashboard/relatórios agregam todos os dados do período e não usam esse limite. Ausência de paginação/exportação de histórico completo está documentada.

## Erros e observabilidade

400 validação; 401 sessão/credenciais; 403 permissão, origem ou CSRF; 404 recurso; 409 conflito de stock/estado/idempotência; 413 pedido >64 KiB; 415 formato; 429 tentativas; 503 erro operacional SQLite; 500 erro imprevisto sem stack trace no cliente. Logs locais incluem request ID, método, path, duração e status. Exceções ficam nos logs do processo; passwords e bodies não são registados.

`/health` verifica que a tabela de versão está acessível. Não equivale a monitorização de todos os subsistemas nem a um SLO medido.

## Deployment

Waitress ligado a `127.0.0.1:5000`, quatro threads, um ficheiro SQLite no disco local. O acesso de rede e HTTPS não estão pré-configurados. Não utilizar SQLite sobre um disco partilhado para simular replicação. Consultar ADRs e manual de operação para backup e opções de evolução.
