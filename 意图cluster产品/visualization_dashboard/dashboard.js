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
    
    // 更新页面标题和头部显示
    const titleMap = {
        'home': '用户意图聚类分析平台',
        'overview': '数据总览',
        'journey': '转化分析',
        'clusters': '用户分析',
        'insights': '业务洞察与建议'
    };
    
    const dashboardHeader = document.getElementById('dashboardHeader');
    if (dashboardHeader) {
        // 首页、转化分析、用户分析页面不显示banner，直接展示主要内容
        if (tabName === 'home' || tabName === 'journey' || tabName === 'clusters') {
            dashboardHeader.style.display = 'none';
        } else {
            dashboardHeader.style.display = 'block';
            const headerTitle = dashboardHeader.querySelector('h1');
            if (headerTitle && titleMap[tabName]) {
                headerTitle.textContent = titleMap[tabName];
            }
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
        'home': '首页',
        'overview': '总览',
        'clusters': '用户聚类',
        'portraits': '用户画像',
        'insights': '业务洞察'
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
            case 'insights':
                loadInsights(); // loadInsights内部会调用loadProducts
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
    if (typeof businessInsights === 'undefined') {
        console.error('businessInsights 数据未加载');
        return;
    }
    
    // 用户聚类分布
    const clusterData = {};
    businessInsights.forEach(insight => {
        const size = parseInt(insight.key_characteristics[0].match(/(\d+)\s*个意图片段/)?.[1] || 0);
        if (size > 0) {
            clusterData[`聚类 ${insight.cluster_id}`] = size;
        }
    });
    
    if (Object.keys(clusterData).length > 0) {
        createPieChart('clusterDistributionChart', clusterData, '用户聚类分布');
    }
    
    // 购买阶段分布
    const stageData = {};
    businessInsights.forEach(insight => {
        const stageMatch = insight.key_characteristics.find(c => c.includes('购买阶段'));
        if (stageMatch) {
            const stage = stageMatch.split(':')[1]?.trim() || '未知';
            const size = parseInt(insight.key_characteristics[0].match(/(\d+)\s*个意图片段/)?.[1] || 0);
            if (stage && size > 0) {
                stageData[stage] = (stageData[stage] || 0) + size;
            }
        }
    });
    
    if (Object.keys(stageData).length > 0) {
        createDoughnutChart('purchaseStageChart', stageData, '购买阶段分布');
    }
    
    // 价格偏好分布
    const priceData = {};
    businessInsights.forEach(insight => {
        const priceMatch = insight.key_characteristics.find(c => c.includes('价格敏感度'));
        if (priceMatch) {
            const price = priceMatch.split(':')[1]?.trim() || '未知';
            const size = parseInt(insight.key_characteristics[0].match(/(\d+)\s*个意图片段/)?.[1] || 0);
            if (price && size > 0) {
                priceData[price] = (priceData[price] || 0) + size;
            }
        }
    });
    
    if (Object.keys(priceData).length > 0) {
        createBarChart('pricePreferenceChart', priceData, '价格偏好分布');
    }
    
    // 核心关注点
    const concernsData = {};
    businessInsights.forEach(insight => {
        const concernMatch = insight.key_characteristics.find(c => c.includes('关注点'));
        if (concernMatch) {
            const concern = concernMatch.split(':')[1]?.trim() || '未知';
            const size = parseInt(insight.key_characteristics[0].match(/(\d+)\s*个意图片段/)?.[1] || 0);
            if (concern && size > 0) {
                concernsData[concern] = (concernsData[concern] || 0) + size;
            }
        }
    });
    
    if (Object.keys(concernsData).length > 0) {
        createHorizontalBarChart('concernsChart', concernsData, '核心关注点');
    }
    
    // 关键洞察
    displayKeyInsights();
}

// 显示关键洞察
function displayKeyInsights() {
    const container = document.getElementById('keyInsights');
    if (!container) return;
    
    container.innerHTML = '';
    
    // 找出最大的几个聚类
    const topClusters = businessInsights
        .map(insight => {
            const size = parseInt(insight.key_characteristics[0].match(/(\d+)\s*个意图片段/)?.[1] || 0);
            return { ...insight, size };
        })
        .sort((a, b) => b.size - a.size)
        .slice(0, 4);
    
    if (topClusters.length === 0) {
        container.innerHTML = '<p>暂无数据</p>';
        return;
    }
    
    topClusters.forEach(cluster => {
        const card = document.createElement('div');
        card.className = 'insight-card';
        card.innerHTML = `
            <h4>聚类 ${cluster.cluster_id}: ${cluster.user_segment_name}</h4>
            <p><strong>规模:</strong> ${cluster.size} 个片段</p>
            <p><strong>策略:</strong> ${cluster.marketing_strategy && cluster.marketing_strategy.length > 0 
                ? cluster.marketing_strategy[0] 
                : '暂无策略建议'}</p>
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
    
    select.innerHTML = '<option value="">-- 选择聚类 --</option>';
    
    businessInsights.forEach(insight => {
        const option = document.createElement('option');
        option.value = insight.cluster_id;
        option.textContent = `聚类 ${insight.cluster_id}: ${insight.user_segment_name}`;
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
    
    container.innerHTML = `
        <div class="cluster-info-card">
            <h3>聚类 ${clusterId}: ${insight.user_segment_name}</h3>
            
            <div class="info-grid">
                ${insight.key_characteristics.map(char => `
                    <div class="info-item">
                        <strong>${char.split(':')[0]}</strong>
                        <span>${char.split(':')[1] || char}</span>
                    </div>
                `).join('')}
            </div>
            
            <div class="strategy-section">
                <h4>📊 营销策略建议</h4>
                <ul class="strategy-list">
                    ${insight.marketing_strategy.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
            
            <div class="strategy-section">
                <h4>🛍️ 产品推荐</h4>
                <ul class="strategy-list">
                    ${insight.product_recommendations.length > 0 
                        ? insight.product_recommendations.map(r => `<li>${r}</li>`).join('')
                        : '<li>需要进一步分析产品偏好</li>'}
                </ul>
            </div>
            
            <div class="strategy-section">
                <h4>⚡ 转化优化建议</h4>
                <ul class="strategy-list">
                    ${insight.conversion_optimization.map(o => `<li>${o}</li>`).join('')}
                </ul>
            </div>
            
            ${insight.pricing_strategy && insight.pricing_strategy.length > 0 ? `
            <div class="strategy-section">
                <h4>💰 价格策略建议</h4>
                <ul class="strategy-list">
                    ${insight.pricing_strategy.map(p => `<li>${p}</li>`).join('')}
                </ul>
            </div>
            ` : ''}
            
            <div class="strategy-section">
                <h4>📝 内容策略建议</h4>
                <ul class="strategy-list">
                    ${insight.content_strategy && insight.content_strategy.length > 0 
                        ? insight.content_strategy.map(c => `<li>${c}</li>`).join('')
                        : '<li>暂无内容策略建议</li>'}
                </ul>
            </div>
            
            ${insight.campaign_differentiation && insight.campaign_differentiation.length > 0 ? `
            <div class="strategy-section">
                <h4>🎯 差异化营销活动</h4>
                <ul class="strategy-list">
                    ${insight.campaign_differentiation.map(c => `<li>${c}</li>`).join('')}
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
        const clusterName = insight ? insight.user_segment_name : `聚类 ${portrait.cluster_id}`;
        
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
        
        // 准备使用场景偏好数据
        const scenarioData = {
            ...(portrait.intent_profile?.main_appeal || {}),
            ...(portrait.intent_profile?.concerns || {})
        };
        
        // 准备雷达图数据
        const radarData = prepareRadarData(portrait);
        
        const cardId = `portrait-card-${portrait.cluster_id}`;
        card.id = cardId;
        
        card.innerHTML = `
            <div class="portrait-header">
                <div class="portrait-title-section">
                    <h3>聚类 ${portrait.cluster_id}</h3>
                    <h2>${clusterName}</h2>
                </div>
                <div class="portrait-stats-mini">
                    <div class="stat-mini">
                        <span class="stat-mini-value">${portrait.unique_users}</span>
                        <span class="stat-mini-label">用户</span>
                    </div>
                    <div class="stat-mini">
                        <span class="stat-mini-value">${portrait.segment_count}</span>
                        <span class="stat-mini-label">片段</span>
                    </div>
                    <div class="stat-mini">
                        <span class="stat-mini-value">${(portrait.avg_duration_seconds || 0).toFixed(0)}s</span>
                        <span class="stat-mini-label">时长</span>
                    </div>
                </div>
            </div>
            
            <div class="portrait-visualizations">
                <!-- 词云 -->
                <div class="visualization-section">
                    <h4>📝 用户关注词云</h4>
                    <canvas id="wordcloud-${portrait.cluster_id}" class="wordcloud-canvas"></canvas>
                </div>
                
                <!-- 价格偏好 -->
                <div class="visualization-section">
                    <h4>💰 价格偏好分布</h4>
                    <canvas id="priceChart-${portrait.cluster_id}" class="chart-canvas"></canvas>
                </div>
                
                <!-- 使用场景偏好 -->
                <div class="visualization-section">
                    <h4>🎯 使用场景偏好</h4>
                    <canvas id="scenarioChart-${portrait.cluster_id}" class="chart-canvas"></canvas>
                </div>
                
                <!-- 特征雷达图 -->
                <div class="visualization-section">
                    <h4>📊 特征雷达图</h4>
                    <canvas id="radarChart-${portrait.cluster_id}" class="chart-canvas"></canvas>
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
            
            // 渲染价格偏好图表
            if (Object.keys(priceData).length > 0) {
                createDoughnutChart(`priceChart-${portrait.cluster_id}`, priceData, '价格偏好');
            } else {
                // 如果没有价格数据，显示占位符
                const priceCanvas = document.getElementById(`priceChart-${portrait.cluster_id}`);
                if (priceCanvas && priceCanvas.parentElement) {
                    priceCanvas.parentElement.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><p>暂无价格偏好数据</p></div>';
                }
            }
            
            // 渲染使用场景偏好图表
            if (Object.keys(scenarioData).length > 0) {
                createHorizontalBarChart(`scenarioChart-${portrait.cluster_id}`, scenarioData, '使用场景偏好');
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
    
    console.log('准备词云数据 - 聚类', portrait.cluster_id);
    
    // 1. 从特征中提取关键词（必须保留，即使被过滤也要保留）
    if (portrait.characteristics) {
        Object.entries(portrait.characteristics).forEach(([key, value]) => {
            if (value && typeof value === 'string') {
                // 根据特征类型设置不同权重
                const weightMap = {
                    'behavior': 50,  // 行为模式最重要
                    'urgency': 45,   // 紧迫度次重要
                    'stage': 40,     // 购买阶段
                    'product': 35,   // 产品偏好
                    'concern': 30,   // 关注点
                    'need': 40       // 核心需求
                };
                const size = weightMap[key] || 30;
                words.push({ text: value, size: size, source: 'characteristics' });
                console.log(`  - 特征词: ${value} (${key}, 权重: ${size})`);
            }
        });
    }
    
    // 2. 从核心需求中提取（高权重）
    if (portrait.intent_profile?.main_appeal) {
        Object.keys(portrait.intent_profile.main_appeal).forEach(key => {
            if (key && !genericTerms.includes(key)) {
                words.push({ text: key, size: 45, source: 'main_appeal' });
                console.log(`  - 核心需求: ${key} (权重: 45)`);
            } else if (key) {
                // 即使被过滤，也作为备用词（权重较低）
                words.push({ text: key, size: 25, source: 'main_appeal_fallback' });
            }
        });
    }
    
    // 3. 从关注点中提取
    if (portrait.intent_profile?.concerns) {
        Object.keys(portrait.intent_profile.concerns).forEach(key => {
            if (key && !genericTerms.includes(key)) {
                words.push({ text: key, size: 35, source: 'concerns' });
                console.log(`  - 关注点: ${key} (权重: 35)`);
            } else if (key) {
                words.push({ text: key, size: 20, source: 'concerns_fallback' });
            }
        });
    }
    
    // 4. 从产品偏好中提取（重要：处理"X偏好"格式）
    if (portrait.product_preferences) {
        Object.keys(portrait.product_preferences).forEach(key => {
            if (key && key !== '多产品比较') {
                if (key.includes('偏好')) {
                    // 提取产品名称（如"F1偏好" -> "F1"）
                    const productName = key.replace('偏好', '').trim();
                    if (productName) {
                        words.push({ text: productName, size: 40, source: 'product' });
                        console.log(`  - 产品: ${productName} (从"${key}"提取, 权重: 40)`);
                    }
                } else {
                    words.push({ text: key, size: 30, source: 'product' });
                    console.log(`  - 产品: ${key} (权重: 30)`);
                }
            }
        });
    }
    
    // 5. 从价格偏好中提取（即使被过滤也保留）
    if (portrait.intent_profile?.price_range) {
        Object.keys(portrait.intent_profile.price_range).forEach(key => {
            if (key && !genericTerms.includes(key)) {
                words.push({ text: key, size: 25, source: 'price' });
                console.log(`  - 价格偏好: ${key} (权重: 25)`);
            }
        });
    }
    
    // 6. 从业务洞察中提取关键词
    if (insight) {
        // 从产品推荐中提取
        if (insight.product_recommendations) {
            insight.product_recommendations.forEach(rec => {
                // 提取【】中的关键词
                const keywords = rec.match(/【([^】]+)】/g);
                if (keywords) {
                    keywords.forEach(kw => {
                        const text = kw.replace(/【|】/g, '').trim();
                        if (text) {
                            words.push({ text: text, size: 20, source: 'recommendations' });
                            console.log(`  - 推荐关键词: ${text} (权重: 20)`);
                        }
                    });
                }
                // 提取产品名称（如"F1偏好"、"Z6偏好"）
                const productMatches = rec.match(/([A-Z]\d+)\s*偏好/g);
                if (productMatches) {
                    productMatches.forEach(match => {
                        const productName = match.replace(/\s*偏好/g, '').trim();
                        if (productName) {
                            words.push({ text: productName, size: 30, source: 'recommendations_product' });
                            console.log(`  - 推荐产品: ${productName} (权重: 30)`);
                        }
                    });
                }
            });
        }
        
        // 从关键特征中提取
        if (insight.key_characteristics) {
            insight.key_characteristics.forEach(char => {
                // 提取核心需求
                if (char.includes('核心需求:')) {
                    const need = char.split('核心需求:')[1]?.trim();
                    if (need && need !== '综合需求') {
                        words.push({ text: need, size: 40, source: 'key_characteristics' });
                        console.log(`  - 关键特征-核心需求: ${need} (权重: 40)`);
                    }
                }
                // 提取产品偏好
                if (char.includes('产品偏好:')) {
                    const product = char.split('产品偏好:')[1]?.trim();
                    if (product && product !== '多产品比较') {
                        if (product.includes('偏好')) {
                            const productName = product.replace('偏好', '').trim();
                            if (productName) {
                                words.push({ text: productName, size: 35, source: 'key_characteristics_product' });
                                console.log(`  - 关键特征-产品: ${productName} (权重: 35)`);
                            }
                        } else {
                            words.push({ text: product, size: 35, source: 'key_characteristics_product' });
                        }
                    }
                }
                // 提取关注点
                if (char.includes('关注点:')) {
                    const concern = char.split('关注点:')[1]?.trim();
                    if (concern && concern !== '综合关注') {
                        words.push({ text: concern, size: 30, source: 'key_characteristics_concern' });
                        console.log(`  - 关键特征-关注点: ${concern} (权重: 30)`);
                    }
                }
            });
        }
    }
    
    // 7. 从聚类名称中提取关键词（去除emoji）
    if (portrait.cluster_name) {
        const cleanName = portrait.cluster_name.replace(/[🔍⚡👁️]/g, '').trim();
        if (cleanName) {
            // 分割名称中的关键词
            const nameParts = cleanName.split(/[·\s]+/);
            nameParts.forEach(part => {
                if (part && part.length > 1) {
                    words.push({ text: part, size: 35, source: 'cluster_name' });
                    console.log(`  - 聚类名称: ${part} (权重: 35)`);
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
    
    // 转换为词云格式 [text, size]
    let result = Object.entries(wordMap)
        .filter(([text]) => text && text.length > 0 && text.length <= 10) // 过滤空词和过长的词
        .map(([text, size]) => [text, Math.min(Math.max(size, 15), 60)]);
    
    // 如果结果为空或太少，添加特征词作为备用
    if (result.length === 0) {
        console.warn('词云数据为空，使用特征词作为备用');
        if (portrait.characteristics) {
            Object.values(portrait.characteristics).forEach(value => {
                if (value && typeof value === 'string' && value.length > 0) {
                    result.push([value, 30]);
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
        labels: ['行为模式', '意图紧迫度', '购买阶段', '价格敏感度', '关注点', '核心需求'],
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
        let height = 200;
        
        if (container) {
            // 使用offsetWidth而不是getBoundingClientRect，因为后者可能返回0
            const containerWidth = container.offsetWidth || container.clientWidth || 300;
            width = Math.max(containerWidth - 48, 300); // 减去padding，最小300
        }
        
        // 确保canvas有合理的尺寸
        if (width < 200) width = 300;
        if (height < 150) height = 200;
        
        // 设置canvas尺寸 - 先设置样式再设置属性
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
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
        
        console.log('渲染词云:', canvasId, '尺寸:', width, 'x', height, '词数:', wordList.length, '前3个词:', wordList.slice(0, 3));
        
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
                height: height
            });
            
            WordCloudFunc(canvas, {
                list: wordList,
                gridSize: Math.max(4, Math.round(16 * width / 1024)), // 根据宽度调整gridSize，最小4
                weightFactor: function(size) {
                    // 动态调整权重因子，确保词云大小合适
                    const factor = Math.pow(size / 50, 1.5) * (width / 300) * 8;
                    return Math.max(10, Math.min(factor, 100)); // 限制在合理范围内
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
                                    const factor = Math.pow(size / 50, 1.2) * (width / 300) * 12; // 更大的权重因子
                                    return Math.max(15, Math.min(factor, 150));
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
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#ECF2F5',
                        font: {
                            size: 11
                        }
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

// 加载业务洞察页面
function loadInsights() {
    if (typeof businessInsights === 'undefined') {
        console.error('businessInsights 数据未加载');
        return;
    }
    
    // 加载产品偏好数据（显示在产品偏好分析部分）
    if (typeof userPortraits !== 'undefined') {
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
        const productContainer = document.getElementById('productDetails');
        if (productContainer) {
            productContainer.innerHTML = '';
            
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
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);">
                        <strong>主要关注聚类:</strong>
                        <div style="margin-top: 0.5rem;">
                            ${clusters.map(c => `<span style="display: inline-block; padding: 0.25rem 0.75rem; margin: 0.25rem; background: var(--glass); border: 1px solid var(--border); border-radius: 4px;">聚类 ${c.cluster} (${c.count}次)</span>`).join('')}
                        </div>
                    </div>
                    ` : ''}
                `;
                productContainer.appendChild(card);
            });
        }
    }
    
    // 加载业务洞察内容
    const container = document.getElementById('insightsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    businessInsights.forEach(insight => {
        const card = document.createElement('div');
        card.className = 'insight-card-large';
        
        card.innerHTML = `
            <h3>聚类 ${insight.cluster_id}: ${insight.user_segment_name}</h3>
            
            <div class="insight-section">
                <h4>关键特征</h4>
                <ul>
                    ${insight.key_characteristics.map(c => `<li>${c}</li>`).join('')}
                </ul>
            </div>
            
            <div class="insight-section">
                <h4>营销策略建议</h4>
                <ul>
                    ${insight.marketing_strategy.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
            
            <div class="insight-section">
                <h4>产品推荐建议</h4>
                <ul>
                    ${insight.product_recommendations.length > 0 
                        ? insight.product_recommendations.map(r => `<li>${r}</li>`).join('')
                        : '<li>需要进一步分析产品偏好</li>'}
                </ul>
            </div>
            
            <div class="insight-section">
                <h4>转化优化建议</h4>
                <ul>
                    ${insight.conversion_optimization.map(o => `<li>${o}</li>`).join('')}
                </ul>
            </div>
            
            ${insight.pricing_strategy && insight.pricing_strategy.length > 0 ? `
            <div class="insight-section">
                <h4>价格策略建议</h4>
                <ul>
                    ${insight.pricing_strategy.map(p => `<li>${p}</li>`).join('')}
                </ul>
            </div>
            ` : ''}
            
            <div class="insight-section">
                <h4>内容策略建议</h4>
                <ul>
                    ${insight.content_strategy && insight.content_strategy.length > 0 
                        ? insight.content_strategy.map(c => `<li>${c}</li>`).join('')
                        : '<li>暂无内容策略建议</li>'}
                </ul>
            </div>
            
            ${insight.campaign_differentiation && insight.campaign_differentiation.length > 0 ? `
            <div class="insight-section">
                <h4>差异化营销活动</h4>
                <ul>
                    ${insight.campaign_differentiation.map(c => `<li>${c}</li>`).join('')}
                </ul>
            </div>
            ` : ''}
        `;
        container.appendChild(card);
    });
}

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
    
    // 生成可视化
    container.innerHTML = generateJourneyHTML(stages);
    
    // 添加交互效果
    initJourneyInteractions();
}

// 生成转化路径HTML
function generateJourneyHTML(stages) {
    const stageConfig = {
        '浏览阶段': {
            icon: '🔍',
            color: '#60A5FA',
            gradient: 'linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%)',
            description: '用户开始探索产品，了解基本信息'
        },
        '对比阶段': {
            icon: '⚖️',
            color: '#FBBF24',
            gradient: 'linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%)',
            description: '用户比较不同选项，评估产品价值'
        },
        '决策阶段': {
            icon: '✅',
            color: '#7FE8C1',
            gradient: 'linear-gradient(135deg, #7FE8C1 0%, #34D399 100%)',
            description: '用户准备购买，需要转化激励'
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
                        ${config.icon}
                    </div>
                    <div class="stage-info">
                        <h2>${stageName}</h2>
                        <p>${config.description}</p>
                        <div class="stage-stats">
                            <span class="stat-item">
                                <strong>${clusters.length}</strong> 个画像
                            </span>
                            <span class="stat-item">
                                <strong>${totalUsers}</strong> 个片段
                            </span>
                            <span class="stat-item">
                                <strong>${percentage}%</strong> 占比
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
                                        聚类 ${cluster.cluster_id}
                                    </div>
                                    <div class="cluster-size">
                                        ${size} 个片段
                                    </div>
                                </div>
                                <h3 class="cluster-name">${cluster.user_segment_name}</h3>
                                <div class="cluster-progress">
                                    <div class="progress-bar" style="width: ${sizePercentage}%; background: ${config.gradient}"></div>
                                    <span class="progress-text">${sizePercentage}%</span>
                                </div>
                                <div class="cluster-characteristics">
                                    ${cluster.key_characteristics.slice(1, 4).map(char => {
                                        const [key, value] = char.split(':');
                                        return `<div class="char-item">
                                            <span class="char-key">${key}:</span>
                                            <span class="char-value">${value?.trim() || ''}</span>
                                        </div>`;
                                    }).join('')}
                                </div>
                                <div class="cluster-actions">
                                    <button class="btn-view-details" data-cluster-id="${cluster.cluster_id}">
                                        <span class="btn-icon">🔍</span>
                                        <span class="btn-text">查看详情</span>
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
                option.textContent = `聚类 ${insight.cluster_id}: ${insight.user_segment_name}`;
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
                clusterNames[insight.cluster_id] = insight.user_segment_name;
            });
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
            
            <div class="user-segments">
                ${user.segments.map((segment, segIdx) => {
                    const startDate = new Date(segment.start_time);
                    const endDate = new Date(segment.end_time);
                    const timeStr = startDate.toLocaleString('zh-CN', { 
                        month: 'short', 
                        day: 'numeric', 
                        hour: '2-digit', 
                        minute: '2-digit' 
                    });
                    
                    // 获取聚类颜色
                    const clusterColors = {
                        '0': '#7FE8C1', '1': '#7DA6FF', '2': '#A78BFA', '3': '#F472B6',
                        '4': '#60A5FA', '5': '#34D399', '6': '#FBBF24', '7': '#FB7185',
                        '8': '#818CF8', '9': '#A78BFA', '10': '#F472B6', '11': '#60A5FA',
                        '12': '#34D399', '13': '#FBBF24', '14': '#FB7185', '15': '#818CF8',
                        '16': '#7FE8C1', '17': '#7DA6FF'
                    };
                    const clusterColor = clusterColors[segment.cluster_id] || '#8FA0B8';
                    
                    return `
                        <div class="segment-item" data-segment-id="${segment.segment_id}">
                            <div class="segment-timeline">
                                <div class="timeline-dot" style="background: ${clusterColor}"></div>
                                <div class="timeline-line"></div>
                            </div>
                            <div class="segment-content">
                                <div class="segment-header">
                                    <div class="segment-time">
                                        <strong>片段 ${segment.segment_index}</strong>
                                        <span>${timeStr}</span>
                                    </div>
                                    <div class="segment-cluster" style="background: ${clusterColor}20; border-left: 3px solid ${clusterColor}">
                                        <span class="cluster-label">聚类 ${segment.cluster_id}</span>
                                        <span class="cluster-name">${segment.cluster_name}</span>
                                    </div>
                                </div>
                                <div class="segment-details">
                                    <div class="detail-item">
                                        <span class="detail-label">购买阶段:</span>
                                        <span class="detail-value">${segment.purchase_stage}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">持续时间:</span>
                                        <span class="detail-value">${(segment.duration_seconds || (segment.duration_minutes * 60) || 0).toFixed(2)} 秒</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">交互次数:</span>
                                        <span class="detail-value">${segment.record_count} 次</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">意图强度:</span>
                                        <span class="detail-value">${(segment.intent_score * 100).toFixed(0)}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        
        container.appendChild(userCard);
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

// 页面加载完成后处理词云队列
document.addEventListener('DOMContentLoaded', function() {
    // 启动词云队列处理
    setTimeout(processWordCloudQueue, 500);
    setTimeout(processWordCloudQueue, 1000);
    setTimeout(processWordCloudQueue, 2000);
});

document.addEventListener('DOMContentLoaded', function() {
    // 初始化导航栏
    initNavbar();
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
    
    // 初始化折叠卡片
    initAccordions();
    
    // 检查当前激活的标签页
    const currentTab = document.querySelector('.tab-content.active');
    const currentTabId = currentTab ? currentTab.id : 'home';
    
    // 根据当前标签页加载相应内容
    const dashboardHeader = document.getElementById('dashboardHeader');
    
    // 首页、转化分析、用户分析页面不显示banner
    if (currentTabId === 'home' || currentTabId === 'journey' || currentTabId === 'clusters') {
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
    } else if (typeof businessInsights !== 'undefined') {
        setTimeout(() => {
            if (currentTabId === 'overview') {
                loadOverview();
            } else if (currentTabId === 'journey') {
                loadJourneyPage();
            } else if (currentTabId === 'clusters') {
                loadUserAnalysisPage();
            } else if (currentTabId === 'insights') {
                loadInsights();
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

