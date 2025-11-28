#!/usr/bin/env python3
"""
基于业务驱动聚类的用户画像分析
目标：为每个聚类生成有明显差异的营销策略
"""

import json
import pandas as pd
from collections import Counter
from pathlib import Path

class BusinessDrivenPortraitAnalyzer:
    def __init__(self, cluster_results_file='../cluster_timeClip/business_cluster_results.json'):
        self.cluster_results_file = cluster_results_file
        self.df = None
        self.cluster_labels = None
        
    def load_data(self):
        """加载聚类结果"""
        with open(self.cluster_results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.df = pd.DataFrame(data['segments'])
        self.cluster_labels = data['clustering']['cluster_labels']
        
        # 转换时间列
        self.df['start_time'] = pd.to_datetime(self.df['start_time'])
        self.df['end_time'] = pd.to_datetime(self.df['end_time'])
        
        return self.df
    
    def generate_marketing_strategy(self, cluster_id, cluster_data, label_info):
        """为每个聚类生成差异化的营销策略"""
        avg_duration = cluster_data['duration_minutes'].mean()
        avg_interactions = cluster_data['record_count'].mean()
        avg_intent = cluster_data['intent_score'].mean()
        user_count = cluster_data['user_id'].nunique()
        
        characteristics = label_info.get('characteristics', {})
        
        # 检测是否为金融场景（YUP）- 通过检查是否有金融特征字段
        is_financial = 'kyc_status' in characteristics or 'transaction_status' in characteristics or 'main_activity' in characteristics
        
        if is_financial:
            # 金融场景特征
            behavior = characteristics.get('behavior', '探索阶段')
            urgency = characteristics.get('urgency', '中紧迫')
            main_activity = characteristics.get('main_activity', '综合探索')
            kyc_status = characteristics.get('kyc_status', '未开始')
            transaction_status = characteristics.get('transaction_status', '未开始')
            
            # 金融场景的营销策略
            return self.generate_financial_marketing_strategy(
                cluster_id, cluster_data, label_info, behavior, urgency, 
                main_activity, kyc_status, transaction_status,
                avg_duration, avg_interactions, avg_intent, user_count
            )
        else:
            # 电商场景特征
            stage = characteristics.get('stage', '浏览阶段')
            price = characteristics.get('price', '高端价值型')
            engagement = characteristics.get('engagement', '快速浏览者')
            product = characteristics.get('product', '多产品比较')
            concern = characteristics.get('concern', '综合关注')
            need = characteristics.get('need', '综合需求')
        
        strategy = {
            'cluster_id': str(cluster_id),
            'cluster_name': label_info['short_label'],
            'full_label': label_info['full_label'],
            'key_characteristics': {
                'user_count': int(user_count),
                'segment_count': len(cluster_data),
                'avg_duration_minutes': float(avg_duration),
                'avg_interactions': float(avg_interactions),
                'avg_intent_score': float(avg_intent),
                'stage': stage,
                'price_sensitivity': price,
                'engagement_level': engagement,
                'product_preference': product,
                'concern_focus': concern,
                'core_need': need
            },
            'marketing_strategy': [],
            'content_strategy': [],
            'conversion_tactics': [],
            'pricing_strategy': [],
            'product_recommendation': [],
            'campaign_differentiation': []
        }
        
        # 基于购买阶段的策略
        if stage == '决策阶段':
            strategy['marketing_strategy'].append("【高转化优先级】用户已接近购买决策，需要立即转化刺激")
            strategy['marketing_strategy'].append("提供限时优惠、免费试用、快速配送等转化激励")
            strategy['conversion_tactics'].append("在页面添加紧迫感元素（库存紧张、限时优惠倒计时）")
            strategy['conversion_tactics'].append("提供一键购买、快速结账流程")
            strategy['conversion_tactics'].append("展示用户评价、成功案例、满意度数据")
        elif stage == '对比阶段':
            strategy['marketing_strategy'].append("【对比优化】用户正在比较产品，需要差异化优势展示")
            strategy['marketing_strategy'].append("提供详细的产品对比表、功能对比图")
            strategy['conversion_tactics'].append("突出产品独特卖点（USP）")
            strategy['conversion_tactics'].append("提供专业咨询、在线客服支持")
            strategy['conversion_tactics'].append("展示技术优势、认证证书、临床数据")
        else:  # 浏览阶段
            strategy['marketing_strategy'].append("【教育引导】用户处于早期浏览阶段，需要教育性内容")
            strategy['marketing_strategy'].append("提供产品功能说明、使用场景、解决痛点的方式")
            strategy['conversion_tactics'].append("优化首屏内容，快速抓住注意力")
            strategy['conversion_tactics'].append("提供视频教程、使用指南、FAQ")
        
        # 基于价格敏感度的策略
        if price == '价格敏感型':
            strategy['pricing_strategy'].append("【价格驱动】用户对价格敏感，需要突出性价比")
            strategy['pricing_strategy'].append("提供分期付款、优惠券、限时折扣")
            strategy['pricing_strategy'].append("展示价格对比、节省金额、ROI计算")
            strategy['marketing_strategy'].append("强调性价比、长期价值、投资回报")
        elif price == '中等价格型':
            strategy['pricing_strategy'].append("【平衡策略】用户关注价格但更重视价值")
            strategy['pricing_strategy'].append("提供中等价位产品推荐、套餐优惠")
            strategy['pricing_strategy'].append("展示功能与价格的平衡点")
        else:  # 高端价值型
            strategy['pricing_strategy'].append("【价值驱动】用户更关注产品价值和功能，价格敏感度低")
            strategy['pricing_strategy'].append("强调产品品质、技术创新、用户体验")
            strategy['pricing_strategy'].append("提供高端产品线、定制化服务")
            strategy['marketing_strategy'].append("突出品牌价值、专业认证、用户成功案例")
        
        # 基于参与度的策略
        if engagement == '深度研究者':
            strategy['content_strategy'].append("【深度内容】用户深度研究，需要详细的产品信息")
            strategy['content_strategy'].append("提供详细的产品说明、技术参数、使用视频、白皮书")
            strategy['conversion_tactics'].append("提供下载资料、技术文档、案例研究")
            strategy['conversion_tactics'].append("安排专业咨询、产品演示、试用体验")
        elif engagement == '中等参与':
            strategy['content_strategy'].append("【平衡内容】用户中等参与，需要适度的产品信息")
            strategy['content_strategy'].append("提供产品概览、核心功能、使用场景")
            strategy['conversion_tactics'].append("优化页面布局，突出关键信息")
        else:  # 快速浏览者
            strategy['content_strategy'].append("【简洁内容】用户快速浏览，需要快速抓住注意力")
            strategy['content_strategy'].append("优化首屏内容，突出核心卖点和优惠信息")
            strategy['conversion_tactics'].append("使用大标题、醒目图片、简短文案")
            strategy['conversion_tactics'].append("减少页面跳转，提供一站式信息")
        
        # 基于产品偏好的策略
        if product != '多产品比较':
            strategy['product_recommendation'].append(f"【主推产品】{product}")
            strategy['product_recommendation'].append(f"重点展示{product}的核心功能和优势")
            strategy['product_recommendation'].append(f"提供{product}的详细页面、视频、用户评价")
        else:
            strategy['product_recommendation'].append("【多产品比较】用户关注多个产品")
            strategy['product_recommendation'].append("提供产品对比工具、推荐算法")
            strategy['product_recommendation'].append("根据用户需求推荐最适合的产品")
        
        # 基于关注点的策略
        if concern == '价格导向':
            strategy['content_strategy'].append("【价格内容】针对价格关注点制作内容")
            strategy['content_strategy'].append("提供价格说明、优惠活动、性价比分析")
        elif concern == '功能导向':
            strategy['content_strategy'].append("【功能内容】针对功能关注点制作内容")
            strategy['content_strategy'].append("提供功能详解、技术参数、创新点说明")
        elif concern == '舒适度导向':
            strategy['content_strategy'].append("【舒适度内容】针对舒适度关注点制作内容")
            strategy['content_strategy'].append("提供材质说明、人体工学设计、舒适度测试")
        elif concern == '有效性导向':
            strategy['content_strategy'].append("【有效性内容】针对有效性关注点制作内容")
            strategy['content_strategy'].append("提供临床数据、用户反馈、效果对比")
        
        # 基于核心需求的策略
        if need == '止鼾需求':
            strategy['marketing_strategy'].append("【止鼾解决方案】针对止鼾需求制定策略")
            strategy['content_strategy'].append("提供止鼾原理说明、效果展示、用户见证")
        elif need == '颈部疼痛':
            strategy['marketing_strategy'].append("【疼痛缓解方案】针对颈部疼痛制定策略")
            strategy['content_strategy'].append("提供疼痛缓解原理、支撑设计、康复案例")
        elif need == '睡眠质量':
            strategy['marketing_strategy'].append("【睡眠改善方案】针对睡眠质量制定策略")
            strategy['content_strategy'].append("提供睡眠科学、改善方法、数据追踪")
        
        # 差异化营销活动建议
        strategy['campaign_differentiation'] = self.generate_campaign_ideas(
            stage, price, engagement, product, need
        )
        
        return strategy
    
    def generate_campaign_ideas(self, stage, price, engagement, product, need):
        """生成差异化的营销活动建议"""
        campaigns = []
        
        # 基于购买阶段的活动
        if stage == '决策阶段':
            campaigns.append("【限时转化活动】'立即购买立减XX元'、'24小时内下单送XX'")
            campaigns.append("【紧迫感营销】库存告急提醒、优惠倒计时、早鸟优惠")
        elif stage == '对比阶段':
            campaigns.append("【对比引导活动】'产品对比赢好礼'、'选择最适合你的产品'")
            campaigns.append("【专业咨询】免费产品咨询、专家推荐、个性化建议")
        else:
            campaigns.append("【教育引导活动】'了解产品赢好礼'、'注册送优惠券'")
            campaigns.append("【内容营销】产品知识竞赛、使用技巧分享、用户故事征集")
        
        # 基于价格敏感度的活动
        if price == '价格敏感型':
            campaigns.append("【价格优惠活动】'限时折扣'、'满减优惠'、'拼团优惠'")
            campaigns.append("【分期付款】0利息分期、灵活还款、降低购买门槛")
        elif price == '高端价值型':
            campaigns.append("【价值展示活动】'品质体验'、'VIP服务'、'专属定制'")
            campaigns.append("【品牌活动】品牌故事、用户成功案例、专业认证展示")
        
        # 基于参与度的活动
        if engagement == '深度研究者':
            campaigns.append("【深度体验活动】'产品试用'、'技术白皮书下载'、'专家咨询'")
            campaigns.append("【专业内容】技术研讨会、产品演示、案例研究")
        elif engagement == '快速浏览者':
            campaigns.append("【快速转化活动】'一键购买'、'快速了解'、'秒杀优惠'")
            campaigns.append("【简化流程】简化注册、快速结账、移动端优化")
        
        return campaigns
    
    def generate_financial_marketing_strategy(self, cluster_id, cluster_data, label_info, 
                                             behavior, urgency, main_activity, 
                                             kyc_status, transaction_status,
                                             avg_duration, avg_interactions, avg_intent, user_count):
        """为金融场景（YUP）生成差异化的营销策略"""
        # 获取首笔订单相关特征
        characteristics = label_info.get('characteristics', {})
        first_order_completed = characteristics.get('first_order_completed', '否')
        post_first_order = characteristics.get('post_first_order', '否')
        
        # 计算平均特征（用于判断）
        avg_first_order_completed = cluster_data['first_order_completed'].mean() if 'first_order_completed' in cluster_data.columns else 0
        avg_post_first_order = cluster_data['post_first_order'].mean() if 'post_first_order' in cluster_data.columns else 0
        
        strategy = {
            'cluster_id': str(cluster_id),
            'cluster_name': label_info['short_label'],
            'full_label': label_info['full_label'],
            'key_characteristics': {
                'user_count': int(user_count),
                'segment_count': len(cluster_data),
                'avg_duration_minutes': float(avg_duration),
                'avg_interactions': float(avg_interactions),
                'avg_intent_score': float(avg_intent),
                'behavior': behavior,
                'urgency': urgency,
                'main_activity': main_activity,
                'kyc_status': kyc_status,
                'transaction_status': transaction_status,
                'first_order_completed': first_order_completed,
                'post_first_order': post_first_order
            },
            'marketing_strategy': [],
            'content_strategy': [],
            'conversion_tactics': [],
            'pricing_strategy': [],
            'product_recommendation': [],
            'campaign_differentiation': []
        }
        
        # ========== 根据首笔订单状态生成差异化策略 ==========
        
        # 情况1: 已完成首笔订单且当前片段在首单之后 - 重点提升复购率
        if avg_first_order_completed > 0.5 and avg_post_first_order > 0.5:
            strategy['marketing_strategy'].append("【复购提升】基于首单推荐相关服务，在关键时间节点（3天、7天、15天、30天）推送个性化复购激励")
            strategy['marketing_strategy'].append("建立复购奖励体系：复购优惠券、积分加倍、会员升级")
            
            strategy['content_strategy'].append("展示首单使用效果和用户评价，推送相关服务介绍和复购优惠活动")
            
            strategy['conversion_tactics'].append("首单完成后立即推送7天内复购优惠券，提供一键复购功能")
            strategy['conversion_tactics'].append("建立复购积分系统，根据浏览行为识别复购意向并推送优惠")
            
            strategy['product_recommendation'].append("推荐升级版服务、组合套餐、限时新品")
            
            strategy['campaign_differentiation'].append("复购优惠券、首单后3/7/30天限时折扣、基于首单的个性化推荐")
        
        # 情况2: 已完成首笔订单但当前片段在首单之前 - 引导完成首单
        elif avg_first_order_completed > 0.5 and avg_post_first_order <= 0.5:
            strategy['marketing_strategy'].append("【首单完成中】简化流程，在关键节点提供客服支持，设置完成奖励")
            
            strategy['conversion_tactics'].append("优化支付流程，发送完成提醒和进度通知，提供帮助中心")
        
        # 情况3: 未完成首笔订单 - 促进首单完成
        else:
            strategy['marketing_strategy'].append("【促进首单】提供新用户专享优惠（首单折扣、免手续费、新用户礼包），简化注册和KYC流程")
            strategy['marketing_strategy'].append("建立信任机制：展示平台安全性、用户评价、成功案例、资金保障")
            
            strategy['content_strategy'].append("展示首单优惠和完成后的权益，提供操作指南，分享首单成功案例")
            
            strategy['conversion_tactics'].append("在首页显著展示首单优惠，简化流程支持自动识别，提供新手引导和限时优惠倒计时")
            
            strategy['product_recommendation'].append("推荐低门槛高价值首单服务、首单优惠套餐、热门服务、限时新品")
            
            strategy['campaign_differentiation'].append("新用户注册奖励、首单专享优惠、免手续费快速通道、新手任务引导")
        
        # 基于交易状态的策略（优先级低于首笔订单状态，避免重复）
        if transaction_status == '进行中' and not (avg_first_order_completed > 0.5 and avg_post_first_order > 0.5):
            strategy['marketing_strategy'].append("【交易进行中】简化交易流程，提供多渠道客服支持，实时监控并解决卡点")
            strategy['conversion_tactics'].append("优化支付页面减少步骤，发送交易进度提醒，提供帮助中心")
        
        # 基于KYC状态的策略（针对KYC导向的聚类）
        if kyc_status == '已开始' and main_activity == 'KYC导向':
            strategy['marketing_strategy'].append("【KYC进行中】主动识别卡点，提供针对性帮助和KYC专属客服通道")
            strategy['content_strategy'].append("提供KYC流程说明和常见问题库，设置专属客服快速响应")
            strategy['conversion_tactics'].append("优化KYC流程支持多种验证方式，发送进度提醒，设置完成奖励")
        elif kyc_status == '未开始' and main_activity == 'KYC导向' and transaction_status == '未开始':
            strategy['marketing_strategy'].append("【引导KYC】说明KYC重要性（账户安全、功能解锁），展示完成后的权益")
            strategy['conversion_tactics'].append("突出KYC奖励，简化流程支持自动识别，提供视频教程")
        
        # 基于主要活动的策略（仅针对特定导向）
        if main_activity == '支付导向':
            strategy['product_recommendation'].append("推荐快捷支付、分期付款、支付安全保障和支付优惠活动")
            strategy['content_strategy'].append("提供支付教程和安全机制说明，展示支付优惠信息")
        elif main_activity == '充值导向':
            strategy['product_recommendation'].append("推荐充值优惠（返现、折扣、奖励）和多种充值方式")
            strategy['content_strategy'].append("提供充值教程，展示充值优惠活动和安全保障说明")
        elif main_activity == '优惠券导向':
            strategy['product_recommendation'].append("推荐优惠券活动和使用指南，展示奖励机制")
            strategy['content_strategy'].append("提供优惠券说明和活动信息，分享使用技巧")
        
        # 基于紧迫度的策略（仅针对极端情况）
        if urgency == '高紧迫':
            strategy['conversion_tactics'].append("提供限时优惠和快速通道，设置专属客服优先处理")
        elif urgency == '低紧迫':
            strategy['marketing_strategy'].append("建立内容营销体系，定期推送教育性内容和使用案例")
        
        return strategy
    
    def analyze_all_clusters(self):
        """分析所有聚类"""
        if self.df is None:
            self.load_data()
        
        all_strategies = []
        
        for cluster_id, label_info in self.cluster_labels.items():
            cluster_data = self.df[self.df['business_cluster'] == int(cluster_id)]
            
            if len(cluster_data) == 0:
                continue
            
            strategy = self.generate_marketing_strategy(
                cluster_id, cluster_data, label_info
            )
            all_strategies.append(strategy)
        
        return all_strategies
    
    def save_results(self, strategies, output_dir='.'):
        """保存分析结果"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # 保存JSON
        json_file = output_dir / 'business_driven_insights.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(strategies, f, indent=2, ensure_ascii=False)
        print(f"业务洞察已保存到: {json_file}")
        
        # 保存CSV摘要
        csv_data = []
        for s in strategies:
            csv_data.append({
                '聚类ID': s['cluster_id'],
                '聚类名称': s['cluster_name'],
                '完整标签': s['full_label'],
                '用户数': s['key_characteristics']['user_count'],
                '片段数': s['key_characteristics']['segment_count'],
                '购买阶段': s['key_characteristics'].get('stage', s['key_characteristics'].get('behavior', '')),
                '价格敏感度': s['key_characteristics'].get('price_sensitivity', s['key_characteristics'].get('main_activity', '')),
                '参与度': s['key_characteristics'].get('engagement_level', s['key_characteristics'].get('urgency', '')),
                '产品偏好': s['key_characteristics'].get('product_preference', s['key_characteristics'].get('main_activity', '')),
                '核心需求': s['key_characteristics'].get('core_need', s['key_characteristics'].get('kyc_status', '')),
                '营销策略重点': '; '.join(s['marketing_strategy'][:2]),
                '转化策略': '; '.join(s['conversion_tactics'][:2]) if s['conversion_tactics'] else '',
                '价格策略': '; '.join(s['pricing_strategy'][:2]) if s['pricing_strategy'] else '',
            })
        
        df = pd.DataFrame(csv_data)
        csv_file = output_dir / 'business_driven_insights_summary.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"CSV摘要已保存到: {csv_file}")
        
        # 生成Markdown报告
        self.generate_markdown_report(strategies, output_dir / 'business_driven_report.md')
    
    def generate_markdown_report(self, strategies, output_file):
        """生成Markdown报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 基于业务驱动的用户画像与营销策略报告\n\n")
            f.write("本报告基于业务维度聚类结果，为每个聚类生成差异化的营销策略。\n\n")
            f.write("---\n\n")
            
            for strategy in strategies:
                f.write(f"## 聚类 {strategy['cluster_id']}: {strategy['cluster_name']}\n\n")
                f.write(f"**完整标签**: {strategy['full_label']}\n\n")
                
                f.write("### 关键特征\n\n")
                chars = strategy['key_characteristics']
                f.write(f"- 用户数: {chars['user_count']} 个独立用户\n")
                f.write(f"- 片段数: {chars['segment_count']} 个意图片段\n")
                f.write(f"- 平均浏览时长: {chars['avg_duration_minutes']:.2f} 分钟\n")
                f.write(f"- 平均交互次数: {chars['avg_interactions']:.2f} 次\n")
                f.write(f"- 平均意图强度: {chars['avg_intent_score']:.2f}\n")
                # 根据是否为金融场景显示不同特征
                if 'kyc_status' in chars:
                    f.write(f"- 行为模式: {chars.get('behavior', '')}\n")
                    f.write(f"- 紧迫度: {chars.get('urgency', '')}\n")
                    f.write(f"- 主要活动: {chars.get('main_activity', '')}\n")
                    f.write(f"- KYC状态: {chars.get('kyc_status', '')}\n")
                    f.write(f"- 交易状态: {chars.get('transaction_status', '')}\n")
                else:
                    f.write(f"- 购买阶段: {chars.get('stage', '')}\n")
                    f.write(f"- 价格敏感度: {chars.get('price_sensitivity', '')}\n")
                    f.write(f"- 参与度: {chars.get('engagement_level', '')}\n")
                    f.write(f"- 产品偏好: {chars.get('product_preference', '')}\n")
                    f.write(f"- 关注点: {chars.get('concern_focus', '')}\n")
                    f.write(f"- 核心需求: {chars.get('core_need', '')}\n")
                f.write("\n")
                
                f.write("### 营销策略\n\n")
                for item in strategy['marketing_strategy']:
                    f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("### 内容策略\n\n")
                for item in strategy['content_strategy']:
                    f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("### 转化策略\n\n")
                for item in strategy['conversion_tactics']:
                    f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("### 价格策略\n\n")
                for item in strategy['pricing_strategy']:
                    f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("### 产品推荐\n\n")
                for item in strategy['product_recommendation']:
                    f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("### 差异化营销活动\n\n")
                for item in strategy['campaign_differentiation']:
                    f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("---\n\n")
        
        print(f"Markdown报告已保存到: {output_file}")

if __name__ == '__main__':
    analyzer = BusinessDrivenPortraitAnalyzer()
    strategies = analyzer.analyze_all_clusters()
    analyzer.save_results(strategies)

