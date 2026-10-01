# Instalação e operação

## Windows

Pré-requisitos: Python ≥3.10 com módulo venv, rede para o PyPI na primeira instalação; Edge para E2E. Validado em Windows 10.0.26200, Python 3.10.7, SQLite fornecido pelo Python. Node/npm não são necessários.

```powershell
.\setup.ps1
.\start.ps1
```

O setup instala apenas `requirements.txt`; `-Dev` instala `requirements-dev.txt`. Os scripts entram na pasta do projeto e configuram `PYTHONPATH=src`. Não exigem ativar o venv. Init preserva bases existentes e publica um novo seed só depois de terminar com sucesso. A `.seed-tmp` de uma carga interrompida deve ser inspecionada, não sobrescrita silenciosamente.

Comandos equivalentes, para execução manual:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m mercado init
.\.venv\Scripts\python.exe -m mercado serve --port 5000
```

Abrir `http://127.0.0.1:5000`; parar com Ctrl+C. Uma porta ocupada pode ser substituída: `.\start.ps1 -Port 5001`. Nenhum processo precisa de privilégios de administrador para servir numa porta livre.

## Linux/macOS

Receita fornecida; execução local desta entrega foi no Windows. A CI Linux está configurada, mas não foi executada remotamente nesta sessão.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --disable-pip-version-check -r requirements.txt
export PYTHONPATH=src
python -m mercado init
python -m mercado serve
```

## Configuração

| Variável | Predefinição | Uso |
|---|---|---|
| `POS_DATABASE` | `instance/mercado.sqlite3` | Caminho SQLite; a opção CLI `--database` sobrepõe |
| `POS_TRUSTED_HOSTS` | `localhost,127.0.0.1,[::1]` | Hosts aceites, separados por vírgula |
| `POS_COOKIE_SECURE` | `0` | `1` apenas num endpoint HTTPS corretamente configurado |

`.env.example` é uma referência; `.env` não é carregado automaticamente. Exportar as variáveis na shell. Não há segredo fixo de sessão: os tokens são aleatórios, opacos e guardados com hash. Não usar as contas públicas seed fora da demonstração.

## Testes e build

```powershell
.\setup.ps1 -Dev
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe scripts/check.py
.\.venv\Scripts\python.exe scripts/smoke_package.py
.\.venv\Scripts\python.exe scripts/e2e.py
.\.venv\Scripts\python.exe scripts/benchmark.py
.\.venv\Scripts\python.exe -m pip_audit --no-deps --disable-pip -r requirements.txt -f cyclonedx-json -o artifacts/sbom.cdx.json
```

`check.py` para no primeiro erro e executa lint, formatação, pytest com JUnit e build. O wheel/sdist inclui schema, template e assets. Para distribuir, instalar primeiro as versões de `requirements.txt` e depois `pip install --no-deps dist/mercado_pos-0.1.0-py3-none-any.whl`; `python -m mercado init` e `serve` funcionam sem `PYTHONPATH` numa instalação de wheel.

No E2E, `--channel chromium` permite usar o navegador descarregado pelo Playwright: `python -m playwright install chromium`. O script cria uma base temporária e um servidor com porta livre, fecha ambos no fim e grava capturas/JSON em `artifacts/`.

## Backup e recuperação

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m mercado backup --output instance/backup-2026-10-01.sqlite3
```

É usada a API de backup SQLite para incluir alterações confirmadas em WAL. O destino deve ser novo; o comando não substitui ficheiros e verifica `PRAGMA integrity_check`. Guardar cópias fora do disco do servidor é responsabilidade operacional; o script só escreve o destino indicado.

Para recuperar: parar o servidor; escolher uma cópia íntegra; executar `python -m mercado serve --database instance/backup-2026-10-01.sqlite3`. Validar `/health`, contagem de vendas, talões e stock. Guardar a base original para investigação. Se for necessário voltar ao nome anterior, fazê-lo apenas com o serviço parado e incluindo a disciplina de checkpoint/ficheiros WAL. Não copiar apenas o `.sqlite3` de um serviço ativo.

Testado: integridade, foreign keys, contagem de vendas após backup e restauro através da aplicação. Não medidos: RPO/RTO de produção, recuperação de desastre em hardware diferente e backups remotos automáticos.

## Manutenção, migração e rollback

Versão de schema inicial: 1. Init cria tabelas/índices ausentes, não transforma estruturas já existentes. Antes de qualquer futura alteração de schema: backup, migração versionada, teste em cópia e plano de reversão. Rollback da aplicação: voltar ao wheel anterior apenas se compatível com o schema; caso contrário restaurar a cópia pré-migração. Não existe rollback automático ou release remota configurada.

O ficheiro de base, WAL, backups e logs exigem permissões de acesso do sistema operativo. As sessões expiram em 8 horas; o login limpa sessões e buckets de tentativas expirados. Eventos de negócio não são purgados automaticamente. Monitorizar espaço em disco e erros 5xx/503.

## Troubleshooting

| Sintoma | Ação |
|---|---|
| `No module named mercado` | Configurar `PYTHONPATH=src` na raiz ou instalar o wheel. |
| PowerShell bloqueia script | Usar a opção `-ExecutionPolicy Bypass -File` apenas para esse processo, ou comandos manuais. |
| Instalação sem rede | Garantir acesso autorizado ao PyPI ou preparar um wheelhouse; não é necessário acesso externo depois de instalado. |
| Erro de origem/CSRF | Usar sempre o mesmo host/porta; atualizar página e autenticar novamente. |
| Caixa ocupada | Fechar o turno com o operador que o abriu; admin não força o fecho de terceiros nesta versão. |
| Venda sem stock | Atualizar catálogo; gerente pode registar reposição justificada. |
| `database is locked` / 503 | Verificar processos externos e locks; não abrir múltiplos servidores sobre disco de rede. Repetir a mesma chave de venda se o resultado for incerto. |
| Build falha | Instalar dependências de desenvolvimento; usar `--no-isolation` com versões fixadas. |
| Edge indisponível | Instalar Chromium com Playwright e usar `--channel chromium`. |

Para produção: validar requisitos com o cliente; integrar faturação/pagamentos; gestão de contas; HTTPS; política de retenção; monitorização; backups remotos testados; revisão independente; testes de carga e recuperação. Não existe aprovação de disponibilização real nesta entrega.
