#!/usr/bin/env python3
"""
基于聚类结果的用户画像分析
分析每个聚类的用户特征，并生成业务指导性结论
"""

import json
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime
import re
from pathlib import Path

class UserPortraitAnalyzer:
    def __init__(self, cluster_results_file='../cluster_results.json'):
        self.cluster_results_file = cluster_results_file
        self.segments = []
        self.df = None
        
    def load_data(self):
        """加载聚类结果数据"""
        print("正在加载聚类结果数据...")
        with open(self.cluster_results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.segments = data['segments']
        self.df = pd.DataFrame(self.segments)
        print(f"已加载 {len(self.segments)} 个片段")
        
    def parse_intent_from_text(self, text):
        """从文本中解析意图信息"""
        intent_info = {
            'core_interests': [],
            'product_focus': {},
            'purchase_stage': None,
            'price_range': None,
            'main_appeal': None,
            'concerns': []
        }
        
        # 提取核心兴趣（常见关键词）
        interest_keywords = {
            'snoring': ['snoring', 'snore', 'anti-snore', 'anti-snoring'],
            'sleep_quality': ['sleep quality', 'sleep improvement', 'better sleep'],
            'neck_pain': ['neck pain', 'neck support', 'cervical', 'pain relief'],
            'ai_technology': ['ai', 'smart', 'technology', 'sensors'],
            'app_tracking': ['app', 'tracking', 'monitoring', 'data'],
            'ergonomic': ['ergonomic', 'comfort', 'adjustable'],
            'mattress': ['mattress', 'mattress pad', 'bed']
        }
        
        text_lower = text.lower()
        for category, keywords in interest_keywords.items():
            if any(kw in text_lower for kw in keywords):
                intent_info['core_interests'].append(category)
        
        # 提取价格范围
        if 'premium' in text_lower:
            intent_info['price_range'] = 'premium'
        elif 'mid-range' in text_lower or 'mid range' in text_lower:
            intent_info['price_range'] = 'mid-range'
        elif 'budget' in text_lower:
            intent_info['price_range'] = 'budget'
        
        # 提取购买阶段
        if 'browsing' in text_lower:
            intent_info['purchase_stage'] = 'browsing'
        elif 'comparing' in text_lower:
            intent_info['purchase_stage'] = 'comparing'
        elif 'deciding' in text_lower:
            intent_info['purchase_stage'] = 'deciding'
        
        # 提取主要吸引力
        if 'snore reduction' in text_lower or 'snoring solution' in text_lower:
            intent_info['main_appeal'] = 'snore_reduction'
        elif 'sleep quality' in text_lower:
            intent_info['main_appeal'] = 'sleep_quality'
        elif 'pain relief' in text_lower:
            intent_info['main_appeal'] = 'pain_relief'
        elif 'comfort' in text_lower:
            intent_info['main_appeal'] = 'comfort'
        
        # 提取关注点
        concern_keywords = {
            'effectiveness': ['effectiveness', 'clinically proven', 'works'],
            'price': ['price', 'cost', 'discount', 'sale'],
            'comfort': ['comfort', 'comfortable', 'ergonomic'],
            'features': ['features', 'technology', 'sensors', 'app'],
            'shipping': ['shipping', 'delivery', 'free shipping'],
            'trial': ['trial', 'return', 'warranty']
        }
        
        for concern, keywords in concern_keywords.items():
            if any(kw in text_lower for kw in keywords):
                intent_info['concerns'].append(concern)
        
        return intent_info
    
    def analyze_cluster_portrait(self, cluster_id):
        """分析单个聚类的用户画像"""
        cluster_segments = self.df[self.df['kmeans_cluster'] == cluster_id]
        
        if len(cluster_segments) == 0:
            return None
        
        # 基本统计
        portrait = {
            'cluster_id': cluster_id,
            'segment_count': len(cluster_segments),
            'unique_users': cluster_segments['user_id'].nunique(),
            'avg_duration_minutes': cluster_segments['duration_minutes'].mean(),
            'avg_record_count': cluster_segments['record_count'].mean(),
            'time_patterns': {},
            'intent_profile': {
                'core_interests': Counter(),
                'price_range': Counter(),
                'purchase_stage': Counter(),
                'main_appeal': Counter(),
                'concerns': Counter()
            },
            'product_preferences': Counter(),
            'behavior_patterns': {}
        }
        
        # 时间模式分析
        cluster_segments['start_time'] = pd.to_datetime(cluster_segments['start_time'])
        cluster_segments['hour'] = cluster_segments['start_time'].dt.hour
        cluster_segments['day_of_week'] = cluster_segments['start_time'].dt.day_name()
        
        portrait['time_patterns'] = {
            'peak_hours': cluster_segments['hour'].mode().tolist()[:3],
            'peak_days': cluster_segments['day_of_week'].mode().tolist()[:3],
            'avg_duration': cluster_segments['duration_minutes'].mean()
        }
        
        # 意图画像分析
        for _, segment in cluster_segments.iterrows():
            intent_info = self.parse_intent_from_text(segment['text'])
            
            for interest in intent_info['core_interests']:
                portrait['intent_profile']['core_interests'][interest] += 1
            
            if intent_info['price_range']:
                portrait['intent_profile']['price_range'][intent_info['price_range']] += 1
            
            if intent_info['purchase_stage']:
                portrait['intent_profile']['purchase_stage'][intent_info['purchase_stage']] += 1
            
            if intent_info['main_appeal']:
                portrait['intent_profile']['main_appeal'][intent_info['main_appeal']] += 1
            
            for concern in intent_info['concerns']:
                portrait['intent_profile']['concerns'][concern] += 1
        
        # 产品偏好分析（从文本中提取产品名称）
        product_keywords = {
            'A1': ['a1', 'ai anti-snore'],
            'Z6': ['z6', 'smart anti-snore'],
            'F1': ['f1', 'floating'],
            'H02': ['h02', 'lotus', 'cervical'],
            'G1': ['g1', 'mattress pad', 'mattress'],
            'Z1': ['z1']
        }
        
        for _, segment in cluster_segments.iterrows():
            text_lower = segment['text'].lower()
            for product, keywords in product_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    portrait['product_preferences'][product] += 1
        
        # 行为模式
        portrait['behavior_patterns'] = {
            'high_engagement': (cluster_segments['record_count'] > cluster_segments['record_count'].quantile(0.75)).sum(),
            'quick_browsing': (cluster_segments['duration_minutes'] < 1).sum(),
            'deep_research': (cluster_segments['duration_minutes'] > 5).sum(),
            'multi_session': cluster_segments['user_id'].value_counts().gt(1).sum()
        }
        
        return portrait
    
    def generate_business_insights(self, portrait):
        """基于用户画像生成业务指导性结论"""
        insights = {
            'cluster_id': portrait['cluster_id'],
            'user_segment_name': '',
            'key_characteristics': [],
            'marketing_strategy': [],
            'product_recommendations': [],
            'conversion_optimization': [],
            'pricing_strategy': [],
            'content_strategy': []
        }
        
        # 确定用户细分名称
        top_interests = [item[0] for item in portrait['intent_profile']['core_interests'].most_common(2)]
        top_appeal = portrait['intent_profile']['main_appeal'].most_common(1)
        
        if 'snoring' in str(top_interests).lower():
            insights['user_segment_name'] = '止鼾需求用户'
        elif 'neck_pain' in str(top_interests).lower():
            insights['user_segment_name'] = '颈部疼痛缓解用户'
        elif 'sleep_quality' in str(top_interests).lower():
            insights['user_segment_name'] = '睡眠质量改善用户'
        elif 'mattress' in str(top_interests).lower():
            insights['user_segment_name'] = '智能床垫用户'
        else:
            insights['user_segment_name'] = '综合睡眠产品用户'
        
        # 关键特征
        insights['key_characteristics'].append(f"用户规模: {portrait['unique_users']} 个独立用户，{portrait['segment_count']} 个意图片段")
        insights['key_characteristics'].append(f"平均浏览时长: {portrait['avg_duration_minutes']:.1f} 分钟")
        insights['key_characteristics'].append(f"平均交互次数: {portrait['avg_record_count']:.1f} 次")
        
        # 核心兴趣
        top_3_interests = portrait['intent_profile']['core_interests'].most_common(3)
        if top_3_interests:
            interests_str = '、'.join([f"{item[0]}({item[1]}次)" for item in top_3_interests])
            insights['key_characteristics'].append(f"核心关注点: {interests_str}")
        
        # 购买阶段
        purchase_stage = portrait['intent_profile']['purchase_stage'].most_common(1)
        if purchase_stage:
            stage_map = {'browsing': '浏览阶段', 'comparing': '对比阶段', 'deciding': '决策阶段'}
            stage_name = stage_map.get(purchase_stage[0][0], purchase_stage[0][0])
            insights['key_characteristics'].append(f"主要购买阶段: {stage_name} ({purchase_stage[0][1]}次)")
        
        # 价格敏感度
        price_range = portrait['intent_profile']['price_range'].most_common(1)
        if price_range:
            price_map = {'premium': '高端', 'mid-range': '中端', 'budget': '经济型'}
            price_name = price_map.get(price_range[0][0], price_range[0][0])
            insights['key_characteristics'].append(f"价格偏好: {price_name} ({price_range[0][1]}次)")
        
        # 营销策略
        if portrait['intent_profile']['purchase_stage'].get('browsing', 0) > portrait['intent_profile']['purchase_stage'].get('deciding', 0):
            insights['marketing_strategy'].append("处于早期浏览阶段，需要教育性内容引导")
            insights['marketing_strategy'].append("重点展示产品功能和解决痛点的方式")
        elif portrait['intent_profile']['purchase_stage'].get('comparing', 0) > 0:
            insights['marketing_strategy'].append("处于对比阶段，需要突出产品差异化优势")
            insights['marketing_strategy'].append("提供详细的产品对比图表和用户评价")
        else:
            insights['marketing_strategy'].append("处于决策阶段，需要临门一脚的转化刺激")
            insights['marketing_strategy'].append("提供限时优惠、免费试用、快速配送等转化激励")
        
        # 产品推荐
        top_products = portrait['product_preferences'].most_common(3)
        if top_products:
            insights['product_recommendations'].append(f"最关注产品: {', '.join([f'{p[0]}({p[1]}次)' for p in top_products])}")
        
        # 转化优化
        if portrait['behavior_patterns']['quick_browsing'] > portrait['behavior_patterns']['deep_research']:
            insights['conversion_optimization'].append("用户浏览时间短，需要快速抓住注意力")
            insights['conversion_optimization'].append("优化首屏内容，突出核心卖点和优惠信息")
        else:
            insights['conversion_optimization'].append("用户深度研究，需要提供详细的产品信息")
            insights['conversion_optimization'].append("提供详细的产品说明、技术参数、使用视频等")
        
        # 价格策略
        if portrait['intent_profile']['concerns'].get('price', 0) > 0:
            insights['pricing_strategy'].append("价格敏感度高，需要突出性价比")
            insights['pricing_strategy'].append("提供分期付款、优惠券、限时折扣等价格策略")
        
        # 内容策略
        top_concerns = portrait['intent_profile']['concerns'].most_common(3)
        if top_concerns:
            concerns_list = [c[0] for c in top_concerns]
            insights['content_strategy'].append(f"主要关注点: {', '.join(concerns_list)}")
            insights['content_strategy'].append("针对这些关注点制作专门的内容和FAQ")
        
        # 时间策略
        if portrait['time_patterns']['peak_hours']:
            insights['content_strategy'].append(f"活跃时段: {', '.join([str(h) for h in portrait['time_patterns']['peak_hours']])} 点")
            insights['content_strategy'].append("在这些时段投放广告或推送营销内容")
        
        return insights
    
    def analyze_all_clusters(self):
        """分析所有聚类"""
        print("\n开始分析所有聚类的用户画像...")
        
        all_portraits = []
        all_insights = []
        
        # 获取所有聚类ID
        cluster_ids = sorted(self.df['kmeans_cluster'].unique())
        
        for cluster_id in cluster_ids:
            print(f"正在分析聚类 {cluster_id}...")
            portrait = self.analyze_cluster_portrait(cluster_id)
            if portrait:
                all_portraits.append(portrait)
                insights = self.generate_business_insights(portrait)
                all_insights.append(insights)
        
        return all_portraits, all_insights
    
    def save_results(self, portraits, insights):
        """保存分析结果"""
        # 保存详细画像
        portraits_file = 'user_portraits_detailed.json'
        with open(portraits_file, 'w', encoding='utf-8') as f:
            json.dump(portraits, f, indent=2, ensure_ascii=False, default=str)
        print(f"详细用户画像已保存到: {portraits_file}")
        
        # 保存业务洞察
        insights_file = 'business_insights.json'
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
        print(f"业务洞察已保存到: {insights_file}")
        
        # 生成可读性报告
        self.generate_readable_report(insights)
        
        # 生成CSV汇总
        self.generate_summary_csv(insights)
    
    def generate_readable_report(self, insights):
        """生成可读性报告"""
        report_file = 'user_portrait_report.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 用户画像分析报告\n\n")
            f.write("基于聚类结果的用户画像分析和业务指导建议\n\n")
            f.write("---\n\n")
            
            for insight in insights:
                f.write(f"## 聚类 {insight['cluster_id']}: {insight['user_segment_name']}\n\n")
                
                f.write("### 关键特征\n")
                for char in insight['key_characteristics']:
                    f.write(f"- {char}\n")
                f.write("\n")
                
                f.write("### 营销策略建议\n")
                for strategy in insight['marketing_strategy']:
                    f.write(f"- {strategy}\n")
                f.write("\n")
                
                f.write("### 产品推荐建议\n")
                for rec in insight['product_recommendations']:
                    f.write(f"- {rec}\n")
                if not insight['product_recommendations']:
                    f.write("- 需要进一步分析产品偏好\n")
                f.write("\n")
                
                f.write("### 转化优化建议\n")
                for opt in insight['conversion_optimization']:
                    f.write(f"- {opt}\n")
                f.write("\n")
                
                f.write("### 价格策略建议\n")
                for price in insight['pricing_strategy']:
                    f.write(f"- {price}\n")
                if not insight['pricing_strategy']:
                    f.write("- 价格敏感度较低，可重点强调产品价值\n")
                f.write("\n")
                
                f.write("### 内容策略建议\n")
                for content in insight['content_strategy']:
                    f.write(f"- {content}\n")
                f.write("\n")
                
                f.write("---\n\n")
        
        print(f"可读性报告已保存到: {report_file}")
    
    def generate_summary_csv(self, insights):
        """生成CSV汇总表"""
        summary_data = []
        for insight in insights:
            summary_data.append({
                '聚类ID': insight['cluster_id'],
                '用户细分': insight['user_segment_name'],
                '关键特征': '; '.join(insight['key_characteristics']),
                '营销策略': '; '.join(insight['marketing_strategy']),
                '产品推荐': '; '.join(insight['product_recommendations']) if insight['product_recommendations'] else '',
                '转化优化': '; '.join(insight['conversion_optimization']),
                '价格策略': '; '.join(insight['pricing_strategy']) if insight['pricing_strategy'] else '',
                '内容策略': '; '.join(insight['content_strategy'])
            })
        
        df = pd.DataFrame(summary_data)
        csv_file = 'business_insights_summary.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"CSV汇总表已保存到: {csv_file}")
    
    def run(self):
        """执行完整分析流程"""
        self.load_data()
        portraits, insights = self.analyze_all_clusters()
        self.save_results(portraits, insights)
        
        print("\n" + "="*80)
        print("用户画像分析完成！")
        print("="*80)
        print(f"\n共分析了 {len(insights)} 个聚类")
        print("\n生成的文件:")
        print("  - user_portraits_detailed.json: 详细用户画像数据")
        print("  - business_insights.json: 业务洞察数据")
        print("  - user_portrait_report.md: 可读性报告")
        print("  - business_insights_summary.csv: CSV汇总表")

if __name__ == '__main__':
    analyzer = UserPortraitAnalyzer('../cluster_results.json')
    analyzer.run()

