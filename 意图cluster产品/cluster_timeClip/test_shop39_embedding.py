#!/usr/bin/env python3
"""
测试店铺39的Gemini Embedding聚类
"""

import os
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from behavior_intent_clustering import BehaviorIntentClusterer

def main():
    # 获取API密钥
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  请设置环境变量 GEMINI_API_KEY")
        print("   例如: export GEMINI_API_KEY='your-api-key'")
        return
    
    print("="*80)
    print("测试店铺39的Gemini Embedding聚类")
    print("="*80)
    
    # 创建聚类分析器
    clusterer = BehaviorIntentClusterer(
        intent_change_threshold=0.3,
        gemini_api_key=api_key
    )
    
    # 运行分析
    input_file = Path('../data_extract/extracted_data_shop_39.json')
    if not input_file.exists():
        print(f"❌ 数据文件不存在: {input_file}")
        return
    
    print(f"\n使用输入文件: {input_file}")
    results = clusterer.analyze(input_file=str(input_file), shop_id=39)
    
    print("\n" + "="*80)
    print("✅ 测试完成!")
    print("="*80)
    print(f"聚类数: {results['clustering']['n_clusters']}")
    print(f"片段数: {len(results['segments'])}")

if __name__ == '__main__':
    main()

