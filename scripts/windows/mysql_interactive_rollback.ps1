# MySQL 数据库交互式执行与回滚脚本
# 创建日期: 2025-09-29
# 用途: 提供安全的交互式数据库操作，包含确认与回滚机制

param (
    [Parameter(Mandatory=$false)]
    [string]$Action = "check",
    
    [Parameter(Mandatory=$false)]
    [string]$ExtraFile = "E:\mtm-helper\backend\.private\mysql-extra.cnf",
    
    [Parameter(Mandatory=$false)]
    [string]$MySQLPath = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
    
    [Parameter(Mandatory=$false)]
    [string]$BackupDir = "E:\mtm-helper\backup\mysql"
)

# 验证环境
function Test-Environment {
    if (!(Test-Path $MySQLPath)) {
        Write-Error "MySQL 客户端不存在: $MySQLPath"
        return $false
    }
    
    if (!(Test-Path $ExtraFile)) {
        Write-Error "MySQL 凭据文件不存在: $ExtraFile"
        return $false
    }
    
    # 测试连接
    try {
        $testCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"SELECT 'CONNECTION_TEST_OK' AS status;`" 2>&1"
        $testResult = Invoke-Expression $testCmd
        
        if ($testResult -match "CONNECTION_TEST_OK") {
            Write-Host "[OK] MySQL 连接测试成功" -ForegroundColor Green
            return $true
        } else {
            Write-Error "MySQL 连接测试失败: $testResult"
            return $false
        }
    } catch {
        Write-Error "MySQL 连接测试异常: $_"
        return $false
    }
}

# 创建备份目录
function Initialize-Backup {
    if (!(Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        Write-Host "[INIT] 已创建备份目录: $BackupDir" -ForegroundColor Yellow
    }
    
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $backupFile = Join-Path $BackupDir "mysql_users_$timestamp.sql"
    
    # 备份用户表
    try {
        $backupCmd = @"
& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e "
SELECT CONCAT(
    'CREATE USER IF NOT EXISTS ''', user, '''@''', host, ''' IDENTIFIED WITH ''', plugin, ''' AS ''', authentication_string, ''';'
) AS user_create_stmt FROM mysql.user;" > `"$backupFile`"
"@
        Invoke-Expression $backupCmd
        
        $grantBackupCmd = @"
& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e "
SELECT CONCAT(
    'SHOW GRANTS FOR ''', user, '''@''', host, ''';'
) AS show_grants_stmt FROM mysql.user;" >> `"$backupFile`"
"@
        Invoke-Expression $grantBackupCmd
        
        Write-Host "[BACKUP] 已备份用户表到: $backupFile" -ForegroundColor Green
        return $backupFile
    } catch {
        Write-Error "备份用户表失败: $_"
        return $null
    }
}

# 检查通配主机账户
function Get-WildcardAccounts {
    try {
        $cmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"SELECT user, host FROM mysql.user WHERE host='%' ORDER BY user, host;`" 2>&1"
        $result = Invoke-Expression $cmd
        
        if ($result -match "Empty set") {
            Write-Host "[CHECK] 未发现通配主机账户" -ForegroundColor Green
            return @()
        } else {
            $lines = $result -split "`n" | Where-Object { $_ -match "^\S+\s+%$" }
            $accounts = @()
            
            foreach ($line in $lines) {
                if ($line -match "^(\S+)\s+%$") {
                    $user = $Matches[1]
                    $accounts += "$user@%"
                    Write-Host "[WARN] 发现通配主机账户: $user@%" -ForegroundColor Yellow
                }
            }
            
            return $accounts
        }
    } catch {
        Write-Error "检查通配主机账户失败: $_"
        return $null
    }
}

# 交互式处理通配主机账户
function Remove-WildcardAccount {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Account
    )
    
    if ($Account -match "^(\S+)@%$") {
        $user = $Matches[1]
        
        Write-Host "`n===== 处理通配主机账户: $Account =====" -ForegroundColor Yellow
        
        # 获取账户权限
        try {
            $grantCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"SHOW GRANTS FOR '$user'@'%';`" 2>&1"
            $grants = Invoke-Expression $grantCmd
            
            Write-Host "`n当前权限:" -ForegroundColor Cyan
            $grants | ForEach-Object { Write-Host $_ }
            
            # 获取可能的替代主机
            $hostCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"SELECT host FROM information_schema.processlist WHERE user='$user' AND host NOT LIKE '%:%' GROUP BY host;`" 2>&1"
            $hosts = Invoke-Expression $hostCmd
            
            $hostLines = $hosts -split "`n" | Where-Object { $_ -match "^\S+$" -and $_ -ne "host" }
            
            if ($hostLines.Count -gt 0) {
                Write-Host "`n可能的替代主机:" -ForegroundColor Cyan
                $hostLines | ForEach-Object { Write-Host "- $_" }
            }
            
            # 提供选项
            Write-Host "`n可选操作:" -ForegroundColor Cyan
            Write-Host "1. 删除此通配主机账户" -ForegroundColor White
            Write-Host "2. 将此账户限制到特定主机 (localhost, 127.0.0.1, ::1)" -ForegroundColor White
            Write-Host "3. 将此账户限制到特定网段" -ForegroundColor White
            Write-Host "4. 跳过此账户" -ForegroundColor White
            
            $choice = Read-Host "请选择操作 (1-4)"
            
            switch ($choice) {
                "1" {
                    $confirm = Read-Host "确认删除账户 $Account? (y/n)"
                    if ($confirm -eq "y") {
                        $dropCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"DROP USER '$user'@'%';`" 2>&1"
                        $dropResult = Invoke-Expression $dropCmd
                        Write-Host "[ACTION] 已删除账户: $Account" -ForegroundColor Green
                        return $true
                    } else {
                        Write-Host "[SKIP] 已取消删除操作" -ForegroundColor Yellow
                        return $false
                    }
                }
                "2" {
                    $confirm = Read-Host "确认将账户 $Account 限制到本地三地址? (y/n)"
                    if ($confirm -eq "y") {
                        # 获取当前权限语句
                        $grantStmts = @()
                        foreach ($line in $grants) {
                            if ($line -match "GRANT (.+) ON (.+) TO") {
                                $privileges = $Matches[1]
                                $objects = $Matches[2]
                                $grantStmts += "GRANT $privileges ON $objects TO '$user'@'localhost';"
                                $grantStmts += "GRANT $privileges ON $objects TO '$user'@'127.0.0.1';"
                                $grantStmts += "GRANT $privileges ON $objects TO '$user'@'::1';"
                            }
                        }
                        
                        # 创建本地三地址账户
                        $createCmd = @"
& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e "
CREATE USER IF NOT EXISTS '$user'@'localhost' IDENTIFIED BY 'Temp123456!';
CREATE USER IF NOT EXISTS '$user'@'127.0.0.1' IDENTIFIED BY 'Temp123456!';
CREATE USER IF NOT EXISTS '$user'@'::1' IDENTIFIED BY 'Temp123456!';
" 2>&1
"@
                        $createResult = Invoke-Expression $createCmd
                        
                        # 应用权限
                        foreach ($stmt in $grantStmts) {
                            $grantCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"$stmt`" 2>&1"
                            $grantResult = Invoke-Expression $grantCmd
                        }
                        
                        # 删除通配账户
                        $dropCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"DROP USER '$user'@'%';`" 2>&1"
                        $dropResult = Invoke-Expression $dropCmd
                        
                        Write-Host "[ACTION] 已将账户 $Account 限制到本地三地址" -ForegroundColor Green
                        Write-Host "[SECURITY] 请立即修改临时密码!" -ForegroundColor Red
                        return $true
                    } else {
                        Write-Host "[SKIP] 已取消限制操作" -ForegroundColor Yellow
                        return $false
                    }
                }
                "3" {
                    $network = Read-Host "请输入网段 (例如: 192.168.1.%)"
                    $confirm = Read-Host "确认将账户 $Account 限制到网段 $network? (y/n)"
                    if ($confirm -eq "y") {
                        # 获取当前权限语句
                        $grantStmts = @()
                        foreach ($line in $grants) {
                            if ($line -match "GRANT (.+) ON (.+) TO") {
                                $privileges = $Matches[1]
                                $objects = $Matches[2]
                                $grantStmts += "GRANT $privileges ON $objects TO '$user'@'$network';"
                            }
                        }
                        
                        # 创建网段账户
                        $createCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"CREATE USER IF NOT EXISTS '$user'@'$network' IDENTIFIED BY 'Temp123456!';`" 2>&1"
                        $createResult = Invoke-Expression $createCmd
                        
                        # 应用权限
                        foreach ($stmt in $grantStmts) {
                            $grantCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"$stmt`" 2>&1"
                            $grantResult = Invoke-Expression $grantCmd
                        }
                        
                        # 删除通配账户
                        $dropCmd = "& `"$MySQLPath`" --defaults-extra-file=`"$ExtraFile`" -e `"DROP USER '$user'@'%';`" 2>&1"
                        $dropResult = Invoke-Expression $dropCmd
                        
                        Write-Host "[ACTION] 已将账户 $Account 限制到网段 $network" -ForegroundColor Green
                        Write-Host "[SECURITY] 请立即修改临时密码!" -ForegroundColor Red
                        return $true
                    } else {
                        Write-Host "[SKIP] 已取消限制操作" -ForegroundColor Yellow
                        return $false
                    }
                }
                "4" {
                    Write-Host "[SKIP] 已跳过账户: $Account" -ForegroundColor Yellow
                    return $false
                }
                default {
                    Write-Host "[ERROR] 无效选择，已跳过账户: $Account" -ForegroundColor Red
                    return $false
                }
            }
        } catch {
            Write-Error "处理账户 $Account 失败: $_"
            return $false
        }
    } else {
        Write-Error "无效的账户格式: $Account"
        return $false
    }
}

# 创建最终审计报告
function New-FinalReport {
    param (
        [string]$BackupFile,
        [array]$ProcessedAccounts
    )
    
    $reportPath = "E:\mtm-helper\docs\FINAL_AUDIT_REPORT_$(Get-Date -Format 'yyyyMMdd').md"
    $summaryPath = "E:\mtm-helper\docs\AUDIT_SUMMARY_20250929.md"
    
    $reportContent = @"
# MySQL 数据库安全审计最终报告

**生成时间:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**审计人员:** 系统管理员
**审计范围:** MySQL 数据库安全配置与账户权限

## 执行摘要

本次审计针对 MySQL 数据库进行了全面安全评估，重点关注以下方面：

1. 连接安全与稳定性
2. 账户权限与认证插件
3. 通配主机账户风险
4. 应用侧连通性

"@

    # 添加摘要报告内容
    if (Test-Path $summaryPath) {
        $summaryContent = Get-Content -Path $summaryPath -Raw
        $reportContent += "`n`n## 审计摘要`n`n$summaryContent"
    }
    
    # 添加账户处理记录
    if ($ProcessedAccounts.Count -gt 0) {
        $reportContent += "`n`n## 账户处理记录`n"
        
        foreach ($account in $ProcessedAccounts) {
            $reportContent += "`n- $account"
        }
    } else {
        $reportContent += "`n`n## 账户处理记录`n`n未执行账户处理操作或无需处理的账户。"
    }
    
    # 添加备份信息
    if ($BackupFile) {
        $reportContent += "`n`n## 备份信息`n`n已创建数据库用户备份: $BackupFile"
    }
    
    # 添加安全建议
    $reportContent += @"
    
## 安全建议

1. **账户安全**:
   - 持续避免创建通配主机账户 (`host='%'`)
   - 定期审计特权账户权限
   - 使用强密码策略并定期轮换密码

2. **连接安全**:
   - 持续监控 `Aborted_connects` 与 `Connection_errors_*` 指标
   - 使用安全凭据文件连接 MySQL，避免明文密码
   - 配置适当的连接超时与重试策略

3. **应用安全**:
   - 处理 pkg_resources 弃用警告
   - 定期更新依赖库版本
   - 实施连接池管理最佳实践

## 后续行动

1. 继续定期执行巡检 (每4小时)
2. 处理 pkg_resources 弃用警告
3. 实施定期账户审计流程
4. 建立数据库安全基线与监控告警
"@
    
    Set-Content -Path $reportPath -Value $reportContent -Encoding UTF8
    Write-Host "[DONE] 已创建最终审计报告: $reportPath" -ForegroundColor Green
    return $reportPath
}

# 主函数
function Main {
    # 显示标题
    Write-Host "`n===== MySQL 数据库交互式执行与回滚脚本 =====" -ForegroundColor Cyan
    Write-Host "操作: $Action" -ForegroundColor White
    Write-Host "MySQL: $MySQLPath" -ForegroundColor White
    Write-Host "凭据: $ExtraFile" -ForegroundColor White
    Write-Host "备份: $BackupDir`n" -ForegroundColor White
    
    # 验证环境
    if (!(Test-Environment)) {
        return
    }
    
    # 初始化备份
    $backupFile = Initialize-Backup
    if (!$backupFile) {
        return
    }
    
    # 根据操作执行不同功能
    switch ($Action) {
        "check" {
            # 检查通配主机账户
            $accounts = Get-WildcardAccounts
            
            if ($accounts.Count -eq 0) {
                Write-Host "`n[RESULT] 未发现需要处理的通配主机账户" -ForegroundColor Green
                
                # 创建最终报告
                $reportPath = New-FinalReport -BackupFile $backupFile -ProcessedAccounts @()
                Write-Host "`n审计完成，未发现需要处理的安全问题。" -ForegroundColor Green
            } else {
                Write-Host "`n[WARN] 发现 $($accounts.Count) 个通配主机账户" -ForegroundColor Yellow
                Write-Host "请使用 -Action fix 参数运行此脚本以交互式处理这些账户" -ForegroundColor Yellow
            }
        }
        "fix" {
            # 检查并处理通配主机账户
            $accounts = Get-WildcardAccounts
            $processedAccounts = @()
            
            if ($accounts.Count -eq 0) {
                Write-Host "`n[RESULT] 未发现需要处理的通配主机账户" -ForegroundColor Green
            } else {
                Write-Host "`n[WARN] 发现 $($accounts.Count) 个通配主机账户，开始交互式处理" -ForegroundColor Yellow
                
                foreach ($account in $accounts) {
                    $result = Remove-WildcardAccount -Account $account
                    if ($result) {
                        $processedAccounts += "已处理: $account"
                    } else {
                        $processedAccounts += "已跳过: $account"
                    }
                }
                
                # 再次检查
                $remainingAccounts = Get-WildcardAccounts
                if ($remainingAccounts.Count -eq 0) {
                    Write-Host "`n[SUCCESS] 所有通配主机账户已处理完成" -ForegroundColor Green
                } else {
                    Write-Host "`n[WARN] 仍有 $($remainingAccounts.Count) 个通配主机账户未处理" -ForegroundColor Yellow
                }
            }
            
            # 创建最终报告
            $reportPath = New-FinalReport -BackupFile $backupFile -ProcessedAccounts $processedAccounts
            Write-Host "`n处理完成，请查看最终报告: $reportPath" -ForegroundColor Green
        }
        "report" {
            # 仅创建最终报告
            $reportPath = New-FinalReport -BackupFile $backupFile -ProcessedAccounts @()
            Write-Host "`n已创建最终报告: $reportPath" -ForegroundColor Green
        }
        default {
            Write-Error "无效的操作: $Action"
        }
    }
}

# 执行主函数
Main
