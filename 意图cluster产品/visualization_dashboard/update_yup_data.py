#!/usr/bin/env python3
"""
为YUP店铺生成data_shop_YUP.js文件
"""

import json
import sys
from pathlib import Path

# 导入update_data.py中的函数
sys.path.insert(0, str(Path(__file__).parent))
from update_data import convert_to_dashboard_format

def generate_yup_data_js():
    """为YUP生成data_shop_YUP.js文件"""
    base_dir = Path(__file__).parent
    parent_dir = base_dir.parent
    
    # 加载聚类结果
    cluster_file = parent_dir / 'cluster_timeClip' / 'business_cluster_results_shop_YUP.json'
    if not cluster_file.exists():
        print(f"❌ 错误: 找不到聚类结果文件 {cluster_file}")
        return False
    
    with open(cluster_file, 'r', encoding='utf-8') as f:
        cluster_data = json.load(f)
    
    # 添加shop_id
    cluster_data['shop_id'] = 'YUP'
    
    # 加载业务洞察
    insights_file = parent_dir / 'user_portrait_analysis' / 'business_driven_insights_shop_YUP.json'
    if not insights_file.exists():
        print(f"❌ 错误: 找不到业务洞察文件 {insights_file}")
        return False
    
    with open(insights_file, 'r', encoding='utf-8') as f:
        insights_data = json.load(f)
    
    print(f"✅ 已加载YUP数据:")
    print(f"   - 聚类结果: {len(cluster_data.get('segments', []))} 个片段")
    print(f"   - 业务洞察: {len(insights_data)} 个聚类")
    
    # 转换为仪表板格式
    print("\n正在转换数据格式...")
    dashboard_data = convert_to_dashboard_format(cluster_data, insights_data)
    
    # 生成data_shop_YUP.js文件
    output_file = base_dir / 'data_shop_YUP.js'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('// 用户意图分析数据\n')
        f.write('// 自动生成，请勿手动编辑\n\n')
        
        # 业务洞察数据
        f.write('// 业务洞察数据\n')
        f.write('const businessInsights = ')
        json.dump(dashboard_data['businessInsights'], f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        # 用户画像数据
        f.write('// 用户画像数据\n')
        f.write('const userPortraits = ')
        json.dump(dashboard_data['userPortraits'], f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        # 统计数据
        f.write('// 统计数据\n')
        f.write('const stats = ')
        json.dump(dashboard_data['stats'], f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        # 时间序列数据
        f.write('// 时间序列数据\n')
        f.write('const timeSeries = ')
        json.dump(dashboard_data['timeSeries'], f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        # 用户轨迹数据
        f.write('// 用户轨迹数据\n')
        f.write('const userTrajectories = ')
        json.dump(dashboard_data['userTrajectories'], f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        f.write('// 数据加载完成\n')
        f.write('console.log("YUP数据加载完成:", stats);\n')
    
    print(f"\n✅ data_shop_YUP.js文件已生成: {output_file}")
    print(f"   - 业务洞察: {len(dashboard_data['businessInsights'])} 个聚类")
    print(f"   - 用户画像: {len(dashboard_data['userPortraits'])} 个聚类")
    print(f"   - 总用户数: {dashboard_data['stats']['totalUsers']}")
    print(f"   - 总片段数: {dashboard_data['stats']['totalSegments']}")
    print(f"   - 用户轨迹: {len(dashboard_data.get('userTrajectories', []))} 个用户")
    
    return True

if __name__ == '__main__':
    print("="*80)
    print("为YUP店铺生成data_shop_YUP.js文件")
    print("="*80)
    print()
    
    success = generate_yup_data_js()
    
    if success:
        print("\n✅ 完成!")
    else:
        print("\n❌ 生成失败!")
        sys.exit(1)

