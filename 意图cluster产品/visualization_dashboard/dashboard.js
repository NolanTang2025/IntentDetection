// 仪表板主要功能脚本

// 标签页切换
function showTab(tabName, element) {
    // 隐藏所有标签页
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 移除所有导航链接的active状态
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // 显示选中的标签页
    document.getElementById(tabName).classList.add('active');
    
    // 激活对应的导航链接
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('data-tab') === tabName) {
            link.classList.add('active');
        }
    });
    
    // 更新页面标题和头部显示（使用多语言）
    const titleMap = {
        'home': typeof t === 'function' ? t('home.title') : '用户意图聚类分析平台',
        'overview': typeof t === 'function' ? t('header.overview') : '数据总览',
        'journey': typeof t === 'function' ? t('journey.title') : '转化分析',
        'clusters': typeof t === 'function' ? t('clusters.title') : '用户分析',
        'financial': '业务洞察'
    };
    
    const dashboardHeader = document.getElementById('dashboardHeader');
    if (dashboardHeader) {
        // 首页、转化分析、用户分析、金融市场分析页面不显示banner，直接展示主要内容
        if (tabName === 'home' || tabName === 'journey' || tabName === 'clusters' || tabName === 'financial') {
            dashboardHeader.style.display = 'none';
        } else {
            dashboardHeader.style.display = 'block';
            const headerTitle = dashboardHeader.querySelector('h1');
            if (headerTitle && titleMap[tabName]) {
                headerTitle.textContent = titleMap[tabName];
            }
            // 更新副标题
            const headerSubtitle = dashboardHeader.querySelector('.subtitle');
            if (headerSubtitle && tabName === 'overview') {
                headerSubtitle.textContent = typeof t === 'function' ? t('header.overviewSubtitle') : '实时用户意图分析与业务洞察';
            }
        }
    }
    
    // 金融市场分析tab：隐藏店铺选择器，显示YUP数据
    const shopSelectorContainer = document.getElementById('shopSelectorContainer');
    if (shopSelectorContainer) {
        if (tabName === 'financial') {
            shopSelectorContainer.style.display = 'none';
        } else {
            shopSelectorContainer.style.display = 'block';
        }
    }
    
    // 根据标签页加载相应内容
    loadTabContent(tabName);
    
    // 滚动到顶部
    if (tabName === 'home') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        window.scrollTo({ top: 64, behavior: 'smooth' });
    }
}

// 获取标签页显示名称
function getTabName(tabId) {
    const names = {
        'home': t('nav.home'),
        'overview': t('nav.overview'),
        'clusters': t('nav.clusters'),
        'portraits': t('clusters.portrait.title'),
    };
    return names[tabId] || tabId;
}

// 加载标签页内容
function loadTabContent(tabName) {
    // 添加加载动画
    const activeTab = document.querySelector('.tab-content.active');
    if (activeTab) {
        activeTab.style.opacity = '0';
        activeTab.style.transform = 'translateY(10px)';
    }
    
    setTimeout(() => {
        switch(tabName) {
            case 'home':
                loadHomepage();
                break;
            case 'overview':
                loadOverview();
                break;
            case 'journey':
                loadJourneyPage();
                break;
            case 'clusters':
                loadUserAnalysisPage();
                break;
            case 'financial':
                loadFinancialAnalysisPage();
                break;
        }
        
        // 恢复显示
        const newActiveTab = document.querySelector('.tab-content.active');
        if (newActiveTab) {
            newActiveTab.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            newActiveTab.style.opacity = '1';
            newActiveTab.style.transform = 'translateY(0)';
        }
    }, 150);
}

// 加载总览页面
function loadOverview() {
    if (typeof businessInsights === 'undefined' || !Array.isArray(businessInsights) || businessInsights.length === 0) {
        console.error('businessInsights 数据未加载或为空');
        // 显示提示信息
        const chartsGrid = document.querySelector('.charts-grid');
        if (chartsGrid) {
            chartsGrid.innerHTML = '<div class="no-data-message"><p>数据加载中，请稍候...</p></div>';
        }
        return;
    }
    
    // 用户聚类分布
    const clusterData = {};
    businessInsights.forEach(insight => {
        if (!insight || !insight.key_characteristics || !Array.isArray(insight.key_characteristics) || insight.key_characteristics.length === 0) {
            return;
        }
        const sizeMatch = insight.key_characteristics[0].match(/(\d+)\s*个意图片段/);
        const size = sizeMatch ? parseInt(sizeMatch[1]) : 0;
        if (size > 0 && !isNaN(size)) {
            const clusterLabel = currentLanguage === 'zh' ? `聚类 ${insight.cluster_id}` : `Cluster ${insight.cluster_id}`;
            clusterData[clusterLabel] = size;
        }
    });
    
    if (Object.keys(clusterData).length > 0) {
        createPieChart('clusterDistributionChart', clusterData, t('overview.charts.clusterDistribution'));
    }
    
    // 购买阶段分布
    const stageData = {};
    businessInsights.forEach(insight => {
        if (!insight || !insight.key_characteristics || !Array.isArray(insight.key_characteristics)) {
            return;
        }
        const stageMatch = insight.key_characteristics.find(c => c && c.includes('购买阶段'));
        if (stageMatch) {
            const stage = stageMatch.split(':')[1]?.trim() || '未知';
            const sizeMatch = insight.key_characteristics[0].match(/(\d+)\s*个意图片段/);
            const size = sizeMatch ? parseInt(sizeMatch[1]) : 0;
            if (stage && size > 0 && !isNaN(size)) {
                // 翻译阶段名称
                const stageTranslations = {
                    '浏览阶段': t('stages.browsing'),
                    '对比阶段': t('stages.comparison'),
                    '决策阶段': t('stages.decision'),
                    '未知': currentLanguage === 'zh' ? '未知' : 'Unknown'
                };
                const translatedStage = stageTranslations[stage] || stage;
                stageData[translatedStage] = (stageData[translatedStage] || 0) + size;
            }
        }
    });
    
    if (Object.keys(stageData).length > 0) {
        createDoughnutChart('purchaseStageChart', stageData, t('overview.charts.purchaseStage'));
    }
    
    // 价格偏好分布
    const priceData = {};
    businessInsights.forEach(insight => {
        if (!insight || !insight.key_characteristics || !Array.isArray(insight.key_characteristics)) {
            return;
        }
        const priceMatch = insight.key_characteristics.find(c => c && c.includes('价格敏感度'));
        if (priceMatch) {
            const price = priceMatch.split(':')[1]?.trim() || '未知';
            const sizeMatch = insight.key_characteristics[0].match(/(\d+)\s*个意图片段/);
            const size = sizeMatch ? parseInt(sizeMatch[1]) : 0;
            if (price && size > 0 && !isNaN(size)) {
                // 翻译价格偏好类型
                let translatedPrice = price;
                if (currentLanguage === 'en' && typeof translateKeyCharacteristic === 'function') {
                    const translated = translateKeyCharacteristic(`价格敏感度: ${price}`);
                    translatedPrice = translated.split(':')[1]?.trim() || price;
                }
                priceData[translatedPrice] = (priceData[translatedPrice] || 0) + size;
            }
        }
    });
    
    if (Object.keys(priceData).length > 0) {
        createBarChart('pricePreferenceChart', priceData, t('overview.charts.pricePreference'));
    }
    
    // 核心关注点
    const concernsData = {};
    businessInsights.forEach(insight => {
        if (!insight || !insight.key_characteristics || !Array.isArray(insight.key_characteristics)) {
            return;
        }
        const concernMatch = insight.key_characteristics.find(c => c && c.includes('关注点'));
        if (concernMatch) {
            const concern = concernMatch.split(':')[1]?.trim() || '未知';
            const sizeMatch = insight.key_characteristics[0].match(/(\d+)\s*个意图片段/);
            const size = sizeMatch ? parseInt(sizeMatch[1]) : 0;
            if (concern && size > 0 && !isNaN(size)) {
                // 翻译关注点
                let translatedConcern = concern;
                if (currentLanguage === 'en' && typeof translateKeyCharacteristic === 'function') {
                    const translated = translateKeyCharacteristic(`关注点: ${concern}`);
                    translatedConcern = translated.split(':')[1]?.trim() || concern;
                }
                concernsData[translatedConcern] = (concernsData[translatedConcern] || 0) + size;
            }
        }
    });
    
    if (Object.keys(concernsData).length > 0) {
        createHorizontalBarChart('concernsChart', concernsData, t('overview.charts.concerns'));
    }
    
    // 关键洞察
    displayKeyInsights();
}

// 显示关键洞察
function displayKeyInsights() {
    const container = document.getElementById('keyInsights');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (typeof businessInsights === 'undefined' || !Array.isArray(businessInsights) || businessInsights.length === 0) {
        container.innerHTML = '<p>暂无数据</p>';
        return;
    }
    
    // 找出最大的几个聚类
    const topClusters = businessInsights
        .map(insight => {
            if (!insight || !insight.key_characteristics || !Array.isArray(insight.key_characteristics) || insight.key_characteristics.length === 0) {
                return null;
            }
            const sizeMatch = insight.key_characteristics[0].match(/(\d+)\s*个意图片段/);
            const size = sizeMatch ? parseInt(sizeMatch[1]) : 0;
            if (isNaN(size)) {
                return null;
            }
            return { ...insight, size };
        })
        .filter(item => item !== null && item.size > 0)
        .sort((a, b) => b.size - a.size)
        .slice(0, 4);
    
    if (topClusters.length === 0) {
        container.innerHTML = '<p>暂无数据</p>';
        return;
    }
    
    topClusters.forEach(cluster => {
        const card = document.createElement('div');
        card.className = 'insight-card';
        const clusterLabel = t('cluster.label');
        const sizeLabel = t('cluster.size');
        const strategyLabel = currentLanguage === 'zh' ? '策略' : 'Strategy';
        const segmentsLabel = t('cluster.segments');
        const noStrategyLabel = t('cluster.noStrategy');
        card.innerHTML = `
            <h4>${clusterLabel} ${cluster.cluster_id}: ${getClusterDisplayName(cluster.user_segment_name)}</h4>
            <p><strong>${sizeLabel}:</strong> ${cluster.size} ${segmentsLabel}</p>
            <p><strong>${strategyLabel}:</strong> ${cluster.marketing_strategy && cluster.marketing_strategy.length > 0 
                ? (typeof translateStrategyText === 'function' 
                    ? translateStrategyText(cluster.marketing_strategy[0]) 
                    : cluster.marketing_strategy[0])
                : noStrategyLabel}</p>
        `;
        container.appendChild(card);
    });
}

// 加载聚类页面
function loadClusters() {
    if (typeof businessInsights === 'undefined') {
        console.error('businessInsights 数据未加载');
        return;
    }
    
    const select = document.getElementById('clusterSelect');
    if (!select) return;
    
    select.innerHTML = `<option value="">${t('cluster.selectPlaceholder')}</option>`;
    
    businessInsights.forEach(insight => {
        const option = document.createElement('option');
        option.value = insight.cluster_id;
        const clusterLabel = t('cluster.label');
        option.textContent = `${clusterLabel} ${insight.cluster_id}: ${getClusterDisplayName(insight.user_segment_name)}`;
        select.appendChild(option);
    });
}

// 处理查看详情按钮点击
function handleViewDetails(clusterId, event) {
    if (event) {
        event.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击
    }
    
    // 切换到转化分析页面（用户聚类现在在这里）
    showTab('journey');
    
    // 等待页面切换完成后显示详情
    setTimeout(() => {
        // 确保切换到用户聚类子标签页
        switchSubTab('cluster');
        
        // 设置选择器并显示详情
        setTimeout(() => {
            const select = document.getElementById('clusterSelect');
            if (select) {
                select.value = clusterId;
                showClusterDetails(clusterId);
                
                // 滚动到详情区域
                const details = document.getElementById('clusterDetails');
                if (details) {
                    details.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        }, 100);
    }, 300);
}

// 显示聚类详情
function showClusterDetails(clusterId) {
    if (!clusterId || typeof businessInsights === 'undefined') {
        const details = document.getElementById('clusterDetails');
        if (details) {
            details.classList.remove('active');
        }
        return;
    }
    
    const insight = businessInsights.find(i => i.cluster_id === clusterId);
    if (!insight) return;
    
    const portrait = typeof userPortraits !== 'undefined' 
        ? userPortraits.find(p => p.cluster_id === clusterId || p.cluster_id === parseInt(clusterId))
        : null;
    
    const container = document.getElementById('clusterDetails');
    container.classList.add('active');
    
    const clusterLabel = t('cluster.label');
    container.innerHTML = `
        <div class="cluster-info-card">
            <h3>${clusterLabel} ${clusterId}: ${getClusterDisplayName(insight.user_segment_name)}</h3>
            
            <div class="info-grid">
                ${(function() {
                    // 支持两种格式：数组（电商）和对象（金融）
                    let characteristics = [];
                    if (Array.isArray(insight.key_characteristics)) {
                        // 电商场景：数组格式
                        characteristics = insight.key_characteristics.map(char => {
                            const translatedChar = typeof translateKeyCharacteristic === 'function' 
                                ? translateKeyCharacteristic(char) 
                                : char;
                            const parts = translatedChar.split(':');
                            const key = parts[0]?.trim() || '';
                            const value = parts.slice(1).join(':').trim() || '';
                            return { key, value: value || translatedChar };
                        });
                    } else if (typeof insight.key_characteristics === 'object') {
                        // 金融场景：对象格式
                        const chars = insight.key_characteristics;
                        // 金融特征映射
                        const financialLabels = {
                            'user_count': '用户数',
                            'segment_count': '片段数',
                            'avg_duration_minutes': '平均浏览时长（分钟）',
                            'avg_interactions': '平均交互次数',
                            'avg_intent_score': '平均意图强度',
                            'behavior': '行为模式',
                            'urgency': '紧迫度',
                            'main_activity': '主要活动',
                            'kyc_status': 'KYC状态',
                            'transaction_status': '交易状态',
                            'stage': '购买阶段',
                            'price_sensitivity': '价格敏感度',
                            'engagement_level': '参与度',
                            'product_preference': '产品偏好',
                            'concern_focus': '关注点',
                            'core_need': '核心需求'
                        };
                        Object.keys(chars).forEach(key => {
                            if (chars[key] !== null && chars[key] !== undefined) {
                                const label = financialLabels[key] || key;
                                let value = chars[key];
                                if (typeof value === 'number') {
                                    if (key.includes('duration')) {
                                        value = value.toFixed(2);
                                    } else if (key.includes('score')) {
                                        value = value.toFixed(2);
                                    } else {
                                        value = value.toFixed(0);
                                    }
                                }
                                characteristics.push({ key: label, value: String(value) });
                            }
                        });
                    }
                    
                    return characteristics.map(char => `
                        <div class="info-item">
                            <strong>${char.key}</strong>
                            <span>${char.value}</span>
                        </div>
                    `).join('');
                })()}
            </div>
            
            <div class="strategy-section">
                <h4>${t('strategy.marketing')}</h4>
                <ul class="strategy-list">
                    ${insight.marketing_strategy.map(s => {
                        const translated = typeof translateStrategyText === 'function' 
                            ? translateStrategyText(s) 
                            : s;
                        return `<li>${translated}</li>`;
                    }).join('')}
                </ul>
            </div>
            
            <div class="strategy-section">
                <h4>${t('strategy.product')}</h4>
                <ul class="strategy-list">
                    ${insight.product_recommendations.length > 0 
                        ? insight.product_recommendations.map(r => {
                            const translated = typeof translateStrategyText === 'function' 
                                ? translateStrategyText(r) 
                                : r;
                            return `<li>${translated}</li>`;
                        }).join('')
                        : `<li>${t('strategy.noProductRecommendation')}</li>`}
                </ul>
            </div>
            
            <div class="strategy-section">
                <h4>${t('strategy.conversion')}</h4>
                <ul class="strategy-list">
                    ${insight.conversion_optimization.map(o => {
                        const translated = typeof translateStrategyText === 'function' 
                            ? translateStrategyText(o) 
                            : o;
                        return `<li>${translated}</li>`;
                    }).join('')}
                </ul>
            </div>
            
            ${insight.pricing_strategy && insight.pricing_strategy.length > 0 ? `
            <div class="strategy-section">
                <h4>${t('strategy.pricing')}</h4>
                <ul class="strategy-list">
                    ${insight.pricing_strategy.map(p => {
                        const translated = typeof translateStrategyText === 'function' 
                            ? translateStrategyText(p) 
                            : p;
                        return `<li>${translated}</li>`;
                    }).join('')}
                </ul>
            </div>
            ` : ''}
            
            <div class="strategy-section">
                <h4>${t('strategy.content')}</h4>
                <ul class="strategy-list">
                    ${insight.content_strategy && insight.content_strategy.length > 0 
                        ? insight.content_strategy.map(c => {
                            const translated = typeof translateStrategyText === 'function' 
                                ? translateStrategyText(c) 
                                : c;
                            return `<li>${translated}</li>`;
                        }).join('')
                        : `<li>${t('strategy.noContentStrategy')}</li>`}
                </ul>
            </div>
            
            ${insight.campaign_differentiation && insight.campaign_differentiation.length > 0 ? `
            <div class="strategy-section">
                <h4>${t('strategy.campaign')}</h4>
                <ul class="strategy-list">
                    ${insight.campaign_differentiation.map(c => {
                        const translated = typeof translateStrategyText === 'function' 
                            ? translateStrategyText(c) 
                            : c;
                        return `<li>${translated}</li>`;
                    }).join('')}
                </ul>
            </div>
            ` : ''}
        </div>
    `;
}

// 加载用户画像页面
function loadPortraits() {
    if (typeof userPortraits === 'undefined') {
        console.error('userPortraits 数据未加载');
        return;
    }
    
    const container = document.getElementById('portraitCards');
    if (!container) return;
    
    container.innerHTML = '';
    
    userPortraits.forEach((portrait, index) => {
        const card = document.createElement('div');
        card.className = 'portrait-card-enhanced';
        
        // 获取聚类名称
        const insight = businessInsights.find(i => i.cluster_id === portrait.cluster_id);
        const clusterLabel = t('cluster.label');
        const clusterName = insight ? getClusterDisplayName(insight.user_segment_name) : `${clusterLabel} ${portrait.cluster_id}`;
        
        // 准备词云数据（优先使用从实际数据中提取的关键词）
        let wordCloudData = [];
        if (portrait.keywords && portrait.keywords.length > 0) {
            // 使用从实际数据中提取的关键词
            wordCloudData = portrait.keywords;
            console.log(`聚类 ${portrait.cluster_id} 使用实际数据关键词:`, wordCloudData.length, '个词');
        } else {
            // 如果没有实际关键词，使用特征词
            wordCloudData = prepareWordCloudData(portrait, insight);
            console.log(`聚类 ${portrait.cluster_id} 使用特征词:`, wordCloudData.length, '个词');
        }
        
        // 准备价格偏好数据
        const priceData = portrait.intent_profile?.price_range || {};
        
        // 准备使用场景偏好数据（用于热力图）
        const scenarioData = {
            main_appeal: portrait.intent_profile?.main_appeal || {},
            concerns: portrait.intent_profile?.concerns || {},
            purchase_stage: portrait.intent_profile?.purchase_stage || {},
            price_range: portrait.intent_profile?.price_range || {},
            product_preferences: portrait.product_preferences || {}
        };
        
        // 准备雷达图数据
        const radarData = prepareRadarData(portrait);
        
        const cardId = `portrait-card-${portrait.cluster_id}`;
        card.id = cardId;
        
        card.innerHTML = `
            <div class="portrait-header">
                <div class="portrait-title-section">
                    <h3>${t('cluster.label')} ${portrait.cluster_id}</h3>
                    <h2>${clusterName}</h2>
                </div>
                <div class="portrait-stats-mini">
                    <div class="stat-mini">
                        <span class="stat-mini-value">${portrait.unique_users}</span>
                        <span class="stat-mini-label">用户</span>
                    </div>
                    <div class="stat-mini">
                        <span class="stat-mini-value">${portrait.segment_count}</span>
                        <span class="stat-mini-label">${currentLanguage === 'zh' ? '片段' : 'Segments'}</span>
                    </div>
                    <div class="stat-mini">
                        <span class="stat-mini-value">${(portrait.avg_duration_seconds || 0).toFixed(0)}s</span>
                        <span class="stat-mini-label">${currentLanguage === 'zh' ? '时长' : 'Duration'}</span>
                    </div>
                </div>
            </div>
            
            <div class="portrait-visualizations">
                <!-- 第一行：词云和价格偏好 -->
                <div class="visualization-section visualization-compact">
                    <div class="visualization-header">
                        <h4>${currentLanguage === 'zh' ? '用户关注词云' : 'User Attention Word Cloud'}</h4>
                    </div>
                    <div class="visualization-content">
                    <canvas id="wordcloud-${portrait.cluster_id}" class="wordcloud-canvas"></canvas>
                    </div>
                </div>
                
                <div class="visualization-section visualization-compact">
                    <div class="visualization-header">
                        <h4>${currentLanguage === 'zh' ? '价格偏好' : 'Price Preference'}</h4>
                    </div>
                    <div class="visualization-content price-preference-content">
                        <div id="pricePreference-${portrait.cluster_id}" class="price-preference-display"></div>
                    </div>
                </div>
                
                <!-- 第二行：使用场景偏好热力图（全宽） -->
                <div class="visualization-section visualization-fullwidth">
                    <div class="visualization-header">
                        <h4>${currentLanguage === 'zh' ? '使用场景偏好热力图' : 'Scenario Preference Heatmap'}</h4>
                        <p class="visualization-subtitle">${currentLanguage === 'zh' ? '展示用户在不同场景维度的偏好强度' : 'Display user preference intensity across different scenario dimensions'}</p>
                    </div>
                    <div class="visualization-content visualization-heatmap">
                        <canvas id="scenarioChart-${portrait.cluster_id}" class="heatmap-canvas"></canvas>
                    </div>
                </div>
                
                <!-- 第三行：特征雷达图（全宽） -->
                <div class="visualization-section visualization-fullwidth">
                    <div class="visualization-header">
                        <h4>${currentLanguage === 'zh' ? '用户特征雷达图' : 'User Characteristics Radar Chart'}</h4>
                        <p class="visualization-subtitle">${currentLanguage === 'zh' ? '多维度用户特征分析' : 'Multi-dimensional user characteristics analysis'}</p>
                    </div>
                    <div class="visualization-content">
                        <canvas id="radarChart-${portrait.cluster_id}" class="chart-canvas chart-radar"></canvas>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(card);
        
        // 延迟渲染图表，确保DOM已创建
        setTimeout(() => {
            // 渲染词云（renderWordCloud函数内部会检查库是否加载并处理队列）
            if (wordCloudData && wordCloudData.length > 0) {
                renderWordCloud(`wordcloud-${portrait.cluster_id}`, wordCloudData);
            } else {
                console.warn(`聚类 ${portrait.cluster_id} 词云数据为空`);
                const canvas = document.getElementById(`wordcloud-${portrait.cluster_id}`);
                if (canvas && canvas.parentElement) {
                    canvas.parentElement.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>暂无词云数据</p></div>';
                }
            }
            
            // 渲染价格偏好显示
            renderPricePreference(`pricePreference-${portrait.cluster_id}`, priceData);
            
            // 渲染使用场景偏好热力图
            if (Object.keys(scenarioData).length > 0) {
                const scenarioCanvas = document.getElementById(`scenarioChart-${portrait.cluster_id}`);
                if (scenarioCanvas) {
                    // 覆盖CSS高度限制，允许热力图自适应高度
                    scenarioCanvas.style.height = 'auto';
                    scenarioCanvas.style.minHeight = '400px';
                }
                createScenarioHeatmap(`scenarioChart-${portrait.cluster_id}`, scenarioData, portrait.cluster_id);
            } else {
                // 如果没有场景数据，显示占位符
                const scenarioCanvas = document.getElementById(`scenarioChart-${portrait.cluster_id}`);
                if (scenarioCanvas && scenarioCanvas.parentElement) {
                    scenarioCanvas.parentElement.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>暂无使用场景数据</p></div>';
                }
            }
            
            // 渲染雷达图
            createRadarChart(`radarChart-${portrait.cluster_id}`, radarData);
        }, 100 * (index + 1));
    });
}

// 准备词云数据
function prepareWordCloudData(portrait, insight) {
    const words = [];
    const genericTerms = ['综合需求', '综合关注', '多产品比较', '未知', '高端价值型'];
    
    // 过滤掉分析结果相关的词（用户特质，不是用户兴趣）
    const analysisTerms = [
        '快速浏览', '单次浏览', '中等参与', '深度研究',
        '低紧迫', '中紧迫', '高紧迫',
        '浏览阶段', '对比阶段', '决策阶段',
        '预算导向', '中端平衡', '高端价值型',
        '功能导向', '价格导向', '舒适度导向', '有效性导向',
        '止鼾需求', '颈部疼痛', '睡眠质量', '综合需求',
        '综合关注', '多产品比较'
    ];
    
    console.log('准备词云数据 - 聚类', portrait.cluster_id);
    
    // 1. 从核心需求中提取（高权重）- 这是用户感兴趣的点
    if (portrait.intent_profile?.main_appeal) {
        Object.keys(portrait.intent_profile.main_appeal).forEach(key => {
            if (key && !genericTerms.includes(key) && !analysisTerms.includes(key)) {
                words.push({ text: key, size: 50, source: 'main_appeal' });
                console.log(`  - 核心需求: ${key} (权重: 50)`);
            }
        });
    }
    
    // 2. 从关注点中提取 - 这是用户关心的问题
    if (portrait.intent_profile?.concerns) {
        Object.keys(portrait.intent_profile.concerns).forEach(key => {
            if (key && !genericTerms.includes(key) && !analysisTerms.includes(key)) {
                words.push({ text: key, size: 40, source: 'concerns' });
                console.log(`  - 关注点: ${key} (权重: 40)`);
            }
        });
    }
    
    // 3. 从产品偏好中提取（重要：处理"X偏好"格式）- 这是用户感兴趣的产品
    if (portrait.product_preferences) {
        Object.keys(portrait.product_preferences).forEach(key => {
            if (key && key !== '多产品比较' && !analysisTerms.includes(key)) {
                if (key.includes('偏好')) {
                    // 提取产品名称（如"F1偏好" -> "F1"）
                    const productName = key.replace('偏好', '').trim();
                    if (productName) {
                        words.push({ text: productName, size: 45, source: 'product' });
                        console.log(`  - 产品: ${productName} (从"${key}"提取, 权重: 45)`);
                    }
                } else {
                    words.push({ text: key, size: 35, source: 'product' });
                    console.log(`  - 产品: ${key} (权重: 35)`);
                }
            }
        });
    }
    
    // 4. 从价格偏好中提取 - 但只提取具体的价格范围，不提取分析结果
    if (portrait.intent_profile?.price_range) {
        Object.keys(portrait.intent_profile.price_range).forEach(key => {
            if (key && !genericTerms.includes(key) && !analysisTerms.includes(key)) {
                // 只保留具体的价格描述，如"$100-$200"等，不保留"预算导向"等分析结果
                words.push({ text: key, size: 30, source: 'price' });
                console.log(`  - 价格偏好: ${key} (权重: 30)`);
            }
        });
    }
    
    // 5. 从业务洞察中提取关键词（只提取用户兴趣相关的，不提取分析结果）
    if (insight) {
        // 从产品推荐中提取
        if (insight.product_recommendations) {
            insight.product_recommendations.forEach(rec => {
                // 提取【】中的关键词
                const keywords = rec.match(/【([^】]+)】/g);
                if (keywords) {
                    keywords.forEach(kw => {
                        const text = kw.replace(/【|】/g, '').trim();
                        if (text && !analysisTerms.includes(text)) {
                            words.push({ text: text, size: 25, source: 'recommendations' });
                            console.log(`  - 推荐关键词: ${text} (权重: 25)`);
                        }
                    });
                }
                // 提取产品名称（如"F1偏好"、"Z6偏好"）
                const productMatches = rec.match(/([A-Z]\d+)\s*偏好/g);
                if (productMatches) {
                    productMatches.forEach(match => {
                        const productName = match.replace(/\s*偏好/g, '').trim();
                        if (productName) {
                            words.push({ text: productName, size: 35, source: 'recommendations_product' });
                            console.log(`  - 推荐产品: ${productName} (权重: 35)`);
                        }
                    });
                }
            });
        }
        
        // 从关键特征中提取（只提取用户兴趣，不提取分析结果）
        if (insight.key_characteristics) {
            insight.key_characteristics.forEach(char => {
                // 提取核心需求（用户感兴趣的需求）
                if (char.includes('核心需求:')) {
                    const need = char.split('核心需求:')[1]?.trim();
                    if (need && need !== '综合需求' && !analysisTerms.includes(need)) {
                        words.push({ text: need, size: 45, source: 'key_characteristics' });
                        console.log(`  - 关键特征-核心需求: ${need} (权重: 45)`);
                    }
                }
                // 提取产品偏好（用户感兴趣的产品）
                if (char.includes('产品偏好:')) {
                    const product = char.split('产品偏好:')[1]?.trim();
                    if (product && product !== '多产品比较' && !analysisTerms.includes(product)) {
                        if (product.includes('偏好')) {
                            const productName = product.replace('偏好', '').trim();
                            if (productName) {
                                words.push({ text: productName, size: 40, source: 'key_characteristics_product' });
                                console.log(`  - 关键特征-产品: ${productName} (权重: 40)`);
                            }
                        } else {
                            words.push({ text: product, size: 40, source: 'key_characteristics_product' });
                        }
                    }
                }
                // 提取关注点（用户关心的问题）
                if (char.includes('关注点:')) {
                    const concern = char.split('关注点:')[1]?.trim();
                    if (concern && concern !== '综合关注' && !analysisTerms.includes(concern)) {
                        words.push({ text: concern, size: 35, source: 'key_characteristics_concern' });
                        console.log(`  - 关键特征-关注点: ${concern} (权重: 35)`);
                    }
                }
            });
        }
    }
    
    // 去重并合并相同词的权重（保留最大权重）
    const wordMap = {};
    words.forEach(w => {
        if (wordMap[w.text]) {
            wordMap[w.text] = Math.max(wordMap[w.text], w.size);
        } else {
            wordMap[w.text] = w.size;
        }
    });
    
    console.log('词云数据映射:', wordMap);
    
    // 转换为词云格式 [text, size]，并过滤掉分析结果相关的词
    let result = Object.entries(wordMap)
        .filter(([text]) => {
            // 过滤条件：非空、长度合理、不是分析结果
            return text && 
                   text.length > 0 && 
                   text.length <= 15 && 
                   !analysisTerms.includes(text) &&
                   !genericTerms.includes(text);
        })
        .map(([text, size]) => [text, Math.min(Math.max(size, 15), 60)]);
    
    // 如果结果为空或太少，尝试从产品偏好中提取
    if (result.length === 0) {
        console.warn('词云数据为空，尝试从产品偏好中提取');
        if (portrait.product_preferences) {
            Object.keys(portrait.product_preferences).forEach(key => {
                if (key && key !== '多产品比较' && !analysisTerms.includes(key)) {
                    if (key.includes('偏好')) {
                        const productName = key.replace('偏好', '').trim();
                        if (productName) {
                            result.push([productName, 30]);
                        }
                    } else {
                        result.push([key, 30]);
                    }
                }
            });
        }
    }
    
    // 如果还是为空，使用默认词
    if (result.length === 0) {
        console.warn('使用默认词云数据');
        result = [
            [portrait.cluster_name || '用户画像', 40],
            ['数据分析', 30],
            ['聚类分析', 25]
        ];
    }
    
    console.log('最终词云数据:', result);
    return result;
}

// 准备雷达图数据
function prepareRadarData(portrait) {
    const characteristics = portrait.characteristics || {};
    
    // 将特征转换为数值（用于雷达图）
    const behaviorMap = { '单次浏览': 1, '快速浏览': 2, '中等参与': 3, '深度研究': 4 };
    const urgencyMap = { '低紧迫': 1, '中紧迫': 2, '高紧迫': 3 };
    const stageMap = { '浏览阶段': 1, '对比阶段': 2, '决策阶段': 3 };
    const priceMap = { '预算导向': 1, '中端平衡': 2, '高端价值型': 3 };
    const concernMap = { '功能导向': 1, '价格导向': 2, '舒适度导向': 3, '有效性导向': 4, '综合关注': 2.5 };
    const needMap = { '止鼾需求': 1, '颈部疼痛': 2, '睡眠质量': 2.5, '综合需求': 2 };
    
    return {
        labels: [
            t('dataFields.behaviorPattern'),
            t('dataFields.intentUrgency'),
            t('dataFields.purchaseStage'),
            t('dataFields.priceSensitivity'),
            t('dataFields.concerns'),
            t('dataFields.coreNeeds')
        ],
        values: [
            (behaviorMap[characteristics.behavior] || 2) * 25,
            (urgencyMap[characteristics.urgency] || 1) * 25,
            (stageMap[characteristics.stage] || 1) * 25,
            (priceMap[characteristics.price] || 2) * 25,
            (concernMap[characteristics.concern] || 2.5) * 25,
            (needMap[characteristics.need] || 2) * 25
        ]
    };
}

// 全局词云渲染队列
window.wordCloudQueue = window.wordCloudQueue || [];

// 等待WordCloud库加载并渲染队列中的词云
function processWordCloudQueue() {
    if (window.wordCloudQueue.length === 0) return;
    
    const WordCloudFunc = getWordCloudFunction();
    if (!WordCloudFunc) {
        // 如果库还没加载，等待一下再试
        setTimeout(processWordCloudQueue, 200);
        return;
    }
    
    // 处理队列中的所有词云
    while (window.wordCloudQueue.length > 0) {
        const { canvasId, words } = window.wordCloudQueue.shift();
        renderWordCloudInternal(canvasId, words, WordCloudFunc);
    }
}

// 获取WordCloud函数
function getWordCloudFunction() {
    if (typeof WordCloud !== 'undefined') {
        return WordCloud;
    }
    if (typeof window !== 'undefined' && typeof window.WordCloud !== 'undefined') {
        return window.WordCloud;
    }
    if (typeof window !== 'undefined' && typeof window.wordcloud !== 'undefined') {
        return window.wordcloud;
    }
    return null;
}

// 内部渲染函数
function renderWordCloudInternal(canvasId, words, WordCloudFunc) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error('Canvas not found:', canvasId);
        return;
    }
    
    try {
        // 确保canvas可见
        canvas.style.display = 'block';
        canvas.style.visibility = 'visible';
        canvas.style.opacity = '1';
        
        // 获取canvas的实际尺寸 - 使用offsetWidth更可靠
        const container = canvas.parentElement;
        let width = 300;
        const height = 240; // 固定高度，与CSS保持一致
        
        if (container) {
            // 使用offsetWidth而不是getBoundingClientRect，因为后者可能返回0
            const containerWidth = container.offsetWidth || container.clientWidth || 300;
            width = Math.max(containerWidth - 48, 300); // 减去padding，最小300
        }
        
        // 确保canvas有合理的尺寸
        if (width < 200) width = 300;
        
        // 设置canvas尺寸 - 先设置样式再设置属性
        canvas.style.width = '100%';
        canvas.style.height = height + 'px';
        canvas.style.maxWidth = '100%';
        canvas.width = width;
        canvas.height = height;
        
        // 强制重绘
        canvas.getContext('2d').clearRect(0, 0, width, height);
        
        // 确保数据格式正确：[[word, size], ...]
        const wordList = words.map(w => {
            if (Array.isArray(w) && w.length >= 2) {
                return [String(w[0]), Number(w[1])];
            }
            return null;
        }).filter(w => w !== null && w[0] && w[0].length > 0);
        
        if (wordList.length === 0) {
            throw new Error('词云数据格式不正确或为空');
        }
        
        // 计算频率范围，用于动态调整字体大小
        const frequencies = wordList.map(w => w[1]);
        const minFreq = Math.min(...frequencies);
        const maxFreq = Math.max(...frequencies);
        const freqRange = maxFreq - minFreq || 1; // 避免除以0
        
        console.log('渲染词云:', canvasId, '尺寸:', width, 'x', height, '词数:', wordList.length, 
                    '频率范围:', minFreq, '-', maxFreq, '前3个词:', wordList.slice(0, 3));
        
        // 获取context
        const ctx = canvas.getContext('2d');
        
        // 清空canvas并设置背景（用于调试）
        ctx.fillStyle = 'transparent';
        ctx.fillRect(0, 0, width, height);
        ctx.clearRect(0, 0, width, height);
        
        // 渲染词云 - 使用更可靠的参数
        try {
            // 确保WordCloud函数存在
            if (typeof WordCloudFunc !== 'function') {
                throw new Error('WordCloud函数不可用');
            }
            
            console.log('调用WordCloud函数，参数:', {
                canvas: canvas,
                listLength: wordList.length,
                gridSize: Math.max(4, Math.round(16 * width / 1024)),
                width: width,
                height: height,
                freqRange: `${minFreq}-${maxFreq}`
            });
            
            WordCloudFunc(canvas, {
                list: wordList,
                gridSize: Math.max(4, Math.round(16 * width / 1024)), // 根据宽度调整gridSize，最小4
                weightFactor: function(size) {
                    // 根据频率范围动态调整字体大小
                    // 将频率映射到 0-1 范围
                    const normalizedFreq = (size - minFreq) / freqRange;
                    
                    // 使用平方根函数使大小差异更明显，同时保持平滑过渡
                    const normalizedSize = Math.sqrt(normalizedFreq);
                    
                    // 将归一化大小映射到字体大小范围
                    // 最小字体：12px，最大字体：根据canvas宽度动态调整（最大不超过80px）
                    const minFontSize = 12;
                    const maxFontSize = Math.min(Math.max(width / 8, 30), 80);
                    const fontSize = minFontSize + normalizedSize * (maxFontSize - minFontSize);
                    
                    // 根据canvas宽度调整缩放因子
                    const scaleFactor = Math.max(width / 400, 0.8);
                    
                    return fontSize * scaleFactor;
                },
                fontFamily: 'Arial, "Microsoft YaHei", "PingFang SC", sans-serif',
                color: function() {
                    const colors = ['#7FE8C1', '#7DA6FF', '#A78BFA', '#F472B6', '#60A5FA', '#34D399', '#FBBF24'];
                    return colors[Math.floor(Math.random() * colors.length)];
                },
                rotateRatio: 0.3,
                rotationSteps: 2,
                backgroundColor: 'transparent',
                minSize: 12,
                drawOutOfBound: false,
                shrinkToFit: true // 确保词云适应canvas
            });
            
            console.log('词云渲染调用完成:', canvasId);
            
            // 延迟验证渲染结果，给WordCloud库足够时间渲染（WordCloud是同步的，但可能需要时间绘制）
            setTimeout(() => {
                try {
                    // 检查整个canvas的内容
                    const imageData = ctx.getImageData(0, 0, width, height);
                    let pixelCount = 0;
                    let colorPixelCount = 0;
                    
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        const r = imageData.data[i];
                        const g = imageData.data[i + 1];
                        const b = imageData.data[i + 2];
                        const a = imageData.data[i + 3];
                        
                        // 检查是否有非透明像素
                        if (a > 0) {
                            pixelCount++;
                            // 检查是否有颜色（不是纯黑或纯白）
                            if (r > 0 || g > 0 || b > 0) {
                                colorPixelCount++;
                            }
                        }
                    }
                    
                    console.log('词云渲染验证:', canvasId, {
                        totalPixels: imageData.data.length / 4,
                        nonTransparentPixels: pixelCount,
                        colorPixels: colorPixelCount,
                        percentage: ((colorPixelCount / (width * height)) * 100).toFixed(2) + '%'
                    });
                    
                    if (colorPixelCount < 50) {
                        console.warn('词云可能未正确渲染:', canvasId, '彩色像素数:', colorPixelCount);
                        // 尝试重新渲染一次，使用更激进的参数
                        console.log('尝试重新渲染词云（使用更激进的参数）:', canvasId);
                        setTimeout(() => {
                            ctx.clearRect(0, 0, width, height);
                            WordCloudFunc(canvas, {
                                list: wordList,
                                gridSize: Math.max(2, Math.round(8 * width / 1024)), // 更小的gridSize
                                weightFactor: function(size) {
                                    // 根据频率范围动态调整字体大小（重新渲染时使用更激进的参数）
                                    const normalizedFreq = (size - minFreq) / freqRange;
                                    const normalizedSize = Math.sqrt(normalizedFreq);
                                    
                                    // 重新渲染时使用更大的字体范围
                                    const minFontSize = 15;
                                    const maxFontSize = Math.min(Math.max(width / 6, 40), 100);
                                    const fontSize = minFontSize + normalizedSize * (maxFontSize - minFontSize);
                                    
                                    const scaleFactor = Math.max(width / 350, 1.0);
                                    return fontSize * scaleFactor;
                                },
                                fontFamily: 'Arial, "Microsoft YaHei", "PingFang SC", sans-serif',
                                color: function() {
                                    const colors = ['#7FE8C1', '#7DA6FF', '#A78BFA', '#F472B6', '#60A5FA', '#34D399', '#FBBF24'];
                                    return colors[Math.floor(Math.random() * colors.length)];
                                },
                                rotateRatio: 0.3,
                                rotationSteps: 2,
                                backgroundColor: 'transparent',
                                minSize: 10,
                                drawOutOfBound: false,
                                shrinkToFit: true
                            });
                        }, 300);
                    } else {
                        console.log('✓ 词云渲染验证成功:', canvasId);
                    }
                } catch (verifyError) {
                    console.error('验证词云渲染时出错:', verifyError);
                }
            }, 800); // 增加延迟时间到800ms，确保渲染完成
        } catch (renderError) {
            console.error('WordCloud渲染调用出错:', renderError);
            throw renderError;
        }
        
    } catch (e) {
        console.error('Error rendering word cloud:', canvasId, e);
        const container = canvas.parentElement;
        if (container) {
            // 显示关键词列表作为fallback
            const wordList = words.map(w => Array.isArray(w) ? w[0] : w).filter(w => w).slice(0, 20);
            container.innerHTML = `
                <div style="padding: 20px; text-align: center; color: var(--text-secondary);">
                    <p style="margin-bottom: 10px; color: var(--text); font-weight: 600;">关键词</p>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;">
                        ${wordList.map(word => `<span style="padding: 4px 12px; background: var(--glass); border: 1px solid var(--border); border-radius: 12px; font-size: 12px;">${word}</span>`).join('')}
                    </div>
                    <p style="margin-top: 10px; font-size: 11px; color: var(--muted);">词云渲染失败，显示关键词列表</p>
                </div>
            `;
        }
    }
}

// 渲染词云（公共接口）
function renderWordCloud(canvasId, words) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error('Canvas not found:', canvasId);
        return;
    }
    
    if (!words || words.length === 0) {
        console.warn('词云数据为空:', canvasId);
        const container = canvas.parentElement;
        if (container) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>暂无词云数据</p></div>';
        }
        return;
    }
    
    // 检查WordCloud是否可用
    const WordCloudFunc = getWordCloudFunction();
    
    if (!WordCloudFunc) {
        // 如果库未加载，加入队列等待
        console.log('WordCloud库未加载，加入渲染队列:', canvasId);
        window.wordCloudQueue.push({ canvasId, words });
        
        // 启动队列处理
        if (!window.wordCloudQueueProcessing) {
            window.wordCloudQueueProcessing = true;
            processWordCloudQueue();
        }
        return;
    }
    
    // 直接渲染
    renderWordCloudInternal(canvasId, words, WordCloudFunc);
}

// 重新渲染所有词云（用于库加载后）
function renderAllWordClouds() {
    console.log('重新渲染所有词云...');
    // 触发所有portrait卡片重新渲染
    if (typeof loadPortraits === 'function') {
        loadPortraits();
    }
}

// 创建雷达图
function createRadarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: data.labels,
            datasets: [{
                label: '特征强度',
                data: data.values,
                backgroundColor: 'rgba(127, 232, 193, 0.2)',
                borderColor: '#7FE8C1',
                borderWidth: 2,
                pointBackgroundColor: '#7FE8C1',
                pointBorderColor: '#0E1624',
                pointHoverBackgroundColor: '#7DA6FF',
                pointHoverBorderColor: '#0E1624'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1, // 强制保持1:1比例，防止变形
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 27, 46, 0.9)',
                    titleColor: '#ECF2F5',
                    bodyColor: '#ECF2F5',
                    borderColor: '#7FE8C1',
                    borderWidth: 1
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 25,
                        color: '#8FA0B8',
                        font: {
                            size: 10
                        },
                        display: true
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        lineWidth: 1
                    },
                    pointLabels: {
                        color: '#ECF2F5',
                        font: {
                            size: 11,
                            weight: '500'
                        },
                        padding: 12
                    },
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        lineWidth: 1
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

// 加载业务洞察页面（已删除）

// 加载首页
function loadHomepage() {
    // 更新统计数据
    if (typeof stats !== 'undefined') {
        const homeTotalUsers = document.getElementById('homeTotalUsers');
        const homeTotalClusters = document.getElementById('homeTotalClusters');
        const homeTotalSegments = document.getElementById('homeTotalSegments');
        
        if (homeTotalUsers) {
            animateValue(homeTotalUsers, 0, stats.totalUsers || 0, 1500);
        }
        if (homeTotalClusters) {
            animateValue(homeTotalClusters, 0, stats.totalClusters || 0, 1500);
        }
        if (homeTotalSegments) {
            animateValue(homeTotalSegments, 0, stats.totalSegments || 0, 1500);
        }
    }
    
    // 绑定快速操作链接
    document.querySelectorAll('.action-card[data-tab]').forEach(card => {
        card.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = card.getAttribute('data-tab');
            if (tabName) {
                showTab(tabName);
            }
        });
    });
}

// 加载产品偏好页面
function loadProducts() {
    if (typeof userPortraits === 'undefined') {
        console.error('userPortraits 数据未加载');
        return;
    }
    
    // 统计所有产品的关注度
    const productData = {};
    
    userPortraits.forEach(portrait => {
        if (portrait.product_preferences) {
            Object.entries(portrait.product_preferences).forEach(([product, count]) => {
                productData[product] = (productData[product] || 0) + count;
            });
        }
    });
    
    if (Object.keys(productData).length > 0) {
        createBarChart('productPreferenceChart', productData, '产品关注度');
    }
    
    // 显示产品详情
    const container = document.getElementById('productDetails');
    if (!container) return;
    
    container.innerHTML = '';
    
    const sortedProducts = Object.entries(productData)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    sortedProducts.forEach(([product, count]) => {
        // 找出关注这个产品的聚类
        const clusters = userPortraits
            .filter(p => p.product_preferences && p.product_preferences[product] > 0)
            .map(p => ({
                cluster: p.cluster_id,
                count: p.product_preferences[product]
            }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 3);
        
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <h4>${product}</h4>
            <div class="product-stats">
                <div class="product-stat">
                    <div class="product-stat-value">${count}</div>
                    <div class="product-stat-label">总关注次数</div>
                </div>
                <div class="product-stat">
                    <div class="product-stat-value">${clusters.length}</div>
                    <div class="product-stat-label">相关聚类</div>
                </div>
            </div>
            ${clusters.length > 0 ? `
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e9ecef;">
                <strong>主要关注聚类:</strong>
                <div style="margin-top: 0.5rem;">
                    ${clusters.map(c => `<span style="display: inline-block; padding: 0.25rem 0.75rem; margin: 0.25rem; background: #f0f0f0; border-radius: 4px;">聚类 ${c.cluster} (${c.count}次)</span>`).join('')}
                </div>
            </div>
            ` : ''}
        `;
        container.appendChild(card);
    });
}

// 创建饼图 - 深色主题
function createPieChart(canvasId, data, title) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    
    // 深色主题配色
    const colors = [
        '#7FE8C1', '#7DA6FF', '#A78BFA', '#F472B6',
        '#60A5FA', '#34D399', '#FBBF24', '#FB7185',
        '#818CF8', '#A78BFA', '#F472B6', '#60A5FA',
        '#34D399', '#FBBF24', '#FB7185', '#818CF8',
        '#7FE8C1', '#7DA6FF', '#A78BFA', '#F472B6'
    ];
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: colors.slice(0, Object.keys(data).length),
                borderColor: '#0E1624',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#ECF2F5',
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 27, 46, 0.9)',
                    titleColor: '#ECF2F5',
                    bodyColor: '#ECF2F5',
                    borderColor: '#7FE8C1',
                    borderWidth: 1
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true
            }
        }
    });
}

// 渲染价格偏好显示（简洁形式）
function renderPricePreference(containerId, priceData) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!priceData || Object.keys(priceData).length === 0) {
        container.innerHTML = `<div class="price-preference-empty">${currentLanguage === 'zh' ? '暂无价格偏好数据' : 'No price preference data'}</div>`;
        return;
    }
    
    // 获取价格偏好类型和数值
    const priceTypes = Object.keys(priceData);
    const priceValues = Object.values(priceData);
    
    // 价格偏好颜色映射
    const priceColors = {
        '预算导向': '#60A5FA',
        '中端平衡': '#7DA6FF',
        '高端价值型': '#7FE8C1',
        '价格导向': '#F472B6',
        '价值导向': '#A78BFA'
    };
    
    // 如果只有一个价格偏好类型，显示大卡片
    if (priceTypes.length === 1) {
        const priceType = priceTypes[0];
        const priceValue = priceValues[0];
        const priceColor = priceColors[priceType] || '#8FA0B8';
        
        container.innerHTML = `
            <div class="price-preference-card" style="border-top-color: ${priceColor}">
                <div class="price-preference-icon" style="background: ${priceColor}20; color: ${priceColor}">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                    </svg>
                </div>
                    <div class="price-preference-info">
                    <div class="price-preference-label">${currentLanguage === 'zh' ? '价格偏好类型' : 'Price Preference Type'}</div>
                    <div class="price-preference-value" style="color: ${priceColor}">${typeof translateKeyCharacteristic === 'function' ? translateKeyCharacteristic(`价格敏感度: ${priceType}`).split(':')[1]?.trim() || priceType : priceType}</div>
                    <div class="price-preference-count">${priceValue} ${currentLanguage === 'zh' ? '个片段' : ' segments'}</div>
                </div>
            </div>
        `;
    } else {
        // 如果有多个，显示列表
        container.innerHTML = priceTypes.map((priceType, index) => {
            const priceValue = priceValues[index];
            const priceColor = priceColors[priceType] || '#8FA0B8';
            
            return `
                <div class="price-preference-item" style="border-left-color: ${priceColor}">
                    <div class="price-preference-item-icon" style="background: ${priceColor}20; color: ${priceColor}">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                        </svg>
                    </div>
                    <div class="price-preference-item-info">
                        <div class="price-preference-item-label" style="color: ${priceColor}">${typeof translateKeyCharacteristic === 'function' ? translateKeyCharacteristic(`价格敏感度: ${priceType}`).split(':')[1]?.trim() || priceType : priceType}</div>
                        <div class="price-preference-item-count">${priceValue} ${currentLanguage === 'zh' ? '个片段' : ' segments'}</div>
                    </div>
                </div>
            `;
        }).join('');
    }
}

// 创建环形图 - 深色主题
function createDoughnutChart(canvasId, data, title) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    
    const colors = ['#7FE8C1', '#7DA6FF', '#A78BFA', '#F472B6', '#60A5FA'];
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: colors.slice(0, Object.keys(data).length),
                borderColor: '#0E1624',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#ECF2F5',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 27, 46, 0.9)',
                    titleColor: '#ECF2F5',
                    bodyColor: '#ECF2F5',
                    borderColor: '#7FE8C1',
                    borderWidth: 1
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true
            }
        }
    });
}

// 创建柱状图 - 深色主题
function createBarChart(canvasId, data, title) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    
    const sortedData = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(d => d[0]),
            datasets: [{
                label: '数量',
                data: sortedData.map(d => d[1]),
                backgroundColor: 'rgba(127, 232, 193, 0.8)',
                borderColor: '#7FE8C1',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 27, 46, 0.9)',
                    titleColor: '#ECF2F5',
                    bodyColor: '#ECF2F5',
                    borderColor: '#7FE8C1',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#8FA0B8'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        color: '#8FA0B8'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// 创建水平柱状图 - 深色主题
function createHorizontalBarChart(canvasId, data, title) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    
    const sortedData = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(d => d[0]),
            datasets: [{
                label: '关注度',
                data: sortedData.map(d => d[1]),
                backgroundColor: 'rgba(125, 166, 255, 0.8)',
                borderColor: '#7DA6FF',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 27, 46, 0.9)',
                    titleColor: '#ECF2F5',
                    bodyColor: '#ECF2F5',
                    borderColor: '#7DA6FF',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        color: '#8FA0B8'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                y: {
                    ticks: {
                        color: '#8FA0B8'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// 创建使用场景偏好热力图
function createScenarioHeatmap(canvasId, scenarioData, clusterId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // 收集所有场景数据
    const allScenarios = [];
    const scenarioCategories = {
        [t('dataFields.coreNeeds')]: scenarioData.main_appeal || {},
        [t('dataFields.concerns')]: scenarioData.concerns || {},
        [t('dataFields.purchaseStage')]: scenarioData.purchase_stage || {},
        [t('dataFields.priceSensitivity')]: scenarioData.price_range || {},
        [t('dataFields.productPreference')]: scenarioData.product_preferences || {}
    };
    
    // 构建场景列表（排除通用术语）
    const genericTerms = currentLanguage === 'zh' 
        ? ['综合需求', '综合关注', '多产品比较', '未知']
        : ['Comprehensive Needs', 'Comprehensive Concerns', 'Multi-Product Comparison', 'Unknown'];
    const scenarioList = [];
    
    Object.entries(scenarioCategories).forEach(([category, data]) => {
        Object.entries(data).forEach(([scenario, value]) => {
            // 检查是否在通用术语中（支持中英文）
            const isGeneric = genericTerms.includes(scenario) || 
                            (currentLanguage === 'en' && ['综合需求', '综合关注', '多产品比较', '未知'].includes(scenario));
            if (scenario && !isGeneric && value > 0) {
                scenarioList.push({
                    category: category,
                    name: scenario,
                    value: value
                });
            }
        });
    });
    
    if (scenarioList.length === 0) {
        const noDataText = currentLanguage === 'zh' ? '暂无使用场景数据' : 'No scenario data available';
        canvas.parentElement.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>${noDataText}</p></div>`;
        return;
    }
    
    // 按类别和值排序，但限制每个类别最多显示前5个
    const categoryGroups = {};
    scenarioList.forEach(scenario => {
        if (!categoryGroups[scenario.category]) {
            categoryGroups[scenario.category] = [];
        }
        categoryGroups[scenario.category].push(scenario);
    });
    
    // 每个类别取前5个，按值排序
    const sortedScenarios = [];
    Object.keys(categoryGroups).sort().forEach(category => {
        const items = categoryGroups[category]
            .sort((a, b) => b.value - a.value)
            .slice(0, 5); // 每个类别最多5个
        sortedScenarios.push(...items);
    });
    
    // 获取容器尺寸 - 充分利用容器空间
    const container = canvas.parentElement;
    const containerWidth = container ? container.offsetWidth : 800;
    const containerPadding = 40; // 左右padding
    const width = Math.max(containerWidth - containerPadding, 600);
    
    // 使用专业的设计尺寸
    const cellHeight = 45; // 单元格高度
    const headerHeight = 70; // 标题区域高度
    const footerHeight = 60; // 图例区域高度
    const categorySpacing = 15; // 类别间距
    const categoryHeaderHeight = 30; // 类别标题高度
    
    // 计算总高度
    const categoryCount = Object.keys(categoryGroups).length;
    const totalHeight = sortedScenarios.length * cellHeight + 
                       categoryCount * (categorySpacing + categoryHeaderHeight) + 
                       headerHeight + 
                       footerHeight;
    const minHeight = 450; // 最小高度
    const height = Math.max(totalHeight, minHeight);
    
    // 设置canvas尺寸，使用高DPI渲染
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    canvas.style.maxHeight = 'none';
    canvas.style.minHeight = height + 'px';
    
    // 缩放上下文以支持高DPI
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    
    ctx.clearRect(0, 0, width, height);
    
    // 绘制背景渐变
    const bgGradient = ctx.createLinearGradient(0, 0, width, height);
    bgGradient.addColorStop(0, 'rgba(17, 27, 46, 0.3)');
    bgGradient.addColorStop(1, 'rgba(17, 27, 46, 0.1)');
    ctx.fillStyle = bgGradient;
    ctx.fillRect(0, 0, width, height);
    
    // 计算最大值用于归一化
    const maxValue = Math.max(...sortedScenarios.map(s => s.value));
    const minValue = Math.min(...sortedScenarios.map(s => s.value));
    const valueRange = maxValue - minValue || 1;
    
    // 设置样式 - 专业设计尺寸
    const cellPadding = 8;
    const labelWidth = Math.min(280, width * 0.32); // 标签宽度
    const valueWidth = 90;
    const heatmapWidth = width - labelWidth - valueWidth - 50;
    const startY = headerHeight;
    
    // 绘制标题区域
    ctx.fillStyle = '#ECF2F5';
    ctx.font = 'bold 18px Arial, "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'left';
    const heatmapTitle = currentLanguage === 'zh' ? '场景偏好强度分析' : 'Scenario Preference Intensity Analysis';
    ctx.fillText(heatmapTitle, 20, 40);
    
    // 绘制副标题
    ctx.fillStyle = '#8FA0B8';
    ctx.font = '13px Arial, "Microsoft YaHei", sans-serif';
    const subtitle = currentLanguage === 'zh' 
        ? `共 ${sortedScenarios.length} 个场景 | 强度范围: ${minValue} - ${maxValue}`
        : `${sortedScenarios.length} scenarios | Intensity range: ${minValue} - ${maxValue}`;
    ctx.fillText(subtitle, 20, 60);
    
    // 绘制类别标签和图例
    let currentY = startY;
    let currentCategory = '';
    const categoryColors = {
        [t('dataFields.coreNeeds')]: '#7FE8C1',
        [t('dataFields.concerns')]: '#7DA6FF',
        [t('dataFields.purchaseStage')]: '#A78BFA',
        [t('dataFields.priceSensitivity')]: '#F472B6',
        [t('dataFields.productPreference')]: '#60A5FA'
    };
    
    sortedScenarios.forEach((scenario, index) => {
        // 绘制类别分隔
        if (scenario.category !== currentCategory) {
            // 如果不是第一个类别，添加间距
            if (currentCategory !== '') {
                currentY += categorySpacing;
            }
            currentCategory = scenario.category;
            
            // 绘制类别标签背景
            const categoryColor = categoryColors[scenario.category] || '#8FA0B8';
            const categoryLabelY = currentY;
            
            ctx.fillStyle = categoryColor + '20';
            ctx.fillRect(15, categoryLabelY, width - 30, categoryHeaderHeight);
            
            // 绘制类别标签文字
            ctx.fillStyle = categoryColor;
            ctx.font = 'bold 15px Arial, "Microsoft YaHei", sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText(scenario.category, 25, categoryLabelY + 20);
            
            // 绘制类别分隔线
            ctx.strokeStyle = categoryColor + '40';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(15, categoryLabelY + categoryHeaderHeight);
            ctx.lineTo(width - 15, categoryLabelY + categoryHeaderHeight);
            ctx.stroke();
            
            // 更新currentY到类别标签下方
            currentY += categoryHeaderHeight;
        }
        
        // 计算颜色强度（0-1）
        const normalizedValue = (scenario.value - minValue) / valueRange;
        
        // 使用渐变色：从深色到亮色
        const colorIntensity = normalizedValue;
        const baseColor = categoryColors[scenario.category] || '#8FA0B8';
        
        // 将hex颜色转换为RGB
        const hex = baseColor.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        
        // 根据强度调整颜色（强度越高，颜色越亮）
        const alpha = 0.3 + colorIntensity * 0.7; // 透明度从0.3到1.0
        const brightR = Math.round(r + (255 - r) * colorIntensity * 0.3);
        const brightG = Math.round(g + (255 - g) * colorIntensity * 0.3);
        const brightB = Math.round(b + (255 - b) * colorIntensity * 0.3);
        
        // 绘制热力单元格
        const cellY = currentY;
        const cellHeightInner = cellHeight - cellPadding * 2;
        
        // 绘制单元格背景（渐变）
        const cellGradient = ctx.createLinearGradient(labelWidth, cellY, labelWidth + heatmapWidth, cellY);
        cellGradient.addColorStop(0, `rgba(${brightR}, ${brightG}, ${brightB}, ${alpha * 0.5})`);
        cellGradient.addColorStop(1, `rgba(${brightR}, ${brightG}, ${brightB}, ${alpha})`);
        ctx.fillStyle = cellGradient;
        ctx.fillRect(labelWidth, cellY + cellPadding, heatmapWidth, cellHeightInner);
        
        // 绘制边框（更精致的边框）
        ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.4)`;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(labelWidth, cellY + cellPadding, heatmapWidth, cellHeightInner);
        
        // 绘制进度条（在热力单元格内，更明显）
        const progressWidth = (normalizedValue * heatmapWidth) - 8;
        if (progressWidth > 0) {
            const progressGradient = ctx.createLinearGradient(labelWidth + 4, cellY + cellPadding + 4, labelWidth + 4 + progressWidth, cellY + cellPadding + 4);
            progressGradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 0.9)`);
            progressGradient.addColorStop(1, categoryColors[scenario.category] || `rgba(${r}, ${g}, ${b}, 0.95)`);
            ctx.fillStyle = progressGradient;
            ctx.fillRect(labelWidth + 4, cellY + cellPadding + 4, progressWidth, cellHeightInner - 8);
            
            // 进度条高光
            ctx.fillStyle = `rgba(255, 255, 255, 0.2)`;
            ctx.fillRect(labelWidth + 4, cellY + cellPadding + 4, progressWidth, 2);
        }
        
        // 绘制场景名称（更清晰的文字）
        ctx.fillStyle = '#ECF2F5';
        ctx.font = '14px Arial, "Microsoft YaHei", sans-serif';
        ctx.textAlign = 'left';
        // 翻译场景名称
        let translatedName = scenario.name;
        if (currentLanguage === 'en' && typeof translateKeyCharacteristic === 'function') {
            // 尝试翻译场景名称
            const translated = translateKeyCharacteristic(`场景: ${scenario.name}`);
            translatedName = translated.split(':')[1]?.trim() || scenario.name;
        }
        const maxNameLength = Math.floor((labelWidth - 40) / 9);
        const displayName = translatedName.length > maxNameLength ? translatedName.substring(0, maxNameLength) + '...' : translatedName;
        ctx.fillText(displayName, 25, cellY + cellHeight / 2 + 5);
        
        // 绘制数值（带背景）
        const valueText = scenario.value.toString();
        ctx.font = 'bold 13px Arial, "Microsoft YaHei", sans-serif';
        const valueTextWidth = ctx.measureText(valueText).width;
        const valueX = labelWidth + heatmapWidth + valueWidth - 15;
        const valueY = cellY + cellHeight / 2 + 5;
        
        // 数值背景
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, 0.2)`;
        ctx.fillRect(valueX - valueTextWidth - 8, cellY + cellPadding + 6, valueTextWidth + 12, cellHeightInner - 12);
        
        // 数值文字
        ctx.fillStyle = categoryColors[scenario.category] || '#ECF2F5';
        ctx.textAlign = 'right';
        ctx.fillText(valueText, valueX, valueY);
        
        // 移动到下一个单元格位置
        currentY += cellHeight;
    });
    
    // 绘制图例 - 专业设计
    const legendY = height - 40;
    const legendHeight = 20;
    
    // 图例标题
    ctx.fillStyle = '#8FA0B8';
    ctx.font = 'bold 13px Arial, "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('强度图例:', labelWidth + 10, legendY - 5);
    
    // 图例标签
    ctx.font = '12px Arial, "Microsoft YaHei", sans-serif';
    ctx.fillText('低', labelWidth + 100, legendY + 8);
    ctx.fillText('高', labelWidth + heatmapWidth - 50, legendY + 8);
    
    // 绘制图例渐变条
    const legendStartX = labelWidth + 140;
    const legendWidth = heatmapWidth - 200;
    const legendGradient = ctx.createLinearGradient(legendStartX, legendY, legendStartX + legendWidth, legendY);
    legendGradient.addColorStop(0, 'rgba(143, 160, 184, 0.3)');
    legendGradient.addColorStop(0.3, 'rgba(125, 166, 255, 0.5)');
    legendGradient.addColorStop(0.7, 'rgba(167, 139, 250, 0.7)');
    legendGradient.addColorStop(1, 'rgba(127, 232, 193, 0.9)');
    
    // 图例背景
    ctx.fillStyle = 'rgba(17, 27, 46, 0.5)';
    ctx.fillRect(legendStartX, legendY, legendWidth, legendHeight);
    
    // 图例渐变
    ctx.fillStyle = legendGradient;
    ctx.fillRect(legendStartX + 2, legendY + 2, legendWidth - 4, legendHeight - 4);
    
    // 图例边框
    ctx.strokeStyle = 'rgba(143, 160, 184, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.strokeRect(legendStartX, legendY, legendWidth, legendHeight);
    
    // 图例刻度
    ctx.fillStyle = '#8FA0B8';
    ctx.font = '10px Arial, "Microsoft YaHei", sans-serif';
    for (let i = 0; i <= 4; i++) {
        const tickX = legendStartX + (legendWidth / 4) * i;
        ctx.beginPath();
        ctx.moveTo(tickX, legendY + legendHeight);
        ctx.lineTo(tickX, legendY + legendHeight + 4);
        ctx.stroke();
        if (i % 2 === 0) {
            const value = minValue + (maxValue - minValue) * (i / 4);
            ctx.fillText(Math.round(value).toString(), tickX - 10, legendY + legendHeight + 16);
        }
    }
}

// 用户转化路径可视化
function loadJourney() {
    if (typeof businessInsights === 'undefined' || businessInsights.length === 0) {
        console.error('businessInsights 数据未加载');
        return;
    }
    
    const container = document.getElementById('journeyVisualization');
    if (!container) return;
    
    // 按购买阶段分组聚类
    const stages = {
        '浏览阶段': [],
        '对比阶段': [],
        '决策阶段': []
    };
    
    businessInsights.forEach(insight => {
        const stageMatch = insight.key_characteristics.find(c => c.includes('购买阶段'));
        if (stageMatch) {
            const stage = stageMatch.split(':')[1]?.trim() || '浏览阶段';
            if (stages[stage]) {
                const size = parseInt(insight.key_characteristics[0].match(/(\d+)\s*个意图片段/)?.[1] || 0);
                stages[stage].push({
                    ...insight,
                    size: size
                });
            }
        }
    });
    
    // 按规模排序
    Object.keys(stages).forEach(stage => {
        stages[stage].sort((a, b) => b.size - a.size);
    });
    
    // 计算转化漏斗数据
    const funnelData = {
        '浏览阶段': stages['浏览阶段'].reduce((sum, c) => sum + c.size, 0),
        '对比阶段': stages['对比阶段'].reduce((sum, c) => sum + c.size, 0),
        '决策阶段': stages['决策阶段'].reduce((sum, c) => sum + c.size, 0)
    };
    
    // 生成可视化
    container.innerHTML = `
        <div class="journey-visualization-container">
            <div class="journey-funnel-section">
                <h3>${t('journey.path.funnelAnalysis')}</h3>
                <p class="section-subtitle">${t('journey.path.funnelSubtitle')}</p>
                <div class="funnel-container">
                    <canvas id="journeyFunnelChart"></canvas>
                </div>
            </div>
            <div class="journey-flow-section">
                <h3>${t('journey.path.flowChart')}</h3>
                <p class="section-subtitle">${t('journey.path.flowSubtitle')}</p>
                <div class="flow-diagram-container">
                    <canvas id="journeyFlowChart"></canvas>
                </div>
            </div>
            <div class="journey-clusters-section">
                ${generateJourneyHTML(stages)}
            </div>
        </div>
    `;
    
    // 渲染漏斗图
    setTimeout(() => {
        createJourneyFunnelChart('journeyFunnelChart', funnelData);
        createJourneyFlowChart('journeyFlowChart', stages);
    }, 100);
    
    // 添加交互效果
    initJourneyInteractions();
}

// 创建转化漏斗图
function createJourneyFunnelChart(canvasId, funnelData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;
    const width = container ? container.offsetWidth : 800;
    const height = 400;
    
    canvas.width = width;
    canvas.height = height;
    canvas.style.width = '100%';
    canvas.style.height = height + 'px';
    
    // 计算数据
    const stages = ['浏览阶段', '对比阶段', '决策阶段'];
    const values = stages.map(s => funnelData[s] || 0);
    const maxValue = Math.max(...values);
    
    // 计算转化率
    const conversionRates = [];
    for (let i = 0; i < values.length; i++) {
        if (i === 0) {
            conversionRates.push(100);
        } else {
            const rate = values[i] > 0 ? (values[i] / values[i-1] * 100).toFixed(1) : 0;
            conversionRates.push(parseFloat(rate));
        }
    }
    
    // 绘制背景
    ctx.fillStyle = 'rgba(17, 27, 46, 0.3)';
    ctx.fillRect(0, 0, width, height);
    
    // 漏斗图参数
    const funnelTopWidth = width * 0.6;
    const funnelBottomWidth = width * 0.3;
    const funnelHeight = height - 120;
    const startY = 60;
    const centerX = width / 2;
    const stageHeight = funnelHeight / stages.length;
    
    // 颜色配置
    const stageColors = {
        '浏览阶段': '#60A5FA',
        '对比阶段': '#FBBF24',
        '决策阶段': '#7FE8C1'
    };
    
    // 绘制漏斗
    stages.forEach((stage, index) => {
        const topWidth = funnelTopWidth - (funnelTopWidth - funnelBottomWidth) * (index / stages.length);
        const bottomWidth = funnelTopWidth - (funnelTopWidth - funnelBottomWidth) * ((index + 1) / stages.length);
        const y = startY + index * stageHeight;
        const value = values[index];
        const widthRatio = value / maxValue;
        const actualTopWidth = funnelBottomWidth + (funnelTopWidth - funnelBottomWidth) * (1 - index / stages.length) * widthRatio;
        const actualBottomWidth = funnelBottomWidth + (funnelTopWidth - funnelBottomWidth) * (1 - (index + 1) / stages.length) * widthRatio;
        
        const color = stageColors[stage] || '#8FA0B8';
        
        // 绘制漏斗段
        ctx.beginPath();
        ctx.moveTo(centerX - actualTopWidth / 2, y);
        ctx.lineTo(centerX + actualTopWidth / 2, y);
        ctx.lineTo(centerX + actualBottomWidth / 2, y + stageHeight);
        ctx.lineTo(centerX - actualBottomWidth / 2, y + stageHeight);
        ctx.closePath();
        
        // 渐变填充
        const gradient = ctx.createLinearGradient(centerX - actualTopWidth / 2, y, centerX + actualTopWidth / 2, y + stageHeight);
        gradient.addColorStop(0, color + '80');
        gradient.addColorStop(1, color + '40');
        ctx.fillStyle = gradient;
        ctx.fill();
        
        // 边框
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // 绘制数值和标签
        const stageTranslations = {
            '浏览阶段': t('stages.browsing'),
            '对比阶段': t('stages.comparison'),
            '决策阶段': t('stages.decision')
        };
        const displayStage = stageTranslations[stage] || stage;
        ctx.fillStyle = '#ECF2F5';
        ctx.font = 'bold 16px Arial, "Microsoft YaHei", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(displayStage, centerX, y + stageHeight / 2 - 20);
        
        ctx.font = 'bold 24px Arial, "Microsoft YaHei", sans-serif';
        ctx.fillText(value.toString(), centerX, y + stageHeight / 2 + 10);
        
        // 转化率
        if (index > 0) {
            ctx.fillStyle = '#8FA0B8';
            ctx.font = '12px Arial, "Microsoft YaHei", sans-serif';
            const rate = conversionRates[index];
            const lossRate = (100 - rate).toFixed(1);
            const conversionLabel = currentLanguage === 'zh' ? '转化率' : 'Conversion Rate';
            const lossLabel = currentLanguage === 'zh' ? '流失' : 'Loss';
            ctx.fillText(`${conversionLabel}: ${rate}% (${lossLabel}: ${lossRate}%)`, centerX, y + stageHeight / 2 + 30);
        }
    });
    
    // 绘制标题
    ctx.fillStyle = '#ECF2F5';
    ctx.font = 'bold 18px Arial, "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'left';
    const funnelTitle = t('journey.path.funnelChart');
    ctx.fillText(funnelTitle, 20, 30);
}

// 创建转化路径流程图
function createJourneyFlowChart(canvasId, stages) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;
    const width = container ? container.offsetWidth : 1000;
    const height = 300;
    
    canvas.width = width;
    canvas.height = height;
    canvas.style.width = '100%';
    canvas.style.height = height + 'px';
    
    // 计算每个阶段的总数
    const stageTotals = {};
    Object.keys(stages).forEach(stage => {
        stageTotals[stage] = stages[stage].reduce((sum, c) => sum + c.size, 0);
    });
    
    const total = Object.values(stageTotals).reduce((sum, v) => sum + v, 0);
    
    // 阶段配置
    const stageConfig = {
        '浏览阶段': { color: '#60A5FA', x: width * 0.15 },
        '对比阶段': { color: '#FBBF24', x: width * 0.5 },
        '决策阶段': { color: '#7FE8C1', x: width * 0.85 }
    };
    
    const nodeRadius = 60;
    const centerY = height / 2;
    
    // 绘制连接线和箭头
    const stagesList = ['浏览阶段', '对比阶段', '决策阶段'];
    for (let i = 0; i < stagesList.length - 1; i++) {
        const fromStage = stagesList[i];
        const toStage = stagesList[i + 1];
        const fromX = stageConfig[fromStage].x;
        const toX = stageConfig[toStage].x;
        
        // 计算转化率
        const fromValue = stageTotals[fromStage];
        const toValue = stageTotals[toStage];
        const conversionRate = fromValue > 0 ? (toValue / fromValue * 100).toFixed(1) : 0;
        const lossRate = (100 - conversionRate).toFixed(1);
        
        // 绘制连接线
        ctx.strokeStyle = stageConfig[toStage].color + '60';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(fromX + nodeRadius, centerY);
        ctx.lineTo(toX - nodeRadius, centerY);
        ctx.stroke();
        
        // 绘制箭头
        const arrowX = toX - nodeRadius;
        ctx.fillStyle = stageConfig[toStage].color;
        ctx.beginPath();
        ctx.moveTo(arrowX, centerY);
        ctx.lineTo(arrowX - 15, centerY - 8);
        ctx.lineTo(arrowX - 15, centerY + 8);
        ctx.closePath();
        ctx.fill();
        
        // 绘制转化率标签
        const labelX = (fromX + toX) / 2;
        ctx.fillStyle = '#8FA0B8';
        ctx.font = '12px Arial, "Microsoft YaHei", sans-serif';
        ctx.textAlign = 'center';
        const conversionLabel = currentLanguage === 'zh' ? '转化' : 'Conversion';
        const lossLabel = currentLanguage === 'zh' ? '流失' : 'Loss';
        ctx.fillText(`${conversionLabel}: ${conversionRate}%`, labelX, centerY - 15);
        ctx.fillText(`${lossLabel}: ${lossRate}%`, labelX, centerY + 30);
    }
    
    // 绘制节点
    stagesList.forEach((stage, index) => {
        const config = stageConfig[stage];
        const value = stageTotals[stage];
        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
        
        // 绘制节点圆圈
        ctx.beginPath();
        ctx.arc(config.x, centerY, nodeRadius, 0, Math.PI * 2);
        ctx.fillStyle = config.color + '30';
        ctx.fill();
        ctx.strokeStyle = config.color;
        ctx.lineWidth = 3;
        ctx.stroke();
        
        // 绘制阶段名称
        const stageTranslations = {
            '浏览阶段': t('stages.browsing'),
            '对比阶段': t('stages.comparison'),
            '决策阶段': t('stages.decision')
        };
        const displayStage = stageTranslations[stage] || stage;
        ctx.fillStyle = '#ECF2F5';
        ctx.font = 'bold 14px Arial, "Microsoft YaHei", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(displayStage, config.x, centerY - 15);
        
        // 绘制数值
        ctx.font = 'bold 20px Arial, "Microsoft YaHei", sans-serif';
        ctx.fillText(value.toString(), config.x, centerY + 10);
        
        // 绘制百分比
        ctx.fillStyle = '#8FA0B8';
        ctx.font = '12px Arial, "Microsoft YaHei", sans-serif';
        ctx.fillText(`${percentage}%`, config.x, centerY + 30);
    });
}

// 生成转化路径HTML
function generateJourneyHTML(stages) {
    const stageConfig = {
        '浏览阶段': {
            color: '#60A5FA',
            gradient: 'linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%)',
            description: t('stages.browsingDesc'),
            name: t('stages.browsing')
        },
        '对比阶段': {
            color: '#FBBF24',
            gradient: 'linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%)',
            description: t('stages.comparisonDesc'),
            name: t('stages.comparison')
        },
        '决策阶段': {
            color: '#7FE8C1',
            gradient: 'linear-gradient(135deg, #7FE8C1 0%, #34D399 100%)',
            description: t('stages.decisionDesc'),
            name: t('stages.decision')
        }
    };
    
    let html = '<div class="journey-path">';
    
    Object.entries(stages).forEach(([stageName, clusters], index) => {
        const config = stageConfig[stageName];
        const totalUsers = clusters.reduce((sum, c) => sum + c.size, 0);
        const percentage = clusters.length > 0 ? Math.round((totalUsers / businessInsights.reduce((sum, i) => {
            const size = parseInt(i.key_characteristics[0].match(/(\d+)\s*个意图片段/)?.[1] || 0);
            return sum + size;
        }, 0)) * 100) : 0;
        
        html += `
            <div class="journey-stage" data-stage="${stageName}">
                <div class="stage-header">
                    <div class="stage-icon" style="background: ${config.gradient}">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                            ${stageName === '浏览阶段' ? '<path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>' : ''}
                            ${stageName === '对比阶段' ? '<path d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"/><path d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10"/><path d="M13 7h7a1 1 0 011 1v7"/><path d="M13 12h7"/>' : ''}
                            ${stageName === '决策阶段' ? '<path d="M9 12l2 2 4-4"/><path d="M21 12c-1 0-2-1-2-2s1-2 2-2 2 1 2 2-1 2-2 2"/><path d="M3 12c1 0 2-1 2-2s-1-2-2-2-2 1-2 2 1 2 2 2"/><path d="M12 3c0 1-1 2-2 2s-2-1-2-2 1-2 2-2 2 1 2 2"/><path d="M12 21c0-1 1-2 2-2s2 1 2 2-1 2-2 2-2-1-2-2"/>' : ''}
                        </svg>
                    </div>
                    <div class="stage-info">
                        <h2>${config.name || stageName}</h2>
                        <p>${config.description}</p>
                        <div class="stage-stats">
                            <span class="stat-item">
                                <strong>${clusters.length}</strong> ${t('stages.personas')}
                            </span>
                            <span class="stat-item">
                                <strong>${totalUsers}</strong> ${t('stages.segments')}
                            </span>
                            <span class="stat-item">
                                <strong>${percentage}%</strong> ${t('stages.percentage')}
                            </span>
                        </div>
                    </div>
                </div>
                
                <div class="clusters-grid">
                    ${clusters.map((cluster, idx) => {
                        const size = cluster.size;
                        const sizePercentage = totalUsers > 0 ? Math.round((size / totalUsers) * 100) : 0;
                        return `
                            <div class="cluster-card" data-cluster-id="${cluster.cluster_id}" style="animation-delay: ${idx * 0.1}s">
                                <div class="cluster-header">
                                    <div class="cluster-badge" style="background: ${config.gradient}">
                                        ${t('cluster.label')} ${cluster.cluster_id}
                                    </div>
                                    <div class="cluster-size">
                                        ${size} ${t('cluster.segments')}
                                    </div>
                                </div>
                                <h3 class="cluster-name">${getClusterDisplayName(cluster.user_segment_name)}</h3>
                                <div class="cluster-progress">
                                    <div class="progress-bar" style="width: ${sizePercentage}%; background: ${config.gradient}"></div>
                                    <span class="progress-text">${sizePercentage}%</span>
                                </div>
                                <div class="cluster-characteristics">
                                    ${cluster.key_characteristics.slice(1, 4).map(char => {
                                        const translatedChar = typeof translateKeyCharacteristic === 'function' 
                                            ? translateKeyCharacteristic(char) 
                                            : char;
                                        const [key, value] = translatedChar.split(':');
                                        return `<div class="char-item">
                                            <span class="char-key">${key?.trim() || ''}:</span>
                                            <span class="char-value">${value?.trim() || ''}</span>
                                        </div>`;
                                    }).join('')}
                                </div>
                                <div class="cluster-actions">
                                    <button class="btn-view-details" data-cluster-id="${cluster.cluster_id}">
                                        <span class="btn-text">${currentLanguage === 'zh' ? '查看详情' : 'View Details'}</span>
                                        <span class="btn-arrow">→</span>
                                    </button>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                
                ${index < Object.keys(stages).length - 1 ? `
                    <div class="stage-connector">
                        <svg width="100%" height="60" viewBox="0 0 200 60" preserveAspectRatio="none">
                            <path d="M 0 30 Q 100 0, 200 30" 
                                  stroke="${config.color}" 
                                  stroke-width="3" 
                                  fill="none" 
                                  stroke-dasharray="5,5"
                                  opacity="0.5"/>
                            <path d="M 0 30 Q 100 60, 200 30" 
                                  stroke="${config.color}" 
                                  stroke-width="3" 
                                  fill="none" 
                                  stroke-dasharray="5,5"
                                  opacity="0.5"/>
                            <circle cx="100" cy="30" r="8" fill="${config.color}" opacity="0.8">
                                <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>
                            </circle>
                        </svg>
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    
    return html;
}

// 加载转化分析页面
function loadJourneyPage() {
    // 默认显示转化路径
    switchSubTab('path');
}

// 加载用户分析页面
function loadUserAnalysisPage() {
    // 默认显示用户画像
    switchSubTab('portrait');
}

// 加载金融市场分析页面
function loadFinancialAnalysisPage() {
    // 加载YUP数据
    loadYUPData();
    // 默认显示聚类总览
    switchFinancialSubTab('overview');
}

// 加载YUP数据
function loadYUPData() {
    // 检查是否已加载YUP数据
    if (typeof window.yupDataLoaded !== 'undefined' && window.yupDataLoaded) {
        // 数据已加载，直接使用
        return;
    }
    
    // 尝试从multi_shop_data.js加载YUP数据
    if (typeof shopData !== 'undefined' && shopData['YUP']) {
        window.financialBusinessInsights = shopData['YUP'].businessInsights || [];
        window.financialUserPortraits = shopData['YUP'].userPortraits || [];
        window.financialStats = shopData['YUP'].stats || {};
        window.financialTimeSeries = shopData['YUP'].timeSeries || [];
        window.financialUserTrajectories = shopData['YUP'].userTrajectories || [];
        window.yupDataLoaded = true;
        console.log('YUP数据已从multi_shop_data.js加载');
        return;
    }
    
    // 尝试从data_shop_YUP.js加载
    const script = document.createElement('script');
    script.src = 'data_shop_YUP.js';
    script.onload = function() {
        if (typeof businessInsights !== 'undefined') {
            window.financialBusinessInsights = businessInsights;
            window.financialUserPortraits = userPortraits || [];
            window.financialStats = stats || {};
            window.financialTimeSeries = timeSeries || [];
            window.financialUserTrajectories = userTrajectories || [];
            window.yupDataLoaded = true;
            console.log('YUP数据已从data_shop_YUP.js加载');
            // 重新加载当前页面
            const activeTab = document.querySelector('.tab-content.active');
            if (activeTab && activeTab.id === 'financial') {
                loadFinancialAnalysisPage();
            }
        }
    };
    script.onerror = function() {
        console.error('无法加载YUP数据文件');
        const container = document.getElementById('financialPortraitCards');
        if (container) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>无法加载YUP数据，请确保data_shop_YUP.js文件存在</p></div>';
        }
    };
    document.head.appendChild(script);
}

// 切换金融分析子标签页（优化性能）
function switchFinancialSubTab(subTabName) {
    const financialTab = document.getElementById('financial');
    if (!financialTab) return;
    
    // 使用requestAnimationFrame优化切换
    requestAnimationFrame(() => {
        // 更新按钮状态
        financialTab.querySelectorAll('.sub-tab-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-sub-tab') === `financial-${subTabName}`) {
                btn.classList.add('active');
            }
        });
        
        // 更新内容显示
        financialTab.querySelectorAll('.sub-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        const targetContent = document.getElementById(`subTab-financial-${subTabName}`);
        if (targetContent) {
            targetContent.classList.add('active');
        }
        
        // 根据子标签页加载相应内容（延迟加载）
        setTimeout(() => {
            if (subTabName === 'overview') {
                loadFinancialOverview();
            } else if (subTabName === 'portrait') {
                loadFinancialUserTrajectories();
            } else if (subTabName === 'clusters') {
                loadFinancialClusters();
            }
        }, 50);
    });
}

// 加载金融分析总览（优化性能）
function loadFinancialOverview() {
    if (!window.financialBusinessInsights || window.financialBusinessInsights.length === 0) {
        console.warn('金融分析数据未加载，尝试加载YUP数据...');
        loadYUPData();
        setTimeout(() => loadFinancialOverview(), 500);
        return;
    }
    
    // 使用requestAnimationFrame优化渲染
    requestAnimationFrame(() => {
        // 计算业务指标
        const insights = window.financialBusinessInsights;
        const totalUsers = window.financialStats?.totalUsers || 0;
        const totalSegments = window.financialStats?.totalSegments || 0;
        
        // 计算交易完成率
        const completedUsers = insights.reduce((sum, i) => {
            return sum + (i.key_characteristics?.transaction_status === '已完成' ? (i.key_characteristics?.user_count || 0) : 0);
        }, 0);
        const transactionRate = totalUsers > 0 ? ((completedUsers / totalUsers) * 100).toFixed(1) : 0;
        
        // 计算KYC完成率
        const kycStartedUsers = insights.reduce((sum, i) => {
            return sum + (i.key_characteristics?.kyc_status === '已开始' ? (i.key_characteristics?.user_count || 0) : 0);
        }, 0);
        const kycRate = totalUsers > 0 ? ((kycStartedUsers / totalUsers) * 100).toFixed(1) : 0;
        
        // 计算平均意图强度
        const avgIntentScore = totalUsers > 0 ? insights.reduce((sum, i) => {
            return sum + ((i.key_characteristics?.avg_intent_score || 0) * (i.key_characteristics?.user_count || 0));
        }, 0) / totalUsers : 0;
        const intentScorePercent = (avgIntentScore * 100).toFixed(0);
        
        // 更新核心业务指标
        const statsContainer = document.getElementById('financialStats');
        if (statsContainer) {
            statsContainer.innerHTML = `
            <div class="kpi-card" style="background: var(--card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; width: 80px; height: 80px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%); border-radius: 0 0 0 100%;"></div>
                <div style="display: flex; align-items: center; gap: 1rem; position: relative; z-index: 1;">
                    <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; flex-shrink: 0;">👥</div>
                    <div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: var(--text); line-height: 1;">${totalUsers}</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.25rem;">总用户数</div>
                    </div>
                </div>
            </div>
            <div class="kpi-card" style="background: var(--card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; width: 80px; height: 80px; background: linear-gradient(135deg, rgba(79, 172, 254, 0.2) 0%, rgba(0, 242, 254, 0.2) 100%); border-radius: 0 0 0 100%;"></div>
                <div style="display: flex; align-items: center; gap: 1rem; position: relative; z-index: 1;">
                    <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; flex-shrink: 0;">✅</div>
                    <div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: var(--text); line-height: 1;">${transactionRate}%</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.25rem;">交易完成率</div>
                    </div>
                </div>
            </div>
            <div class="kpi-card" style="background: var(--card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; width: 80px; height: 80px; background: linear-gradient(135deg, rgba(67, 233, 123, 0.2) 0%, rgba(56, 249, 215, 0.2) 100%); border-radius: 0 0 0 100%;"></div>
                <div style="display: flex; align-items: center; gap: 1rem; position: relative; z-index: 1;">
                    <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; flex-shrink: 0;">🔐</div>
                    <div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: var(--text); line-height: 1;">${kycRate}%</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.25rem;">身份验证率</div>
                    </div>
                </div>
            </div>
            <div class="kpi-card" style="background: var(--card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; width: 80px; height: 80px; background: linear-gradient(135deg, rgba(240, 147, 251, 0.2) 0%, rgba(245, 87, 108, 0.2) 100%); border-radius: 0 0 0 100%;"></div>
                <div style="display: flex; align-items: center; gap: 1rem; position: relative; z-index: 1;">
                    <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; flex-shrink: 0;">⚡</div>
                    <div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: var(--text); line-height: 1;">${intentScorePercent}%</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.25rem;">平均意图强度</div>
                    </div>
                </div>
            </div>
        `;
        }
        
        // 延迟加载非关键内容
        setTimeout(() => {
            // 加载快速洞察
            loadFinancialQuickInsights();
            
            // 加载用户分组
            loadFinancialUserGroups();
        }, 100);
        
        // 延迟加载图表（最耗时）
        setTimeout(() => {
            loadFinancialCharts();
        }, 300);
    });
}

// 图表实例缓存
const financialChartInstances = {};

// 加载金融分析图表（延迟加载优化性能）
function loadFinancialCharts() {
    if (!window.financialBusinessInsights || window.financialBusinessInsights.length === 0) return;
    
    // 使用IntersectionObserver延迟加载图表，只在可见时渲染
    const chartCanvases = [
        { id: 'financialClusterDistributionChart', render: renderFinancialClusterDistributionChart },
        { id: 'financialKYCStatusChart', render: renderFinancialKYCStatusChart },
        { id: 'financialTransactionStatusChart', render: renderFinancialTransactionStatusChart },
        { id: 'financialMainActivityChart', render: renderFinancialMainActivityChart }
    ];
    
    chartCanvases.forEach(({ id, render }) => {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        
        // 销毁旧图表实例
        if (financialChartInstances[id]) {
            financialChartInstances[id].destroy();
            delete financialChartInstances[id];
        }
        
        // 使用IntersectionObserver延迟加载
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // 延迟渲染，避免阻塞
                    requestAnimationFrame(() => {
                        setTimeout(() => {
                            render(canvas);
                        }, 100);
                    });
                    observer.unobserve(entry.target);
                }
            });
        }, { rootMargin: '50px' });
        
        observer.observe(canvas);
    });
}

// 渲染聚类分布图
function renderFinancialClusterDistributionChart(canvas) {
    if (!window.financialBusinessInsights || typeof Chart === 'undefined') return;
    
    // 如果已有实例，先销毁
    if (financialChartInstances['financialClusterDistributionChart']) {
        financialChartInstances['financialClusterDistributionChart'].destroy();
    }
    
    const insights = window.financialBusinessInsights;
    
    // 计算每个聚类的用户数
    const clusterData = insights.map(insight => ({
        label: insight.user_segment_name || `聚类 ${insight.cluster_id}`,
        value: insight.key_characteristics?.user_count || 0,
        clusterId: insight.cluster_id
    })).filter(d => d.value > 0);
    
    if (clusterData.length === 0) return;
    
    // 使用Chart.js渲染
    financialChartInstances['financialClusterDistributionChart'] = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: clusterData.map(d => d.label),
            datasets: [{
                data: clusterData.map(d => d.value),
                backgroundColor: [
                    '#667eea', '#764ba2', '#f093fb', '#f5576c',
                    '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ECF2F5',
                        font: { size: 11 },
                        padding: 10,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// 渲染KYC状态分布图
function renderFinancialKYCStatusChart(canvas) {
    if (!window.financialBusinessInsights || typeof Chart === 'undefined') return;
    
    // 如果已有实例，先销毁
    if (financialChartInstances['financialKYCStatusChart']) {
        financialChartInstances['financialKYCStatusChart'].destroy();
    }
    
    const insights = window.financialBusinessInsights;
    
    // 统计KYC状态
    const kycStatusCounts = {};
    insights.forEach(insight => {
        const status = insight.key_characteristics?.kyc_status || '未知';
        kycStatusCounts[status] = (kycStatusCounts[status] || 0) + (insight.key_characteristics?.user_count || 0);
    });
    
    const labels = Object.keys(kycStatusCounts);
    const data = Object.values(kycStatusCounts);
    
    if (labels.length === 0) return;
    
    financialChartInstances['financialKYCStatusChart'] = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '用户数',
                data: data,
                backgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#ECF2F5', font: { size: 11 } },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                x: {
                    ticks: { color: '#ECF2F5', font: { size: 11 } },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                }
            }
        }
    });
}

// 渲染交易状态分布图
function renderFinancialTransactionStatusChart(canvas) {
    if (!window.financialBusinessInsights || typeof Chart === 'undefined') return;
    
    // 如果已有实例，先销毁
    if (financialChartInstances['financialTransactionStatusChart']) {
        financialChartInstances['financialTransactionStatusChart'].destroy();
    }
    
    const insights = window.financialBusinessInsights;
    
    // 统计交易状态
    const transactionStatusCounts = {};
    insights.forEach(insight => {
        const status = insight.key_characteristics?.transaction_status || '未知';
        transactionStatusCounts[status] = (transactionStatusCounts[status] || 0) + (insight.key_characteristics?.user_count || 0);
    });
    
    const labels = Object.keys(transactionStatusCounts);
    const data = Object.values(transactionStatusCounts);
    
    if (labels.length === 0) return;
    
    financialChartInstances['financialTransactionStatusChart'] = new Chart(canvas, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#4facfe', '#00f2fe', '#43e97b', '#f5576c']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#ECF2F5', font: { size: 11 }, padding: 10, usePointStyle: true }
                }
            }
        }
    });
}

// 渲染主要活动分布图
function renderFinancialMainActivityChart(canvas) {
    if (!window.financialBusinessInsights || typeof Chart === 'undefined') return;
    
    // 如果已有实例，先销毁
    if (financialChartInstances['financialMainActivityChart']) {
        financialChartInstances['financialMainActivityChart'].destroy();
    }
    
    const insights = window.financialBusinessInsights;
    
    // 统计主要活动
    const activityCounts = {};
    insights.forEach(insight => {
        const activity = insight.key_characteristics?.main_activity || '未知';
        activityCounts[activity] = (activityCounts[activity] || 0) + (insight.key_characteristics?.user_count || 0);
    });
    
    const labels = Object.keys(activityCounts);
    const data = Object.values(activityCounts);
    
    if (labels.length === 0) return;
    
    financialChartInstances['financialMainActivityChart'] = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '用户数',
                data: data,
                backgroundColor: '#f093fb'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { color: '#ECF2F5', font: { size: 11 } },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                y: {
                    ticks: { color: '#ECF2F5', font: { size: 11 } },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                }
            }
        }
    });
}

// 加载快速洞察
function loadFinancialQuickInsights() {
    if (!window.financialBusinessInsights) return;
    
    const container = document.getElementById('financialQuickInsights');
    if (!container) return;
    
    const insights = window.financialBusinessInsights;
    
    // 找出需要关注的用户群体
    const needsAttention = insights.filter(i => {
        const chars = i.key_characteristics || {};
        return (chars.transaction_status === '未开始' || chars.transaction_status === '进行中') && 
               (chars.user_count || 0) > 0;
    });
    
    // 找出高价值用户群体
    const highValue = insights.filter(i => {
        const chars = i.key_characteristics || {};
        return chars.transaction_status === '已完成' && (chars.user_count || 0) > 0;
    });
    
    container.innerHTML = '';
    
    // 需要关注的用户
    if (needsAttention.length > 0) {
        const card = document.createElement('div');
        card.style.cssText = 'background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(251, 113, 133, 0.15) 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(251, 191, 36, 0.3); margin-bottom: 1rem;';
        card.innerHTML = `
            <div style="display: flex; align-items: start; gap: 1rem;">
                <div style="font-size: 2rem; flex-shrink: 0;">⚠️</div>
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 0.5rem 0; color: var(--text); font-size: 1.1rem;">需要关注的用户群体</h4>
                    <p style="margin: 0 0 1rem 0; color: var(--text-secondary); font-size: 0.95rem;">有 ${needsAttention.length} 个用户群体尚未完成交易，建议优先跟进</p>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${needsAttention.slice(0, 3).map(i => {
                            const chars = i.key_characteristics || {};
                            return `<span style="padding: 0.5rem 1rem; background: rgba(251, 191, 36, 0.2); border-radius: 6px; font-size: 0.9rem; color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.3);">
                                ${i.user_segment_name || `群体${i.cluster_id}`} (${chars.user_count || 0}人)
                            </span>`;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
        container.appendChild(card);
    }
    
    // 高价值用户
    if (highValue.length > 0) {
        const card = document.createElement('div');
        card.style.cssText = 'background: linear-gradient(135deg, rgba(67, 233, 123, 0.15) 0%, rgba(56, 249, 215, 0.15) 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(67, 233, 123, 0.3);';
        card.innerHTML = `
            <div style="display: flex; align-items: start; gap: 1rem;">
                <div style="font-size: 2rem; flex-shrink: 0;">✨</div>
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 0.5rem 0; color: var(--text); font-size: 1.1rem;">高价值用户群体</h4>
                    <p style="margin: 0 0 1rem 0; color: var(--text-secondary); font-size: 0.95rem;">有 ${highValue.length} 个用户群体已完成交易，建议重点维护和复购营销</p>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${highValue.slice(0, 3).map(i => {
                            const chars = i.key_characteristics || {};
                            return `<span style="padding: 0.5rem 1rem; background: rgba(67, 233, 123, 0.2); border-radius: 6px; font-size: 0.9rem; color: #43e97b; border: 1px solid rgba(67, 233, 123, 0.3);">
                                ${i.user_segment_name || `群体${i.cluster_id}`} (${chars.user_count || 0}人)
                            </span>`;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
        container.appendChild(card);
    }
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 加载用户分组卡片（优化性能）
function loadFinancialUserGroups() {
    if (!window.financialBusinessInsights) return;
    
    const container = document.getElementById('financialUserGroups');
    if (!container) return;
    
    // 清空容器，避免重复添加
    container.innerHTML = '';
    
    // 使用DocumentFragment批量操作DOM
    const fragment = document.createDocumentFragment();
    
    // 去重：按 cluster_id 去重，保留用户数最多的
    const uniqueInsights = {};
    window.financialBusinessInsights.forEach(insight => {
        const clusterId = insight.cluster_id;
        if (!uniqueInsights[clusterId]) {
            uniqueInsights[clusterId] = insight;
        } else {
            // 如果已存在，保留用户数更多的
            const existingCount = uniqueInsights[clusterId].key_characteristics?.user_count || 0;
            const newCount = insight.key_characteristics?.user_count || 0;
            if (newCount > existingCount) {
                uniqueInsights[clusterId] = insight;
            }
        }
    });
    
    const insights = Object.values(uniqueInsights).sort((a, b) => {
        return (b.key_characteristics?.user_count || 0) - (a.key_characteristics?.user_count || 0);
    });
    
    // 使用requestAnimationFrame分批渲染
    let index = 0;
    const batchSize = 5;
    
    const renderBatch = () => {
        const endIndex = Math.min(index + batchSize, insights.length);
        
        for (let i = index; i < endIndex; i++) {
            const insight = insights[i];
            const chars = insight.key_characteristics || {};
            const userCount = chars.user_count || 0;
            if (userCount === 0) continue;
            
            const card = document.createElement('div');
            card.className = 'financial-group-card';
            card.dataset.clusterId = insight.cluster_id;
            card.style.cssText = 'background: var(--card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border); transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease; cursor: pointer; will-change: transform;';
            
            // 根据状态确定颜色
            let statusColor = '#667eea';
            let statusBg = 'rgba(102, 126, 234, 0.1)';
            let statusIcon = '👤';
            
            if (chars.transaction_status === '已完成') {
                statusColor = '#43e97b';
                statusBg = 'rgba(67, 233, 123, 0.1)';
                statusIcon = '✅';
            } else if (chars.transaction_status === '进行中') {
                statusColor = '#4facfe';
                statusBg = 'rgba(79, 172, 254, 0.1)';
                statusIcon = '🔄';
            } else if (chars.transaction_status === '未开始') {
                statusColor = '#FBBF24';
                statusBg = 'rgba(251, 191, 36, 0.1)';
                statusIcon = '⏳';
            }
            
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                            <div style="width: 40px; height: 40px; background: ${statusBg}; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; border: 2px solid ${statusColor};">${statusIcon}</div>
                            <div>
                                <h4 style="margin: 0; color: var(--text); font-size: 1.1rem; font-weight: 600;">${insight.full_label || insight.user_segment_name || insight.cluster_name || `用户群体 ${insight.cluster_id}`}</h4>
                                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem;">${userCount} 位用户${chars.main_activity ? ' · ' + chars.main_activity : ''}</div>
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: ${statusColor};">${userCount}</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">用户数</div>
                    </div>
                </div>
                
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
                    ${chars.transaction_status ? `<span style="padding: 0.4rem 0.8rem; background: ${statusBg}; color: ${statusColor}; border-radius: 6px; font-size: 0.85rem; font-weight: 500; border: 1px solid ${statusColor}40;">${chars.transaction_status}</span>` : ''}
                    ${chars.kyc_status ? `<span style="padding: 0.4rem 0.8rem; background: rgba(102, 126, 234, 0.1); color: #667eea; border-radius: 6px; font-size: 0.85rem; font-weight: 500; border: 1px solid rgba(102, 126, 234, 0.3);">${chars.kyc_status === '已开始' ? '已验证' : '未验证'}</span>` : ''}
                    ${chars.main_activity ? `<span style="padding: 0.4rem 0.8rem; background: rgba(240, 147, 251, 0.1); color: #f093fb; border-radius: 6px; font-size: 0.85rem; font-weight: 500; border: 1px solid rgba(240, 147, 251, 0.3);">${chars.main_activity}</span>` : ''}
                </div>
                
                ${insight.marketing_strategy && insight.marketing_strategy.length > 0 ? `
                    <div style="padding-top: 1rem; border-top: 1px solid var(--border);">
                        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem; font-weight: 500;">💡 运营建议</div>
                        <div style="font-size: 0.9rem; color: var(--text); line-height: 1.6;">${insight.marketing_strategy[0].replace(/【.*?】/g, '').substring(0, 60)}${insight.marketing_strategy[0].length > 60 ? '...' : ''}</div>
                    </div>
                ` : ''}
                
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); text-align: center;">
                    <span style="color: var(--accent); font-size: 0.9rem; font-weight: 500;">点击查看详情 →</span>
                </div>
            `;
            
            fragment.appendChild(card);
        }
        
        index = endIndex;
        
        if (index < insights.length) {
            requestAnimationFrame(renderBatch);
        } else {
            container.appendChild(fragment);
            // 使用事件委托优化事件监听
            initFinancialCardEvents(container);
        }
    };
    
    requestAnimationFrame(renderBatch);
}

// 使用事件委托优化卡片事件
function initFinancialCardEvents(container) {
    // 移除旧的事件监听器
    const newContainer = container.cloneNode(true);
    container.parentNode.replaceChild(newContainer, container);
    
    // 使用事件委托
    newContainer.addEventListener('mouseenter', throttle((e) => {
        const card = e.target.closest('.financial-group-card');
        if (card) {
            card.style.transform = 'translateY(-4px)';
            card.style.boxShadow = '0 8px 16px rgba(0,0,0,0.2)';
            card.style.borderColor = 'rgba(102, 126, 234, 0.5)';
        }
    }, 50), true);
    
    newContainer.addEventListener('mouseleave', throttle((e) => {
        const card = e.target.closest('.financial-group-card');
        if (card) {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = 'none';
            card.style.borderColor = 'var(--border)';
        }
    }, 50), true);
    
    newContainer.addEventListener('click', (e) => {
        const card = e.target.closest('.financial-group-card');
        if (card) {
            const clusterId = card.dataset.clusterId;
            showTab('financial');
            setTimeout(() => {
                switchFinancialSubTab('clusters');
                setTimeout(() => {
                    const select = document.getElementById('financialClusterSelect');
                    if (select) {
                        select.value = clusterId;
                        showFinancialClusterDetails(clusterId);
                    }
                }, 100);
            }, 300);
        }
    });
}

// 加载金融用户轨迹（参考主页面实现）
function loadFinancialUserTrajectories() {
    if (!window.financialUserTrajectories || window.financialUserTrajectories.length === 0) {
        console.warn('金融用户轨迹数据未加载');
        const container = document.getElementById('financialUserTrajectories');
        if (container) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>暂无用户轨迹数据</p></div>';
        }
        return;
    }
    
    // 过滤掉用户ID为空的用户
    const validUsers = window.financialUserTrajectories.filter(user => user.user_id && user.user_id.trim() !== '');
    
    if (validUsers.length === 0) {
        const container = document.getElementById('financialUserTrajectories');
        if (container) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>暂无有效用户轨迹数据</p></div>';
        }
        return;
    }
    
    // 加载聚类筛选选项（优先使用full_label）
    if (window.financialBusinessInsights && window.financialBusinessInsights.length > 0) {
        const clusterFilter = document.getElementById('financialClusterFilter');
        if (clusterFilter) {
            clusterFilter.innerHTML = '<option value="">所有聚类</option>';
            window.financialBusinessInsights.forEach(insight => {
                const option = document.createElement('option');
                option.value = insight.cluster_id;
                const displayName = insight.full_label || insight.user_segment_name || insight.cluster_name || '';
                option.textContent = `聚类 ${insight.cluster_id}: ${removeEmojiFromClusterName(displayName)}`;
                clusterFilter.appendChild(option);
            });
        }
    }
    
    // 渲染用户列表
    renderFinancialUserTrajectories(validUsers);
    
    // 绑定搜索和筛选事件
    const searchInput = document.getElementById('financialUserSearch');
    const clusterFilter = document.getElementById('financialClusterFilter');
    const sortOption = document.getElementById('financialSortOption');
    
    if (searchInput) {
        searchInput.removeEventListener('input', filterAndRenderFinancial);
        searchInput.addEventListener('input', () => filterAndRenderFinancial());
    }
    if (clusterFilter) {
        clusterFilter.removeEventListener('change', filterAndRenderFinancial);
        clusterFilter.addEventListener('change', () => filterAndRenderFinancial());
    }
    if (sortOption) {
        sortOption.removeEventListener('change', filterAndRenderFinancial);
        sortOption.addEventListener('change', () => filterAndRenderFinancial());
    }
}

// 筛选和渲染金融用户轨迹
function filterAndRenderFinancial() {
    if (!window.financialUserTrajectories) return;
    
    let filtered = [...window.financialUserTrajectories];
    
    // 过滤掉用户ID为空的用户
    filtered = filtered.filter(user => user.user_id && user.user_id.trim() !== '');
    
    // 搜索筛选
    const searchTerm = document.getElementById('financialUserSearch')?.value.toLowerCase() || '';
    if (searchTerm) {
        filtered = filtered.filter(user => 
            user.user_id.toLowerCase().includes(searchTerm)
        );
    }
    
    // 聚类筛选
    const clusterFilter = document.getElementById('financialClusterFilter')?.value || '';
    if (clusterFilter) {
        filtered = filtered.filter(user => 
            user.cluster_ids.includes(clusterFilter)
        );
    }
    
    // 排序
    const sortOption = document.getElementById('financialSortOption')?.value || 'time';
    if (sortOption === 'segments') {
        filtered.sort((a, b) => b.segment_count - a.segment_count);
    } else if (sortOption === 'clusters') {
        filtered.sort((a, b) => b.unique_clusters - a.unique_clusters);
    } else {
        // 按时间排序（第一个片段的时间）
        filtered.sort((a, b) => {
            if (a.segments.length === 0 || b.segments.length === 0) return 0;
            return a.segments[0].start_time.localeCompare(b.segments[0].start_time);
        });
    }
    
    renderFinancialUserTrajectories(filtered);
}

// 渲染金融用户轨迹列表
function renderFinancialUserTrajectories(users) {
    const container = document.getElementById('financialUserTrajectories');
    if (!container) return;
    
    if (users.length === 0) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>没有找到匹配的用户</p></div>';
        return;
    }
    
    container.innerHTML = '';
    
    users.forEach((user, index) => {
        const userCard = document.createElement('div');
        userCard.className = 'user-trajectory-card';
        userCard.style.animationDelay = `${index * 0.05}s`;
        
        // 获取聚类名称映射（优先使用full_label）
        const clusterNames = {};
        if (window.financialBusinessInsights) {
            window.financialBusinessInsights.forEach(insight => {
                const label = insight.full_label || insight.user_segment_name || insight.cluster_name || '';
                clusterNames[insight.cluster_id] = removeEmojiFromClusterName(label);
            });
        }
        
        // 计算用户行为统计（确保包含所有片段，包括时长为0的片段）
        const segments = user.segments || [];
        
        // 调试信息：输出所有片段
        console.log(`用户 ${user.user_id} 的片段:`, segments.map(s => ({
            index: s.segment_index,
            cluster_id: s.cluster_id,
            duration: s.duration_minutes,
            full_label: s.full_label
        })));
        
        const avgIntentScore = segments.length > 0 
            ? segments.reduce((sum, s) => sum + (s.intent_score || 0), 0) / segments.length 
            : 0;
        
        userCard.innerHTML = `
            <div class="user-header">
                <div class="user-id-section">
                    <h3 class="user-id">${user.user_id}</h3>
                    <div class="user-stats">
                        <span class="stat-badge">
                            <strong>${user.segment_count}</strong> 个片段
                        </span>
                        <span class="stat-badge">
                            <strong>${user.unique_clusters}</strong> 个聚类
                        </span>
                        <span class="stat-badge">
                            <strong>${user.total_duration.toFixed(1)}</strong> 秒
                        </span>
                        <span class="stat-badge">
                            <strong>${user.total_records}</strong> 次交互
                        </span>
                        <span class="stat-badge intent-badge">
                            <strong>${(avgIntentScore * 100).toFixed(0)}%</strong> 平均意图强度
                        </span>
                    </div>
                </div>
                <div class="user-clusters-summary">
                    <strong>聚类分布:</strong>
                    ${user.cluster_ids.map(cid => {
                        // 优先使用full_label，如果没有则使用cluster_name或user_segment_name
                        let name = clusterNames[cid] || `聚类${cid}`;
                        let characteristics = {};
                        if (window.financialBusinessInsights) {
                            const insight = window.financialBusinessInsights.find(i => String(i.cluster_id) === String(cid));
                            if (insight) {
                                name = insight.full_label || insight.user_segment_name || insight.cluster_name || name;
                                characteristics = insight.key_characteristics || {};
                            }
                        }
                        // 构建详细的tooltip信息
                        const tooltipParts = [getClusterDisplayName(name)];
                        if (characteristics.main_activity) {
                            tooltipParts.push(`主要活动: ${characteristics.main_activity}`);
                        }
                        if (characteristics.behavior) {
                            tooltipParts.push(`行为模式: ${characteristics.behavior}`);
                        }
                        if (characteristics.kyc_status) {
                            tooltipParts.push(`KYC状态: ${characteristics.kyc_status}`);
                        }
                        if (characteristics.transaction_status) {
                            tooltipParts.push(`交易状态: ${characteristics.transaction_status}`);
                        }
                        if (characteristics.first_order_completed) {
                            tooltipParts.push(`首单状态: ${characteristics.first_order_completed === '是' ? '已完成' : '未完成'}`);
                        }
                        const tooltipText = tooltipParts.join('\\n');
                        return `<span class="cluster-tag" data-cluster-id="${cid}" title="${tooltipText}" style="position: relative;">
                            <span class="cluster-id">聚类 ${cid}</span>
                            ${characteristics.main_activity ? `<span class="cluster-badge" style="margin-left: 0.5rem; font-size: 0.75rem; opacity: 0.8;">${characteristics.main_activity}</span>` : ''}
                        </span>`;
                    }).join('')}
                </div>
            </div>
            
            <!-- 用户轨迹时间线可视化 -->
            <div class="user-trajectory-timeline">
                <div class="timeline-header">
                    <h4>行为时间线</h4>
                </div>
                <div class="timeline-wrapper" style="display: flex; gap: 1.5rem; align-items: flex-start;">
                    <div class="timeline-container" style="flex: 1;">
                        <canvas id="financialTrajectoryTimeline-${user.user_id}" class="trajectory-timeline-canvas"></canvas>
                        <div id="financialTimelineTooltips-${user.user_id}" class="timeline-tooltips"></div>
                    </div>
                    <div class="intent-summary-panel" id="financialIntentSummary-${user.user_id}" style="width: 280px; min-width: 280px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; position: sticky; top: 1rem;">
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                            <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px;">
                                💭
                            </div>
                            <h4 style="margin: 0; color: var(--text); font-size: 1rem; font-weight: 600;">一句话意图</h4>
                        </div>
                        <div id="financialIntentText-${user.user_id}" style="min-height: 80px; padding: 1rem; background: var(--card); border-radius: 8px; border-left: 4px solid #667eea; color: var(--text); line-height: 1.6; font-size: 0.95rem;">
                            <div style="color: var(--text-secondary); font-style: italic;">将鼠标悬停在时间线节点上查看实时意图</div>
                        </div>
                        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);">
                            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">当前片段信息</div>
                            <div id="financialCurrentSegment-${user.user_id}" style="font-size: 0.9rem; color: var(--text);">
                                <div style="margin-bottom: 0.25rem;">片段: <span style="color: #667eea; font-weight: 600;">-</span></div>
                                <div style="margin-bottom: 0.25rem;">聚类: <span style="color: #667eea; font-weight: 600;">-</span></div>
                                <div>意图强度: <span style="color: #667eea; font-weight: 600;">-</span></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(userCard);
        
        // 渲染用户轨迹时间线
        setTimeout(() => {
            renderFinancialUserTrajectoryTimeline(`financialTrajectoryTimeline-${user.user_id}`, user);
        }, 100 * (index + 1));
    });
}

// 渲染金融用户轨迹时间线（简化版，适配金融场景）
function renderFinancialUserTrajectoryTimeline(canvasId, user) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !user.segments || user.segments.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;
    const width = container ? container.offsetWidth : 800;
    const height = 300;
    
    // 高DPI支持
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.scale(dpr, dpr);
    
    // 聚类颜色映射
    const clusterColors = {
        '0': '#7FE8C1', '1': '#7DA6FF', '2': '#A78BFA', '3': '#F472B6',
        '4': '#60A5FA', '5': '#34D399', '6': '#FBBF24', '7': '#FB7185',
        '8': '#818CF8', '9': '#A78BFA', '10': '#F472B6', '11': '#60A5FA',
        '12': '#34D399', '13': '#FBBF24', '14': '#FB7185', '15': '#818CF8',
        '16': '#7FE8C1', '17': '#7DA6FF'
    };
    
    // 计算时间范围
    const segments = user.segments.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    const startTime = new Date(segments[0].start_time);
    const endTime = new Date(segments[segments.length - 1].end_time);
    const timeRange = endTime - startTime || 1;
    
    const padding = 50;
    const timelineY = height / 2;
    const timelineStartX = padding;
    const timelineWidth = width - padding * 2;
    
    // 绘制时间线
    ctx.strokeStyle = 'rgba(143, 160, 184, 0.4)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(timelineStartX, timelineY);
    ctx.lineTo(timelineStartX + timelineWidth, timelineY);
    ctx.stroke();
    
    // 存储节点位置用于交互
    const nodePositions = [];
    const tooltipContainer = document.getElementById(`financialTimelineTooltips-${user.user_id}`);
    if (tooltipContainer) {
        tooltipContainer.innerHTML = ''; // 清空之前的工具提示
    }
    
    // 绘制片段节点
    segments.forEach((segment, index) => {
        const segmentTime = new Date(segment.start_time);
        const timeRatio = (segmentTime - startTime) / timeRange;
        const x = timelineStartX + timeRatio * timelineWidth;
        
        const clusterColor = clusterColors[segment.cluster_id] || '#8FA0B8';
        
        // 绘制节点
        ctx.beginPath();
        ctx.arc(x, timelineY, 8, 0, Math.PI * 2);
        ctx.fillStyle = clusterColor;
        ctx.fill();
        ctx.strokeStyle = '#ECF2F5';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // 绘制意图强度指示器
        const intentScore = segment.intent_score || 0;
        const intentHeight = intentScore * 40;
        ctx.fillStyle = clusterColor + '60';
        ctx.fillRect(x - 2, timelineY - intentHeight, 4, intentHeight);
        
        // 存储节点信息用于交互
        nodePositions.push({
            x, y: timelineY, segment, index
        });
        
        // 创建详细的片段信息卡片（默认隐藏，悬停时显示）
        if (tooltipContainer) {
            const tooltip = document.createElement('div');
            tooltip.className = 'timeline-segment-tooltip';
            tooltip.id = `financialTooltip-${user.user_id}-${index}`;
            tooltip.style.left = `${x}px`;
            tooltip.style.top = '20px';
            tooltip.style.transform = 'translateX(-50%)';
            tooltip.style.opacity = '0';
            tooltip.style.pointerEvents = 'none';
            
            const duration = (segment.duration_seconds || (segment.duration_minutes * 60) || 0).toFixed(2);
            const segmentLabel = currentLanguage === 'zh' ? '片段' : 'Segment';
            const clusterLabel = currentLanguage === 'zh' ? '聚类' : 'Cluster';
            const startDate = new Date(segment.start_time);
            const locale = currentLanguage === 'zh' ? 'zh-CN' : 'en-US';
            const timeStr = startDate.toLocaleString(locale, { 
                month: 'short', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            // 获取聚类名称和特征（优先使用full_label）
            let clusterName = segment.full_label || segment.cluster_name || '';
            let clusterCharacteristics = {};
            if (window.financialBusinessInsights) {
                const insight = window.financialBusinessInsights.find(i => String(i.cluster_id) === String(segment.cluster_id));
                if (insight) {
                    clusterName = insight.full_label || insight.user_segment_name || insight.cluster_name || '';
                    clusterCharacteristics = insight.key_characteristics || {};
                }
            }
            
            tooltip.innerHTML = `
                <div class="tooltip-header">
                    <span class="tooltip-title">${segmentLabel} ${segment.segment_index || index + 1}</span>
                    <span class="tooltip-time">${timeStr}</span>
                </div>
                <div class="tooltip-cluster" style="background: ${clusterColor}20; border-left: 3px solid ${clusterColor}">
                    <span class="cluster-label">${clusterLabel} ${segment.cluster_id}</span>
                    ${clusterName ? `<span class="cluster-name">${getClusterDisplayName(clusterName)}</span>` : ''}
                </div>
                ${Object.keys(clusterCharacteristics).length > 0 ? `
                <div class="tooltip-characteristics" style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(143, 160, 184, 0.2);">
                    ${clusterCharacteristics.main_activity ? `
                        <div class="tooltip-char-item" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.85rem; color: var(--text-secondary);">主要活动:</span>
                            <span style="font-size: 0.9rem; font-weight: 600; color: #f093fb; padding: 0.25rem 0.5rem; background: rgba(240, 147, 251, 0.1); border-radius: 4px;">${clusterCharacteristics.main_activity}</span>
                        </div>
                    ` : ''}
                    ${clusterCharacteristics.behavior ? `
                        <div class="tooltip-char-item" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.85rem; color: var(--text-secondary);">行为模式:</span>
                            <span style="font-size: 0.9rem; font-weight: 600; color: #667eea; padding: 0.25rem 0.5rem; background: rgba(102, 126, 234, 0.1); border-radius: 4px;">${clusterCharacteristics.behavior}</span>
                        </div>
                    ` : ''}
                    ${clusterCharacteristics.kyc_status ? `
                        <div class="tooltip-char-item" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.85rem; color: var(--text-secondary);">KYC状态:</span>
                            <span style="font-size: 0.9rem; font-weight: 600; color: ${clusterCharacteristics.kyc_status === '已开始' ? '#43e97b' : '#8FA0B8'}; padding: 0.25rem 0.5rem; background: ${clusterCharacteristics.kyc_status === '已开始' ? 'rgba(67, 233, 123, 0.1)' : 'rgba(143, 160, 184, 0.1)'}; border-radius: 4px;">${clusterCharacteristics.kyc_status === '已开始' ? '已验证' : clusterCharacteristics.kyc_status === '未开始' ? '未验证' : clusterCharacteristics.kyc_status}</span>
                        </div>
                    ` : ''}
                    ${clusterCharacteristics.transaction_status ? `
                        <div class="tooltip-char-item" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.85rem; color: var(--text-secondary);">交易状态:</span>
                            <span style="font-size: 0.9rem; font-weight: 600; color: ${clusterCharacteristics.transaction_status === '已完成' ? '#43e97b' : clusterCharacteristics.transaction_status === '进行中' ? '#4facfe' : '#FBBF24'}; padding: 0.25rem 0.5rem; background: ${clusterCharacteristics.transaction_status === '已完成' ? 'rgba(67, 233, 123, 0.1)' : clusterCharacteristics.transaction_status === '进行中' ? 'rgba(79, 172, 254, 0.1)' : 'rgba(251, 191, 36, 0.1)'}; border-radius: 4px;">${clusterCharacteristics.transaction_status}</span>
                        </div>
                    ` : ''}
                    ${clusterCharacteristics.first_order_completed ? `
                        <div class="tooltip-char-item" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.85rem; color: var(--text-secondary);">首单状态:</span>
                            <span style="font-size: 0.9rem; font-weight: 600; color: ${clusterCharacteristics.first_order_completed === '是' ? '#43e97b' : '#8FA0B8'}; padding: 0.25rem 0.5rem; background: ${clusterCharacteristics.first_order_completed === '是' ? 'rgba(67, 233, 123, 0.1)' : 'rgba(143, 160, 184, 0.1)'}; border-radius: 4px;">${clusterCharacteristics.first_order_completed === '是' ? '已完成首单' : '未完成首单'}</span>
                        </div>
                    ` : ''}
                    ${clusterCharacteristics.post_first_order ? `
                        <div class="tooltip-char-item" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.85rem; color: var(--text-secondary);">订单阶段:</span>
                            <span style="font-size: 0.9rem; font-weight: 600; color: ${clusterCharacteristics.post_first_order === '是' ? '#4facfe' : '#8FA0B8'}; padding: 0.25rem 0.5rem; background: ${clusterCharacteristics.post_first_order === '是' ? 'rgba(79, 172, 254, 0.1)' : 'rgba(143, 160, 184, 0.1)'}; border-radius: 4px;">${clusterCharacteristics.post_first_order === '是' ? '首单后活跃' : '首单前/未完成'}</span>
                        </div>
                    ` : ''}
                    ${clusterCharacteristics.urgency ? `
                        <div class="tooltip-char-item" style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 0.85rem; color: var(--text-secondary);">紧迫度:</span>
                            <span style="font-size: 0.9rem; font-weight: 600; color: #43e97b; padding: 0.25rem 0.5rem; background: rgba(67, 233, 123, 0.1); border-radius: 4px;">${clusterCharacteristics.urgency}</span>
                        </div>
                    ` : ''}
                </div>
                ` : ''}
                <div class="tooltip-details" style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(143, 160, 184, 0.2);">
                    <div class="tooltip-detail-item">
                        <span class="tooltip-label">${currentLanguage === 'zh' ? '持续时间' : 'Duration'}:</span>
                        <span class="tooltip-value">${duration} ${currentLanguage === 'zh' ? '秒' : 's'}</span>
                    </div>
                    <div class="tooltip-detail-item">
                        <span class="tooltip-label">${currentLanguage === 'zh' ? '交互次数' : 'Interactions'}:</span>
                        <span class="tooltip-value">${segment.record_count || 0} ${currentLanguage === 'zh' ? '次' : ''}</span>
                    </div>
                    <div class="tooltip-detail-item intent-item">
                        <span class="tooltip-label">${currentLanguage === 'zh' ? '意图强度' : 'Intent Score'}:</span>
                        <div class="intent-progress">
                            <div class="intent-progress-bar" style="width: ${(intentScore * 100).toFixed(0)}%; background: linear-gradient(90deg, ${clusterColor} 0%, ${clusterColor}dd 100%);"></div>
                            <span class="intent-progress-value">${(intentScore * 100).toFixed(0)}%</span>
                        </div>
                    </div>
                </div>
            `;
            tooltipContainer.appendChild(tooltip);
        }
        
        // 绘制时间标签
        if (index === 0 || index === segments.length - 1 || 
            (index % Math.max(1, Math.floor(segments.length / 5)) === 0)) {
            ctx.fillStyle = '#8FA0B8';
            ctx.font = '11px Arial, "Microsoft YaHei", sans-serif';
            ctx.textAlign = 'center';
            const timeStr = segmentTime.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
            ctx.fillText(timeStr, x, timelineY + 25);
        }
    });
    
    // 添加鼠标交互
    let currentHoveredIndex = -1;
    let hideTimeout = null;
    let showTimeout = null;
    let isTooltipVisible = false;
    
    // 生成一句话意图
    const generateIntentSummary = (segment) => {
        let intentText = '';
        const chars = segment.characteristics || {};
        
        // 获取聚类信息
        let clusterName = segment.full_label || segment.cluster_name || '';
        let clusterCharacteristics = {};
        if (window.financialBusinessInsights) {
            const insight = window.financialBusinessInsights.find(i => String(i.cluster_id) === String(segment.cluster_id));
            if (insight) {
                clusterName = insight.full_label || insight.user_segment_name || insight.cluster_name || '';
                clusterCharacteristics = insight.key_characteristics || {};
            }
        }
        
        // 构建一句话意图
        const parts = [];
        
        // 主要活动
        if (segment.main_activity || clusterCharacteristics.main_activity) {
            parts.push(segment.main_activity || clusterCharacteristics.main_activity);
        }
        
        // 行为模式
        if (segment.behavior || clusterCharacteristics.behavior) {
            const behavior = segment.behavior || clusterCharacteristics.behavior;
            if (behavior === '首单后活跃') {
                parts.push('首单后活跃');
            } else if (behavior === '激活阶段') {
                parts.push('激活阶段');
            }
        }
        
        // KYC状态
        if (segment.kyc_status === '已开始' || clusterCharacteristics.kyc_status === '已开始') {
            parts.push('正在完成KYC验证');
        }
        
        // 交易状态
        if (segment.transaction_status || clusterCharacteristics.transaction_status) {
            const status = segment.transaction_status || clusterCharacteristics.transaction_status;
            if (status === '进行中') {
                parts.push('交易进行中');
            } else if (status === '已完成') {
                parts.push('交易已完成');
            }
        }
        
        // 紧迫度
        if (segment.urgency || clusterCharacteristics.urgency) {
            const urgency = segment.urgency || clusterCharacteristics.urgency;
            if (urgency === '高紧迫') {
                parts.push('高紧迫度');
            } else if (urgency === '中紧迫') {
                parts.push('中紧迫度');
            }
        }
        
        // 意图强度
        const intentScore = segment.intent_score || 0;
        if (intentScore > 0.7) {
            parts.push('意图强烈');
        } else if (intentScore < 0.3) {
            parts.push('意图较弱');
        }
        
        // 组合成一句话
        if (parts.length > 0) {
            intentText = `用户当前处于${parts.join('、')}状态`;
        } else if (clusterName) {
            intentText = `用户当前属于${getClusterDisplayName(clusterName)}群体`;
        } else {
            intentText = `用户当前处于聚类${segment.cluster_id}，意图强度${(intentScore * 100).toFixed(0)}%`;
        }
        
        return intentText;
    };
    
    // 更新一句话意图显示
    const updateIntentSummary = (segment, segmentIndex) => {
        const intentTextEl = document.getElementById(`financialIntentText-${user.user_id}`);
        const currentSegmentEl = document.getElementById(`financialCurrentSegment-${user.user_id}`);
        
        if (intentTextEl) {
            const intentText = generateIntentSummary(segment);
            intentTextEl.innerHTML = `<div style="color: var(--text); line-height: 1.6;">${intentText}</div>`;
        }
        
        if (currentSegmentEl) {
            const intentScore = segment.intent_score || 0;
            currentSegmentEl.innerHTML = `
                <div style="margin-bottom: 0.25rem;">片段: <span style="color: #667eea; font-weight: 600;">${segment.segment_index !== undefined ? segment.segment_index : segmentIndex + 1}</span></div>
                <div style="margin-bottom: 0.25rem;">聚类: <span style="color: #667eea; font-weight: 600;">${segment.cluster_id}</span></div>
                <div>意图强度: <span style="color: #667eea; font-weight: 600;">${(intentScore * 100).toFixed(0)}%</span></div>
            `;
        }
    };
    
    const showTooltip = (nodeIndex) => {
        if (hideTimeout) {
            clearTimeout(hideTimeout);
            hideTimeout = null;
        }
        
        if (currentHoveredIndex === nodeIndex && isTooltipVisible) {
            return; // 已经显示，不需要重复操作
        }
        
        // 清除之前的显示延迟
        if (showTimeout) {
            clearTimeout(showTimeout);
        }
        
        showTimeout = setTimeout(() => {
            // 隐藏所有工具提示
            if (tooltipContainer) {
                tooltipContainer.querySelectorAll('.timeline-segment-tooltip').forEach(t => {
                    t.style.opacity = '0';
                    t.style.pointerEvents = 'none';
                });
            }
            
            // 显示当前工具提示
            const tooltip = document.getElementById(`financialTooltip-${user.user_id}-${nodeIndex}`);
            const node = nodePositions.find(n => n.index === nodeIndex);
            
            if (tooltip && node) {
                // 更新一句话意图
                updateIntentSummary(node.segment, nodeIndex);
                
                // 先设置位置，再显示（避免闪烁）
                tooltip.style.left = `${node.x}px`;
                tooltip.style.top = '20px';
                tooltip.style.display = 'block'; // 确保元素可见
                
                // 调整位置，确保不超出容器
                requestAnimationFrame(() => {
                    const tooltipRect = tooltip.getBoundingClientRect();
                    const containerRect = tooltipContainer.getBoundingClientRect();
                    const canvasRect = canvas.getBoundingClientRect();
                    
                    let transformX = '-50%';
                    let offsetY = 0;
                    
                    // 水平位置调整
                    if (tooltipRect.right > containerRect.right) {
                        transformX = 'calc(-100% + 50%)';
                    } else if (tooltipRect.left < containerRect.left) {
                        transformX = '0';
                    }
                    
                    // 垂直位置调整（如果工具提示超出画布，显示在下方）
                    if (tooltipRect.bottom > canvasRect.bottom) {
                        offsetY = 150;
                    }
                    
                    tooltip.style.transform = `translateX(${transformX}) translateY(${offsetY}px)`;
                    tooltip.style.opacity = '1';
                    tooltip.style.pointerEvents = 'auto';
                });
            }
            currentHoveredIndex = nodeIndex;
            isTooltipVisible = true;
            showTimeout = null;
        }, 100); // 100ms延迟显示，减少频繁切换
    };
    
    const hideTooltip = (immediate = false) => {
        if (showTimeout) {
            clearTimeout(showTimeout);
            showTimeout = null;
        }
        
        if (immediate) {
            if (tooltipContainer) {
                tooltipContainer.querySelectorAll('.timeline-segment-tooltip').forEach(t => {
                    t.style.opacity = '0';
                    t.style.pointerEvents = 'none';
                });
            }
            // 恢复默认显示（显示最后一个片段）
            if (segments.length > 0) {
                const lastSegment = segments[segments.length - 1];
                updateIntentSummary(lastSegment, segments.length - 1);
            }
            currentHoveredIndex = -1;
            isTooltipVisible = false;
        } else {
            // 延迟隐藏，给用户时间移动到工具提示上
            hideTimeout = setTimeout(() => {
                if (tooltipContainer) {
                    tooltipContainer.querySelectorAll('.timeline-segment-tooltip').forEach(t => {
                        t.style.opacity = '0';
                        t.style.pointerEvents = 'none';
                    });
                }
                // 恢复默认显示（显示最后一个片段）
                if (segments.length > 0) {
                    const lastSegment = segments[segments.length - 1];
                    updateIntentSummary(lastSegment, segments.length - 1);
                }
                currentHoveredIndex = -1;
                isTooltipVisible = false;
                hideTimeout = null;
            }, 200); // 200ms延迟隐藏
        }
    };
    
    // 初始化：显示最后一个片段的一句话意图
    if (segments.length > 0) {
        const lastSegment = segments[segments.length - 1];
        updateIntentSummary(lastSegment, segments.length - 1);
    }
    
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left) * (canvas.width / dpr / rect.width);
        const mouseY = (e.clientY - rect.top) * (canvas.height / dpr / rect.height);
        
        let hoveredNode = null;
        nodePositions.forEach(node => {
            // 检查是否在节点附近
            const dist = Math.sqrt(Math.pow(mouseX - node.x, 2) + Math.pow(mouseY - node.y, 2));
            if (dist < 20) {
                hoveredNode = node;
            }
        });
        
        if (hoveredNode) {
            canvas.style.cursor = 'pointer';
            showTooltip(hoveredNode.index);
        } else {
            canvas.style.cursor = 'default';
            hideTooltip();
        }
    });
    
    // 在工具提示容器上添加鼠标事件，保持工具提示显示
    if (tooltipContainer) {
        tooltipContainer.addEventListener('mousemove', (e) => {
            if (isTooltipVisible && currentHoveredIndex !== -1) {
                // 如果鼠标在工具提示上，保持显示
                if (hideTimeout) {
                    clearTimeout(hideTimeout);
                    hideTimeout = null;
                }
            }
        });
        
        tooltipContainer.addEventListener('mouseleave', () => {
            hideTooltip();
        });
    }
    
    canvas.addEventListener('mouseleave', () => {
        canvas.style.cursor = 'default';
        hideTooltip();
    });
    
    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left) * (canvas.width / dpr / rect.width);
        const mouseY = (e.clientY - rect.top) * (canvas.height / dpr / rect.height);
        
        nodePositions.forEach(node => {
            const dist = Math.sqrt(Math.pow(mouseX - node.x, 2) + Math.pow(mouseY - node.y, 2));
            if (dist < 20) {
                // 切换工具提示显示/隐藏
                const tooltip = document.getElementById(`financialTooltip-${user.user_id}-${node.index}`);
                if (tooltip) {
                    if (isTooltipVisible && currentHoveredIndex === node.index) {
                        hideTooltip(true);
                    } else {
                        showTooltip(node.index);
                    }
                }
            }
        });
    });
}

// 优化画像卡片事件
function initPortraitCardEvents(container) {
    container.addEventListener('mouseenter', throttle((e) => {
        const card = e.target.closest('.portrait-card');
        if (card) {
            card.style.transform = 'translateY(-4px)';
            card.style.boxShadow = '0 8px 24px rgba(0,0,0,0.15)';
        }
    }, 50), true);
    
    container.addEventListener('mouseleave', throttle((e) => {
        const card = e.target.closest('.portrait-card');
        if (card) {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = 'none';
        }
    }, 50), true);
}

// 加载金融聚类详情
function loadFinancialClusters() {
    if (!window.financialBusinessInsights || window.financialBusinessInsights.length === 0) {
        const container = document.getElementById('financialClusterDetails');
        if (container) {
            container.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);"><p>暂无聚类数据</p></div>';
        }
        return;
    }
    
    const select = document.getElementById('financialClusterSelect');
    if (select) {
        select.innerHTML = '<option value="">-- 选择聚类 --</option>';
        window.financialBusinessInsights.forEach(insight => {
            const option = document.createElement('option');
            option.value = insight.cluster_id;
            const displayName = insight.full_label || insight.user_segment_name || insight.cluster_name || '';
            option.textContent = `聚类 ${insight.cluster_id}: ${removeEmojiFromClusterName(displayName)}`;
            select.appendChild(option);
        });
        
        // 自动选择并显示第一个聚类
        if (window.financialBusinessInsights.length > 0) {
            const firstClusterId = window.financialBusinessInsights[0].cluster_id;
            select.value = firstClusterId;
            showFinancialClusterDetails(firstClusterId);
        }
    }
}

// 显示金融聚类详情
function showFinancialClusterDetails(clusterId) {
    if (!clusterId || !window.financialBusinessInsights) {
        console.warn('showFinancialClusterDetails: 缺少参数或数据', { clusterId, hasData: !!window.financialBusinessInsights });
        return;
    }
    
    // 确保clusterId是字符串类型进行匹配
    const insight = window.financialBusinessInsights.find(i => String(i.cluster_id) === String(clusterId));
    if (!insight) {
        console.warn('showFinancialClusterDetails: 未找到对应的聚类', { clusterId, availableIds: window.financialBusinessInsights.map(i => i.cluster_id) });
        const container = document.getElementById('financialClusterDetails');
        if (container) {
            container.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);"><p>未找到对应的聚类数据</p></div>';
        }
        return;
    }
    
    const container = document.getElementById('financialClusterDetails');
    if (!container) return;
    
    const chars = insight.key_characteristics || {};
    
    // 调试信息
    console.log('显示聚类详情:', {
        clusterId,
        insight: insight,
        hasMarketingStrategy: !!insight.marketing_strategy,
        marketingStrategyLength: insight.marketing_strategy?.length || 0,
        hasProductRecommendation: !!insight.product_recommendation,
        hasConversionTactics: !!insight.conversion_tactics,
        containerExists: !!container
    });
    
    // 确保容器可见
    if (container) {
        container.style.display = 'block';
        container.style.visibility = 'visible';
        container.style.opacity = '1';
    }
    
    // 确定状态颜色
    let statusColor = '#667eea';
    let statusBg = 'rgba(102, 126, 234, 0.1)';
    if (chars.transaction_status === '已完成') {
        statusColor = '#43e97b';
        statusBg = 'rgba(67, 233, 123, 0.1)';
    } else if (chars.transaction_status === '进行中') {
        statusColor = '#4facfe';
        statusBg = 'rgba(79, 172, 254, 0.1)';
    } else if (chars.transaction_status === '未开始') {
        statusColor = '#FBBF24';
        statusBg = 'rgba(251, 191, 36, 0.1)';
    }
    
    // 准备策略内容（确保数组存在且不为空）
    // 注意：字段名可能不同，需要兼容多种命名方式
    const marketingStrategy = Array.isArray(insight.marketing_strategy) ? insight.marketing_strategy : [];
    const productRecommendations = Array.isArray(insight.product_recommendation) ? insight.product_recommendation : 
                                  Array.isArray(insight.product_recommendations) ? insight.product_recommendations : [];
    const conversionOptimization = Array.isArray(insight.conversion_tactics) ? insight.conversion_tactics : 
                                   Array.isArray(insight.conversion_optimization) ? insight.conversion_optimization : [];
    const contentStrategy = Array.isArray(insight.content_strategy) ? insight.content_strategy : [];
    const campaignDifferentiation = Array.isArray(insight.campaign_differentiation) ? insight.campaign_differentiation : [];
    
    container.innerHTML = `
        <div style="background: var(--card); padding: 2rem; border-radius: 16px; border: 1px solid var(--border);">
            <!-- 头部 -->
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 2px solid var(--border);">
                <div style="width: 64px; height: 64px; background: ${statusBg}; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 32px; border: 3px solid ${statusColor};">
                    ${chars.transaction_status === '已完成' ? '✅' : chars.transaction_status === '进行中' ? '🔄' : '⏳'}
                </div>
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 0.5rem 0; color: var(--text); font-size: 1.5rem;">${insight.full_label || insight.user_segment_name || insight.cluster_name || `用户群体 ${clusterId}`}</h3>
                    <p style="margin: 0; color: var(--text-secondary);">${chars.user_count || 0} 位用户 · ${chars.segment_count || 0} 个行为片段${chars.main_activity ? ' · ' + chars.main_activity : ''}</p>
                </div>
            </div>
            
            <!-- 关键指标 -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                <div style="padding: 1.5rem; background: rgba(102, 126, 234, 0.1); border-radius: 12px; border-left: 4px solid #667eea;">
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">用户数</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #667eea;">${chars.user_count || 0}</div>
                </div>
                <div style="padding: 1.5rem; background: rgba(79, 172, 254, 0.1); border-radius: 12px; border-left: 4px solid #4facfe;">
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">行为片段</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #4facfe;">${chars.segment_count || 0}</div>
                </div>
                <div style="padding: 1.5rem; background: rgba(240, 147, 251, 0.1); border-radius: 12px; border-left: 4px solid #f093fb;">
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">意图强度</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #f093fb;">${((chars.avg_intent_score || 0) * 100).toFixed(0)}%</div>
                </div>
            </div>
            
            <!-- 用户特征 -->
            <div style="margin-bottom: 2rem;">
                <h4 style="margin: 0 0 1rem 0; color: var(--text); font-size: 1.1rem;">用户特征</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                    ${chars.transaction_status ? `
                        <div style="padding: 1rem; background: ${statusBg}; border-radius: 8px; border: 1px solid ${statusColor}40;">
                            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">交易状态</div>
                            <div style="font-size: 1.1rem; font-weight: 600; color: ${statusColor};">${chars.transaction_status}</div>
                        </div>
                    ` : ''}
                    ${chars.kyc_status ? `
                        <div style="padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 8px; border: 1px solid rgba(102, 126, 234, 0.3);">
                            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">身份验证</div>
                            <div style="font-size: 1.1rem; font-weight: 600; color: #667eea;">${chars.kyc_status === '已开始' ? '已验证' : chars.kyc_status === '未开始' ? '未验证' : chars.kyc_status}</div>
                        </div>
                    ` : ''}
                    ${chars.main_activity ? `
                        <div style="padding: 1rem; background: rgba(240, 147, 251, 0.1); border-radius: 8px; border: 1px solid rgba(240, 147, 251, 0.3);">
                            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">主要行为</div>
                            <div style="font-size: 1.1rem; font-weight: 600; color: #f093fb;">${chars.main_activity}</div>
                        </div>
                    ` : ''}
                    ${chars.behavior ? `
                        <div style="padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 8px; border: 1px solid rgba(102, 126, 234, 0.3);">
                            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">行为模式</div>
                            <div style="font-size: 1.1rem; font-weight: 600; color: #667eea;">${chars.behavior}</div>
                        </div>
                    ` : ''}
                    ${chars.first_order_completed ? `
                        <div style="padding: 1rem; background: rgba(67, 233, 123, 0.1); border-radius: 8px; border: 1px solid rgba(67, 233, 123, 0.3);">
                            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">首单状态</div>
                            <div style="font-size: 1.1rem; font-weight: 600; color: #43e97b;">${chars.first_order_completed === '是' ? '已完成首单' : '未完成首单'}</div>
                        </div>
                    ` : ''}
                    ${chars.post_first_order ? `
                        <div style="padding: 1rem; background: rgba(79, 172, 254, 0.1); border-radius: 8px; border: 1px solid rgba(79, 172, 254, 0.3);">
                            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">订单阶段</div>
                            <div style="font-size: 1.1rem; font-weight: 600; color: #4facfe;">${chars.post_first_order === '是' ? '首单后活跃' : '首单前/未完成'}</div>
                        </div>
                    ` : ''}
                    ${chars.urgency ? `
                        <div style="padding: 1rem; background: rgba(67, 233, 123, 0.1); border-radius: 8px; border: 1px solid rgba(67, 233, 123, 0.3);">
                            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">紧迫度</div>
                            <div style="font-size: 1.1rem; font-weight: 600; color: #43e97b;">${chars.urgency}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
            
            <!-- 运营策略 - 可视化卡片布局 -->
            ${marketingStrategy.length > 0 ? `
                <div style="margin-bottom: 2rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                            💡
                        </div>
                        <h4 style="margin: 0; color: var(--text); font-size: 1.3rem; font-weight: 700;">运营策略建议</h4>
                        <span style="padding: 0.25rem 0.75rem; background: rgba(102, 126, 234, 0.1); color: #667eea; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">${marketingStrategy.length} 项策略</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                        ${marketingStrategy.map((strategy, idx) => {
                            const strategyText = String(strategy);
                            const hasCategory = strategyText.includes('【') && strategyText.includes('】');
                            const category = hasCategory ? strategyText.match(/【(.*?)】/)?.[1] : '';
                            const content = hasCategory ? strategyText.replace(/【.*?】/g, '').trim() : strategyText;
                            const isFirstInCategory = idx === 0 || !marketingStrategy[idx - 1].includes(category);
                            
                            return `
                                <div style="padding: 1.25rem; background: var(--card); border: 1px solid var(--border); border-radius: 12px; transition: all 0.3s ease; position: relative; overflow: hidden;" 
                                     onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(102, 126, 234, 0.15)';" 
                                     onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                                    ${hasCategory && isFirstInCategory ? `
                                        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);"></div>
                                        <div style="margin-bottom: 0.75rem;">
                                            <span style="display: inline-block; padding: 0.35rem 0.75rem; background: rgba(102, 126, 234, 0.1); color: #667eea; border-radius: 6px; font-size: 0.85rem; font-weight: 600;">${category}</span>
                                        </div>
                                    ` : ''}
                                    <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                                        <div style="width: 6px; height: 6px; background: #667eea; border-radius: 50%; margin-top: 0.5rem; flex-shrink: 0;"></div>
                                        <p style="margin: 0; color: var(--text); line-height: 1.7; font-size: 0.95rem;">${content}</p>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            ` : '<div style="margin-bottom: 2rem; padding: 2rem; background: rgba(143, 160, 184, 0.05); border-radius: 12px; border: 1px dashed var(--border); text-align: center;"><p style="margin: 0; color: var(--text-secondary);">暂无运营策略数据</p></div>'}
            
            <!-- 产品推荐 - 可视化卡片布局 -->
            ${productRecommendations.length > 0 ? `
                <div style="margin-bottom: 2rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                            🎯
                        </div>
                        <h4 style="margin: 0; color: var(--text); font-size: 1.3rem; font-weight: 700;">产品/服务推荐</h4>
                        <span style="padding: 0.25rem 0.75rem; background: rgba(79, 172, 254, 0.1); color: #4facfe; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">${productRecommendations.length} 项推荐</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                        ${productRecommendations.map((rec, idx) => {
                            const recText = String(rec);
                            const hasCategory = recText.includes('【') && recText.includes('】');
                            const category = hasCategory ? recText.match(/【(.*?)】/)?.[1] : '';
                            const content = hasCategory ? recText.replace(/【.*?】/g, '').trim() : recText;
                            const isFirstInCategory = idx === 0 || !productRecommendations[idx - 1].includes(category);
                            
                            return `
                                <div style="padding: 1.25rem; background: var(--card); border: 1px solid var(--border); border-radius: 12px; transition: all 0.3s ease; position: relative; overflow: hidden;" 
                                     onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(79, 172, 254, 0.15)';" 
                                     onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                                    ${hasCategory && isFirstInCategory ? `
                                        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);"></div>
                                        <div style="margin-bottom: 0.75rem;">
                                            <span style="display: inline-block; padding: 0.35rem 0.75rem; background: rgba(79, 172, 254, 0.1); color: #4facfe; border-radius: 6px; font-size: 0.85rem; font-weight: 600;">${category}</span>
                                        </div>
                                    ` : ''}
                                    <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                                        <div style="width: 6px; height: 6px; background: #4facfe; border-radius: 50%; margin-top: 0.5rem; flex-shrink: 0;"></div>
                                        <p style="margin: 0; color: var(--text); line-height: 1.7; font-size: 0.95rem;">${content}</p>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            ` : ''}
            
            <!-- 转化优化 - 可视化卡片布局 -->
            ${conversionOptimization.length > 0 ? `
                <div style="margin-bottom: 2rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                            ⚡
                        </div>
                        <h4 style="margin: 0; color: var(--text); font-size: 1.3rem; font-weight: 700;">转化优化建议</h4>
                        <span style="padding: 0.25rem 0.75rem; background: rgba(67, 233, 123, 0.1); color: #43e97b; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">${conversionOptimization.length} 项建议</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                        ${conversionOptimization.map((opt, idx) => {
                            const optText = String(opt);
                            const hasCategory = optText.includes('【') && optText.includes('】');
                            const category = hasCategory ? optText.match(/【(.*?)】/)?.[1] : '';
                            const content = hasCategory ? optText.replace(/【.*?】/g, '').trim() : optText;
                            const isFirstInCategory = idx === 0 || !conversionOptimization[idx - 1].includes(category);
                            
                            return `
                                <div style="padding: 1.25rem; background: var(--card); border: 1px solid var(--border); border-radius: 12px; transition: all 0.3s ease; position: relative; overflow: hidden;" 
                                     onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(67, 233, 123, 0.15)';" 
                                     onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                                    ${hasCategory && isFirstInCategory ? `
                                        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%);"></div>
                                        <div style="margin-bottom: 0.75rem;">
                                            <span style="display: inline-block; padding: 0.35rem 0.75rem; background: rgba(67, 233, 123, 0.1); color: #43e97b; border-radius: 6px; font-size: 0.85rem; font-weight: 600;">${category}</span>
                                        </div>
                                    ` : ''}
                                    <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                                        <div style="width: 6px; height: 6px; background: #43e97b; border-radius: 50%; margin-top: 0.5rem; flex-shrink: 0;"></div>
                                        <p style="margin: 0; color: var(--text); line-height: 1.7; font-size: 0.95rem;">${content}</p>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            ` : ''}
            
            <!-- 内容策略 - 可视化卡片布局 -->
            ${contentStrategy.length > 0 ? `
                <div style="margin-bottom: 2rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #f093fb 0%, #fbbf24 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                            📝
                        </div>
                        <h4 style="margin: 0; color: var(--text); font-size: 1.3rem; font-weight: 700;">内容策略</h4>
                        <span style="padding: 0.25rem 0.75rem; background: rgba(240, 147, 251, 0.1); color: #f093fb; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">${contentStrategy.length} 项策略</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                        ${contentStrategy.map((strategy, idx) => {
                            const strategyText = String(strategy);
                            return `
                                <div style="padding: 1.25rem; background: var(--card); border: 1px solid var(--border); border-radius: 12px; transition: all 0.3s ease; position: relative; overflow: hidden;" 
                                     onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(240, 147, 251, 0.15)';" 
                                     onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #f093fb 0%, #fbbf24 100%);"></div>
                                    <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                                        <div style="width: 6px; height: 6px; background: #f093fb; border-radius: 50%; margin-top: 0.5rem; flex-shrink: 0;"></div>
                                        <p style="margin: 0; color: var(--text); line-height: 1.7; font-size: 0.95rem;">${strategyText}</p>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            ` : ''}
            
            <!-- 活动差异化 - 可视化卡片布局 -->
            ${campaignDifferentiation.length > 0 ? `
                <div style="margin-bottom: 0;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #fbbf24 0%, #fb7185 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                            🎪
                        </div>
                        <h4 style="margin: 0; color: var(--text); font-size: 1.3rem; font-weight: 700;">活动差异化建议</h4>
                        <span style="padding: 0.25rem 0.75rem; background: rgba(251, 191, 36, 0.1); color: #fbbf24; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">${campaignDifferentiation.length} 项活动</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                        ${campaignDifferentiation.map((campaign, idx) => {
                            const campaignText = String(campaign);
                            const hasCategory = campaignText.includes('【') && campaignText.includes('】');
                            const category = hasCategory ? campaignText.match(/【(.*?)】/)?.[1] : '';
                            const content = hasCategory ? campaignText.replace(/【.*?】/g, '').trim() : campaignText;
                            const isFirstInCategory = idx === 0 || !campaignDifferentiation[idx - 1].includes(category);
                            
                            return `
                                <div style="padding: 1.25rem; background: var(--card); border: 1px solid var(--border); border-radius: 12px; transition: all 0.3s ease; position: relative; overflow: hidden;" 
                                     onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(251, 191, 36, 0.15)';" 
                                     onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                                    ${hasCategory && isFirstInCategory ? `
                                        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #fbbf24 0%, #fb7185 100%);"></div>
                                        <div style="margin-bottom: 0.75rem;">
                                            <span style="display: inline-block; padding: 0.35rem 0.75rem; background: rgba(251, 191, 36, 0.1); color: #fbbf24; border-radius: 6px; font-size: 0.85rem; font-weight: 600;">${category}</span>
                                        </div>
                                    ` : ''}
                                    <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                                        <div style="width: 6px; height: 6px; background: #fbbf24; border-radius: 50%; margin-top: 0.5rem; flex-shrink: 0;"></div>
                                        <p style="margin: 0; color: var(--text); line-height: 1.7; font-size: 0.95rem;">${content}</p>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

// 切换子标签页
function switchSubTab(subTabName) {
    // 获取当前激活的主标签页
    const activeMainTab = document.querySelector('.tab-content.active');
    const mainTabId = activeMainTab ? activeMainTab.id : '';
    
    // 更新按钮状态（只更新当前主标签页下的子标签按钮）
    if (activeMainTab) {
        activeMainTab.querySelectorAll('.sub-tab-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-sub-tab') === subTabName) {
                btn.classList.add('active');
            }
        });
    }
    
    // 更新内容显示（只更新当前主标签页下的子标签内容）
    if (activeMainTab) {
        activeMainTab.querySelectorAll('.sub-tab-content').forEach(content => {
            content.classList.remove('active');
        });
    }
    
    const targetContent = document.getElementById(`subTab-${subTabName}`);
    if (targetContent) {
        targetContent.classList.add('active');
    }
    
    // 根据子标签页加载相应内容
    if (subTabName === 'path') {
        loadJourney();
    } else if (subTabName === 'trajectory') {
        loadUserTrajectories();
    } else if (subTabName === 'cluster') {
        loadClusters();
    } else if (subTabName === 'portrait') {
        loadPortraits();
    }
}

// 用户轨迹可视化
function loadUserTrajectories() {
    if (typeof userTrajectories === 'undefined' || userTrajectories.length === 0) {
        console.error('userTrajectories 数据未加载');
        const container = document.getElementById('userTrajectories');
        if (container) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>暂无用户轨迹数据</p></div>';
        }
        return;
    }
    
    // 过滤掉用户ID为空的用户
    const validUsers = userTrajectories.filter(user => user.user_id && user.user_id.trim() !== '');
    
    if (validUsers.length === 0) {
        const container = document.getElementById('userTrajectories');
        if (container) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>暂无有效用户轨迹数据</p></div>';
        }
        return;
    }
    
    // 加载聚类筛选选项
    if (typeof businessInsights !== 'undefined') {
        const clusterFilter = document.getElementById('clusterFilter');
        if (clusterFilter) {
            // 清空现有选项（除了"所有聚类"）
            clusterFilter.innerHTML = '<option value="">所有聚类</option>';
            businessInsights.forEach(insight => {
                const option = document.createElement('option');
                option.value = insight.cluster_id;
                option.textContent = `聚类 ${insight.cluster_id}: ${removeEmojiFromClusterName(insight.user_segment_name)}`;
                clusterFilter.appendChild(option);
            });
        }
    }
    
    // 渲染用户列表（只渲染有效用户）
    renderUserTrajectories(validUsers);
    
    // 绑定搜索和筛选事件
    const searchInput = document.getElementById('userSearch');
    const clusterFilter = document.getElementById('clusterFilter');
    const sortOption = document.getElementById('sortOption');
    
    if (searchInput) {
        searchInput.removeEventListener('input', filterAndRender);
        searchInput.addEventListener('input', () => filterAndRender());
    }
    if (clusterFilter) {
        clusterFilter.removeEventListener('change', filterAndRender);
        clusterFilter.addEventListener('change', () => filterAndRender());
    }
    if (sortOption) {
        sortOption.removeEventListener('change', filterAndRender);
        sortOption.addEventListener('change', () => filterAndRender());
    }
}

// 筛选和渲染用户轨迹
function filterAndRender() {
    if (typeof userTrajectories === 'undefined') return;
    
    let filtered = [...userTrajectories];
    
    // 过滤掉用户ID为空的用户
    filtered = filtered.filter(user => user.user_id && user.user_id.trim() !== '');
    
    // 搜索筛选
    const searchTerm = document.getElementById('userSearch')?.value.toLowerCase() || '';
    if (searchTerm) {
        filtered = filtered.filter(user => 
            user.user_id.toLowerCase().includes(searchTerm)
        );
    }
    
    // 聚类筛选
    const clusterFilter = document.getElementById('clusterFilter')?.value || '';
    if (clusterFilter) {
        filtered = filtered.filter(user => 
            user.cluster_ids.includes(clusterFilter)
        );
    }
    
    // 排序
    const sortOption = document.getElementById('sortOption')?.value || 'time';
    if (sortOption === 'segments') {
        filtered.sort((a, b) => b.segment_count - a.segment_count);
    } else if (sortOption === 'clusters') {
        filtered.sort((a, b) => b.unique_clusters - a.unique_clusters);
    } else {
        // 按时间排序（第一个片段的时间）
        filtered.sort((a, b) => {
            if (a.segments.length === 0 || b.segments.length === 0) return 0;
            return a.segments[0].start_time.localeCompare(b.segments[0].start_time);
        });
    }
    
    renderUserTrajectories(filtered);
}

// 渲染用户轨迹列表
function renderUserTrajectories(users) {
    const container = document.getElementById('userTrajectories');
    if (!container) return;
    
    if (users.length === 0) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>没有找到匹配的用户</p></div>';
        return;
    }
    
    container.innerHTML = '';
    
    users.forEach((user, index) => {
        const userCard = document.createElement('div');
        userCard.className = 'user-trajectory-card';
        userCard.style.animationDelay = `${index * 0.05}s`;
        
        // 获取聚类名称映射
        const clusterNames = {};
        if (typeof businessInsights !== 'undefined') {
            businessInsights.forEach(insight => {
                clusterNames[insight.cluster_id] = removeEmojiFromClusterName(insight.user_segment_name);
            });
        }
        
        // 分析用户卡点
        const stuckPoint = analyzeUserStuckPoint(user);
        
        // 计算用户行为统计
        const segments = user.segments || [];
        const stageCounts = segments.reduce((acc, seg) => {
            const stage = seg.purchase_stage || '浏览阶段';
            acc[stage] = (acc[stage] || 0) + 1;
            return acc;
        }, {});
        
        const avgIntentScore = segments.length > 0 
            ? segments.reduce((sum, s) => sum + (s.intent_score || 0), 0) / segments.length 
            : 0;
        
        // 计算阶段转换
        const stageTransitions = [];
        for (let i = 0; i < segments.length - 1; i++) {
            const from = segments[i].purchase_stage || '浏览阶段';
            const to = segments[i + 1].purchase_stage || '浏览阶段';
            if (from !== to) {
                stageTransitions.push({ from, to });
            }
        }
        
        userCard.innerHTML = `
            <div class="user-header">
                <div class="user-id-section">
                    <h3 class="user-id">${user.user_id}</h3>
                    <div class="user-stats">
                        <span class="stat-badge">
                            <strong>${user.segment_count}</strong> 个片段
                        </span>
                        <span class="stat-badge">
                            <strong>${user.unique_clusters}</strong> 个聚类
                        </span>
                        <span class="stat-badge">
                            <strong>${user.total_duration.toFixed(1)}</strong> 秒
                        </span>
                        <span class="stat-badge">
                            <strong>${user.total_records}</strong> 次交互
                        </span>
                        <span class="stat-badge intent-badge">
                            <strong>${(avgIntentScore * 100).toFixed(0)}%</strong> 平均意图强度
                        </span>
                    </div>
                </div>
                <div class="user-clusters-summary">
                    <strong>聚类分布:</strong>
                    ${user.cluster_ids.map(cid => {
                        const name = clusterNames[cid] || `聚类${cid}`;
                        return `<span class="cluster-tag" data-cluster-id="${cid}">聚类 ${cid}</span>`;
                    }).join('')}
                </div>
            </div>
            
            <!-- 用户行为概览卡片 -->
            <div class="user-overview-cards">
                <div class="overview-card stage-overview">
                    <div class="overview-header">
                        <span class="overview-icon">📊</span>
                        <span class="overview-title">${t('trajectory.stageDistribution')}</span>
                    </div>
                    <div class="stage-bars">
                        ${['浏览阶段', '对比阶段', '决策阶段'].map(stage => {
                            const stageTranslations = {
                                '浏览阶段': t('stages.browsing'),
                                '对比阶段': t('stages.comparison'),
                                '决策阶段': t('stages.decision')
                            };
                            const displayStage = stageTranslations[stage] || stage;
                            const count = stageCounts[stage] || 0;
                            const percentage = segments.length > 0 ? (count / segments.length * 100).toFixed(0) : 0;
                            const stageColors = {
                                '浏览阶段': '#60A5FA',
                                '对比阶段': '#FBBF24',
                                '决策阶段': '#7FE8C1'
                    };
                    return `
                                <div class="stage-bar-item">
                                    <div class="stage-bar-label">
                                        <span>${displayStage}</span>
                                        <span class="stage-bar-value">${count} (${percentage}%)</span>
                            </div>
                                    <div class="stage-bar-container">
                                        <div class="stage-bar-fill" style="width: ${percentage}%; background: ${stageColors[stage]}"></div>
                                    </div>
                                    </div>
                            `;
                        }).join('')}
                                </div>
                                    </div>
                
                <div class="overview-card path-overview">
                    <div class="overview-header">
                        <span class="overview-icon">🔄</span>
                        <span class="overview-title">${t('trajectory.conversionPath')}</span>
                                    </div>
                    <div class="path-visualization">
                        <canvas id="pathCanvas-${user.user_id}" class="path-canvas"></canvas>
                                    </div>
                                    </div>
                
                ${stuckPoint ? `
                <div class="overview-card stuck-point-card" style="border-left: 4px solid ${stuckPoint.color}">
                    <div class="overview-header">
                        <span class="overview-icon" style="color: ${stuckPoint.color}">⚠️</span>
                        <span class="overview-title">${currentLanguage === 'zh' ? '卡点分析' : 'Stuck Point Analysis'}</span>
                                </div>
                    <p class="stuck-point-message" style="color: ${stuckPoint.color}">${stuckPoint.message}</p>
                            </div>
                ` : ''}
                        </div>
            
            <!-- 用户轨迹时间线可视化（包含片段信息） -->
            <div class="user-trajectory-timeline">
                <div class="timeline-header">
                    <h4>${currentLanguage === 'zh' ? '行为时间线' : 'Behavior Timeline'}</h4>
                    <div class="timeline-legend">
                        <span class="legend-item">
                            <span class="legend-dot" style="background: #60A5FA"></span>
                            <span>${t('stages.browsing')}</span>
                        </span>
                        <span class="legend-item">
                            <span class="legend-dot" style="background: #FBBF24"></span>
                            <span>${t('stages.comparison')}</span>
                        </span>
                        <span class="legend-item">
                            <span class="legend-dot" style="background: #7FE8C1"></span>
                            <span>${t('stages.decision')}</span>
                        </span>
                    </div>
                </div>
                <div class="timeline-container">
                    <canvas id="trajectoryTimeline-${user.user_id}" class="trajectory-timeline-canvas"></canvas>
                    <div id="timelineTooltips-${user.user_id}" class="timeline-tooltips"></div>
                </div>
            </div>
        `;
        
        container.appendChild(userCard);
        
        // 渲染用户轨迹时间线和路径图
        setTimeout(() => {
            renderUserTrajectoryTimeline(`trajectoryTimeline-${user.user_id}`, user);
            renderUserPathVisualization(`pathCanvas-${user.user_id}`, user);
        }, 100 * (index + 1));
    });
    
    // 绑定聚类标签点击事件
    container.querySelectorAll('.cluster-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const clusterId = this.getAttribute('data-cluster-id');
            showTab('journey');
            setTimeout(() => {
                switchSubTab('cluster');
                setTimeout(() => {
                    const select = document.getElementById('clusterSelect');
                    if (select) {
                        select.value = clusterId;
                        showClusterDetails(clusterId);
                    }
                }, 100);
            }, 300);
        });
    });
}

// 初始化转化路径交互
function initJourneyInteractions() {
    // 卡片悬停效果
    document.querySelectorAll('.cluster-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // 点击卡片跳转到聚类详情（排除按钮及其子元素）
    document.querySelectorAll('.cluster-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // 如果点击的是按钮或其子元素，不触发卡片点击
            if (e.target.closest('.btn-view-details')) {
                return;
            }
            const clusterId = this.getAttribute('data-cluster-id');
            handleViewDetails(clusterId, e);
        });
    });
    
    // 为按钮添加点击事件（使用事件委托，因为按钮是动态生成的）
    const journeyContainer = document.getElementById('journeyVisualization');
    if (journeyContainer) {
        journeyContainer.addEventListener('click', function(e) {
            if (e.target.closest('.btn-view-details')) {
                const btn = e.target.closest('.btn-view-details');
                const card = btn.closest('.cluster-card');
                if (card) {
                    const clusterId = card.getAttribute('data-cluster-id') || btn.getAttribute('data-cluster-id');
                    if (clusterId) {
                        handleViewDetails(clusterId, e);
                    }
                }
            }
        });
    }
}

// 数字动画效果
function animateValue(element, start, end, duration) {
    if (!element) return;
    
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = Math.floor(progress * (end - start) + start);
        element.textContent = current;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// 初始化折叠卡片
function initAccordions() {
    document.querySelectorAll('.acc-item').forEach(item => {
        const header = item.querySelector('.acc-header');
        const content = item.querySelector('.acc-content');
        
        if (!header || !content) return;
        
        header.onclick = () => {
            const active = item.classList.toggle('active');
            content.style.maxHeight = active ? content.scrollHeight + 'px' : '0px';
        };
    });
}

// 初始化导航栏点击事件
function initNavbar() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = link.getAttribute('data-tab');
            if (tabName) {
                showTab(tabName, link);
            }
        });
    });
}

// 页面加载时初始化
// 检查WordCloud库是否加载
function checkWordCloudLibrary() {
    if (typeof WordCloud !== 'undefined') {
        return WordCloud;
    } else if (typeof window !== 'undefined' && typeof window.WordCloud !== 'undefined') {
        return window.WordCloud;
    }
    return null;
}

// 等待WordCloud库加载
function waitForWordCloud(callback, maxAttempts = 10) {
    let attempts = 0;
    const checkInterval = setInterval(() => {
        attempts++;
        const WordCloudFunc = checkWordCloudLibrary();
        if (WordCloudFunc) {
            clearInterval(checkInterval);
            console.log('WordCloud库已加载');
            if (callback) callback(WordCloudFunc);
        } else if (attempts >= maxAttempts) {
            clearInterval(checkInterval);
            console.error('WordCloud库加载超时');
            if (callback) callback(null);
        }
    }, 200);
}

// 移除聚类名中的emoji
function removeEmojiFromClusterName(name) {
    if (!name) return name;
    // 移除所有emoji和variation selector（包括FE0F）
    return name.replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{FE00}-\u{FE0F}]|[\u{200D}]/gu, '').trim();
}

// 获取聚类显示名称（支持多语言）
function getClusterDisplayName(clusterName) {
    if (typeof translateClusterName === 'function') {
        return translateClusterName(clusterName);
    }
    return removeEmojiFromClusterName(clusterName);
}

// 页面加载完成后处理词云队列
document.addEventListener('DOMContentLoaded', function() {
    // 启动词云队列处理
    setTimeout(processWordCloudQueue, 500);
    setTimeout(processWordCloudQueue, 1000);
    setTimeout(processWordCloudQueue, 2000);
});

// 聚类更新功能
let updateIntervalId = null;
let lastUpdateTime = null;

// 初始化更新设置
function initUpdateSettings() {
    const updateSelect = document.getElementById('autoUpdateInterval');
    const updateBtn = document.getElementById('updateClustersBtn');
    
    if (!updateSelect || !updateBtn) return;
    
    // 从本地存储加载设置
    const savedInterval = localStorage.getItem('clusterAutoUpdateInterval') || 'manual';
    updateSelect.value = savedInterval;
    
    // 加载上次更新时间
    const savedLastUpdate = localStorage.getItem('clusterLastUpdateTime');
    if (savedLastUpdate) {
        lastUpdateTime = new Date(savedLastUpdate);
    }
    
    // 监听选择器变化
    updateSelect.addEventListener('change', (e) => {
        const interval = e.target.value;
        localStorage.setItem('clusterAutoUpdateInterval', interval);
        setupAutoUpdate(interval);
    });
    
    // 监听手动更新按钮
    updateBtn.addEventListener('click', () => {
        triggerClusterUpdate();
    });
    
    // 初始化自动更新
    setupAutoUpdate(savedInterval);
}

// 设置自动更新
function setupAutoUpdate(interval) {
    // 清除现有定时器
    if (updateIntervalId) {
        clearInterval(updateIntervalId);
        updateIntervalId = null;
    }
    
    if (interval === 'manual') {
        return;
    }
    
    // 计算更新间隔（毫秒）
    const intervals = {
        '3days': 3 * 24 * 60 * 60 * 1000,
        '1week': 7 * 24 * 60 * 60 * 1000,
        '1month': 30 * 24 * 60 * 60 * 1000,
        '3months': 90 * 24 * 60 * 60 * 1000
    };
    
    const intervalMs = intervals[interval];
    if (!intervalMs) return;
    
    // 如果上次更新时间存在，检查是否需要立即更新
    if (lastUpdateTime) {
        const timeSinceLastUpdate = Date.now() - lastUpdateTime.getTime();
        if (timeSinceLastUpdate >= intervalMs) {
            // 已经超过更新间隔，立即更新
            triggerClusterUpdate();
        } else {
            // 设置定时器，在剩余时间后更新
            const remainingTime = intervalMs - timeSinceLastUpdate;
            updateIntervalId = setTimeout(() => {
                triggerClusterUpdate();
                // 然后设置定期更新
                updateIntervalId = setInterval(() => {
                    triggerClusterUpdate();
                }, intervalMs);
            }, remainingTime);
        }
    } else {
        // 没有上次更新时间，立即更新一次，然后设置定期更新
        triggerClusterUpdate();
        updateIntervalId = setInterval(() => {
            triggerClusterUpdate();
        }, intervalMs);
    }
}

// 触发聚类更新
async function triggerClusterUpdate() {
    const updateBtn = document.getElementById('updateClustersBtn');
    if (!updateBtn) return;
    
    // 显示加载状态
    updateBtn.disabled = true;
    updateBtn.classList.add('updating');
    const btnSpan = updateBtn.querySelector('span');
    if (btnSpan) btnSpan.textContent = t('header.updating');
    
    // 显示状态提示
        showUpdateStatus('info', t('update.updating'));
    
    try {
        // 调用后端API更新聚类
        // 注意：这里需要根据实际的后端API进行调整
        // 如果没有后端API，可以调用Python脚本
        const response = await fetch('/api/update-clusters', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            // 如果没有后端API，尝试调用本地Python脚本
            throw new Error('后端API不可用，请手动运行更新脚本');
        }
        
        const result = await response.json();
        
        // 更新成功
        lastUpdateTime = new Date();
        localStorage.setItem('clusterLastUpdateTime', lastUpdateTime.toISOString());
        
        // 重新加载数据
        await reloadClusterData();
        
        // 显示成功提示
        showUpdateStatus('success', t('update.success'));
        
        // 刷新当前页面内容
        const currentTab = document.querySelector('.tab-content.active');
        if (currentTab) {
            const tabName = currentTab.id;
            loadTabContent(tabName);
        }
        
    } catch (error) {
        console.error('更新聚类失败:', error);
        // 提供手动更新提示
        showUpdateStatus('error', t('update.error'));
    } finally {
        // 恢复按钮状态
        updateBtn.disabled = false;
        updateBtn.classList.remove('updating');
        const btnSpan = updateBtn.querySelector('span');
        if (btnSpan) btnSpan.textContent = t('header.updateClusters');
    }
}

// 重新加载聚类数据
async function reloadClusterData() {
    try {
        // 重新加载data.js中的数据
        // 注意：这里需要根据实际的数据加载方式进行调整
        return new Promise((resolve, reject) => {
            const dataScript = document.createElement('script');
            dataScript.src = 'data.js?t=' + Date.now(); // 添加时间戳防止缓存
            dataScript.onload = () => {
                console.log('数据重新加载完成');
                resolve();
            };
            dataScript.onerror = () => {
                console.error('数据重新加载失败');
                reject(new Error('数据加载失败'));
            };
            document.head.appendChild(dataScript);
        });
    } catch (error) {
        console.error('重新加载数据失败:', error);
        throw error;
    }
}

// 显示更新状态提示
function showUpdateStatus(type, message) {
    // 移除现有状态提示
    const existingStatus = document.querySelector('.update-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    // 创建新状态提示
    const statusDiv = document.createElement('div');
    statusDiv.className = `update-status ${type} show`;
    
    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : '⏳';
    statusDiv.innerHTML = `
        <span style="font-size: 18px;">${icon}</span>
        <span>${message}</span>
    `;
    
    document.body.appendChild(statusDiv);
    
    // 3秒后自动隐藏
    setTimeout(() => {
        statusDiv.classList.remove('show');
        setTimeout(() => {
            statusDiv.remove();
        }, 300);
    }, 3000);
}

// 初始化语言切换器
function initLanguageSwitcher() {
    const langBtn = document.getElementById('langBtn');
    const currentLangSpan = document.getElementById('currentLang');
    
    if (!langBtn || !currentLangSpan) {
        console.warn('Language switcher elements not found');
        return;
    }
    
    // 更新当前语言显示
    function updateLangDisplay() {
        // 从localStorage或全局变量获取当前语言
        const currentLang = typeof currentLanguage !== 'undefined' ? currentLanguage : (localStorage.getItem('dashboardLanguage') || 'zh');
        currentLangSpan.textContent = currentLang === 'zh' ? '中文' : 'English';
    }
    
    // 初始化显示
    updateLangDisplay();
    
    // 点击切换语言
    langBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // 获取当前语言
        const currentLang = typeof currentLanguage !== 'undefined' ? currentLanguage : (localStorage.getItem('dashboardLanguage') || 'zh');
        const newLang = currentLang === 'zh' ? 'en' : 'zh';
        
        console.log('Switching language from', currentLang, 'to', newLang);
        
        // 添加按钮点击动画
        langBtn.style.transform = 'scale(0.95)';
        setTimeout(() => {
            langBtn.style.transform = 'scale(1)';
        }, 100);
        
        // 切换语言 - 确保函数存在
        if (typeof switchLanguage === 'function') {
            switchLanguage(newLang);
        } else if (typeof window.switchLanguage === 'function') {
            window.switchLanguage(newLang);
        } else {
            // 如果函数不存在，手动切换
            console.warn('switchLanguage function not found, using fallback');
            if (typeof i18n !== 'undefined' && i18n[newLang]) {
                if (typeof currentLanguage !== 'undefined') {
                    currentLanguage = newLang;
                } else if (typeof window.currentLanguage !== 'undefined') {
                    window.currentLanguage = newLang;
                }
                localStorage.setItem('dashboardLanguage', newLang);
                if (typeof updatePageLanguage === 'function') {
                    updatePageLanguage();
                } else if (typeof window.updatePageLanguage === 'function') {
                    window.updatePageLanguage();
                }
            }
        }
        
        // 更新显示
        setTimeout(() => {
            updateLangDisplay();
        }, 100);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // 初始化导航栏
    initNavbar();
    
    // 初始化语言切换器（延迟确保i18n.js已加载）
    setTimeout(() => {
        initLanguageSwitcher();
    }, 100);
    
    // 初始化更新设置
    initUpdateSettings();
    
    // 初始化页面语言（延迟确保i18n.js已加载）
    setTimeout(() => {
        if (typeof updatePageLanguage === 'function') {
            updatePageLanguage();
        }
    }, 150);
    
    // 更新统计数据（带动画效果）
    if (typeof stats !== 'undefined') {
        const totalUsersEl = document.getElementById('totalUsers');
        const totalSegmentsEl = document.getElementById('totalSegments');
        const totalClustersEl = document.getElementById('totalClusters');
        
        if (totalUsersEl) {
            animateValue(totalUsersEl, 0, stats.totalUsers || 0, 1500);
        }
        if (totalSegmentsEl) {
            animateValue(totalSegmentsEl, 0, stats.totalSegments || 0, 1500);
        }
        if (totalClustersEl) {
            animateValue(totalClustersEl, 0, stats.totalClusters || 0, 1500);
        }
    } else if (typeof totalUsers !== 'undefined') {
        // 兼容旧格式
        const totalUsersEl = document.getElementById('totalUsers');
        const totalSegmentsEl = document.getElementById('totalSegments');
        const totalClustersEl = document.getElementById('totalClusters');
        
        if (totalUsersEl) animateValue(totalUsersEl, 0, totalUsers, 1500);
        if (totalSegmentsEl) animateValue(totalSegmentsEl, 0, totalSegments, 1500);
        if (totalClustersEl) animateValue(totalClustersEl, 0, totalClusters, 1500);
    }
    
    // 检查URL hash，支持直接打开特定tab
    const hash = window.location.hash.replace('#', '');
    if (hash) {
        const validTabs = ['home', 'overview', 'journey', 'clusters', 'financial'];
        if (validTabs.includes(hash)) {
            // 找到对应的导航链接并点击
            const navLink = document.querySelector(`.nav-link[data-tab="${hash}"]`);
            if (navLink) {
                // 延迟执行，确保DOM已完全加载
                setTimeout(() => {
                    navLink.click();
                }, 100);
            }
        }
    }
    
    // 初始化折叠卡片
    initAccordions();
    
    // 检查当前激活的标签页
    const currentTab = document.querySelector('.tab-content.active');
    const currentTabId = currentTab ? currentTab.id : 'home';
    
    // 根据当前标签页加载相应内容
    const dashboardHeader = document.getElementById('dashboardHeader');
    
    // 首页、转化分析、用户分析、金融市场分析页面不显示banner
    if (currentTabId === 'home' || currentTabId === 'journey' || currentTabId === 'clusters' || currentTabId === 'financial') {
        if (dashboardHeader) {
            dashboardHeader.style.display = 'none';
        }
    } else {
        // 其他页面：显示仪表板头部
        if (dashboardHeader) {
            dashboardHeader.style.display = 'block';
        }
    }
    
    // 加载对应页面内容
    if (currentTabId === 'home') {
        // 加载首页内容
        if (typeof stats !== 'undefined') {
            setTimeout(() => {
                loadHomepage();
            }, 300);
        }
    } else if (currentTabId === 'financial') {
        // 加载金融市场分析页面
        setTimeout(() => {
            loadFinancialAnalysisPage();
        }, 300);
    } else if (typeof businessInsights !== 'undefined') {
        setTimeout(() => {
            if (currentTabId === 'overview') {
                loadOverview();
            } else if (currentTabId === 'journey') {
                loadJourneyPage();
            } else if (currentTabId === 'clusters') {
                loadUserAnalysisPage();
            }
        }, 300);
    }
    
    // 加载聚类选择器（如果需要）
    if (typeof businessInsights !== 'undefined') {
        loadClusters();
    }
    
    // 监听标签页切换，重新初始化折叠卡片
    const observer = new MutationObserver(() => {
        initAccordions();
    });
    
    const main = document.querySelector('.dashboard-main');
    if (main) {
        observer.observe(main, { childList: true, subtree: true });
    }
    
    // 添加页面加载动画
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// 分析用户卡点
function analyzeUserStuckPoint(user) {
    if (!user.segments || user.segments.length === 0) return null;
    
    const stages = ['浏览阶段', '对比阶段', '决策阶段'];
    const lastSegment = user.segments[user.segments.length - 1];
    const lastStage = lastSegment.purchase_stage || '浏览阶段';
    const stageIndex = stages.indexOf(lastStage);
    
    const stageNames = {
        '浏览阶段': t('stages.browsing'),
        '对比阶段': t('stages.comparison'),
        '决策阶段': t('stages.decision')
    };
    
    // 如果用户在浏览阶段停留很久
    if (lastStage === '浏览阶段' && user.segments.length >= 2) {
        const browseSegments = user.segments.filter(s => s.purchase_stage === '浏览阶段');
        if (browseSegments.length >= 2) {
            const message = currentLanguage === 'zh' 
                ? `用户在浏览阶段停留，${browseSegments.length}个片段未进入对比阶段，可能需要优化产品介绍或引导`
                : `User stuck in ${stageNames['浏览阶段']} stage, ${browseSegments.length} segments haven't entered ${stageNames['对比阶段']} stage, may need to optimize product introduction or guidance`;
            return {
                color: '#F472B6',
                message: message
            };
        }
    }
    
    // 如果用户在对比阶段停留很久
    if (lastStage === '对比阶段' && user.segments.length >= 3) {
        const compareSegments = user.segments.filter(s => s.purchase_stage === '对比阶段');
        if (compareSegments.length >= 2) {
            const message = currentLanguage === 'zh'
                ? `用户在对比阶段停留，${compareSegments.length}个片段未进入决策阶段，可能需要提供更清晰的对比信息或优惠`
                : `User stuck in ${stageNames['对比阶段']} stage, ${compareSegments.length} segments haven't entered ${stageNames['决策阶段']} stage, may need clearer comparison information or offers`;
            return {
                color: '#FBBF24',
                message: message
            };
        }
    }
    
    // 如果用户从未进入决策阶段
    if (stageIndex < 2 && user.segments.length >= 3) {
        const message = currentLanguage === 'zh'
            ? `用户未进入决策阶段，在${lastStage}停留，可能需要更强的转化激励`
            : `User hasn't entered ${stageNames['决策阶段']} stage, stuck at ${stageNames[lastStage] || lastStage}, may need stronger conversion incentives`;
        return {
            color: '#FB7185',
            message: message
        };
    }
    
    // 如果用户意图强度低
    const avgIntentScore = user.segments.reduce((sum, s) => sum + (s.intent_score || 0), 0) / user.segments.length;
    if (avgIntentScore < 0.5 && user.segments.length >= 2) {
        const message = currentLanguage === 'zh'
            ? `用户意图强度较低(${(avgIntentScore * 100).toFixed(0)}%)，可能需要重新激活用户兴趣`
            : `User intent score is low (${(avgIntentScore * 100).toFixed(0)}%), may need to reactivate user interest`;
        return {
            color: '#8FA0B8',
            message: message
        };
    }
    
    return null;
}

// 渲染用户轨迹时间线
function renderUserTrajectoryTimeline(canvasId, user) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !user.segments || user.segments.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;
    const width = container ? container.offsetWidth : 800;
    const height = 400; // 增加高度以容纳更大的片段信息卡片
    
    // 高DPI支持
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.scale(dpr, dpr);
    
    // 聚类颜色映射
    const clusterColors = {
        '0': '#7FE8C1', '1': '#7DA6FF', '2': '#A78BFA', '3': '#F472B6',
        '4': '#60A5FA', '5': '#34D399', '6': '#FBBF24', '7': '#FB7185',
        '8': '#818CF8', '9': '#A78BFA', '10': '#F472B6', '11': '#60A5FA',
        '12': '#34D399', '13': '#FBBF24', '14': '#FB7185', '15': '#818CF8',
        '16': '#7FE8C1', '17': '#7DA6FF'
    };
    
    // 阶段颜色映射
    const stageColors = {
        '浏览阶段': '#60A5FA',
        '对比阶段': '#FBBF24',
        '决策阶段': '#7FE8C1'
    };
    
    // 计算时间范围
    const segments = user.segments.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    const startTime = new Date(segments[0].start_time);
    const endTime = new Date(segments[segments.length - 1].end_time);
    const timeRange = endTime - startTime || 1;
    
    const padding = 50;
    const timelineY = 130; // 时间线位置，为上方片段信息留出更多空间
    const timelineStartX = padding;
    const timelineWidth = width - padding * 2;
    const segmentCardHeight = 110; // 增加片段信息卡片高度以容纳更大的文字
    
    // 绘制背景网格
    ctx.strokeStyle = 'rgba(143, 160, 184, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const x = timelineStartX + (timelineWidth / 4) * i;
        ctx.beginPath();
        ctx.moveTo(x, 30);
        ctx.lineTo(x, height - 30);
        ctx.stroke();
    }
    
    // 绘制时间线
    ctx.strokeStyle = 'rgba(143, 160, 184, 0.4)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(timelineStartX, timelineY);
    ctx.lineTo(timelineStartX + timelineWidth, timelineY);
    ctx.stroke();
    
    // 绘制阶段区域背景
    const stageRegions = [];
    let currentStage = segments[0].purchase_stage || '浏览阶段';
    let stageStartX = timelineStartX;
    
    segments.forEach((segment, index) => {
        const segmentTime = new Date(segment.start_time);
        const timeRatio = (segmentTime - startTime) / timeRange;
        const x = timelineStartX + timeRatio * timelineWidth;
        const stage = segment.purchase_stage || '浏览阶段';
        
        if (stage !== currentStage || index === segments.length - 1) {
            if (index === segments.length - 1) {
                stageRegions.push({
                    stage: currentStage,
                    startX: stageStartX,
                    endX: x,
                    color: stageColors[currentStage] + '15'
                });
            } else {
                stageRegions.push({
                    stage: currentStage,
                    startX: stageStartX,
                    endX: x,
                    color: stageColors[currentStage] + '15'
                });
                currentStage = stage;
                stageStartX = x;
            }
        }
    });
    
    // 绘制阶段区域
    stageRegions.forEach(region => {
        ctx.fillStyle = region.color;
        ctx.fillRect(region.startX, timelineY - 40, region.endX - region.startX, 80);
    });
    
    // 存储节点位置用于交互
    const nodePositions = [];
    const tooltipContainer = document.getElementById(`timelineTooltips-${user.user_id}`);
    if (tooltipContainer) {
        tooltipContainer.innerHTML = ''; // 清空之前的工具提示
    }
    
    // 绘制片段节点和信息卡片
    segments.forEach((segment, index) => {
        const segmentTime = new Date(segment.start_time);
        const timeRatio = (segmentTime - startTime) / timeRange;
        const x = timelineStartX + timeRatio * timelineWidth;
        
        const clusterColor = clusterColors[segment.cluster_id] || '#8FA0B8';
        const stageColor = stageColors[segment.purchase_stage] || '#8FA0B8';
        
        // 计算片段持续时间用于绘制片段块
        const segmentEndTime = new Date(segment.end_time);
        const segmentDuration = segmentEndTime - segmentTime;
        const segmentWidth = Math.max(2, (segmentDuration / timeRange) * timelineWidth);
        const segmentStartX = x - segmentWidth / 2;
        
        // 绘制片段持续时间块（在时间线上方）
        ctx.fillStyle = clusterColor + '20';
        ctx.fillRect(segmentStartX, 20, segmentWidth, segmentCardHeight);
        ctx.strokeStyle = clusterColor + '60';
        ctx.lineWidth = 1;
        ctx.strokeRect(segmentStartX, 20, segmentWidth, segmentCardHeight);
        
        // 绘制片段信息文本（增大字体）
        const startDate = new Date(segment.start_time);
        const locale = currentLanguage === 'zh' ? 'zh-CN' : 'en-US';
        const timeStr = startDate.toLocaleString(locale, { 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // 片段编号和聚类
        const segmentLabel = currentLanguage === 'zh' ? '片段' : 'Segment';
        const clusterLabel = t('cluster.label');
        ctx.fillStyle = '#ECF2F5';
        ctx.font = 'bold 13px Arial, "Microsoft YaHei", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${segmentLabel} ${segment.segment_index || index + 1}`, x, 40);
        
        ctx.fillStyle = clusterColor;
        ctx.font = '12px Arial, "Microsoft YaHei", sans-serif';
        ctx.fillText(`${clusterLabel} ${segment.cluster_id}`, x, 58);
        
        // 阶段和意图强度
        const stageTranslations = {
            '浏览阶段': currentLanguage === 'zh' ? '浏览阶段' : 'Browsing',
            '对比阶段': currentLanguage === 'zh' ? '对比阶段' : 'Comparison',
            '决策阶段': currentLanguage === 'zh' ? '决策阶段' : 'Decision'
        };
        const purchaseStage = segment.purchase_stage || (currentLanguage === 'zh' ? '浏览阶段' : 'Browsing');
        const displayStage = stageTranslations[purchaseStage] || purchaseStage;
        ctx.fillStyle = stageColor;
        ctx.font = '12px Arial, "Microsoft YaHei", sans-serif';
        ctx.fillText(displayStage, x, 76);
        
        const intentScore = segment.intent_score || 0;
        const intentLabel = currentLanguage === 'zh' ? '意图' : 'Intent';
        ctx.fillStyle = '#8FA0B8';
        ctx.font = '11px Arial, "Microsoft YaHei", sans-serif';
        ctx.fillText(`${intentLabel}: ${(intentScore * 100).toFixed(0)}%`, x, 94);
        
        // 持续时间
        const duration = (segment.duration_seconds || (segment.duration_minutes * 60) || 0).toFixed(1);
        const durationUnit = currentLanguage === 'zh' ? '秒' : 's';
        ctx.fillText(`${duration}${durationUnit}`, x, 112);
        
        // 绘制意图强度指示器（背景）
        const intentHeight = intentScore * 35;
        ctx.fillStyle = stageColor + '30';
        ctx.fillRect(x - 3, timelineY - intentHeight, 6, intentHeight);
        
        // 绘制节点（带阴影效果）
        ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
        ctx.shadowBlur = 4;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 2;
        
        ctx.beginPath();
        ctx.arc(x, timelineY, 10, 0, Math.PI * 2);
        ctx.fillStyle = clusterColor;
        ctx.fill();
        ctx.strokeStyle = stageColor;
        ctx.lineWidth = 3;
        ctx.stroke();
        
        ctx.shadowBlur = 0;
        
        // 绘制意图强度指示器（前景）
        ctx.fillStyle = stageColor + '80';
        ctx.fillRect(x - 2, timelineY - intentHeight, 4, intentHeight);
        
        // 存储节点信息用于交互
        nodePositions.push({
            x, y: timelineY, segment, index, segmentStartX, segmentWidth
        });
        
        // 创建详细的片段信息卡片（默认隐藏，悬停时显示）
        if (tooltipContainer) {
            const tooltip = document.createElement('div');
            tooltip.className = 'timeline-segment-tooltip';
            tooltip.id = `tooltip-${user.user_id}-${index}`;
            tooltip.style.left = `${x}px`;
            tooltip.style.top = '20px';
            tooltip.style.transform = 'translateX(-50%)';
            tooltip.style.opacity = '0';
            tooltip.style.pointerEvents = 'none';
            
            const duration = (segment.duration_seconds || (segment.duration_minutes * 60) || 0).toFixed(2);
            const segmentLabel = currentLanguage === 'zh' ? '片段' : 'Segment';
            const clusterLabel = t('cluster.label');
            const stageTranslations = {
                '浏览阶段': currentLanguage === 'zh' ? '浏览阶段' : 'Browsing',
                '对比阶段': currentLanguage === 'zh' ? '对比阶段' : 'Comparison',
                '决策阶段': currentLanguage === 'zh' ? '决策阶段' : 'Decision'
            };
            const purchaseStage = segment.purchase_stage || (currentLanguage === 'zh' ? '浏览阶段' : 'Browsing');
            const displayStage = stageTranslations[purchaseStage] || purchaseStage;
            tooltip.innerHTML = `
                <div class="tooltip-header">
                    <span class="tooltip-title">${segmentLabel} ${segment.segment_index || index + 1}</span>
                    <span class="tooltip-time">${timeStr}</span>
                </div>
                <div class="tooltip-cluster" style="background: ${clusterColor}20; border-left: 3px solid ${clusterColor}">
                    <span class="cluster-label">${clusterLabel} ${segment.cluster_id}</span>
                    ${segment.cluster_name ? `<span class="cluster-name">${getClusterDisplayName(segment.cluster_name)}</span>` : ''}
                </div>
                <div class="tooltip-details">
                    <div class="tooltip-detail-item">
                        <span class="tooltip-label">${currentLanguage === 'zh' ? '购买阶段' : 'Purchase Stage'}:</span>
                        <span class="tooltip-value stage-badge" style="background: ${stageColor}20; color: ${stageColor}; border-left: 3px solid ${stageColor}">${displayStage}</span>
                    </div>
                    <div class="tooltip-detail-item">
                        <span class="tooltip-label">${currentLanguage === 'zh' ? '持续时间' : 'Duration'}:</span>
                        <span class="tooltip-value">${duration} ${currentLanguage === 'zh' ? '秒' : 's'}</span>
                    </div>
                    <div class="tooltip-detail-item">
                        <span class="tooltip-label">交互次数:</span>
                        <span class="tooltip-value">${segment.record_count || 0} 次</span>
                    </div>
                    <div class="tooltip-detail-item intent-item">
                        <span class="tooltip-label">意图强度:</span>
                        <div class="intent-progress">
                            <div class="intent-progress-bar" style="width: ${(intentScore * 100).toFixed(0)}%; background: linear-gradient(90deg, ${stageColor} 0%, ${clusterColor} 100%);"></div>
                            <span class="intent-progress-value">${(intentScore * 100).toFixed(0)}%</span>
                        </div>
                    </div>
                </div>
            `;
            tooltipContainer.appendChild(tooltip);
        }
        
        // 绘制时间标签（在时间线下方）
        if (index === 0 || index === segments.length - 1 || 
            (index % Math.max(1, Math.floor(segments.length / 5)) === 0)) {
            ctx.fillStyle = '#8FA0B8';
            ctx.font = '13px Arial, "Microsoft YaHei", sans-serif';
            ctx.textAlign = 'center';
            const timeStr = segmentTime.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
            ctx.fillText(timeStr, x, timelineY + 35);
        }
    });
    
    // 添加鼠标交互（优化稳定性）
    let currentHoveredIndex = -1;
    let hideTimeout = null;
    let showTimeout = null;
    let isTooltipVisible = false;
    
    const showTooltip = (nodeIndex) => {
        if (hideTimeout) {
            clearTimeout(hideTimeout);
            hideTimeout = null;
        }
        
        if (currentHoveredIndex === nodeIndex && isTooltipVisible) {
            return; // 已经显示，不需要重复操作
        }
        
        // 清除之前的显示延迟
        if (showTimeout) {
            clearTimeout(showTimeout);
        }
        
        showTimeout = setTimeout(() => {
            // 隐藏所有工具提示
            if (tooltipContainer) {
                tooltipContainer.querySelectorAll('.timeline-segment-tooltip').forEach(t => {
                    t.style.opacity = '0';
                    t.style.pointerEvents = 'none';
                });
            }
            
            // 显示当前工具提示
            const tooltip = document.getElementById(`tooltip-${user.user_id}-${nodeIndex}`);
            if (tooltip) {
                // 先设置位置，再显示（避免闪烁）
                const node = nodePositions.find(n => n.index === nodeIndex);
                if (node) {
                    tooltip.style.left = `${node.x}px`;
                    tooltip.style.top = '20px';
                    tooltip.style.display = 'block'; // 确保元素可见
                    
                    // 调整位置，确保不超出容器
                    requestAnimationFrame(() => {
                        const tooltipRect = tooltip.getBoundingClientRect();
                        const containerRect = tooltipContainer.getBoundingClientRect();
                        const canvasRect = canvas.getBoundingClientRect();
                        
                        let transformX = '-50%';
                        let offsetY = 0;
                        
                        // 水平位置调整
                        if (tooltipRect.right > containerRect.right) {
                            transformX = 'calc(-100% + 50%)';
                        } else if (tooltipRect.left < containerRect.left) {
                            transformX = '0';
                        }
                        
                        // 垂直位置调整（如果工具提示超出画布，显示在下方）
                        if (tooltipRect.bottom > canvasRect.bottom) {
                            offsetY = segmentCardHeight + 30;
                        }
                        
                        tooltip.style.transform = `translateX(${transformX}) translateY(${offsetY}px)`;
                        tooltip.style.opacity = '1';
                        tooltip.style.pointerEvents = 'auto';
                    });
                }
            }
            currentHoveredIndex = nodeIndex;
            isTooltipVisible = true;
            showTimeout = null;
        }, 100); // 100ms延迟显示，减少频繁切换
    };
    
    const hideTooltip = (immediate = false) => {
        if (showTimeout) {
            clearTimeout(showTimeout);
            showTimeout = null;
        }
        
        if (immediate) {
            if (tooltipContainer) {
                tooltipContainer.querySelectorAll('.timeline-segment-tooltip').forEach(t => {
                    t.style.opacity = '0';
                    t.style.pointerEvents = 'none';
                });
            }
            currentHoveredIndex = -1;
            isTooltipVisible = false;
        } else {
            // 延迟隐藏，给用户时间移动到工具提示上
            hideTimeout = setTimeout(() => {
                if (tooltipContainer) {
                    tooltipContainer.querySelectorAll('.timeline-segment-tooltip').forEach(t => {
                        t.style.opacity = '0';
                        t.style.pointerEvents = 'none';
                    });
                }
                currentHoveredIndex = -1;
                isTooltipVisible = false;
                hideTimeout = null;
            }, 200); // 200ms延迟隐藏
        }
    };
    
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left) * (canvas.width / dpr / rect.width);
        const mouseY = (e.clientY - rect.top) * (canvas.height / dpr / rect.height);
        
        let hoveredNode = null;
        nodePositions.forEach(node => {
            // 检查是否在片段块区域内（扩大检测区域）
            const inSegmentBlock = mouseX >= node.segmentStartX - 5 && 
                                   mouseX <= node.segmentStartX + node.segmentWidth + 5 &&
                                   mouseY >= 15 && mouseY <= 20 + segmentCardHeight + 10;
            // 或检查是否在节点附近
            const dist = Math.sqrt(Math.pow(mouseX - node.x, 2) + Math.pow(mouseY - node.y, 2));
            if (inSegmentBlock || dist < 20) {
                hoveredNode = node;
            }
        });
        
        if (hoveredNode) {
            canvas.style.cursor = 'pointer';
            showTooltip(hoveredNode.index);
        } else {
            canvas.style.cursor = 'default';
            hideTooltip();
        }
    });
    
    // 在工具提示容器上添加鼠标事件，保持工具提示显示
    if (tooltipContainer) {
        tooltipContainer.addEventListener('mousemove', (e) => {
            if (isTooltipVisible && currentHoveredIndex !== -1) {
                // 如果鼠标在工具提示上，保持显示
                if (hideTimeout) {
                    clearTimeout(hideTimeout);
                    hideTimeout = null;
                }
            }
        });
        
        tooltipContainer.addEventListener('mouseleave', () => {
            hideTooltip();
        });
    }
    
    canvas.addEventListener('mouseleave', () => {
        canvas.style.cursor = 'default';
        hideTooltip();
    });
    
    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left) * (canvas.width / dpr / rect.width);
        const mouseY = (e.clientY - rect.top) * (canvas.height / dpr / rect.height);
        
        nodePositions.forEach(node => {
            const inSegmentBlock = mouseX >= node.segmentStartX - 5 && 
                                   mouseX <= node.segmentStartX + node.segmentWidth + 5 &&
                                   mouseY >= 15 && mouseY <= 20 + segmentCardHeight + 10;
            const dist = Math.sqrt(Math.pow(mouseX - node.x, 2) + Math.pow(mouseY - node.y, 2));
            if (inSegmentBlock || dist < 20) {
                // 切换工具提示显示/隐藏
                const tooltip = document.getElementById(`tooltip-${user.user_id}-${node.index}`);
                if (tooltip) {
                    if (isTooltipVisible && currentHoveredIndex === node.index) {
                        hideTooltip(true);
                    } else {
                        showTooltip(node.index);
                    }
                }
            }
        });
    });
}

// 渲染用户路径可视化
function renderUserPathVisualization(canvasId, user) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !user.segments || user.segments.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;
    const width = container ? container.offsetWidth : 300;
    const height = 120;
    
    // 高DPI支持
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.scale(dpr, dpr);
    
    const stages = ['浏览阶段', '对比阶段', '决策阶段'];
    const stageNames = {
        '浏览阶段': t('stages.browsing'),
        '对比阶段': t('stages.comparison'),
        '决策阶段': t('stages.decision')
    };
    const stageColors = {
        '浏览阶段': '#60A5FA',
        '对比阶段': '#FBBF24',
        '决策阶段': '#7FE8C1'
    };
    
    // 计算阶段转换
    const segments = user.segments.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    const transitions = [];
    for (let i = 0; i < segments.length - 1; i++) {
        const from = segments[i].purchase_stage || '浏览阶段';
        const to = segments[i + 1].purchase_stage || '浏览阶段';
        if (from !== to) {
            transitions.push({ from, to });
        }
    }
    
    // 绘制节点
    const nodeRadius = 20;
    const nodeSpacing = (width - 40) / (stages.length - 1);
    const centerY = height / 2;
    
    stages.forEach((stage, index) => {
        const x = 20 + index * nodeSpacing;
        
        // 绘制连接线
        if (index < stages.length - 1) {
            const nextX = 20 + (index + 1) * nodeSpacing;
            const hasTransition = transitions.some(t => t.from === stage && t.to === stages[index + 1]);
            
            ctx.strokeStyle = hasTransition ? stageColors[stages[index + 1]] + '60' : 'rgba(143, 160, 184, 0.2)';
            ctx.lineWidth = hasTransition ? 3 : 1;
            ctx.setLineDash(hasTransition ? [] : [5, 5]);
            ctx.beginPath();
            ctx.moveTo(x + nodeRadius, centerY);
            ctx.lineTo(nextX - nodeRadius, centerY);
            ctx.stroke();
            ctx.setLineDash([]);
            
            // 绘制箭头
            if (hasTransition) {
                ctx.fillStyle = stageColors[stages[index + 1]];
                ctx.beginPath();
                ctx.moveTo(nextX - nodeRadius, centerY);
                ctx.lineTo(nextX - nodeRadius - 8, centerY - 5);
                ctx.lineTo(nextX - nodeRadius - 8, centerY + 5);
                ctx.closePath();
                ctx.fill();
            }
        }
        
        // 绘制节点
        const isReached = segments.some(s => (s.purchase_stage || '浏览阶段') === stage);
        const isCurrent = segments[segments.length - 1].purchase_stage === stage;
        
        ctx.beginPath();
        ctx.arc(x, centerY, nodeRadius, 0, Math.PI * 2);
        ctx.fillStyle = isReached ? stageColors[stage] : 'rgba(143, 160, 184, 0.3)';
        ctx.fill();
        
        if (isCurrent) {
            ctx.strokeStyle = '#ECF2F5';
            ctx.lineWidth = 3;
            ctx.stroke();
        }
        
        // 绘制阶段标签
        ctx.fillStyle = isReached ? '#ECF2F5' : '#8FA0B8';
        ctx.font = '11px Arial, "Microsoft YaHei", sans-serif';
        ctx.textAlign = 'center';
        const displayStage = stageNames[stage] || stage;
        ctx.fillText(displayStage, x, centerY + 4);
    });
}

