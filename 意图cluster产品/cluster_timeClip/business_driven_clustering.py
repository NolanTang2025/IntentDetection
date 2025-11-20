#!/usr/bin/env python3
"""
基于业务维度的意图聚类分析
目标：创建有明显业务区分度的用户聚类，驱动差异化营销策略
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from pathlib import Path

class BusinessDrivenClusterer:
    def __init__(self, 
                 gap_threshold_minutes=10,
                 inactivity_threshold_minutes=15):
        self.gap_threshold = timedelta(minutes=gap_threshold_minutes)
        self.inactivity_threshold = timedelta(minutes=inactivity_threshold_minutes)
    
    def parse_timestamp(self, ts_str):
        """解析时间戳字符串"""
        try:
            return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        except:
            return datetime.fromisoformat(ts_str)
    
    def extract_business_features(self, output_str, duration_minutes, record_count):
        """从output中提取业务特征"""
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
            
            features = {
                # 购买阶段编码 (0=browsing, 1=comparing, 2=deciding)
                'purchase_stage': 0,
                # 价格敏感度编码 (0=budget, 1=mid-range, 2=premium)
                'price_sensitivity': 2,
                # 参与度编码 (基于时长和交互次数)
                'engagement_level': 0,
                # 产品偏好编码 (0=Z6, 1=A1, 2=F1, 3=H02, 4=G1, 5=其他/多产品)
                'product_preference': 5,
                # 关注点编码 (0=功能导向, 1=价格导向, 2=舒适度导向, 3=有效性导向, 4=综合)
                'concern_focus': 4,
                # 核心需求编码 (0=止鼾, 1=颈部疼痛, 2=睡眠质量, 3=综合)
                'core_need': 3,
                # 意图强度
                'intent_score': data.get('intent_score', 0.5)
            }
            
            # 1. 购买阶段
            purchase_signals = intent.get('purchase_signals', {})
            stage = purchase_signals.get('stage', 'browsing')
            if 'deciding' in str(stage).lower():
                features['purchase_stage'] = 2
            elif 'comparing' in str(stage).lower():
                features['purchase_stage'] = 1
            else:
                features['purchase_stage'] = 0
            
            # 2. 价格敏感度
            product_focus = intent.get('product_focus', {})
            price_range = product_focus.get('price_range', 'premium')
            if 'budget' in str(price_range).lower() or 'economy' in str(price_range).lower():
                features['price_sensitivity'] = 0
            elif 'mid' in str(price_range).lower() or 'medium' in str(price_range).lower():
                features['price_sensitivity'] = 1
            else:
                features['price_sensitivity'] = 2
            
            # 3. 参与度（基于时长和交互次数）
            # 快速浏览: <1分钟 且 <3次交互
            # 中等参与: 1-5分钟 或 3-10次交互
            # 深度研究: >5分钟 或 >10次交互
            if duration_minutes < 1 and record_count < 3:
                features['engagement_level'] = 0  # 快速浏览
            elif duration_minutes > 5 or record_count > 10:
                features['engagement_level'] = 2  # 深度研究
            elif duration_minutes >= 1 or record_count >= 3:
                features['engagement_level'] = 1  # 中等参与
            else:
                features['engagement_level'] = 0  # 默认快速浏览
            
            # 4. 产品偏好
            core_interests = intent.get('core_interests', [])
            product_focus_attrs = product_focus.get('key_attributes', [])
            all_text = ' '.join([str(x).lower() for x in core_interests + product_focus_attrs])
            
            product_counts = {
                'z6': all_text.count('z6') + all_text.count('mems'),
                'a1': all_text.count('a1') + all_text.count('ai anti-snore'),
                'f1': all_text.count('f1') + all_text.count('ergonomic'),
                'h02': all_text.count('h02') + all_text.count('neck'),
                'g1': all_text.count('g1') + all_text.count('mattress')
            }
            
            max_product = max(product_counts.items(), key=lambda x: x[1])
            if max_product[1] > 0:
                product_map = {'z6': 0, 'a1': 1, 'f1': 2, 'h02': 3, 'g1': 4}
                features['product_preference'] = product_map.get(max_product[0], 5)
            
            # 5. 关注点
            concerns = purchase_signals.get('concerns', [])
            if isinstance(concerns, str):
                concerns = [concerns]
            concerns_text = ' '.join([str(x).lower() for x in concerns])
            
            if 'price' in concerns_text or 'cost' in concerns_text or 'discount' in concerns_text:
                features['concern_focus'] = 1  # 价格导向
            elif 'comfort' in concerns_text or 'comfortable' in concerns_text:
                features['concern_focus'] = 2  # 舒适度导向
            elif 'effectiveness' in concerns_text or 'effective' in concerns_text or 'work' in concerns_text:
                features['concern_focus'] = 3  # 有效性导向
            elif 'feature' in concerns_text or 'function' in concerns_text or 'technology' in concerns_text:
                features['concern_focus'] = 0  # 功能导向
            else:
                features['concern_focus'] = 4  # 综合
            
            # 6. 核心需求
            main_appeal = product_focus.get('main_appeal', '')
            if 'snore' in str(main_appeal).lower() or 'snoring' in str(main_appeal).lower():
                features['core_need'] = 0  # 止鼾
            elif 'neck' in str(main_appeal).lower() or 'pain' in str(main_appeal).lower():
                features['core_need'] = 1  # 颈部疼痛
            elif 'sleep' in str(main_appeal).lower() and 'quality' in str(main_appeal).lower():
                features['core_need'] = 2  # 睡眠质量
            else:
                features['core_need'] = 3  # 综合
            
            return features
            
        except Exception as e:
            # 如果解析失败，返回默认值
            return {
                'purchase_stage': 0,
                'price_sensitivity': 2,
                'engagement_level': 0,
                'product_preference': 5,
                'concern_focus': 4,
                'core_need': 3,
                'intent_score': 0.5
            }
    
    def segment_by_time(self, data):
        """按时间窗口切分用户行为"""
        # 按用户分组
        user_groups = defaultdict(list)
        for record in data:
            user_groups[record['user_id']].append(record)
        
        all_segments = []
        segment_metadata = []
        
        for user_id, records in user_groups.items():
            # 按时间排序
            records.sort(key=lambda x: self.parse_timestamp(x['timestamp']))
            
            # 时间窗口切分
            segments = []
            current_segment = [records[0]]
            
            for i in range(1, len(records)):
                prev_time = self.parse_timestamp(records[i-1]['timestamp'])
                curr_time = self.parse_timestamp(records[i]['timestamp'])
                time_gap = curr_time - prev_time
                
                if time_gap > self.gap_threshold or time_gap > self.inactivity_threshold:
                    # 开始新片段
                    segments.append(current_segment)
                    current_segment = [records[i]]
                else:
                    current_segment.append(records[i])
            
            if current_segment:
                segments.append(current_segment)
            
            # 为每个片段提取特征
            for seg_idx, segment in enumerate(segments):
                if len(segment) == 0:
                    continue
                
                first_record = segment[0]
                last_record = segment[-1]
                duration = (self.parse_timestamp(last_record['timestamp']) - 
                           self.parse_timestamp(first_record['timestamp'])).total_seconds() / 60
                
                # 合并所有output文本
                combined_output = ' '.join([r.get('output', '') for r in segment])
                
                # 提取业务特征
                features = self.extract_business_features(
                    combined_output, 
                    duration, 
                    len(segment)
                )
                
                # 保存片段元数据
                metadata = {
                    'user_id': user_id,
                    'segment_id': f"{user_id}_seg_{seg_idx}",
                    'segment_index': seg_idx,
                    'start_time': first_record['timestamp'],
                    'end_time': last_record['timestamp'],
                    'duration_minutes': duration,
                    'record_count': len(segment),
                    **features
                }
                
                segment_metadata.append(metadata)
                all_segments.append(segment)
        
        return all_segments, segment_metadata
    
    def cluster_by_business_dimensions(self, segment_metadata):
        """基于业务维度进行聚类"""
        df = pd.DataFrame(segment_metadata)
        
        # 选择用于聚类的特征
        feature_cols = [
            'purchase_stage',
            'price_sensitivity',
            'engagement_level',
            'product_preference',
            'concern_focus',
            'core_need',
            'intent_score'
        ]
        
        # 提取特征矩阵
        X = df[feature_cols].values
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 使用KMeans聚类
        # 根据业务需求，我们创建12-15个有明显差异的聚类
        # 先尝试15个聚类，如果某个聚类太大，可以进一步细分
        n_clusters = 15
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # 添加聚类标签
        df['business_cluster'] = cluster_labels
        
        # 检查是否有过大的聚类（>30%的数据），如果有则进一步细分
        cluster_counts = pd.Series(cluster_labels).value_counts()
        max_cluster_size = len(df) * 0.3
        
        # 迭代细分，直到没有过大的聚类
        max_iterations = 3
        iteration = 0
        while cluster_counts.max() > max_cluster_size and iteration < max_iterations:
            iteration += 1
            # 找到过大的聚类
            large_cluster_id = cluster_counts.idxmax()
            large_cluster_data = df[df['business_cluster'] == large_cluster_id]
            
            # 对过大聚类进行二次聚类
            if len(large_cluster_data) > 5:
                X_large = large_cluster_data[feature_cols].values
                X_large_scaled = scaler.transform(X_large)
                
                # 对过大聚类再分3-5个子聚类
                n_sub_clusters = min(5, max(3, len(large_cluster_data) // 20))
                if n_sub_clusters > 1:
                    sub_kmeans = KMeans(n_clusters=n_sub_clusters, random_state=42, n_init=10)
                    sub_labels = sub_kmeans.fit_predict(X_large_scaled)
                    
                    # 重新分配聚类ID（使用新的ID范围）
                    max_existing_cluster = max(df['business_cluster'].values)
                    new_cluster_ids = [max_existing_cluster + 1 + label for label in sub_labels]
                    
                    # 更新聚类标签
                    df.loc[df['business_cluster'] == large_cluster_id, 'business_cluster'] = new_cluster_ids
                    cluster_labels = df['business_cluster'].values
                    cluster_counts = pd.Series(cluster_labels).value_counts()
                else:
                    break
            else:
                break
        
        # 添加聚类标签
        df['business_cluster'] = cluster_labels
        
        # 为每个聚类生成业务标签
        cluster_labels_dict = self.generate_cluster_labels(df, df['business_cluster'].values)
        
        return df, cluster_labels_dict
    
    def generate_cluster_labels(self, df, cluster_labels):
        """为每个聚类生成有业务含义的标签"""
        cluster_labels_dict = {}
        
        # 获取所有唯一的聚类ID，转换为Python原生类型
        unique_cluster_ids = sorted([int(x) for x in df['business_cluster'].unique()])
        
        for cluster_id in unique_cluster_ids:
            cluster_data = df[df['business_cluster'] == cluster_id]
            
            # 计算聚类的平均特征
            avg_stage = cluster_data['purchase_stage'].mean()
            avg_price = cluster_data['price_sensitivity'].mean()
            avg_engagement = cluster_data['engagement_level'].mean()
            avg_product = cluster_data['product_preference'].mode()[0] if len(cluster_data['product_preference'].mode()) > 0 else 5
            avg_concern = cluster_data['concern_focus'].mode()[0] if len(cluster_data['concern_focus'].mode()) > 0 else 4
            avg_need = cluster_data['core_need'].mode()[0] if len(cluster_data['core_need'].mode()) > 0 else 3
            
            # 生成业务标签
            # 购买阶段标签
            if avg_stage >= 1.5:
                stage_label = "决策阶段"
            elif avg_stage >= 0.5:
                stage_label = "对比阶段"
            else:
                stage_label = "浏览阶段"
            
            # 价格敏感度标签
            if avg_price <= 0.5:
                price_label = "价格敏感型"
            elif avg_price <= 1.5:
                price_label = "中等价格型"
            else:
                price_label = "高端价值型"
            
            # 参与度标签
            if avg_engagement >= 1.5:
                engagement_label = "深度研究者"
            elif avg_engagement >= 0.5:
                engagement_label = "中等参与"
            else:
                engagement_label = "快速浏览者"
            
            # 产品偏好标签
            product_map = {0: "Z6偏好", 1: "A1偏好", 2: "F1偏好", 3: "H02偏好", 4: "G1偏好", 5: "多产品比较"}
            product_label = product_map.get(int(avg_product), "多产品比较")
            
            # 关注点标签
            concern_map = {0: "功能导向", 1: "价格导向", 2: "舒适度导向", 3: "有效性导向", 4: "综合关注"}
            concern_label = concern_map.get(int(avg_concern), "综合关注")
            
            # 核心需求标签
            need_map = {0: "止鼾需求", 1: "颈部疼痛", 2: "睡眠质量", 3: "综合需求"}
            need_label = need_map.get(int(avg_need), "综合需求")
            
            # 组合标签（选择最重要的3-4个维度）
            # 优先级：参与度 > 购买阶段 > 价格敏感度 > 产品偏好 > 核心需求
            # 创建更有区分度的标签
            if avg_engagement >= 1.5:
                # 深度研究者优先显示
                if avg_stage >= 1.5:
                    primary_label = f"{engagement_label}·决策型"
                elif avg_stage >= 0.5:
                    primary_label = f"{engagement_label}·对比型"
                else:
                    primary_label = f"{engagement_label}·浏览型"
            elif avg_stage >= 1.5:
                # 决策阶段优先显示
                primary_label = f"{price_label}·决策型"
            elif avg_stage >= 0.5:
                # 对比阶段优先显示
                primary_label = f"{price_label}·对比型"
            else:
                # 浏览阶段
                if avg_engagement >= 0.5:
                    primary_label = f"{price_label}·中等参与"
                else:
                    primary_label = f"{price_label}·快速浏览"
            
            # 完整标签（包含产品偏好和核心需求，增加区分度）
            if product_label != "多产品比较":
                full_label = f"{primary_label}·{product_label}·{need_label}"
            else:
                # 如果产品偏好不明确，用关注点替代
                full_label = f"{primary_label}·{concern_label}·{need_label}"
            
            # 确保cluster_id是Python原生int类型
            cluster_labels_dict[int(cluster_id)] = {
                'short_label': primary_label,
                'full_label': full_label,
                'characteristics': {
                    'stage': stage_label,
                    'price': price_label,
                    'engagement': engagement_label,
                    'product': product_label,
                    'concern': concern_label,
                    'need': need_label
                },
                'avg_features': {
                    'purchase_stage': float(avg_stage),
                    'price_sensitivity': float(avg_price),
                    'engagement_level': float(avg_engagement),
                    'product_preference': int(avg_product),
                    'concern_focus': int(avg_concern),
                    'core_need': int(avg_need)
                }
            }
        
        return cluster_labels_dict
    
    def analyze(self, input_file='../extracted_data.json'):
        """执行完整的聚类分析"""
        print("="*80)
        print("基于业务维度的意图聚类分析")
        print("="*80)
        
        # 加载数据
        print(f"\n正在加载数据: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"加载了 {len(data)} 条记录")
        
        # 时间窗口切分
        print("\n正在进行时间窗口切分...")
        all_segments, segment_metadata = self.segment_by_time(data)
        print(f"切分为 {len(segment_metadata)} 个意图片段")
        
        # 业务维度聚类
        print("\n正在进行业务维度聚类...")
        df, cluster_labels_dict = self.cluster_by_business_dimensions(segment_metadata)
        
        # 保存结果
        # 确保聚类ID是Python原生类型
        cluster_counts_dict = {}
        for k, v in df['business_cluster'].value_counts().to_dict().items():
            cluster_counts_dict[int(k)] = int(v)
        
        results = {
            'segments': df.to_dict('records'),
            'clustering': {
                'n_clusters': len(set(df['business_cluster'])),
                'cluster_labels': cluster_labels_dict,
                'cluster_counts': cluster_counts_dict
            }
        }
        
        output_file = 'business_cluster_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n结果已保存到: {output_file}")
        
        # 保存CSV
        csv_file = 'business_cluster_results.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"CSV结果已保存到: {csv_file}")
        
        # 打印聚类摘要
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results):
        """打印聚类摘要"""
        print("\n" + "="*80)
        print("聚类分析摘要")
        print("="*80)
        
        df = pd.DataFrame(results['segments'])
        cluster_labels = results['clustering']['cluster_labels']
        cluster_counts = results['clustering']['cluster_counts']
        
        print(f"\n总片段数: {len(df)}")
        print(f"总用户数: {df['user_id'].nunique()}")
        print(f"聚类数: {results['clustering']['n_clusters']}")
        
        print("\n各聚类详情:")
        print("-"*80)
        for cluster_id in sorted(cluster_counts.keys()):
            count = cluster_counts[cluster_id]
            if cluster_id not in cluster_labels:
                # 如果聚类ID不在标签字典中，生成一个临时标签
                cluster_df = df[df['business_cluster'] == cluster_id]
                label_info = {
                    'short_label': f"聚类{cluster_id}",
                    'full_label': f"聚类{cluster_id}",
                    'characteristics': {},
                    'avg_features': {}
                }
            else:
                label_info = cluster_labels[cluster_id]
            
            cluster_df = df[df['business_cluster'] == cluster_id]
            
            print(f"\n聚类 {cluster_id}: {label_info['short_label']}")
            print(f"  片段数: {count}")
            print(f"  用户数: {cluster_df['user_id'].nunique()}")
            print(f"  完整标签: {label_info['full_label']}")
            if label_info.get('characteristics'):
                print(f"  特征: {label_info['characteristics']}")
            print(f"  平均浏览时长: {cluster_df['duration_minutes'].mean():.2f} 分钟")
            print(f"  平均交互次数: {cluster_df['record_count'].mean():.2f} 次")
            print(f"  平均意图强度: {cluster_df['intent_score'].mean():.2f}")

if __name__ == '__main__':
    clusterer = BusinessDrivenClusterer()
    clusterer.analyze()

