# Modelo de qualidade

Análise académica das nove características indicadas na prompt, usando a [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) como enquadramento. Não é uma avaliação normativa integral nem certificação. Os requisitos específicos e os testes são decisões deste projeto.

| Característica | Aplicabilidade / requisito | Métrica e alvo | Método / resultado |
|---|---|---|---|
| Functional suitability | Fluxos de caixa/stock, F-001…013 | Todos os cenários críticos implementados e suite 100% aprovada | API/E2E; resultados no relatório; adequação a cliente pendente |
| Performance efficiency | Leituras PoS/gestão, NF-003 | P95 <200 ms em 100 leituras locais por endpoint | Benchmark reproduzível; alvo local atingido |
| Compatibility | Navegador HTTP/JSON e SQLite local | Fluxo E2E no Edge; instalação Windows | Verificado localmente; Chromium/Linux na CI configurada, outros browsers pendentes |
| Interaction capability | Interface responsiva, NF-005 | Sem overflow de página a 390 px; controlos rotulados; erros compreensíveis | E2E/capturas; ensaio com utilizadores e leitor de ecrã pendente |
| Reliability | Stock/caixa consistentes, NF-001/002 | Zero overselling e duplicações nos cenários concorrentes; backup íntegro | Testes concorrentes e backup aprovados; RTO/RPO não medidos |
| Security | SEC-001…004 | Acessos indevidos bloqueados; zero vulnerabilidades runtime conhecidas na consulta | Suite de segurança/audit; pentest e ASVS integral pendentes |
| Maintainability | Domínio separado, requisitos rastreados | Lint/format sem erros; matriz cobre todos os requisitos | Checks e inspeção; revisão por outra pessoa pendente |
| Flexibility | Configuração externa e pacote instalável | Caminho de DB/porta configurável; wheel inclui assets/schema | CLI/build/smoke; escala distribuída excluída |
| Safety | Prejuízo operacional/financeiro por erro de sistema | Recusar stock negativo, preço manipulado, pagamento insuficiente e anulação inválida | Testes aprovados; sem função de segurança física crítica; análise formal de safety N/A |

Decisão de avaliação: comportamento e integridade têm prioridade sobre número de funcionalidades. Cobertura de linhas, complexidade ciclomática, lead time e satisfação do cliente não foram medidos. Não converter a existência de ficheiros em evidência de maturidade organizacional.
