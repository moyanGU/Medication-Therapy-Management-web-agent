# MySQL 数据库安全巡检函数库
# 创建日期: 2025-09-29
# 用途: 提供可复用的数据库巡检与安全审计功能

# 全局配置
$global:MySQLExtraFile = "E:\mtm-helper\backend\.private\mysql-extra.cnf"
$global:MySQLPath = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
$global:DefaultReport = "E:\mtm-helper\docs\AUDIT_DB_LATEST.txt"

# 验证环境与依赖
function Test-MySQLAuditEnvironment {
    param (
        [string]$MySQLPath = $global:MySQLPath,
        [string]$ExtraFile = $global:MySQLExtraFile
    )
    
    $result = @{
        MySQLExists = $false
        ExtraFileExists = $false
        CanConnect = $false
        ErrorMessage = $null
    }
    
    try {
        # 检查 MySQL 客户端
        if (Test-Path $MySQLPath) {
            $result.MySQLExists = $true
        } else {
            $result.ErrorMessage = "MySQL 客户端未找到: $MySQLPath"
            return $result
        }
        
        # 检查凭据文件
        if (Test-Path $ExtraFile) {
            $result.ExtraFileExists = $true
        } else {
            $result.ErrorMessage = "MySQL 凭据文件未找到: $ExtraFile"
            return $result
        }
        
        # 测试连接
        $testCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"SELECT 'CONNECTION_TEST_OK' AS status;`" 2>&1"
        $testResult = Invoke-Expression $testCmd
        
        if ($testResult -match "CONNECTION_TEST_OK") {
            $result.CanConnect = $true
        } else {
            $result.ErrorMessage = "MySQL 连接测试失败: $testResult"
        }
    } catch {
        $result.ErrorMessage = "环境检查异常: $_"
    }
    
    return $result
}

# 创建新的审计报告
function New-MySQLAuditReport {
    param (
        [string]$ReportPath = $global:DefaultReport,
        [string]$Title = "MySQL 数据库安全审计报告",
        [switch]$Force
    )
    
    if ((Test-Path $ReportPath) -and -not $Force) {
        Write-Warning "报告文件已存在: $ReportPath. 使用 -Force 参数覆盖."
        return $false
    }
    
    try {
        $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        $content = @"
===== $Title - $timestamp =====
审计开始时间: $timestamp
执行环境: $(Get-Location)
MySQL 客户端: $($global:MySQLPath)
凭据文件: $($global:MySQLExtraFile)

"@
        Set-Content -Path $ReportPath -Value $content -Encoding UTF8
        Write-Host "已创建新的审计报告: $ReportPath"
        return $true
    } catch {
        Write-Error "创建审计报告失败: $_"
        return $false
    }
}

# 执行 MySQL 查询并追加到报告
function Invoke-MySQLQuery {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Query,
        [string]$ReportPath = $global:DefaultReport,
        [string]$MySQLPath = $global:MySQLPath,
        [string]$ExtraFile = $global:MySQLExtraFile,
        [string]$SectionTitle,
        [switch]$AppendToReport
    )
    
    try {
        if ($SectionTitle) {
            if ($AppendToReport) {
                Add-Content -Path $ReportPath -Value "`n-- $SectionTitle --" -Encoding UTF8
            } else {
                Write-Host "`n-- $SectionTitle --"
            }
        }
        
        $cmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"$Query`" 2>&1"
        $result = Invoke-Expression $cmd
        
        if ($AppendToReport) {
            $result | Out-File -FilePath $ReportPath -Append -Encoding UTF8
        } else {
            return $result
        }
    } catch {
        $errorMsg = "MySQL 查询执行失败: $_"
        if ($AppendToReport) {
            Add-Content -Path $ReportPath -Value $errorMsg -Encoding UTF8
        } else {
            Write-Error $errorMsg
        }
    }
}

# 执行标准巡检并追加到报告
function Invoke-MySQLAudit {
    param (
        [string]$ReportPath = $global:DefaultReport,
        [string]$CheckName = "PERIODIC_CHECK",
        [string]$MySQLPath = $global:MySQLPath,
        [string]$ExtraFile = $global:MySQLExtraFile,
        [string]$TestDBScript = "E:\mtm-helper\backend\test_db.py",
        [switch]$CreateNewReport
    )
    
    # 验证环境
    $envCheck = Test-MySQLAuditEnvironment -MySQLPath $MySQLPath -ExtraFile $ExtraFile
    if (-not $envCheck.CanConnect) {
        Write-Error "环境检查失败: $($envCheck.ErrorMessage)"
        return $false
    }
    
    # 创建或追加报告
    if ($CreateNewReport) {
        if (-not (New-MySQLAuditReport -ReportPath $ReportPath -Force)) {
            return $false
        }
    }
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -Path $ReportPath -Value "`n===== SETUP: defaults-extra-file verified, $CheckName - $timestamp =====" -Encoding UTF8
    Add-Content -Path $ReportPath -Value "WorkingDir: $(Get-Location) | mysql: $MySQLPath" -Encoding UTF8
    
    # 核心指标
    Write-Host "[METRICS] 采集核心指标"
    Invoke-MySQLQuery -Query "SHOW GLOBAL STATUS LIKE 'Aborted_connects';" -ReportPath $ReportPath -AppendToReport -SectionTitle "核心指标 - Aborted_connects"
    Invoke-MySQLQuery -Query "SHOW GLOBAL STATUS LIKE 'Threads_connected';" -ReportPath $ReportPath -AppendToReport
    Invoke-MySQLQuery -Query "SHOW GLOBAL STATUS LIKE 'Uptime';" -ReportPath $ReportPath -AppendToReport
    Invoke-MySQLQuery -Query "SHOW GLOBAL STATUS LIKE 'Connection_errors_%';" -ReportPath $ReportPath -AppendToReport -SectionTitle "连接错误家族指标"
    
    # 账号与插件分布
    Write-Host "[USER] 采集账号与插件分布"
    Invoke-MySQLQuery -Query "SELECT plugin, COUNT(*) AS cnt FROM mysql.user GROUP BY plugin ORDER BY cnt DESC;" -ReportPath $ReportPath -AppendToReport -SectionTitle "账号插件分布"
    Invoke-MySQLQuery -Query "SELECT 'guard_admin_count' AS label, COUNT(*) AS cnt FROM mysql.user WHERE user='guard_admin';" -ReportPath $ReportPath -AppendToReport -SectionTitle "guard_admin 计数"
    Invoke-MySQLQuery -Query "SELECT user, host FROM mysql.user WHERE host='%' ORDER BY user, host;" -ReportPath $ReportPath -AppendToReport -SectionTitle "通配主机账户列表"
    
    # 应用侧连通性自检
    Write-Host "[APP] 执行应用侧连通性自检"
    Add-Content -Path $ReportPath -Value "`n-- Application connectivity self-check --" -Encoding UTF8
    
    $pyCandidates = @(
        "E:\mtm-helper\backend\.venv\Scripts\python.exe",
        "E:\mtm-helper\.venv\Scripts\python.exe",
        "E:\mtm-helper\backend\venv\Scripts\python.exe",
        "python"
    )
    $pyExe = $pyCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    
    if ($pyExe -and (Test-Path $TestDBScript)) {
        & $pyExe $TestDBScript 2>&1 | Out-File -FilePath $ReportPath -Append -Encoding UTF8
        Write-Host "[APP] 自检完成"
    } else {
        $warnMsg = "[WARN] Python 虚拟环境未找到或测试脚本不存在，跳过应用侧自检"
        Add-Content -Path $ReportPath -Value $warnMsg -Encoding UTF8
        Write-Warning $warnMsg
    }
    
    Add-Content -Path $ReportPath -Value "===== END OF $CheckName =====" -Encoding UTF8
    Write-Host "[DONE] 巡检已追加到报告: $ReportPath"
    return $true
}

# 解析巡检报告并输出摘要
function Get-MySQLAuditSummary {
    param (
        [string]$ReportPath = $global:DefaultReport,
        [string]$CheckName = "PERIODIC_CHECK"
    )
    
    if (!(Test-Path $ReportPath)) {
        Write-Error "报告文件不存在: $ReportPath"
        return $null
    }
    
    $content = Get-Content -Path $ReportPath
    $startMatch = $content | Select-String -Pattern "$CheckName" | Select-Object -Last 1
    $endMatch = $content | Select-String -Pattern "END OF $CheckName" | Select-Object -Last 1
    
    if (!$startMatch -or !$endMatch) {
        Write-Warning "未找到巡检区块标记: $CheckName"
        return $null
    }
    
    $start = $startMatch.LineNumber
    $end = $endMatch.LineNumber
    $slice = $content[($start-1)..($end-1)]
    
    # 解析指标
    $summary = @{
        CheckName = $CheckName
        Timestamp = $null
        AbortedConnects = $null
        ThreadsConnected = $null
        Uptime = $null
        ConnectionErrors = @()
        GuardAdminCount = $null
        WildcardHostCount = 0
        PluginDistribution = @()
        ApplicationConnectivity = $null
    }
    
    # 提取时间戳
    $timestampLine = $slice | Where-Object { $_ -match "$CheckName - (.+)$" } | Select-Object -First 1
    if ($timestampLine -and $timestampLine -match "$CheckName - (.+)$") {
        $summary.Timestamp = $Matches[1]
    }
    
    # 提取核心指标
    $abortedLine = $slice | Where-Object { $_ -match "^Aborted_connects\s+(\d+)$" } | Select-Object -First 1
    if ($abortedLine -and $abortedLine -match "^Aborted_connects\s+(\d+)$") {
        $summary.AbortedConnects = [int]$Matches[1]
    }
    
    $threadsLine = $slice | Where-Object { $_ -match "^Threads_connected\s+(\d+)$" } | Select-Object -First 1
    if ($threadsLine -and $threadsLine -match "^Threads_connected\s+(\d+)$") {
        $summary.ThreadsConnected = [int]$Matches[1]
    }
    
    $uptimeLine = $slice | Where-Object { $_ -match "^Uptime\s+(\d+)$" } | Select-Object -First 1
    if ($uptimeLine -and $uptimeLine -match "^Uptime\s+(\d+)$") {
        $summary.Uptime = [int]$Matches[1]
    }
    
    # 提取连接错误
    foreach ($line in ($slice | Where-Object { $_ -match "^Connection_errors_\w+\s+\d+$" })) {
        if ($line -match "^(Connection_errors_\w+)\s+(\d+)$") {
            $summary.ConnectionErrors += [PSCustomObject]@{
                Name = $Matches[1]
                Value = [int]$Matches[2]
            }
        }
    }
    
    # 提取 guard_admin 计数
    $guardLine = $slice | Where-Object { $_ -match "^guard_admin_count\s+(\d+)$" } | Select-Object -First 1
    if ($guardLine -and $guardLine -match "^guard_admin_count\s+(\d+)$") {
        $summary.GuardAdminCount = [int]$Matches[1]
    }
    
    # 提取通配主机账户
    $wildList = $slice | Where-Object { $_ -match "^\S+\s+%$" }
    $summary.WildcardHostCount = ($wildList | Measure-Object).Count
    
    # 提取插件分布
    $inPluginSection = $false
    foreach ($line in $slice) {
        if ($line -match "^plugin\s+cnt$") {
            $inPluginSection = $true
            continue
        }
        
        if ($inPluginSection -and $line -match "^([A-Za-z0-9_]+)\s+(\d+)$") {
            $summary.PluginDistribution += [PSCustomObject]@{
                Plugin = $Matches[1]
                Count = [int]$Matches[2]
            }
            continue
        }
        
        if ($inPluginSection -and -not ($line -match "^([A-Za-z0-9_]+)\s+(\d+)$")) {
            $inPluginSection = $false
        }
    }
    
    # 提取应用连通性
    $connOk = $slice | Where-Object { $_ -match "连接到数据库.*成功" } | Measure-Object
    if ($connOk.Count -gt 0) {
        $summary.ApplicationConnectivity = "成功"
    } else {
        $connFail = $slice | Where-Object { $_ -match "连接到数据库.*失败|连接错误" } | Measure-Object
        if ($connFail.Count -gt 0) {
            $summary.ApplicationConnectivity = "失败"
        }
    }
    
    return $summary
}

# 输出格式化摘要
function Format-MySQLAuditSummary {
    param (
        [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
        [PSObject]$Summary
    )
    
    process {
        if ($null -eq $Summary) {
            Write-Warning "无法格式化空摘要"
            return
        }
        
        Write-Host "`n===== $($Summary.CheckName) 摘要 ($($Summary.Timestamp)) ====="
        Write-Host "核心指标:"
        Write-Host "  - Aborted_connects: $($Summary.AbortedConnects)"
        Write-Host "  - Threads_connected: $($Summary.ThreadsConnected)"
        Write-Host "  - Uptime: $($Summary.Uptime)"
        
        Write-Host "`n连接错误家族:"
        if ($Summary.ConnectionErrors.Count -gt 0) {
            $nonZeroErrors = $Summary.ConnectionErrors | Where-Object { $_.Value -gt 0 }
            $totalErrors = ($Summary.ConnectionErrors | Measure-Object -Property Value -Sum).Sum
            
            Write-Host "  - 总计: $totalErrors (共 $($Summary.ConnectionErrors.Count) 项)"
            if ($nonZeroErrors.Count -gt 0) {
                Write-Host "  - 非零项:"
                foreach ($err in $nonZeroErrors) {
                    Write-Host "    * $($err.Name): $($err.Value)"
                }
            } else {
                Write-Host "  - 所有项均为零 (正常)"
            }
        } else {
            Write-Host "  - 未解析到连接错误指标"
        }
        
        Write-Host "`n账号安全:"
        Write-Host "  - guard_admin 计数: $($Summary.GuardAdminCount)"
        Write-Host "  - 通配主机账户数量: $($Summary.WildcardHostCount)"
        
        Write-Host "`n插件分布:"
        if ($Summary.PluginDistribution.Count -gt 0) {
            foreach ($plugin in $Summary.PluginDistribution) {
                Write-Host "  - $($plugin.Plugin): $($plugin.Count)"
            }
        } else {
            Write-Host "  - 未解析到插件分布"
        }
        
        Write-Host "`n应用连通性: $($Summary.ApplicationConnectivity)"
        Write-Host "===== 摘要结束 ====="
    }
}

# 创建安全凭据文件
function New-MySQLCredentialFile {
    param (
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        [Parameter(Mandatory=$true)]
        [string]$Username,
        [Parameter(Mandatory=$true)]
        [string]$Password,
        [string]$Host = "127.0.0.1",
        [int]$Port = 3306,
        [switch]$Force
    )
    
    if ((Test-Path $FilePath) -and -not $Force) {
        Write-Warning "凭据文件已存在: $FilePath. 使用 -Force 参数覆盖."
        return $false
    }
    
    try {
        $fileDir = Split-Path -Parent $FilePath
        if (!(Test-Path $fileDir)) {
            New-Item -ItemType Directory -Path $fileDir -Force | Out-Null
        }
        
        $content = @"
[client]
user=$Username
password=$Password
host=$Host
port=$Port
"@
        
        Set-Content -Path $FilePath -Value $content -Encoding UTF8
        
        # 设置文件权限 (仅当前用户可读写)
        $acl = Get-Acl -Path $FilePath
        $acl.SetAccessRuleProtection($true, $false)
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
            "FullControl",
            "Allow"
        )
        $acl.AddAccessRule($rule)
        Set-Acl -Path $FilePath -AclObject $acl
        
        Write-Host "已创建安全凭据文件: $FilePath"
        
        # 添加到 .gitignore 或 .git/info/exclude
        $gitExcludePath = Join-Path (Split-Path -Parent (Split-Path -Parent $FilePath)) ".git\info\exclude"
        if (Test-Path $gitExcludePath) {
            $relativePath = $FilePath.Substring((Split-Path -Parent (Split-Path -Parent $FilePath)).Length + 1)
            $dirPath = Split-Path -Parent $relativePath
            
            $excludeContent = Get-Content -Path $gitExcludePath
            $patterns = @($relativePath, "$dirPath/")
            
            $updated = $false
            foreach ($pattern in $patterns) {
                if ($excludeContent -notcontains $pattern) {
                    Add-Content -Path $gitExcludePath -Value $pattern
                    $updated = $true
                }
            }
            
            if ($updated) {
                Write-Host "已将凭据文件路径添加到 Git exclude 列表"
            }
        }
        
        return $true
    } catch {
        Write-Error "创建凭据文件失败: $_"
        return $false
    }
}

# 导出函数
Export-ModuleMember -Function Test-MySQLAuditEnvironment, New-MySQLAuditReport, Invoke-MySQLQuery, Invoke-MySQLAudit, Get-MySQLAuditSummary, Format-MySQLAuditSummary, New-MySQLCredentialFile
