"""
动作模型定义
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


class ActionType(Enum):
    """动作类型枚举"""
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    CREATE_DISCOUNT = "create_discount"
    UPDATE_RECOMMENDATION = "update_recommendation"
    TRIGGER_CUSTOMER_SERVICE = "trigger_customer_service"
    UPDATE_PRODUCT_PRICE = "update_product_price"
    CREATE_MARKETING_CAMPAIGN = "create_marketing_campaign"
    PUSH_NOTIFICATION = "push_notification"


class ActionStatus(Enum):
    """动作状态枚举"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Action:
    """运营动作模型"""
    action_id: str
    action_type: ActionType
    target_cluster_id: Optional[str] = None
    target_user_ids: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"  # low, medium, high, urgent
    scheduled_time: Optional[datetime] = None
    status: ActionStatus = ActionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "target_cluster_id": self.target_cluster_id,
            "target_user_ids": self.target_user_ids,
            "parameters": self.parameters,
            "priority": self.priority,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "result": self.result,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        """从字典创建"""
        return cls(
            action_id=data["action_id"],
            action_type=ActionType(data["action_type"]),
            target_cluster_id=data.get("target_cluster_id"),
            target_user_ids=data.get("target_user_ids", []),
            parameters=data.get("parameters", {}),
            priority=data.get("priority", "medium"),
            scheduled_time=datetime.fromisoformat(data["scheduled_time"]) if data.get("scheduled_time") else None,
            status=ActionStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            executed_at=datetime.fromisoformat(data["executed_at"]) if data.get("executed_at") else None,
            result=data.get("result"),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
        )


