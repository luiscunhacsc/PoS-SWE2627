# Manual de utilização e demonstração

## Entrar e escolher uma loja

Abrir `http://127.0.0.1:5000`. Usar `admin` / `Demo2026!` para explorar todas as lojas. `caixa.lisboa` permite experimentar o perfil de operador e `gerente.lisboa` o de gerente. Os sufixos `porto` e `coimbra` dão os perfis equivalentes nas outras lojas.

No topo, escolher a loja. Mudar de loja com um carrinho exige confirmação e remove os seus artigos. Uma mudança de loja não encerra um turno aberto; o operador deve fechá-lo para abrir outro. Administradores podem alternar as três lojas; os restantes perfis só veem a sua.

## Operador: abrir, vender e fechar

1. Abrir **Ponto de venda → Abrir caixa**. Escolher uma caixa livre e introduzir o fundo, por exemplo `150,00`.
2. Pesquisar `Leite`. Adicionar **Leite meio-gordo · 1 L**, duas vezes. O total será `1,78 €`.
3. Também pode escrever `2000000000013` e carregar Enter. Leitores que funcionem como teclado podem enviar este código; não foi testado hardware físico. Estes códigos são internos, não identificadores GS1 certificados.
4. Escolher **Cobrar → Numerário**, recebido `2,00`, confirmar. O talão apresenta troco `0,22 €` e pode ser impresso pelo navegador.
5. O carrinho fica vazio e o stock reduz-se em duas unidades. Cartão/MB WAY simulam o pagamento, sem banco nem recolha de dados de cartão.
6. Em **Vendas**, consultar o talão. Os preços históricos não mudam se o catálogo for atualizado fora da interface.
7. Em **Fechar turno**, contar o numerário. Se apenas ocorreu a venda acima, o esperado é `151,78 €`. Introduzir o contado e confirmar. A diferença é registada, mesmo quando não é zero.

Pedidos com pagamento insuficiente ou stock esgotado apresentam erro e conservam o carrinho. Se ocorrer uma falha de rede ao confirmar, repetir sem alterar o carrinho/pagamento reutiliza o identificador da tentativa. Antes de recriar manualmente uma compra após reload, consultar o histórico para evitar uma nova venda distinta.

## Gerente: anular e gerir stock

Para anular, abrir um talão de venda concluída, selecionar **Anular venda**, introduzir motivo de pelo menos cinco caracteres e confirmar. O turno original deve estar aberto. O stock é reposto uma única vez e a venda fica no histórico como anulada. Não existe reembolso bancário real.

Em **Inventário**, filtrar **Stock a repor** ou **Esgotado**. **Ajustar** aceita `20` para adicionar ou `-3` para retirar, sempre com motivo. Uma quantidade final negativa é rejeitada. **Ver movimentos** mostra os últimos 200 registos da loja. Operadores consultam inventário, mas não podem ajustá-lo.

Dashboard e relatórios apresentam totais calculados a partir da base, excluindo anulações. O período é fixo em sete dias e os dias são agrupados em UTC; a hora apresentada nos talões usa a configuração local do navegador.

## Administrador

Pode fazer os fluxos de venda e gestão em qualquer loja, consultar ocupação das caixas em **Lojas** e os últimos 200 eventos em **Auditoria**. Não existe interface de administração de contas ou criação de produtos nesta versão. A manipulação direta da base não substitui um fluxo de gestão auditado.

## Guião de aceitação pelo cliente

Usar uma base nova ou registar stock inicial antes de começar. Assinalar o resultado de cada cenário; a aceitação humana não foi realizada nesta entrega.

| Cenário | Dados e ação | Resultado esperado |
|---|---|---|
| AC-01 | Login de `caixa.lisboa` | Só Lisboa; sem auditoria/relatórios/ajuste |
| AC-02 | Abrir caixa com 150 € e vender dois leites em dinheiro, recebido 2 € | Total 1,78 €, troco 0,22 €, stock −2 |
| AC-03 | Repetir com recebido 1 € | Erro; nenhuma nova venda ou alteração de stock |
| AC-04 | Procurar peito de frango esgotado no seed | Cartão desativado; API rejeita tentativa de venda |
| AC-05 | Gerente anula AC-02 antes do fecho | Motivo obrigatório; stock +2; numerário esperado volta a 150 € |
| AC-06 | Fechar turno e tentar anular venda desse turno | Anulação rejeitada; turno permanece fechado |
| AC-07 | Gerente repõe 10 unidades com motivo | Quantidade +10 e movimento visível |
| AC-08 | Admin muda para Porto e consulta relatórios | Dados e stock de Porto; nenhuma mistura com Lisboa |
| AC-09 | Terminar sessão e tentar consultar API | 401; novo login necessário |
| AC-10 | Executar backup e servir a cópia | Talões e stock preservados; health `ok` |

Teclado: Tab navega os controlos, Enter submete formulários, Escape fecha diálogos. Os diálogos de anulação/ajuste/fecho requerem confirmação explícita. Há texto de erro e estado para além da cor. Validação com leitores de ecrã e utilizadores reais está pendente.
