# 自动化聚类分析脚本使用说明

## 概述

`automated_analysis.py` 是一个完整的自动化脚本，可以为所有店铺执行完整的聚类分析流程。

## 功能

脚本会自动为每个店铺执行以下步骤：

1. **数据提取检查** - 检查数据文件是否存在
2. **聚类分析** - 基于意图变化进行用户行为聚类
3. **聚类结果分析** - 生成聚类统计和分析报告
4. **用户画像分析** - 生成业务洞察和营销策略
5. **前端数据更新** - 更新可视化仪表板数据
6. **多店铺数据合并** - 创建支持多店铺切换的数据文件

## 使用方法

### 方法1: 直接运行Python脚本

```bash
cd 意图cluster产品
python3 automated_analysis.py
```

### 方法2: 使用快速启动脚本（推荐）

**Linux/Mac:**
```bash
cd 意图cluster产品
./run_analysis.sh
```

**Windows:**
```cmd
cd 意图cluster产品
run_analysis.bat
```

### 配置店铺列表

编辑 `automated_analysis.py` 文件，修改 `SHOPS` 变量：

```python
SHOPS = [28, 29, 39, 49, 53]  # 修改为你需要的店铺ID列表
```

## 输出文件

### 每个店铺生成的文件

#### 聚类结果
- `cluster_timeClip/business_cluster_results_shop_{shop_id}.json`
- `cluster_timeClip/business_cluster_results_shop_{shop_id}.csv`
- `cluster_timeClip/cluster_analysis_shop_{shop_id}.json`

#### 业务洞察
- `user_portrait_analysis/business_driven_insights_shop_{shop_id}.json`
- `user_portrait_analysis/business_driven_insights_summary_shop_{shop_id}.csv`
- `user_portrait_analysis/business_driven_report_shop_{shop_id}.md`

#### 前端数据
- `visualization_dashboard/data_shop_{shop_id}.js`

### 多店铺数据
- `visualization_dashboard/multi_shop_data.js` - 包含所有店铺的数据

### 总结报告
- `analysis_summary.json` - 包含所有店铺的处理结果和统计信息

## 执行流程

```
开始
  ↓
对每个店铺:
  ├─ 检查数据文件
  ├─ 聚类分析
  ├─ 聚类结果分析
  ├─ 用户画像分析
  └─ 更新前端数据
  ↓
创建多店铺数据
  ↓
生成总结报告
  ↓
结束
```

## 日志输出

脚本会输出详细的执行日志，包括：
- ✅ 成功步骤
- ❌ 失败步骤
- ⚠️ 警告信息
- ℹ️ 一般信息

## 错误处理

- 如果某个店铺的数据文件不存在，会跳过该店铺
- 如果某个步骤失败，会继续执行后续步骤
- 所有错误信息都会记录在日志中

## 性能

- 处理时间取决于数据量
- 每个店铺大约需要 10-30 秒
- 所有店铺总耗时通常在 1-5 分钟

## 注意事项

1. **数据文件**：确保 `data_extract/extracted_data_shop_{shop_id}.json` 文件存在
2. **Python环境**：需要安装以下依赖：
   - pandas
   - numpy
   - scikit-learn
   - json
3. **文件权限**：确保脚本有读写权限

## 示例输出

```
================================================================================
自动化聚类分析系统
================================================================================
开始时间: 2025-11-26 16:51:24
处理店铺: 28, 29, 39, 49, 53
================================================================================

[16:51:24] ℹ️ 开始处理店铺 28
[16:51:24] ✅ 店铺 28: 数据文件已存在，包含 144 条记录
[16:51:24] ℹ️ 店铺 28: 开始聚类分析...
[16:51:30] ✅ 店铺 28: 聚类结果已保存
[16:51:30] ✅ 店铺 28: 所有步骤完成

...

================================================================================
分析完成总结
================================================================================
成功: 5/5 个店铺
```

## 故障排除

### 问题：找不到数据文件
**解决**：确保 `data_extract/extracted_data_shop_{shop_id}.json` 文件存在

### 问题：聚类分析失败
**解决**：检查数据文件格式是否正确，确保包含必要的字段

### 问题：用户画像分析失败
**解决**：确保聚类结果文件已成功生成

### 问题：前端数据更新失败
**解决**：检查 `visualization_dashboard/update_data.py` 是否存在且可执行

## 后续步骤

执行完成后：
1. 打开 `visualization_dashboard/index.html` 查看结果
2. 使用店铺选择器切换不同店铺
3. 查看 `analysis_summary.json` 了解处理结果

