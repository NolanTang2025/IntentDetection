#!/usr/bin/env python3
"""
运营Agent使用示例
"""

import logging
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from agent_core import OperationAgent
from models.cluster_analysis import ClusterAnalysis
from models.user_segment import UserSegment

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)
    
    # 初始化Agent
    agent = OperationAgent()
    
    # 创建聚类分析结果（示例数据）
    cluster_analysis = ClusterAnalysis(
        cluster_id="cluster_0",
        cluster_name="决策阶段·高端价值型",
        user_count=100,
        segment_count=150,
        characteristics={
            "stage": "决策阶段",
            "price": "高端价值型",
            "engagement": "深度研究",
        },
        purchase_stage_distribution={
            "决策阶段": 80,
            "对比阶段": 20,
        },
        price_preference_distribution={
            "高端价值型": 70,
            "中端价值型": 30,
        },
        avg_intent_score=0.75,
        conversion_rate=0.15,
    )
    
    # 处理聚类分析（不自动执行，仅生成动作）
    result = agent.process_cluster_analysis(cluster_analysis, auto_execute=False)
    
    print(f"\n处理结果:")
    print(f"  聚类ID: {result['cluster_id']}")
    print(f"  生成动作数: {result['actions_generated']}")
    print(f"  生成策略数: {result['strategies_generated']}")
    
    # 查看Agent状态
    status = agent.get_agent_status()
    print(f"\nAgent状态:")
    print(f"  策略数量: {status['strategies_count']}")
    print(f"  执行历史记录数: {status['execution_history_count']}")


def example_with_user_segments():
    """带用户分群的示例"""
    print("\n" + "=" * 60)
    print("示例2: 带用户分群的处理")
    print("=" * 60)
    
    agent = OperationAgent()
    
    # 创建用户分群
    user_segments = [
        UserSegment(
            user_id="user_001",
            cluster_id="cluster_0",
            purchase_stage="决策阶段",
            price_sensitivity="高端价值型",
            engagement_level="深度研究",
            intent_score=0.85,
            conversion_probability=0.8,
        ),
        UserSegment(
            user_id="user_002",
            cluster_id="cluster_0",
            purchase_stage="决策阶段",
            price_sensitivity="高端价值型",
            engagement_level="深度研究",
            intent_score=0.75,
            conversion_probability=0.7,
        ),
    ]
    
    # 创建聚类分析
    cluster_analysis = ClusterAnalysis(
        cluster_id="cluster_0",
        cluster_name="决策阶段·高端价值型",
        user_count=len(user_segments),
        segment_count=len(user_segments),
        characteristics={
            "stage": "决策阶段",
            "price": "高端价值型",
        },
        user_segments=user_segments,
        avg_intent_score=0.80,
    )
    
    # 处理（这里设置为False，因为实际执行需要配置API）
    result = agent.process_cluster_analysis(cluster_analysis, auto_execute=False)
    
    print(f"\n处理结果:")
    print(f"  目标用户数: {len(user_segments)}")
    print(f"  生成动作数: {result['actions_generated']}")


def example_batch_processing():
    """批量处理示例"""
    print("\n" + "=" * 60)
    print("示例3: 批量处理多个聚类")
    print("=" * 60)
    
    agent = OperationAgent()
    
    # 创建多个聚类分析
    cluster_analyses = [
        ClusterAnalysis(
            cluster_id="cluster_0",
            cluster_name="决策阶段·高端价值型",
            user_count=100,
            segment_count=150,
            characteristics={"stage": "决策阶段", "price": "高端价值型"},
            avg_intent_score=0.75,
        ),
        ClusterAnalysis(
            cluster_id="cluster_1",
            cluster_name="浏览阶段·价格敏感型",
            user_count=200,
            segment_count=300,
            characteristics={"stage": "浏览阶段", "price": "价格敏感型"},
            avg_intent_score=0.45,
        ),
    ]
    
    # 批量处理
    result = agent.process_multiple_clusters(cluster_analyses, auto_execute=False)
    
    print(f"\n批量处理结果:")
    print(f"  处理聚类数: {result['processed_clusters']}")
    print(f"  总生成动作数: {result['total_actions_generated']}")


def example_custom_strategy():
    """自定义策略示例"""
    print("\n" + "=" * 60)
    print("示例4: 添加自定义策略")
    print("=" * 60)
    
    from operation_agent.models.strategy import Strategy, StrategyType
    from operation_agent.models.action import Action, ActionType
    import uuid
    
    agent = OperationAgent()
    
    # 创建自定义策略
    custom_strategy = Strategy(
        strategy_id=str(uuid.uuid4()),
        strategy_type=StrategyType.CONVERSION,
        name="高意图用户紧急转化策略",
        description="针对意图强度>0.8的用户，立即发送高额优惠券",
        conditions={
            "min_intent_score": 0.8,
            "purchase_stage": "决策阶段",
        },
        actions=[
            Action(
                action_id=str(uuid.uuid4()),
                action_type=ActionType.CREATE_DISCOUNT,
                parameters={
                    "discount_type": "percentage",
                    "discount_value": 25,  # 25%折扣
                    "expiry_days": 3,
                },
                priority="urgent",
            ),
        ],
        priority="urgent",
    )
    
    # 添加策略
    agent.add_strategy(custom_strategy)
    
    print(f"\n已添加自定义策略:")
    print(f"  策略ID: {custom_strategy.strategy_id}")
    print(f"  策略名称: {custom_strategy.name}")
    print(f"  当前策略总数: {len(agent.decision_engine.get_strategies())}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("运营Agent使用示例")
    print("=" * 60 + "\n")
    
    # 运行示例
    example_basic_usage()
    example_with_user_segments()
    example_batch_processing()
    example_custom_strategy()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)

