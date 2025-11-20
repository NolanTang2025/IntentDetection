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
        'clusters': '用户聚类分析',
        'portraits': '用户画像分析',
        'insights': '业务洞察与建议'
    };
    
    const dashboardHeader = document.getElementById('dashboardHeader');
    if (dashboardHeader) {
        if (tabName === 'home') {
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
            case 'clusters':
                loadClusters();
                break;
            case 'portraits':
                loadPortraits();
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
    
    userPortraits.forEach(portrait => {
        const card = document.createElement('div');
        card.className = 'portrait-card';
        
        // 获取聚类名称
        const insight = businessInsights.find(i => i.cluster_id === portrait.cluster_id);
        const clusterName = insight ? insight.user_segment_name : `聚类 ${portrait.cluster_id}`;
        
        // 获取核心需求
        const coreNeed = insight && insight.key_characteristics 
            ? insight.key_characteristics.find(c => c.includes('核心需求'))?.split(':')[1]?.trim() || '综合需求'
            : '综合需求';
        
        card.innerHTML = `
            <h3>聚类 ${portrait.cluster_id}: ${clusterName}</h3>
            <div class="portrait-stats">
                <div class="portrait-stat">
                    <div class="portrait-stat-value">${portrait.unique_users}</div>
                    <div class="portrait-stat-label">独立用户</div>
                </div>
                <div class="portrait-stat">
                    <div class="portrait-stat-value">${portrait.avg_duration_minutes.toFixed(1)}</div>
                    <div class="portrait-stat-label">平均时长(分钟)</div>
                </div>
                <div class="portrait-stat">
                    <div class="portrait-stat-value">${portrait.avg_record_count.toFixed(1)}</div>
                    <div class="portrait-stat-label">平均交互次数</div>
                </div>
            </div>
            <div class="info-item" style="margin-top: 1rem;">
                <strong>核心需求:</strong>
                <span>${coreNeed}</span>
            </div>
            ${portrait.characteristics ? `
            <div class="info-item" style="margin-top: 0.5rem;">
                <strong>购买阶段:</strong>
                <span>${portrait.characteristics.stage || '未知'}</span>
            </div>
            <div class="info-item" style="margin-top: 0.5rem;">
                <strong>价格敏感度:</strong>
                <span>${portrait.characteristics.price || '未知'}</span>
            </div>
            ` : ''}
        `;
        container.appendChild(card);
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
    if (currentTabId === 'home') {
        // 首页：隐藏仪表板头部
        const dashboardHeader = document.getElementById('dashboardHeader');
        if (dashboardHeader) {
            dashboardHeader.style.display = 'none';
        }
        // 加载首页内容
        if (typeof stats !== 'undefined') {
            setTimeout(() => {
                loadHomepage();
            }, 300);
        }
    } else {
        // 其他页面：显示仪表板头部
        const dashboardHeader = document.getElementById('dashboardHeader');
        if (dashboardHeader) {
            dashboardHeader.style.display = 'block';
        }
        // 加载对应页面内容
        if (typeof businessInsights !== 'undefined') {
            setTimeout(() => {
                if (currentTabId === 'overview') {
                    loadOverview();
                } else if (currentTabId === 'clusters') {
                    loadClusters();
                } else if (currentTabId === 'portraits') {
                    loadPortraits();
                } else if (currentTabId === 'insights') {
                    loadInsights();
                }
            }, 300);
        }
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

