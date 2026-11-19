$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Instale Python 3.12 ou superior.' }
    & $python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Não foi possível instalar as dependências.' }
}
Write-Host 'Abra http://127.0.0.1:8766 no navegador. Mantenha esta janela aberta.'
& $python app.py
