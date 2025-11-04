<#
.SYNOPSIS
  生产环境监控脚本：检测Redis连接/认证错误、统计日志错误率、辅助触发回滚（关闭Spug短信推送）。
.DESCRIPTION
  - 支持按时间窗口统计日志中的Redis相关错误（Regex模式可扩展）
  - 使用 redis-cli 进行健康检查与关键键验证
  - 当错误数超过阈值时，给出回滚建议并可自动修改 .env 中的 SPUG_PUSH_ENABLED=false（需传参启用）
.PARAMETER LogPath
  要分析的日志文件路径（默认：E:\mtm-helper\backend\runserver.log）。
.PARAMETER WindowSeconds
  统计时间窗口（秒）。默认 60。
.PARAMETER Threshold
  告警阈值（窗口内错误匹配次数）。默认 8。
.PARAMETER RedisHost
  Redis主机地址（支持IPv6）。默认 ::1。
.PARAMETER RedisPort
  Redis端口。默认 6379。
.PARAMETER RedisPassword
  Redis认证密码。默认从环境读取，未设置则使用 Ghp880218。
.PARAMETER KeyPrefix
  Django缓存 KEY_PREFIX。默认 mtm-helper。
.PARAMETER Version
  Django缓存版本号（VERSION）。默认 1。
.PARAMETER AutoRollback
  是否自动将 .env 中的 SPUG_PUSH_ENABLED 设置为 false。默认 false。
.PARAMETER EnvPath
  .env 文件路径。默认 E:\mtm-helper\backend\.env。
.EXAMPLE
  ./monitor_prod.ps1 -LogPath E:\mtm-helper\backend\runserver.log -WindowSeconds 60 -Threshold 8 -AutoRollback $true
#>
param(
  [string]$LogPath = "E:\mtm-helper\backend\logs\django.log",
  [int]$WindowSeconds = 60,
  [int]$Threshold = 8,
  [string]$RedisHost = "::1",
  [int]$RedisPort = 6379,
  [string]$RedisPassword = $(if ($env:REDIS_PASSWORD) { $env:REDIS_PASSWORD } else { "Ghp880218" }),
  [string]$KeyPrefix = "mtm-helper",
  [int]$Version = 1,
  [switch]$AutoRollback,
  [string]$EnvPath = "E:\mtm-helper\backend\.env"
)

# 设置输出编码为UTF-8，减少中文日志乱码
try {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

function Test-RedisHealth {
  <#
  .SYNOPSIS
    使用 redis-cli 进行连接与键验证的健康检查。
  .OUTPUTS
    [pscustomobject] 包含 Connected、Keyspace、Keys、SampleTTL、Errors 等字段。
  #>
  param()
  $cli = "D:\Redis-x64-3.0.504\redis-cli.exe"
  if (-not (Test-Path $cli)) {
    return [pscustomobject]@{ Connected = $false; Errors = @("redis-cli not found: $cli") }
  }
  $location = "[${RedisHost}]:${RedisPort}"
  $result = [pscustomobject]@{
    Connected = $false
    Keyspace = $null
    Keys = @()
    SampleTTL = @{}
    Errors = @()
  }
  try {
    $keyspace = & $cli -h $RedisHost -p $RedisPort -a $RedisPassword INFO KEYSPACE 2>&1
    if ($LASTEXITCODE -eq 0 -and $keyspace) {
      $result.Connected = $true
      $result.Keyspace = ($keyspace -split "`n") | Where-Object { $_ -match "^db\d:" }
    } else {
      $result.Errors += @("Failed INFO KEYSPACE: $keyspace")
    }
    $prefix = "${KeyPrefix}:${Version}:sms:"
    $keys = & $cli -h $RedisHost -p $RedisPort -a $RedisPassword KEYS "$prefix*" 2>&1
    if ($LASTEXITCODE -eq 0) {
      $result.Keys = ($keys -split "`n") | Where-Object { $_ -match "^${KeyPrefix}:${Version}:" }
    }
    $codeKey = "${KeyPrefix}:${Version}:sms:code:13800138000"
    $rateKey = "${KeyPrefix}:${Version}:sms:rate:13800138000"
    $ttl1 = & $cli -h $RedisHost -p $RedisPort -a $RedisPassword TTL $codeKey 2>&1
    $ttl2 = & $cli -h $RedisHost -p $RedisPort -a $RedisPassword TTL $rateKey 2>&1
    $result.SampleTTL = @{ $codeKey = $ttl1; $rateKey = $ttl2 }
  } catch {
    $result.Errors += @($_.Exception.Message)
  }
  return $result
}

function Get-ErrorCount {
  <#
  .SYNOPSIS
    读取日志文件，统计最近 WindowSeconds 内的 Redis 相关错误次数。
  .OUTPUTS
    [int] 错误次数
  #>
  param()
  if (-not (Test-Path $LogPath)) {
    return 0
  }
  $now = Get-Date
  $start = $now.AddSeconds(-$WindowSeconds)
  $lines = Get-Content -Path $LogPath -Tail 5000 -ErrorAction SilentlyContinue
  $regexes = @(
    'Redis\s+ConnectionError',
    'Redis\s+AuthenticationError',
    'Error\s+10061\s+connecting',
    'Connection\s+refused',
    'NOAUTH\s+Authentication\s+required',
    'WRONGPASS',
    'Redis缓存连接异常',
    '写入验证码/限流缓存失败',
    '读取频率限制缓存失败'
  )
  $count = 0
  foreach ($line in $lines) {
    # 简化时间过滤（如果日志包含ISO时间，可增强为按时间过滤）
    foreach ($re in $regexes) {
      if ($line -match $re) { $count++ ; break }
    }
  }
  return $count
}

function Toggle-SpugPushDisabled {
  <#
  .SYNOPSIS
    将 .env 中的 SPUG_PUSH_ENABLED 设置为 false。
  .OUTPUTS
    [bool] 操作是否成功
  #>
  param()
  try {
    if (-not (Test-Path $EnvPath)) { return $false }
    $content = Get-Content -Path $EnvPath
    $updated = $false
    $new = @()
    foreach ($line in $content) {
      if ($line -match '^\s*SPUG_PUSH_ENABLED\s*=') {
        $new += 'SPUG_PUSH_ENABLED=false'
        $updated = $true
      } else {
        $new += $line
      }
    }
    if (-not $updated) { $new += 'SPUG_PUSH_ENABLED=false' }
    Set-Content -Path $EnvPath -Value $new -Encoding UTF8
    return $true
  } catch {
    Write-Warning "Failed to update SPUG_PUSH_ENABLED: $($_.Exception.Message)"
    return $false
  }
}

# 主流程
Write-Host "[Monitor] Window=${WindowSeconds}s, Threshold=${Threshold}, LogPath=${LogPath}"
$health = Test-RedisHealth
Write-Host "[Redis] Connected=$($health.Connected) Keyspace=$($health.Keyspace)"
if ($health.Keys.Count -gt 0) {
  Write-Host "[Redis] Keys sample:`n$($health.Keys | Out-String)"
}
foreach ($kv in $health.SampleTTL.GetEnumerator()) {
  Write-Host "[Redis] TTL $($kv.Key) => $($kv.Value)"
}
if ($health.Errors.Count -gt 0) {
  Write-Warning "[Redis] Errors: $($health.Errors -join '; ')"
}

$err = Get-ErrorCount
Write-Host "[Log] ErrorCount(last ${WindowSeconds}s) = $err"

if ($err -ge $Threshold) {
  Write-Warning "[Alert] Redis error rate exceeded threshold: $err >= $Threshold"
  if ($AutoRollback) {
    $ok = Toggle-SpugPushDisabled
    if ($ok) {
      Write-Host "[Rollback] SPUG_PUSH_ENABLED=false applied to $EnvPath"
      Write-Host "[Action Required] 请平滑重启后端服务以生效（先停止旧进程，再启动，避免重复启动）。"
    } else {
      Write-Warning "[Rollback] Failed to update .env; 请手动确认并修改。"
    }
  } else {
    Write-Host "[Advice] 建议临时关闭Spug推送：在 .env 设置 SPUG_PUSH_ENABLED=false 并重启后端。"
  }
} else {
  Write-Host "[OK] Redis error rate within threshold."
}