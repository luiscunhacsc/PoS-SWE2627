param([int]$Port = 5000)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonPath = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Execute primeiro .\setup.ps1' }
$env:PYTHONPATH = Join-Path $PSScriptRoot 'src'
& $pythonPath -m mercado init
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível preparar a base de dados.' }
& $pythonPath -m mercado serve --port $Port
exit $LASTEXITCODE
