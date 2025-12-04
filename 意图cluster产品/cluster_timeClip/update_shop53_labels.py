#!/usr/bin/env python3
"""
更新shop53的聚类标签，使用基于文本的标签生成器
"""

import json
import pandas as pd
import sys
from pathlib import Path
import numpy as np

# 添加路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / 'cluster_timeClip'))
from embedding_based_label_generator import EmbeddingBasedLabelGenerator

def convert_to_native(obj):
    """转换numpy类型为Python原生类型"""
    if isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def main():
    # 加载数据
    cluster_file = BASE_DIR / 'cluster_timeClip' / 'business_cluster_results_shop_53.json'
    print(f"加载聚类结果文件: {cluster_file}")
    
    with open(cluster_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    segments_df = pd.DataFrame(data['segments'])
    segments_df['business_cluster'] = segments_df['business_cluster'].astype(int)
    
    # 加载原始数据
    extracted_file = BASE_DIR / 'data_extract' / 'extracted_data_shop_53.json'
    print(f"加载原始数据文件: {extracted_file}")
    
    with open(extracted_file, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    
    # 生成新标签
    print("\n正在生成基于文本的聚类标签...")
    label_generator = EmbeddingBasedLabelGenerator()
    cluster_labels_dict = label_generator.generate_labels_for_clusters(
        segments_df, 
        segments_df['business_cluster'].values,
        extracted_data=extracted_data
    )
    
    # 转换numpy类型为Python原生类型
    cluster_labels_dict = convert_to_native(cluster_labels_dict)
    
    # 更新数据
    data['clustering']['cluster_labels'] = cluster_labels_dict
    
    # 保存
    print(f"\n保存更新后的聚类结果...")
    with open(cluster_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 已生成 {len(cluster_labels_dict)} 个聚类的标签")
    print("\n聚类标签示例:")
    for i, (k, v) in enumerate(list(cluster_labels_dict.items())[:10]):
        print(f"  聚类 {k}: {v.get('short_label', 'N/A')} - {v.get('full_label', 'N/A')}")

if __name__ == '__main__':
    main()

