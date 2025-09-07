@echo off
echo 启动Redis服务器...
echo 使用配置文件: %~dp0redis.conf
REM 安全：不回显Redis密码
D:\Redis-x64-3.0.504\redis-server.exe "%~dp0redis.conf"
pause