"""
策略模型定义
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from .action import Action


class StrategyType(Enum):
    """策略类型枚举"""
    CONVERSION = "conversion"  # 转化策略
    RETENTION = "retention"  # 留存策略
    REPURCHASE = "repurchase"  # 复购策略
    WINBACK = "winback"  # 挽回策略
    ENGAGEMENT = "engagement"  # 参与度策略


class StrategyStatus(Enum):
    """策略状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


@dataclass
class Strategy:
    """运营策略模型"""
    strategy_id: str
    strategy_type: StrategyType
    name: str
    description: str
    conditions: Dict[str, Any]  # 触发条件
    actions: List[Action]  # 执行的动作列表
    priority: str = "medium"
    enabled: bool = True
    status: StrategyStatus = StrategyStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    executed_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)  # 效果指标
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "strategy_id": self.strategy_id,
            "strategy_type": self.strategy_type.value,
            "name": self.name,
            "description": self.description,
            "conditions": self.conditions,
            "actions": [action.to_dict() for action in self.actions],
            "priority": self.priority,
            "enabled": self.enabled,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "executed_count": self.executed_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "metrics": self.metrics,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Strategy":
        """从字典创建"""
        return cls(
            strategy_id=data["strategy_id"],
            strategy_type=StrategyType(data["strategy_type"]),
            name=data["name"],
            description=data["description"],
            conditions=data.get("conditions", {}),
            actions=[Action.from_dict(a) for a in data.get("actions", [])],
            priority=data.get("priority", "medium"),
            enabled=data.get("enabled", True),
            status=StrategyStatus(data.get("status", "draft")),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            executed_count=data.get("executed_count", 0),
            success_count=data.get("success_count", 0),
            failure_count=data.get("failure_count", 0),
            metrics=data.get("metrics", {}),
        )


