#!/usr/bin/env python3
"""
基于用户行为意图的聚类分析
目标：让商家可以快速捕捉到当下的用户意图并给出相应的反应
结合行为特征（交互次数、时长、意图强度）和意图特征（购买阶段、产品偏好等）
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from pathlib import Path

class BehaviorIntentClusterer:
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
        """从output中提取业务特征（复用原有逻辑）"""
        try:
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
            
            data = json.loads(cleaned)
            intent = data.get('intent', {})
            
            features = {
                'purchase_stage': 0,
                'price_sensitivity': 2,
                'product_preference': 5,
                'concern_focus': 4,
                'core_need': 3,
                'intent_score': data.get('intent_score', 0.5)
            }
            
            # 购买阶段
            purchase_signals = intent.get('purchase_signals', {})
            stage = purchase_signals.get('stage', 'browsing')
            if 'deciding' in str(stage).lower():
                features['purchase_stage'] = 2
            elif 'comparing' in str(stage).lower():
                features['purchase_stage'] = 1
            else:
                features['purchase_stage'] = 0
            
            # 价格敏感度
            product_focus = intent.get('product_focus', {})
            price_range = product_focus.get('price_range', 'premium')
            if 'budget' in str(price_range).lower() or 'economy' in str(price_range).lower():
                features['price_sensitivity'] = 0
            elif 'mid' in str(price_range).lower() or 'medium' in str(price_range).lower():
                features['price_sensitivity'] = 1
            else:
                features['price_sensitivity'] = 2
            
            # 产品偏好
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
            
            # 关注点
            concerns = purchase_signals.get('concerns', [])
            if isinstance(concerns, str):
                concerns = [concerns]
            concerns_text = ' '.join([str(x).lower() for x in concerns])
            
            if 'price' in concerns_text or 'cost' in concerns_text or 'discount' in concerns_text:
                features['concern_focus'] = 1
            elif 'comfort' in concerns_text or 'comfortable' in concerns_text:
                features['concern_focus'] = 2
            elif 'effectiveness' in concerns_text or 'effective' in concerns_text or 'work' in concerns_text:
                features['concern_focus'] = 3
            elif 'feature' in concerns_text or 'function' in concerns_text or 'technology' in concerns_text:
                features['concern_focus'] = 0
            else:
                features['concern_focus'] = 4
            
            # 核心需求
            main_appeal = product_focus.get('main_appeal', '')
            if 'snore' in str(main_appeal).lower() or 'snoring' in str(main_appeal).lower():
                features['core_need'] = 0
            elif 'neck' in str(main_appeal).lower() or 'pain' in str(main_appeal).lower():
                features['core_need'] = 1
            elif 'sleep' in str(main_appeal).lower() and 'quality' in str(main_appeal).lower():
                features['core_need'] = 2
            else:
                features['core_need'] = 3
            
            return features
            
        except Exception as e:
            return {
                'purchase_stage': 0,
                'price_sensitivity': 2,
                'product_preference': 5,
                'concern_focus': 4,
                'core_need': 3,
                'intent_score': 0.5
            }
    
    def segment_by_time(self, data):
        """按时间窗口切分用户行为"""
        user_groups = defaultdict(list)
        for record in data:
            user_groups[record['user_id']].append(record)
        
        all_segments = []
        segment_metadata = []
        
        for user_id, records in user_groups.items():
            records.sort(key=lambda x: self.parse_timestamp(x['timestamp']))
            
            segments = []
            current_segment = [records[0]]
            
            for i in range(1, len(records)):
                prev_time = self.parse_timestamp(records[i-1]['timestamp'])
                curr_time = self.parse_timestamp(records[i]['timestamp'])
                time_gap = curr_time - prev_time
                
                if time_gap > self.gap_threshold or time_gap > self.inactivity_threshold:
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
                
                combined_output = ' '.join([r.get('output', '') for r in segment])
                
                features = self.extract_business_features(
                    combined_output, 
                    duration, 
                    len(segment)
                )
                
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
    
    def cluster_by_behavior_intent(self, segment_metadata):
        """基于行为意图进行聚类 - 使用原始特征，让算法自动发现模式"""
        df = pd.DataFrame(segment_metadata)
        
        # 使用原始特征进行聚类，不做人工定义
        # 只做合理的特征工程（对数变换处理长尾分布，标准化）
        feature_cols = [
            # 行为特征（原始值）
            'record_count',          # 交互次数
            'duration_minutes',      # 浏览时长（分钟）
            'intent_score',          # 意图强度
            # 意图特征（从文本提取的）
            'purchase_stage',        # 购买阶段 (0=browsing, 1=comparing, 2=deciding)
            'product_preference',    # 产品偏好 (0-5)
            'concern_focus',         # 关注点 (0-4)
            'core_need'              # 核心需求 (0-3)
        ]
        
        # 提取特征矩阵
        X = df[feature_cols].copy()
        
        # 对长尾分布的特征进行对数变换（让算法更容易发现模式）
        X['record_count_log'] = np.log1p(X['record_count'])
        X['duration_minutes_log'] = np.log1p(X['duration_minutes'] + 0.001)  # 避免log(0)
        
        # 移除原始值，使用变换后的值
        X = X.drop(['record_count', 'duration_minutes'], axis=1)
        X.columns = ['intent_score', 'purchase_stage', 'product_preference', 
                     'concern_focus', 'core_need', 'record_count_log', 'duration_minutes_log']
        
        # 标准化（让不同量纲的特征在相同尺度上）
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 使用KMeans聚类 - 让算法自动发现数据中的模式
        # 使用肘部法则或轮廓系数来确定最优聚类数
        # 这里先用一个合理的范围，后续可以优化
        n_clusters = 15
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20, max_iter=300)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        df['business_cluster'] = cluster_labels
        
        # 保存原始特征值用于后续分析
        df['record_count_log'] = X['record_count_log'].values
        df['duration_minutes_log'] = X['duration_minutes_log'].values
        
        # 为每个聚类生成业务标签（基于聚类结果的特征分布）
        cluster_labels_dict = self.generate_behavior_intent_labels(df, df['business_cluster'].values)
        
        return df, cluster_labels_dict
    
    def generate_behavior_intent_labels(self, df, cluster_labels):
        """为每个聚类生成基于行为意图的标签 - 根据算法发现的模式自动生成"""
        cluster_labels_dict = {}
        unique_cluster_ids = sorted([int(x) for x in df['business_cluster'].unique()])
        
        # 计算全局统计信息，用于相对比较
        global_avg_record = df['record_count'].mean()
        global_avg_duration = df['duration_minutes'].mean()
        global_avg_intent = df['intent_score'].mean()
        
        for cluster_id in unique_cluster_ids:
            cluster_data = df[df['business_cluster'] == cluster_id]
            
            # 计算聚类的平均特征（使用原始值）
            avg_record_count = cluster_data['record_count'].mean()
            avg_duration = cluster_data['duration_minutes'].mean()
            avg_intent = cluster_data['intent_score'].mean()
            avg_stage = cluster_data['purchase_stage'].mean()
            avg_product = cluster_data['product_preference'].mode()[0] if len(cluster_data['product_preference'].mode()) > 0 else 5
            avg_concern = cluster_data['concern_focus'].mode()[0] if len(cluster_data['concern_focus'].mode()) > 0 else 4
            avg_need = cluster_data['core_need'].mode()[0] if len(cluster_data['core_need'].mode()) > 0 else 3
            
            # 根据算法发现的模式自动生成行为标签（基于相对值）
            record_ratio = avg_record_count / global_avg_record if global_avg_record > 0 else 1
            duration_ratio = avg_duration / global_avg_duration if global_avg_duration > 0 else 1
            
            # 行为模式：基于算法发现的交互模式
            if avg_record_count <= 1:
                behavior_label = "单次浏览"
                action_priority = "低优先级"
                recommended_action = "观察，无需立即反应"
            elif record_ratio < 0.5 and duration_ratio < 0.5:
                behavior_label = "快速浏览"
                action_priority = "中优先级"
                recommended_action = "优化首屏内容，快速抓住注意力"
            elif record_ratio > 2 or duration_ratio > 2:
                behavior_label = "深度研究"
                action_priority = "高优先级"
                recommended_action = "提供专业咨询和转化激励"
            else:
                behavior_label = "中等参与"
                action_priority = "中高优先级"
                recommended_action = "提供详细信息和引导"
            
            # 意图紧迫度：基于算法发现的意图模式
            intent_ratio = avg_intent / global_avg_intent if global_avg_intent > 0 else 1
            if avg_intent > 0.8 and avg_stage >= 1.5:
                urgency_label = "高紧迫"
            elif avg_intent > 0.7 or avg_stage >= 1:
                urgency_label = "中紧迫"
            else:
                urgency_label = "低紧迫"
            
            # 购买阶段标签
            if avg_stage >= 1.5:
                stage_label = "决策阶段"
            elif avg_stage >= 0.5:
                stage_label = "对比阶段"
            else:
                stage_label = "浏览阶段"
            
            # 产品偏好标签
            product_map = {0: "Z6偏好", 1: "A1偏好", 2: "F1偏好", 3: "H02偏好", 4: "G1偏好", 5: "多产品比较"}
            product_label = product_map.get(int(avg_product), "多产品比较")
            
            # 关注点标签
            concern_map = {0: "功能导向", 1: "价格导向", 2: "舒适度导向", 3: "有效性导向", 4: "综合关注"}
            concern_label = concern_map.get(int(avg_concern), "综合关注")
            
            # 核心需求标签
            need_map = {0: "止鼾需求", 1: "颈部疼痛", 2: "睡眠质量", 3: "综合需求"}
            need_label = need_map.get(int(avg_need), "综合需求")
            
            # 生成主标签：行为模式 + 意图紧迫度（基于算法发现的模式）
            if urgency_label == "高紧迫" and behavior_label == "深度研究":
                primary_label = f"高紧迫·深度研究"
            elif urgency_label == "高紧迫":
                primary_label = f"高紧迫·{behavior_label}"
            elif behavior_label == "深度研究":
                primary_label = f"深度研究·{urgency_label}"
            elif behavior_label == "单次浏览":
                primary_label = f"单次浏览·{urgency_label}"
            else:
                primary_label = f"{behavior_label}·{urgency_label}"
            
            # 完整标签
            if product_label != "多产品比较":
                full_label = f"{primary_label}·{product_label}·{need_label}"
            else:
                full_label = f"{primary_label}·{concern_label}·{need_label}"
            
            cluster_labels_dict[int(cluster_id)] = {
                'short_label': primary_label,
                'full_label': full_label,
                'action_priority': action_priority,
                'recommended_action': recommended_action,
                'characteristics': {
                    'behavior': behavior_label,
                    'urgency': urgency_label,
                    'stage': stage_label,
                    'product': product_label,
                    'concern': concern_label,
                    'need': need_label
                },
                'avg_features': {
                    'record_count': float(avg_record_count),
                    'duration_minutes': float(avg_duration),
                    'intent_score': float(avg_intent),
                    'purchase_stage': float(avg_stage),
                    'product_preference': int(avg_product),
                    'concern_focus': int(avg_concern),
                    'core_need': int(avg_need)
                }
            }
        
        return cluster_labels_dict
    
    def analyze(self, input_file='../extracted_data.json'):
        """执行完整的聚类分析"""
        print("="*80)
        print("基于用户行为意图的聚类分析")
        print("目标：让商家可以快速捕捉到当下的用户意图并给出相应的反应")
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
        
        # 行为意图聚类
        print("\n正在进行行为意图聚类...")
        df, cluster_labels_dict = self.cluster_by_behavior_intent(segment_metadata)
        
        # 保存结果
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
        print("行为意图聚类分析摘要")
        print("="*80)
        
        df = pd.DataFrame(results['segments'])
        cluster_labels = results['clustering']['cluster_labels']
        cluster_counts = results['clustering']['cluster_counts']
        
        print(f"\n总片段数: {len(df)}")
        print(f"总用户数: {df['user_id'].nunique()}")
        print(f"聚类数: {results['clustering']['n_clusters']}")
        
        print("\n各聚类详情（按优先级排序）:")
        print("-"*80)
        
        # 按优先级排序（基于原始特征：意图强度和交互次数）
        sorted_clusters = sorted(cluster_counts.items(), 
                                key=lambda x: (
                                    cluster_labels[x[0]]['avg_features']['intent_score'],
                                    cluster_labels[x[0]]['avg_features']['record_count']
                                ), reverse=True)
        
        for cluster_id, count in sorted_clusters:
            label_info = cluster_labels[cluster_id]
            cluster_df = df[df['business_cluster'] == cluster_id]
            
            print(f"\n聚类 {cluster_id}: {label_info['short_label']}")
            print(f"  完整标签: {label_info['full_label']}")
            print(f"  优先级: {label_info['action_priority']}")
            print(f"  推荐行动: {label_info['recommended_action']}")
            print(f"  片段数: {count}")
            print(f"  用户数: {cluster_df['user_id'].nunique()}")
            print(f"  平均意图强度: {cluster_df['intent_score'].mean():.2f}")
            print(f"  平均交互次数: {cluster_df['record_count'].mean():.1f} 次")
            print(f"  平均浏览时长: {cluster_df['duration_minutes'].mean():.2f} 分钟")
            print(f"  购买阶段: {label_info['characteristics']['stage']}")
            print(f"  产品偏好: {label_info['characteristics']['product']}")

if __name__ == '__main__':
    clusterer = BehaviorIntentClusterer()
    clusterer.analyze()

