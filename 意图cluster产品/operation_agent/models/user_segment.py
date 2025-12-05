"""
用户分群模型定义
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class UserSegment:
    """用户分群模型"""
    user_id: str
    cluster_id: str
    purchase_stage: str  # 浏览阶段, 对比阶段, 决策阶段
    price_sensitivity: str  # 价格敏感型, 中端价值型, 高端价值型
    engagement_level: str  # 快速浏览者, 中等参与, 深度研究者
    product_preference: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    core_needs: List[str] = field(default_factory=list)
    intent_score: float = 0.0
    last_activity_time: Optional[str] = None
    conversion_probability: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "cluster_id": self.cluster_id,
            "purchase_stage": self.purchase_stage,
            "price_sensitivity": self.price_sensitivity,
            "engagement_level": self.engagement_level,
            "product_preference": self.product_preference,
            "concerns": self.concerns,
            "core_needs": self.core_needs,
            "intent_score": self.intent_score,
            "last_activity_time": self.last_activity_time,
            "conversion_probability": self.conversion_probability,
        }


