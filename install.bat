@echo off
echo ========================================
echo 商业情报分析系统 - 环境安装脚本
echo ========================================
echo.

echo 正在检查conda环境...
conda --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到conda，请先安装Anaconda或Miniconda
    pause
    exit /b 1
)

echo 创建conda环境...
conda env create -f environment.yml

if %errorlevel% neq 0 (
    echo 错误: conda环境创建失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 环境安装完成！
echo ========================================
echo.
echo 请使用以下命令激活环境：
echo   conda activate insightedge_bi
echo.
echo 然后运行系统：
echo   python main.py
echo.
pause




