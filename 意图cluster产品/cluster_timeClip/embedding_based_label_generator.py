#!/usr/bin/env python3
"""
基于embedding聚类的标签生成器
从聚类的文本内容中提取更具体的特征，生成有区分度的标签
"""

import json
import pandas as pd
import re
from collections import Counter, defaultdict
from pathlib import Path


class EmbeddingBasedLabelGenerator:
    """基于embedding聚类的标签生成器"""
    
    def __init__(self):
        # 关注点关键词映射
        self.concern_keywords = {
            '功能导向': ['feature', 'function', 'technology', 'specification', 'capability', 'functionality', 
                      '功能', '特性', '技术', '规格', '能力'],
            '价格导向': ['price', 'cost', 'discount', 'affordable', 'budget', 'value', 'cheap', 'expensive',
                      '价格', '成本', '折扣', '实惠', '预算', '价值', '便宜', '昂贵'],
            '舒适度导向': ['comfort', 'comfortable', 'soft', 'material', 'texture', 'feel', 'quality',
                        '舒适', '柔软', '材质', '质感', '手感', '质量'],
            '有效性导向': ['effective', 'effectiveness', 'work', 'result', 'benefit', 'improve', 'help',
                        '有效', '效果', '作用', '结果', '好处', '改善', '帮助'],
            '外观导向': ['appearance', 'look', 'design', 'style', 'aesthetic', 'beautiful', 'realistic',
                       '外观', '设计', '风格', '美学', '美丽', '逼真'],
            '尺寸导向': ['size', 'dimension', 'measurement', 'inch', 'cm', 'large', 'small',
                       '尺寸', '大小', '英寸', '厘米', '大', '小'],
            '材质导向': ['material', 'silicone', 'platinum', 'fabric', 'texture', 'quality',
                        '材质', '硅胶', '铂金', '面料', '质感', '质量']
        }
        
        # 核心需求关键词映射
        self.need_keywords = {
            '收藏需求': ['collect', 'collection', 'collectible', 'collector', 'display', 'art',
                        '收藏', '收集', '收藏品', '展示', '艺术'],
            '礼物需求': ['gift', 'present', 'christmas', 'birthday', 'give', 'recipient',
                        '礼物', '礼品', '圣诞', '生日', '赠送', '收礼人'],
            '陪伴需求': ['companion', 'companionship', 'comfort', 'therapeutic', 'emotional', 'support',
                        '陪伴', '安慰', '治疗', '情感', '支持'],
            '游戏需求': ['play', 'toy', 'pretend', 'nurturing', 'interactive', 'fun',
                        '游戏', '玩具', '假装', '互动', '有趣'],
            '教育需求': ['education', 'learning', 'teaching', 'nursery', 'training', 'child',
                        '教育', '学习', '教学', '育儿', '训练', '儿童'],
            '装饰需求': ['decor', 'decoration', 'display', 'home', 'room', 'aesthetic',
                        '装饰', '摆设', '展示', '家居', '房间', '美学']
        }
        
        # 产品类型关键词映射
        self.product_keywords = {
            '婴儿娃娃': ['baby', 'infant', 'newborn', 'doll', 'reborn', 'realistic',
                       '婴儿', '新生儿', '娃娃', '重生', '逼真'],
            '硅胶娃娃': ['silicone', 'platinum silicone', 'full silicone', 'silicone body',
                        '硅胶', '铂金硅胶', '全硅胶', '硅胶身体'],
            '互动娃娃': ['interactive', 'heartbeat', 'breath', 'talking', 'sound', 'voice',
                        '互动', '心跳', '呼吸', '说话', '声音', '语音'],
            '配件': ['accessory', 'outfit', 'clothing', 'pacifier', 'bottle', 'diaper',
                    '配件', '服装', '衣服', '奶嘴', '奶瓶', '尿布']
        }
    
    def extract_text_from_segment(self, segment):
        """从segment中提取文本内容"""
        texts = []
        
        # 从output字段提取
        output = segment.get('output', '')
        if output:
            try:
                # 清理output字符串
                cleaned = output.strip()
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
                
                # 提取各种文本字段
                core_interests = intent.get('core_interests', [])
                if isinstance(core_interests, list):
                    texts.extend([str(x).lower() for x in core_interests])
                
                product_focus = intent.get('product_focus', {})
                key_attributes = product_focus.get('key_attributes', [])
                if isinstance(key_attributes, list):
                    texts.extend([str(x).lower() for x in key_attributes])
                
                main_appeal = product_focus.get('main_appeal', '')
                if main_appeal:
                    texts.append(str(main_appeal).lower())
                
                purchase_signals = intent.get('purchase_signals', {})
                concerns = purchase_signals.get('concerns', [])
                if isinstance(concerns, list):
                    texts.extend([str(x).lower() for x in concerns])
                elif isinstance(concerns, str):
                    texts.append(concerns.lower())
                
                behavior_summary = intent.get('behavior_summary', {})
                browsing_path = behavior_summary.get('browsing_path', '')
                if browsing_path:
                    texts.append(browsing_path.lower())
                
                match_analysis = intent.get('match_analysis', {})
                customer_portrait = match_analysis.get('customer_portrait', '')
                if customer_portrait:
                    texts.append(customer_portrait.lower())
                
            except Exception as e:
                pass
        
        # 从text字段提取
        text = segment.get('text', '')
        if text:
            texts.append(str(text).lower())
        
        return ' '.join(texts)
    
    def analyze_cluster_text(self, cluster_texts):
        """分析聚类的文本内容，提取特征"""
        # 合并所有文本
        all_text = ' '.join(cluster_texts)
        
        # 分析关注点
        concern_scores = {}
        for concern, keywords in self.concern_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                concern_scores[concern] = score
        
        # 分析核心需求
        need_scores = {}
        for need, keywords in self.need_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if need == '礼物需求':
                # 特别关注礼物相关
                gift_indicators = ['gift', 'christmas', 'birthday', 'present', '礼物', '圣诞', '生日']
                score += sum(2 for indicator in gift_indicators if indicator in all_text)
            if score > 0:
                need_scores[need] = score
        
        # 分析产品类型
        product_scores = {}
        for product, keywords in self.product_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                product_scores[product] = score
        
        # 提取关键词（最常见的词）
        words = re.findall(r'\b[a-z]{3,}\b', all_text)
        word_counts = Counter(words)
        top_keywords = [word for word, count in word_counts.most_common(10) 
                       if count >= len(cluster_texts) * 0.1]  # 至少在10%的文本中出现
        
        return {
            'concern_scores': concern_scores,
            'need_scores': need_scores,
            'product_scores': product_scores,
            'top_keywords': top_keywords[:5]  # 只取前5个
        }
    
    def generate_cluster_label(self, cluster_id, cluster_data, cluster_texts):
        """为单个聚类生成标签"""
        # 分析文本
        analysis = self.analyze_cluster_text(cluster_texts)
        
        # 计算数值特征的平均值
        avg_stage = cluster_data['purchase_stage'].mean() if 'purchase_stage' in cluster_data.columns else 0
        avg_price = cluster_data['price_sensitivity'].mean() if 'price_sensitivity' in cluster_data.columns else 2
        avg_engagement = cluster_data['engagement_level'].mean() if 'engagement_level' in cluster_data.columns else 0
        
        # 确定参与度标签
        if avg_engagement >= 1.5:
            engagement_label = "深度研究"
        elif avg_engagement >= 0.5:
            engagement_label = "中等参与"
        else:
            engagement_label = "快速浏览"
        
        # 确定购买阶段标签
        if avg_stage >= 1.5:
            stage_label = "决策阶段"
        elif avg_stage >= 0.5:
            stage_label = "对比阶段"
        else:
            stage_label = "浏览阶段"
        
        # 确定价格敏感度标签
        if avg_price <= 0.5:
            price_label = "价格敏感"
        elif avg_price <= 1.5:
            price_label = "中等价格"
        else:
            price_label = "高端价值"
        
        # 从文本分析中提取关注点
        concern_scores = analysis['concern_scores']
        if concern_scores:
            top_concern = max(concern_scores.items(), key=lambda x: x[1])[0]
        else:
            top_concern = "综合关注"
        
        # 从文本分析中提取核心需求
        need_scores = analysis['need_scores']
        if need_scores:
            top_need = max(need_scores.items(), key=lambda x: x[1])[0]
        else:
            top_need = "综合需求"
        
        # 从文本分析中提取产品偏好
        product_scores = analysis['product_scores']
        if product_scores:
            top_product = max(product_scores.items(), key=lambda x: x[1])[0]
        else:
            top_product = "多产品比较"
        
        # 生成简短标签（优先使用文本分析的结果）
        # 格式：参与度·关注点/需求
        if top_concern != "综合关注":
            short_label = f"{engagement_label}·{top_concern}"
        elif top_need != "综合需求":
            short_label = f"{engagement_label}·{top_need}"
        else:
            short_label = f"{engagement_label}·{stage_label}"
        
        # 生成完整标签
        label_parts = [engagement_label]
        if top_concern != "综合关注":
            label_parts.append(top_concern)
        if top_need != "综合需求":
            label_parts.append(top_need)
        elif top_product != "多产品比较":
            label_parts.append(top_product)
        
        full_label = "·".join(label_parts)
        
        # 生成特征字典
        characteristics = {
            'stage': stage_label,
            'price': price_label,
            'engagement': engagement_label,
            'product': top_product,
            'concern': top_concern,
            'need': top_need
        }
        
        # 添加文本分析结果
        characteristics['top_keywords'] = analysis['top_keywords']
        characteristics['text_analysis'] = {
            'concern_scores': concern_scores,
            'need_scores': need_scores,
            'product_scores': product_scores
        }
        
        return {
            'short_label': short_label,
            'full_label': full_label,
            'characteristics': characteristics,
            'avg_features': {
                'purchase_stage': float(avg_stage),
                'price_sensitivity': float(avg_price),
                'engagement_level': float(avg_engagement),
                'product_preference': cluster_data['product_preference'].mode()[0] if 'product_preference' in cluster_data.columns and len(cluster_data['product_preference'].mode()) > 0 else 5,
                'concern_focus': cluster_data['concern_focus'].mode()[0] if 'concern_focus' in cluster_data.columns and len(cluster_data['concern_focus'].mode()) > 0 else 4,
                'core_need': cluster_data['core_need'].mode()[0] if 'core_need' in cluster_data.columns and len(cluster_data['core_need'].mode()) > 0 else 3
            }
        }
    
    def generate_labels_for_clusters(self, df, cluster_labels, extracted_data=None):
        """为所有聚类生成标签"""
        cluster_labels_dict = {}
        
        # 获取所有唯一的聚类ID
        unique_cluster_ids = sorted([int(x) for x in df['business_cluster'].unique()])
        
        # 如果有原始数据，用于提取文本
        text_map = {}
        if extracted_data:
            for record in extracted_data:
                user_id = record.get('user_id', '')
                output = record.get('output', '')
                if user_id and output:
                    if user_id not in text_map:
                        text_map[user_id] = []
                    text_map[user_id].append(output)
        
        for cluster_id in unique_cluster_ids:
            cluster_data = df[df['business_cluster'] == cluster_id]
            
            # 收集该聚类的所有文本
            cluster_texts = []
            
            # 从segments中提取文本
            for idx, row in cluster_data.iterrows():
                segment_text = self.extract_text_from_segment(row.to_dict())
                if segment_text:
                    cluster_texts.append(segment_text)
            
            # 如果文本太少，尝试从原始数据中补充
            if len(cluster_texts) < len(cluster_data) * 0.5 and extracted_data:
                user_ids = cluster_data['user_id'].unique()
                for user_id in user_ids:
                    if user_id in text_map:
                        cluster_texts.extend(text_map[user_id])
            
            # 生成标签
            label_info = self.generate_cluster_label(cluster_id, cluster_data, cluster_texts)
            cluster_labels_dict[int(cluster_id)] = label_info
        
        return cluster_labels_dict

