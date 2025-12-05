"""
聚类分析模型定义
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .user_segment import UserSegment


@dataclass
class ClusterAnalysis:
    """聚类分析结果模型"""
    cluster_id: str
    cluster_name: str
    user_count: int
    segment_count: int
    characteristics: Dict[str, Any]  # 聚类特征
    user_segments: List[UserSegment] = field(default_factory=list)
    purchase_stage_distribution: Dict[str, int] = field(default_factory=dict)
    price_preference_distribution: Dict[str, int] = field(default_factory=dict)
    engagement_level: str = ""
    top_interests: List[str] = field(default_factory=list)
    top_concerns: List[str] = field(default_factory=list)
    conversion_rate: float = 0.0
    avg_intent_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "cluster_id": self.cluster_id,
            "cluster_name": self.cluster_name,
            "user_count": self.user_count,
            "segment_count": self.segment_count,
            "characteristics": self.characteristics,
            "user_segments": [seg.to_dict() for seg in self.user_segments],
            "purchase_stage_distribution": self.purchase_stage_distribution,
            "price_preference_distribution": self.price_preference_distribution,
            "engagement_level": self.engagement_level,
            "top_interests": self.top_interests,
            "top_concerns": self.top_concerns,
            "conversion_rate": self.conversion_rate,
            "avg_intent_score": self.avg_intent_score,
        }


