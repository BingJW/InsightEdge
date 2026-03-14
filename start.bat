@echo off
chcp 65001 >nul
echo ========================================
echo 商业情报分析系统 - 启动脚本
echo ========================================
echo.

cd /d %~dp0

if not exist "venv\Scripts\python.exe" (
    echo 错误: 虚拟环境不存在，请先运行安装脚本
    echo 正在创建虚拟环境...
    python -m venv venv
    echo 正在安装依赖包...
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo 启动系统...
venv\Scripts\python.exe main.py

pause



