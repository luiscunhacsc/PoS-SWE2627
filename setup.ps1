param([switch]$Dev)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar o ambiente Python.' }
}
$pythonPath = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$requirementsPath = if ($Dev) { 'requirements-dev.txt' } else { 'requirements.txt' }
& $pythonPath -m pip install --disable-pip-version-check -r $requirementsPath
if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependências.' }
$env:PYTHONPATH = Join-Path $PSScriptRoot 'src'
& $pythonPath -m mercado init
if ($LASTEXITCODE -ne 0) { throw 'Falha ao inicializar a base de dados.' }
Write-Host 'Preparado. Execute .\start.ps1 e abra http://127.0.0.1:5000'
