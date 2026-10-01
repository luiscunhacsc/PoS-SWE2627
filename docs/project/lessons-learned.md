# Lições observadas

1. Os requisitos de engenharia da prompt são mais amplos do que o ecrã de caixa. Delimitar pagamentos/fiscalidade e ligar artefactos à evidência tornou o âmbito defensável.
2. Testar simultaneamente a última unidade revelou uma propriedade que um simples teste de interface não demonstra: a leitura e a alteração de stock precisam da mesma fronteira de transação.
3. A navegação visual parecia correta, mas a seta decorativa alterava o nome acessível do link. Um E2E orientado por rótulos detetou o problema; `aria-hidden` corrigiu-o.
4. Criar vendas seed através do domínio mantém preços, IVA e movimentos coerentes. Um turno histórico consolidado continua a ser uma simplificação explícita, não um retrato de operação real.
5. Windows, caminhos acentuados e encoding exigem cuidado: os ficheiros do projeto são UTF-8; scripts fornecidos usam `PYTHONPATH` e evitam exigir instalação editable em diretório acentuado.
6. Um scan limpo, testes locais e um workflow no disco são evidências distintas de CI remoto, aprovação humana e produção. A documentação preserva essas diferenças.

Melhoria proposta: validar os cenários AC com operadores reais antes de expandir o catálogo funcional; priorizar identidade, calendário comercial, recuperação e integrações antes de gráficos adicionais.
