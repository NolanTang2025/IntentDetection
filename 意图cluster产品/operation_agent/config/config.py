"""
配置管理
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径（可选）
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        # 默认配置
        default_config = {
            "shopify": {
                "api_key": os.getenv("SHOPIFY_API_KEY", ""),
                "api_secret": os.getenv("SHOPIFY_API_SECRET", ""),
                "shop_domain": os.getenv("SHOPIFY_SHOP_DOMAIN", ""),
                "api_version": "2024-01",
            },
            "email": {
                "provider": os.getenv("EMAIL_PROVIDER", "sendgrid"),
                "api_key": os.getenv("EMAIL_API_KEY", ""),
                "from_email": os.getenv("EMAIL_FROM", ""),
            },
            "sms": {
                "provider": os.getenv("SMS_PROVIDER", "twilio"),
                "api_key": os.getenv("SMS_API_KEY", ""),
                "from_number": os.getenv("SMS_FROM_NUMBER", ""),
            },
            "decision_engine": {
                "enable_ml": False,
                "default_priority": "medium",
            },
            "action_executor": {
                "max_retries": 3,
                "retry_delay_seconds": 60,
            },
            "feedback_loop": {
                "enable_auto_optimization": False,
                "optimization_interval_hours": 24,
            },
        }
        
        # 如果提供了配置文件，加载并合并
        if self.config_file and Path(self.config_file).exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                default_config.update(file_config)
        
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self, config_file: Optional[str] = None):
        """保存配置到文件"""
        file_path = config_file or self.config_file
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)


