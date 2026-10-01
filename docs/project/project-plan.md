# Plano, incrementos e histórico real

## Âmbito e responsabilidades

Solicitante: utilizador desta sessão. Implementação/documentação/verificação local: Codex, assistente de desenvolvimento. Dono de produto, equipa, calendário académico e revisor humano: não indicados. Não há link preenchido para projeto-modelo; não foi analisado um exemplo inacessível.

Estimativa de esforço de manutenção/produção não realizada: depende de requisitos fiscais, lojas concorrentes, hardware, equipa e objetivos operacionais. A entrega aqui é uma baseline local com fluxos completos e documentação, não um semestre fictício.

| Incremento | Objetivo / requisitos | Artefactos | Critério de conclusão local | Resultado |
|---|---|---|---|---|
| I1 | Contexto, dados e segurança F-001/002/012 | Requisitos, schema, seed, autenticação | Login e dados consistentes, papéis isolados | Implementado/verificado |
| I2 | Caixa/venda/anulação F-004…008, NF-001/002 | Domínio, API, PoS, testes | Venda atómica, troco, exclusividade, retry e fecho corretos | Implementado/verificado |
| I3 | Gestão de loja F-003/009…011 | Inventário, dashboard, relatórios, audit | Ajustes autorizados, agregados e navegação funcional | Implementado/verificado |
| I4 | Evidência e reprodução F-013/NF-003…006 | Scripts, CI, manuais, quality/security/RTM | Check local + E2E + backup + build e evidências | Verificado localmente; CI remoto pendente |

## Histórico da sessão — 2026-10-01

1. Inspeção confirmou uma pasta com a prompt, sem aplicação existente. Leitura em UTF-8 preservou o ficheiro original.
2. Escolheu-se Python disponível localmente; Node/npm não foram necessários. Arquitetura e requisitos explicitam pressupostos.
3. Criaram-se persistência, domínio e API, seguido da interface e geração de dados. Dados seed passam pelo serviço de venda, conservando consistência de movimentos.
4. A instalação inicial de dependências foi impedida pelo acesso de rede do ambiente restrito; a instalação autorizada no venv foi concluída. Não se alteraram pacotes globais.
5. A suite de 44 testes passou. O E2E inicial detetou que a seta decorativa fazia parte do nome acessível de links; corrigiu-se com `aria-hidden` e o cenário passou.
6. A revisão ajustou o dia dos relatórios a UTC explícito, tratamento de CSRF não ASCII, data seed sem eventos futuros e acesso a logout em mobile.
7. Foram produzidos build, métricas, audit/SBOM, documentação e evidência local. O Git foi inicializado, sem fabricar commits ou revisões.

Desvios: nenhuma integração real foi tentada; âmbito académico declarado desde o início. Infraestrutura distribuída, Docker e funcionalidades secundárias adiadas por prioridade à verificação dos fluxos críticos. As limitações constam da dívida técnica.

## Definition of Done

Uma funcionalidade está implementada quando existe ponta a ponta em UI/API/domínio/dados, valida erros e preserva invariantes. Está verificada localmente quando os testes associados passam e os documentos/matriz estão atualizados. Está aprovada para release apenas após revisão independente, CI remoto verde, risco residual aceite e validação do responsável. A baseline satisfaz a verificação local descrita; não satisfaz ainda a aprovação formal para produção/release de equipa.

Gestão de alterações: associar mudança a requisito/regra, avaliar impacto via RTM, atualizar ADR se necessário, testar, rever, atualizar changelog e só depois gerar tag/release. Não atribuir resultados medidos a ambientes onde não foram executados.
