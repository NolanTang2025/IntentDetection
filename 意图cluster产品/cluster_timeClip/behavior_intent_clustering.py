#!/usr/bin/env python3
"""
基于用户行为意图的聚类分析
目标：让商家可以快速捕捉到当下的用户意图并给出相应的反应
结合行为特征（交互次数、时长、意图强度）和意图特征（购买阶段、产品偏好等）

核心改进：基于意图变化的分段策略
- 当用户意图真正发生变化时才进行意图切片
- 一个用户可以拥有多个意图片段（不同时间段可能有不同意图）
- 不再机械地按固定时间间隔分段，而是智能识别意图变化

店铺39特殊处理：使用Gemini API进行文本embedding聚类
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from pathlib import Path
import os
import time

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    # 加载.env文件（从项目根目录）
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✅ 已加载.env文件: {env_path}")
    else:
        # 也尝试从当前目录加载
        load_dotenv(override=True)
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    # 如果没有安装python-dotenv，仍然可以从环境变量读取
    print("⚠️  python-dotenv 未安装，将仅从环境变量读取API密钥")

# 尝试导入Gemini API（店铺39使用）
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google.generativeai 未安装，店铺39将使用默认方法。安装: pip install google-generativeai")

class BehaviorIntentClusterer:
    def __init__(self, 
                 gap_threshold_minutes=10,
                 inactivity_threshold_minutes=15,
                 intent_change_threshold=0.3,
                 gemini_api_key=None):
        """
        参数:
            gap_threshold_minutes: 时间间隔阈值（分钟），超过此值即使意图没变也可能分段
            inactivity_threshold_minutes: 不活跃阈值（分钟），超过此值强制分段
            intent_change_threshold: 意图变化阈值 (0-1)，超过此值认为意图发生变化
            gemini_api_key: Gemini API密钥（用于店铺39的embedding）
        """
        self.gap_threshold = timedelta(minutes=gap_threshold_minutes)
        self.inactivity_threshold = timedelta(minutes=inactivity_threshold_minutes)
        self.intent_change_threshold = intent_change_threshold
        
        # 加载API密钥（优先级：参数 > 环境变量 > .env文件）
        if gemini_api_key:
            self.gemini_api_key = gemini_api_key
            print(f"✅ 使用传入的Gemini API密钥")
        else:
            # 尝试从环境变量读取（包括从.env文件加载的）
            self.gemini_api_key = os.getenv('GEMINI_API_KEY')
            if self.gemini_api_key:
                print(f"✅ 从环境变量读取Gemini API密钥")
            else:
                print("⚠️  未找到Gemini API密钥，店铺39将使用默认方法")
        
        # 如果提供了API密钥，配置Gemini
        if self.gemini_api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.gemini_api_key)
            print(f"✅ Gemini API已配置")
        elif self.gemini_api_key and not GEMINI_AVAILABLE:
            print("⚠️  已提供API密钥但google-generativeai未安装，请运行: pip install google-generativeai")
    
    def parse_timestamp(self, ts_str):
        """解析时间戳字符串"""
        try:
            return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        except:
            return datetime.fromisoformat(ts_str)
    
    def extract_business_features(self, output_str, duration_minutes, record_count):
        """从output中提取业务特征（支持多种数据格式，包括Markdown+JSON混合格式）"""
        try:
            import re
            
            cleaned = output_str.strip()
            
            # 方法0: 先尝试解析外层JSON（处理转义字符）
            try:
                # 尝试去除最外层的引号，如果存在
                if cleaned.startswith('"') and cleaned.endswith('"'):
                    temp_cleaned = cleaned[1:-1]
                    # 尝试解析一次，看是否是转义的JSON字符串
                    parsed_outer = json.loads(temp_cleaned)
                    if isinstance(parsed_outer, str):
                        cleaned = parsed_outer.strip()
                    else: # 如果解析出来不是字符串，说明外层引号是JSON的一部分，恢复
                        cleaned = temp_cleaned
                else:
                    # 如果没有外层引号，直接使用
                    pass
            except Exception as e:
                # 如果解析失败，说明不是转义的JSON字符串，直接移除外层引号
                if cleaned.startswith('"'):
                    cleaned = cleaned[1:]
                if cleaned.endswith('"'):
                    cleaned = cleaned[:-1]
                cleaned = cleaned.strip()
            
            data = None
            intent = {}
            
            # 方法1: 尝试提取```json代码块中的内容（最常见格式）
            json_start = cleaned.find('```json')
            if json_start >= 0:
                content_start = json_start + 7
                # 查找所有{位置（从content_start开始）
                brace_positions = [i for i, char in enumerate(cleaned) if char == '{' and i >= content_start]
                
                # 从后往前查找包含"intent"的JSON对象
                for brace_start in reversed(brace_positions):
                    brace_count = 0
                    brace_end = -1
                    for i in range(brace_start, len(cleaned)):
                        if cleaned[i] == '{':
                            brace_count += 1
                        elif cleaned[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                brace_end = i + 1
                                break
                    
                    if brace_end > brace_start:
                        json_str = cleaned[brace_start:brace_end]
                        # 尝试修复不完整的JSON
                        try:
                            data = json.loads(json_str)
                            if 'intent' in data:
                                intent = data.get('intent', {})
                                json_match = True
                                break
                        except json.JSONDecodeError as e:
                            # 尝试修复不完整的JSON
                            try:
                                # 尝试添加缺失的闭合括号
                                fixed_json_str = json_str
                                open_braces = fixed_json_str.count('{')
                                close_braces = fixed_json_str.count('}')
                                if open_braces > close_braces:
                                    fixed_json_str += '}' * (open_braces - close_braces)
                                data = json.loads(fixed_json_str)
                                if 'intent' in data:
                                    intent = data.get('intent', {})
                                    json_match = True
                                    break
                            except:
                                continue
                
                if 'json_match' not in locals():
                    json_match = None
            else:
                json_match = None
            
            # 如果方法1失败，继续使用方法2 (直接解析整个字符串，或查找最后一个JSON)
            if not json_match or not intent:
                # 移除代码块标记
                temp_cleaned = cleaned
                if temp_cleaned.startswith('```json'):
                    temp_cleaned = temp_cleaned[7:]
                if temp_cleaned.endswith('```'):
                    temp_cleaned = temp_cleaned[:-3]
                temp_cleaned = temp_cleaned.strip()
                
                try:
                    data = json.loads(temp_cleaned)
                    intent = data.get('intent', {})
                except:
                    # 方法3: 如果还是失败，尝试查找最后一个完整的JSON对象
                    # 查找最后一个{...}结构（从末尾开始）
                    brace_start = temp_cleaned.rfind('{')
                    if brace_start != -1:
                        # 尝试找到匹配的闭合括号
                        brace_count = 0
                        brace_end = -1
                        for i in range(brace_start, len(temp_cleaned)):
                            if temp_cleaned[i] == '{':
                                brace_count += 1
                            elif temp_cleaned[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    brace_end = i + 1
                                    break
                        
                        if brace_end > brace_start:
                            json_str = temp_cleaned[brace_start:brace_end]
                            try:
                                data = json.loads(json_str)
                                intent = data.get('intent', {})
                            except:
                                # 尝试修复不完整的JSON
                                try:
                                    fixed_json_str = json_str
                                    open_braces = fixed_json_str.count('{')
                                    close_braces = fixed_json_str.count('}')
                                    if open_braces > close_braces:
                                        fixed_json_str += '}' * (open_braces - close_braces)
                                    data = json.loads(fixed_json_str)
                                    intent = data.get('intent', {})
                                except:
                                    data = {'intent_score': 0.5}
                                    intent = {}
                        else: # 如果没有找到匹配的闭合括号，尝试从brace_start到末尾
                            json_str = temp_cleaned[brace_start:]
                            try:
                                # 尝试修复不完整的JSON
                                fixed_json_str = json_str
                                open_braces = fixed_json_str.count('{')
                                close_braces = fixed_json_str.count('}')
                                if open_braces > close_braces:
                                    fixed_json_str += '}' * (open_braces - close_braces)
                                data = json.loads(fixed_json_str)
                                intent = data.get('intent', {})
                            except:
                                data = {'intent_score': 0.5}
                                intent = {}
                    else:
                        data = {'intent_score': 0.5}
                        intent = {}
            
            # 如果data还是None，创建默认结构
            if data is None:
                data = {'intent_score': 0.5}
            
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
            
            # 处理组合阶段，例如 "browsing/comparing"
            stage_lower = str(stage).lower()
            if 'deciding' in stage_lower:
                features['purchase_stage'] = 2
            elif 'comparing' in stage_lower:
                features['purchase_stage'] = 1
            else:
                features['purchase_stage'] = 0
            
            # 价格敏感度
            product_focus = intent.get('product_focus', {})
            price_range = product_focus.get('price_range', 'premium')
            price_lower = str(price_range).lower()
            if 'budget' in price_lower or 'economy' in price_lower or 'low' in price_lower:
                features['price_sensitivity'] = 0
            elif 'mid' in price_lower or 'medium' in price_lower:
                features['price_sensitivity'] = 1
            else:
                features['price_sensitivity'] = 2
            
            # 产品偏好（从core_interests和product_focus中提取）
            core_interests = intent.get('core_interests', [])
            key_attributes = product_focus.get('key_attributes', [])
            all_product_terms = []
            if isinstance(core_interests, list):
                all_product_terms.extend([str(x).lower() for x in core_interests])
            if isinstance(key_attributes, list):
                all_product_terms.extend([str(x).lower() for x in key_attributes])
            
            # 产品映射
            product_map = {
                'z6': 0, 'a1': 1, 'f1': 2, 'h02': 3, 'h2': 3, 'g1': 4
            }
            features['product_preference'] = 5  # 默认：无偏好
            for term in all_product_terms:
                for product_key, product_id in product_map.items():
                    if product_key in term:
                        features['product_preference'] = product_id
                        break
                if features['product_preference'] != 5:
                    break
            
            # 关注点（从concerns中提取）
            concerns = purchase_signals.get('concerns', [])
            if concerns and isinstance(concerns, list) and len(concerns) > 0:
                concern_str = ' '.join([str(x).lower() for x in concerns if x])
                if 'price' in concern_str or 'cost' in concern_str:
                    features['concern_focus'] = 0
                elif 'quality' in concern_str or 'durability' in concern_str:
                    features['concern_focus'] = 1
                elif 'comfort' in concern_str or 'comfortable' in concern_str:
                    features['concern_focus'] = 2
                elif 'effectiveness' in concern_str or 'effect' in concern_str:
                    features['concern_focus'] = 3
                else:
                    features['concern_focus'] = 4
            else:
                features['concern_focus'] = 4
            
            # 核心需求（从core_interests和main_appeal中提取）
            main_appeal = product_focus.get('main_appeal', '')
            all_need_terms = ' '.join([str(x).lower() for x in core_interests if x]) + ' ' + str(main_appeal).lower()
            if 'snoring' in all_need_terms or 'snore' in all_need_terms:
                features['core_need'] = 0
            elif 'neck' in all_need_terms or 'pain' in all_need_terms:
                features['core_need'] = 1
            elif 'sleep' in all_need_terms and 'quality' in all_need_terms:
                features['core_need'] = 2
            else:
                features['core_need'] = 3
            
            return features
            
        except Exception as e:
            # print(f"特征提取失败: {e}, output_str: {output_str[:500]}")
            return {
                'purchase_stage': 0,
                'price_sensitivity': 2,
                'product_preference': 5,
                'concern_focus': 4,
                'core_need': 3,
                'intent_score': 0.5
            }
    
    def extract_financial_features(self, segment_records, all_user_records=None):
        """从片段记录中提取金融相关特征（专门用于YUP等金融公司）
        
        参数:
            segment_records: 当前片段的记录列表
            all_user_records: 该用户的所有记录（用于计算用户级别特征，如首次交易时间）
        """
        if not segment_records:
            return {
                'kyc_started': 0,
                'kyc_event_count': 0,
                'has_transaction': 0,
                'transaction_completed': 0,
                'first_order_completed': 0,  # 新增：用户是否已完成首笔订单
                'post_first_order': 0,  # 新增：当前片段是否在首笔订单之后
                'event_count': 0,
                'payment_related_events': 0,
                'recharge_related_events': 0,
                'voucher_related_events': 0,
                'intent_score': 0.5
            }
        
        # 提取事件名称列表
        event_names = [r.get('event_name', '') for r in segment_records if r.get('event_name')]
        
        # 特征1: 是否开始KYC（包含人脸识别相关事件）
        kyc_started = 1 if any('face' in str(e).lower() or 'verification' in str(e).lower() or 'kyc' in str(e).lower() 
                               for e in event_names) else 0
        
        # 特征2: KYC相关事件数量
        kyc_events = [e for e in event_names if any(keyword in str(e).lower() 
                   for keyword in ['face', 'verification', 'kyc', 'ocr', 'activate'])]
        kyc_event_count = len(kyc_events)
        
        # 特征3: 是否完成交易
        has_transaction = 1 if any(r.get('has_transaction', False) for r in segment_records) else 0
        
        # 特征4: 交易状态（从output中提取）
        transaction_completed = 0
        intent_score = 0.5
        for record in reversed(segment_records):  # 从后往前查找最新的状态
            output = record.get('output', '')
            if output:
                try:
                    # 尝试解析output中的JSON
                    cleaned = output.strip()
                    if cleaned.startswith('"'):
                        cleaned = cleaned[1:-1]
                    if '```json' in cleaned:
                        json_start = cleaned.find('{')
                        if json_start >= 0:
                            json_str = cleaned[json_start:]
                            brace_count = 0
                            json_end = -1
                            for i, char in enumerate(json_str):
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        json_end = i + 1
                                        break
                            if json_end > 0:
                                data = json.loads(json_str[:json_end])
                                intent = data.get('intent', {})
                                purchase_signals = intent.get('purchase_signals', {})
                                stage = str(purchase_signals.get('stage', '')).lower()
                                if 'completed' in stage:
                                    transaction_completed = 1
                                intent_score = data.get('intent_score', 0.5)
                                break
                except:
                    continue
        
        # 特征5: 用户级别的首笔订单完成状态（基于所有用户记录）
        first_order_completed = 0
        post_first_order = 0
        if all_user_records:
            # 检查用户是否在任何记录中完成了首笔订单
            user_first_order_completed = False
            first_order_timestamp = None
            
            # 按时间排序所有记录
            sorted_user_records = sorted(all_user_records, key=lambda x: self.parse_timestamp(x.get('timestamp', '')))
            
            # 查找首笔订单完成的时间点（查找第一次出现completed状态）
            for record in sorted_user_records:
                output = record.get('output', '')
                if output:
                    try:
                        cleaned = output.strip()
                        if cleaned.startswith('"'):
                            cleaned = cleaned[1:-1]
                        # 移除转义字符
                        cleaned = cleaned.replace('\\n', '\n').replace('\\"', '"')
                        
                        # 尝试多种方式解析JSON
                        json_start = cleaned.find('{')
                        if json_start >= 0:
                            json_str = cleaned[json_start:]
                            brace_count = 0
                            json_end = -1
                            for i, char in enumerate(json_str):
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        json_end = i + 1
                                        break
                            
                            if json_end > 0:
                                try:
                                    data = json.loads(json_str[:json_end])
                                    intent = data.get('intent', {})
                                    purchase_signals = intent.get('purchase_signals', {})
                                    stage = str(purchase_signals.get('stage', '')).lower()
                                    transaction_status = str(purchase_signals.get('transaction_status', '')).lower()
                                    
                                    # 检查是否完成首笔订单（stage或transaction_status为completed）
                                    # 注意：需要确保这是第一次出现completed，而不是所有记录都是completed
                                    if ('completed' in stage or 'completed' in transaction_status):
                                        # 检查是否有实际的交易事件（如支付、提交订单等）
                                        event_name = record.get('event_name', '').lower()
                                        has_payment_event = any(keyword in event_name for keyword in ['pay', 'checkout', 'submit', 'recharge'])
                                        
                                        if has_payment_event or 'completed' in transaction_status:
                                            if not user_first_order_completed:
                                                user_first_order_completed = True
                                                first_order_timestamp = record.get('timestamp')
                                                break
                                except json.JSONDecodeError:
                                    # 如果JSON解析失败，尝试字符串匹配
                                    if '"transaction_status": "completed"' in cleaned or '"transaction_status":"completed"' in cleaned:
                                        event_name = record.get('event_name', '').lower()
                                        has_payment_event = any(keyword in event_name for keyword in ['pay', 'checkout', 'submit', 'recharge'])
                                        if has_payment_event:
                                            if not user_first_order_completed:
                                                user_first_order_completed = True
                                                first_order_timestamp = record.get('timestamp')
                                                break
                    except Exception as e:
                        continue
            
            # 如果用户已完成首笔订单
            if user_first_order_completed:
                first_order_completed = 1
                
                # 检查当前片段是否在首笔订单之后
                segment_start = segment_records[0].get('timestamp')
                if first_order_timestamp and segment_start:
                    try:
                        first_order_time = self.parse_timestamp(first_order_timestamp)
                        segment_start_time = self.parse_timestamp(segment_start)
                        if segment_start_time >= first_order_time:
                            post_first_order = 1
                    except:
                        pass
        
        # 特征5: 事件总数
        event_count = len(event_names)
        
        # 特征6: 支付相关事件数量
        payment_events = [e for e in event_names if any(keyword in str(e).lower() 
                       for keyword in ['pay', 'checkout', 'payment', 'qr', 'qris'])]
        payment_related_events = len(payment_events)
        
        # 特征7: 充值相关事件数量
        recharge_events = [e for e in event_names if any(keyword in str(e).lower() 
                        for keyword in ['recharge', 'topup', 'top_up', 'phone', 'electricity'])]
        recharge_related_events = len(recharge_events)
        
        # 特征8: 优惠券相关事件数量
        voucher_events = [e for e in event_names if 'voucher' in str(e).lower()]
        voucher_related_events = len(voucher_events)
        
        # ========== 新增：更细致的业务特征 ==========
        
        # 特征9: 功能探索深度（使用功能的多样性）
        unique_events = len(set(event_names))
        feature_diversity = unique_events / max(event_count, 1)  # 功能多样性比率
        
        # 特征10: 激活相关事件（账户激活、额度激活等）
        activation_events = [e for e in event_names if any(keyword in str(e).lower() 
                          for keyword in ['activate', 'activation', 'success', 'binding'])]
        activation_related_events = len(activation_events)
        
        # 特征11: 主页/导航相关事件（用户浏览深度）
        navigation_events = [e for e in event_names if any(keyword in str(e).lower() 
                          for keyword in ['home', 'nav', 'page', 'show_'])]
        navigation_related_events = len(navigation_events)
        
        # 特征12: 点击行为相关事件（用户交互活跃度）
        click_events = [e for e in event_names if 'click' in str(e).lower()]
        click_related_events = len(click_events)
        
        # 特征13: 用户中心/个人中心相关事件（用户管理行为）
        profile_events = [e for e in event_names if any(keyword in str(e).lower() 
                       for keyword in ['profile', 'profil', 'mgm', 'account', 'user'])]
        profile_related_events = len(profile_events)
        
        # 特征14: 任务/活动相关事件（用户参与度）
        task_events = [e for e in event_names if any(keyword in str(e).lower() 
                   for keyword in ['task', 'activity', 'zone', 'banner', 'campaign'])]
        task_related_events = len(task_events)
        
        # 特征15: 交互深度（点击事件与展示事件的比率）
        show_events = [e for e in event_names if 'show_' in str(e).lower()]
        show_related_events = len(show_events)
        interaction_depth = click_related_events / max(show_related_events, 1)  # 交互深度
        
        # 特征16: 业务场景类型（基于事件组合判断）
        # 0=激活阶段, 1=KYC阶段, 2=探索阶段, 3=支付阶段, 4=充值阶段, 5=优惠券阶段, 6=复购阶段, 7=综合
        business_scenario = 7  # 默认综合
        if activation_related_events > 0 and kyc_started == 0:
            business_scenario = 0  # 激活阶段
        elif kyc_started > 0 and payment_related_events == 0:
            business_scenario = 1  # KYC阶段
        elif payment_related_events > recharge_related_events and payment_related_events > voucher_related_events:
            business_scenario = 3  # 支付阶段
        elif recharge_related_events > payment_related_events and recharge_related_events > voucher_related_events:
            business_scenario = 4  # 充值阶段
        elif voucher_related_events > 3:
            business_scenario = 5  # 优惠券阶段
        elif post_first_order > 0:
            business_scenario = 6  # 复购阶段
        elif event_count > 10 and unique_events > 5:
            business_scenario = 2  # 探索阶段
        
        # 特征17: 行为集中度（主要活动类型的集中程度）
        activity_counts = {
            'payment': payment_related_events,
            'recharge': recharge_related_events,
            'voucher': voucher_related_events,
            'navigation': navigation_related_events,
            'task': task_related_events
        }
        max_activity = max(activity_counts.values()) if activity_counts.values() else 0
        total_activities = sum(activity_counts.values())
        activity_concentration = max_activity / max(total_activities, 1)  # 行为集中度
        
        # 特征18: 时间活跃度（基于片段时长和事件数的综合活跃度）
        if segment_records:
            first_time = self.parse_timestamp(segment_records[0].get('timestamp', ''))
            last_time = self.parse_timestamp(segment_records[-1].get('timestamp', ''))
            time_span_minutes = (last_time - first_time).total_seconds() / 60
            time_span_minutes = max(time_span_minutes, 0.001)  # 避免除零
            activity_intensity = event_count / time_span_minutes  # 每分钟事件数
        else:
            activity_intensity = 0
        
        return {
            'kyc_started': kyc_started,
            'kyc_event_count': kyc_event_count,
            'has_transaction': has_transaction,
            'transaction_completed': transaction_completed,
            'first_order_completed': first_order_completed,
            'post_first_order': post_first_order,
            'event_count': event_count,
            'payment_related_events': payment_related_events,
            'recharge_related_events': recharge_related_events,
            'voucher_related_events': voucher_related_events,
            'intent_score': intent_score,
            # 新增特征
            'feature_diversity': feature_diversity,  # 功能多样性
            'activation_related_events': activation_related_events,  # 激活相关事件
            'navigation_related_events': navigation_related_events,  # 导航相关事件
            'click_related_events': click_related_events,  # 点击相关事件
            'profile_related_events': profile_related_events,  # 个人中心相关事件
            'task_related_events': task_related_events,  # 任务/活动相关事件
            'interaction_depth': interaction_depth,  # 交互深度
            'business_scenario': business_scenario,  # 业务场景类型
            'activity_concentration': activity_concentration,  # 行为集中度
            'activity_intensity': activity_intensity  # 时间活跃度
            }
    
    def extract_intent_features_from_record(self, record):
        """从单个行为记录中提取意图特征（用于意图变化检测）"""
        output = record.get('output', '')
        if not output:
            return None
        
        # 使用extract_business_features提取特征
        features = self.extract_business_features(output, 0, 1)
        return features
    
    def calculate_intent_change(self, prev_features, curr_features):
        """计算意图变化程度（0-1）"""
        if prev_features is None or curr_features is None:
            return 1.0
        
        # 计算各特征的变化
        changes = []
        
        # 购买阶段变化（权重高）
        stage_change = abs(prev_features.get('purchase_stage', 0) - curr_features.get('purchase_stage', 0)) / 2.0
        changes.append(stage_change * 0.3)
        
        # 产品偏好变化（权重高）
        product_change = abs(prev_features.get('product_preference', 5) - curr_features.get('product_preference', 5)) / 5.0
        changes.append(product_change * 0.3)
        
        # 价格敏感度变化
        price_change = abs(prev_features.get('price_sensitivity', 2) - curr_features.get('price_sensitivity', 2)) / 2.0
        changes.append(price_change * 0.15)
        
        # 关注点变化
        concern_change = abs(prev_features.get('concern_focus', 4) - curr_features.get('concern_focus', 4)) / 4.0
        changes.append(concern_change * 0.15)
        
        # 核心需求变化
        need_change = abs(prev_features.get('core_need', 3) - curr_features.get('core_need', 3)) / 3.0
        changes.append(need_change * 0.1)
        
        # 返回加权平均变化度
        return sum(changes)
    
    def extract_text_from_output(self, output_str):
        """从output字段中提取文本内容（用于embedding）"""
        try:
            import re
            
            cleaned = output_str.strip()
            # 移除外层引号
            if cleaned.startswith('"') and cleaned.endswith('"'):
                cleaned = cleaned[1:-1]
            # 移除代码块标记
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # 尝试解析JSON
            try:
                json_start = cleaned.find('{')
                if json_start >= 0:
                    json_str = cleaned[json_start:]
                    brace_count = 0
                    json_end = -1
                    for i, char in enumerate(json_str):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i + 1
                                break
                    
                    if json_end > 0:
                        json_str = json_str[:json_end]
                        data = json.loads(json_str)
                        intent = data.get('intent', {})
                        
                        # 提取文本内容
                        text_parts = []
                        
                        # core_interests
                        if 'core_interests' in intent:
                            interests = intent['core_interests']
                            if isinstance(interests, list):
                                text_parts.extend([str(x) for x in interests if x])
                        
                        # product_focus
                        if 'product_focus' in intent:
                            pf = intent['product_focus']
                            if isinstance(pf, dict):
                                if 'key_attributes' in pf:
                                    attrs = pf['key_attributes']
                                    if isinstance(attrs, list):
                                        text_parts.extend([str(x) for x in attrs if x])
                                if 'main_appeal' in pf and pf['main_appeal']:
                                    text_parts.append(str(pf['main_appeal']))
                        
                        # purchase_signals
                        if 'purchase_signals' in intent:
                            ps = intent['purchase_signals']
                            if isinstance(ps, dict):
                                if 'concerns' in ps and ps['concerns']:
                                    concerns = ps['concerns']
                                    if isinstance(concerns, list):
                                        text_parts.extend([str(x) for x in concerns if x])
                        
                        return ' '.join(text_parts)
            except:
                pass
            
            # 如果JSON解析失败，返回清理后的原始文本
            return cleaned[:500]  # 限制长度
            
        except Exception as e:
            return ""
    
    def get_gemini_embedding(self, text, task_type="CLUSTERING"):
        """使用Gemini API获取文本embedding"""
        if not GEMINI_AVAILABLE or not self.gemini_api_key:
            raise ValueError("Gemini API不可用，请安装google-generativeai并设置API密钥")
        
        try:
            # 使用Gemini embedding模型
            # 注意：task_type参数用于指定任务类型（CLUSTERING）
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type=task_type
            )
            embedding = result['embedding']
            print(f"    ✓ 生成embedding，维度: {len(embedding)}")
            return embedding
        except Exception as e:
            print(f"⚠️  Gemini embedding失败: {e}")
            # 如果失败，返回None，让调用者处理
            raise
    
    def cluster_by_gemini_embedding(self, segment_metadata, shop_id=39, input_file=None):
        """使用Gemini embedding进行聚类（仅用于店铺39）"""
        if not GEMINI_AVAILABLE or not self.gemini_api_key:
            print("⚠️  Gemini API不可用，店铺39将使用默认数值特征聚类")
            return self.cluster_by_behavior_intent(segment_metadata)
        
        print(f"  使用Gemini API进行文本embedding聚类（店铺{shop_id}）...")
        df = pd.DataFrame(segment_metadata)
        
        # 从原始数据中提取文本
        print("  正在从原始数据提取文本...")
        # 优先使用传入的input_file，否则尝试相对路径
        if input_file is None:
            # 尝试多个可能的路径
            possible_paths = [
                Path(f'../data_extract/extracted_data_shop_{shop_id}.json'),
                Path(f'data_extract/extracted_data_shop_{shop_id}.json'),
                Path(f'../意图cluster产品/data_extract/extracted_data_shop_{shop_id}.json'),
            ]
            input_file = None
            for path in possible_paths:
                if path.exists():
                    input_file = path
                    break
        
        if input_file is None or not Path(input_file).exists():
            print(f"  ⚠️  原始数据文件不存在，使用默认方法")
            return self.cluster_by_behavior_intent(segment_metadata)
        
        input_file = Path(input_file)
        
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # 创建user_id和timestamp到output的映射
        output_map = {}
        for record in raw_data:
            user_id = record.get('user_id')
            timestamp = record.get('timestamp')
            output = record.get('output', '')
            if user_id and timestamp and output:
                key = (user_id, timestamp)
                output_map[key] = output
        
        # 为每个segment提取文本并生成embedding
        print("  正在生成embedding向量...")
        embeddings = []
        valid_indices = []
        
        # 按user_id分组output，提高查找效率
        user_outputs = defaultdict(list)
        for record in raw_data:
            user_id = record.get('user_id')
            output = record.get('output', '')
            if user_id and output:
                user_outputs[user_id].append({
                    'timestamp': record.get('timestamp'),
                    'output': output
                })
        
        for idx, seg in enumerate(segment_metadata):
            user_id = seg.get('user_id')
            start_time = seg.get('start_time')
            end_time = seg.get('end_time')
            
            # 从该用户的所有output中查找匹配的
            text = ""
            if user_id in user_outputs:
                for record in user_outputs[user_id]:
                    ts = record['timestamp']
                    if start_time <= ts <= end_time:
                        extracted_text = self.extract_text_from_output(record['output'])
                        if extracted_text and len(extracted_text) > 10:
                            text = extracted_text
                            break
                
                # 如果时间范围内没找到，使用该用户最近的output
                if not text and user_outputs[user_id]:
                    # 按时间排序，取最接近end_time的
                    sorted_outputs = sorted(user_outputs[user_id], 
                                           key=lambda x: abs((self.parse_timestamp(x['timestamp']) - 
                                                             self.parse_timestamp(end_time)).total_seconds()))
                    for record in sorted_outputs[:3]:  # 尝试前3个最接近的
                        extracted_text = self.extract_text_from_output(record['output'])
                        if extracted_text and len(extracted_text) > 10:
                            text = extracted_text
                            break
            
            if text:
                try:
                    embedding = self.get_gemini_embedding(text, task_type="CLUSTERING")
                    embeddings.append(embedding)
                    valid_indices.append(idx)
                    if (idx + 1) % 50 == 0:
                        print(f"    已处理 {idx + 1}/{len(segment_metadata)} 个片段...")
                        time.sleep(0.1)  # 避免API限流
                except Exception as e:
                    print(f"    ⚠️  片段 {idx} embedding失败: {e}")
                    # 使用默认特征
                    valid_indices.append(idx)
                    # 创建一个零向量作为占位符（embedding-001的维度是768）
                    embeddings.append([0.0] * 768)
            else:
                # 如果没有文本，使用默认特征
                valid_indices.append(idx)
                embeddings.append([0.0] * 768)
        
        if len(embeddings) == 0:
            print("  ⚠️  没有生成任何embedding，使用默认方法")
            return self.cluster_by_behavior_intent(segment_metadata)
        
        print(f"  成功生成 {len(embeddings)} 个embedding向量")
        print(f"  Embedding维度: {len(embeddings[0])}")
        
        # 转换为numpy数组
        X_embeddings = np.array(embeddings)
        
        # 标准化embedding向量
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_embeddings)
        
        # 使用KMeans聚类
        n_samples = len(X_scaled)
        max_clusters = 100
        min_clusters = 3
        calculated_clusters = max(min_clusters, n_samples // 20)
        n_clusters = min(calculated_clusters, max_clusters, n_samples)
        if n_clusters < 1:
            n_clusters = 1
        
        print(f"  数据量: {n_samples} 个片段，使用 {n_clusters} 个聚类")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20, max_iter=300)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # 更新DataFrame
        df['business_cluster'] = cluster_labels
        
        # 为每个聚类生成业务标签（基于聚类结果的特征分布）
        cluster_labels_dict = self.generate_behavior_intent_labels(df, cluster_labels)
        
        return df, cluster_labels_dict
    
    def segment_by_intent_change(self, data, intent_change_threshold=0.3):
        """基于意图变化切分用户行为
        
        参数:
            data: 用户行为数据列表
            intent_change_threshold: 意图变化阈值 (0-1)，超过此值认为意图发生变化
        """
        user_groups = defaultdict(list)
        for record in data:
            user_groups[record['user_id']].append(record)
        
        all_segments = []
        segment_metadata = []
        
        for user_id, records in user_groups.items():
            records.sort(key=lambda x: self.parse_timestamp(x['timestamp']))
            
            if len(records) == 0:
                continue
            
            segments = []
            current_segment = [records[0]]
            prev_intent_features = self.extract_intent_features_from_record(records[0])
            
            for i in range(1, len(records)):
                prev_time = self.parse_timestamp(records[i-1]['timestamp'])
                curr_time = self.parse_timestamp(records[i]['timestamp'])
                time_gap = curr_time - prev_time
                
                # 提取当前行为的意图特征
                curr_intent_features = self.extract_intent_features_from_record(records[i])
                
                # 判断是否需要分段
                should_segment = False
                segment_reason = ""
                
                # 情况1: 时间间隔过长（即使意图没变，也应该分段）
                if time_gap > self.inactivity_threshold:
                    should_segment = True
                    segment_reason = "长时间间隔"
                # 情况2: 意图发生显著变化
                elif prev_intent_features is not None and curr_intent_features is not None:
                    intent_change = self.calculate_intent_change(prev_intent_features, curr_intent_features)
                    if intent_change >= intent_change_threshold:
                        should_segment = True
                        segment_reason = f"意图变化 (变化度: {intent_change:.2f})"
                # 情况3: 无法提取意图特征，但时间间隔较长
                elif time_gap > self.gap_threshold:
                    should_segment = True
                    segment_reason = "时间间隔且无法提取意图"
                
                if should_segment:
                    segments.append(current_segment)
                    current_segment = [records[i]]
                    prev_intent_features = curr_intent_features
                else:
                    current_segment.append(records[i])
                    # 更新当前片段的代表性意图特征（使用最新的意图）
                    if curr_intent_features is not None:
                        prev_intent_features = curr_intent_features
            
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
                
                # 使用最后一个记录的output（代表最新的意图状态）
                latest_output = last_record.get('output', '')
                if not latest_output and len(segment) > 1:
                    latest_output = segment[-2].get('output', '')
                if not latest_output:
                    latest_output = first_record.get('output', '')
                
                features = self.extract_business_features(
                    latest_output, 
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
    
    def segment_by_time(self, data):
        """按时间窗口切分用户行为（保留原方法作为备选）"""
        user_groups = defaultdict(list)
        for record in data:
            user_groups[record['user_id']].append(record)
        
        all_segments = []
        segment_metadata = []
        
        for user_id, records in user_groups.items():
            records.sort(key=lambda x: self.parse_timestamp(x['timestamp']))
            
            if len(records) == 0:
                continue
            
            segments = []
            current_segment = [records[0]]
            
            for i in range(1, len(records)):
                prev_time = self.parse_timestamp(records[i-1]['timestamp'])
                curr_time = self.parse_timestamp(records[i]['timestamp'])
                time_gap = curr_time - prev_time
                
                if time_gap > self.gap_threshold:
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
                
                # 使用最后一个记录的output（代表最新的意图状态）
                latest_output = last_record.get('output', '')
                if not latest_output and len(segment) > 1:
                    latest_output = segment[-2].get('output', '')
                if not latest_output:
                    latest_output = first_record.get('output', '')
                
                features = self.extract_business_features(
                    latest_output, 
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
    
    def segment_by_financial_intent(self, data, intent_change_threshold=0.3):
        """基于金融意图变化切分用户行为（专门用于YUP等金融公司）
        
        参数:
            data: 用户行为数据列表
            intent_change_threshold: 意图变化阈值 (0-1)，超过此值认为意图发生变化
        """
        user_groups = defaultdict(list)
        for record in data:
            user_groups[record['user_id']].append(record)
        
        all_segments = []
        segment_metadata = []
        
        for user_id, records in user_groups.items():
            records.sort(key=lambda x: self.parse_timestamp(x['timestamp']))
            
            if len(records) == 0:
                continue
            
            segments = []
            current_segment = [records[0]]
            prev_features = self.extract_financial_features([records[0]], records)
            
            for i in range(1, len(records)):
                prev_time = self.parse_timestamp(records[i-1]['timestamp'])
                curr_time = self.parse_timestamp(records[i]['timestamp'])
                time_gap = curr_time - prev_time
                
                # 提取当前行为的特征
                curr_features = self.extract_financial_features([records[i]], records)
                
                # 判断是否需要分段
                should_segment = False
                segment_reason = ""
                
                # 情况1: 时间间隔过长
                if time_gap > self.inactivity_threshold:
                    should_segment = True
                    segment_reason = "长时间间隔"
                # 情况2: 交易状态发生变化（重要：从无交易到有交易）
                elif prev_features.get('has_transaction', 0) != curr_features.get('has_transaction', 0):
                    should_segment = True
                    segment_reason = "交易状态变化"
                # 情况3: KYC状态发生变化
                elif prev_features.get('kyc_started', 0) != curr_features.get('kyc_started', 0):
                    should_segment = True
                    segment_reason = "KYC状态变化"
                # 情况4: 时间间隔较长
                elif time_gap > self.gap_threshold:
                    should_segment = True
                    segment_reason = "时间间隔"
                
                if should_segment:
                    segments.append(current_segment)
                    current_segment = [records[i]]
                    prev_features = curr_features
                else:
                    current_segment.append(records[i])
                    # 更新特征（使用整个当前片段）
                    prev_features = self.extract_financial_features(current_segment, records)
            
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
                
                # 提取金融特征
                financial_features = self.extract_financial_features(segment, records)
                
                metadata = {
                    'user_id': user_id,
                    'segment_id': f"{user_id}_seg_{seg_idx}",
                    'segment_index': seg_idx,
                    'start_time': first_record['timestamp'],
                    'end_time': last_record['timestamp'],
                    'duration_minutes': duration,
                    'record_count': len(segment),
                    **financial_features
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
            'core_need',             # 核心需求 (0-3)
            'price_sensitivity'      # 价格敏感度 (0=预算导向, 1=中端, 2=高端)
        ]
        
        # 提取特征矩阵
        X = df[feature_cols].copy()
        
        # 对长尾分布的特征进行对数变换（让算法更容易发现模式）
        X['record_count_log'] = np.log1p(X['record_count'])
        X['duration_minutes_log'] = np.log1p(X['duration_minutes'] + 0.001)  # 避免log(0)
        
        # 移除原始值，使用变换后的值
        X = X.drop(['record_count', 'duration_minutes'], axis=1)
        X.columns = ['intent_score', 'purchase_stage', 'product_preference', 
                     'concern_focus', 'core_need', 'price_sensitivity', 
                     'record_count_log', 'duration_minutes_log']
        
        # 标准化（让不同量纲的特征在相同尺度上）
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 使用KMeans聚类 - 让算法自动发现数据中的模式
        # 根据数据量动态调整聚类数：至少需要n_clusters个样本
        n_samples = len(X_scaled)
        # 计算合适的聚类数：每20个样本1个聚类，最少3个，最多100个，但不能超过样本数
        # 设置合理的上限，避免聚类数过多导致难以解释
        max_clusters = 100
        min_clusters = 3
        # 根据数据量计算聚类数：每20个样本1个聚类
        calculated_clusters = max(min_clusters, n_samples // 20)
        # 限制在合理范围内，但不能超过样本数
        n_clusters = min(calculated_clusters, max_clusters, n_samples)
        if n_clusters < 1:
            n_clusters = 1  # 至少1个聚类
        
        print(f"  数据量: {n_samples} 个片段，使用 {n_clusters} 个聚类")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20, max_iter=300)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        df['business_cluster'] = cluster_labels
        
        # 保存原始特征值用于后续分析
        df['record_count_log'] = X['record_count_log'].values
        df['duration_minutes_log'] = X['duration_minutes_log'].values
        
        # 为每个聚类生成业务标签（基于聚类结果的特征分布）
        cluster_labels_dict = self.generate_behavior_intent_labels(df, df['business_cluster'].values)
        
        return df, cluster_labels_dict
    
    def cluster_by_financial_features(self, segment_metadata):
        """基于金融特征进行聚类（专门用于YUP等金融公司）"""
        df = pd.DataFrame(segment_metadata)
        
        # 金融相关特征（增强版，包含更多业务维度）
        feature_cols = [
            # KYC相关特征
            'kyc_started',              # 是否开始KYC (0/1)
            'kyc_event_count',          # KYC事件数量
            # 交易相关特征
            'has_transaction',          # 是否有交易 (0/1)
            'transaction_completed',    # 是否完成交易 (0/1)
            'first_order_completed',    # 用户是否已完成首笔订单 (0/1)
            'post_first_order',         # 当前片段是否在首笔订单之后 (0/1)
            # 行为活跃度特征
            'event_count',              # 事件总数
            'payment_related_events',   # 支付相关事件数
            'recharge_related_events',  # 充值相关事件数
            'voucher_related_events',   # 优惠券相关事件数
            # 时间特征
            'duration_minutes',         # 片段时长（分钟）
            'record_count',             # 记录数量
            # 意图强度
            'intent_score',             # 意图强度
            # 新增：业务深度特征
            'feature_diversity',        # 功能多样性
            'activation_related_events', # 激活相关事件
            'navigation_related_events', # 导航相关事件
            'click_related_events',     # 点击相关事件
            'profile_related_events',    # 个人中心相关事件
            'task_related_events',       # 任务/活动相关事件
            'interaction_depth',         # 交互深度
            'business_scenario',         # 业务场景类型
            'activity_concentration',    # 行为集中度
            'activity_intensity'         # 时间活跃度
        ]
        
        # 确保所有特征列都存在
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0
        
        # 提取特征矩阵
        X = df[feature_cols].copy()
        
        # 对长尾分布的特征进行对数变换
        X['event_count_log'] = np.log1p(X['event_count'])
        X['kyc_event_count_log'] = np.log1p(X['kyc_event_count'])
        X['payment_related_events_log'] = np.log1p(X['payment_related_events'])
        X['recharge_related_events_log'] = np.log1p(X['recharge_related_events'])
        X['voucher_related_events_log'] = np.log1p(X['voucher_related_events'])
        X['duration_minutes_log'] = np.log1p(X['duration_minutes'] + 0.001)
        X['record_count_log'] = np.log1p(X['record_count'])
        # 新增特征的对数变换
        if 'activation_related_events' in X.columns:
            X['activation_related_events_log'] = np.log1p(X['activation_related_events'])
        if 'navigation_related_events' in X.columns:
            X['navigation_related_events_log'] = np.log1p(X['navigation_related_events'])
        if 'click_related_events' in X.columns:
            X['click_related_events_log'] = np.log1p(X['click_related_events'])
        if 'profile_related_events' in X.columns:
            X['profile_related_events_log'] = np.log1p(X['profile_related_events'])
        if 'task_related_events' in X.columns:
            X['task_related_events_log'] = np.log1p(X['task_related_events'])
        if 'activity_intensity' in X.columns:
            X['activity_intensity_log'] = np.log1p(X['activity_intensity'] + 0.001)
        
        # 移除原始值，使用变换后的值
        cols_to_drop = ['event_count', 'kyc_event_count', 'payment_related_events', 
                       'recharge_related_events', 'voucher_related_events', 
                       'duration_minutes', 'record_count']
        # 如果新特征存在，也移除原始值
        for col in ['activation_related_events', 'navigation_related_events', 
                   'click_related_events', 'profile_related_events', 
                   'task_related_events', 'activity_intensity']:
            if col in X.columns and f'{col}_log' in X.columns:
                cols_to_drop.append(col)
        X = X.drop([col for col in cols_to_drop if col in X.columns], axis=1)
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 使用KMeans聚类（更精细的聚类）
        n_samples = len(X_scaled)
        # 对于小样本，使用更细致的聚类（每3-5个样本1个聚类）
        # 对于大样本，使用每10-15个样本1个聚类
        if n_samples < 20:
            # 小样本：更细致的聚类
            calculated_clusters = max(3, n_samples // 3)  # 每3个样本1个聚类
            max_clusters = min(10, n_samples)  # 最多10个聚类
        else:
            # 大样本：标准聚类
            calculated_clusters = max(5, n_samples // 10)  # 每10个样本1个聚类
            max_clusters = 100
        
        n_clusters = min(calculated_clusters, max_clusters, n_samples)
        if n_clusters < 1:
            n_clusters = 1
        
        print(f"  数据量: {n_samples} 个片段，使用 {n_clusters} 个聚类（精细模式）")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=50, max_iter=500)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        df['business_cluster'] = cluster_labels
        
        # 保存变换后的特征值用于后续分析
        log_cols = ['event_count_log', 'kyc_event_count_log', 'payment_related_events_log',
                   'recharge_related_events_log', 'voucher_related_events_log',
                   'duration_minutes_log', 'record_count_log',
                   'activation_related_events_log', 'navigation_related_events_log',
                   'click_related_events_log', 'profile_related_events_log',
                   'task_related_events_log', 'activity_intensity_log']
        for col in log_cols:
            if col in X.columns:
                df[col] = X[col].values
        
        # 为每个聚类生成金融业务标签
        cluster_labels_dict = self.generate_financial_labels(df, cluster_labels)
        
        return df, cluster_labels_dict
    
    def generate_financial_labels(self, df, cluster_labels):
        """为每个聚类生成基于金融特征的标签"""
        cluster_labels_dict = {}
        unique_cluster_ids = sorted([int(x) for x in df['business_cluster'].unique()])
        
        # 计算全局统计信息
        global_avg_kyc = df['kyc_event_count'].mean()
        global_avg_transaction = df['has_transaction'].mean()
        global_avg_intent = df['intent_score'].mean()
        global_avg_events = df['event_count'].mean()
        
        for cluster_id in unique_cluster_ids:
            cluster_data = df[df['business_cluster'] == cluster_id]
            
            # 计算聚类的平均特征
            avg_kyc_started = cluster_data['kyc_started'].mean()
            avg_kyc_events = cluster_data['kyc_event_count'].mean()
            avg_has_transaction = cluster_data['has_transaction'].mean()
            avg_transaction_completed = cluster_data['transaction_completed'].mean()
            avg_event_count = cluster_data['event_count'].mean()
            avg_payment_events = cluster_data['payment_related_events'].mean()
            avg_recharge_events = cluster_data['recharge_related_events'].mean()
            avg_voucher_events = cluster_data['voucher_related_events'].mean()
            avg_intent_score = cluster_data['intent_score'].mean()
            avg_duration = cluster_data['duration_minutes'].mean()
            
            # 计算首笔订单相关特征
            avg_first_order_completed = cluster_data['first_order_completed'].mean() if 'first_order_completed' in cluster_data.columns else 0
            avg_post_first_order = cluster_data['post_first_order'].mean() if 'post_first_order' in cluster_data.columns else 0
            
            # 获取业务场景特征（如果存在）
            avg_business_scenario = cluster_data['business_scenario'].mean() if 'business_scenario' in cluster_data.columns else 7
            avg_activity_concentration = cluster_data['activity_concentration'].mean() if 'activity_concentration' in cluster_data.columns else 0.5
            avg_feature_diversity = cluster_data['feature_diversity'].mean() if 'feature_diversity' in cluster_data.columns else 0.5
            avg_activity_intensity = cluster_data['activity_intensity'].mean() if 'activity_intensity' in cluster_data.columns else 0
            
            # 生成行为模式标签（优先考虑业务场景和首笔订单状态）
            scenario_labels = {
                0: "激活阶段",
                1: "KYC进行中",
                2: "探索阶段",
                3: "支付阶段",
                4: "充值阶段",
                5: "优惠券阶段",
                6: "复购阶段",
                7: "综合探索"
            }
            
            # 根据业务场景和首笔订单状态生成标签
            if avg_first_order_completed > 0.5:
                # 用户已完成首笔订单
                if avg_post_first_order > 0.5:
                    if avg_business_scenario == 6:
                        behavior_label = "复购活跃"
                    elif avg_business_scenario == 5:
                        behavior_label = "复购·优惠券导向"
                    elif avg_business_scenario == 4:
                        behavior_label = "复购·充值导向"
                    elif avg_business_scenario == 3:
                        behavior_label = "复购·支付导向"
                    else:
                        behavior_label = "首单后活跃"
                else:
                    behavior_label = "首单完成中"
            elif avg_business_scenario < 7:
                # 根据业务场景判断
                behavior_label = scenario_labels.get(int(avg_business_scenario), "探索阶段")
            elif avg_has_transaction > 0.5:
                behavior_label = "交易进行中"
            elif avg_kyc_started > 0.5:
                behavior_label = "KYC进行中"
            elif avg_event_count < 5:
                behavior_label = "低活跃度"
            else:
                behavior_label = "探索阶段"
            
            # 生成紧迫度标签（基于意图强度）
            intent_ratio = avg_intent_score / global_avg_intent if global_avg_intent > 0 else 1.0
            if intent_ratio > 1.2:
                urgency_label = "高紧迫"
            elif intent_ratio < 0.8:
                urgency_label = "低紧迫"
            else:
                urgency_label = "中紧迫"
            
            # 生成短标签
            short_label = f"{behavior_label}·{urgency_label}"
            
            # 确定主要行为类型（考虑更多维度）
            # 获取新增特征
            avg_activation_events = cluster_data['activation_related_events'].mean() if 'activation_related_events' in cluster_data.columns else 0
            avg_navigation_events = cluster_data['navigation_related_events'].mean() if 'navigation_related_events' in cluster_data.columns else 0
            avg_task_events = cluster_data['task_related_events'].mean() if 'task_related_events' in cluster_data.columns else 0
            
            # 根据业务场景和事件分布确定主要活动
            if avg_business_scenario == 0:
                main_activity = "激活导向"
            elif avg_business_scenario == 1:
                main_activity = "KYC导向"
            elif avg_business_scenario == 3:
                main_activity = "支付导向"
            elif avg_business_scenario == 4:
                main_activity = "充值导向"
            elif avg_business_scenario == 5:
                main_activity = "优惠券导向"
            elif avg_business_scenario == 6:
                main_activity = "复购导向"
            elif avg_task_events > 3:
                main_activity = "任务/活动导向"
            elif avg_navigation_events > avg_event_count * 0.5:
                main_activity = "浏览导向"
            elif avg_payment_events > avg_recharge_events and avg_payment_events > avg_voucher_events:
                main_activity = "支付导向"
            elif avg_recharge_events > avg_payment_events and avg_recharge_events > avg_voucher_events:
                main_activity = "充值导向"
            elif avg_voucher_events > 0:
                main_activity = "优惠券导向"
            else:
                main_activity = "综合探索"
            
            # 生成完整标签
            full_label = f"{behavior_label}·{urgency_label}·{main_activity}"
            
            # 确定优先级和推荐行动（基于首笔订单状态）
            if avg_first_order_completed > 0.5:
                # 已完成首笔订单的用户：重点提升复购率
                if avg_post_first_order > 0.5:
                    action_priority = "高"
                    recommended_action = "促进再次下单"
                else:
                    action_priority = "中"
                    recommended_action = "引导完成首单并促进复购"
            else:
                # 未完成首笔订单的用户：重点促进首单
                priority_score = avg_transaction_completed * 0.5 + avg_intent_score * 0.3 + (avg_event_count / 50.0) * 0.2
                if priority_score > 0.7:
                    action_priority = "高"
                    recommended_action = "促进首笔订单完成"
                elif priority_score > 0.4:
                    action_priority = "中"
                    recommended_action = "引导完成KYC或首单"
                else:
                    action_priority = "低"
                    recommended_action = "提升活跃度和参与度"
            
            cluster_labels_dict[str(cluster_id)] = {
                'short_label': short_label,
                'full_label': full_label,
                'action_priority': action_priority,
                'recommended_action': recommended_action,
                'characteristics': {
                    'behavior': behavior_label,
                    'urgency': urgency_label,
                    'main_activity': main_activity,
                    'kyc_status': "已开始" if avg_kyc_started > 0.5 else "未开始",
                    'transaction_status': "已完成" if avg_transaction_completed > 0.5 else ("进行中" if avg_has_transaction > 0.5 else "未开始"),
                    'first_order_completed': "是" if avg_first_order_completed > 0.5 else "否",
                    'post_first_order': "是" if avg_post_first_order > 0.5 else "否"
                },
                'avg_features': {
                    'kyc_started': float(avg_kyc_started),
                    'kyc_event_count': float(avg_kyc_events),
                    'has_transaction': float(avg_has_transaction),
                    'transaction_completed': float(avg_transaction_completed),
                    'first_order_completed': float(avg_first_order_completed),
                    'post_first_order': float(avg_post_first_order),
                    'event_count': float(avg_event_count),
                    'payment_related_events': float(avg_payment_events),
                    'recharge_related_events': float(avg_recharge_events),
                    'voucher_related_events': float(avg_voucher_events),
                    'intent_score': float(avg_intent_score),
                    'duration_minutes': float(avg_duration),
                    'record_count': float(cluster_data['record_count'].mean())
                }
            }
        
        return cluster_labels_dict
    
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
            avg_intent_score = cluster_data['intent_score'].mean()
            
            # 计算相对值（用于生成标签）
            record_ratio = avg_record_count / global_avg_record if global_avg_record > 0 else 1.0
            duration_ratio = avg_duration / global_avg_duration if global_avg_duration > 0 else 1.0
            intent_ratio = avg_intent_score / global_avg_intent if global_avg_intent > 0 else 1.0
            
            # 生成行为模式标签
            if avg_record_count <= 1:
                behavior_label = "单次浏览"
            elif record_ratio < 0.7:
                behavior_label = "快速浏览"
            elif record_ratio > 1.5:
                behavior_label = "深度研究"
            else:
                behavior_label = "中等参与"
            
            # 生成紧迫度标签
            if intent_ratio > 1.2:
                urgency_label = "高紧迫"
            elif intent_ratio < 0.8:
                urgency_label = "低紧迫"
            else:
                urgency_label = "中紧迫"
            
            # 生成短标签
            short_label = f"{behavior_label}·{urgency_label}"
            
            # 获取购买阶段
            stage_counts = cluster_data['purchase_stage'].value_counts()
            dominant_stage = stage_counts.idxmax() if len(stage_counts) > 0 else 0
            stage_map = {0: '浏览阶段', 1: '对比阶段', 2: '决策阶段'}
            stage_name = stage_map.get(dominant_stage, '浏览阶段')
            
            # 获取价格敏感度
            price_counts = cluster_data['price_sensitivity'].value_counts()
            dominant_price = price_counts.idxmax() if len(price_counts) > 0 else 2
            price_map = {0: '预算导向', 1: '中端平衡', 2: '高端价值型'}
            price_name = price_map.get(dominant_price, '高端价值型')
            
            # 获取产品偏好
            product_counts = cluster_data['product_preference'].value_counts()
            dominant_product = product_counts.idxmax() if len(product_counts) > 0 else 5
            product_map = {0: 'Z6偏好', 1: 'A1偏好', 2: 'F1偏好', 3: 'H02偏好', 4: 'G1偏好', 5: '多产品比较'}
            product_name = product_map.get(dominant_product, '多产品比较')
            
            # 获取关注点
            concern_counts = cluster_data['concern_focus'].value_counts()
            dominant_concern = concern_counts.idxmax() if len(concern_counts) > 0 else 4
            concern_map = {0: '价格导向', 1: '质量导向', 2: '舒适度导向', 3: '有效性导向', 4: '综合关注'}
            concern_name = concern_map.get(dominant_concern, '综合关注')
            
            # 获取核心需求
            need_counts = cluster_data['core_need'].value_counts()
            dominant_need = need_counts.idxmax() if len(need_counts) > 0 else 3
            need_map = {0: '止鼾需求', 1: '颈部疼痛', 2: '睡眠质量', 3: '综合需求'}
            need_name = need_map.get(dominant_need, '综合需求')
            
            # 获取参与度
            if avg_duration <= 0.01:
                engagement = "快速浏览者"
            elif duration_ratio < 0.5:
                engagement = "快速浏览者"
            elif duration_ratio > 2.0:
                engagement = "深度研究者"
            else:
                engagement = "中等参与者"
            
            # 生成完整标签
            full_label = f"{behavior_label}·{urgency_label}·{stage_name}·{product_name}"
            
            # 确定优先级（基于意图强度和交互次数）
            priority_score = avg_intent_score * 0.7 + (avg_record_count / 10.0) * 0.3
            if priority_score > 0.7:
                action_priority = "高"
                recommended_action = "立即转化"
            elif priority_score > 0.4:
                action_priority = "中"
                recommended_action = "引导转化"
            else:
                action_priority = "低"
                recommended_action = "教育引导"
            
            cluster_labels_dict[str(cluster_id)] = {
                'short_label': short_label,
                'full_label': full_label,
                'action_priority': action_priority,
                'recommended_action': recommended_action,
                'characteristics': {
                    'behavior': behavior_label,
                    'urgency': urgency_label,
                    'stage': stage_name,
                    'price': price_name,
                    'product': product_name,
                    'concern': concern_name,
                    'need': need_name,
                    'engagement': engagement
                },
                'avg_features': {
                    'record_count': float(avg_record_count),
                    'duration_minutes': float(avg_duration),
                    'intent_score': float(avg_intent_score),
                    'purchase_stage': int(dominant_stage),
                    'price_sensitivity': int(dominant_price),
                    'product_preference': int(dominant_product),
                    'concern_focus': int(dominant_concern),
                    'core_need': int(dominant_need)
                }
            }
        
        return cluster_labels_dict
    
    def analyze(self, input_file='../extracted_data.json', shop_id=None):
        """执行完整的聚类分析"""
        print("="*80)
        print("基于用户行为意图的聚类分析")
        print("目标：让商家可以快速捕捉到当下的用户意图并给出相应的反应")
        print("="*80)
        
        # 检测店铺ID（从文件名或数据中）
        if shop_id is None:
            # 尝试从文件名中提取
            if 'shop_39' in str(input_file) or 'shop_39' in str(Path(input_file).name):
                shop_id = 39
            elif 'shop_YUP' in str(input_file) or 'YUP' in str(Path(input_file).name):
                shop_id = 'YUP'
            else:
                # 尝试从数据中检测
                try:
                    with open(input_file, 'r', encoding='utf-8') as f:
                        sample_data = json.load(f)
                        if sample_data and len(sample_data) > 0:
                            shop_id = sample_data[0].get('shop_id')
                            if shop_id:
                                # 尝试转换为整数，如果失败则保持原值（可能是字符串如YUP）
                                try:
                                shop_id = int(shop_id)
                                except (ValueError, TypeError):
                                    shop_id = str(shop_id)
                except:
                    pass
        
        # 加载数据
        print(f"\n正在加载数据: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"加载了 {len(data)} 条记录")
        
        if shop_id:
            print(f"检测到店铺ID: {shop_id}")
        
        # 基于意图变化切分（当用户意图真正发生变化时才分段）
        print("\n正在进行基于意图变化的行为切分...")
        if shop_id == 'YUP':
            print("  策略：基于金融特征变化切分（KYC状态、交易状态、时间间隔）")
            all_segments, segment_metadata = self.segment_by_financial_intent(data, intent_change_threshold=self.intent_change_threshold)
        else:
        print("  策略：当用户意图发生显著变化时创建新片段，允许一个用户拥有多个意图片段")
        all_segments, segment_metadata = self.segment_by_intent_change(data, intent_change_threshold=self.intent_change_threshold)
        print(f"切分为 {len(segment_metadata)} 个意图片段")
        print(f"  参数：意图变化阈值={self.intent_change_threshold}, 时间间隔阈值={self.gap_threshold.total_seconds()/60:.0f}分钟/{self.inactivity_threshold.total_seconds()/60:.0f}分钟")
        
        # 行为意图聚类（店铺39使用Gemini embedding，YUP使用金融特征，其他使用默认方法）
        print("\n正在进行行为意图聚类...")
        if shop_id == 39:
            df, cluster_labels_dict = self.cluster_by_gemini_embedding(segment_metadata, shop_id=39, input_file=input_file)
        elif shop_id == 'YUP':
            df, cluster_labels_dict = self.cluster_by_financial_features(segment_metadata)
        else:
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
        # 只处理在cluster_labels中存在的cluster_id
        valid_clusters = {k: v for k, v in cluster_counts.items() if k in cluster_labels}
        sorted_clusters = sorted(valid_clusters.items(), 
                                key=lambda x: (
                                    cluster_labels[x[0]]['avg_features'].get('intent_score', 0),
                                    cluster_labels[x[0]]['avg_features'].get('record_count', 0)
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
            
            # 根据聚类类型显示不同的特征
            if 'kyc_started' in cluster_df.columns:
                # 金融特征（YUP）
                print(f"  KYC状态: {label_info['characteristics'].get('kyc_status', '未知')}")
                print(f"  交易状态: {label_info['characteristics'].get('transaction_status', '未知')}")
                print(f"  主要活动: {label_info['characteristics'].get('main_activity', '未知')}")
                if 'kyc_event_count' in cluster_df.columns:
                    print(f"  平均KYC事件数: {cluster_df['kyc_event_count'].mean():.1f}")
                if 'payment_related_events' in cluster_df.columns:
                    print(f"  支付相关事件: {cluster_df['payment_related_events'].mean():.1f}")
                    print(f"  充值相关事件: {cluster_df['recharge_related_events'].mean():.1f}")
                    print(f"  优惠券相关事件: {cluster_df['voucher_related_events'].mean():.1f}")
            else:
                # 电商特征（其他店铺）
                print(f"  购买阶段: {label_info['characteristics'].get('stage', '未知')}")
                print(f"  产品偏好: {label_info['characteristics'].get('product', '未知')}")

if __name__ == '__main__':
    clusterer = BehaviorIntentClusterer()
    clusterer.analyze()
