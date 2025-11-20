#!/usr/bin/env python3
"""
更新可视化仪表板的数据文件
将业务驱动聚类结果转换为仪表板格式
"""

import json
import sys
from pathlib import Path

def load_business_cluster_results():
    """加载业务驱动聚类结果"""
    cluster_file = Path('../cluster_timeClip/business_cluster_results.json')
    with open(cluster_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_business_insights():
    """加载业务洞察"""
    insights_file = Path('../user_portrait_analysis/business_driven_insights.json')
    with open(insights_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_to_dashboard_format(cluster_results, business_insights):
    """转换为仪表板格式"""
    # 准备businessInsights数据
    dashboard_insights = []
    
    for insight in business_insights:
        dashboard_insight = {
            'cluster_id': insight['cluster_id'],
            'user_segment_name': insight['cluster_name'],
            'key_characteristics': [
                f"用户规模: {insight['key_characteristics']['user_count']} 个独立用户，{insight['key_characteristics']['segment_count']} 个意图片段",
                f"平均浏览时长: {insight['key_characteristics']['avg_duration_minutes']:.1f} 分钟",
                f"平均交互次数: {insight['key_characteristics']['avg_interactions']:.1f} 次",
                f"平均意图强度: {insight['key_characteristics']['avg_intent_score']:.2f}",
                f"购买阶段: {insight['key_characteristics']['stage']}",
                f"价格敏感度: {insight['key_characteristics']['price_sensitivity']}",
                f"参与度: {insight['key_characteristics']['engagement_level']}",
                f"产品偏好: {insight['key_characteristics']['product_preference']}",
                f"关注点: {insight['key_characteristics']['concern_focus']}",
                f"核心需求: {insight['key_characteristics']['core_need']}"
            ],
            'marketing_strategy': insight['marketing_strategy'],
            'product_recommendations': insight['product_recommendation'],
            'conversion_optimization': insight['conversion_tactics'],
            'pricing_strategy': insight['pricing_strategy'],
            'content_strategy': insight['content_strategy'],
            'campaign_differentiation': insight['campaign_differentiation']
        }
        dashboard_insights.append(dashboard_insight)
    
    # 准备userPortraits数据（基于聚类结果）
    dashboard_portraits = []
    
    segments_df_data = cluster_results['segments']
    cluster_labels = cluster_results['clustering']['cluster_labels']
    
    # 按聚类分组统计
    from collections import defaultdict
    cluster_stats = defaultdict(lambda: {
        'user_ids': set(),
        'segments': [],
        'durations': [],
        'interactions': [],
        'intent_scores': []
    })
    
    for segment in segments_df_data:
        cluster_id = segment['business_cluster']
        cluster_stats[cluster_id]['user_ids'].add(segment['user_id'])
        cluster_stats[cluster_id]['segments'].append(segment)
        cluster_stats[cluster_id]['durations'].append(segment.get('duration_minutes', 0))
        cluster_stats[cluster_id]['interactions'].append(segment.get('record_count', 0))
        cluster_stats[cluster_id]['intent_scores'].append(segment.get('intent_score', 0.5))
    
    for cluster_id, stats in cluster_stats.items():
        cluster_id_str = str(cluster_id)
        label_info = cluster_labels.get(cluster_id_str, {})
        
        portrait = {
            'cluster_id': cluster_id_str,
            'segment_count': len(stats['segments']),
            'unique_users': len(stats['user_ids']),
            'avg_duration_minutes': sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0,
            'avg_record_count': sum(stats['interactions']) / len(stats['interactions']) if stats['interactions'] else 0,
            'avg_intent_score': sum(stats['intent_scores']) / len(stats['intent_scores']) if stats['intent_scores'] else 0.5,
            'cluster_name': label_info.get('short_label', f'聚类{cluster_id}'),
            'full_label': label_info.get('full_label', f'聚类{cluster_id}'),
            'characteristics': label_info.get('characteristics', {}),
            'intent_profile': {
                'core_interests': {},
                'price_range': {label_info.get('characteristics', {}).get('price', '高端价值型'): len(stats['segments'])},
                'purchase_stage': {label_info.get('characteristics', {}).get('stage', '浏览阶段'): len(stats['segments'])},
                'main_appeal': {label_info.get('characteristics', {}).get('need', '综合需求'): len(stats['segments'])},
                'concerns': {label_info.get('characteristics', {}).get('concern', '综合关注'): len(stats['segments'])}
            },
            'product_preferences': {
                label_info.get('characteristics', {}).get('product', '多产品比较'): len(stats['segments'])
            },
            'behavior_patterns': {
                'engagement_level': label_info.get('characteristics', {}).get('engagement', '快速浏览者')
            }
        }
        dashboard_portraits.append(portrait)
    
    # 统计数据
    total_users = len(set(seg['user_id'] for seg in segments_df_data))
    total_segments = len(segments_df_data)
    total_clusters = len(cluster_labels)
    
    stats = {
        'totalUsers': total_users,
        'totalSegments': total_segments,
        'totalClusters': total_clusters,
        'avgDuration': sum(seg.get('duration_minutes', 0) for seg in segments_df_data) / total_segments if total_segments > 0 else 0,
        'avgInteractions': sum(seg.get('record_count', 0) for seg in segments_df_data) / total_segments if total_segments > 0 else 0
    }
    
    return {
        'businessInsights': dashboard_insights,
        'userPortraits': dashboard_portraits,
        'stats': stats
    }

def generate_data_js(dashboard_data, output_file='data.js'):
    """生成data.js文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('// 用户意图分析数据\n')
        f.write('// 自动生成，请勿手动编辑\n\n')
        
        f.write('// 业务洞察数据\n')
        f.write('const businessInsights = ')
        json.dump(dashboard_data['businessInsights'], f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        f.write('// 用户画像数据\n')
        f.write('const userPortraits = ')
        json.dump(dashboard_data['userPortraits'], f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        f.write('// 统计数据\n')
        f.write('const stats = ')
        json.dump(dashboard_data['stats'], f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        f.write('// 数据加载完成\n')
        f.write('console.log("数据加载完成:", {\n')
        f.write('  businessInsights: businessInsights.length,\n')
        f.write('  userPortraits: userPortraits.length,\n')
        f.write('  stats: stats\n')
        f.write('});\n')

def main():
    print("正在加载数据...")
    cluster_results = load_business_cluster_results()
    business_insights = load_business_insights()
    
    print("正在转换数据格式...")
    dashboard_data = convert_to_dashboard_format(cluster_results, business_insights)
    
    print("正在生成data.js文件...")
    output_file = Path('data.js')
    generate_data_js(dashboard_data, output_file)
    
    print(f"\n✅ 数据文件已更新: {output_file}")
    print(f"   - 业务洞察: {len(dashboard_data['businessInsights'])} 个聚类")
    print(f"   - 用户画像: {len(dashboard_data['userPortraits'])} 个聚类")
    print(f"   - 总用户数: {dashboard_data['stats']['totalUsers']}")
    print(f"   - 总片段数: {dashboard_data['stats']['totalSegments']}")

if __name__ == '__main__':
    main()

