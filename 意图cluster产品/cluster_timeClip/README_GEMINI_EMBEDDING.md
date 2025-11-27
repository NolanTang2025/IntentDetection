# Gemini Embedding 聚类说明

## 概述

店铺39使用Gemini API进行文本embedding聚类，其他店铺继续使用数值特征聚类。

## 安装依赖

```bash
pip install google-generativeai python-dotenv
```

## 设置API密钥

### 方法1: 使用.env文件（推荐）

1. 复制 `.env.example` 为 `.env`：
```bash
cd 意图cluster产品
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的API密钥：
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

3. 代码会自动从 `.env` 文件读取API密钥

### 方法2: 环境变量

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### 方法3: 在代码中设置

修改 `automated_analysis.py` 或直接传递API密钥：

```python
clusterer = BehaviorIntentClusterer(
    intent_change_threshold=0.3,
    gemini_api_key="YOUR_GEMINI_API_KEY"
)
```

**注意**: `.env` 文件已添加到 `.gitignore`，不会被提交到版本控制。

## 使用方法

### 运行自动化分析（所有店铺）

```bash
cd 意图cluster产品
python3 automated_analysis.py
```

店铺39会自动使用Gemini embedding，其他店铺使用默认方法。

### 单独运行店铺39

```bash
cd 意图cluster产品/cluster_timeClip
python3 -c "
from behavior_intent_clustering import BehaviorIntentClusterer
import os

clusterer = BehaviorIntentClusterer(
    gemini_api_key=os.getenv('GEMINI_API_KEY')
)
clusterer.analyze(
    input_file='../data_extract/extracted_data_shop_39.json',
    shop_id=39
)
"
```

## Embedding参数

- **模型**: `models/embedding-001`
- **任务类型**: `CLUSTERING` (用于聚类任务)
- **维度**: 768维向量

## 工作原理

1. 从原始数据中提取文本（从output字段的JSON中提取core_interests、key_attributes等）
2. 使用Gemini API为每个文本生成embedding向量
3. 对embedding向量进行标准化
4. 使用K-Means进行聚类
5. 生成聚类标签和业务洞察

## 注意事项

- 如果Gemini API不可用，店铺39会自动回退到默认的数值特征聚类
- API调用有速率限制，代码中已添加延迟以避免限流
- Embedding生成可能需要一些时间，取决于数据量

