# Relatório técnico — Mercado PoS

**Documento:** RT-MRC-001. **Versão:** 0.1.0. **Data:** 2026-10-01. **Estado:** baseline académica com verificação local; revisão independente e aceitação pendentes. **Autor da implementação assistida:** Codex, sob instrução do utilizador. **Histórico:** primeira versão produzida nesta sessão; não existe histórico anterior atribuído a uma equipa.

## 1. Problema, objetivos e âmbito

Criar um PoS para uma cadeia de supermercados e disponibilizar dados fictícios para testar. A prompt impõe correspondência verificável entre requisitos, decisões, código, testes e operação. A cadeia Mercado e os utilizadores são fictícios. O objetivo desta baseline é demonstrar os fluxos críticos completos num ambiente local e reproduzível. Requisitos de cliente não fornecidos foram tratados como pressupostos, não como entrevistas realizadas.

Incluído: lojas, perfis, turnos, catálogo, carrinho, pagamento simulado, talões, anulações, inventário, relatórios, auditoria e backup. Excluído: fiscalidade certificada, integrações financeiras/periféricos, offline, gestão completa de fornecedores e clientes. Stakeholders e histórias em [requisitos](requirements/requirements.md).

## 2. Requisitos, modelos e decisões

Baseline com 13 requisitos funcionais, 6 não funcionais, 4 de segurança e 10 regras. [Matriz de rastreabilidade](requirements/traceability-matrix.md) associa casos de uso, implementação e evidência. [Arquitetura](architecture/architecture.md) inclui modelos Mermaid editáveis: contexto/containers/deployment, ER, sequência, estados e atores. ADRs registam escolha de monólito local e dinheiro/transações/simulação.

## 3. Implementação e dados

Python/Flask para HTTP e domínio; SQLite com constraints, WAL e transações; Waitress; JavaScript sem framework. Dinheiro em inteiros, stock não negativo, autorização por loja/papel, snapshots de linhas e idempotência. O seed cria 3 lojas, 6 caixas, 48 produtos, 7 contas e 180 vendas, com movimentos reconciliáveis. O histórico é sintético e usa um turno consolidado por loja.

O frontend apresenta valores calculados a partir da base; não há métricas de negócio hardcoded. Ícones/SVG e tipografia do sistema não dependem de serviços externos. [API](architecture/api.md) documenta o contrato.

## 4. Verificação, validação e evidências

44 testes automatizados de domínio/API/integração/segurança aprovados; E2E Edge com oito etapas, desktop/mobile; benchmark local de três leituras; Ruff; build wheel/sdist; verificação de backup; scan de dependências runtime e SBOM. Resultados e limites em [test-report](testing/test-report.md). O número de testes não é uma percentagem de cobertura de código.

O cenário E2E verificou utilização real de navegador, mas não representa validação pelo cliente. O guião AC está disponível no [manual](manual-user.md); aceitação humana, impressão física, acessibilidade assistiva e ambiente de produção não foram validados.

## 5. Segurança, privacidade e processo

[Segurança](security/security.md) e [STRIDE](security/threat-model.md) explicitam fronteiras, ameaças, controlos e residuais. Sem dados pessoais de clientes ou cartões. Passwords seed públicas e operação local não são desenho de produção. Há plano, registo de riscos, histórico real, dívida técnica e métricas; não há alegação de equipa madura, certificação ou CI remoto executado. [Mapeamento](compliance/standards-mapping.md) apresenta práticas selecionadas e N/A justificados.

## 6. Manutenção e reprodução

README, manuais, scripts de setup/start/check/E2E/benchmark, requisitos fixados, workflow e ficheiros de schema permitem reproduzir a baseline. Backup usa a API SQLite e verifica integridade. Migrations futuras e deployment real estão pendentes. O projeto Git foi inicializado; commits, tags e revisão serão registados quando efetivamente realizados.

## 7. Limitações e evolução

A [dívida técnica](quality/technical-debt.md) enumera gaps por prioridade. Antes de qualquer utilização comercial: validação de requisitos e integrações, identidade e TLS, operação/retention, revisão externa, carga/recuperação e aceitação. O [relatório de qualidade](quality/software-engineering-quality-report.md) separa planeado, implementado, verificado e futuro.

## 8. Declaração de apoio de IA

Codex foi usado para analisar a prompt, delimitar pressupostos, propor decisões, gerar código/schema/dados fictícios, criar testes/documentos e executar verificações através de ferramentas locais. Não existe componente de IA no produto. O modelo interno exato e métricas de produtividade não são inferidos.

Verificação das saídas geradas: suite automatizada, E2E em browser, inspeção de capturas, lint/formatação, build, integridade/backup, audit de dependências e revisão cruzada dos artefactos. Não houve revisão independente por outra pessoa nesta sessão. O uso de IA não transfere a responsabilidade técnica: a equipa deve compreender, rever e defender os resultados antes de avaliação ou release.

## 9. Referências

Referência principal: [prompt original fornecida](../Prompt_Unificada_Projeto_Engenharia_Software_Mestrado.md), preservada. Referências técnicas primárias: [Flask security](https://flask.palletsprojects.com/en/stable/web-security/), [Flask/Waitress](https://flask.palletsprojects.com/en/stable/deploying/waitress/), [SQLite transactions](https://www.sqlite.org/lang_transaction.html). Referenciais de processo: [standards-mapping](compliance/standards-mapping.md).
