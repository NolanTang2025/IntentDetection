"""
决策引擎
基于聚类分析结果，自动决策执行哪些运营动作
"""

import uuid
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from .models.action import Action, ActionType, ActionStatus
    from .models.cluster_analysis import ClusterAnalysis
    from .models.user_segment import UserSegment
    from .models.strategy import Strategy, StrategyType, StrategyStatus
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from models.action import Action, ActionType, ActionStatus
    from models.cluster_analysis import ClusterAnalysis
    from models.user_segment import UserSegment
    from models.strategy import Strategy, StrategyType, StrategyStatus


class DecisionEngine:
    """决策引擎类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化决策引擎
        
        Args:
            config: 配置字典，包含决策规则配置
        """
        self.config = config or {}
        self.strategies: List[Strategy] = []
        self._load_default_strategies()
    
    def _load_default_strategies(self):
        """加载默认策略"""
        # 决策阶段用户转化策略
        self.strategies.append(Strategy(
            strategy_id=str(uuid.uuid4()),
            strategy_type=StrategyType.CONVERSION,
            name="决策阶段用户转化策略",
            description="针对处于决策阶段的用户，发送限时优惠券促进转化",
            conditions={
                "purchase_stage": "决策阶段",
                "min_intent_score": 0.6,
            },
            actions=[
                Action(
                    action_id=str(uuid.uuid4()),
                    action_type=ActionType.CREATE_DISCOUNT,
                    parameters={
                        "discount_type": "percentage",
                        "discount_value": 15,
                        "expiry_days": 7,
                    },
                    priority="high",
                ),
                Action(
                    action_id=str(uuid.uuid4()),
                    action_type=ActionType.SEND_EMAIL,
                    parameters={
                        "template": "decision_stage_coupon",
                        "delay_minutes": 0,
                    },
                    priority="high",
                ),
            ],
            priority="high",
            enabled=True,
            status=StrategyStatus.ACTIVE,
        ))
        
        # 浏览阶段用户引导策略（降低意图强度要求，使其更容易匹配）
        self.strategies.append(Strategy(
            strategy_id=str(uuid.uuid4()),
            strategy_type=StrategyType.ENGAGEMENT,
            name="浏览阶段用户引导策略",
            description="针对浏览阶段的用户，发送产品推荐和内容引导",
            conditions={
                "purchase_stage": "浏览阶段",
                "min_intent_score": 0.0,  # 降低要求，匹配所有浏览阶段用户
            },
            actions=[
                Action(
                    action_id=str(uuid.uuid4()),
                    action_type=ActionType.SEND_EMAIL,
                    parameters={
                        "template": "browsing_stage_recommendation",
                        "delay_minutes": 30,
                    },
                    priority="medium",
                ),
            ],
            priority="medium",
            enabled=True,
            status=StrategyStatus.ACTIVE,
        ))
        
        # 对比阶段用户策略
        self.strategies.append(Strategy(
            strategy_id=str(uuid.uuid4()),
            strategy_type=StrategyType.CONVERSION,
            name="对比阶段用户策略",
            description="针对对比阶段的用户，提供产品对比和优惠信息",
            conditions={
                "purchase_stage": "对比阶段",
                "min_intent_score": 0.4,
            },
            actions=[
                Action(
                    action_id=str(uuid.uuid4()),
                    action_type=ActionType.SEND_EMAIL,
                    parameters={
                        "template": "comparing_stage_guide",
                        "delay_minutes": 15,
                    },
                    priority="medium",
                ),
            ],
            priority="medium",
            enabled=True,
            status=StrategyStatus.ACTIVE,
        ))
    
    def decide_actions(
        self,
        cluster_analysis: ClusterAnalysis,
        user_segments: Optional[List[UserSegment]] = None
    ) -> List[Action]:
        """
        基于聚类分析结果决定执行哪些动作
        
        Args:
            cluster_analysis: 聚类分析结果
            user_segments: 用户分群列表（可选）
            
        Returns:
            需要执行的动作列表
        """
        actions = []
        
        # 遍历所有策略，检查是否匹配条件
        for strategy in self.strategies:
            if not strategy.enabled or strategy.status.value != "active":
                continue
            
            # 检查策略条件是否匹配
            if self._match_conditions(strategy, cluster_analysis, user_segments):
                # 为每个匹配的策略生成动作
                for action_template in strategy.actions:
                    action = self._create_action_from_template(
                        action_template,
                        cluster_analysis,
                        user_segments
                    )
                    actions.append(action)
        
        # 按优先级排序
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        actions.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        return actions
    
    def _match_conditions(
        self,
        strategy: Strategy,
        cluster_analysis: ClusterAnalysis,
        user_segments: Optional[List[UserSegment]]
    ) -> bool:
        """
        检查策略条件是否匹配
        
        Args:
            strategy: 策略对象
            cluster_analysis: 聚类分析结果
            user_segments: 用户分群列表
            
        Returns:
            是否匹配
        """
        conditions = strategy.conditions
        
        # 检查购买阶段（支持模糊匹配）
        if "purchase_stage" in conditions:
            dominant_stage = cluster_analysis.characteristics.get("stage", "")
            required_stage = conditions["purchase_stage"]
            
            # 精确匹配
            if dominant_stage == required_stage:
                pass  # 匹配
            # 模糊匹配：如果要求"决策阶段"，也匹配"对比决策阶段"等
            elif required_stage in dominant_stage or dominant_stage in required_stage:
                pass  # 匹配
            else:
                return False
        
        # 检查意图强度
        if "min_intent_score" in conditions:
            if cluster_analysis.avg_intent_score < conditions["min_intent_score"]:
                return False
        
        # 检查价格敏感度
        if "price_sensitivity" in conditions:
            price_sens = cluster_analysis.characteristics.get("price", "")
            if price_sens != conditions["price_sensitivity"]:
                return False
        
        # 检查用户数量
        if "min_user_count" in conditions:
            if cluster_analysis.user_count < conditions["min_user_count"]:
                return False
        
        return True
    
    def _create_action_from_template(
        self,
        action_template: Action,
        cluster_analysis: ClusterAnalysis,
        user_segments: Optional[List[UserSegment]]
    ) -> Action:
        """
        从动作模板创建实际动作
        
        Args:
            action_template: 动作模板
            cluster_analysis: 聚类分析结果
            user_segments: 用户分群列表
            
        Returns:
            新的动作对象
        """
        import uuid
        from copy import deepcopy
        
        # 创建新动作
        action = Action(
            action_id=str(uuid.uuid4()),
            action_type=action_template.action_type,
            target_cluster_id=cluster_analysis.cluster_id,
            target_user_ids=[seg.user_id for seg in (user_segments or [])],
            parameters=deepcopy(action_template.parameters),
            priority=action_template.priority,
            scheduled_time=action_template.scheduled_time,
        )
        
        # 根据动作类型填充参数
        if action.action_type == ActionType.CREATE_DISCOUNT:
            # 可以根据聚类特征调整折扣力度
            if cluster_analysis.characteristics.get("price") == "价格敏感型":
                action.parameters["discount_value"] = action.parameters.get("discount_value", 15) + 5
        
        elif action.action_type == ActionType.SEND_EMAIL:
            # 填充邮件模板变量
            action.parameters["variables"] = {
                "cluster_name": cluster_analysis.cluster_name,
                "user_count": cluster_analysis.user_count,
            }
        
        return action
    
    def add_strategy(self, strategy: Strategy):
        """添加新策略"""
        self.strategies.append(strategy)
    
    def remove_strategy(self, strategy_id: str):
        """移除策略"""
        self.strategies = [s for s in self.strategies if s.strategy_id != strategy_id]
    
    def get_strategies(self) -> List[Strategy]:
        """获取所有策略"""
        return self.strategies

