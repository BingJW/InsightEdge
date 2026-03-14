@echo off
chcp 65001 >nul
echo ========================================
echo 商业情报分析系统 - Web服务启动
echo ========================================
echo.

cd /d %~dp0

if not exist "venv\Scripts\python.exe" (
    echo 错误: 虚拟环境不存在，请先运行 install.bat
    pause
    exit /b 1
)

echo 启动Web服务...
echo 访问地址: http://localhost:5000
echo 默认账户: admin/admin123 或 user1/user123
echo.
echo 按 Ctrl+C 停止服务
echo.

venv\Scripts\python.exe app.py

pause



