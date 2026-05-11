$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendDir = Join-Path $repoRoot 'backend'
$pythonExe = Join-Path $backendDir '.venv\Scripts\python.exe'

if (-not (Test-Path $pythonExe)) {
  Write-Error "backend virtualenv python not found: $pythonExe"
}

$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'

Push-Location $backendDir
try {
  & $pythonExe -m pytest -q -p pytest_django.plugin
}
finally {
  Pop-Location
}
