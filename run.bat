@echo off
echo ========================================
echo 商业情报分析系统 - 运行脚本
echo ========================================
echo.

echo 检查conda环境...
call conda activate insightedge_bi

if %errorlevel% neq 0 (
    echo 错误: 无法激活conda环境，请先运行 install.bat 安装环境
    pause
    exit /b 1
)

echo 运行系统...
python main.py

pause




