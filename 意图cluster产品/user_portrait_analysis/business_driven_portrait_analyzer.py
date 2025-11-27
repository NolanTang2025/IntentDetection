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
                'transaction_status': transaction_status
            },
            'marketing_strategy': [],
            'content_strategy': [],
            'conversion_tactics': [],
            'pricing_strategy': [],
            'product_recommendation': [],
            'campaign_differentiation': []
        }
        
        # 基于交易状态的策略（更详细的策略）
        if transaction_status == '已完成':
            strategy['marketing_strategy'].append("【交易完成用户】用户已完成交易，需要提升活跃度和复购")
            strategy['marketing_strategy'].append("提供新功能推荐、优惠活动、会员权益")
            strategy['marketing_strategy'].append("建立用户忠诚度计划，通过积分、等级、专属权益提升用户粘性")
            strategy['marketing_strategy'].append("定期推送个性化内容，包括新功能介绍、使用技巧、优惠信息")
            strategy['conversion_tactics'].append("推送个性化推荐、限时优惠、积分奖励")
            strategy['conversion_tactics'].append("引导用户探索更多功能、参与活动")
            strategy['conversion_tactics'].append("设置复购提醒，在合适时机推送相关优惠和活动")
            strategy['conversion_tactics'].append("提供会员专享通道，优先处理会员请求，提升服务体验")
        elif transaction_status == '进行中':
            strategy['marketing_strategy'].append("【交易进行中】用户正在完成交易，需要协助完成流程")
            strategy['marketing_strategy'].append("简化交易流程、提供客服支持、解决支付问题")
            strategy['marketing_strategy'].append("实时监控交易状态，主动识别并解决卡点问题")
            strategy['marketing_strategy'].append("提供多渠道客服支持（在线客服、电话、邮件），确保用户能及时获得帮助")
            strategy['conversion_tactics'].append("优化支付页面，减少支付步骤，提供多种支付方式（银行卡、第三方支付、数字钱包）")
            strategy['conversion_tactics'].append("发送交易提醒，包括交易进度、待办事项、异常提醒")
            strategy['conversion_tactics'].append("提供交易帮助中心，包含常见问题、操作指南、故障排除")
            strategy['conversion_tactics'].append("设置交易超时提醒，防止用户因等待时间过长而放弃")
        else:  # 未开始
            strategy['marketing_strategy'].append("【潜在用户】用户尚未开始交易，需要引导完成首次交易")
            strategy['marketing_strategy'].append("提供新用户优惠、首次交易奖励、使用指南")
            strategy['marketing_strategy'].append("降低首次交易门槛，提供新手专享优惠、免手续费、快速通道")
            strategy['marketing_strategy'].append("建立信任机制，展示平台安全性、用户评价、成功案例")
            strategy['conversion_tactics'].append("突出首次交易优惠，在首页、注册页、引导页显著展示")
            strategy['conversion_tactics'].append("简化注册流程，减少必填项，支持一键注册、第三方账号登录")
            strategy['conversion_tactics'].append("提供新手引导，包括产品介绍、操作演示、常见问题")
            strategy['conversion_tactics'].append("设置新手任务系统，完成指定任务可获得奖励，提升用户参与度")
        
        # 基于KYC状态的策略（更详细的策略）
        if kyc_status == '已开始':
            strategy['marketing_strategy'].append("【KYC进行中】用户正在完成身份验证，需要协助完成KYC")
            strategy['marketing_strategy'].append("主动识别KYC卡点，提供针对性帮助和指导")
            strategy['content_strategy'].append("提供KYC流程说明，包括步骤详解、所需材料、注意事项")
            strategy['content_strategy'].append("建立KYC常见问题库，覆盖常见错误、审核失败原因、解决方案")
            strategy['content_strategy'].append("提供客服支持，设置KYC专属客服通道，快速响应问题")
            strategy['conversion_tactics'].append("优化KYC流程，支持多种验证方式（人脸识别、身份证OCR、人工审核）")
            strategy['conversion_tactics'].append("发送KYC进度提醒，包括当前步骤、待办事项、预计完成时间")
            strategy['conversion_tactics'].append("提供帮助文档，包括操作视频、图文教程、故障排除指南")
            strategy['conversion_tactics'].append("设置KYC完成奖励，激励用户尽快完成验证")
        elif kyc_status == '未开始':
            if transaction_status == '未开始':
                strategy['marketing_strategy'].append("【引导KYC】用户尚未开始KYC，需要引导完成身份验证")
                strategy['marketing_strategy'].append("说明KYC的重要性，包括账户安全、功能解锁、交易限制等")
                strategy['content_strategy'].append("说明KYC的重要性、安全性和便捷性")
                strategy['content_strategy'].append("展示KYC完成后的权益，包括更高额度、更多功能、专属服务")
                strategy['content_strategy'].append("提供KYC流程预览，让用户了解所需时间和步骤")
                strategy['conversion_tactics'].append("突出KYC奖励，包括完成KYC送优惠券、积分、专属权益")
                strategy['conversion_tactics'].append("简化KYC流程，减少必填项，支持自动识别、一键提交")
                strategy['conversion_tactics'].append("提供KYC引导，包括操作提示、材料准备、注意事项")
                strategy['conversion_tactics'].append("提供视频教程，展示KYC操作流程，降低用户操作难度")
        
        # 基于主要活动的策略（更详细的策略）
        if main_activity == '支付导向':
            strategy['product_recommendation'].append("【支付功能】用户关注支付功能，重点推荐支付相关服务和优惠")
            strategy['product_recommendation'].append("推荐支付相关功能，包括快捷支付、分期付款、支付安全保障")
            strategy['product_recommendation'].append("提供支付优惠活动，包括支付返现、支付折扣、支付积分")
            strategy['content_strategy'].append("提供支付教程，包括支付方式介绍、操作步骤、注意事项")
            strategy['content_strategy'].append("说明支付安全机制，包括加密技术、风控体系、资金保障")
            strategy['content_strategy'].append("展示支付优惠信息，包括限时活动、会员专享、新用户福利")
        elif main_activity == '充值导向':
            strategy['product_recommendation'].append("【充值功能】用户关注充值功能，重点推荐充值相关服务和优惠")
            strategy['product_recommendation'].append("推荐充值优惠，包括充值返现、充值折扣、充值奖励")
            strategy['product_recommendation'].append("提供多种充值方式，包括银行卡、第三方支付、数字钱包")
            strategy['content_strategy'].append("提供充值教程，包括充值方式介绍、操作步骤、到账时间")
            strategy['content_strategy'].append("展示充值优惠活动，包括限时活动、会员专享、新用户福利")
            strategy['content_strategy'].append("说明充值安全保障，包括资金安全、到账保障、异常处理")
        elif main_activity == '优惠券导向':
            strategy['product_recommendation'].append("【优惠券功能】用户关注优惠券，重点推荐优惠券相关服务和活动")
            strategy['product_recommendation'].append("推荐优惠券活动，包括新用户专享、限时抢购、会员专享")
            strategy['product_recommendation'].append("提供优惠券使用指南，包括使用规则、适用范围、有效期说明")
            strategy['product_recommendation'].append("展示优惠券奖励机制，包括领取方式、使用技巧、叠加规则")
            strategy['content_strategy'].append("提供优惠券说明，包括优惠券类型、使用条件、注意事项")
            strategy['content_strategy'].append("展示优惠券活动，包括活动时间、参与方式、奖励内容")
            strategy['content_strategy'].append("提供优惠券使用技巧，包括最佳使用时机、叠加策略、省钱攻略")
        
        # 基于紧迫度的策略（更详细的策略）
        if urgency == '高紧迫':
            strategy['conversion_tactics'].append("【高优先级】用户意图强烈，需要立即转化")
            strategy['conversion_tactics'].append("提供限时优惠，包括倒计时提醒、库存告急、早鸟优惠")
            strategy['conversion_tactics'].append("设置快速通道，包括VIP通道、专属客服、优先处理")
            strategy['conversion_tactics'].append("提供专属客服，包括在线客服、电话客服、专属顾问")
        elif urgency == '低紧迫':
            strategy['marketing_strategy'].append("【培育用户】用户意图较低，需要长期培育")
            strategy['marketing_strategy'].append("建立内容营销体系，定期推送教育性内容、使用案例、功能介绍")
            strategy['content_strategy'].append("提供教育性内容，包括产品介绍、使用指南、行业资讯")
            strategy['content_strategy'].append("展示使用案例，包括成功案例、用户故事、效果展示")
            strategy['content_strategy'].append("介绍产品功能，包括核心功能、特色功能、创新点")
        
        # 基于行为模式的策略（更详细的策略）
        if behavior == '已完成交易':
            strategy['campaign_differentiation'].append("【复购活动】'推荐新功能'、'会员专享'、'积分兑换'")
            strategy['campaign_differentiation'].append("【活跃度提升】'每日签到'、'任务奖励'、'社区活动'")
            strategy['campaign_differentiation'].append("【忠诚度计划】'会员等级'、'积分商城'、'专属权益'")
            strategy['campaign_differentiation'].append("【社交互动】'用户社区'、'分享奖励'、'邀请好友'")
        elif behavior == 'KYC进行中':
            strategy['campaign_differentiation'].append("【KYC完成奖励】'完成KYC送优惠券'、'KYC快速通道'")
            strategy['campaign_differentiation'].append("【协助完成】'KYC帮助中心'、'在线客服'、'视频教程'")
            strategy['campaign_differentiation'].append("【进度提醒】'KYC进度推送'、'待办提醒'、'完成通知'")
        elif behavior == '探索阶段':
            strategy['campaign_differentiation'].append("【新用户活动】'新用户注册奖励'、'首次交易优惠'")
            strategy['campaign_differentiation'].append("【引导活动】'功能探索'、'使用指南'、'新手任务'")
            strategy['campaign_differentiation'].append("【信任建立】'安全保障'、'用户评价'、'成功案例'")
            strategy['campaign_differentiation'].append("【降低门槛】'免手续费'、'快速通道'、'专属优惠'")
        
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

