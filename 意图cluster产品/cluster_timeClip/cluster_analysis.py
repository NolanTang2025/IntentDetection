#!/usr/bin/env python3
"""
基于时间切片的意图聚类分析
方案B：Time-window segmentation + 聚类
"""

import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
import pandas as pd
from pathlib import Path

class IntentClusterAnalyzer:
    def __init__(self, 
                 gap_threshold_minutes=10,  # 事件间隔 > 10分钟 → 切一段
                 inactivity_threshold_minutes=15,  # 15分钟无操作 → 意图结束
                 fixed_window_minutes=None):  # 固定窗口（可选）
        self.gap_threshold = timedelta(minutes=gap_threshold_minutes)
        self.inactivity_threshold = timedelta(minutes=inactivity_threshold_minutes)
        self.fixed_window = timedelta(minutes=fixed_window_minutes) if fixed_window_minutes else None
    
    def parse_timestamp(self, ts_str):
        """解析时间戳字符串"""
        try:
            return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        except:
            return datetime.fromisoformat(ts_str)
    
    def extract_text_features(self, output_str):
        """从output中提取文本特征"""
        try:
            # 清理output字符串
            cleaned = output_str.strip()
            if cleaned.startswith('"'):
                cleaned = cleaned[1:]
            if cleaned.endswith('"'):
                cleaned = cleaned[:-1]
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # 解析JSON
            data = json.loads(cleaned)
            intent = data.get('intent', {})
            
            # 提取关键文本信息
            text_parts = []
            
            # core_interests
            if 'core_interests' in intent:
                interests = intent['core_interests']
                if isinstance(interests, list):
                    text_parts.extend([str(x) for x in interests if x is not None])
            
            # product_focus
            if 'product_focus' in intent:
                pf = intent['product_focus']
                if isinstance(pf, dict):
                    if 'key_attributes' in pf:
                        attrs = pf['key_attributes']
                        if isinstance(attrs, list):
                            text_parts.extend([str(x) for x in attrs if x is not None])
                    if 'main_appeal' in pf and pf['main_appeal']:
                        text_parts.append(str(pf['main_appeal']))
                    if 'price_range' in pf and pf['price_range']:
                        text_parts.append(str(pf['price_range']))
            
            # purchase_signals
            if 'purchase_signals' in intent:
                ps = intent['purchase_signals']
                if isinstance(ps, dict):
                    if 'stage' in ps and ps['stage']:
                        text_parts.append(str(ps['stage']))
                    if 'concerns' in ps:
                        concerns = ps['concerns']
                        if isinstance(concerns, list):
                            text_parts.extend([str(x) for x in concerns if x is not None])
                        elif concerns:
                            text_parts.append(str(concerns))
            
            # behavior_summary
            if 'behavior_summary' in intent:
                bs = intent['behavior_summary']
                if isinstance(bs, dict):
                    for key in ['engagement', 'browsing_path', 'evolution']:
                        if key in bs and bs[key]:
                            text_parts.append(str(bs[key]))
            
            # match_analysis
            if 'match_analysis' in intent:
                ma = intent['match_analysis']
                if isinstance(ma, dict):
                    for key in ['user_fit', 'use_case', 'customer_portrait']:
                        if key in ma and ma[key]:
                            text_parts.append(str(ma[key]))
            
            return ' '.join(text_parts)
        except Exception as e:
            # 静默处理错误，返回空字符串
            return ""
    
    def segment_by_time_window(self, user_records):
        """按时间窗口对用户记录进行切片"""
        if not user_records:
            return []
        
        # 按时间排序
        sorted_records = sorted(user_records, key=lambda x: self.parse_timestamp(x['timestamp']))
        
        segments = []
        current_segment = [sorted_records[0]]
        
        for i in range(1, len(sorted_records)):
            prev_time = self.parse_timestamp(sorted_records[i-1]['timestamp'])
            curr_time = self.parse_timestamp(sorted_records[i]['timestamp'])
            time_gap = curr_time - prev_time
            
            # 判断是否需要切分
            should_split = False
            
            if self.fixed_window:
                # 固定窗口模式
                segment_start = self.parse_timestamp(current_segment[0]['timestamp'])
                if curr_time - segment_start >= self.fixed_window:
                    should_split = True
            else:
                # 动态窗口模式
                if time_gap > self.gap_threshold:
                    # 间隔超过阈值，切分
                    should_split = True
                elif time_gap > self.inactivity_threshold:
                    # 超过无操作阈值，切分
                    should_split = True
            
            if should_split:
                # 保存当前片段，开始新片段
                segments.append(current_segment)
                current_segment = [sorted_records[i]]
            else:
                # 继续当前片段
                current_segment.append(sorted_records[i])
        
        # 添加最后一个片段
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def segment_to_text(self, segment):
        """将片段转换为文本（用于聚类）"""
        texts = []
        for record in segment:
            text = self.extract_text_features(record['output'])
            if text:
                texts.append(text)
        return ' '.join(texts)
    
    def analyze(self, input_file='extracted_data.json'):
        """执行完整的聚类分析"""
        print(f"正在读取数据: {input_file}")
        
        # 读取数据
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"总记录数: {len(data)}")
        
        # 按用户分组
        user_records = defaultdict(list)
        for record in data:
            user_id = record.get('user_id', '')
            if user_id:
                user_records[user_id].append(record)
        
        print(f"用户数: {len(user_records)}")
        
        # 对每个用户进行时间切片
        all_segments = []
        segment_metadata = []
        
        for user_id, records in user_records.items():
            segments = self.segment_by_time_window(records)
            for seg_idx, segment in enumerate(segments):
                if segment:
                    # 提取文本特征
                    text = self.segment_to_text(segment)
                    if text:
                        all_segments.append(text)
                        # 保存元数据
                        first_record = segment[0]
                        last_record = segment[-1]
                        segment_metadata.append({
                            'user_id': user_id,
                            'segment_id': f"{user_id}_seg_{seg_idx}",
                            'segment_index': seg_idx,
                            'start_time': first_record['timestamp'],
                            'end_time': last_record['timestamp'],
                            'duration_minutes': (
                                self.parse_timestamp(last_record['timestamp']) - 
                                self.parse_timestamp(first_record['timestamp'])
                            ).total_seconds() / 60,
                            'record_count': len(segment),
                            'text': text
                        })
        
        print(f"总片段数: {len(all_segments)}")
        
        if len(all_segments) < 2:
            print("片段数太少，无法进行聚类分析")
            return
        
        # 文本向量化
        print("正在进行文本向量化...")
        vectorizer = TfidfVectorizer(
            max_features=500,
            min_df=2,
            max_df=0.95,
            ngram_range=(1, 2),
            stop_words='english'
        )
        X = vectorizer.fit_transform(all_segments)
        
        print(f"特征维度: {X.shape}")
        
        # 聚类分析
        print("正在进行聚类分析...")
        
        # 方法1: KMeans（需要指定聚类数）
        n_clusters = min(20, max(3, len(all_segments) // 10))  # 自适应聚类数
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(X)
        
        # 方法2: DBSCAN（自动确定聚类数）
        dbscan = DBSCAN(eps=0.3, min_samples=3, metric='cosine')
        dbscan_labels = dbscan.fit_predict(X.toarray())
        
        # 添加聚类结果到元数据
        for i, metadata in enumerate(segment_metadata):
            metadata['kmeans_cluster'] = int(kmeans_labels[i])
            metadata['dbscan_cluster'] = int(dbscan_labels[i])
        
        # 保存结果
        results = {
            'segments': segment_metadata,
            'clustering': {
                'kmeans': {
                    'n_clusters': n_clusters,
                    'cluster_counts': {int(k): int(np.sum(kmeans_labels == k)) 
                                     for k in range(n_clusters)}
                },
                'dbscan': {
                    'n_clusters': len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0),
                    'n_noise': int(np.sum(dbscan_labels == -1)),
                    'cluster_counts': {int(k): int(np.sum(dbscan_labels == k)) 
                                     for k in set(dbscan_labels) if k != -1}
                }
            }
        }
        
        # 保存JSON结果
        output_file = 'cluster_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"结果已保存到: {output_file}")
        
        # 保存CSV结果（便于查看）
        csv_file = 'cluster_results.csv'
        df = pd.DataFrame(segment_metadata)
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"CSV结果已保存到: {csv_file}")
        
        # 生成聚类摘要
        self.generate_summary(results, vectorizer, all_segments)
        
        return results
    
    def generate_summary(self, results, vectorizer, texts):
        """生成聚类摘要报告"""
        print("\n" + "="*80)
        print("聚类分析摘要")
        print("="*80)
        
        segments = results['segments']
        kmeans_info = results['clustering']['kmeans']
        dbscan_info = results['clustering']['dbscan']
        
        print(f"\n总片段数: {len(segments)}")
        print(f"\nKMeans 聚类结果:")
        print(f"  聚类数: {kmeans_info['n_clusters']}")
        print(f"  各聚类大小: {kmeans_info['cluster_counts']}")
        
        print(f"\nDBSCAN 聚类结果:")
        print(f"  聚类数: {dbscan_info['n_clusters']}")
        print(f"  噪声点: {dbscan_info['n_noise']}")
        print(f"  各聚类大小: {dbscan_info['cluster_counts']}")
        
        # 按KMeans聚类分组，显示每个聚类的代表性文本
        print(f"\nKMeans 各聚类代表性片段（前3个）:")
        for cluster_id in range(kmeans_info['n_clusters']):
            cluster_segments = [s for s in segments if s['kmeans_cluster'] == cluster_id]
            if cluster_segments:
                print(f"\n  聚类 {cluster_id} (共 {len(cluster_segments)} 个片段):")
                for i, seg in enumerate(cluster_segments[:3]):
                    text_preview = seg['text'][:200] + "..." if len(seg['text']) > 200 else seg['text']
                    print(f"    片段 {i+1}: {text_preview}")
        
        # 保存摘要到文件
        summary_file = 'cluster_summary.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("意图聚类分析摘要\n")
            f.write("="*80 + "\n\n")
            f.write(f"总片段数: {len(segments)}\n")
            f.write(f"\nKMeans 聚类结果:\n")
            f.write(f"  聚类数: {kmeans_info['n_clusters']}\n")
            f.write(f"  各聚类大小: {kmeans_info['cluster_counts']}\n")
            f.write(f"\nDBSCAN 聚类结果:\n")
            f.write(f"  聚类数: {dbscan_info['n_clusters']}\n")
            f.write(f"  噪声点: {dbscan_info['n_noise']}\n")
            f.write(f"  各聚类大小: {dbscan_info['cluster_counts']}\n")
            
            f.write(f"\n各聚类详细信息:\n")
            for cluster_id in range(kmeans_info['n_clusters']):
                cluster_segments = [s for s in segments if s['kmeans_cluster'] == cluster_id]
                if cluster_segments:
                    f.write(f"\n聚类 {cluster_id} (共 {len(cluster_segments)} 个片段):\n")
                    for i, seg in enumerate(cluster_segments[:5]):
                        f.write(f"  片段 {i+1}:\n")
                        f.write(f"    用户: {seg['user_id']}\n")
                        f.write(f"    时间: {seg['start_time']} 到 {seg['end_time']}\n")
                        f.write(f"    时长: {seg['duration_minutes']:.2f} 分钟\n")
                        f.write(f"    记录数: {seg['record_count']}\n")
                        text_preview = seg['text'][:300] + "..." if len(seg['text']) > 300 else seg['text']
                        f.write(f"    文本: {text_preview}\n\n")
        
        print(f"\n详细摘要已保存到: {summary_file}")


def main():
    """主函数"""
    # 创建分析器
    # 可以调整这些参数：
    # - gap_threshold_minutes: 事件间隔阈值（分钟）
    # - inactivity_threshold_minutes: 无操作阈值（分钟）
    # - fixed_window_minutes: 固定窗口（分钟，None表示使用动态窗口）
    
    analyzer = IntentClusterAnalyzer(
        gap_threshold_minutes=10,      # 间隔 > 10分钟 → 切分
        inactivity_threshold_minutes=15,  # 15分钟无操作 → 切分
        fixed_window_minutes=None      # None = 使用动态窗口，或设置如 5/10 使用固定窗口
    )
    
    # 执行分析
    results = analyzer.analyze('extracted_data.json')
    
    print("\n分析完成！")


if __name__ == '__main__':
    main()

