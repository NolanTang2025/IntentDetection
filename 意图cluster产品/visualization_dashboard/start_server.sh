#!/bin/bash
# 启动本地服务器脚本

echo "正在启动用户意图分析仪表板..."
echo ""
echo "服务器将在以下地址启动："
echo "  http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 检查Python版本
if command -v python3 &> /dev/null; then
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    python -m http.server 8000
else
    echo "错误: 未找到 Python，请安装 Python 3"
    exit 1
fi

