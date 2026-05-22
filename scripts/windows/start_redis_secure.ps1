<#
.SYNOPSIS
  Read REDIS_PASSWORD from backend/.env and start local Redis on Windows.

.DESCRIPTION
  - Default env file: backend/.env
  - Default Redis server: D:\Redis-x64-3.0.504\redis-server.exe
  - If REDIS_PASSWORD exists, start Redis with --requirepass
  - If port 6379 is already listening, skip startup
#>

param(
  [string]$EnvPath = "",
  [string]$RedisExe = ""
)

$ErrorActionPreference = "Stop"

$defaultRedisCandidates = @(
  "D:\\Redis-x64-3.0.504\\redis-server.exe",
  "C:\\Redis\\redis-server.exe",
  "C:\\Program Files\\Redis\\redis-server.exe"
)

function Get-RepoRoot {
  return (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
}

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

function Test-PortListening {
  param([int]$Port)

  $match = netstat -ano | Select-String ":$Port\s+.*LISTENING"
  return $null -ne $match
}

function Resolve-ExecutablePath {
  param(
    [string]$PreferredPath,
    [string[]]$Candidates,
    [string]$CommandName,
    [string]$Label
  )

  if ($PreferredPath) {
    if (Test-Path $PreferredPath) {
      return (Resolve-Path $PreferredPath).Path
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

  throw "Could not find $Label. Pass -RedisExe explicitly or add $CommandName to PATH."
}

$repoRoot = Get-RepoRoot
$envFile = if ($EnvPath) { $EnvPath } else { Join-Path $repoRoot "backend\\.env" }
$redisConf = Join-Path $repoRoot "redis.conf"
$resolvedRedisExe = Resolve-ExecutablePath -PreferredPath $RedisExe -Candidates $defaultRedisCandidates -CommandName "redis-server" -Label "redis-server.exe"

Write-Host "[start_redis_secure] repo root: $repoRoot"
Write-Host "[start_redis_secure] env file : $envFile"
Write-Host "[start_redis_secure] redis exe : $resolvedRedisExe"

if (-not (Test-Path $redisConf)) {
  throw "Missing redis.conf: $redisConf"
}

if (Test-PortListening -Port 6379) {
  Write-Host "[start_redis_secure] Port 6379 is already listening. Skip startup."
  exit 0
}

$envVars = Parse-DotEnv -Path $envFile
$redisPassword = $envVars["REDIS_PASSWORD"]

$arguments = @("`"$redisConf`"")
if ($redisPassword) {
  $arguments += "--requirepass"
  $arguments += $redisPassword
  Write-Host "[start_redis_secure] Starting Redis with requirepass."
}
else {
  Write-Warning "[start_redis_secure] REDIS_PASSWORD not found. Starting Redis without password."
}

Start-Process -FilePath $resolvedRedisExe -ArgumentList $arguments -WindowStyle Minimized
Start-Sleep -Seconds 2

if (Test-PortListening -Port 6379) {
  Write-Host "[start_redis_secure] Redis is listening on 6379."
  exit 0
}

throw "Redis did not start listening on 6379. Please inspect the local Redis process."
