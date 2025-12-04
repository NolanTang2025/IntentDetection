#!/bin/bash
# 自动运行聚类脚本，自动读取API key

echo "=========================================="
echo "意图聚类脚本 - 自动运行"
echo "=========================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  未在环境变量中找到 GEMINI_API_KEY"
    echo ""
    echo "尝试从可能的配置文件读取..."
    
    # 尝试从 .env 文件读取
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env"
        echo "✓ 从 .env 文件读取配置"
    fi
    
    # 尝试从项目根目录的 .env 文件读取
    if [ -z "$GEMINI_API_KEY" ] && [ -f "$PROJECT_ROOT/.env" ]; then
        source "$PROJECT_ROOT/.env"
        echo "✓ 从项目根目录 .env 文件读取配置"
    fi
    
    # 如果还是没有，提示用户
    if [ -z "$GEMINI_API_KEY" ]; then
        echo ""
        echo "❌ 未找到 GEMINI_API_KEY"
        echo ""
        echo "请设置API key，方式之一："
        echo "  1. 在当前shell中设置: export GEMINI_API_KEY='your-api-key'"
        echo "  2. 创建 $SCRIPT_DIR/.env 文件，添加: GEMINI_API_KEY='your-api-key'"
        echo ""
        exit 1
    fi
fi

echo "✓ 找到API key: ${GEMINI_API_KEY:0:15}..."
echo ""

# 运行Python脚本
echo "开始运行聚类脚本..."
echo ""
python3 "$SCRIPT_DIR/user_clustering.py"

