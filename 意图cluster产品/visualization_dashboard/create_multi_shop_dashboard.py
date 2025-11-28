#!/usr/bin/env python3
"""
创建多店铺前端展示页面
支持在不同店铺之间切换查看数据
"""

import json
from pathlib import Path
from collections import defaultdict

SHOPS = [28, 29, 39, 49, 53, 'YUP']

def load_shop_data(shop_id):
    """加载指定店铺的数据"""
    base_dir = Path(__file__).parent
    
    # 加载聚类结果
    cluster_file = base_dir.parent / 'cluster_timeClip' / f'business_cluster_results_shop_{shop_id}.json'
    if not cluster_file.exists():
        return None
    
    with open(cluster_file, 'r', encoding='utf-8') as f:
        cluster_data = json.load(f)
    
    # 加载业务洞察
    insights_file = base_dir.parent / 'user_portrait_analysis' / f'business_driven_insights_shop_{shop_id}.json'
    insights_data = []
    if insights_file.exists():
        with open(insights_file, 'r', encoding='utf-8') as f:
            insights_data = json.load(f)
    
    return {
        'cluster_data': cluster_data,
        'insights_data': insights_data,
        'shop_id': shop_id
    }

def create_multi_shop_data():
    """创建多店铺数据文件"""
    print("正在加载所有店铺数据...")
    
    all_shops_data = {}
    shop_stats = {}
    
    for shop_id in SHOPS:
        print(f"  加载店铺 {shop_id}...")
        shop_data = load_shop_data(shop_id)
        if shop_data:
            all_shops_data[shop_id] = shop_data
            
            # 计算统计信息
            segments = shop_data['cluster_data'].get('segments', [])
            total_users = len(set(s.get('user_id') for s in segments))
            total_segments = len(segments)
            total_clusters = len(set(s.get('business_cluster') for s in segments))
            
            shop_stats[shop_id] = {
                'total_users': total_users,
                'total_segments': total_segments,
                'total_clusters': total_clusters,
                'has_insights': len(shop_data['insights_data']) > 0
            }
        else:
            print(f"  ⚠️  店铺 {shop_id} 数据不存在")
    
    # 生成汇总数据
    summary = {
        'total_shops': len(all_shops_data),
        'shops': list(all_shops_data.keys()),
        'shop_stats': shop_stats,
        'total_users_all_shops': sum(s['total_users'] for s in shop_stats.values()),
        'total_segments_all_shops': sum(s['total_segments'] for s in shop_stats.values())
    }
    
    return all_shops_data, summary

def generate_multi_shop_js(all_shops_data, summary):
    """生成多店铺JavaScript数据文件"""
    output_file = Path(__file__).parent / 'multi_shop_data.js'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('// 多店铺聚类分析数据\n')
        f.write('// 自动生成，请勿手动编辑\n\n')
        
        f.write('// 店铺汇总信息\n')
        f.write('const shopSummary = ')
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write(';\n\n')
        
        f.write('// 各店铺数据\n')
        f.write('const shopData = {};\n\n')
        
        for shop_id, shop_data in all_shops_data.items():
            f.write(f'// 店铺 {shop_id} 数据\n')
            # 如果shop_id是字符串，需要加引号；如果是数字，直接使用
            if isinstance(shop_id, str):
                f.write(f'shopData["{shop_id}"] = ')
            else:
            f.write(f'shopData[{shop_id}] = ')
            
            # 准备店铺数据（类似单店铺的data.js格式）
            from update_data import convert_to_dashboard_format
            # 在cluster_data中添加shop_id，以便词云生成时使用
            cluster_data_with_shop = shop_data['cluster_data'].copy()
            cluster_data_with_shop['shop_id'] = shop_id
            dashboard_data = convert_to_dashboard_format(
                cluster_data_with_shop,
                shop_data['insights_data']
            )
            
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            f.write(';\n\n')
        
        f.write('// 数据加载完成\n')
        f.write('console.log("多店铺数据加载完成:", shopSummary);\n')
    
    print(f"✅ 多店铺数据文件已生成: {output_file}")
    return output_file

def main():
    """主函数"""
    print("="*80)
    print("创建多店铺前端展示")
    print("="*80)
    
    # 加载所有店铺数据
    all_shops_data, summary = create_multi_shop_data()
    
    if not all_shops_data:
        print("❌ 没有找到任何店铺数据")
        return
    
    print(f"\n找到 {len(all_shops_data)} 个店铺的数据:")
    for shop_id, stats in summary['shop_stats'].items():
        print(f"  店铺 {shop_id}: {stats['total_users']} 用户, {stats['total_segments']} 片段, {stats['total_clusters']} 聚类")
    
    # 生成多店铺数据文件
    print("\n正在生成多店铺数据文件...")
    generate_multi_shop_js(all_shops_data, summary)
    
    print("\n✅ 完成!")
    print("\n提示: 可以创建一个支持店铺切换的前端页面来展示这些数据")

if __name__ == '__main__':
    main()

