param(
  [string]$MySqlExe = "",
  [string]$RedisCli = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendDir = Join-Path $repoRoot "backend"
$pythonExe = Join-Path $backendDir ".venv\\Scripts\\python.exe"
$envPath = Join-Path $backendDir ".env"
$smokeScript = Join-Path $repoRoot "scripts\\python\\local_stack_smoke.py"
$defaultMySqlCandidates = @(
  "D:\\MySQL\\bin\\mysql.exe",
  "C:\\Program Files\\MySQL\\MySQL Server 9.7\\bin\\mysql.exe",
  "C:\\Program Files\\MySQL\\MySQL Server 9.0\\bin\\mysql.exe",
  "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe"
)
$defaultRedisCliCandidates = @(
  "D:\\Redis-x64-3.0.504\\redis-cli.exe",
  "C:\\Redis\\redis-cli.exe",
  "C:\\Program Files\\Redis\\redis-cli.exe"
)

function Parse-DotEnv {
  param([string]$Path)

  $result = @{}
  if (-not (Test-Path $Path)) {
    throw "Missing .env file: $Path"
  }

  foreach ($line in Get-Content -Path $Path) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith("#")) {
      continue
    }

    if ($trimmed -match "^(?<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?<value>.*)$") {
      $key = $Matches["key"]
      $value = $Matches["value"].Trim()

      if ($value.StartsWith('"') -and $value.EndsWith('"')) {
        $value = $value.Substring(1, $value.Length - 2)
      }
      elseif ($value.StartsWith("'") -and $value.EndsWith("'")) {
        $value = $value.Substring(1, $value.Length - 2)
      }

      $result[$key] = $value
    }
  }

  return $result
}

function Get-EnvValue {
  param(
    [hashtable]$Vars,
    [string]$Key,
    [string]$Default = ""
  )

  if ($Vars.ContainsKey($Key) -and $null -ne $Vars[$Key] -and $Vars[$Key] -ne "") {
    return [string]$Vars[$Key]
  }

  return $Default
}

function Write-Step {
  param([string]$Message)
  Write-Host ""
  Write-Host "== $Message =="
}

function Resolve-ExecutablePath {
  param(
    [string]$PreferredPath,
    [string[]]$Candidates,
    [string]$CommandName,
    [string]$Label,
    [switch]$Optional
  )

  if ($PreferredPath) {
    if (Test-Path $PreferredPath) {
      return (Resolve-Path $PreferredPath).Path
    }

    if ($Optional) {
      return $null
    }

    throw "Configured $Label path does not exist: $PreferredPath"
  }

  $command = Get-Command $CommandName -ErrorAction SilentlyContinue
  if ($command -and $command.Source -and (Test-Path $command.Source)) {
    return $command.Source
  }

  foreach ($candidate in $Candidates) {
    if (Test-Path $candidate) {
      return (Resolve-Path $candidate).Path
    }
  }

  if ($Optional) {
    return $null
  }

  throw "Could not find $Label. Pass it explicitly or add $CommandName to PATH."
}

if (-not (Test-Path $pythonExe)) {
  throw "Missing backend virtualenv python: $pythonExe"
}

if (-not (Test-Path $smokeScript)) {
  throw "Missing smoke script: $smokeScript"
}

$envVars = Parse-DotEnv -Path $envPath
$dbHost = Get-EnvValue -Vars $envVars -Key "DB_HOST" -Default "127.0.0.1"
$dbPort = Get-EnvValue -Vars $envVars -Key "DB_PORT" -Default "3306"
$dbUser = Get-EnvValue -Vars $envVars -Key "DB_USER"
$dbPassword = Get-EnvValue -Vars $envVars -Key "DB_PASSWORD"
$redisHost = Get-EnvValue -Vars $envVars -Key "REDIS_HOST" -Default "127.0.0.1"
$redisPort = Get-EnvValue -Vars $envVars -Key "REDIS_PORT" -Default "6379"
$redisPassword = Get-EnvValue -Vars $envVars -Key "REDIS_PASSWORD"
$mysqlExe = Resolve-ExecutablePath -PreferredPath $MySqlExe -Candidates $defaultMySqlCandidates -CommandName "mysql" -Label "MySQL CLI"
$resolvedRedisCli = Resolve-ExecutablePath -PreferredPath $RedisCli -Candidates $defaultRedisCliCandidates -CommandName "redis-cli" -Label "Redis CLI" -Optional

Write-Step "Check MySQL CLI"
& $mysqlExe --version

Write-Step "Check Redis CLI"
if (-not $resolvedRedisCli) {
  Write-Warning "Redis CLI not found. Pass -RedisCli explicitly or add redis-cli to PATH."
}
else {
  & $resolvedRedisCli --version
}

Write-Step "Verify MySQL connection"
$mysqlArgs = @(
  "-h", $dbHost,
  "-P", $dbPort,
  "-u", $dbUser,
  ("-p" + $dbPassword),
  "-e", "SELECT 1;"
)
try
{
  & $mysqlExe @mysqlArgs
  Write-Host "MySQL connection OK."
}
catch
{
  Write-Warning "MySQL connection failed. Check DB_USER and DB_PASSWORD in backend/.env."
}

Write-Step "Verify Redis PING"
if ($resolvedRedisCli) {
  try
  {
    $redisArgs = @("-h", $redisHost, "-p", $redisPort)
    if ($redisPassword) {
      $redisArgs += @("-a", $redisPassword)
    }
    $redisArgs += "ping"
    $redisPing = & $resolvedRedisCli @redisArgs
    Write-Host "Redis response: $redisPing"
  }
  catch
  {
    Write-Warning "Redis PING failed. Start Redis first."
  }
}

Write-Step "Run Django system check"
Push-Location $backendDir
try
{
  & $pythonExe manage.py check
}
finally
{
  Pop-Location
}

Write-Step "Run Django DB/Cache smoke check"
Push-Location $backendDir
try
{
  & $pythonExe $smokeScript
}
finally
{
  Pop-Location
}
