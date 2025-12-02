// 用户意图分析数据
// 自动生成，请勿手动编辑

// 业务洞察数据
const businessInsights = [
  {
    "cluster_id": "0",
    "cluster_name": "Medium Urgency",
    "user_segment_name": "Medium Urgency",
    "full_label": "Medium Urgency · Task/Activity Oriented",
    "key_characteristics": {
      "user_count": 2,
      "segment_count": 4,
      "avg_duration_minutes": 3.3875,
      "avg_interactions": 19.75,
      "avg_intent_score": 0.5,
      "urgency": "Medium Urgency",
      "main_activity": "Task/Activity Oriented",
      "kyc_status": "Not Started",
      "transaction_status": "In Progress",
      "first_order_completed": "Yes"
    },
    "marketing_strategy": [
      "[Repurchase Boost] Recommend related services based on first order, push personalized repurchase incentives at key time points (3 days, 7 days, 15 days, 30 days)",
      "Build repurchase reward system: repurchase coupons, double points, membership upgrade"
    ],
    "product_recommendations": [
      "Recommend upgraded services, combo packages, limited-time new products"
    ],
    "conversion_optimization": [
      "Push repurchase coupons within 7 days immediately after first order completion, provide one-click repurchase function",
      "Build repurchase points system, identify repurchase intent based on browsing behavior and push offers"
    ],
    "pricing_strategy": [],
    "content_strategy": [
      "Display first order usage effects and user reviews, push related service introductions and repurchase promotional activities"
    ],
    "campaign_differentiation": [
      "Repurchase coupons, 3/7/30-day limited-time discounts after first order, personalized recommendations based on first order"
    ]
  },
  {
    "cluster_id": "1",
    "cluster_name": "Activation Stage · Medium Urgency",
    "user_segment_name": "Activation Stage · Medium Urgency",
    "full_label": "Activation Stage · Medium Urgency · Activation Oriented",
    "key_characteristics": {
      "user_count": 1,
      "segment_count": 1,
      "avg_duration_minutes": 14.75,
      "avg_interactions": 142.0,
      "avg_intent_score": 0.5,
      "behavior": "Activation Stage",
      "urgency": "Medium Urgency",
      "main_activity": "Activation Oriented",
      "kyc_status": "Not Started",
      "transaction_status": "Not Started",
      "first_order_completed": "No"
    },
    "marketing_strategy": [
      "[Promote First Order] Provide new user exclusive offers (first order discount, no handling fee, new user gift package), simplify registration and KYC process",
      "Build trust mechanism: display platform security, user reviews, success cases, fund protection"
    ],
    "product_recommendations": [
      "Recommend low-threshold high-value first order services, first order discount packages, popular services, limited-time new products"
    ],
    "conversion_optimization": [
      "Prominently display first order offers on homepage, simplify process with auto-recognition support, provide new user guidance and limited-time offer countdown"
    ],
    "pricing_strategy": [],
    "content_strategy": [
      "Display first order offers and post-completion benefits, provide operation guides, share first order success cases"
    ],
    "campaign_differentiation": [
      "New user registration rewards, first order exclusive offers, no handling fee fast track, new user task guidance"
    ]
  },
  {
    "cluster_id": "2",
    "cluster_name": "Medium Urgency",
    "user_segment_name": "Medium Urgency",
    "full_label": "Medium Urgency · KYC Oriented",
    "key_characteristics": {
      "user_count": 1,
      "segment_count": 1,
      "avg_duration_minutes": 0.0,
      "avg_interactions": 1.0,
      "avg_intent_score": 0.5,
      "urgency": "Medium Urgency",
      "main_activity": "KYC Oriented",
      "kyc_status": "Started",
      "transaction_status": "In Progress",
      "first_order_completed": "Yes"
    },
    "marketing_strategy": [
      "[Repurchase Boost] Recommend related services based on first order, push personalized repurchase incentives at key time points (3 days, 7 days, 15 days, 30 days)",
      "Build repurchase reward system: repurchase coupons, double points, membership upgrade",
      "[KYC In Progress] Proactively identify bottlenecks, provide targeted assistance and KYC exclusive customer service channel"
    ],
    "product_recommendations": [
      "Recommend upgraded services, combo packages, limited-time new products"
    ],
    "conversion_optimization": [
      "Push repurchase coupons within 7 days immediately after first order completion, provide one-click repurchase function",
      "Build repurchase points system, identify repurchase intent based on browsing behavior and push offers",
      "Optimize KYC process supporting multiple verification methods, send progress reminders, set completion rewards"
    ],
    "pricing_strategy": [],
    "content_strategy": [
      "Display first order usage effects and user reviews, push related service introductions and repurchase promotional activities",
      "Provide KYC process instructions and FAQ library, set up exclusive customer service for quick response"
    ],
    "campaign_differentiation": [
      "Repurchase coupons, 3/7/30-day limited-time discounts after first order, personalized recommendations based on first order"
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
    "cluster_name": "Medium Urgency",
    "full_label": "Medium Urgency · KYC Oriented",
    "characteristics": {
      "urgency": "Medium Urgency",
      "main_activity": "KYC Oriented",
      "kyc_status": "Started",
      "transaction_status": "In Progress",
      "first_order_completed": "Yes"
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
    "cluster_name": "Medium Urgency",
    "full_label": "Medium Urgency · Task/Activity Oriented",
    "characteristics": {
      "urgency": "Medium Urgency",
      "main_activity": "Task/Activity Oriented",
      "kyc_status": "Not Started",
      "transaction_status": "In Progress",
      "first_order_completed": "Yes"
    },
    "intent_profile": {
      "core_interests": {},
      "price_range": {
        "高端价值型": 4
      },
      "purchase_stage": {
        "Browsing Stage": 4
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
    "cluster_name": "Activation Stage · Medium Urgency",
    "full_label": "Activation Stage · Medium Urgency · Activation Oriented",
    "characteristics": {
      "behavior": "Activation Stage",
      "urgency": "Medium Urgency",
      "main_activity": "Activation Oriented",
      "kyc_status": "Not Started",
      "transaction_status": "Not Started",
      "first_order_completed": "No"
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
      "Medium Urgency": 5,
      "Activation Stage · Medium Urgency": 1
    },
    "stages": {
      "Browsing Stage": 6
    },
    "portrait_stage": {
      "Medium Urgency": {
        "Browsing Stage": 5
      },
      "Activation Stage · Medium Urgency": {
        "Browsing Stage": 1
      }
    },
    "hourly": {
      "2025-10-10 09:00": {
        "portraits": {
          "Medium Urgency": 2
        },
        "stages": {
          "Browsing Stage": 2
        },
        "portrait_stage": {
          "Medium Urgency": {
            "Browsing Stage": 2
          }
        }
      },
      "2025-10-10 11:00": {
        "portraits": {
          "Medium Urgency": 2
        },
        "stages": {
          "Browsing Stage": 2
        },
        "portrait_stage": {
          "Medium Urgency": {
            "Browsing Stage": 2
          }
        }
      },
      "2025-10-10 19:00": {
        "portraits": {
          "Activation Stage · Medium Urgency": 1,
          "Medium Urgency": 1
        },
        "stages": {
          "Browsing Stage": 2
        },
        "portrait_stage": {
          "Activation Stage · Medium Urgency": {
            "Browsing Stage": 1
          },
          "Medium Urgency": {
            "Browsing Stage": 1
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
        "cluster_name": "Medium Urgency",
        "full_label": "Medium Urgency · KYC Oriented",
        "purchase_stage": "Browsing Stage",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "KYC Oriented",
        "kyc_status": "Started",
        "transaction_status": "In Progress",
        "first_order_completed": "Yes",
        "urgency": "Medium Urgency"
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
        "cluster_name": "Medium Urgency",
        "full_label": "Medium Urgency · Task/Activity Oriented",
        "purchase_stage": "Browsing Stage",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "Task/Activity Oriented",
        "kyc_status": "Not Started",
        "transaction_status": "In Progress",
        "first_order_completed": "Yes",
        "urgency": "Medium Urgency"
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
        "cluster_name": "Medium Urgency",
        "full_label": "Medium Urgency · Task/Activity Oriented",
        "purchase_stage": "Browsing Stage",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "Task/Activity Oriented",
        "behavior": "Repurchase · Coupon Oriented",
        "kyc_status": "Not Started",
        "transaction_status": "In Progress",
        "first_order_completed": "Yes",
        "urgency": "Medium Urgency"
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
        "cluster_name": "Medium Urgency",
        "full_label": "Medium Urgency · Task/Activity Oriented",
        "purchase_stage": "Browsing Stage",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "Task/Activity Oriented",
        "behavior": "Repurchase · Payment Oriented",
        "kyc_status": "Not Started",
        "transaction_status": "In Progress",
        "first_order_completed": "Yes",
        "urgency": "Medium Urgency"
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
        "cluster_name": "Activation Stage · Medium Urgency",
        "full_label": "Activation Stage · Medium Urgency · Activation Oriented",
        "purchase_stage": "Browsing Stage",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "Activation Oriented",
        "behavior": "Activation Stage",
        "kyc_status": "Not Started",
        "transaction_status": "Not Started",
        "first_order_completed": "No",
        "urgency": "Medium Urgency"
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
        "cluster_name": "Medium Urgency",
        "full_label": "Medium Urgency · Task/Activity Oriented",
        "purchase_stage": "Browsing Stage",
        "intent_score": 0.5,
        "price_sensitivity": 2,
        "engagement_level": 0,
        "main_activity": "Task/Activity Oriented",
        "behavior": "Payment Oriented",
        "kyc_status": "Not Started",
        "transaction_status": "Not Started",
        "first_order_completed": "No",
        "urgency": "Medium Urgency"
      }
    ]
  }
];

// 数据加载完成
console.log("YUP数据加载完成:", stats);
