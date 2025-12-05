"""
执行结果模型定义
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from .action import ActionStatus


@dataclass
class ExecutionResult:
    """动作执行结果模型"""
    action_id: str
    status: ActionStatus
    execution_time: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)  # 效果指标
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "action_id": self.action_id,
            "status": self.status.value,
            "execution_time": self.execution_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "result_data": self.result_data,
            "error_message": self.error_message,
            "metrics": self.metrics,
        }


