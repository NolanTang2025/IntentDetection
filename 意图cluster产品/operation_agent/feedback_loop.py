"""
反馈循环
监控执行效果，优化策略
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from .models.action import Action
    from .models.execution_result import ExecutionResult
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from models.action import Action
    from models.execution_result import ExecutionResult

logger = logging.getLogger(__name__)


class FeedbackLoop:
    """反馈循环类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化反馈循环
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.execution_records: List[Dict[str, Any]] = []
        self.metrics_cache: Dict[str, Dict[str, Any]] = {}
    
    def record_execution(
        self,
        cluster_id: str,
        actions: List[Action],
        execution_results: List[ExecutionResult]
    ):
        """
        记录执行结果
        
        Args:
            cluster_id: 聚类ID
            actions: 执行的动作列表
            execution_results: 执行结果列表
        """
        record = {
            "cluster_id": cluster_id,
            "timestamp": datetime.now().isoformat(),
            "actions": [a.to_dict() for a in actions],
            "results": [r.to_dict() for r in execution_results],
        }
        
        self.execution_records.append(record)
        logger.info(f"记录执行反馈: 聚类 {cluster_id}, {len(actions)} 个动作")
    
    def get_metrics(
        self,
        cluster_id: Optional[str] = None,
        action_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取效果指标
        
        Args:
            cluster_id: 聚类ID（可选）
            action_type: 动作类型（可选）
            
        Returns:
            效果指标字典
        """
        # 过滤记录
        filtered_records = self.execution_records
        if cluster_id:
            filtered_records = [r for r in filtered_records if r["cluster_id"] == cluster_id]
        
        # 计算指标
        total_actions = 0
        successful_actions = 0
        failed_actions = 0
        
        for record in filtered_records:
            for result in record["results"]:
                if action_type and result.get("action_type") != action_type:
                    continue
                
                total_actions += 1
                if result["status"] == "completed":
                    successful_actions += 1
                else:
                    failed_actions += 1
        
        success_rate = successful_actions / total_actions if total_actions > 0 else 0
        
        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "success_rate": success_rate,
        }
    
    def get_records_count(self) -> int:
        """获取记录数量"""
        return len(self.execution_records)
    
    def analyze_effectiveness(
        self,
        cluster_id: str,
        before_metrics: Dict[str, Any],
        after_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析策略效果
        
        Args:
            cluster_id: 聚类ID
            before_metrics: 执行前的指标
            after_metrics: 执行后的指标
            
        Returns:
            效果分析结果
        """
        # 计算提升
        conversion_lift = 0.0
        if "conversion_rate" in before_metrics and "conversion_rate" in after_metrics:
            conversion_lift = after_metrics["conversion_rate"] - before_metrics["conversion_rate"]
        
        return {
            "cluster_id": cluster_id,
            "conversion_lift": conversion_lift,
            "before_metrics": before_metrics,
            "after_metrics": after_metrics,
        }

