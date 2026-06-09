@echo off
echo ========================================
echo   启动测试服务
echo ========================================
cd /d %~dp0
python server.py
pause
