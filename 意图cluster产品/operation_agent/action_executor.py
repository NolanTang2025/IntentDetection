"""
动作执行器
执行具体的运营动作
"""

import time
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from .models.action import Action, ActionStatus
    from .models.execution_result import ExecutionResult
    from .integrations.shopify_api import ShopifyIntegration
    from .integrations.email_service import EmailService
    from .integrations.sms_service import SMSService
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from models.action import Action, ActionStatus
    from models.execution_result import ExecutionResult
    from integrations.shopify_api import ShopifyIntegration
    from integrations.email_service import EmailService
    from integrations.sms_service import SMSService

logger = logging.getLogger(__name__)


class ActionExecutor:
    """动作执行器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化动作执行器
        
        Args:
            config: 配置字典，包含各种服务的API密钥等
        """
        self.config = config or {}
        
        # 初始化各种集成服务
        self.shopify = ShopifyIntegration(config.get("shopify", {}))
        self.email_service = EmailService(config.get("email", {}))
        self.sms_service = SMSService(config.get("sms", {}))
        
        # 执行历史记录
        self.execution_history: List[ExecutionResult] = []
    
    def execute(self, action: Action) -> ExecutionResult:
        """
        执行运营动作
        
        Args:
            action: 要执行的动作
            
        Returns:
            执行结果
        """
        start_time = time.time()
        action.status = ActionStatus.EXECUTING
        
        try:
            logger.info(f"开始执行动作: {action.action_id}, 类型: {action.action_type.value}")
            
            # 根据动作类型执行相应的操作
            if action.action_type.value == "send_email":
                result = self._execute_send_email(action)
            elif action.action_type.value == "send_sms":
                result = self._execute_send_sms(action)
            elif action.action_type.value == "create_discount":
                result = self._execute_create_discount(action)
            elif action.action_type.value == "update_recommendation":
                result = self._execute_update_recommendation(action)
            elif action.action_type.value == "trigger_customer_service":
                result = self._execute_trigger_customer_service(action)
            else:
                raise ValueError(f"不支持的动作类型: {action.action_type.value}")
            
            # 更新动作状态
            action.status = ActionStatus.COMPLETED
            action.executed_at = datetime.now()
            action.result = result
            
            duration = time.time() - start_time
            
            execution_result = ExecutionResult(
                action_id=action.action_id,
                status=ActionStatus.COMPLETED,
                duration_seconds=duration,
                result_data=result,
            )
            
            logger.info(f"动作执行成功: {action.action_id}, 耗时: {duration:.2f}秒")
            
        except Exception as e:
            # 处理执行失败
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            action.executed_at = datetime.now()
            
            duration = time.time() - start_time
            
            execution_result = ExecutionResult(
                action_id=action.action_id,
                status=ActionStatus.FAILED,
                duration_seconds=duration,
                error_message=str(e),
            )
            
            logger.error(f"动作执行失败: {action.action_id}, 错误: {str(e)}")
            
            # 如果未达到最大重试次数，可以安排重试
            if action.retry_count < action.max_retries:
                action.retry_count += 1
                logger.info(f"安排重试: {action.action_id}, 重试次数: {action.retry_count}")
        
        # 记录执行历史
        self.execution_history.append(execution_result)
        
        return execution_result
    
    def _execute_send_email(self, action: Action) -> Dict[str, Any]:
        """执行发送邮件动作"""
        template = action.parameters.get("template", "default")
        variables = action.parameters.get("variables", {})
        delay_minutes = action.parameters.get("delay_minutes", 0)
        
        # 发送邮件给目标用户
        results = []
        for user_id in action.target_user_ids:
            result = self.email_service.send_email(
                user_id=user_id,
                template=template,
                variables=variables,
                delay_minutes=delay_minutes,
            )
            results.append(result)
        
        return {
            "sent_count": len(results),
            "success_count": sum(1 for r in results if r.get("success")),
            "results": results,
        }
    
    def _execute_send_sms(self, action: Action) -> Dict[str, Any]:
        """执行发送短信动作"""
        message = action.parameters.get("message", "")
        
        results = []
        for user_id in action.target_user_ids:
            result = self.sms_service.send_sms(
                user_id=user_id,
                message=message,
            )
            results.append(result)
        
        return {
            "sent_count": len(results),
            "success_count": sum(1 for r in results if r.get("success")),
            "results": results,
        }
    
    def _execute_create_discount(self, action: Action) -> Dict[str, Any]:
        """执行创建折扣码动作"""
        discount_type = action.parameters.get("discount_type", "percentage")
        discount_value = action.parameters.get("discount_value", 10)
        expiry_days = action.parameters.get("expiry_days", 30)
        usage_limit = action.parameters.get("usage_limit", 1)
        
        # 为每个目标用户创建专属折扣码
        discount_codes = []
        for user_id in action.target_user_ids:
            code = self.shopify.create_discount_code(
                discount_type=discount_type,
                discount_value=discount_value,
                expiry_days=expiry_days,
                usage_limit=usage_limit,
                customer_id=user_id,
            )
            discount_codes.append(code)
        
        return {
            "created_count": len(discount_codes),
            "discount_codes": discount_codes,
        }
    
    def _execute_update_recommendation(self, action: Action) -> Dict[str, Any]:
        """执行更新产品推荐动作"""
        product_ids = action.parameters.get("product_ids", [])
        
        results = []
        for user_id in action.target_user_ids:
            result = self.shopify.update_product_recommendation(
                customer_id=user_id,
                product_ids=product_ids,
            )
            results.append(result)
        
        return {
            "updated_count": len(results),
            "success_count": sum(1 for r in results if r.get("success")),
            "results": results,
        }
    
    def _execute_trigger_customer_service(self, action: Action) -> Dict[str, Any]:
        """执行触发客服跟进动作"""
        message = action.parameters.get("message", "用户需要客服跟进")
        priority = action.parameters.get("priority", "medium")
        
        results = []
        for user_id in action.target_user_ids:
            result = self.shopify.create_customer_service_ticket(
                customer_id=user_id,
                message=message,
                priority=priority,
            )
            results.append(result)
        
        return {
            "created_count": len(results),
            "success_count": sum(1 for r in results if r.get("success")),
            "results": results,
        }
    
    def get_execution_history(self, limit: int = 100) -> List[ExecutionResult]:
        """获取执行历史"""
        return self.execution_history[-limit:]

