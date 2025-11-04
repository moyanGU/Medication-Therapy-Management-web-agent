# MySQL 数据库监控与日志过滤操作指引

本文档提供了用于监控 MySQL 数据库安全状态的查询语句、日志过滤正则表达式以及常见问题的处理方法。

## 核心监控指标

### 连接与认证监控

```sql
-- 连接中止计数（关键指标，上升趋势需关注）
SHOW GLOBAL STATUS LIKE 'Aborted_connects';

-- 当前连接数
SHOW GLOBAL STATUS LIKE 'Threads_connected';

-- 连接错误家族（全部应为0，任何非零值需立即调查）
SHOW GLOBAL STATUS LIKE 'Connection_errors_%';

-- 最大连接数配置
SHOW VARIABLES LIKE 'max_connections';

-- 连接超时配置
SHOW VARIABLES LIKE '%timeout%';
```

### 账号安全监控

```sql
-- 插件分布（应以 caching_sha2_password 为主）
SELECT plugin, COUNT(*) AS cnt 
FROM mysql.user 
GROUP BY plugin 
ORDER BY cnt DESC;

-- 通配主机账户（应为空，任何结果都需审核）
SELECT user, host 
FROM mysql.user 
WHERE host='%' 
ORDER BY user, host;

-- 特权账户审计（应仅限 root 与必要管理账号）
SELECT user, host 
FROM mysql.user 
WHERE Super_priv='Y' OR Grant_priv='Y'
ORDER BY user, host;
```

## 日志过滤正则表达式

以下正则表达式可用于过滤 MySQL 错误日志中的安全相关事件：

### 认证与连接问题

```
# 认证失败
^(?i)Access denied for user '.+?'@'.+?'(.*)$

# 连接中止
^(?i)Aborted connection .+? to db: .+? user: .+? host: .+?$

# 连接错误读包
^(?i)Got an error reading communication packets$

# 插件/认证警告
^(?i)caching_sha2_password|mysql_native_password|sha256_password$
```

### 权限与安全问题

```
# 权限变更
^(?i)GRANT|REVOKE$

# 用户创建或修改
^(?i)CREATE USER|ALTER USER|DROP USER$

# 主机访问控制
^(?i)host='%'|host='0.0.0.0'|host='.*'$
```

## 常见问题处理

### 连接错误增加

如果 `Aborted_connects` 或 `Connection_errors_*` 指标出现上升趋势：

1. 检查网络连接稳定性
2. 验证应用连接池配置是否合理
3. 检查 MySQL 最大连接数与超时设置
4. 审查最近的账号或权限变更
5. 检查客户端认证插件与服务器兼容性

### 通配主机账户处理

发现 `host='%'` 的账户时：

1. 审核账户权限范围，确认是否必要
2. 将账户限制到特定 IP 或网段：
   ```sql
   -- 收敛到特定网段
   UPDATE mysql.user SET host='192.168.1.%' WHERE user='example_user' AND host='%';
   
   -- 或收敛到本地三地址
   DELETE FROM mysql.user WHERE user='example_user' AND host='%';
   CREATE USER 'example_user'@'localhost' IDENTIFIED BY 'password';
   CREATE USER 'example_user'@'127.0.0.1' IDENTIFIED BY 'password';
   CREATE USER 'example_user'@'::1' IDENTIFIED BY 'password';
   
   -- 刷新权限
   FLUSH PRIVILEGES;
   ```

### 安全凭据管理

使用 `--defaults-extra-file` 方式存储凭据，避免明文密码：

1. 创建凭据文件（如 `mysql-extra.cnf`）：
   ```
   [client]
   user=username
   password=password
   host=127.0.0.1
   port=3306
   ```

2. 设置严格的文件权限（仅当前用户可读）

3. 使用方式：
   ```
   mysql --defaults-extra-file=/path/to/mysql-extra.cnf
   ```

## 定期审计建议

1. 每日检查 `Aborted_connects` 与 `Connection_errors_*` 指标
2. 每周审计通配主机账户与特权账户
3. 每月全面审计用户权限与插件分布
4. 系统变更后立即执行完整审计

## 回滚准备

如需回滚账户变更，请准备以下脚本：

```sql
-- 示例：恢复删除的账户
CREATE USER 'example_user'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'password';
GRANT SELECT, INSERT, UPDATE, DELETE ON example_db.* TO 'example_user'@'%';
FLUSH PRIVILEGES;
```

确保在执行任何变更前备份当前账户状态：

```sql
SELECT * FROM mysql.user WHERE user='target_user' INTO OUTFILE '/tmp/user_backup.txt';
SHOW GRANTS FOR 'target_user'@'host';
```

## 参考资源

- [MySQL 8.0 认证插件文档](https://dev.mysql.com/doc/refman/8.0/en/authentication-plugins.html)
- [MySQL 连接问题排查指南](https://dev.mysql.com/doc/refman/8.0/en/connection-problems.html)
- [MySQL 安全最佳实践](https://dev.mysql.com/doc/refman/8.0/en/security.html)
