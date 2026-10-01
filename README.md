# Mercado · PoS para supermercados

Sistema académico funcional para uma cadeia fictícia de supermercados, desenvolvido a partir de [Prompt_Unificada_Projeto_Engenharia_Software_Mestrado.md](Prompt_Unificada_Projeto_Engenharia_Software_Mestrado.md). Interface em português, persistência SQLite, backend Flask e servidor Waitress. Versão **0.1.0**.

## Experimentar no Windows

Requisito: Python 3.10 ou superior. A versão efetivamente verificada foi **Python 3.10.7**, no Windows. A instalação inicial precisa de acesso ao PyPI.

```powershell
.\setup.ps1
.\start.ps1
```

Abrir **http://127.0.0.1:5000**. Se a política local impedir scripts, executar `powershell -ExecutionPolicy Bypass -File .\setup.ps1` e, depois, o mesmo comando com `start.ps1`. Isto não altera a política permanente do sistema.

Na pasta entregue, o ambiente virtual e a base inicial já foram preparados: basta executar **`.\start.ps1`**. Estes artefactos locais são ignorados pelo Git e reconstruídos pelo setup.

| Conta fictícia | Perfil | Acesso |
|---|---|---|
| `admin` | Administrador | Todas as lojas e auditoria |
| `gerente.lisboa` | Gerente | Lisboa, relatórios e gestão de stock |
| `caixa.lisboa` | Operador | Caixa, vendas e consulta de stock de Lisboa |
| `gerente.porto`, `caixa.porto` | Gerente / operador | Porto |
| `gerente.coimbra`, `caixa.coimbra` | Gerente / operador | Coimbra |

**Palavra-passe de todas as contas de teste: `Demo2026!`.** São credenciais públicas exclusivamente para a demonstração local.

## O que funciona

- Autenticação, sessões revogáveis e permissões verificadas no servidor.
- Seleção de loja; catálogo, pesquisa por nome, SKU ou código de barras interno.
- Abertura e fecho de turnos, fundo inicial, apuramento de numerário e diferenças.
- Carrinho, validação de stock, preços calculados pelo servidor e IVA demonstrativo incluído.
- Pagamentos simulados em numerário, cartão e MB WAY; troco e talão imprimível.
- Venda atómica, proteção contra repetição do mesmo pedido e concorrência no último artigo.
- Anulação integral por gerente/admin, com motivo, reposição de stock e turno ainda aberto.
- Stock por loja, alertas, ajustes com justificação e movimentos auditáveis.
- Dashboard, histórico de vendas, relatórios de sete dias e auditoria global.
- Backup consistente, health check, logs estruturados, testes, CI e documentação de engenharia.

## Dados fictícios

`python -m mercado init` cria **3 lojas, 6 caixas, 48 produtos, 144 posições de stock, 7 utilizadores e 180 vendas** distribuídas por 30 dias. Inclui cinco produtos por loja no limite de reposição, um deles esgotado. Não utiliza nomes de clientes, dados bancários ou dados externos. Os perfis são personagens fictícias.

A geração usa uma semente fixa. `--reference-date 2026-10-01` permite fixar a data de referência. Hashes de palavras-passe são deliberadamente aleatórios. Reexecutar `init` preserva a base existente; para outra demonstração, indicar `--database instance/outra.sqlite3`.

## Verificação

```powershell
.\setup.ps1 -Dev
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe scripts/check.py
.\.venv\Scripts\python.exe scripts/e2e.py
.\.venv\Scripts\python.exe scripts/benchmark.py
.\.venv\Scripts\python.exe -m pip_audit --no-deps --disable-pip -r requirements.txt
```

O E2E usa Microsoft Edge instalado no Windows; para Chromium: `python -m playwright install chromium` e `python scripts/e2e.py --channel chromium`. Os testes usam bases isoladas e não alteram a demonstração.

Resultados e condições de execução: [relatório de testes](docs/testing/test-report.md). Artefactos reproduzíveis em `artifacts/`; evidência da entrega em [docs/testing/evidence](docs/testing/evidence/). O pipeline GitHub Actions foi configurado; a execução remota depende de publicar o repositório e não é declarada como realizada.

## Documentação

| Documento | Conteúdo |
|---|---|
| [Instalação e operação](docs/manual-installation.md) | Windows/Linux, configuração, build, backup, recuperação |
| [Manual de utilização](docs/manual-user.md) | Fluxos por perfil e guião de demonstração |
| [Requisitos](docs/requirements/requirements.md) | Âmbito, critérios de aceitação e regras |
| [Rastreabilidade](docs/requirements/traceability-matrix.md) | Requisitos → código → testes |
| [Arquitetura](docs/architecture/architecture.md) | Camadas, transações, dados, modelos e ADRs |
| [API](docs/architecture/api.md) | Contratos HTTP, autenticação, exemplos e erros |
| [Segurança](docs/security/security.md) | Controlos, ameaças, privacidade e limitações |
| [Relatório técnico](docs/technical-report.md) | Síntese estruturada do projeto |
| [Relatório de qualidade](docs/quality/software-engineering-quality-report.md) | Implementado, verificado, pendente e futuro |
| [Mapeamento de referenciais](docs/compliance/standards-mapping.md) | Práticas e evidências; sem certificação |

## Limites da entrega

É uma demonstração local com pagamentos simulados e **talões sem valor fiscal**. Não integra faturação certificada, AT/SAF-T, adquirentes bancários, balanças, devoluções parciais, promoções, fidelização, compras a fornecedores ou operação offline. O catálogo é carregado pelo seed; a interface não inclui criação de produtos/utilizadores. SQLite centralizado é adequado à demonstração, não foi qualificado para uma cadeia real em produção. Consulte [dívida técnica](docs/quality/technical-debt.md).

Os campos do ficheiro base relativos a equipa, prazo e projeto-modelo não estavam preenchidos. Os pressupostos estão identificados; não se inventaram validações por clientes, revisões humanas, histórico de semestre ou certificações.
