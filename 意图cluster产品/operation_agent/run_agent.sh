#!/bin/bash
# 运营Agent运行脚本
# 使用方法: ./run_agent.sh <shop_id> [--execute]

cd "$(dirname "$0")"
python3 integrate_with_clustering.py "$@"


