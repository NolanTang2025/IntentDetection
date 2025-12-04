# 用户聚类分析

这个脚本用于对不同店铺的用户进行聚类分析。

## 功能

1. **数据读取**: 自动读取 `data_extract` 目录下所有店铺的数据文件
2. **用户聚合**: 按 `user_id` 聚合每个用户的所有 session 数据
3. **文本提取**: 从 JSON 格式的意图数据中提取关键信息，转换为文本描述
4. **Embedding生成**: 使用 Google Gemini API 生成用户意图的 embedding 向量
5. **聚类分析**: 使用 K-means 算法对每个店铺的用户进行聚类

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置 API 密钥

设置环境变量：

```bash
export GEMINI_API_KEY='your-api-key-here'
```

或者在脚本中直接修改 `GEMINI_API_KEY` 变量。

## 使用方法

```bash
python user_clustering.py
```

## 输出结果

脚本会生成 `clustering_results.json` 文件，包含：

- 每个店铺的聚类结果
- 每个用户的聚类标签
- 聚类质量指标（轮廓系数等）
- 各聚类的用户分布

## 数据格式

输入数据文件格式：`extracted_data_shop_{shop_id}.json`

每个文件应包含以下字段：
- `user_id`: 用户ID
- `session_id`: 会话ID
- `timestamp`: 时间戳
- `output`: JSON格式的用户意图数据

## 聚类方法

当前使用 K-means 聚类算法，聚类数会根据用户数量自动调整。

## 注意事项

- 确保已安装所有依赖包
- 需要有效的 Gemini API 密钥
- API 调用有速率限制，脚本已添加延迟以避免限流
- 如果某个店铺的用户数少于2，将跳过该店铺的聚类

