@echo off
REM Windows 快速启动本地服务器脚本

echo 🚀 启动本地服务器...
echo.

REM 检查Python是否安装
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 使用 Python 启动服务器
    echo 📱 访问地址: http://localhost:8000
    echo 🛑 按 Ctrl+C 停止服务器
    echo.
    python -m http.server 8000
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ 使用 Python 3 启动服务器
        echo 📱 访问地址: http://localhost:8000
        echo 🛑 按 Ctrl+C 停止服务器
        echo.
        python3 -m http.server 8000
    ) else (
        echo ❌ 未找到 Python
        echo 请安装 Python 或使用其他方法部署
        pause
        exit /b 1
    )
)

