"""
运营Agent核心引擎
协调各个模块，实现从分析到执行的完整流程
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# 支持相对导入和绝对导入
try:
    from .decision_engine import DecisionEngine
    from .action_executor import ActionExecutor
    from .strategy_generator import StrategyGenerator
    from .feedback_loop import FeedbackLoop
    from .models.cluster_analysis import ClusterAnalysis
    from .models.action import Action
    from .models.strategy import Strategy
except ImportError:
    # 如果相对导入失败，使用绝对导入
    sys.path.insert(0, str(Path(__file__).parent))
    from decision_engine import DecisionEngine
    from action_executor import ActionExecutor
    from strategy_generator import StrategyGenerator
    from feedback_loop import FeedbackLoop
    from models.cluster_analysis import ClusterAnalysis
    from models.action import Action
    from models.strategy import Strategy

logger = logging.getLogger(__name__)


class OperationAgent:
    """运营Agent核心类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化运营Agent
        
        Args:
            config: 配置字典
        """
        self.config = config if config is not None else {}
        
        # 初始化各个模块
        self.decision_engine = DecisionEngine(self.config.get("decision_engine", {}))
        self.action_executor = ActionExecutor(self.config.get("action_executor", {}))
        self.strategy_generator = StrategyGenerator(self.config.get("strategy_generator", {}))
        self.feedback_loop = FeedbackLoop(self.config.get("feedback_loop", {}))
        
        logger.info("运营Agent初始化完成")
    
    def process_cluster_analysis(
        self,
        cluster_analysis: ClusterAnalysis,
        auto_execute: bool = True
    ) -> Dict[str, Any]:
        """
        处理聚类分析结果，生成并执行运营策略
        
        Args:
            cluster_analysis: 聚类分析结果
            auto_execute: 是否自动执行动作（默认True）
            
        Returns:
            处理结果字典
        """
        logger.info(f"开始处理聚类分析: {cluster_analysis.cluster_id}")
        
        # 1. 决策：决定执行哪些动作
        actions = self.decision_engine.decide_actions(cluster_analysis)
        logger.info(f"决策引擎生成了 {len(actions)} 个动作")
        
        # 2. 生成策略（可选）
        strategies = self.strategy_generator.generate_strategies(cluster_analysis)
        logger.info(f"策略生成器生成了 {len(strategies)} 个策略")
        
        # 3. 执行动作
        execution_results = []
        if auto_execute:
            for action in actions:
                result = self.action_executor.execute(action)
                execution_results.append(result)
                logger.info(f"动作执行完成: {action.action_id}, 状态: {result.status.value}")
        
        # 4. 记录反馈（用于后续优化）
        if execution_results:
            self.feedback_loop.record_execution(
                cluster_analysis.cluster_id,
                actions,
                execution_results
            )
        
        return {
            "cluster_id": cluster_analysis.cluster_id,
            "actions_generated": len(actions),
            "actions_executed": len(execution_results),
            "strategies_generated": len(strategies),
            "execution_results": [r.to_dict() for r in execution_results],
        }
    
    def process_multiple_clusters(
        self,
        cluster_analyses: List[ClusterAnalysis],
        auto_execute: bool = True
    ) -> Dict[str, Any]:
        """
        批量处理多个聚类分析
        
        Args:
            cluster_analyses: 聚类分析结果列表
            auto_execute: 是否自动执行动作
            
        Returns:
            批量处理结果
        """
        logger.info(f"开始批量处理 {len(cluster_analyses)} 个聚类")
        
        results = []
        for cluster_analysis in cluster_analyses:
            result = self.process_cluster_analysis(cluster_analysis, auto_execute)
            results.append(result)
        
        return {
            "total_clusters": len(cluster_analyses),
            "processed_clusters": len(results),
            "total_actions_generated": sum(r["actions_generated"] for r in results),
            "total_actions_executed": sum(r["actions_executed"] for r in results),
            "results": results,
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "strategies_count": len(self.decision_engine.get_strategies()),
            "execution_history_count": len(self.action_executor.get_execution_history()),
            "feedback_records_count": self.feedback_loop.get_records_count(),
        }
    
    def add_strategy(self, strategy: Strategy):
        """添加新策略"""
        self.decision_engine.add_strategy(strategy)
        logger.info(f"添加新策略: {strategy.strategy_id}")
    
    def remove_strategy(self, strategy_id: str):
        """移除策略"""
        self.decision_engine.remove_strategy(strategy_id)
        logger.info(f"移除策略: {strategy_id}")

