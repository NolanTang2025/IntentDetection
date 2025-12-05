#!/usr/bin/env python3
"""
将运营Agent与现有聚类分析系统集成
从聚类结果文件加载数据，自动生成并执行运营策略
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from agent_core import OperationAgent
from models.cluster_analysis import ClusterAnalysis
from models.user_segment import UserSegment

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_cluster_results(file_path: Path) -> Dict[str, Any]:
    """加载聚类结果文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_to_cluster_analysis(
    cluster_data: Dict[str, Any],
    cluster_id: str
) -> ClusterAnalysis:
    """
    将聚类结果数据转换为ClusterAnalysis模型
    
    Args:
        cluster_data: 聚类结果数据
        cluster_id: 聚类ID
        
    Returns:
        ClusterAnalysis对象
    """
    # 从business_cluster_results格式转换
    segments = cluster_data.get("segments", [])
    cluster_info = cluster_data.get("clustering", {})
    cluster_labels = cluster_info.get("cluster_labels", {})
    
    # 获取当前聚类的信息
    cluster_label_info = cluster_labels.get(cluster_id, {})
    
    # 筛选属于当前聚类的segments
    cluster_segments = [
        seg for seg in segments
        if str(seg.get("business_cluster", "")) == cluster_id
    ]
    
    # 提取用户ID列表
    user_ids = list(set(seg.get("user_id", "") for seg in cluster_segments if seg.get("user_id")))
    
    # 构建特征字典
    characteristics = cluster_label_info.get("characteristics", {})
    if not characteristics:
        # 从segment中提取特征
        if cluster_segments:
            first_seg = cluster_segments[0]
            characteristics = {
                "stage": first_seg.get("purchase_stage", "浏览阶段"),
                "price": first_seg.get("price_sensitivity", "中端价值型"),
                "engagement": first_seg.get("engagement_level", "快速浏览者"),
            }
        else:
            characteristics = {
                "stage": "浏览阶段",
                "price": "中端价值型",
                "engagement": "快速浏览者",
            }
    
    # 确保特征字段名称与决策引擎匹配
    # 将可能的字段名统一
    if "stage" not in characteristics:
        characteristics["stage"] = characteristics.get("purchase_stage", "浏览阶段")
    if "price" not in characteristics:
        characteristics["price"] = characteristics.get("price_sensitivity", "中端价值型")
    
    # 统计购买阶段分布
    purchase_stage_dist = {}
    for seg in cluster_segments:
        stage = seg.get("purchase_stage", "浏览阶段")
        purchase_stage_dist[stage] = purchase_stage_dist.get(stage, 0) + 1
    
    # 统计价格偏好分布
    price_pref_dist = {}
    for seg in cluster_segments:
        price = seg.get("price_sensitivity", "中端价值型")
        price_pref_dist[price] = price_pref_dist.get(price, 0) + 1
    
    # 计算平均意图强度
    intent_scores = [seg.get("intent_score", 0.5) for seg in cluster_segments if seg.get("intent_score")]
    avg_intent_score = sum(intent_scores) / len(intent_scores) if intent_scores else 0.5
    
    # 创建ClusterAnalysis对象
    cluster_analysis = ClusterAnalysis(
        cluster_id=cluster_id,
        cluster_name=cluster_label_info.get("short_label", f"聚类 {cluster_id}"),
        user_count=len(user_ids),
        segment_count=len(cluster_segments),
        characteristics=characteristics,
        purchase_stage_distribution=purchase_stage_dist,
        price_preference_distribution=price_pref_dist,
        avg_intent_score=avg_intent_score,
    )
    
    return cluster_analysis


def process_shop_clusters(
    shop_id: str,
    auto_execute: bool = False
) -> Dict[str, Any]:
    """
    处理指定店铺的所有聚类
    
    Args:
        shop_id: 店铺ID
        auto_execute: 是否自动执行动作（默认False，仅生成动作）
        
    Returns:
        处理结果
    """
    # 加载聚类结果文件
    cluster_file = Path(__file__).parent.parent / "cluster_timeClip" / f"business_cluster_results_shop_{shop_id}.json"
    
    if not cluster_file.exists():
        logger.error(f"找不到聚类结果文件: {cluster_file}")
        return {"error": f"文件不存在: {cluster_file}"}
    
    logger.info(f"加载聚类结果: {cluster_file}")
    cluster_data = load_cluster_results(cluster_file)
    
    # 获取所有聚类ID
    cluster_labels = cluster_data.get("clustering", {}).get("cluster_labels", {})
    cluster_ids = list(cluster_labels.keys())
    
    logger.info(f"找到 {len(cluster_ids)} 个聚类")
    
    # 初始化Agent
    agent = OperationAgent()
    
    # 转换并处理每个聚类
    cluster_analyses = []
    for cluster_id in cluster_ids:
        try:
            cluster_analysis = convert_to_cluster_analysis(cluster_data, cluster_id)
            cluster_analyses.append(cluster_analysis)
        except Exception as e:
            logger.error(f"转换聚类 {cluster_id} 失败: {e}")
            continue
    
    # 批量处理
    if cluster_analyses:
        result = agent.process_multiple_clusters(cluster_analyses, auto_execute=auto_execute)
        return result
    else:
        return {"error": "没有可处理的聚类"}


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="运营Agent与聚类分析集成")
    parser.add_argument("shop_id", help="店铺ID (例如: 53)")
    parser.add_argument("--execute", action="store_true", help="自动执行动作（默认仅生成）")
    parser.add_argument("--cluster-id", help="只处理指定的聚类ID（可选）")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"处理店铺 {args.shop_id} 的聚类分析")
    print("=" * 60)
    
    if args.cluster_id:
        # 处理单个聚类
        print(f"处理单个聚类: {args.cluster_id}")
        # TODO: 实现单聚类处理
        print("单聚类处理功能待实现")
    else:
        # 处理所有聚类
        result = process_shop_clusters(args.shop_id, auto_execute=args.execute)
        
        if "error" in result:
            print(f"❌ 错误: {result['error']}")
            return
        
        print(f"\n✅ 处理完成!")
        print(f"  处理聚类数: {result['processed_clusters']}")
        print(f"  总生成动作数: {result['total_actions_generated']}")
        print(f"  总执行动作数: {result['total_actions_executed']}")
        
        if args.execute:
            print("\n⚠️  注意: 动作已自动执行，请检查执行结果")
        else:
            print("\n💡 提示: 使用 --execute 参数可以自动执行动作")


if __name__ == "__main__":
    main()

