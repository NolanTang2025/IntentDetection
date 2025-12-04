#!/usr/bin/env python3
"""
处理shop_28的聚类结果，转换为标准格式并生成前端数据
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import pandas as pd

# 添加路径
BASE_DIR = Path(__file__).parent
CLUSTER_DIR = BASE_DIR / 'cluster_timeClip'
PORTRAIT_DIR = BASE_DIR / 'user_portrait_analysis'
DASHBOARD_DIR = BASE_DIR / 'visualization_dashboard'
DATA_EXTRACT_DIR = BASE_DIR / 'data_extract'

def load_clustering_results():
    """加载聚类结果文件"""
    clustering_file = BASE_DIR / 'cluster_results_by_shop' / 'shop_28' / 'clustering_results.json'
    with open(clustering_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['28']

def load_extracted_data():
    """加载原始提取的数据"""
    extracted_file = DATA_EXTRACT_DIR / 'extracted_data_shop_28.json'
    with open(extracted_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_to_business_cluster_format(clustering_data, extracted_data):
    """将聚类结果转换为business_cluster_results格式"""
    labels = clustering_data['clustering']['labels']
    n_clusters = clustering_data['clustering']['n_clusters']
    
    print(f"  处理 {len(labels)} 个标签，{n_clusters} 个聚类")
    
    # 创建索引映射：labels的索引对应extracted_data的索引
    # 假设labels和extracted_data的顺序一致
    if len(labels) != len(extracted_data):
        print(f"  ⚠️  警告: labels数量({len(labels)})与extracted_data数量({len(extracted_data)})不一致")
        # 取较小的长度
        min_len = min(len(labels), len(extracted_data))
        labels = labels[:min_len]
        extracted_data = extracted_data[:min_len]
    
    # 按聚类分组
    cluster_segments = defaultdict(list)
    
    for idx, (label, record) in enumerate(zip(labels, extracted_data)):
        cluster_id = int(label)
        
        # 获取基本信息
        user_id = record.get('userId') or record.get('user_id', '')
        session_id = record.get('sessionId') or record.get('session_id', f'session_{idx}')
        timestamp = record.get('timestamp') or record.get('start_time', '')
        output_str = record.get('output', '')
        
        # 解析output获取意图信息
        intent_score = 0.5
        try:
            if output_str:
                cleaned = output_str.strip()
                if cleaned.startswith('"'):
                    cleaned = cleaned[1:-1]
                if cleaned.startswith('```json'):
                    cleaned = cleaned[7:-3]
                if cleaned.startswith('```'):
                    cleaned = cleaned[3:-3]
                data = json.loads(cleaned)
                intent_score = data.get('intent_score', 0.5)
        except:
            pass
        
        # 创建segment
        segment = {
            'segment_id': f"{user_id}_{session_id}_{idx}",
            'user_id': user_id,
            'session_id': session_id,
            'start_time': timestamp,
            'end_time': timestamp,  # 单次session，开始和结束时间相同
            'duration_minutes': 0.0,  # 需要从数据中计算或估算
            'record_count': 1,
            'intent_score': intent_score,
            'business_cluster': str(cluster_id),
            'purchase_stage': 0,
            'text': output_str[:200] if output_str else '',  # 截取前200字符作为文本摘要
            'output': output_str
        }
        
        cluster_segments[cluster_id].append(segment)
    
    # 转换为segments列表
    all_segments = []
    for cluster_id, segments in cluster_segments.items():
        all_segments.extend(segments)
    
    # 生成聚类标签（简化版，后续会由用户画像分析生成更详细的标签）
    cluster_labels = {}
    for cluster_id in range(n_clusters):
        cluster_segments_list = cluster_segments.get(cluster_id, [])
        if cluster_segments_list:
            cluster_labels[str(cluster_id)] = {
                'short_label': f'Cluster {cluster_id}',
                'full_label': f'Cluster {cluster_id}',
                'cluster_name': f'Cluster {cluster_id}',
                'user_segment_name': f'Cluster {cluster_id}',
                'characteristics': {}
            }
    
    # 构建business_cluster_results格式
    result = {
        'shop_id': '28',
        'segments': all_segments,
        'clustering': {
            'n_clusters': n_clusters,
            'cluster_labels': cluster_labels,
            'cluster_counts': {str(k): len(v) for k, v in cluster_segments.items()},
            'method': clustering_data['clustering'].get('method', 'kmeans')
        }
    }
    
    return result

def main():
    print("=" * 80)
    print("处理 Shop 28 聚类结果")
    print("=" * 80)
    
    # 步骤1: 加载数据
    print("\n[1/5] 加载聚类结果和原始数据...")
    clustering_data = load_clustering_results()
    extracted_data = load_extracted_data()
    print(f"  ✓ 聚类结果: {clustering_data['n_intentions']} 个意图, {clustering_data['clustering']['n_clusters']} 个聚类")
    print(f"  ✓ 原始数据: {len(extracted_data)} 条记录")
    
    # 步骤2: 转换为business_cluster_results格式并提取特征
    print("\n[2/5] 转换数据格式并提取特征...")
    business_cluster_results = convert_to_business_cluster_format(clustering_data, extracted_data)
    print(f"  ✓ 生成 {len(business_cluster_results['segments'])} 个片段")
    print(f"  ✓ {len(business_cluster_results['clustering']['cluster_labels'])} 个聚类")
    
    # 提取业务特征
    print("  提取业务特征...")
    sys.path.insert(0, str(BASE_DIR / 'cluster_timeClip'))
    from behavior_intent_clustering import BehaviorIntentClusterer
    
    segments_df = pd.DataFrame(business_cluster_results['segments'])
    segments_df['business_cluster'] = segments_df['business_cluster'].astype(int)
    
    clusterer = BehaviorIntentClusterer()
    
    # 为每个segment提取特征
    print(f"  处理 {len(segments_df)} 个片段...")
    for idx, row in segments_df.iterrows():
        features = clusterer.extract_business_features(
            row.get('output', ''), 
            row.get('duration_minutes', 0), 
            row.get('record_count', 1)
        )
        # 将特征添加到segment
        for key, value in features.items():
            segments_df.at[idx, key] = value
    
    # 更新business_cluster_results
    business_cluster_results['segments'] = segments_df.to_dict(orient='records')
    print(f"  ✓ 已提取所有片段特征")
    
    # 步骤3: 保存business_cluster_results
    print("\n[3/5] 保存聚类结果...")
    output_file = CLUSTER_DIR / 'business_cluster_results_shop_28.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(business_cluster_results, f, indent=2, ensure_ascii=False)
    print(f"  ✓ 已保存: {output_file}")
    
    # 步骤4: 运行用户画像分析
    print("\n[4/5] 运行用户画像分析...")
    sys.path.insert(0, str(PORTRAIT_DIR))
    from business_driven_portrait_analyzer import BusinessDrivenPortraitAnalyzer
    
    original_cwd = Path.cwd()
    os.chdir(PORTRAIT_DIR)
    try:
        analyzer = BusinessDrivenPortraitAnalyzer(
            cluster_results_file=f'../cluster_timeClip/business_cluster_results_shop_28.json'
        )
        strategies = analyzer.analyze_all_clusters()
        analyzer.save_results(strategies)
        
        # 重命名输出文件
        import shutil
        output_files = {
            'business_driven_insights.json': 'business_driven_insights_shop_28.json',
            'business_driven_insights_summary.csv': 'business_driven_insights_summary_shop_28.csv',
            'business_driven_report.md': 'business_driven_report_shop_28.md'
        }
        
        for old_name, new_name in output_files.items():
            old_path = PORTRAIT_DIR / old_name
            new_path = PORTRAIT_DIR / new_name
            if old_path.exists():
                shutil.move(str(old_path), str(new_path))
                print(f"  ✓ 已保存: {new_name}")
    finally:
        os.chdir(original_cwd)
    
    # 步骤5: 更新前端数据
    print("\n[5/5] 更新前端数据...")
    sys.path.insert(0, str(DASHBOARD_DIR))
    from update_data import convert_to_dashboard_format
    
    insights_file = PORTRAIT_DIR / 'business_driven_insights_shop_28.json'
    with open(insights_file, 'r', encoding='utf-8') as f:
        insights_data = json.load(f)
    
    dashboard_data = convert_to_dashboard_format(business_cluster_results, insights_data)
    
    # 生成data_shop_28.js
    output_js = DASHBOARD_DIR / 'data_shop_28.js'
    with open(output_js, 'w', encoding='utf-8') as f:
        f.write('// Shop 28 聚类分析数据\n')
        f.write('// 自动生成，请勿手动编辑\n\n')
        f.write(f'const businessInsights = {json.dumps(dashboard_data["businessInsights"], indent=2, ensure_ascii=False)};\n\n')
        f.write(f'const userPortraits = {json.dumps(dashboard_data["userPortraits"], indent=2, ensure_ascii=False)};\n\n')
        f.write(f'const stats = {json.dumps(dashboard_data["stats"], indent=2, ensure_ascii=False)};\n\n')
        f.write(f'const timeSeries = {json.dumps(dashboard_data["timeSeries"], indent=2, ensure_ascii=False)};\n\n')
        f.write(f'const userTrajectories = {json.dumps(dashboard_data["userTrajectories"], indent=2, ensure_ascii=False)};\n')
    
    print(f"  ✓ 已保存: {output_js}")
    
    print("\n" + "=" * 80)
    print("✅ Shop 28 聚类分析完成！")
    print("=" * 80)
    print("\n下一步: 运行 create_multi_shop_dashboard.py 更新 multi_shop_data.js")

if __name__ == '__main__':
    import os
    main()

