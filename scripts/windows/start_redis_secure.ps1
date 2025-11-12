<#
 .SYNOPSIS
  从 backend/.env 读取 REDIS_PASSWORD 并安全启动本地 Redis（Windows），确保与 Django 配置一致。

 .DESCRIPTION
  - 自动解析仓库根目录下 backend/.env，提取 REDIS_PASSWORD 环境变量。
  - 使用 D:\Redis-x64-3.0.504\redis-server.exe 按仓库根目录下 redis.conf 启动服务。
  - 若读取到 REDIS_PASSWORD，则以 --requirepass 方式启用认证；否则以无密码方式启动（仅用于本地开发）。
  - 输出关键日志，便于控制台诊断。

 .PARAMETER EnvPath
  可选，显式指定 .env 文件路径；不指定时默认读取 仓库根目录/backend/.env。

 .PARAMETER RedisExe
  可选，显式指定 redis-server.exe 路径；默认为 D:\Redis-x64-3.0.504\redis-server.exe。

 .NOTES
  - 请勿将敏感信息提交到版本库。此脚本仅在本地开发环境使用。
  - 启动后可通过 `netstat -ano | findstr 6379` 验证监听端口。
#>

param(
  [string]$EnvPath = "",
  [string]$RedisExe = "D:\\Redis-x64-3.0.504\\redis-server.exe"
)

function Get-RepoRoot {
  <# 获取仓库根目录 #>
  try {
    $root = Resolve-Path (Join-Path $PSScriptRoot "..\..") | Select-Object -ExpandProperty Path
    return $root
  } catch {
    Write-Warning "[start_redis_secure] 无法解析仓库根目录，使用当前脚本目录上两级为根"
    return (Join-Path $PSScriptRoot "..\..")
  }
}

function Parse-DotEnv([string]$Path) {
  <# 解析 .env 文件为字典 #>
  $result = @{}
  if (-not (Test-Path $Path)) {
    Write-Warning "[start_redis_secure] .env 文件不存在: $Path"
    return $result
  }
  Get-Content -Path $Path | ForEach-Object {
    $line = $_.Trim()
    if (-not $line) { return }
    if ($line.StartsWith('#')) { return }
    if ($line -match '^(?<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?<val>.*)$') {
      $key = $Matches['key']
      $val = $Matches['val'].Trim()
      # 去除包裹引号
      if ($val.StartsWith('"') -and $val.EndsWith('"')) { $val = $val.Trim('"') }
      if ($val.StartsWith('\'') -and $val.EndsWith('\'')) { $val = $val.Trim('\'') }
      $result[$key] = $val
    }
  }
  return $result
}

$repoRoot = Get-RepoRoot
Write-Host "[start_redis_secure] 仓库根目录: $repoRoot"

$envFile = if ($EnvPath) { $EnvPath } else { Join-Path $repoRoot "backend\.env" }
Write-Host "[start_redis_secure] 读取 .env: $envFile"
$envVars = Parse-DotEnv -Path $envFile

$redisPassword = $envVars['REDIS_PASSWORD']
if ($redisPassword) {
  Write-Host "[start_redis_secure] 检测到 REDIS_PASSWORD（已屏蔽）"
  # 注入当前会话环境变量，但不回显具体值
  $env:REDIS_PASSWORD = $redisPassword
} else {
  Write-Warning "[start_redis_secure] 未在 .env 中检测到 REDIS_PASSWORD，将以无密码方式启动（仅开发环境允许）"
}

$confPath = Join-Path $repoRoot "redis.conf"
if (-not (Test-Path $confPath)) {
  Write-Error "[start_redis_secure] 未找到 redis.conf: $confPath"
  exit 1
}

if (-not (Test-Path $RedisExe)) {
  Write-Error "[start_redis_secure] 未找到 redis-server.exe: $RedisExe"
  exit 1
}

Write-Host "[start_redis_secure] 使用配置文件启动: $confPath"
if ($redisPassword) {
  Write-Host "[start_redis_secure] 以启用认证方式启动 Redis"
  Start-Process -FilePath $RedisExe -ArgumentList "`"$confPath`"", "--requirepass $redisPassword" -WindowStyle Minimized
} else {
  Write-Host "[start_redis_secure] 以无密码方式启动 Redis（仅开发环境）"
  Start-Process -FilePath $RedisExe -ArgumentList "`"$confPath`"" -WindowStyle Minimized
}

Write-Host "[start_redis_secure] 已发起启动，请使用 'netstat -ano | findstr 6379' 验证监听状态"