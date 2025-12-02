# 用户意图数据处理流程

本文档详细说明从输入原始用户意图数据到最终在可视化仪表板上显示的完整数据处理流程。

## 📊 整体流程图

```
原始数据输入
    ↓
[步骤1] 数据提取 (extract_data.py)
    ↓
结构化JSON数据 (extracted_data_shop_{id}.json)
    ↓
[步骤2] 聚类分析 (behavior_intent_clustering.py)
    ↓
聚类结果 (business_cluster_results_shop_{id}.json)
    ↓
[步骤3] 聚类结果分析 (cluster_analysis.py)
    ↓
聚类统计报告 (cluster_analysis_shop_{id}.json)
    ↓
[步骤4] 用户画像分析 (business_driven_portrait_analyzer.py)
    ↓
业务洞察 (business_driven_insights_shop_{id}.json)
    ↓
[步骤5] 前端数据更新 (update_data.py)
    ↓
前端数据文件 (data_shop_{id}.js)
    ↓
[步骤6] 多店铺数据合并 (create_multi_shop_dashboard.py)
    ↓
多店铺数据文件 (multi_shop_data.js)
    ↓
可视化仪表板 (dashboard.js + index.html)
    ↓
最终展示
```

---

## 🔄 详细步骤说明

### 步骤1: 数据提取 (Data Extraction)

**脚本**: `data_extract/extract_data.py`

**输入**:
- 原始CSV文件: `raw_data1126.csv` (或其他原始数据文件)
- 包含字段: `name`, `output`, `userId`, `sessionId`, `timestamp`

**处理过程**:
1. 从CSV中筛选 `name == "analyze_intent_and_rate_tags"` 的记录
2. 提取 `output` 字段，只保留到 `match_analysis` 部分结束
3. 清理和解析JSON格式（处理转义字符、代码块标记等）
4. 提取关键字段: `userId`, `sessionId`, `timestamp`, `output`

**输出**:
- `data_extract/extracted_data_shop_{shop_id}.json`
- 格式示例:
```json
[
  {
    "userId": "user123",
    "sessionId": "session456",
    "timestamp": "2024-01-01T10:00:00Z",
    "output": "{\"intent\": {...}, \"intent_score\": 0.8, ...}"
  }
]
```

**关键功能**:
- `extract_output_until_match_analysis()`: 提取output到match_analysis部分
- 处理JSON转义和代码块标记
- 按店铺ID分组保存

---

### 步骤2: 聚类分析 (Clustering Analysis)

**脚本**: `cluster_timeClip/behavior_intent_clustering.py`

**输入**:
- `data_extract/extracted_data_shop_{shop_id}.json`

**处理过程**:

#### 2.1 时间切片 (Time Segmentation)
- 基于意图变化进行智能分段
- 当用户意图变化超过阈值（默认0.3）时创建新片段
- 考虑时间间隔（默认10分钟）和不活跃时间（默认15分钟）
- 每个用户可能产生多个意图片段

#### 2.2 特征提取 (Feature Extraction)
从每个意图片段中提取特征:

**行为特征**:
- `duration_minutes`: 片段持续时间
- `record_count`: 交互次数
- `intent_score`: 意图强度（平均值）

**业务特征** (从output JSON中提取):
- `purchase_stage`: 购买阶段 (0=浏览, 1=对比, 2=决策)
- `price_sensitivity`: 价格敏感度 (0=预算型, 1=中端, 2=高端)
- `engagement_level`: 参与度 (基于时长和交互次数)
- `product_preference`: 产品偏好 (编码为数字)
- `concern_focus`: 关注点 (编码为数字)
- `core_need`: 核心需求 (编码为数字)

**特殊处理**:
- 店铺39: 使用Gemini API进行文本embedding聚类
- 其他店铺: 使用TF-IDF + K-Means聚类

#### 2.3 聚类算法 (Clustering)
- 使用K-Means算法进行聚类
- 特征标准化 (StandardScaler)
- 自动确定聚类数量（基于数据量）

#### 2.4 聚类标签生成 (Label Generation)
为每个聚类生成业务标签:
- `short_label`: 简短标签（如"激活阶段·中紧迫"）
- `full_label`: 完整标签（如"激活阶段·中紧迫·激活导向"）
- `cluster_name`: 聚类名称
- `user_segment_name`: 用户分群名称

**输出**:
- `cluster_timeClip/business_cluster_results_shop_{shop_id}.json`
- `cluster_timeClip/business_cluster_results_shop_{shop_id}.csv`

**输出格式**:
```json
{
  "segments": [
    {
      "segment_id": "user123_session456_seg1",
      "user_id": "user123",
      "session_id": "session456",
      "start_time": "2024-01-01T10:00:00Z",
      "end_time": "2024-01-01T10:15:00Z",
      "duration_minutes": 15.0,
      "record_count": 50,
      "intent_score": 0.75,
      "business_cluster": "1",
      "purchase_stage": 1,
      "text": "用户行为文本摘要"
    }
  ],
  "clustering": {
    "n_clusters": 5,
    "cluster_labels": {
      "1": {
        "short_label": "激活阶段·中紧迫",
        "full_label": "激活阶段·中紧迫·激活导向",
        "cluster_name": "激活阶段·中紧迫",
        "user_segment_name": "激活阶段·中紧迫"
      }
    },
    "cluster_counts": {"1": 10, "2": 8, ...}
  }
}
```

---

### 步骤3: 聚类结果分析 (Cluster Analysis)

**脚本**: `cluster_timeClip/cluster_analysis.py` (通过 `automated_analysis.py` 调用)

**输入**:
- `cluster_timeClip/business_cluster_results_shop_{shop_id}.json`

**处理过程**:
1. 加载聚类结果
2. 计算统计信息:
   - 总片段数
   - 总用户数
   - 聚类数量
   - 平均每个用户的片段数
   - 聚类分布

**输出**:
- `cluster_timeClip/cluster_analysis_shop_{shop_id}.json`

**输出格式**:
```json
{
  "shop_id": "YUP",
  "analysis_date": "2024-01-01T12:00:00",
  "statistics": {
    "total_segments": 100,
    "total_users": 50,
    "n_clusters": 5,
    "avg_segments_per_user": 2.0
  },
  "cluster_distribution": {"1": 20, "2": 15, ...},
  "cluster_labels": {...}
}
```

---

### 步骤4: 用户画像分析 (User Portrait Analysis)

**脚本**: `user_portrait_analysis/business_driven_portrait_analyzer.py`

**输入**:
- `cluster_timeClip/business_cluster_results_shop_{shop_id}.json`

**处理过程**:

#### 4.1 聚类特征分析
对每个聚类计算:
- 平均持续时间
- 平均交互次数
- 平均意图强度
- 用户数量
- 片段数量

#### 4.2 业务特征提取
从聚类标签中提取业务特征:
- 阶段 (stage): 浏览/对比/决策/激活等
- 价格敏感度 (price_sensitivity)
- 参与度 (engagement)
- 产品偏好 (product_preference)
- 关注点 (concern)
- 核心需求 (core_need)

**金融场景特殊处理** (YUP等):
- `behavior`: 行为模式（激活导向/KYC导向/支付导向等）
- `urgency`: 紧迫度（高/中/低）
- `main_activity`: 主要活动
- `kyc_status`: KYC状态
- `transaction_status`: 交易状态

#### 4.3 营销策略生成
为每个聚类生成差异化营销策略:

**策略类型**:
1. `marketing_strategy`: 营销策略（数组）
2. `product_recommendations`: 产品/服务推荐（数组）
3. `conversion_optimization`: 转化优化建议（数组）
4. `content_strategy`: 内容策略（数组）
5. `campaign_differentiation`: 活动差异化建议（数组）
6. `pricing_strategy`: 定价策略（数组）

**策略生成逻辑**:
- 基于聚类特征自动生成
- 针对金融场景和电商场景有不同的策略模板
- 使用AI生成（如果配置了API）

**输出**:
- `user_portrait_analysis/business_driven_insights_shop_{shop_id}.json`
- `user_portrait_analysis/business_driven_insights_summary_shop_{shop_id}.csv`
- `user_portrait_analysis/business_driven_report_shop_{shop_id}.md`

**输出格式**:
```json
[
  {
    "cluster_id": "1",
    "cluster_name": "激活阶段·中紧迫",
    "full_label": "激活阶段·中紧迫·激活导向",
    "key_characteristics": {
      "user_count": 10,
      "segment_count": 15,
      "avg_duration_minutes": 14.75,
      "avg_interactions": 142,
      "avg_intent_score": 0.5
    },
    "marketing_strategy": [
      "【促进首单】提供新用户专享优惠...",
      "建立信任机制：展示平台安全性..."
    ],
    "product_recommendations": [
      "推荐低门槛高价值首单服务..."
    ],
    "conversion_optimization": [...],
    "content_strategy": [...],
    "campaign_differentiation": [...]
  }
]
```

---

### 步骤5: 前端数据更新 (Frontend Data Update)

**脚本**: `visualization_dashboard/update_data.py`

**输入**:
- `cluster_timeClip/business_cluster_results_shop_{shop_id}.json`
- `user_portrait_analysis/business_driven_insights_shop_{shop_id}.json`

**处理过程**:

#### 5.1 数据转换
将聚类结果和业务洞察转换为前端需要的格式:

**businessInsights** (业务洞察):
- 从 `business_driven_insights.json` 转换
- 包含每个聚类的完整信息和策略

**userPortraits** (用户画像):
- 从聚类结果中提取用户特征
- 生成用户画像数据

**stats** (统计信息):
- 总用户数
- 总片段数
- 聚类数量
- 平均意图强度等

**timeSeries** (时间序列):
- 按日期和小时统计用户画像分布
- 按日期和小时统计阶段分布

**userTrajectories** (用户轨迹):
- 每个用户的完整行为轨迹
- 包含所有片段的时间线
- 聚类分配信息

#### 5.2 数据格式化
- 转换为JavaScript对象格式
- 添加必要的元数据
- 处理时间格式

**输出**:
- `visualization_dashboard/data_shop_{shop_id}.js`

**输出格式**:
```javascript
const businessInsights = [
  {
    cluster_id: "1",
    cluster_name: "激活阶段·中紧迫",
    full_label: "激活阶段·中紧迫·激活导向",
    key_characteristics: {...},
    marketing_strategy: [...],
    product_recommendations: [...],
    ...
  }
];

const userPortraits = [...];
const stats = {...};
const timeSeries = [...];
const userTrajectories = [...];
```

---

### 步骤6: 多店铺数据合并 (Multi-Shop Data Merge)

**脚本**: `visualization_dashboard/create_multi_shop_dashboard.py`

**输入**:
- 所有店铺的 `data_shop_{shop_id}.js` 文件

**处理过程**:
1. 读取所有店铺的数据文件
2. 合并到一个统一的 `shopData` 对象中
3. 按店铺ID组织数据

**输出**:
- `visualization_dashboard/multi_shop_data.js`

**输出格式**:
```javascript
const shopData = {
  "YUP": {
    businessInsights: [...],
    userPortraits: [...],
    stats: {...},
    timeSeries: [...],
    userTrajectories: [...]
  },
  "28": {...},
  "29": {...},
  ...
};
```

---

### 步骤7: 前端可视化 (Frontend Visualization)

**文件**:
- `visualization_dashboard/index.html`
- `visualization_dashboard/dashboard.js`
- `visualization_dashboard/i18n.js`
- `visualization_dashboard/multi_shop_data.js`

**处理过程**:

#### 7.1 数据加载
- 从 `multi_shop_data.js` 加载数据
- 根据选择的店铺ID获取对应数据

#### 7.2 页面渲染
- **总览页面**: 显示统计信息和关键洞察
- **聚类分析页面**: 显示所有聚类及其详情
- **用户轨迹页面**: 显示用户行为轨迹时间线

#### 7.3 交互功能
- 店铺切换
- 聚类详情展开/收起
- 用户轨迹筛选和查看
- 语言切换（中英文）

**关键函数**:
- `loadFinancialClusters()`: 加载聚类数据
- `showFinancialClusterDetails()`: 显示聚类详情
- `renderFinancialUserTrajectories()`: 渲染用户轨迹
- `renderUserTrajectoryTimeline()`: 渲染时间线

---

## 🚀 自动化执行

### 使用自动化脚本

**主脚本**: `automated_analysis.py`

**执行方式**:
```bash
cd 意图cluster产品
python3 automated_analysis.py
```

或使用快速启动脚本:
```bash
# Linux/Mac
./run_analysis.sh

# Windows
run_analysis.bat
```

**自动化流程**:
1. 对每个店铺执行步骤1-5
2. 执行步骤6（多店铺数据合并）
3. 生成总结报告 (`analysis_summary.json`)

**配置**:
编辑 `automated_analysis.py` 中的 `SHOPS` 变量:
```python
SHOPS = [28, 29, 39, 49, 53, 'YUP']
```

---

## 📁 文件结构

```
意图cluster产品/
├── data_extract/                          # 步骤1: 数据提取
│   ├── extract_data.py
│   ├── raw_data1126.csv                   # 原始数据输入
│   └── extracted_data_shop_{id}.json      # 输出
│
├── cluster_timeClip/                      # 步骤2-3: 聚类分析
│   ├── behavior_intent_clustering.py      # 聚类主脚本
│   ├── business_driven_clustering.py      # 业务驱动聚类
│   ├── cluster_analysis.py                # 聚类结果分析
│   ├── business_cluster_results_shop_{id}.json  # 聚类结果
│   └── cluster_analysis_shop_{id}.json   # 聚类统计
│
├── user_portrait_analysis/                # 步骤4: 用户画像
│   ├── business_driven_portrait_analyzer.py
│   ├── business_driven_insights_shop_{id}.json   # 业务洞察
│   └── business_driven_report_shop_{id}.md      # 报告
│
├── visualization_dashboard/                # 步骤5-7: 前端
│   ├── update_data.py                     # 数据更新脚本
│   ├── create_multi_shop_dashboard.py     # 多店铺合并
│   ├── data_shop_{id}.js                  # 单店铺数据
│   ├── multi_shop_data.js                 # 多店铺数据
│   ├── dashboard.js                       # 前端逻辑
│   ├── index.html                         # 主页面
│   └── i18n.js                           # 国际化
│
└── automated_analysis.py                 # 自动化主脚本
```

---

## 🔧 关键参数配置

### 聚类参数
- `gap_threshold_minutes`: 时间间隔阈值（默认10分钟）
- `inactivity_threshold_minutes`: 不活跃阈值（默认15分钟）
- `intent_change_threshold`: 意图变化阈值（默认0.3）

### API配置
- `GEMINI_API_KEY`: Gemini API密钥（用于店铺39的embedding）

### 数据路径
- 所有路径都是相对路径，基于脚本所在目录
- 确保脚本在正确的目录下运行

---

## 📊 数据流转示例

### 示例: 处理YUP店铺数据

1. **输入**: `raw_data1126.csv` (包含YUP用户行为数据)
2. **步骤1**: 提取 → `extracted_data_shop_YUP.json` (100条记录)
3. **步骤2**: 聚类 → `business_cluster_results_shop_YUP.json` (5个聚类, 50个片段)
4. **步骤3**: 分析 → `cluster_analysis_shop_YUP.json` (统计信息)
5. **步骤4**: 画像 → `business_driven_insights_shop_YUP.json` (5个聚类的策略)
6. **步骤5**: 更新 → `data_shop_YUP.js` (前端数据)
7. **步骤6**: 合并 → `multi_shop_data.js` (包含YUP数据)
8. **步骤7**: 展示 → 在dashboard中查看YUP的聚类和策略

---

## ⚠️ 注意事项

1. **数据格式**: 确保原始数据包含必要的字段（userId, sessionId, timestamp, output）
2. **API密钥**: 店铺39需要Gemini API密钥（在.env文件中配置）
3. **文件路径**: 确保所有脚本在正确的目录下运行
4. **依赖安装**: 需要安装pandas, numpy, scikit-learn等依赖
5. **数据一致性**: 确保每个步骤的输出格式正确，以便下一步处理

---

## 🔍 故障排除

### 问题1: 数据提取失败
- 检查原始CSV文件是否存在
- 检查CSV文件格式是否正确
- 确保包含 `name == "analyze_intent_and_rate_tags"` 的记录

### 问题2: 聚类分析失败
- 检查提取的数据文件是否存在
- 确保数据包含有效的output字段
- 检查JSON格式是否正确

### 问题3: 用户画像分析失败
- 确保聚类结果文件已生成
- 检查聚类结果文件格式是否正确

### 问题4: 前端数据更新失败
- 确保聚类结果和业务洞察文件都存在
- 检查文件路径是否正确

---

## 📝 总结

整个数据处理流程是一个完整的管道，从原始数据到最终可视化展示，每个步骤都有明确的输入和输出。使用 `automated_analysis.py` 可以自动化执行所有步骤，大大简化了数据处理流程。

