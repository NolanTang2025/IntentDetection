#!/bin/bash

# 快速启动本地服务器脚本

echo "🚀 启动本地服务器..."
echo ""

# 检查Python是否安装
if command -v python3 &> /dev/null; then
    echo "✅ 使用 Python 3 启动服务器"
    echo "📱 访问地址: http://localhost:8000"
    echo "🛑 按 Ctrl+C 停止服务器"
    echo ""
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    echo "✅ 使用 Python 2 启动服务器"
    echo "📱 访问地址: http://localhost:8000"
    echo "🛑 按 Ctrl+C 停止服务器"
    echo ""
    python -m SimpleHTTPServer 8000
elif command -v php &> /dev/null; then
    echo "✅ 使用 PHP 启动服务器"
    echo "📱 访问地址: http://localhost:8000"
    echo "🛑 按 Ctrl+C 停止服务器"
    echo ""
    php -S localhost:8000
else
    echo "❌ 未找到 Python 或 PHP"
    echo "请安装 Python 3 或使用其他方法部署"
    exit 1
fi

