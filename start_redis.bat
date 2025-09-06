@echo off
echo 启动Redis服务器...
echo 使用配置文件: %~dp0redis.conf
echo Redis密码: ghp880218
D:\Redis-x64-3.0.504\redis-server.exe "%~dp0redis.conf"
pause