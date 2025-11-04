#requires -Version 5.1
<#
Script: monitor_prod.ps1
Purpose: 快速告警脚本（本机/容器）用于轮询 Docker 容器日志、采样 MySQL/Redis 运行时指标，并在达到阈值时触发即时告警。
Usage:
  powershell -ExecutionPolicy Bypass -File .\monitor_prod.ps1 -Mode poll -SampleIntervalSec 30 `
    -DockerBackendContainer mtm-helper-backend-1 -DockerNginxContainer mtm-helper-nginx-1 `
    -MySQLHost 127.0.0.1 -MySQLPort 3306 -MySQLUser monitor -MySQLPassword <YOUR_PWD> `
    -RedisHost 127.0.0.1 -RedisPort 6379 -RedisPassword <YOUR_PWD>

注意:
- 默认值仅为占位，请根据生产环境显式传入参数，不要在脚本中硬编码真实口令。
- 阈值请在试运行后结合生产负载调整，避免误报或漏报。
#>

param(
  [ValidateSet('poll','oneshot')]
  [string]$Mode = 'poll',

  # Docker 容器名（根据实际 compose 项目名称调整）
  [string]$DockerBackendContainer = 'mtm-helper-backend-1',
  [string]$DockerNginxContainer  = 'mtm-helper-nginx-1',
  [string]$DockerCliPath = 'D:\Application\Docker\docker\docker.exe',

  # MySQL 连接参数（建议使用只读账号，避免使用 root）
  [string]$MySQLHost = '127.0.0.1',
  [int]$MySQLPort    = 3306,
  [string]$MySQLUser = 'monitor',
  [string]$MySQLPassword = '',
  [string]$MySQLCliPath = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe',

  # Redis 连接参数
  [string]$RedisHost = '127.0.0.1',
  [int]$RedisPort    = 6379,
  [string]$RedisPassword = '',
  [string]$RedisCliPath = 'D:\Redis-x64-3.0.504\redis-cli.exe',

  # 采样与阈值
  [int]$SampleIntervalSec = 30,
  [int]$ErrorBurstThreshold = 5,
  [int]$MySQLConnWarnThreshold = 200,
  [int]$RedisLatencyWarnMs = 50,

  # Django 日志与回滚参数
  [string]$LogPath = 'E:\mtm-helper\backend\logs\django.log',
  [int]$WindowSeconds = 60,
  [int]$Threshold = 8,
  [string]$KeyPrefix = 'mtm-helper',
  [int]$Version = 1,
  [switch]$AutoRollback,
  [string]$EnvPath = 'E:\mtm-helper\backend\.env'
)

# 错误匹配 Regex 模板
$Global:ErrorRegex = @{
  Nginx502 = '\b(502 Bad Gateway|upstream prematurely closed connection|connection refused)\b';
  Nginx504 = '\b(504 Gateway Time-out|upstream timed out)\b';
  GunicornTimeout = '\bWorker timeout\b';
  DjangoTraceback = 'Traceback \(most recent call last\):';
  MySQLError = '\b(ER_[A-Z_]+|ERROR \d{4})\b';
  RedisTimeout = '\b(timeout|BUSY|LOADING|MOVED)\b';
}

function Write-Info {
  param(
    [string]$Message
  )
  $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  Write-Host "[INFO][$ts] $Message" -ForegroundColor Cyan
}

function Write-Warn {
  param(
    [string]$Message
  )
  $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  Write-Host "[WARN][$ts] $Message" -ForegroundColor Yellow
}

function Write-ErrorLine {
  param(
    [string]$Message
  )
  $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  Write-Host "[ALERT][$ts] $Message" -ForegroundColor Red
}

<#
Function: Get-MySQLMetrics
Purpose: 采样 MySQL 当前连接数与最大连接数，并返回结构化结果。
Params: 使用脚本顶层参数 MySQLHost/Port/User/Password
Returns: @{ ThreadsConnected = <int>; MaxConnections = <int> }
#>
function Get-MySQLMetrics {
  try {
    $query = "SHOW GLOBAL STATUS LIKE 'Threads_connected'; SHOW VARIABLES LIKE 'max_connections';"
    # 优先使用 MySQLCliPath，如果不存在则回退到 PATH 中的 mysql
    $mysqlExe = $MySQLCliPath
    if (-not (Test-Path $mysqlExe)) { $mysqlExe = 'mysql' }
    $output = & $mysqlExe -h $MySQLHost -P $MySQLPort -u $MySQLUser "-p$MySQLPassword" -N -e $query 2>$null
    # 解析两列输出：Name<TAB>Value
    $threads = 0
    $maxConn = 0
    foreach ($line in $output) {
      $parts = $line -split "\t"
      if ($parts.Length -ge 2) {
        switch ($parts[0]) {
          'Threads_connected' { $threads = [int]$parts[1] }
          'max_connections'   { $maxConn = [int]$parts[1] }
        }
      }
    }
    if (($output -eq $null -or $output.Count -eq 0) -and $threads -eq 0 -and $maxConn -eq 0) {
      return @{ ThreadsConnected = -1; MaxConnections = -1 }
    }
    return @{ ThreadsConnected = $threads; MaxConnections = $maxConn }
  }
  catch {
    Write-Warn "MySQL 指标采样失败: $($_.Exception.Message)"
    return @{ ThreadsConnected = -1; MaxConnections = -1 }
  }
}

<#
Function: Get-RedisMetrics
Purpose: 使用 redis-cli 测量延迟（PING 往返）并解析关键 INFO 指标。
Params: RedisCliPath/RedisHost/RedisPort/RedisPassword
Returns: @{ LatencyMs = <int>; ConnectedClients = <int>; OpsPerSec = <int>; UsedMemoryHuman = <string> }
#>
function Get-RedisMetrics {
  try {
    if (-not (Test-Path $RedisCliPath)) {
      throw "redis-cli 未找到: $RedisCliPath"
    }
    # 延迟测量
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $pingOut = & $RedisCliPath -h $RedisHost -p $RedisPort -a $RedisPassword ping 2>$null
    $sw.Stop()
    $latencyMs = [int]$sw.ElapsedMilliseconds
    if ($pingOut -notmatch '^PONG') { Write-Warn "Redis PING 未返回 PONG: $pingOut" }

    # INFO 指标解析
    $info = & $RedisCliPath -h $RedisHost -p $RedisPort -a $RedisPassword info 2>$null
    $clients = 0; $ops = 0; $memHuman = ''
    foreach ($line in $info) {
      if ($line -like 'connected_clients*') { $clients = [int]($line -split ':' )[1] }
      elseif ($line -like 'instantaneous_ops_per_sec*') { $ops = [int]($line -split ':' )[1] }
      elseif ($line -like 'used_memory_human*') { $memHuman = ($line -split ':' )[1] }
    }
    return @{ LatencyMs = $latencyMs; ConnectedClients = $clients; OpsPerSec = $ops; UsedMemoryHuman = $memHuman }
  }
  catch {
    Write-Warn "Redis 指标采样失败: $($_.Exception.Message)"
    return @{ LatencyMs = -1; ConnectedClients = -1; OpsPerSec = -1; UsedMemoryHuman = '' }
  }
}

<#
Function: Get-DjangoErrorCount
Purpose: 读取 Django 日志文件，统计最近 WindowSeconds 内的 Redis 相关错误次数（多种正则）。
Params: 使用顶层参数 LogPath/WindowSeconds
Returns: [int] 错误次数
#>
function Get-DjangoErrorCount {
  if (-not (Test-Path $LogPath)) { return 0 }
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
    foreach ($re in $regexes) {
      if ($line -match $re) { $count++; break }
    }
  }
  return $count
}

<#
Function: Get-RedisHealthDetailed
Purpose: 使用 redis-cli 检查短信验证码/限流键前缀，并采样 TTL；用于 Django 短信通道的健康检查。
Params: RedisCliPath/RedisHost/RedisPort/RedisPassword/KeyPrefix/Version
Returns: [pscustomobject] @{ Connected; Keys; SampleTTL; Errors }
#>
function Get-RedisHealthDetailed {
  $cli = $RedisCliPath
  $result = [pscustomobject]@{ Connected = $false; Keys = @(); SampleTTL = @{}; Errors = @() }
  try {
    if (-not (Test-Path $cli)) { $result.Errors += "redis-cli not found: $cli"; return $result }
    $keyspace = & $cli -h $RedisHost -p $RedisPort -a $RedisPassword INFO KEYSPACE 2>&1
    if ($LASTEXITCODE -eq 0 -and $keyspace) { $result.Connected = $true }
    $prefix = "${KeyPrefix}:${Version}:sms:"
    $keys = & $cli -h $RedisHost -p $RedisPort -a $RedisPassword KEYS "$prefix*" 2>&1
    if ($LASTEXITCODE -eq 0) { $result.Keys = ($keys -split "`n") | Where-Object { $_ -match "^${KeyPrefix}:${Version}:" } }
    $codeKey = "${KeyPrefix}:${Version}:sms:code:13800138000"
    $rateKey = "${KeyPrefix}:${Version}:sms:rate:13800138000"
    $ttl1 = & $cli -h $RedisHost -p $RedisPort -a $RedisPassword TTL $codeKey 2>&1
    $ttl2 = & $cli -h $RedisHost -p $RedisPort -a $RedisPassword TTL $rateKey 2>&1
    $result.SampleTTL = @{ $codeKey = $ttl1; $rateKey = $ttl2 }
  }
  catch { $result.Errors += $_.Exception.Message }
  return $result
}

<#
Function: Toggle-SpugPushDisabled
Purpose: 将 .env 中的 SPUG_PUSH_ENABLED 设置为 false，用于自动回滚短信推送。
Params: 使用顶层参数 EnvPath
Returns: [bool]
#>
function Toggle-SpugPushDisabled {
  try {
    if (-not (Test-Path $EnvPath)) { return $false }
    $content = Get-Content -Path $EnvPath
    $updated = $false
    $new = @()
    foreach ($line in $content) {
      if ($line -match '^\s*SPUG_PUSH_ENABLED\s*=') { $new += 'SPUG_PUSH_ENABLED=false'; $updated = $true }
      else { $new += $line }
    }
    if (-not $updated) { $new += 'SPUG_PUSH_ENABLED=false' }
    Set-Content -Path $EnvPath -Value $new -Encoding UTF8
    return $true
  }
  catch { Write-Warn "更新 .env 失败: $($_.Exception.Message)"; return $false }
}

<#
Function: Send-Alert
Purpose: 当触发告警条件时输出高亮日志并发出蜂鸣。
Params: -Message <string>
Returns: None
#>
function Send-Alert {
  param([string]$Message)
  Write-ErrorLine $Message
  try { [Console]::Beep(1000, 300) } catch {}
}

<#
Function: Poll-Once
Purpose: 执行一次采样轮询，包含 Docker 日志错误计数、MySQL/Redis 指标，以及 Django 日志与短信通道健康检查。
Params: 使用顶层参数与全局 Regex
Returns: None
#>
function Poll-Once {
  Write-Info "开始一次采样轮询..."

  # 1) Docker 日志错误采样
  if (Get-Command -Name Get-DockerRecentErrors -ErrorAction SilentlyContinue) {
    $backErr = Get-DockerRecentErrors -ContainerName $DockerBackendContainer -SinceSec 120
    $ngxErr  = Get-DockerRecentErrors -ContainerName $DockerNginxContainer -SinceSec 120
  }
  else {
    Write-Warn "Get-DockerRecentErrors 未定义，使用内联采样"
    $dockerPath = $DockerCliPath
    if (-not (Test-Path $dockerPath)) { $dockerPath = 'docker' }
    $sinceArg = "${120}s"
    $makeSample = {
      param($container)
      if (-not (Get-Command $dockerPath -ErrorAction SilentlyContinue) -and -not (Test-Path $dockerPath)) { return [pscustomobject]@{ Count = 0; Samples = @() } }
      try {
        $logs = & $dockerPath logs $container --since $sinceArg 2>&1
        $count = 0
        $samples = New-Object System.Collections.Generic.List[string]
        foreach ($line in $logs) {
          foreach ($kv in $Global:ErrorRegex.GetEnumerator()) {
            if ($line -match $kv.Value) {
              $count++
              if ($samples.Count -lt 5) { $samples.Add($line) }
              break
            }
          }
        }
        return [pscustomobject]@{ Count = $count; Samples = $samples.ToArray() }
      }
      catch { return [pscustomobject]@{ Count = 0; Samples = @() } }
    }
    $backErr = & $makeSample $DockerBackendContainer
    $ngxErr  = & $makeSample $DockerNginxContainer
  }

  Write-Info "Backend 最近错误计数: $($backErr.Count) | Nginx 最近错误计数: $($ngxErr.Count)"
  if ($backErr.Count -ge $ErrorBurstThreshold) {
    Send-Alert "Backend 错误突发: $($backErr.Count) 条"
    $backErr.Samples | ForEach-Object { Write-ErrorLine "Backend样本: $_" }
  }
  if ($ngxErr.Count -ge $ErrorBurstThreshold) {
    Send-Alert "Nginx 错误突发: $($ngxErr.Count) 条"
    $ngxErr.Samples | ForEach-Object { Write-ErrorLine "Nginx样本: $_" }
  }

  # 2) MySQL 指标采样
  $mysql = Get-MySQLMetrics
  if ($mysql.ThreadsConnected -ge 0) {
    Write-Info "MySQL Threads_connected=$($mysql.ThreadsConnected), max_connections=$($mysql.MaxConnections)"
    if ($mysql.ThreadsConnected -ge $MySQLConnWarnThreshold) {
      Send-Alert "MySQL 连接接近阈值: $($mysql.ThreadsConnected)/$($mysql.MaxConnections)"
    }
  }

  # 3) Redis 指标采样
  $redis = Get-RedisMetrics
  if ($redis.LatencyMs -ge 0) {
    Write-Info "Redis latency=$($redis.LatencyMs)ms, clients=$($redis.ConnectedClients), ops/sec=$($redis.OpsPerSec), mem=$($redis.UsedMemoryHuman)"
    if ($redis.LatencyMs -ge $RedisLatencyWarnMs) {
      Send-Alert "Redis 延迟过高: $($redis.LatencyMs)ms"
    }
  }

  # 4) Django 日志与短信通道健康检查
  Write-Info "Django 日志错误计数与短信通道健康检查..."
  $err = Get-DjangoErrorCount
  Write-Info "[Log] ErrorCount(last ${WindowSeconds}s) = $err"
  $detail = Get-RedisHealthDetailed
  if ($detail.Keys.Count -gt 0) { Write-Info "Redis 键样本:`n$($detail.Keys | Out-String)" }
  foreach ($kv in $detail.SampleTTL.GetEnumerator()) { Write-Info "Redis TTL $($kv.Key) => $($kv.Value)" }
  if ($detail.Errors.Count -gt 0) { Write-Warn "Redis 详细检查错误: $($detail.Errors -join '; ')" }

  if ($err -ge $Threshold) {
    Send-Alert "[Alert] Redis error rate exceeded threshold: $err >= $Threshold"
    if ($AutoRollback) {
      $ok = Toggle-SpugPushDisabled
      if ($ok) {
        Write-Info "[Rollback] SPUG_PUSH_ENABLED=false applied to $EnvPath"
        Write-Info "[Action Required] 请平滑重启后端服务以生效（先停止旧进程，再启动，避免重复启动）。"
      }
      else { Write-Warn "[Rollback] 更新 .env 失败，请手动确认并修改。" }
    }
    else { Write-Info "[Advice] 建议临时关闭Spug推送：在 .env 设置 SPUG_PUSH_ENABLED=false 并重启后端。" }
  }

  Write-Info "采样结束"
}

# 主执行流程
if ($Mode -eq 'poll') {
  Write-Info "进入循环轮询模式, 间隔 ${SampleIntervalSec}s"
  while ($true) {
    Poll-Once
    Start-Sleep -Seconds $SampleIntervalSec
  }
}
else {
  Write-Info "执行一次性采样"
  Poll-Once
}

<#
Function: Get-DockerRecentErrors
Purpose: 读取指定 Docker 容器最近 N 秒日志，并按全局错误正则进行匹配计数，返回样本。
Params: -ContainerName <string> -SinceSec <int>
Returns: [pscustomobject] @{ Count = <int>; Samples = <string[]> }
#>
function Get-DockerRecentErrors {
  param(
    [Parameter(Mandatory=$true)][string]$ContainerName,
    [int]$SinceSec = 120
  )
  $dockerPath = $DockerCliPath
  if (-not (Test-Path $dockerPath)) { $dockerPath = 'docker' }
  if (-not (Get-Command $dockerPath -ErrorAction SilentlyContinue) -and -not (Test-Path $dockerPath)) {
    Write-Warn "Docker CLI 未找到: $dockerPath"; return [pscustomobject]@{ Count = 0; Samples = @() }
  }
  try {
    # docker logs --since N秒 仅在支持的 Docker 版本可用
    $sinceArg = "${SinceSec}s"
    $logs = & $dockerPath logs $ContainerName --since $sinceArg 2>&1
    $count = 0
    $samples = New-Object System.Collections.Generic.List[string]
    foreach ($line in $logs) {
      foreach ($kv in $Global:ErrorRegex.GetEnumerator()) {
        if ($line -match $kv.Value) {
          $count++
          if ($samples.Count -lt 5) { $samples.Add($line) }
          break
        }
      }
    }
    return [pscustomobject]@{ Count = $count; Samples = $samples.ToArray() }
  }
  catch {
    Write-Warn "读取 Docker 日志失败: $($_.Exception.Message)"
    return [pscustomobject]@{ Count = 0; Samples = @() }
  }
}