#!/usr/bin/env python3
"""
修复 shop 28 数据格式：将 key_characteristics 从对象转换为数组格式
"""

import json
import re
from pathlib import Path

def convert_key_characteristics_to_array(kc_obj):
    """将 key_characteristics 对象转换为数组格式"""
    if isinstance(kc_obj, list):
        return kc_obj  # 已经是数组格式
    
    if not isinstance(kc_obj, dict):
        return []
    
    array = []
    
    # 用户规模
    user_count = kc_obj.get('user_count', 0)
    segment_count = kc_obj.get('segment_count', 0)
    if user_count > 0 or segment_count > 0:
        array.append(f"用户规模: {user_count} 个独立用户，{segment_count} 个意图片段")
    
    # 平均浏览时长
    avg_duration = kc_obj.get('avg_duration_minutes', 0)
    if avg_duration > 0:
        if avg_duration < 1:
            array.append(f"平均浏览时长: 瞬时浏览（单次交互）")
        else:
            array.append(f"平均浏览时长: {avg_duration:.2f} 分钟")
    else:
        array.append(f"平均浏览时长: 瞬时浏览（单次交互）")
    
    # 平均交互次数
    avg_interactions = kc_obj.get('avg_interactions', 0)
    if avg_interactions > 0:
        array.append(f"平均交互次数: {avg_interactions:.1f} 次")
    else:
        array.append(f"平均交互次数: 1.0 次")
    
    # 平均意图强度
    avg_intent_score = kc_obj.get('avg_intent_score', 0.5)
    array.append(f"平均意图强度: {avg_intent_score:.2f}")
    
    # 购买阶段 - 从 intent_profile 或直接获取
    purchase_stage = kc_obj.get('purchase_stage')
    if not purchase_stage:
        # 尝试从其他字段推断
        behavior = kc_obj.get('behavior', '')
        if '探索' in behavior or '浏览' in behavior:
            purchase_stage = '浏览阶段'
        elif '对比' in behavior:
            purchase_stage = '对比阶段'
        elif '决策' in behavior or '完成' in behavior:
            purchase_stage = '决策阶段'
        else:
            purchase_stage = '浏览阶段'  # 默认
    array.append(f"购买阶段: {purchase_stage}")
    
    # 价格敏感度
    price_sensitivity = kc_obj.get('price_sensitivity')
    if not price_sensitivity:
        # 从 intent_profile 获取
        price_sensitivity = '高端价值型'  # 默认
    array.append(f"价格敏感度: {price_sensitivity}")
    
    # 关注点
    concern_focus = kc_obj.get('concern_focus')
    if not concern_focus:
        concern_focus = '综合关注'  # 默认
    array.append(f"关注点: {concern_focus}")
    
    # 行为
    behavior = kc_obj.get('behavior', '')
    if behavior:
        array.append(f"行为: {behavior}")
    
    # 紧迫度
    urgency = kc_obj.get('urgency', '')
    if urgency:
        array.append(f"紧迫度: {urgency}")
    
    # 主要活动
    main_activity = kc_obj.get('main_activity', '')
    if main_activity:
        array.append(f"主要活动: {main_activity}")
    
    # KYC状态
    kyc_status = kc_obj.get('kyc_status', '')
    if kyc_status:
        array.append(f"KYC状态: {kyc_status}")
    
    # 交易状态
    transaction_status = kc_obj.get('transaction_status', '')
    if transaction_status:
        array.append(f"交易状态: {transaction_status}")
    
    return array

def fix_shop28_data():
    """修复 shop 28 数据格式"""
    base_dir = Path(__file__).parent
    data_file = base_dir / 'data_shop_28.js'
    
    if not data_file.exists():
        print(f"❌ 错误: 找不到文件 {data_file}")
        return False
    
    print(f"📖 读取文件: {data_file}")
    
    # 读取文件内容
    with open(data_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 businessInsights
    match = re.search(r'const businessInsights = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("❌ 错误: 无法找到 businessInsights 数据")
        return False
    
    insights_str = match.group(1)
    insights = json.loads(insights_str)
    
    print(f"✅ 找到 {len(insights)} 个聚类")
    
    # 转换每个聚类的 key_characteristics
    updated_count = 0
    for insight in insights:
        kc = insight.get('key_characteristics', {})
        if isinstance(kc, dict):
            # 转换为数组格式
            insight['key_characteristics'] = convert_key_characteristics_to_array(kc)
            updated_count += 1
            print(f"  ✓ 聚类 {insight['cluster_id']}: 已转换 key_characteristics")
    
    if updated_count == 0:
        print("ℹ️  所有聚类的 key_characteristics 已经是数组格式")
        return True
    
    # 重新生成文件内容
    new_insights_str = json.dumps(insights, indent=2, ensure_ascii=False)
    
    # 替换原内容
    new_content = content.replace(
        f'const businessInsights = {insights_str};',
        f'const businessInsights = {new_insights_str};'
    )
    
    # 备份原文件
    backup_file = data_file.with_suffix('.js.bak')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 已备份原文件到: {backup_file}")
    
    # 写入新内容
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已更新文件: {data_file}")
    print(f"📊 已转换 {updated_count} 个聚类的数据格式")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("修复 Shop 28 数据格式")
    print("=" * 60)
    fix_shop28_data()
    print("=" * 60)

