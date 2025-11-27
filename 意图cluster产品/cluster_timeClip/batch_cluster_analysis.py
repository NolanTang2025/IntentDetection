#!/usr/bin/env python3
"""
批量处理多个店铺的聚类分析
为每个店铺生成聚类结果、业务洞察和前端数据
"""

import json
import subprocess
import sys
from pathlib import Path
import shutil

# 店铺列表
SHOPS = [28, 29, 39, 49, 53]

def run_clustering_for_shop(shop_id):
    """为指定店铺运行聚类分析"""
    print(f"\n{'='*80}")
    print(f"正在处理店铺 {shop_id}")
    print(f"{'='*80}")
    
    # 输入文件路径
    input_file = f'../data_extract/extracted_data_shop_{shop_id}.json'
    
    # 检查文件是否存在
    if not Path(input_file).exists():
        print(f"❌ 错误: 找不到文件 {input_file}")
        return False
    
    # 导入聚类分析类
    sys.path.insert(0, str(Path(__file__).parent))
    from behavior_intent_clustering import BehaviorIntentClusterer
    
    # 创建聚类分析器
    clusterer = BehaviorIntentClusterer(intent_change_threshold=0.3)
    
    # 运行分析
    try:
        clusterer.analyze(input_file=input_file)
        
        # 重命名输出文件，添加店铺ID
        output_files = {
            'business_cluster_results.json': f'business_cluster_results_shop_{shop_id}.json',
            'business_cluster_results.csv': f'business_cluster_results_shop_{shop_id}.csv'
        }
        
        for old_name, new_name in output_files.items():
            old_path = Path(old_name)
            new_path = Path(new_name)
            if old_path.exists():
                shutil.move(str(old_path), str(new_path))
                print(f"✅ 结果已保存: {new_name}")
        
        return True
    except Exception as e:
        print(f"❌ 聚类分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_portrait_analysis_for_shop(shop_id):
    """为指定店铺运行用户画像分析"""
    print(f"\n正在为店铺 {shop_id} 生成业务洞察...")
    
    # 切换到用户画像分析目录
    portrait_dir = Path(__file__).parent.parent / 'user_portrait_analysis'
    cluster_file = f'../cluster_timeClip/business_cluster_results_shop_{shop_id}.json'
    
    cluster_result_file = Path(__file__).parent / f'business_cluster_results_shop_{shop_id}.json'
    if not cluster_result_file.exists():
        print(f"❌ 错误: 找不到聚类结果文件 {cluster_result_file}")
        return False
    
    # 导入用户画像分析类
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "business_driven_portrait_analyzer",
        portrait_dir / 'business_driven_portrait_analyzer.py'
    )
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(portrait_dir))
    spec.loader.exec_module(module)
    BusinessDrivenPortraitAnalyzer = module.BusinessDrivenPortraitAnalyzer
    
    # 创建分析器，指定聚类结果文件
    analyzer = BusinessDrivenPortraitAnalyzer(
        cluster_results_file=cluster_file
    )
    
    try:
        strategies = analyzer.analyze_all_clusters()
        analyzer.save_results(strategies)
        
        # 重命名输出文件，添加店铺ID
        output_files = {
            'business_driven_insights.json': f'business_driven_insights_shop_{shop_id}.json',
            'business_driven_insights_summary.csv': f'business_driven_insights_summary_shop_{shop_id}.csv',
            'business_driven_report.md': f'business_driven_report_shop_{shop_id}.md'
        }
        
        for old_name, new_name in output_files.items():
            old_path = portrait_dir / old_name
            new_path = portrait_dir / new_name
            if old_path.exists():
                shutil.move(str(old_path), str(new_path))
                print(f"✅ 业务洞察已保存: {new_path}")
        
        return True
    except Exception as e:
        print(f"❌ 用户画像分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_frontend_data_for_shop(shop_id):
    """为指定店铺更新前端数据"""
    print(f"\n正在为店铺 {shop_id} 更新前端数据...")
    
    # 修改update_data.py的路径引用
    # 这里需要临时修改或创建一个适配脚本
    # 为了简化，我们直接修改update_data.py的路径
    
    update_script = Path(__file__).parent.parent / 'visualization_dashboard' / 'update_data.py'
    
    if not update_script.exists():
        print(f"❌ 错误: 找不到更新脚本 {update_script}")
        return False
    
    # 读取update_data.py
    with open(update_script, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 临时修改路径
    original_cluster_path = "../cluster_timeClip/business_cluster_results.json"
    new_cluster_path = f"../cluster_timeClip/business_cluster_results_shop_{shop_id}.json"
    
    original_insights_path = "../user_portrait_analysis/business_driven_insights.json"
    new_insights_path = f"../user_portrait_analysis/business_driven_insights_shop_{shop_id}.json"
    
    # 替换路径
    modified_content = content.replace(original_cluster_path, new_cluster_path)
    modified_content = modified_content.replace(original_insights_path, new_insights_path)
    
    # 创建临时文件
    temp_script = update_script.parent / f'update_data_shop_{shop_id}.py'
    with open(temp_script, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    try:
        # 运行更新脚本
        result = subprocess.run(
            ['python3', str(temp_script)],
            cwd=str(update_script.parent),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # 重命名输出文件
            data_js = update_script.parent / 'data.js'
            data_js_shop = update_script.parent / f'data_shop_{shop_id}.js'
            if data_js.exists():
                shutil.move(str(data_js), str(data_js_shop))
                print(f"✅ 前端数据已保存: data_shop_{shop_id}.js")
            
            # 清理临时脚本
            temp_script.unlink()
            return True
        else:
            print(f"❌ 更新前端数据失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 更新前端数据失败: {e}")
        if temp_script.exists():
            temp_script.unlink()
        return False

def main():
    """主函数：批量处理所有店铺"""
    print("="*80)
    print("批量店铺聚类分析")
    print("="*80)
    
    results = {}
    
    for shop_id in SHOPS:
        print(f"\n\n{'#'*80}")
        print(f"处理店铺 {shop_id}")
        print(f"{'#'*80}")
        
        # 1. 聚类分析
        clustering_success = run_clustering_for_shop(shop_id)
        
        if not clustering_success:
            results[shop_id] = {'status': 'failed', 'step': 'clustering'}
            continue
        
        # 2. 用户画像分析
        portrait_success = run_portrait_analysis_for_shop(shop_id)
        
        if not portrait_success:
            results[shop_id] = {'status': 'partial', 'step': 'portrait'}
            continue
        
        # 3. 更新前端数据
        frontend_success = update_frontend_data_for_shop(shop_id)
        
        if frontend_success:
            results[shop_id] = {'status': 'success'}
        else:
            results[shop_id] = {'status': 'partial', 'step': 'frontend'}
    
    # 打印总结
    print(f"\n\n{'='*80}")
    print("批量处理完成")
    print(f"{'='*80}")
    
    for shop_id, result in results.items():
        status = result['status']
        if status == 'success':
            print(f"✅ 店铺 {shop_id}: 完成")
        elif status == 'partial':
            print(f"⚠️  店铺 {shop_id}: 部分完成 (失败步骤: {result.get('step', 'unknown')})")
        else:
            print(f"❌ 店铺 {shop_id}: 失败 (失败步骤: {result.get('step', 'unknown')})")
    
    # 生成合并的前端数据（可选）
    print(f"\n是否生成合并所有店铺的前端数据？")
    print("提示: 可以创建一个支持多店铺切换的前端页面")

if __name__ == '__main__':
    main()

