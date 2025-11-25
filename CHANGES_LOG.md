# 代码改动日志

本文档记录了所有代码改动，方便后续维护。

## 改动概述

本次改动主要实现了以下功能：
1. **多语言支持（中英文切换）** - 为整个仪表盘添加了完整的中英文双语支持
2. **Insights页面删除** - 移除了业务洞察页面及其相关代码
3. **UI优化** - 修复了z-index层级问题，删除了视频标题

---

## 文件改动列表

### 1. 新增文件

#### `意图cluster产品/visualization_dashboard/i18n.js`
**功能**: 多语言资源文件和翻译函数

**主要内容**:
- 定义了完整的中英文翻译映射（`i18n` 对象）
- 实现了翻译函数 `t(key)` - 支持嵌套键访问
- 实现了语言切换函数 `switchLanguage(lang)`
- 实现了页面语言更新函数 `updatePageLanguage()`
- 实现了聚类名称翻译函数 `translateClusterName(name)`
- 实现了关键特征翻译函数 `translateKeyCharacteristic(charString)`
- 实现了策略文本翻译函数 `translateStrategyText(text)`
- 聚类名称翻译映射表 `clusterNameTranslations`

**关键翻译映射**:
```javascript
// 聚类名称翻译
clusterNames: {
    '快速浏览·低紧迫': 'Quick Browse·Low Urgency',
    '单次浏览·中紧迫': 'Single Browse·Medium Urgency',
    // ... 更多映射
}

// 策略文本翻译
strategyTexts: {
    '【教育引导】用户处于早期浏览阶段，需要教育性内容': '【Educational Guidance】Users are in early browsing stage...',
    // ... 更多映射
}

// 关键特征字段翻译
keyCharacteristics: {
    '用户规模': 'User Scale',
    '平均浏览时长': 'Average Browsing Duration',
    // ... 更多映射
}
```

---

### 2. 修改文件

#### `意图cluster产品/visualization_dashboard/index.html`

**改动内容**:

1. **添加语言切换器**
```html
<!-- 语言切换器 -->
<div class="language-switcher">
    <button class="lang-btn" id="langBtn" title="Switch Language">
        <svg>...</svg>
        <span id="currentLang">中文</span>
    </button>
</div>
```

2. **为所有静态文本添加 `data-i18n` 属性**
   - 导航栏链接
   - 页面标题和副标题
   - 按钮文本
   - 页脚链接
   - 所有UI元素文本

3. **删除Insights页面**
   - 移除了导航栏中的"业务洞察"链接
   - 移除了整个 `<div id="insights" class="tab-content">` 及其内容
   - 移除了首页快速操作中的Insights卡片

4. **添加i18n.js脚本引用**
```html
<script src="i18n.js"></script>
<script src="data.js"></script>
<script src="dashboard.js"></script>
```

---

#### `意图cluster产品/visualization_dashboard/dashboard.js`

**主要改动**:

1. **集成翻译函数到所有动态内容生成**
   - `loadHomepage()` - 首页内容
   - `loadOverview()` - 总览页面图表数据标签翻译
   - `loadUserAnalysisPage()` - 用户分析页面
   - `loadJourneyPage()` - 转化分析页面
   - `showClusterDetails()` - 聚类详情
   - `loadPortraits()` - 用户画像
   - `renderUserTrajectories()` - 用户轨迹
   - `renderUserTrajectoryTimeline()` - 用户轨迹时间线
   - `createScenarioHeatmap()` - 场景偏好热力图
   - `renderPricePreference()` - 价格偏好显示
   - `generateJourneyHTML()` - 转化路径HTML生成

2. **图表数据标签翻译**
```javascript
// 购买阶段分布 - 翻译阶段名称
const stageTranslations = {
    '浏览阶段': t('stages.browsing'),
    '对比阶段': t('stages.comparison'),
    '决策阶段': t('stages.decision')
};

// 价格偏好分布 - 使用translateKeyCharacteristic翻译
let translatedPrice = price;
if (currentLanguage === 'en' && typeof translateKeyCharacteristic === 'function') {
    const translated = translateKeyCharacteristic(`价格敏感度: ${price}`);
    translatedPrice = translated.split(':')[1]?.trim() || price;
}

// 核心关注点 - 使用translateKeyCharacteristic翻译
let translatedConcern = concern;
if (currentLanguage === 'en' && typeof translateKeyCharacteristic === 'function') {
    const translated = translateKeyCharacteristic(`关注点: ${concern}`);
    translatedConcern = translated.split(':')[1]?.trim() || concern;
}
```

3. **策略文本翻译集成**
```javascript
// 所有策略列表都使用translateStrategyText
${insight.marketing_strategy.map(s => {
    const translated = typeof translateStrategyText === 'function' 
        ? translateStrategyText(s) 
        : s;
    return `<li>${translated}</li>`;
}).join('')}
```

4. **删除loadInsights函数**
   - 完全移除了 `loadInsights()` 函数及其所有内容
   - 移除了 `showTab()` 中的 `insights` case

5. **聚类名称显示**
```javascript
// 使用getClusterDisplayName获取翻译后的聚类名称
${getClusterDisplayName(insight.user_segment_name)}
```

---

#### `意图cluster产品/visualization_dashboard/styles.css`

**改动内容**:

1. **添加语言切换器样式**
```css
.language-switcher {
    margin-left: auto; /* Pushes it to the right */
}

.lang-btn {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    color: var(--text);
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.lang-btn:hover {
    background: var(--hover-bg);
    border-color: var(--accent);
}
```

2. **添加语言切换过渡效果**
```css
.dashboard-main {
    transition: opacity 0.15s ease;
}
```

---

#### `intent_interactive_demo.html`

**改动内容**:

1. **修复z-index层级问题**
```css
.completion-overlay {
    z-index: 10001; /* 从10000改为10001，确保在视频插件之上 */
}
```

2. **删除视频标题**
```html
<!-- 删除了以下内容 -->
<div class="video-title">产品视频</div>
```

---

## 翻译映射表

### 导航栏
- `nav.home`: 首页 / Home
- `nav.overview`: 总览 / Overview
- `nav.journey`: 转化分析 / Conversion
- `nav.clusters`: 用户分析 / User Analysis

### 购买阶段
- `stages.browsing`: 浏览阶段 / Browsing
- `stages.comparison`: 对比阶段 / Comparison
- `stages.decision`: 决策阶段 / Decision

### 数据字段
- `dataFields.userScale`: 用户规模 / User Scale
- `dataFields.avgDuration`: 平均浏览时长 / Average Browsing Duration
- `dataFields.purchaseStage`: 购买阶段 / Purchase Stage
- `dataFields.priceSensitivity`: 价格敏感度 / Price Sensitivity
- 等等...

### 策略相关
- `strategy.marketing`: 营销策略建议 / Marketing Strategy Recommendations
- `strategy.product`: 产品推荐 / Product Recommendations
- `strategy.conversion`: 转化优化建议 / Conversion Optimization Suggestions
- 等等...

### 聚类名称
所有聚类名称都通过 `i18n.en.clusterNames` 对象进行映射，例如：
- `快速浏览·低紧迫` → `Quick Browse·Low Urgency`
- `单次浏览·中紧迫` → `Single Browse·Medium Urgency`

---

## 核心函数说明

### 1. `t(key)` - 翻译函数
**功能**: 根据当前语言获取翻译文本
**用法**: `t('nav.home')` 或 `t('stages.browsing')`
**支持**: 嵌套键访问，如 `t('home.dimensions.purchaseStage.title')`

### 2. `switchLanguage(lang)` - 语言切换
**功能**: 切换当前语言（'zh' 或 'en'）
**行为**: 
- 更新 `currentLanguage` 全局变量
- 保存到 `localStorage`
- 调用 `updatePageLanguage()` 更新页面

### 3. `updatePageLanguage()` - 更新页面语言
**功能**: 更新所有带有 `data-i18n` 属性的元素
**行为**:
- 遍历所有 `[data-i18n]` 元素
- 更新文本内容
- 调用 `updateDynamicContent()` 重新渲染动态内容

### 4. `translateClusterName(name)` - 翻译聚类名称
**功能**: 翻译聚类名称，自动移除emoji
**逻辑**:
- 中文模式：移除emoji后返回
- 英文模式：从 `i18n.en.clusterNames` 查找翻译

### 5. `translateKeyCharacteristic(charString)` - 翻译关键特征
**功能**: 翻译格式为"字段名: 值"的关键特征字符串
**处理**:
- 翻译字段名（如"用户规模" → "User Scale"）
- 翻译值中的中文（如"浏览阶段" → "Browsing"）
- 处理单位（如"秒" → "s"）

### 6. `translateStrategyText(text)` - 翻译策略文本
**功能**: 翻译策略建议文本
**处理**:
- 首先尝试完整匹配 `i18n.en.strategyTexts`
- 如果没有匹配，使用部分替换规则
- 翻译标签（如"【教育引导】" → "【Educational Guidance】"）
- 翻译产品偏好（如"H02偏好" → "H02 Preference"）

---

## 维护指南

### 添加新的翻译

1. **在 `i18n.js` 中添加翻译**
```javascript
// 中文
zh: {
    newSection: {
        title: '新标题',
        description: '新描述'
    }
}

// 英文
en: {
    newSection: {
        title: 'New Title',
        description: 'New Description'
    }
}
```

2. **在 HTML 中使用 `data-i18n` 属性**
```html
<h2 data-i18n="newSection.title">新标题</h2>
<p data-i18n="newSection.description">新描述</p>
```

3. **在 JavaScript 中使用 `t()` 函数**
```javascript
const title = t('newSection.title');
```

### 添加新的聚类名称翻译

在 `i18n.js` 的 `en.clusterNames` 对象中添加：
```javascript
clusterNames: {
    '新聚类名称': 'New Cluster Name',
    // ...
}
```

### 添加新的策略文本翻译

在 `i18n.js` 的 `en.strategyTexts` 对象中添加：
```javascript
strategyTexts: {
    '【新标签】中文内容': '【New Label】English Content',
    // ...
}
```

### 添加新的数据字段翻译

在 `i18n.js` 的 `en.keyCharacteristics` 对象中添加：
```javascript
keyCharacteristics: {
    '新字段名': 'New Field Name',
    // ...
}
```

在 `translateKeyCharacteristic` 函数的 `valueTranslations` 对象中添加值翻译：
```javascript
const valueTranslations = {
    '新值': 'New Value',
    // ...
}
```

---

## 注意事项

1. **脚本加载顺序**
   - `i18n.js` 必须在 `dashboard.js` 之前加载
   - 确保在 `index.html` 中按正确顺序引用

2. **动态内容更新**
   - 所有动态生成的内容都需要在语言切换时重新渲染
   - 使用 `updateDynamicContent()` 函数触发重新渲染

3. **聚类名称处理**
   - 聚类名称可能包含emoji，使用 `removeEmojiFromClusterName()` 处理
   - 翻译时先移除emoji，再查找翻译

4. **策略文本翻译**
   - 策略文本翻译使用部分匹配和替换规则
   - 如果添加新的策略文本，建议先在 `strategyTexts` 中添加完整映射

5. **图表数据翻译**
   - 图表数据标签需要在数据准备阶段翻译
   - 确保翻译后的标签作为图表的 `labels` 使用

---

## 测试检查清单

- [ ] 切换语言时，所有静态文本正确更新
- [ ] 切换语言时，所有动态生成的内容正确更新
- [ ] 图表中的标签正确翻译
- [ ] 聚类名称正确翻译
- [ ] 策略文本正确翻译
- [ ] 关键特征字段和值正确翻译
- [ ] 页脚链接正确翻译
- [ ] 语言选择保存在localStorage中
- [ ] 刷新页面后语言选择保持

---

## 版本信息

- **改动日期**: 2025年
- **改动范围**: 多语言支持、UI优化、功能删除
- **影响文件**: 
  - `i18n.js` (新增)
  - `index.html` (修改)
  - `dashboard.js` (修改)
  - `styles.css` (修改)
  - `intent_interactive_demo.html` (修改)

---

## 后续优化建议

1. **翻译完整性检查**
   - 定期检查是否有遗漏的中文文本
   - 确保所有用户可见的文本都有翻译

2. **翻译质量优化**
   - 可以请专业翻译人员审核英文翻译
   - 确保专业术语翻译准确

3. **性能优化**
   - 如果翻译数据很大，可以考虑按需加载
   - 缓存翻译结果避免重复计算

4. **扩展性**
   - 如果需要支持更多语言，可以扩展 `i18n` 对象
   - 添加语言检测功能（根据浏览器语言自动选择）

---

## 联系信息

如有问题或需要进一步维护，请参考本文档或联系开发团队。

