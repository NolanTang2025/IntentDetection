// 用户意图分析数据
// 自动生成，请勿手动编辑

// 业务洞察数据
const businessInsights = [
  {
    "cluster_id": "0",
    "cluster_name": "首单后活跃·中紧迫",
    "user_segment_name": "首单后活跃·中紧迫",
    "full_label": "首单后活跃·中紧迫·任务/活动导向",
    "key_characteristics": {
      "user_count": 2,
      "segment_count": 4,
      "avg_duration_minutes": 3.3875,
      "avg_interactions": 19.75,
      "avg_intent_score": 0.5,
      "behavior": "首单后活跃",
      "urgency": "中紧迫",
      "main_activity": "任务/活动导向",
      "kyc_status": "未开始",
      "transaction_status": "进行中",
      "first_order_completed": "是",
      "post_first_order": "是"
    },
    "marketing_strategy": [
      "【复购提升】基于首单推荐相关服务，在关键时间节点（3天、7天、15天、30天）推送个性化复购激励",
      "建立复购奖励体系：复购优惠券、积分加倍、会员升级"
    ],
    "product_recommendations": [
      "推荐升级版服务、组合套餐、限时新品"
    ],
    "conversion_optimization": [
      "首单完成后立即推送7天内复购优惠券，提供一键复购功能",
      "建立复购积分系统，根据浏览行为识别复购意向并推送优惠"
    ],
    "pricing_strategy": [],
    "content_strategy": [
      "展示首单使用效果和用户评价，推送相关服务介绍和复购优惠活动"
    ],
    "campaign_differentiation": [
      "复购优惠券、首单后3/7/30天限时折扣、基于首单的个性化推荐"
    ]
  },
  {
    "cluster_id": "1",
    "cluster_name": "激活阶段·中紧迫",
    "user_segment_name": "激活阶段·中紧迫",
    "full_label": "激活阶段·中紧迫·激活导向",
    "key_characteristics": {
      "user_count": 1,
      "segment_count": 1,
      "avg_duration_minutes": 14.75,
      "avg_interactions": 142.0,
      "avg_intent_score": 0.5,
      "behavior": "激活阶段",
      "urgency": "中紧迫",
      "main_activity": "激活导向",
      "kyc_status": "未开始",
      "transaction_status": "未开始",
      "first_order_completed": "否",
      "post_first_order": "否"
    },
    "marketing_strategy": [
      "【促进首单】提供新用户专享优惠（首单折扣、免手续费、新用户礼包），简化注册和KYC流程",
      "建立信任机制：展示平台安全性、用户评价、成功案例、资金保障"
    ],
    "product_recommendations": [
      "推荐低门槛高价值首单服务、首单优惠套餐、热门服务、限时新品"
    ],
    "conversion_optimization": [
      "在首页显著展示首单优惠，简化流程支持自动识别，提供新手引导和限时优惠倒计时"
    ],
    "pricing_strategy": [],
    "content_strategy": [
      "展示首单优惠和完成后的权益，提供操作指南，分享首单成功案例"
    ],
    "campaign_differentiation": [
      "新用户注册奖励、首单专享优惠、免手续费快速通道、新手任务引导"
    ]
  },
  {
    "cluster_id": "2",
    "cluster_name": "首单后活跃·中紧迫",
    "user_segment_name": "首单后活跃·中紧迫",
    "full_label": "首单后活跃·中紧迫·KYC导向",
    "key_characteristics": {
      "user_count": 1,
      "segment_count": 1,
      "avg_duration_minutes": 0.0,
      "avg_interactions": 1.0,
      "avg_intent_score": 0.5,
      "behavior": "首单后活跃",
      "urgency": "中紧迫",
      "main_activity": "KYC导向",
      "kyc_status": "已开始",
      "transaction_status": "进行中",
      "first_order_completed": "是",
      "post_first_order": "是"
    },
    "marketing_strategy": [
      "【复购提升】基于首单推荐相关服务，在关键时间节点（3天、7天、15天、30天）推送个性化复购激励",
      "建立复购奖励体系：复购优惠券、积分加倍、会员升级",
      "【KYC进行中】主动识别卡点，提供针对性帮助和KYC专属客服通道"
    ],
    "product_recommendations": [
      "推荐升级版服务、组合套餐、限时新品"
    ],
    "conversion_optimization": [
      "首单完成后立即推送7天内复购优惠券，提供一键复购功能",
      "建立复购积分系统，根据浏览行为识别复购意向并推送优惠",
      "优化KYC流程支持多种验证方式，发送进度提醒，设置完成奖励"
    ],
    "pricing_strategy": [],
    "content_strategy": [
      "展示首单使用效果和用户评价，推送相关服务介绍和复购优惠活动",
      "提供KYC流程说明和常见问题库，设置专属客服快速响应"
    ],
    "campaign_differentiation": [
      "复购优惠券、首单后3/7/30天限时折扣、基于首单的个性化推荐"
    ]
  }
];

// 用户画像数据
const userPortraits = [
  {
    "cluster_id": "2",
    "segment_count": 1,
    "unique_users": 1,
    "avg_duration_seconds": 0,
    "avg_record_count": 1.0,
    "avg_intent_score": 0.5,
    "cluster_name": "首单后活跃·中紧迫",
    "full_label": "首单后活跃·中紧迫·KYC导向",
    "characteristics": {
      "behavior": "首单后活跃",
      "urgency": "中紧迫",
      "main_activity": "KYC导向",
      "kyc_status": "已开始",
      "transaction_status": "进行中",
      "first_order_completed": "是",
      "post_first_order": "是"
    },
    "intent_profile": {
      "core_interests": {},
      "price_range": {
        "高端价值型": 1
      },
      "purchase_stage": {
        "浏览阶段": 1
      },
      "main_appeal": {
        "综合需求": 1
      },
      "concerns": {
        "综合关注": 1
      }
    },
    "product_preferences": {
      "多产品比较": 1
    },
    "behavior_patterns": {
      "engagement_level": "快速浏览者"
    },
    "keywords": [
      [
        "话费充值",
        60
      ],
      [
        "优惠券使用",
        60
      ],
      [
        "任务完成",
        60
      ],
      [
        "首次交易",
        60
      ],
      [
        "额度使用",
        60
      ],
      [
        "激活后行为",
        60
      ],
      [
        "完成首笔交易",
        60
      ]
    ]
  },
  {
    "cluster_id": "0",
    "segment_count": 4,
    "unique_users": 2,
    "avg_duration_seconds": 203.25,
    "avg_record_count": 19.75,
    "avg_intent_score": 0.5,
    "cluster_name": "首单后活跃·中紧迫",
    "full_label": "首单后活跃·中紧迫·任务/活动导向",
    "characteristics": {
      "behavior": "首单后活跃",
      "urgency": "中紧迫",
      "main_activity": "任务/活动导向",
      "kyc_status": "未开始",
      "transaction_status": "进行中",
      "first_order_completed": "是",
      "post_first_order": "是"
    },
    "intent_profile": {
      "core_interests": {},
      "price_range": {
        "高端价值型": 4
      },
      "purchase_stage": {
        "浏览阶段": 4
      },
      "main_appeal": {
        "综合需求": 4
      },
      "concerns": {
        "综合关注": 4
      }
    },
    "product_preferences": {
      "多产品比较": 4
    },
    "behavior_patterns": {
      "engagement_level": "快速浏览者"
    },
    "keywords": [
      [
        "话费充值",
        60
      ],
      [
        "优惠券使用",
        60
      ],
      [
        "任务完成",
        60
      ],
      [
        "首次交易",
        60
      ],
      [
        "额度使用",
        60
      ],
      [
        "激活后行为",
        60
      ],
      [
        "完成首笔交易",
        60
      ]
    ]
  },
  {
    "cluster_id": "1",
    "segment_count": 1,
    "unique_users": 1,
    "avg_duration_seconds": 885.0,
    "avg_record_count": 142.0,
    "avg_intent_score": 0.5,
    "cluster_name": "激活阶段·中紧迫",
    "full_label": "激活阶段·中紧迫·激活导向",
    "characteristics": {
      "behavior": "激活阶段",
      "urgency": "中紧迫",
      "main_activity": "激活导向",
      "kyc_status": "未开始",
      "transaction_status": "未开始",
      "first_order_completed": "否",
      "post_first_order": "否"
    },
    "intent_profile": {
      "core_interests": {},
      "price_range": {
        "高端价值型": 1
      },
      "purchase_stage": {
        "浏览阶段": 1
      },
      "main_appeal": {
        "综合需求": 1
      },
      "concerns": {
        "综合关注": 1
      }
    },
    "product_preferences": {
      "多产品比较": 1
    },
    "behavior_patterns": {
      "engagement_level": "快速浏览者"
    },
    "keywords": [
      [
        "话费充值",
        60
      ],
      [
        "优惠券使用",
        60
      ],
      [
        "任务完成",
        60
      ],
      [
        "首次交易",
        60
      ],
      [
        "额度使用",
        60
      ],
      [
        "激活后行为",
        60
      ],
      [
        "完成首笔交易",
        60
      ]
    ]
  }
];

// 统计数据
const stats = {
  "totalUsers": 2,
  "totalSegments": 6,
  "totalClusters": 3,
  "avgDuration": 339.6,
  "avgInteractions": 37.0
};

// 时间序列数据
const timeSeries = [
  {
    "date": "2025-10-10",
    "portraits": {
      "首单后活跃·中紧迫": 5,
      "激活阶段·中紧迫": 1
    },
    "stages": {
      "浏览阶段": 6
    },
    "portrait_stage": {
      "首单后活跃·中紧迫": {
        "浏览阶段": 5
      },
      "激活阶段·中紧迫": {
        "浏览阶段": 1
      }
    },
    "hourly": {
      "2025-10-10 09:00": {
        "portraits": {
          "首单后活跃·中紧迫": 2
        },
        "stages": {
          "浏览阶段": 2
        },
        "portrait_stage": {
          "首单后活跃·中紧迫": {
            "浏览阶段": 2
          }
        }
      },
      "2025-10-10 11:00": {
        "portraits": {
          "首单后活跃·中紧迫": 2
        },
        "stages": {
          "浏览阶段": 2
        },
        "portrait_stage": {
          "首单后活跃·中紧迫": {
            "浏览阶段": 2
          }
        }
      },
      "2025-10-10 19:00": {
        "portraits": {
          "激活阶段·中紧迫": 1,
          "首单后活跃·中紧迫": 1
        },
        "stages": {
          "浏览阶段": 2
        },
        "portrait_stage": {
          "激活阶段·中紧迫": {
            "浏览阶段": 1
          },
          "首单后活跃·中紧迫": {
            "浏览阶段": 1
          }
        }
      }
    }
  }
];

// 用户轨迹数据
const userTrajectories = [
  {
    "user_id": "011c40cc5105419293c6a52635546b4a",
    "segment_count": 4,
    "unique_clusters": 2,
    "cluster_ids": [
      "0",
      "2"
    ],
    "total_duration": 714.0,
    "total_records": 67,
    "segments": [
      {
        "segment_id": "011c40cc5105419293c6a52635546b4a_seg_0",
        "segment_index": 0,
        "start_time": "2025-10-10T09:47:43Z",
        "end_time": "2025-10-10T09:47:43Z",
        "duration_seconds": 0.0,
        "duration_minutes": 0.0,
        "record_count": 1,
        "cluster_id": "2",
        "cluster_name": "首单后活跃·中紧迫",
        "full_label": "首单后活跃·中紧迫·KYC导向",
        "purchase_stage": "浏览阶段",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "KYC导向",
        "behavior": "首单后活跃",
        "kyc_status": "已开始",
        "transaction_status": "进行中",
        "first_order_completed": "是",
        "post_first_order": "是",
        "urgency": "中紧迫"
      },
      {
        "segment_id": "011c40cc5105419293c6a52635546b4a_seg_1",
        "segment_index": 1,
        "start_time": "2025-10-10T09:47:45Z",
        "end_time": "2025-10-10T09:48:56Z",
        "duration_seconds": 71.0,
        "duration_minutes": 1.1833333333333333,
        "record_count": 20,
        "cluster_id": "0",
        "cluster_name": "首单后活跃·中紧迫",
        "full_label": "首单后活跃·中紧迫·任务/活动导向",
        "purchase_stage": "浏览阶段",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "任务/活动导向",
        "behavior": "首单后活跃",
        "kyc_status": "未开始",
        "transaction_status": "进行中",
        "first_order_completed": "是",
        "post_first_order": "是",
        "urgency": "中紧迫"
      },
      {
        "segment_id": "011c40cc5105419293c6a52635546b4a_seg_2",
        "segment_index": 2,
        "start_time": "2025-10-10T11:21:35Z",
        "end_time": "2025-10-10T11:30:08Z",
        "duration_seconds": 513.0,
        "duration_minutes": 8.55,
        "record_count": 21,
        "cluster_id": "0",
        "cluster_name": "首单后活跃·中紧迫",
        "full_label": "首单后活跃·中紧迫·任务/活动导向",
        "purchase_stage": "浏览阶段",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "任务/活动导向",
        "behavior": "复购·优惠券导向",
        "kyc_status": "未开始",
        "transaction_status": "进行中",
        "first_order_completed": "是",
        "post_first_order": "是",
        "urgency": "中紧迫"
      },
      {
        "segment_id": "011c40cc5105419293c6a52635546b4a_seg_3",
        "segment_index": 3,
        "start_time": "2025-10-10T11:43:58Z",
        "end_time": "2025-10-10T11:46:08Z",
        "duration_seconds": 130.0,
        "duration_minutes": 2.1666666666666665,
        "record_count": 25,
        "cluster_id": "0",
        "cluster_name": "首单后活跃·中紧迫",
        "full_label": "首单后活跃·中紧迫·任务/活动导向",
        "purchase_stage": "浏览阶段",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "任务/活动导向",
        "behavior": "复购·支付导向",
        "kyc_status": "未开始",
        "transaction_status": "进行中",
        "first_order_completed": "是",
        "post_first_order": "是",
        "urgency": "中紧迫"
      }
    ]
  },
  {
    "user_id": "01ef6ac2baf84efe9a762f78aeecbd44",
    "segment_count": 2,
    "unique_clusters": 2,
    "cluster_ids": [
      "0",
      "1"
    ],
    "total_duration": 984.0,
    "total_records": 155,
    "segments": [
      {
        "segment_id": "01ef6ac2baf84efe9a762f78aeecbd44_seg_0",
        "segment_index": 0,
        "start_time": "2025-10-10T19:22:09Z",
        "end_time": "2025-10-10T19:36:54Z",
        "duration_seconds": 885.0,
        "duration_minutes": 14.75,
        "record_count": 142,
        "cluster_id": "1",
        "cluster_name": "激活阶段·中紧迫",
        "full_label": "激活阶段·中紧迫·激活导向",
        "purchase_stage": "浏览阶段",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "激活导向",
        "behavior": "激活阶段",
        "kyc_status": "未开始",
        "transaction_status": "未开始",
        "first_order_completed": "否",
        "post_first_order": "否",
        "urgency": "中紧迫"
      },
      {
        "segment_id": "01ef6ac2baf84efe9a762f78aeecbd44_seg_1",
        "segment_index": 1,
        "start_time": "2025-10-10T19:49:20Z",
        "end_time": "2025-10-10T19:50:59Z",
        "duration_seconds": 99.0,
        "duration_minutes": 1.65,
        "record_count": 13,
        "cluster_id": "0",
        "cluster_name": "首单后活跃·中紧迫",
        "full_label": "首单后活跃·中紧迫·任务/活动导向",
        "purchase_stage": "浏览阶段",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "任务/活动导向",
        "behavior": "支付导向",
        "kyc_status": "未开始",
        "transaction_status": "未开始",
        "first_order_completed": "否",
        "post_first_order": "否",
        "urgency": "中紧迫"
      }
    ]
  }
];

// 数据加载完成
console.log("YUP数据加载完成:", stats);
