# 运营Agent核心模块

智能运营Agent系统，从用户意图分析到自动执行运营策略的完整解决方案。

## 📁 目录结构

```
operation_agent/
├── __init__.py                 # 模块初始化
├── agent_core.py               # Agent核心引擎
├── decision_engine.py          # 决策引擎
├── action_executor.py          # 动作执行器
├── strategy_generator.py       # 策略生成器
├── feedback_loop.py           # 反馈循环
├── models/                     # 数据模型
│   ├── __init__.py
│   ├── action.py              # 动作模型
│   ├── strategy.py            # 策略模型
│   ├── cluster_analysis.py    # 聚类分析模型
│   ├── user_segment.py        # 用户分群模型
│   └── execution_result.py    # 执行结果模型
├── integrations/               # 第三方集成
│   ├── __init__.py
│   ├── shopify_api.py         # Shopify API集成
│   ├── email_service.py       # 邮件服务集成
│   └── sms_service.py         # 短信服务集成
├── config/                     # 配置管理
│   └── config.py
├── utils/                      # 工具函数
├── requirements.txt            # 依赖包
└── README.md                   # 说明文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
export SHOPIFY_API_KEY="your_api_key"
export SHOPIFY_API_SECRET="your_api_secret"
export SHOPIFY_SHOP_DOMAIN="your_shop.myshopify.com"
export EMAIL_API_KEY="your_email_api_key"
export SMS_API_KEY="your_sms_api_key"
```

### 3. 基本使用

```python
from operation_agent import OperationAgent
from operation_agent.models.cluster_analysis import ClusterAnalysis

# 初始化Agent
agent = OperationAgent()

# 创建聚类分析结果（示例）
cluster_analysis = ClusterAnalysis(
    cluster_id="cluster_0",
    cluster_name="决策阶段·高端价值型",
    user_count=100,
    segment_count=150,
    characteristics={
        "stage": "决策阶段",
        "price": "高端价值型",
        "engagement": "深度研究",
    },
    avg_intent_score=0.75,
)

# 处理聚类分析并自动执行策略
result = agent.process_cluster_analysis(cluster_analysis, auto_execute=True)

print(f"生成了 {result['actions_generated']} 个动作")
print(f"执行了 {result['actions_executed']} 个动作")
```

## 📖 核心模块说明

### Agent核心引擎 (agent_core.py)

协调各个模块，实现从分析到执行的完整流程。

**主要功能**：
- 处理聚类分析结果
- 协调决策引擎、动作执行器、策略生成器
- 管理反馈循环

### 决策引擎 (decision_engine.py)

基于聚类分析结果，自动决策执行哪些运营动作。

**主要功能**：
- 策略匹配
- 动作生成
- 优先级排序

### 动作执行器 (action_executor.py)

执行具体的运营动作。

**支持的动作类型**：
- 发送邮件
- 发送短信
- 创建折扣码
- 更新产品推荐
- 触发客服跟进

### 策略生成器 (strategy_generator.py)

基于聚类分析自动生成可执行的运营策略。

**策略类型**：
- 转化策略
- 留存策略
- 复购策略
- 挽回策略

### 反馈循环 (feedback_loop.py)

监控执行效果，优化策略。

**主要功能**：
- 记录执行结果
- 计算效果指标
- 分析策略有效性

## 🔧 配置说明

配置文件示例 (`config.json`):

```json
{
  "shopify": {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "shop_domain": "your_shop.myshopify.com"
  },
  "email": {
    "provider": "sendgrid",
    "api_key": "your_email_api_key"
  },
  "decision_engine": {
    "enable_ml": false,
    "default_priority": "medium"
  }
}
```

## 📝 使用示例

### 示例1: 处理单个聚类

```python
from operation_agent import OperationAgent
from operation_agent.models.cluster_analysis import ClusterAnalysis

agent = OperationAgent()

# 从聚类结果文件加载
cluster_analysis = load_cluster_analysis("cluster_0")

# 处理并执行
result = agent.process_cluster_analysis(cluster_analysis)
```

### 示例2: 批量处理多个聚类

```python
cluster_analyses = load_all_cluster_analyses()

result = agent.process_multiple_clusters(cluster_analyses)
```

### 示例3: 添加自定义策略

```python
from operation_agent.models.strategy import Strategy, StrategyType
from operation_agent.models.action import Action, ActionType

# 创建自定义策略
strategy = Strategy(
    strategy_id="custom_001",
    strategy_type=StrategyType.CONVERSION,
    name="自定义转化策略",
    description="针对特定场景的转化策略",
    conditions={
        "purchase_stage": "对比阶段",
        "min_intent_score": 0.5,
    },
    actions=[
        Action(
            action_id="action_001",
            action_type=ActionType.SEND_EMAIL,
            parameters={"template": "custom_template"},
        ),
    ],
)

# 添加到Agent
agent.add_strategy(strategy)
```

## 🔄 工作流程

```
1. 聚类分析结果输入
   ↓
2. 决策引擎分析并生成动作
   ↓
3. 策略生成器生成策略（可选）
   ↓
4. 动作执行器执行动作
   ↓
5. 反馈循环记录效果
   ↓
6. 持续优化策略
```

## ⚠️ 注意事项

1. **API密钥安全**：请妥善保管API密钥，不要提交到代码仓库
2. **执行限制**：注意第三方服务的API限流
3. **错误处理**：所有动作都有重试机制，但需要监控失败情况
4. **效果监控**：定期检查策略效果，及时调整

## 🚧 待实现功能

- [ ] 完整的Shopify API集成
- [ ] 邮件服务实际集成
- [ ] 短信服务实际集成
- [ ] 任务队列系统（异步执行）
- [ ] 数据库存储（执行历史）
- [ ] 监控和告警系统
- [ ] A/B测试框架
- [ ] 机器学习优化

## 📚 相关文档

- [运营Agent转型方案](../OPERATION_AGENT_TRANSFORMATION.md)
- [产品需求文档](../../PRD.md)


