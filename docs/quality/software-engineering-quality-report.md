# Software Engineering Quality Report — 0.1.0

Data: 2026-10-01. Conclusão delimitada: baseline funcional e verificada localmente para demonstração académica. Não aprovada para operação comercial nem declarada certificada.

| Estado | Entregas / evidências |
|---|---|
| Planeado | Incrementos I1–I4, requisitos e critérios, papéis, arquitetura e plano de testes |
| Implementado | PoS ponta a ponta, seed, perfis, turnos, vendas/pagamentos simulados, anulações, stock, relatórios, audit e backup |
| Verificado localmente | Suite 44/44, E2E Edge, layout mobile, Ruff, build, backup, desempenho local, audit runtime e SBOM; ver relatório de testes |
| Implementado mas por verificar noutro ambiente | Workflow GitHub Actions, receita Linux/Chromium, configuração de cookies para HTTPS |
| Não implementado | Integração fiscal/bancária, gestão de contas/catálogo na UI, devolução parcial, peso, promoções, offline, HA, migrations incrementais |
| Trabalho futuro | Aceitação com operadores, revisão independente, CI remoto, TLS/identidade e integrações; prioridades na dívida técnica |

**Requisitos e rastreabilidade:** critérios identificados, matriz relaciona código e testes. Origem U/P/A distingue pedido, prompt e pressuposto. Sem aprovação de requisitos por cliente inventada.

**Arquitetura:** módulos HTTP/domínio/dados/interface; fronteiras e transações documentadas; ADRs justificam SQLite/Flask e dinheiro inteiro. Concorrência/idempotência têm testes específicos, incluindo locks e rollback.

**Qualidade:** nove características analisadas com metas e limites. Medição de latência é local, não capacidade de uma cadeia. UX teve inspeção e E2E, mas não ensaios com utilizadores reais ou auditoria WCAG integral.

**Segurança e privacidade:** autorização no servidor, CSRF/origin, hashes/sessões, limites, CSP e audit; teste de dependências sem vulnerabilidades runtime conhecidas na data. Threat model identifica residuais; seed só fictício; não existe alegação de conformidade legal/SGSI.

**Processo/CMMI/referenciais:** plano, riscos, matriz, testes, métricas, ADRs e lessons learned evidenciam práticas selecionadas. Faltam histórico longitudinal, revisão independente e validação operacional. O mapeamento é parcial e não um appraisal.

**Problemas conhecidos:** catálogo e identidades dependem do seed; instância única; dias UTC; paginação limitada; carrinho não persiste reload; pagamentos/fiscalidade simulados; backups remotos e recuperação de desastre não automatizados. Itens TD-001…016 tornam o risco explícito.

**Reprodução:** scripts e comandos sem caminhos pessoais, dependências fixadas, base criada do zero e dados seed conferidos. Artefactos de evidência arquivados; geração pode ser repetida em `artifacts/`. CI remota e revisão são condições em aberto na Definition of Done de release.

**Melhoria prioritária:** executar o guião com responsáveis da cadeia, confirmar domínio comercial e contabilístico, fechar riscos P0 e só então dimensionar deployment/integrações. A evolução deve preservar os testes de integridade e a rastreabilidade da baseline.
