# Plano de verificação e validação

Baseline 0.1.0, 2026-10-01. Responsável de execução local: agente de desenvolvimento; revisão independente e aceitação: equipa/cliente a designar. Não foram inventados nomes de revisores.

## Âmbito, níveis e técnicas

- Unidade: dinheiro e arredondamento por particionamento de valores/taxas.
- Integração/API: Flask test client + SQLite real temporário; autenticação, permissões, persistência, transações, erros, estados e idempotência.
- Concorrência: duas ligações e threads sincronizadas por barrier; última unidade e retry simultâneo.
- Sistema/E2E: navegador real, HTTP local, base seed isolada, interação por rótulos acessíveis, dois perfis, desktop e mobile.
- Segurança: acessos indevidos, CSRF/Origin, sessão expirada/revogada, headers, SQL injection, payload e tentativas.
- Performance: 5 warm-ups + 100 leituras sequenciais por endpoint, P95 local; nenhuma conclusão sobre carga real de cadeia.
- Operação: seed, constraints, backup e restauro; construção de wheel e verificação de recursos empacotados.
- Supply chain: audit runtime e SBOM; versões fixadas.

Técnicas: partições de equivalência (pagamentos/papéis), limites (zero, negativo, boolean, decimal, excesso de stock, body), transição de estados (aberto/fechado, concluída/anulada), cenários de erro, replay, concorrência e inspeção de UI. Não se utiliza coverage como substituto de comportamento.

## Ambientes e dados

Suite API: base temporária mínima, 2 lojas, produtos com stock e esgotados, contas de teste com hash PBKDF2 de custo reduzido apenas na fixture. A aplicação seed usa scrypt normal. E2E/benchmark: seed completo em diretório temporário. A base `instance/mercado.sqlite3` do utilizador não é usada pelos testes. Não se usam dados pessoais reais.

Ambiente verificado: Windows/Python 3.10.7, Edge headless para E2E. CI projetada: Ubuntu/Python 3.10/Chromium. Execução remota e matriz completa de browsers pendentes.

## Entrada, saída e aprovações

Entrada: dependências instaladas, schema e requisitos consistentes, runtime importável. Saída local: lint/format/build sem erro, suite 100% aprovada, fluxo E2E crítico aprovado, zero vulnerabilidades conhecidas no scan runtime e evidências geradas. Um erro bloqueia a respetiva verificação; não se altera um teste apenas para esconder um defeito.

Definition of Done para release: critérios funcionais, testes, documentação/rastreabilidade, revisão independente e CI remoto aprovados. Os dois últimos não estão concluídos nesta entrega local. Testes automáticos verificam a implementação; a validação de adequação ao trabalho real exige o [guião de aceitação](../manual-user.md) executado com utilizadores representativos.

Meta de cobertura comportamental: todos os fluxos críticos e invariantes RN-001…RN-009 devem ter pelo menos um cenário positivo e rejeições relevantes. Cobertura de linhas não medida nesta entrega; não se fornece uma percentagem inferida.

## Riscos e pendências

Sem hardware de impressão/scanner/balança, gateway bancário ou ambiente fiscal. Impressão física, acessibilidade assistiva, falhas de disco durante commit, stress prolongado e aceitação humana pendentes. Falhas de rede são tratadas por erro/retry, mas a perda do carrinho após reload está documentada. A estratégia não constitui qualificação de produção.

Comandos: [manual de instalação](../manual-installation.md). Resultados reais: [test-report.md](test-report.md); requisitos cobertos: [matriz](../requirements/traceability-matrix.md).
