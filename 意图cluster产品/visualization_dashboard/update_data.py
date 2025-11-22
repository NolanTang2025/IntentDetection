#!/usr/bin/env python3
"""
更新可视化仪表板的数据文件
将业务驱动聚类结果转换为仪表板格式
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

def load_business_cluster_results():
    """加载业务驱动聚类结果"""
    cluster_file = Path('../cluster_timeClip/business_cluster_results.json')
    with open(cluster_file, 'r', encoding='utf-8') as f:
        business_data = json.load(f)
    
    # 如果business_cluster_results.json中没有text字段，尝试从cluster_results.json中加载
    if business_data.get('segments') and len(business_data['segments']) > 0:
        if 'text' not in business_data['segments'][0]:
            # 尝试加载cluster_results.json来获取text字段
            cluster_results_file = Path('../cluster_timeClip/cluster_results.json')
            if cluster_results_file.exists():
                with open(cluster_results_file, 'r', encoding='utf-8') as f:
                    cluster_data = json.load(f)
                # 创建text字段的映射（基于segment_id）
                text_map = {seg.get('segment_id', ''): seg.get('text', '') 
                           for seg in cluster_data.get('segments', [])}
                # 为business_data的segments添加text字段
                for seg in business_data.get('segments', []):
                    seg_id = seg.get('segment_id', '')
                    if seg_id in text_map:
                        seg['text'] = text_map[seg_id]
    
    return business_data

def load_business_insights():
    """加载业务洞察"""
    insights_file = Path('../user_portrait_analysis/business_driven_insights.json')
    with open(insights_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def prepare_time_series_data(segments, cluster_labels):
    """准备时间序列数据，按时间段统计用户画像和阶段分布"""
    # 按日期和小时分组
    daily_data = defaultdict(lambda: {
        'portraits': defaultdict(int),  # 画像分布
        'stages': defaultdict(int),    # 阶段分布
        'portrait_stage': defaultdict(lambda: defaultdict(int)),  # 画像+阶段组合
        'hourly': defaultdict(lambda: {
            'portraits': defaultdict(int),
            'stages': defaultdict(int),
            'portrait_stage': defaultdict(lambda: defaultdict(int))
        })
    })
    
    # 阶段映射
    stage_map = {0: '浏览阶段', 1: '对比阶段', 2: '决策阶段'}
    
    for segment in segments:
        try:
            # 解析时间
            start_time_str = segment.get('start_time', '')
            if not start_time_str:
                continue
            
            # 解析日期和时间
            if 'T' in start_time_str:
                date_part = start_time_str.split('T')[0]
                time_part = start_time_str.split('T')[1].split('.')[0] if '.' in start_time_str.split('T')[1] else start_time_str.split('T')[1].split('Z')[0]
            else:
                parts = start_time_str.split(' ')
                date_part = parts[0] if len(parts) > 0 else start_time_str
                time_part = parts[1] if len(parts) > 1 else '00:00:00'
            
            # 解析小时
            hour = int(time_part.split(':')[0]) if ':' in time_part else 0
            hour_key = f"{date_part} {hour:02d}:00"
            
            # 获取聚类信息
            cluster_id = str(segment.get('business_cluster', ''))
            label_info = cluster_labels.get(cluster_id, {})
            portrait_name = label_info.get('short_label', f'聚类{cluster_id}')
            
            # 获取阶段
            purchase_stage = segment.get('purchase_stage', 0)
            stage_name = stage_map.get(purchase_stage, '浏览阶段')
            
            # 按日期统计
            daily_data[date_part]['portraits'][portrait_name] += 1
            daily_data[date_part]['stages'][stage_name] += 1
            daily_data[date_part]['portrait_stage'][portrait_name][stage_name] += 1
            
            # 按小时统计
            daily_data[date_part]['hourly'][hour_key]['portraits'][portrait_name] += 1
            daily_data[date_part]['hourly'][hour_key]['stages'][stage_name] += 1
            daily_data[date_part]['hourly'][hour_key]['portrait_stage'][portrait_name][stage_name] += 1
            
        except Exception as e:
            print(f"处理时间序列数据时出错: {e}")
            continue
    
    # 转换为列表格式，按日期排序
    time_series = []
    for date_str in sorted(daily_data.keys()):
        data = daily_data[date_str]
        time_series.append({
            'date': date_str,
            'portraits': dict(data['portraits']),
            'stages': dict(data['stages']),
            'portrait_stage': {k: dict(v) for k, v in data['portrait_stage'].items()},
            'hourly': {
                hour_key: {
                    'portraits': dict(hour_data['portraits']),
                    'stages': dict(hour_data['stages']),
                    'portrait_stage': {k: dict(v) for k, v in hour_data['portrait_stage'].items()}
                }
                for hour_key, hour_data in sorted(data['hourly'].items())
            }
        })
    
    return time_series

def extract_keywords_from_text(text):
    """从文本中提取关键词（只提取用户感兴趣的内容，不提取分析结果）"""
    if not text or not isinstance(text, str) or len(text) < 10:
        return []
    
    keywords = []
    
    # 过滤掉分析结果相关的词（这些是用户特质，不是用户兴趣）
    analysis_terms = [
        'browsing', 'quick', 'deep', 'research', 'engagement', 'evolution',
        'stage', 'deciding', 'premium', 'deciding', 'showing', 'indicated',
        'suggests', 'indicates', 'current', 'previous', 'history'
    ]
    
    # 提取产品名称（如 Z6, A1, F1, H02, G1, Z10等）
    product_pattern = r'\b([A-Z]\d+)\b'
    products = re.findall(product_pattern, text)
    keywords.extend(products)
    
    # 提取常见的关键短语（2-3个词的组合，不区分大小写匹配）
    # 这些是用户感兴趣的产品特性和功能
    key_phrases = [
        'Snoring Reduction', 'Sleep Quality', 'Sleep Tracking', 'Ergonomic Design',
        'Anti-Snore', 'Memory Foam', 'Adjustable Height', 'Position Sensors',
        'Auto-Adjustment', 'App Connectivity', 'Sleep Solution', 'Snore Detection',
        'Sleep Posture', 'Smart Technology', 'AI Technology',
        'Sleep Improvement', 'Product Effectiveness', 'Premium', 'Comfortable',
        'Clinically Proven', 'Noise Reduction', 'Head Position', 'Sleep Insights',
        'Smart Pillow', 'AI Anti-Snore', 'Smart Anti-Snore', 'Sleep Quality Improvement',
        'Snoring Solution', 'Product Comparison', 'Smart Sleep', 'Anti-Snoring Technology',
        'Neck Support', 'Cool Sleep', 'Firmness Control', 'Comfort Support',
        'Air Water Tech', 'Free Shipping', 'Trial Period', '30-Night Trial'
    ]
    
    text_lower = text.lower()
    for phrase in key_phrases:
        if phrase.lower() in text_lower:
            keywords.append(phrase)
    
    # 提取技术关键词（AI Technology, MEMS sensors等）
    tech_patterns = [
        (r'\bAI\s+[A-Z][a-z]+', 'AI'),  # AI Technology -> AI
        (r'\bMEMS\s+sensors?', 'MEMS'),
        (r'\bSmart\s+[A-Z][a-z]+', 'Smart'),  # Smart Technology -> Smart
    ]
    
    for pattern, prefix in tech_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            keywords.append(prefix)
    
    # 提取单个重要关键词（大写开头的单词，过滤停用词和分析结果）
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                  'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                  'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
                  'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                  'user', 'users', 'product', 'products', 'page', 'pages', 'session',
                  'sessions', 'action', 'actions', 'indicates', 'suggests', 'shows',
                  'the', 'current', 'previous', 'history', 'showing', 'indicated'}
    
    # 提取大写开头的单词（可能是专有名词或重要概念）
    words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    filtered_words = [w for w in words 
                     if w.lower() not in stop_words 
                     and w.lower() not in [t.lower() for t in analysis_terms]
                     and len(w) > 2]
    # 只保留出现频率较高的词（至少出现2次）
    word_counts = Counter(filtered_words)
    frequent_words = [w for w, count in word_counts.items() if count >= 2]
    keywords.extend(frequent_words[:15])  # 限制数量
    
    return keywords

def extract_cluster_keywords(cluster_segments):
    """从聚类片段中提取关键词并统计频率"""
    all_keywords = []
    
    for segment in cluster_segments:
        text = segment.get('text', '')
        if text and isinstance(text, str) and len(text) > 10:  # 确保文本有效
            keywords = extract_keywords_from_text(text)
            if keywords:
                all_keywords.extend(keywords)
    
    # 统计关键词频率
    keyword_counter = Counter(all_keywords)
    
    # 返回频率最高的前30个关键词，格式为 [word, frequency]
    top_keywords = keyword_counter.most_common(30)
    
    return top_keywords

def prepare_user_trajectories(segments, cluster_labels):
    """准备用户轨迹数据，展示每个用户的所有意图切片"""
    from collections import defaultdict
    
    # 按用户分组
    user_segments = defaultdict(list)
    
    for segment in segments:
        user_id = segment.get('user_id')
        cluster_id = str(segment.get('business_cluster', ''))
        label_info = cluster_labels.get(cluster_id, {})
        
        # 获取阶段信息
        purchase_stage = segment.get('purchase_stage', 0)
        stage_map = {0: '浏览阶段', 1: '对比阶段', 2: '决策阶段'}
        stage_name = stage_map.get(purchase_stage, '浏览阶段')
        
        # 将分钟转换为秒
        duration_seconds = segment.get('duration_minutes', 0) * 60
        
        user_segments[user_id].append({
            'segment_id': segment.get('segment_id', ''),
            'segment_index': segment.get('segment_index', 0),
            'start_time': segment.get('start_time', ''),
            'end_time': segment.get('end_time', ''),
            'duration_seconds': duration_seconds,
            'record_count': segment.get('record_count', 0),
            'cluster_id': cluster_id,
            'cluster_name': label_info.get('short_label', f'聚类{cluster_id}'),
            'full_label': label_info.get('full_label', f'聚类{cluster_id}'),
            'purchase_stage': stage_name,
            'intent_score': segment.get('intent_score', 0.5),
            'price_sensitivity': segment.get('price_sensitivity', 2),
            'engagement_level': segment.get('engagement_level', 0)
        })
    
    # 转换为列表格式，按用户ID排序，每个用户的片段按时间排序
    trajectories = []
    for user_id, segments_list in sorted(user_segments.items()):
        # 按开始时间排序
        segments_list.sort(key=lambda x: x['start_time'])
        
        # 统计用户信息
        unique_clusters = set(seg['cluster_id'] for seg in segments_list)
        total_duration = sum(seg['duration_seconds'] for seg in segments_list)
        total_records = sum(seg['record_count'] for seg in segments_list)
        
        trajectories.append({
            'user_id': user_id,
            'segment_count': len(segments_list),
            'unique_clusters': len(unique_clusters),
            'cluster_ids': sorted(list(unique_clusters)),
            'total_duration': total_duration,
            'total_records': total_records,
            'segments': segments_list
        })
    
    return trajectories

def convert_to_dashboard_format(cluster_results, business_insights):
    """转换为仪表板格式"""
    # 获取片段数据
    segments_df_data = cluster_results['segments']
    
    # 准备businessInsights数据
    dashboard_insights = []
    
    for insight in business_insights:
        # 计算非零时长的平均值（从原始数据中重新计算）
        cluster_id = insight['cluster_id']
        cluster_segments = [s for s in segments_df_data if str(s.get('business_cluster', '')) == str(cluster_id)]
        non_zero_durations = [s.get('duration_minutes', 0) * 60 for s in cluster_segments if s.get('duration_minutes', 0) > 0]
        avg_duration_seconds = sum(non_zero_durations) / len(non_zero_durations) if non_zero_durations else 0
        
        dashboard_insight = {
            'cluster_id': insight['cluster_id'],
            'user_segment_name': insight['cluster_name'],
            'key_characteristics': [
                f"用户规模: {insight['key_characteristics']['user_count']} 个独立用户，{insight['key_characteristics']['segment_count']} 个意图片段",
                f"平均浏览时长: {avg_duration_seconds:.1f} 秒" if avg_duration_seconds > 0 else "平均浏览时长: 瞬时浏览（单次交互）",
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
        # 将分钟转换为秒
        duration_seconds = segment.get('duration_minutes', 0) * 60
        cluster_stats[cluster_id]['durations'].append(duration_seconds)
        cluster_stats[cluster_id]['interactions'].append(segment.get('record_count', 0))
        cluster_stats[cluster_id]['intent_scores'].append(segment.get('intent_score', 0.5))
    
    for cluster_id, stats in cluster_stats.items():
        cluster_id_str = str(cluster_id)
        label_info = cluster_labels.get(cluster_id_str, {})
        
        # 只计算非零时长的平均值（排除单条记录的瞬时片段）
        non_zero_durations = [d for d in stats['durations'] if d > 0]
        avg_duration = sum(non_zero_durations) / len(non_zero_durations) if non_zero_durations else 0
        
        # 提取该聚类的关键词
        cluster_keywords = extract_cluster_keywords(stats['segments'])
        
        # 将关键词转换为词云格式 [word, weight]
        # 权重基于频率，最高频率的词权重为60，最低为15
        wordcloud_data = []
        if cluster_keywords:
            max_freq = cluster_keywords[0][1] if cluster_keywords else 1
            for word, freq in cluster_keywords:
                # 权重范围：15-60，基于频率比例
                weight = int(15 + (freq / max_freq) * 45) if max_freq > 0 else 15
                weight = min(max(weight, 15), 60)  # 确保在范围内
                wordcloud_data.append([word, weight])
        
        portrait = {
            'cluster_id': cluster_id_str,
            'segment_count': len(stats['segments']),
            'unique_users': len(stats['user_ids']),
            'avg_duration_seconds': avg_duration,
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
            },
            'keywords': wordcloud_data  # 添加关键词数据用于词云
        }
        dashboard_portraits.append(portrait)
    
    # 统计数据
    total_users = len(set(seg['user_id'] for seg in segments_df_data))
    total_segments = len(segments_df_data)
    total_clusters = len(cluster_labels)
    
    # 只计算非零时长的平均值
    non_zero_durations = [seg.get('duration_minutes', 0) * 60 for seg in segments_df_data if seg.get('duration_minutes', 0) > 0]
    avg_duration = sum(non_zero_durations) / len(non_zero_durations) if non_zero_durations else 0
    
    stats = {
        'totalUsers': total_users,
        'totalSegments': total_segments,
        'totalClusters': total_clusters,
        'avgDuration': avg_duration,
        'avgInteractions': sum(seg.get('record_count', 0) for seg in segments_df_data) / total_segments if total_segments > 0 else 0
    }
    
    # 准备时间序列数据 - 按时间段统计用户画像和阶段分布
    time_series_data = prepare_time_series_data(segments_df_data, cluster_labels)
    
    # 准备用户轨迹数据 - 每个用户的所有片段及其聚类
    user_trajectories = prepare_user_trajectories(segments_df_data, cluster_labels)
    
    return {
        'businessInsights': dashboard_insights,
        'userPortraits': dashboard_portraits,
        'stats': stats,
        'timeSeries': time_series_data,
        'userTrajectories': user_trajectories
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
        
        f.write('// 时间序列数据\n')
        f.write('const timeSeries = ')
        json.dump(dashboard_data.get('timeSeries', []), f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        f.write('// 用户轨迹数据\n')
        f.write('const userTrajectories = ')
        json.dump(dashboard_data.get('userTrajectories', []), f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        f.write('// 数据加载完成\n')
        f.write('console.log("数据加载完成:", {\n')
        f.write('  businessInsights: businessInsights.length,\n')
        f.write('  userPortraits: userPortraits.length,\n')
        f.write('  stats: stats,\n')
        f.write('  timeSeries: timeSeries.length,\n')
        f.write('  userTrajectories: userTrajectories.length\n')
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
    print(f"   - 时间序列: {len(dashboard_data.get('timeSeries', []))} 个时间点")
    print(f"   - 用户轨迹: {len(dashboard_data.get('userTrajectories', []))} 个用户")

if __name__ == '__main__':
    main()

