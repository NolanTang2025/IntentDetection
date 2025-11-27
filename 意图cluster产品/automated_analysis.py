#!/usr/bin/env python3
"""
完整的自动化分析脚本
为每个店铺执行：
1. 数据提取（如果需要）
2. 聚类分析
3. 聚类结果分析
4. 用户画像分析
5. 业务洞察生成
6. 前端数据更新
7. 多店铺数据合并
"""

import json
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
import traceback

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    # 加载.env文件（从项目根目录）
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✅ 已加载.env文件: {env_path}")
    else:
        # 也尝试从当前目录加载
        load_dotenv(override=True)
except ImportError:
    # 如果没有安装python-dotenv，仍然可以从环境变量读取
    print("⚠️  python-dotenv 未安装，将仅从环境变量读取API密钥")

# 配置
SHOPS = [28, 29, 39, 49, 53, 'YUP']
BASE_DIR = Path(__file__).parent
DATA_EXTRACT_DIR = BASE_DIR / 'data_extract'
CLUSTER_DIR = BASE_DIR / 'cluster_timeClip'
PORTRAIT_DIR = BASE_DIR / 'user_portrait_analysis'
DASHBOARD_DIR = BASE_DIR / 'visualization_dashboard'

class AutomatedAnalyzer:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        
    def log(self, message, level='INFO'):
        """日志输出"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        prefix = {
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'ERROR': '❌',
            'WARNING': '⚠️'
        }.get(level, 'ℹ️')
        print(f"[{timestamp}] {prefix} {message}")
    
    def step1_extract_data(self, shop_id):
        """步骤1: 数据提取（如果需要）"""
        self.log(f"店铺 {shop_id}: 检查数据文件...")
        
        extracted_file = DATA_EXTRACT_DIR / f'extracted_data_shop_{shop_id}.json'
        
        if extracted_file.exists():
            with open(extracted_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.log(f"店铺 {shop_id}: 数据文件已存在，包含 {len(data)} 条记录", 'SUCCESS')
            return True
        else:
            self.log(f"店铺 {shop_id}: 数据文件不存在，请先运行数据提取", 'WARNING')
            return False
    
    def step2_clustering(self, shop_id):
        """步骤2: 聚类分析"""
        self.log(f"店铺 {shop_id}: 开始聚类分析...")
        
        input_file = DATA_EXTRACT_DIR / f'extracted_data_shop_{shop_id}.json'
        
        if not input_file.exists():
            self.log(f"店铺 {shop_id}: 数据文件不存在，跳过", 'ERROR')
            return False
        
        try:
            # 导入聚类分析类
            sys.path.insert(0, str(CLUSTER_DIR))
            from behavior_intent_clustering import BehaviorIntentClusterer
            
            # 获取Gemini API密钥（如果店铺39需要）
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            
            # 创建聚类分析器
            clusterer = BehaviorIntentClusterer(
                intent_change_threshold=0.3,
                gemini_api_key=gemini_api_key
            )
            
            # 运行分析（传递shop_id，店铺39会使用Gemini embedding）
            clusterer.analyze(input_file=str(input_file), shop_id=shop_id)
            
            # 重命名输出文件
            output_files = {
                'business_cluster_results.json': f'business_cluster_results_shop_{shop_id}.json',
                'business_cluster_results.csv': f'business_cluster_results_shop_{shop_id}.csv'
            }
            
            for old_name, new_name in output_files.items():
                old_path = CLUSTER_DIR / old_name
                new_path = CLUSTER_DIR / new_name
                if old_path.exists():
                    shutil.move(str(old_path), str(new_path))
                    self.log(f"店铺 {shop_id}: 聚类结果已保存 - {new_name}", 'SUCCESS')
            
            return True
            
        except Exception as e:
            self.log(f"店铺 {shop_id}: 聚类分析失败 - {str(e)}", 'ERROR')
            traceback.print_exc()
            return False
    
    def step3_cluster_analysis(self, shop_id):
        """步骤3: 聚类结果分析（统计和可视化）"""
        self.log(f"店铺 {shop_id}: 开始聚类结果分析...")
        
        cluster_file = CLUSTER_DIR / f'business_cluster_results_shop_{shop_id}.json'
        
        if not cluster_file.exists():
            self.log(f"店铺 {shop_id}: 聚类结果文件不存在，跳过", 'WARNING')
            return False
        
        try:
            # 加载聚类结果
            with open(cluster_file, 'r', encoding='utf-8') as f:
                cluster_data = json.load(f)
            
            segments = cluster_data.get('segments', [])
            clustering = cluster_data.get('clustering', {})
            
            # 计算统计信息
            total_segments = len(segments)
            total_users = len(set(s.get('user_id') for s in segments))
            n_clusters = clustering.get('n_clusters', 0)
            
            # 生成分析报告
            analysis_report = {
                'shop_id': shop_id,
                'analysis_date': datetime.now().isoformat(),
                'statistics': {
                    'total_segments': total_segments,
                    'total_users': total_users,
                    'n_clusters': n_clusters,
                    'avg_segments_per_user': round(total_segments / total_users, 2) if total_users > 0 else 0
                },
                'cluster_distribution': clustering.get('cluster_counts', {}),
                'cluster_labels': clustering.get('cluster_labels', {})
            }
            
            # 保存分析报告
            report_file = CLUSTER_DIR / f'cluster_analysis_shop_{shop_id}.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_report, f, indent=2, ensure_ascii=False)
            
            self.log(f"店铺 {shop_id}: 聚类分析完成 - {total_segments} 片段, {total_users} 用户, {n_clusters} 聚类", 'SUCCESS')
            return True
            
        except Exception as e:
            self.log(f"店铺 {shop_id}: 聚类结果分析失败 - {str(e)}", 'ERROR')
            traceback.print_exc()
            return False
    
    def step4_portrait_analysis(self, shop_id):
        """步骤4: 用户画像分析"""
        self.log(f"店铺 {shop_id}: 开始用户画像分析...")
        
        cluster_file = CLUSTER_DIR / f'business_cluster_results_shop_{shop_id}.json'
        
        if not cluster_file.exists():
            self.log(f"店铺 {shop_id}: 聚类结果文件不存在，跳过", 'WARNING')
            return False
        
        try:
            # 切换到用户画像分析目录
            original_cwd = Path.cwd()
            os.chdir(PORTRAIT_DIR)
            
            try:
                # 导入用户画像分析类
                sys.path.insert(0, str(PORTRAIT_DIR))
                from business_driven_portrait_analyzer import BusinessDrivenPortraitAnalyzer
                
                # 创建分析器（使用相对路径，从PORTRAIT_DIR的角度）
                relative_path = f'../cluster_timeClip/business_cluster_results_shop_{shop_id}.json'
                analyzer = BusinessDrivenPortraitAnalyzer(
                    cluster_results_file=relative_path
                )
                
                # 运行分析
                strategies = analyzer.analyze_all_clusters()
                analyzer.save_results(strategies)
            finally:
                # 恢复原始工作目录
                os.chdir(original_cwd)
            
            # 重命名输出文件
            output_files = {
                'business_driven_insights.json': f'business_driven_insights_shop_{shop_id}.json',
                'business_driven_insights_summary.csv': f'business_driven_insights_summary_shop_{shop_id}.csv',
                'business_driven_report.md': f'business_driven_report_shop_{shop_id}.md'
            }
            
            for old_name, new_name in output_files.items():
                old_path = PORTRAIT_DIR / old_name
                new_path = PORTRAIT_DIR / new_name
                if old_path.exists():
                    shutil.move(str(old_path), str(new_path))
                    self.log(f"店铺 {shop_id}: 业务洞察已保存 - {new_name}", 'SUCCESS')
            
            return True
            
        except Exception as e:
            self.log(f"店铺 {shop_id}: 用户画像分析失败 - {str(e)}", 'ERROR')
            traceback.print_exc()
            return False
    
    def step5_update_frontend_data(self, shop_id):
        """步骤5: 更新前端数据"""
        self.log(f"店铺 {shop_id}: 开始更新前端数据...")
        
        cluster_file = CLUSTER_DIR / f'business_cluster_results_shop_{shop_id}.json'
        insights_file = PORTRAIT_DIR / f'business_driven_insights_shop_{shop_id}.json'
        
        if not cluster_file.exists():
            self.log(f"店铺 {shop_id}: 聚类结果文件不存在，跳过", 'WARNING')
            return False
        
        try:
            # 导入更新脚本
            sys.path.insert(0, str(DASHBOARD_DIR))
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "update_data",
                DASHBOARD_DIR / 'update_data.py'
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 临时修改路径
            original_cluster_path = "../cluster_timeClip/business_cluster_results.json"
            new_cluster_path = f"../cluster_timeClip/business_cluster_results_shop_{shop_id}.json"
            
            original_insights_path = "../user_portrait_analysis/business_driven_insights.json"
            new_insights_path = f"../user_portrait_analysis/business_driven_insights_shop_{shop_id}.json"
            
            # 读取update_data.py内容
            with open(DASHBOARD_DIR / 'update_data.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换路径
            modified_content = content.replace(original_cluster_path, new_cluster_path)
            modified_content = modified_content.replace(original_insights_path, new_insights_path)
            
            # 创建临时文件
            temp_script = DASHBOARD_DIR / f'update_data_shop_{shop_id}.py'
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # 运行更新脚本
            import subprocess
            result = subprocess.run(
                ['python3', str(temp_script)],
                cwd=str(DASHBOARD_DIR),
                capture_output=True,
                text=True
            )
            
            # 清理临时脚本
            if temp_script.exists():
                temp_script.unlink()
            
            if result.returncode == 0:
                # 重命名输出文件
                data_js = DASHBOARD_DIR / 'data.js'
                data_js_shop = DASHBOARD_DIR / f'data_shop_{shop_id}.js'
                if data_js.exists():
                    shutil.move(str(data_js), str(data_js_shop))
                    self.log(f"店铺 {shop_id}: 前端数据已保存 - data_shop_{shop_id}.js", 'SUCCESS')
                return True
            else:
                self.log(f"店铺 {shop_id}: 前端数据更新失败 - {result.stderr}", 'ERROR')
                return False
                
        except Exception as e:
            self.log(f"店铺 {shop_id}: 前端数据更新失败 - {str(e)}", 'ERROR')
            traceback.print_exc()
            return False
    
    def step6_create_multi_shop_data(self):
        """步骤6: 创建多店铺数据"""
        self.log("创建多店铺数据文件...")
        
        try:
            # 导入多店铺数据创建脚本
            sys.path.insert(0, str(DASHBOARD_DIR))
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "create_multi_shop_dashboard",
                DASHBOARD_DIR / 'create_multi_shop_dashboard.py'
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 运行主函数
            module.main()
            
            self.log("多店铺数据文件已创建", 'SUCCESS')
            return True
            
        except Exception as e:
            self.log(f"创建多店铺数据失败 - {str(e)}", 'ERROR')
            traceback.print_exc()
            return False
    
    def process_shop(self, shop_id):
        """处理单个店铺的完整流程"""
        self.log(f"\n{'='*80}")
        self.log(f"开始处理店铺 {shop_id}", 'INFO')
        self.log(f"{'='*80}")
        
        shop_result = {
            'shop_id': shop_id,
            'steps': {},
            'success': False
        }
        
        # 步骤1: 数据提取检查
        step1_success = self.step1_extract_data(shop_id)
        shop_result['steps']['data_extraction'] = step1_success
        
        if not step1_success:
            self.log(f"店铺 {shop_id}: 数据文件不存在，跳过后续步骤", 'WARNING')
            return shop_result
        
        # 步骤2: 聚类分析
        step2_success = self.step2_clustering(shop_id)
        shop_result['steps']['clustering'] = step2_success
        
        if not step2_success:
            return shop_result
        
        # 步骤3: 聚类结果分析
        step3_success = self.step3_cluster_analysis(shop_id)
        shop_result['steps']['cluster_analysis'] = step3_success
        
        # 步骤4: 用户画像分析
        step4_success = self.step4_portrait_analysis(shop_id)
        shop_result['steps']['portrait_analysis'] = step4_success
        
        # 步骤5: 更新前端数据
        step5_success = self.step5_update_frontend_data(shop_id)
        shop_result['steps']['frontend_update'] = step5_success
        
        # 判断整体是否成功
        shop_result['success'] = all([
            step2_success,  # 聚类分析必须成功
            step4_success,  # 用户画像分析必须成功
        ])
        
        if shop_result['success']:
            self.log(f"店铺 {shop_id}: 所有步骤完成", 'SUCCESS')
        else:
            self.log(f"店铺 {shop_id}: 部分步骤失败", 'WARNING')
        
        return shop_result
    
    def run(self):
        """运行完整的自动化分析流程"""
        print("="*80)
        print("自动化聚类分析系统")
        print("="*80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"处理店铺: {', '.join(map(str, SHOPS))}")
        print("="*80)
        
        # 处理每个店铺
        for shop_id in SHOPS:
            try:
                result = self.process_shop(shop_id)
                self.results[shop_id] = result
            except Exception as e:
                self.log(f"店铺 {shop_id}: 处理过程中发生错误 - {str(e)}", 'ERROR')
                traceback.print_exc()
                self.results[shop_id] = {
                    'shop_id': shop_id,
                    'success': False,
                    'error': str(e)
                }
        
        # 创建多店铺数据
        self.step6_create_multi_shop_data()
        
        # 生成总结报告
        self.generate_summary()
    
    def generate_summary(self):
        """生成总结报告"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "="*80)
        print("分析完成总结")
        print("="*80)
        print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {duration.total_seconds():.1f} 秒")
        print("\n各店铺处理结果:")
        print("-"*80)
        
        success_count = 0
        for shop_id, result in self.results.items():
            status = "✅ 成功" if result.get('success', False) else "❌ 失败"
            print(f"店铺 {shop_id}: {status}")
            
            if result.get('success'):
                success_count += 1
            
            # 显示各步骤状态
            steps = result.get('steps', {})
            for step_name, step_success in steps.items():
                step_status = "✓" if step_success else "✗"
                print(f"  - {step_name}: {step_status}")
        
        print("-"*80)
        print(f"成功: {success_count}/{len(SHOPS)} 个店铺")
        print("="*80)
        
        # 保存总结报告
        summary = {
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_shops': len(SHOPS),
            'successful_shops': success_count,
            'results': self.results
        }
        
        summary_file = BASE_DIR / 'analysis_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.log(f"总结报告已保存: {summary_file}", 'SUCCESS')

def main():
    """主函数"""
    analyzer = AutomatedAnalyzer()
    analyzer.run()

if __name__ == '__main__':
    main()

