"""
策略生成器
基于聚类分析自动生成可执行的运营策略
"""

import uuid
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from .models.cluster_analysis import ClusterAnalysis
    from .models.strategy import Strategy, StrategyType
    from .models.action import Action, ActionType
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from models.cluster_analysis import ClusterAnalysis
    from models.strategy import Strategy, StrategyType
    from models.action import Action, ActionType


class StrategyGenerator:
    """策略生成器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化策略生成器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.strategy_templates = self._load_strategy_templates()
    
    def _load_strategy_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载策略模板"""
        return {
            "high_value_decision": {
                "name": "高价值决策用户转化策略",
                "description": "针对高价值、处于决策阶段的用户，提供VIP服务和专属优惠",
                "conditions": {
                    "purchase_stage": "决策阶段",
                    "price_sensitivity": "高端价值型",
                    "min_intent_score": 0.7,
                },
                "actions": [
                    {
                        "type": ActionType.CREATE_DISCOUNT,
                        "parameters": {
                            "discount_type": "percentage",
                            "discount_value": 20,
                            "expiry_days": 3,
                        },
                        "priority": "urgent",
                    },
                    {
                        "type": ActionType.SEND_EMAIL,
                        "parameters": {
                            "template": "vip_decision_coupon",
                        },
                        "priority": "urgent",
                    },
                ],
            },
            "price_sensitive_browsing": {
                "name": "价格敏感浏览用户引导策略",
                "description": "针对价格敏感、处于浏览阶段的用户，提供性价比产品推荐",
                "conditions": {
                    "purchase_stage": "浏览阶段",
                    "price_sensitivity": "价格敏感型",
                },
                "actions": [
                    {
                        "type": ActionType.SEND_EMAIL,
                        "parameters": {
                            "template": "budget_friendly_recommendation",
                        },
                        "priority": "medium",
                    },
                ],
            },
        }
    
    def generate_strategies(
        self,
        cluster_analysis: ClusterAnalysis
    ) -> List[Strategy]:
        """
        基于聚类分析生成策略
        
        Args:
            cluster_analysis: 聚类分析结果
            
        Returns:
            生成的策略列表
        """
        strategies = []
        
        # 根据聚类特征匹配策略模板
        for template_key, template in self.strategy_templates.items():
            if self._match_template(template, cluster_analysis):
                strategy = self._create_strategy_from_template(
                    template_key,
                    template,
                    cluster_analysis
                )
                strategies.append(strategy)
        
        return strategies
    
    def _match_template(
        self,
        template: Dict[str, Any],
        cluster_analysis: ClusterAnalysis
    ) -> bool:
        """检查模板是否匹配聚类特征"""
        conditions = template.get("conditions", {})
        
        # 检查购买阶段
        if "purchase_stage" in conditions:
            stage = cluster_analysis.characteristics.get("stage", "")
            if stage != conditions["purchase_stage"]:
                return False
        
        # 检查价格敏感度
        if "price_sensitivity" in conditions:
            price = cluster_analysis.characteristics.get("price", "")
            if price != conditions["price_sensitivity"]:
                return False
        
        # 检查意图强度
        if "min_intent_score" in conditions:
            if cluster_analysis.avg_intent_score < conditions["min_intent_score"]:
                return False
        
        return True
    
    def _create_strategy_from_template(
        self,
        template_key: str,
        template: Dict[str, Any],
        cluster_analysis: ClusterAnalysis
    ) -> Strategy:
        """从模板创建策略"""
        actions = []
        for action_template in template.get("actions", []):
            action = Action(
                action_id=str(uuid.uuid4()),
                action_type=action_template["type"],
                target_cluster_id=cluster_analysis.cluster_id,
                parameters=action_template.get("parameters", {}),
                priority=action_template.get("priority", "medium"),
            )
            actions.append(action)
        
        strategy = Strategy(
            strategy_id=str(uuid.uuid4()),
            strategy_type=StrategyType.CONVERSION,  # 默认类型
            name=template["name"],
            description=template["description"],
            conditions=template.get("conditions", {}),
            actions=actions,
        )
        
        return strategy

