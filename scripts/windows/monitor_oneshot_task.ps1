#requires -Version 5.1
<#!
Script: monitor_oneshot_task.ps1
Purpose: 计划任务包装脚本，调用 monitor_prod.ps1 的 oneshot 采样模式，参数使用环境变量以避免在计划任务中暴露明文密码。
#>

# 路径解析（相对当前脚本目录）
$monitor = Join-Path $PSScriptRoot 'monitor_prod.ps1'

# 外部工具路径（根据本机安装路径）
$dockerExe = 'D:\Application\Docker\docker\docker.exe'
$mysqlExe  = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe'
$redisCli  = 'D:\Redis-x64-3.0.504\redis-cli.exe'

# 环境变量口令
$mysqlPwd = $env:MYSQL_PASSWORD
$redisPwd = $env:REDIS_PASSWORD

# 基本参数
$mysqlHost = '127.0.0.1'
$mysqlPort = 3306
$mysqlUser = 'monitor'
$redisHost = '127.0.0.1'
$redisPort = 6379
$logPath   = 'E:\mtm-helper\backend\logs\django.log'

# 记录计划任务执行输出到转录日志
$transcript = 'E:\mtm-helper\backend\logs\monitor_task.log'
Start-Transcript -Path $transcript -Append | Out-Null
try {
  # 触发一次性采样
  & $monitor -Mode oneshot `
    -DockerCliPath $dockerExe `
    -MySQLHost $mysqlHost -MySQLPort $mysqlPort -MySQLUser $mysqlUser -MySQLPassword $mysqlPwd -MySQLCliPath $mysqlExe `
    -RedisHost $redisHost -RedisPort $redisPort -RedisPassword $redisPwd -RedisCliPath $redisCli `
    -LogPath $logPath -WindowSeconds 60 -Threshold 8 -AutoRollback
} finally {
  Stop-Transcript | Out-Null
}