# API HTTP — v0.1.0

Base local: `http://127.0.0.1:5000`. API JSON em `/api`. UTF-8, same-origin, sem CORS. Login cria cookie `pos_session`, HttpOnly, SameSite Strict, validade 8h. Reutilizar o cookie e enviar `X-CSRF-Token` em todos os POST autenticados; obtém-se o CSRF no login ou em `/api/me`. Enviar `Content-Type: application/json`, inclusive no logout.

| Método / caminho | Permissão | Entrada / resultado |
|---|---|---|
| GET `/health` | Público | `status`, `version`; verifica acesso ao schema |
| POST `/api/login` | Público | `{username,password}` → `{csrf}` e cookie |
| POST `/api/logout` | Autenticado | `{}` → `{ok:true}`; revoga cookie no servidor |
| GET `/api/me` | Autenticado | `id,name,username,role,store_id,csrf` |
| GET `/api/stores` | Autenticado | Array de lojas acessíveis com caixas e ocupação |
| GET `/api/products?store_id=1` | Loja autorizada | Array: catálogo ativo, preço, taxa, quantidade e mínimo |
| GET `/api/shifts/current` | Autenticado | Turno do próprio operador ou `null`; inclui esperado em caixa |
| POST `/api/shifts` | Loja autorizada | `{register_id,opening_cents}` → `{id}`, 201 |
| POST `/api/shifts/{id}/close` | Dono do turno | `{counted_cents}` → `expected_cents,counted_cents,difference_cents` |
| POST `/api/sales` | Dono do turno aberto | Payload abaixo → snapshot do talão, 201 |
| GET `/api/sales?store_id=1` | Loja autorizada | Até 200 vendas recentes, incluindo anuladas |
| GET `/api/sales/{id}` | Loja autorizada | Talão com linhas históricas |
| POST `/api/sales/{id}/void` | Gerente/admin da loja | `{reason}` → talão anulado; turno original deve estar aberto |
| POST `/api/inventory/adjust` | Gerente/admin da loja | `{store_id,product_id,delta,reason}` → `{quantity}` |
| GET `/api/inventory/movements?store_id=1` | Gerente/admin da loja | Até 200 movimentos recentes |
| GET `/api/dashboard?store_id=1` | Gerente/admin da loja | Totais de hoje, série, ranking e pagamentos de 7 dias |
| GET `/api/audit` | Admin | Até 200 eventos globais recentes |

Exemplo de venda, após abrir o turno correspondente:

```json
{
  "shift_id": 4,
  "idempotency_key": "example-unique-sale-2026-0001",
  "items": [{"product_id": 13, "quantity": 2}],
  "payment": "cash",
  "tendered_cents": 200
}
```

O leite seed custa 89 cêntimos: total 178, recebido 200, troco 22. `payment` aceita `cash`, `card` ou `mbway`; eletrónicos usam `tendered_cents:0` na entrada, guardando o total efetivo no talão. Quantidades/cêntimos são inteiros JSON, não strings, booleans ou decimais. Taxas e preços enviados pelo cliente são ignorados. Nova venda = nova chave; retry da mesma venda = mesma chave e conteúdo.

Resposta de erro: `{"error":"mensagem em português"}`; falhas operacionais podem incluir `request_id`. A semântica dos códigos está em [arquitetura](architecture.md). O limite do body é 64 KiB. Históricos não possuem paginação nesta versão. Não há endpoints de eliminação de vendas nem para mutação de utilizadores/catálogo.
