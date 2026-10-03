$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$portalPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $portalPython)) { throw 'Create .venv and install requirements first. See README.md.' }
if (!(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'frontend/dist/index.html'))) {
    Push-Location -LiteralPath (Join-Path $PSScriptRoot 'frontend')
    try {
        if (!(Test-Path -LiteralPath 'node_modules')) { npm.cmd ci; if ($LASTEXITCODE -ne 0) { throw 'npm install failed.' } }
        npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
    } finally { Pop-Location }
}
& $portalPython manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
Write-Host 'Open http://127.0.0.1:8000'
& $portalPython manage.py runserver 127.0.0.1:8000
