@echo off
setlocal ENABLEDELAYEDEXPANSION

if "%REDIS_PASSWORD%"=="" (
  echo [WARN] 未检测到 REDIS_PASSWORD 环境变量，Redis 将以无密码方式启动（仅开发环境允许）。
  REM 以独立进程启动 Redis，批处理立即退出
  start "Redis" D:\Redis-x64-3.0.504\redis-server.exe "%~dp0redis.conf"
) else (
  echo [INFO] 使用环境变量传入 Redis 密码，避免明文写入配置文件。
  REM 安全：不回显 Redis 密码，独立进程启动
  start "Redis" D:\Redis-x64-3.0.504\redis-server.exe "%~dp0redis.conf" --requirepass %REDIS_PASSWORD%
)

REM 已移除 pause，避免阻塞与意外终止