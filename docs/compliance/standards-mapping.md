# Mapeamento de referenciais e evidências

Esta é uma aproximação académica a práticas selecionadas, **não certificação**, declaração de conformidade integral, appraisal CMMI ou interpretação de cláusulas normativas. Os textos integrais licenciados das normas não foram usados para uma auditoria cláusula a cláusula. A presença de documentação não prova institucionalização de processo.

| Referência / prática selecionada | Aplicabilidade | Implementação e evidência | Limite |
|---|---|---|---|
| CMMI V3.0 — requisitos, planeamento, riscos, configuração, qualidade, verificação, medição e melhoria | Parcial, dimensão de projeto | `requirements/`, `project/project-plan.md`, `risk-register.md`, Git inicializado, testes, métricas e lessons learned | Sem avaliação de maturidade, histórico organizacional ou appraisal |
| ISO/IEC/IEEE 12207:2026 — organização do ciclo de vida | Parcial | Baseline, arquitetura, implementação, verificação, manutenção/rollback e manuais | Não cobre aquisição/operação real nem todos os processos |
| ISO/IEC/IEEE 29148:2018 — engenharia de requisitos | Aplicável | IDs, origem/pressupostos, prioridade, critérios, casos de uso e RTM | Elicitação/validação com cliente ainda pendente |
| ISO/IEC 25010:2023 — modelo de qualidade | Aplicável como enquadramento | `quality-model.md`, metas, métodos e resultados em `quality-metrics.md` | Avaliação limitada ao âmbito e ambiente declarados |
| ISO/IEC/IEEE 29119 — planeamento e evidência de teste | Parcial | Plano, técnicas, condições, suite, E2E, JUnit, relatório e aceitação | Sem declaração de conformidade com todas as partes/edições |
| ISO/IEC 27001:2022 — abordagem de risco e proteção da informação | Parcial/inspiracional | Segurança, threat model, controlo de acesso, backup, registo de riscos | Não existe SGSI implementado/certificado nem avaliação integral do Anexo A |
| Secure Software Development / Security by Design | Aplicável | Regras servidor, validação, transações, sessão, audit de dependências, threat model | Pentest e revisão independente pendentes |
| Privacy by Design / Default | Aplicável à minimização | Sem dados de cliente/cartão, dados seed fictícios, âmbito de acesso por loja, análise académica de privacidade | Bases legais/retenção de dados reais não determinadas; sem certificação RGPD |
| ISO/IEC 42001:2023 — sistema de gestão de IA no produto | N/A — Not Applicable | O produto não executa modelos de IA ou decisões automatizadas de ML | Apoio de IA no desenvolvimento é declarado separadamente, não torna o produto um sistema de IA |
| AI governance do desenvolvimento assistido | Aplicável como transparência | `technical-report.md`: origem, finalidade e verificação do código/docs gerados | Responsabilidade final da equipa; revisão humana pendente |
| CI/CD e supply chain | Parcial | Workflow, versões fixadas, Dependabot, audit e SBOM local | CI remoto, deployment, hashes completos e actions por SHA pendentes |
| Safety crítica / certificação de equipamento | N/A — Not Applicable no âmbito atual | Sem controlo de equipamento de segurança física | Integridade operacional tratada no modelo de qualidade; hardware futuro exige reavaliação |
| CODE_OF_CONDUCT de comunidade | N/A — Not Applicable nesta baseline | Projeto local sem comunidade ou contribuintes estabelecidos | Adotar se o repositório for aberto a colaboração pública |

## Fontes e alcance

As páginas públicas consultadas confirmam o objeto/identificação dos referenciais; não substituem os textos normativos:

- [ISO/IEC/IEEE 12207:2026 — catálogo ISO](https://www.iso.org/standard/90219.html).
- [ISO/IEC/IEEE 29148:2018 — catálogo ISO](https://www.iso.org/standard/72089.html).
- [ISO/IEC 25010:2023 — catálogo ISO](https://www.iso.org/standard/78176.html).
- [ISACA — apresentação de CMMI V3.0](https://www.isaca.org/resources/news-and-trends/isaca-now-blog/2023/cmmi-updates-take-performance-improvements-to-the-next-level).

As restantes referências seguem as edições/famílias explicitamente indicadas na prompt fornecida. Não se inferem cláusulas, requisitos legais ou níveis de certificação a partir dessas referências.
