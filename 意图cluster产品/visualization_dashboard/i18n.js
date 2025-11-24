// 多语言资源文件
const i18n = {
    zh: {
        // 导航栏
        nav: {
            home: '首页',
            overview: '总览',
            journey: '转化分析',
            clusters: '用户分析',
            insights: '业务洞察'
        },
        // 品牌
        brand: {
            name: 'Intent Analytics',
            subtitle: '用户意图分析平台'
        },
        // 返回按钮
        back: '返回主页',
        backTitle: '返回意图识别主页',
        // 仪表板头部
        header: {
            overview: '数据总览',
            overviewSubtitle: '实时用户意图分析与业务洞察',
            selectDate: '选择日期',
            exportReport: '导出报告',
            autoUpdate: '自动更新：',
            manual: '手动更新',
            update3days: '每3天',
            update1week: '每周',
            update1month: '每月',
            update3months: '每3个月',
            updateClusters: '更新聚类',
            updateClustersTitle: '立即更新聚类数据',
            updating: '更新中...',
            stats: {
                totalUsers: '独立用户',
                totalSegments: '意图片段',
                totalClusters: '用户聚类'
            }
        },
        // 首页
        home: {
            title: '用户意图聚类分析平台',
            subtitle: '基于业务维度的智能用户细分，驱动精准营销策略',
            stats: {
                users: '独立用户',
                clusters: '用户聚类',
                segments: '意图片段'
            },
            methodology: {
                title: '用户聚类方法论',
                description: '基于业务维度的智能聚类，确保每个聚类都有明确的业务含义和差异化的营销策略'
            },
            dimensions: {
                purchaseStage: {
                    title: '购买阶段',
                    desc: '识别用户处于购买漏斗的哪个阶段',
                    tags: ['浏览阶段', '对比阶段', '决策阶段']
                },
                priceSensitivity: {
                    title: '价格敏感度',
                    desc: '分析用户对价格的敏感程度',
                    tags: ['价格敏感型', '中等价格型', '高端价值型']
                },
                engagement: {
                    title: '参与度',
                    desc: '评估用户的浏览深度和参与程度',
                    tags: ['快速浏览者', '中等参与', '深度研究者']
                },
                productPreference: {
                    title: '产品偏好',
                    desc: '识别用户关注的产品类型和型号',
                    tags: ['Z6偏好', 'A1偏好', 'F1偏好', '多产品比较']
                },
                concerns: {
                    title: '关注点',
                    desc: '了解用户最关心的产品特性',
                    tags: ['功能导向', '价格导向', '舒适度导向', '有效性导向']
                },
                coreNeeds: {
                    title: '核心需求',
                    desc: '识别用户的核心购买动机',
                    tags: ['止鼾需求', '颈部疼痛', '睡眠质量', '综合需求']
                }
            },
            benefits: {
                title: '聚类价值',
                description: '每个聚类都有明确的业务含义和差异化的营销策略',
                items: {
                    clear: {
                        number: '01',
                        title: '明确的业务区分',
                        desc: '基于业务维度聚类，每个聚类都有清晰的标签和特征，易于理解和应用'
                    },
                    strategy: {
                        number: '02',
                        title: '差异化营销策略',
                        desc: '针对不同聚类提供独特的营销建议，确保每个群体都有针对性的策略'
                    },
                    actionable: {
                        number: '03',
                        title: '可执行的行动建议',
                        desc: '提供具体的营销活动、内容策略和转化优化建议，可直接应用到业务中'
                    },
                    dataDriven: {
                        number: '04',
                        title: '数据驱动决策',
                        desc: '基于真实的用户行为数据，确保营销策略的科学性和有效性'
                    }
                }
            },
            quickActions: {
                title: '快速开始',
                overview: {
                    title: '查看数据总览',
                    desc: '了解整体用户意图分布和关键指标'
                },
                clusters: {
                    title: '分析用户聚类',
                    desc: '深入了解每个用户群体的特征'
                },
                insights: {
                    title: '业务洞察与产品偏好',
                    desc: '查看营销策略建议和产品偏好分析'
                }
            }
        },
        // 总览页面
        overview: {
            title: '数据总览',
            subtitle: '整体用户意图分析概览与关键指标',
            charts: {
                clusterDistribution: '用户聚类分布',
                purchaseStage: '购买阶段分布',
                pricePreference: '价格偏好分布',
                concerns: '核心关注点'
            },
            insights: {
                title: '关键洞察',
                badge: '实时更新'
            }
        },
        // 转化分析
        journey: {
            title: '转化分析',
            subtitle: '探索用户转化路径与意图轨迹',
            tabs: {
                path: '转化路径',
                trajectory: '用户轨迹',
                cluster: '用户聚类'
            },
            path: {
                title: '用户转化路径可视化',
                subtitle: '探索用户从浏览到决策的完整旅程，了解不同画像在转化各阶段的分布',
                funnelAnalysis: '转化漏斗分析',
                funnelSubtitle: '查看用户在不同阶段的流失情况',
                funnelChart: '用户转化漏斗',
                flowChart: '转化路径流程',
                flowSubtitle: '探索用户从浏览到决策的完整路径'
            },
            trajectory: {
                title: '用户意图轨迹分析',
                subtitle: '查看每个用户在不同时间段的意图切片及其对应的聚类分布',
                search: '搜索用户ID...',
                filter: '筛选:',
                allClusters: '所有聚类',
                sort: '排序:',
                sortByTime: '按时间',
                sortBySegments: '按片段数',
                sortByClusters: '按聚类数'
            },
            cluster: {
                title: '用户聚类分析',
                subtitle: '深入了解每个用户群体的特征与行为模式',
                select: '选择聚类：',
                selectPlaceholder: '-- 选择聚类 --'
            }
        },
        // 用户分析
        clusters: {
            title: '用户分析',
            subtitle: '深入了解用户群体特征与行为模式',
            portrait: {
                title: '用户画像分析',
                subtitle: '详细的用户特征、行为模式与偏好分析'
            }
        },
        // 业务洞察
        insights: {
            title: '业务洞察与建议',
            subtitle: '针对每个用户群体的营销策略、产品偏好与行动建议',
            products: {
                title: '产品偏好分析',
                subtitle: '用户对不同产品的关注度与偏好分析',
                ranking: '产品关注度排名'
            },
            strategies: {
                title: '营销策略建议',
                subtitle: '针对每个用户群体的详细营销策略与行动建议'
            }
        },
        // 更新状态
        update: {
            updating: '正在更新聚类数据...',
            success: '聚类数据更新成功！',
            error: '自动更新失败。请运行Python脚本手动更新：python update_data.py'
        },
        // 通用
        common: {
            loading: '加载中...',
            noData: '暂无数据',
            error: '加载失败'
        },
        // 页脚
        footer: {
            help: '帮助文档',
            api: 'API文档',
            contact: '联系我们'
        },
        // 聚类相关
        cluster: {
            label: '聚类',
            select: '选择聚类',
            selectPlaceholder: '-- 选择聚类 --',
            size: '规模',
            segments: '个片段',
            users: '个用户',
            percentage: '占比',
            noStrategy: '暂无策略建议'
        },
        // 策略相关
        strategy: {
            marketing: '营销策略建议',
            product: '产品推荐',
            conversion: '转化优化建议',
            pricing: '价格策略建议',
            content: '内容策略建议',
            campaign: '差异化营销活动',
            noProductRecommendation: '需要进一步分析产品偏好',
            noContentStrategy: '暂无内容策略建议'
        },
        // 数据字段
        dataFields: {
            userScale: '用户规模',
            avgDuration: '平均浏览时长',
            avgInteractions: '平均交互次数',
            avgIntentScore: '平均意图强度',
            purchaseStage: '购买阶段',
            priceSensitivity: '价格敏感度',
            engagement: '参与度',
            productPreference: '产品偏好',
            concerns: '关注点',
            coreNeeds: '核心需求',
            behaviorPattern: '行为模式',
            intentUrgency: '意图紧迫度'
        },
        // 关键特征字段翻译
        keyCharacteristics: {
            '用户规模': 'User Scale',
            '平均浏览时长': 'Average Browsing Duration',
            '平均交互次数': 'Average Interactions',
            '平均意图强度': 'Average Intent Score',
            '购买阶段': 'Purchase Stage',
            '价格敏感度': 'Price Sensitivity',
            '参与度': 'Engagement',
            '产品偏好': 'Product Preference',
            '关注点': 'Key Concerns',
            '核心需求': 'Core Needs',
            '行为模式': 'Behavior Pattern',
            '意图紧迫度': 'Intent Urgency'
        },
        // 购买阶段
        stages: {
            browsing: '浏览阶段',
            comparison: '对比阶段',
            decision: '决策阶段',
            browsingDesc: '用户开始探索产品，了解基本信息',
            comparisonDesc: '用户比较不同选项，评估产品价值',
            decisionDesc: '用户准备购买，需要转化激励',
            personas: '个画像',
            segments: '个片段',
            percentage: '占比'
        },
        // 用户轨迹
        trajectory: {
            stageDistribution: '阶段分布',
            conversionPath: '转化路径',
            avgIntent: '平均意图强度'
        }
    },
    en: {
        // Navigation
        nav: {
            home: 'Home',
            overview: 'Overview',
            journey: 'Conversion',
            clusters: 'User Analysis',
            insights: 'Insights'
        },
        // Brand
        brand: {
            name: 'Intent Analytics',
            subtitle: 'User Intent Analysis Platform'
        },
        // Back button
        back: 'Back to Home',
        backTitle: 'Back to Intent Recognition Home',
        // Dashboard header
        header: {
            overview: 'Data Overview',
            overviewSubtitle: 'Real-time User Intent Analysis & Business Insights',
            selectDate: 'Select Date',
            exportReport: 'Export Report',
            autoUpdate: 'Auto Update:',
            manual: 'Manual',
            update3days: 'Every 3 Days',
            update1week: 'Weekly',
            update1month: 'Monthly',
            update3months: 'Every 3 Months',
            updateClusters: 'Update Clusters',
            updateClustersTitle: 'Update cluster data immediately',
            updating: 'Updating...',
            stats: {
                totalUsers: 'Unique Users',
                totalSegments: 'Intent Segments',
                totalClusters: 'User Clusters'
            }
        },
        // Home page
        home: {
            title: 'User Intent Clustering Analysis Platform',
            subtitle: 'Intelligent user segmentation based on business dimensions, driving precision marketing strategies',
            stats: {
                users: 'Unique Users',
                clusters: 'User Clusters',
                segments: 'Intent Segments'
            },
            methodology: {
                title: 'User Clustering Methodology',
                description: 'Intelligent clustering based on business dimensions, ensuring each cluster has clear business meaning and differentiated marketing strategies'
            },
            dimensions: {
                purchaseStage: {
                    title: 'Purchase Stage',
                    desc: 'Identify which stage of the purchase funnel users are in',
                    tags: ['Browsing', 'Comparison', 'Decision']
                },
                priceSensitivity: {
                    title: 'Price Sensitivity',
                    desc: 'Analyze users\' sensitivity to price',
                    tags: ['Price Sensitive', 'Moderate Price', 'Premium Value']
                },
                engagement: {
                    title: 'Engagement',
                    desc: 'Assess users\' browsing depth and engagement level',
                    tags: ['Quick Browser', 'Moderate Engagement', 'Deep Researcher']
                },
                productPreference: {
                    title: 'Product Preference',
                    desc: 'Identify product types and models users focus on',
                    tags: ['Z6 Preference', 'A1 Preference', 'F1 Preference', 'Multi-Product Comparison']
                },
                concerns: {
                    title: 'Key Concerns',
                    desc: 'Understand product features users care most about',
                    tags: ['Function-Oriented', 'Price-Oriented', 'Comfort-Oriented', 'Effectiveness-Oriented']
                },
                coreNeeds: {
                    title: 'Core Needs',
                    desc: 'Identify users\' core purchase motivations',
                    tags: ['Snoring Reduction', 'Neck Pain', 'Sleep Quality', 'Comprehensive Needs']
                }
            },
            benefits: {
                title: 'Clustering Value',
                description: 'Each cluster has clear business meaning and differentiated marketing strategies',
                items: {
                    clear: {
                        number: '01',
                        title: 'Clear Business Distinction',
                        desc: 'Clustering based on business dimensions, each cluster has clear labels and characteristics, easy to understand and apply'
                    },
                    strategy: {
                        number: '02',
                        title: 'Differentiated Marketing Strategies',
                        desc: 'Provide unique marketing recommendations for different clusters, ensuring targeted strategies for each group'
                    },
                    actionable: {
                        number: '03',
                        title: 'Actionable Recommendations',
                        desc: 'Provide specific marketing activities, content strategies, and conversion optimization suggestions that can be directly applied to business'
                    },
                    dataDriven: {
                        number: '04',
                        title: 'Data-Driven Decisions',
                        desc: 'Based on real user behavior data, ensuring the scientificity and effectiveness of marketing strategies'
                    }
                }
            },
            quickActions: {
                title: 'Quick Start',
                overview: {
                    title: 'View Data Overview',
                    desc: 'Understand overall user intent distribution and key metrics'
                },
                clusters: {
                    title: 'Analyze User Clusters',
                    desc: 'Deep dive into characteristics of each user group'
                },
                insights: {
                    title: 'Business Insights & Product Preferences',
                    desc: 'View marketing strategy recommendations and product preference analysis'
                }
            }
        },
        // Overview page
        overview: {
            title: 'Data Overview',
            subtitle: 'Overall user intent analysis overview and key metrics',
            charts: {
                clusterDistribution: 'User Cluster Distribution',
                purchaseStage: 'Purchase Stage Distribution',
                pricePreference: 'Price Preference Distribution',
                concerns: 'Key Concerns'
            },
            insights: {
                title: 'Key Insights',
                badge: 'Live Update'
            }
        },
        // Conversion analysis
        journey: {
            title: 'Conversion Analysis',
            subtitle: 'Explore user conversion paths and intent trajectories',
            tabs: {
                path: 'Conversion Path',
                trajectory: 'User Trajectory',
                cluster: 'User Clusters'
            },
            path: {
                title: 'User Conversion Path Visualization',
                subtitle: 'Explore the complete journey from browsing to decision, understand the distribution of different personas across conversion stages',
                funnelAnalysis: 'Conversion Funnel Analysis',
                funnelSubtitle: 'View user drop-off at different stages',
                funnelChart: 'User Conversion Funnel',
                flowChart: 'Conversion Path Flow',
                flowSubtitle: 'Explore the complete path from browsing to decision'
            },
            trajectory: {
                title: 'User Intent Trajectory Analysis',
                subtitle: 'View intent slices and corresponding cluster distribution for each user at different time periods',
                search: 'Search User ID...',
                filter: 'Filter:',
                allClusters: 'All Clusters',
                sort: 'Sort:',
                sortByTime: 'By Time',
                sortBySegments: 'By Segments',
                sortByClusters: 'By Clusters'
            },
            cluster: {
                title: 'User Cluster Analysis',
                subtitle: 'Deep dive into characteristics and behavior patterns of each user group',
                select: 'Select Cluster:',
                selectPlaceholder: '-- Select Cluster --'
            }
        },
        // User analysis
        clusters: {
            title: 'User Analysis',
            subtitle: 'Deep dive into user group characteristics and behavior patterns',
            portrait: {
                title: 'User Portrait Analysis',
                subtitle: 'Detailed user characteristics, behavior patterns and preference analysis'
            }
        },
        // Business insights
        insights: {
            title: 'Business Insights & Recommendations',
            subtitle: 'Marketing strategies, product preferences and action recommendations for each user group',
            products: {
                title: 'Product Preference Analysis',
                subtitle: 'Analysis of users\' attention and preferences for different products',
                ranking: 'Product Attention Ranking'
            },
            strategies: {
                title: 'Marketing Strategy Recommendations',
                subtitle: 'Detailed marketing strategies and action recommendations for each user group'
            }
        },
        // Update status
        update: {
            updating: 'Updating cluster data...',
            success: 'Cluster data updated successfully!',
            error: 'Auto update failed. Please run Python script manually: python update_data.py'
        },
        // Common
        common: {
            loading: 'Loading...',
            noData: 'No Data',
            error: 'Load Failed'
        },
        // Footer
        footer: {
            help: 'Help Documentation',
            api: 'API Documentation',
            contact: 'Contact Us'
        },
        // Cluster related
        cluster: {
            label: 'Cluster',
            select: 'Select Cluster',
            selectPlaceholder: '-- Select Cluster --',
            size: 'Size',
            segments: ' segments',
            users: ' users',
            percentage: 'Share',
            noStrategy: 'No strategy recommendation'
        },
        // Strategy related
        strategy: {
            marketing: 'Marketing Strategy Recommendations',
            product: 'Product Recommendations',
            conversion: 'Conversion Optimization Suggestions',
            pricing: 'Pricing Strategy Suggestions',
            content: 'Content Strategy Suggestions',
            campaign: 'Differentiated Marketing Campaigns',
            noProductRecommendation: 'Further product preference analysis needed',
            noContentStrategy: 'No content strategy recommendations'
        },
        // Data fields
        dataFields: {
            userScale: 'User Scale',
            avgDuration: 'Average Browsing Duration',
            avgInteractions: 'Average Interactions',
            avgIntentScore: 'Average Intent Score',
            purchaseStage: 'Purchase Stage',
            priceSensitivity: 'Price Sensitivity',
            engagement: 'Engagement',
            productPreference: 'Product Preference',
            concerns: 'Key Concerns',
            coreNeeds: 'Core Needs',
            behaviorPattern: 'Behavior Pattern',
            intentUrgency: 'Intent Urgency'
        },
        // Key characteristics field translations
        keyCharacteristics: {
            '用户规模': 'User Scale',
            '平均浏览时长': 'Average Browsing Duration',
            '平均交互次数': 'Average Interactions',
            '平均意图强度': 'Average Intent Score',
            '购买阶段': 'Purchase Stage',
            '价格敏感度': 'Price Sensitivity',
            '参与度': 'Engagement',
            '产品偏好': 'Product Preference',
            '关注点': 'Key Concerns',
            '核心需求': 'Core Needs',
            '行为模式': 'Behavior Pattern',
            '意图紧迫度': 'Intent Urgency'
        },
        // Purchase stages
        stages: {
            browsing: 'Browsing',
            comparison: 'Comparison',
            decision: 'Decision',
            browsingDesc: 'Users start exploring products and learning basic information',
            comparisonDesc: 'Users compare different options and evaluate product value',
            decisionDesc: 'Users are ready to purchase and need conversion incentives',
            personas: ' personas',
            segments: ' segments',
            percentage: 'Share'
        },
        // User trajectory
        trajectory: {
            stageDistribution: 'Stage Distribution',
            conversionPath: 'Conversion Path',
            avgIntent: 'Average Intent Score'
        },
        // Cluster names (all cluster names from data.js, emoji removed)
        clusterNames: {
            '快速浏览·低紧迫': 'Quick Browse·Low Urgency',
            '快速浏览·中紧迫': 'Quick Browse·Medium Urgency',
            '快速浏览·高紧迫': 'Quick Browse·High Urgency',
            '中等参与·低紧迫': 'Moderate Engagement·Low Urgency',
            '中等参与·中紧迫': 'Moderate Engagement·Medium Urgency',
            '中等参与·高紧迫': 'Moderate Engagement·High Urgency',
            '深度研究·低紧迫': 'Deep Research·Low Urgency',
            '深度研究·中紧迫': 'Deep Research·Medium Urgency',
            '深度研究·高紧迫': 'Deep Research·High Urgency',
            '单次浏览·低紧迫': 'Single Browse·Low Urgency',
            '单次浏览·中紧迫': 'Single Browse·Medium Urgency',
            '单次浏览·高紧迫': 'Single Browse·High Urgency',
            '高紧迫·深度研究': 'High Urgency·Deep Research',
            '高紧迫·快速浏览': 'High Urgency·Quick Browse',
            '高紧迫·中等参与': 'High Urgency·Moderate Engagement',
            '高紧迫·单次浏览': 'High Urgency·Single Browse',
            '低紧迫·快速浏览': 'Low Urgency·Quick Browse',
            '低紧迫·中等参与': 'Low Urgency·Moderate Engagement',
            '低紧迫·深度研究': 'Low Urgency·Deep Research',
            '低紧迫·单次浏览': 'Low Urgency·Single Browse',
            '中紧迫·快速浏览': 'Medium Urgency·Quick Browse',
            '中紧迫·中等参与': 'Medium Urgency·Moderate Engagement',
            '中紧迫·深度研究': 'Medium Urgency·Deep Research',
            '中紧迫·单次浏览': 'Medium Urgency·Single Browse'
        },
        // Strategy text translations
        strategyTexts: {
            // Marketing strategy
            '【教育引导】用户处于早期浏览阶段，需要教育性内容': '【Educational Guidance】Users are in early browsing stage and need educational content',
            '提供产品功能说明、使用场景、解决痛点的方式': 'Provide product feature descriptions, use cases, and pain point solutions',
            '突出品牌价值、专业认证、用户成功案例': 'Highlight brand value, professional certifications, and user success stories',
            // Product recommendations
            '【主推产品】H02偏好': '【Featured Product】H02 Preference',
            '【主推产品】F1偏好': '【Featured Product】F1 Preference',
            '【主推产品】Z6偏好': '【Featured Product】Z6 Preference',
            '【主推产品】A1偏好': '【Featured Product】A1 Preference',
            '【多产品比较】用户关注多个产品': '【Multi-Product Comparison】Users focus on multiple products',
            '提供产品对比工具、推荐算法': 'Provide product comparison tools and recommendation algorithms',
            '根据用户需求推荐最适合的产品': 'Recommend the most suitable products based on user needs',
            '重点展示H02偏好的核心功能和优势': 'Highlight core features and advantages of H02 preference',
            '提供H02偏好的详细页面、视频、用户评价': 'Provide detailed pages, videos, and user reviews for H02 preference',
            '重点展示F1偏好的核心功能和优势': 'Highlight core features and advantages of F1 preference',
            '提供F1偏好的详细页面、视频、用户评价': 'Provide detailed pages, videos, and user reviews for F1 preference',
            '重点展示Z6偏好的核心功能和优势': 'Highlight core features and advantages of Z6 preference',
            '提供Z6偏好的详细页面、视频、用户评价': 'Provide detailed pages, videos, and user reviews for Z6 preference',
            '重点展示A1偏好的核心功能和优势': 'Highlight core features and advantages of A1 preference',
            '提供A1偏好的详细页面、视频、用户评价': 'Provide detailed pages, videos, and user reviews for A1 preference',
            // Conversion optimization
            '优化首屏内容，快速抓住注意力': 'Optimize first-screen content to quickly capture attention',
            '提供视频教程、使用指南、FAQ': 'Provide video tutorials, usage guides, and FAQ',
            '使用大标题、醒目图片、简短文案': 'Use large headlines, eye-catching images, and concise copy',
            '减少页面跳转，提供一站式信息': 'Reduce page jumps and provide one-stop information',
            // Pricing strategy
            '【价值驱动】用户更关注产品价值和功能，价格敏感度低': '【Value-Driven】Users focus more on product value and features, with low price sensitivity',
            '强调产品品质、技术创新、用户体验': 'Emphasize product quality, technological innovation, and user experience',
            '提供高端产品线、定制化服务': 'Provide premium product lines and customized services',
            // Content strategy
            '【简洁内容】用户快速浏览，需要快速抓住注意力': '【Concise Content】Users browse quickly and need to quickly capture attention',
            '优化首屏内容，突出核心卖点和优惠信息': 'Optimize first-screen content, highlight core selling points and promotional information',
            // Campaign differentiation
            '【教育引导活动】\'了解产品赢好礼\'、\'注册送优惠券\'': '【Educational Campaign】\'Learn Products Win Prizes\', \'Register for Coupons\'',
            '【内容营销】产品知识竞赛、使用技巧分享、用户故事征集': '【Content Marketing】Product knowledge contests, usage tips sharing, user story collection',
            '【价值展示活动】\'品质体验\'、\'VIP服务\'、\'专属定制\'': '【Value Showcase Campaign】\'Quality Experience\', \'VIP Service\', \'Exclusive Customization\'',
            '【品牌活动】品牌故事、用户成功案例、专业认证展示': '【Brand Campaign】Brand stories, user success cases, professional certification display',
            '【快速转化活动】\'一键购买\'、\'快速了解\'、\'秒杀优惠\'': '【Quick Conversion Campaign】\'One-Click Purchase\', \'Quick Learn\', \'Flash Sale\'',
            '【简化流程】简化注册、快速结账、移动端优化': '【Simplified Process】Simplify registration, quick checkout, mobile optimization'
        }
    }
};

// 翻译聚类名称
function translateClusterName(name) {
    if (!name) return name;
    if (currentLanguage === 'zh') {
        return removeEmojiFromClusterName(name);
    } else {
        // 英文版本：先移除emoji，然后从i18n.en.clusterNames中获取翻译
        const cleanName = removeEmojiFromClusterName(name);
        // 直接从i18n.en.clusterNames中获取翻译
        const translation = i18n.en?.clusterNames?.[cleanName];
        return translation || cleanName;
    }
}

// 移除聚类名中的emoji（如果还没有定义）
if (typeof removeEmojiFromClusterName === 'undefined') {
    function removeEmojiFromClusterName(name) {
        if (!name) return name;
        // 移除所有emoji和variation selector（包括FE0F）
        return name.replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{FE00}-\u{FE0F}]|[\u{200D}]/gu, '').trim();
    }
    if (typeof window !== 'undefined') {
        window.removeEmojiFromClusterName = removeEmojiFromClusterName;
    }
}

// 翻译关键特征字段名
function translateKeyCharacteristicField(fieldName) {
    if (!fieldName) return fieldName;
    if (currentLanguage === 'zh') {
        return fieldName;
    } else {
        return i18n[currentLanguage]?.keyCharacteristics?.[fieldName] || fieldName;
    }
}

// 翻译策略文本
function translateStrategyText(text) {
    if (!text) return text;
    if (currentLanguage === 'zh') {
        return text;
    } else {
        // 从i18n.en.strategyTexts中获取翻译
        const translation = i18n.en?.strategyTexts?.[text];
        if (translation) {
            return translation;
        }
        // 如果没有找到完整匹配，尝试部分匹配和替换
        let translated = text;
        
        // 替换常见的中文标签
        const labelTranslations = {
            '【教育引导】': '【Educational Guidance】',
            '【主推产品】': '【Featured Product】',
            '【多产品比较】': '【Multi-Product Comparison】',
            '【价值驱动】': '【Value-Driven】',
            '【简洁内容】': '【Concise Content】',
            '【教育引导活动】': '【Educational Campaign】',
            '【内容营销】': '【Content Marketing】',
            '【价值展示活动】': '【Value Showcase Campaign】',
            '【品牌活动】': '【Brand Campaign】',
            '【快速转化活动】': '【Quick Conversion Campaign】',
            '【简化流程】': '【Simplified Process】'
        };
        
        Object.keys(labelTranslations).forEach(zh => {
            translated = translated.replace(new RegExp(zh, 'g'), labelTranslations[zh]);
        });
        
        // 替换产品偏好
        translated = translated.replace(/H02偏好/g, 'H02 Preference');
        translated = translated.replace(/F1偏好/g, 'F1 Preference');
        translated = translated.replace(/Z6偏好/g, 'Z6 Preference');
        translated = translated.replace(/A1偏好/g, 'A1 Preference');
        
        // 替换其他常见词汇
        const wordTranslations = {
            '用户处于早期浏览阶段，需要教育性内容': 'Users are in early browsing stage and need educational content',
            '提供产品功能说明、使用场景、解决痛点的方式': 'Provide product feature descriptions, use cases, and pain point solutions',
            '突出品牌价值、专业认证、用户成功案例': 'Highlight brand value, professional certifications, and user success stories',
            '用户关注多个产品': 'Users focus on multiple products',
            '提供产品对比工具、推荐算法': 'Provide product comparison tools and recommendation algorithms',
            '根据用户需求推荐最适合的产品': 'Recommend the most suitable products based on user needs',
            '重点展示': 'Highlight',
            '的核心功能和优势': ' core features and advantages',
            '提供': 'Provide',
            '的详细页面、视频、用户评价': ' detailed pages, videos, and user reviews',
            '优化首屏内容，快速抓住注意力': 'Optimize first-screen content to quickly capture attention',
            '提供视频教程、使用指南、FAQ': 'Provide video tutorials, usage guides, and FAQ',
            '使用大标题、醒目图片、简短文案': 'Use large headlines, eye-catching images, and concise copy',
            '减少页面跳转，提供一站式信息': 'Reduce page jumps and provide one-stop information',
            '用户更关注产品价值和功能，价格敏感度低': 'Users focus more on product value and features, with low price sensitivity',
            '强调产品品质、技术创新、用户体验': 'Emphasize product quality, technological innovation, and user experience',
            '提供高端产品线、定制化服务': 'Provide premium product lines and customized services',
            '用户快速浏览，需要快速抓住注意力': 'Users browse quickly and need to quickly capture attention',
            '优化首屏内容，突出核心卖点和优惠信息': 'Optimize first-screen content, highlight core selling points and promotional information',
            '\'了解产品赢好礼\'、\'注册送优惠券\'': '\'Learn Products Win Prizes\', \'Register for Coupons\'',
            '产品知识竞赛、使用技巧分享、用户故事征集': 'Product knowledge contests, usage tips sharing, user story collection',
            '\'品质体验\'、\'VIP服务\'、\'专属定制\'': '\'Quality Experience\', \'VIP Service\', \'Exclusive Customization\'',
            '品牌故事、用户成功案例、专业认证展示': 'Brand stories, user success cases, professional certification display',
            '\'一键购买\'、\'快速了解\'、\'秒杀优惠\'': '\'One-Click Purchase\', \'Quick Learn\', \'Flash Sale\'',
            '简化注册、快速结账、移动端优化': 'Simplify registration, quick checkout, mobile optimization'
        };
        
        Object.keys(wordTranslations).forEach(zh => {
            translated = translated.replace(new RegExp(zh.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), wordTranslations[zh]);
        });
        
        return translated !== text ? translated : text;
    }
}

// 翻译关键特征字符串（格式：字段名: 值）
function translateKeyCharacteristic(charString) {
    if (!charString) return charString;
    if (currentLanguage === 'zh') {
        return charString;
    }
    
    // 处理格式：字段名: 值
    const colonIndex = charString.indexOf(':');
    if (colonIndex === -1) {
        return charString;
    }
    
    const fieldName = charString.substring(0, colonIndex).trim();
    const value = charString.substring(colonIndex + 1).trim();
    const translatedField = translateKeyCharacteristicField(fieldName);
    
    // 翻译值中的中文（如"浏览阶段"、"高端价值型"等）
    let translatedValue = value;
    
    // 翻译购买阶段
    const stageTranslations = {
        '浏览阶段': t('stages.browsing'),
        '对比阶段': t('stages.comparison'),
        '决策阶段': t('stages.decision')
    };
    Object.keys(stageTranslations).forEach(zh => {
        translatedValue = translatedValue.replace(new RegExp(zh, 'g'), stageTranslations[zh]);
    });
    
    // 翻译其他常见值
    const valueTranslations = {
        '个独立用户': ' unique users',
        '个意图片段': ' intent segments',
        '秒': 's',
        '次': ' times',
        '瞬时浏览（单次交互）': 'Instant Browse (Single Interaction)',
        '瞬时浏览': 'Instant Browse',
        '单次交互': 'Single Interaction',
        '高端价值型': 'Premium Value',
        '中等价格型': 'Moderate Price',
        '价格敏感型': 'Price Sensitive',
        '快速浏览者': 'Quick Browser',
        '中等参与': 'Moderate Engagement',
        '深度研究者': 'Deep Researcher',
        '多产品比较': 'Multi-Product Comparison',
        '综合关注': 'Comprehensive Concerns',
        '综合需求': 'Comprehensive Needs',
        '功能导向': 'Function-Oriented',
        '价格导向': 'Price-Oriented',
        '舒适度导向': 'Comfort-Oriented',
        '有效性导向': 'Effectiveness-Oriented',
        '止鼾需求': 'Snoring Reduction',
        '颈部疼痛': 'Neck Pain',
        '睡眠质量': 'Sleep Quality',
        'H02偏好': 'H02 Preference',
        'F1偏好': 'F1 Preference',
        'Z6偏好': 'Z6 Preference',
        'A1偏好': 'A1 Preference',
        // Price preference types
        '预算导向': 'Budget-Oriented',
        '中端平衡': 'Mid-Range Balanced',
        '高端价值型': 'Premium Value',
        '价格导向': 'Price-Oriented',
        '价值导向': 'Value-Oriented'
    };
    // 按长度从长到短排序，先替换长的短语，避免部分替换问题
    const sortedKeys = Object.keys(valueTranslations).sort((a, b) => b.length - a.length);
    sortedKeys.forEach(zh => {
        translatedValue = translatedValue.replace(new RegExp(zh.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), valueTranslations[zh]);
    });
    
    return `${translatedField}: ${translatedValue}`;
}

// 确保全局可访问
if (typeof window !== 'undefined') {
    window.translateClusterName = translateClusterName;
    window.translateKeyCharacteristic = translateKeyCharacteristic;
    window.translateKeyCharacteristicField = translateKeyCharacteristicField;
    window.translateStrategyText = translateStrategyText;
}

// 当前语言（全局变量）
let currentLanguage = localStorage.getItem('dashboardLanguage') || 'zh';
// 确保全局可访问
if (typeof window !== 'undefined') {
    window.currentLanguage = currentLanguage;
}

// 获取翻译文本
function t(key) {
    const keys = key.split('.');
    let value = i18n[currentLanguage];
    for (const k of keys) {
        if (value === null || value === undefined) {
            return key;
        }
        value = value[k];
    }
    // 如果值是数组，返回数组本身（让调用者处理索引）
    // 如果值是字符串或其他，直接返回
    return value !== undefined && value !== null ? value : key;
}

// 切换语言
function switchLanguage(lang) {
    if (!i18n[lang]) {
        console.error('Invalid language:', lang);
        return;
    }
    console.log('Switching to language:', lang);
    currentLanguage = lang;
    // 确保全局可访问
    if (typeof window !== 'undefined') {
        window.currentLanguage = lang;
    }
    localStorage.setItem('dashboardLanguage', lang);
    
    // 更新语言显示（如果存在）
    const currentLangSpan = document.getElementById('currentLang');
    if (currentLangSpan) {
        currentLangSpan.textContent = lang === 'zh' ? '中文' : 'English';
    }
    
    updatePageLanguage();
}

// 确保全局可访问
if (typeof window !== 'undefined') {
    window.switchLanguage = switchLanguage;
    window.updatePageLanguage = updatePageLanguage;
    window.t = t;
}

// 更新页面语言
function updatePageLanguage() {
    // 添加淡出效果
    const mainContent = document.querySelector('.dashboard-main');
    if (mainContent) {
        mainContent.style.transition = 'opacity 0.15s ease';
        mainContent.style.opacity = '0.6';
    }
    
    // 更新导航栏和所有静态文本
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        let text = t(key);
        
        // 处理数组索引（如 home.dimensions.purchaseStage.tags.0）
        if (text === key || (typeof text === 'object' && !Array.isArray(text) && text !== null)) {
            const parts = key.split('.');
            if (parts.length > 1) {
                const lastPart = parts[parts.length - 1];
                const index = parseInt(lastPart);
                if (!isNaN(index) && index >= 0) {
                    // 尝试获取数组元素
                    const arrayKey = parts.slice(0, -1).join('.');
                    const arrayValue = t(arrayKey);
                    if (Array.isArray(arrayValue) && arrayValue[index] !== undefined) {
                        text = arrayValue[index];
                    }
                }
            }
        }
        
        // 确保text是字符串
        if (typeof text !== 'string') {
            if (Array.isArray(text)) {
                // 如果是数组，取第一个元素
                text = text[0] || key;
            } else if (text === null || text === undefined) {
                text = key;
            } else {
                text = String(text);
            }
        }
        
        if (el.tagName === 'INPUT' && el.type === 'text') {
            el.placeholder = text;
        } else if (el.tagName === 'OPTION') {
            el.textContent = text;
        } else {
            el.textContent = text;
        }
    });
    
    // 更新带有 data-i18n-placeholder 属性的 input 元素
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        el.placeholder = t(key);
    });
    
    // 更新title属性
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        el.title = t(key);
    });
    
    // 更新select选项的文本
    document.querySelectorAll('select option').forEach(option => {
        const key = option.getAttribute('data-i18n');
        if (key) {
            option.textContent = t(key);
        }
    });
    
    // 更新页面标题（如果有）
    const headerTitle = document.querySelector('#dashboardHeader h1');
    if (headerTitle && headerTitle.hasAttribute('data-i18n')) {
        const key = headerTitle.getAttribute('data-i18n');
        headerTitle.textContent = t(key);
    }
    
    // 更新动态内容
    updateDynamicContent();
    
    // 恢复淡入效果
    setTimeout(() => {
        if (mainContent) {
            mainContent.style.opacity = '1';
        }
    }, 150);
}

// 更新动态生成的内容
function updateDynamicContent() {
    // 这里会在dashboard.js中调用，更新所有动态生成的内容
    if (typeof loadTabContent === 'function') {
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab) {
            const tabName = activeTab.id;
            // 使用setTimeout确保DOM更新完成
            setTimeout(() => {
                // 重新加载当前标签页内容，这样所有动态生成的内容都会使用新语言
                loadTabContent(tabName);
            }, 200);
        }
    } else {
        console.warn('loadTabContent function not found');
    }
    
    // 额外更新一些可能遗漏的动态内容
    // 更新图表标题（如果存在）
    if (typeof Chart !== 'undefined') {
        Chart.helpers.each(Chart.instances, function(instance) {
            if (instance.config && instance.config.options && instance.config.options.plugins) {
                if (instance.config.options.plugins.title) {
                    const titleKey = instance.config.data?.i18nTitleKey;
                    if (titleKey) {
                        instance.config.options.plugins.title.text = t(titleKey);
                        instance.update();
                    }
                }
            }
        });
    }
}


