#!/usr/bin/env python3
"""
聚类分析和前端同步脚本
1. 分析每个聚类的特征（购买阶段、价格偏好、用户喜好等）
2. 生成聚类名称（如果还没有）
3. 同步到前端数据文件
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict, Counter

import google.generativeai as genai

# 配置 Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def extract_text_from_output(output: str) -> Dict[str, Any]:
    """从output字段中提取结构化信息"""
    if not output or output.strip() == "":
        return {"text": "", "stage": "", "concerns": [], "use_case": "", "price_range": "", "engagement": "", "customer_portrait": ""}

    result = {
        "text": "",
        "stage": "",
        "concerns": [],
        "use_case": "",
        "price_range": "",
        "engagement": "",
        "customer_portrait": "",
        "core_interests": [],
        "key_attributes": [],
        "main_appeal": ""
    }

    try:
        cleaned = output.strip()
        
        # 如果output以引号开头，尝试移除它（可能是不完整的JSON字符串）
        if cleaned.startswith('"'):
            # 尝试解析为JSON字符串
            try:
                # 如果结尾也有引号，尝试完整解析
                if cleaned.endswith('"'):
                    cleaned = json.loads(cleaned)
                else:
                    # 如果结尾没有引号，手动移除开头的引号
                    cleaned = cleaned[1:]
            except json.JSONDecodeError:
                # 如果解析失败，手动移除引号
                if cleaned.endswith('"'):
                    cleaned = cleaned[1:-1]
                else:
                    cleaned = cleaned[1:]
        
        # 确保cleaned是字符串
        if not isinstance(cleaned, str):
            cleaned = str(cleaned)
        
        # 如果cleaned包含转义的\n（字符串字面量），需要处理
        # 检查是否包含字面量\n（不是实际的换行符）
        if '\\n' in cleaned and '\n' not in cleaned[:100]:
            # 手动替换转义字符
            cleaned = cleaned.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        
        # 移除代码块标记
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            first_newline = cleaned.find("\n")
            if first_newline != -1:
                cleaned = cleaned[first_newline + 1 :]
        
        if cleaned.rstrip().endswith("```"):
            cleaned = cleaned.rstrip()[:-3].rstrip()
        
        cleaned = cleaned.strip()

        # 解析JSON内容
        data = json.loads(cleaned)

        if isinstance(data, dict) and "intent" in data:
            intent = data["intent"]

            # 核心兴趣
            if "core_interests" in intent and intent["core_interests"]:
                result["core_interests"] = intent["core_interests"]

            # 产品关注点
            if "product_focus" in intent:
                pf = intent["product_focus"]
                if "key_attributes" in pf and pf["key_attributes"]:
                    result["key_attributes"] = pf["key_attributes"]
                if "price_range" in pf:
                    result["price_range"] = pf["price_range"]
                if "main_appeal" in pf:
                    result["main_appeal"] = pf["main_appeal"]

            # 购买信号
            if "purchase_signals" in intent:
                ps = intent["purchase_signals"]
                if "stage" in ps:
                    result["stage"] = ps["stage"]
                if "concerns" in ps:
                    concerns = ps["concerns"]
                    if isinstance(concerns, list):
                        result["concerns"] = concerns
                    elif isinstance(concerns, str):
                        result["concerns"] = [concerns]

            # 行为摘要
            if "behavior_summary" in intent:
                bs = intent["behavior_summary"]
                if "engagement" in bs:
                    result["engagement"] = bs["engagement"]

            # 匹配分析
            if "match_analysis" in intent:
                ma = intent["match_analysis"]
                if "customer_portrait" in ma:
                    result["customer_portrait"] = ma["customer_portrait"]
                if "use_case" in ma:
                    result["use_case"] = ma["use_case"]

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        # JSON解析失败，尝试从文本中提取信息
        # 使用正则表达式或简单的字符串匹配
        import re
        
        # 尝试提取购买阶段
        stage_patterns = {
            r'"stage"\s*:\s*"([^"]+)"': 'stage',
            r'购买阶段[：:]\s*([^\s|]+)': 'stage',
        }
        for pattern, key in stage_patterns.items():
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                result[key] = match.group(1)
                break
        
        # 尝试提取价格范围
        price_patterns = {
            r'"price_range"\s*:\s*"([^"]+)"': 'price_range',
            r'价格范围[：:]\s*([^\s|]+)': 'price_range',
        }
        for pattern, key in price_patterns.items():
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                result[key] = match.group(1)
                break
        
        # 尝试提取使用场景
        use_case_patterns = {
            r'"use_case"\s*:\s*"([^"]+)"': 'use_case',
            r'使用场景[：:]\s*([^\s|]+)': 'use_case',
        }
        for pattern, key in use_case_patterns.items():
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                result[key] = match.group(1)
                break

    # 构建text字段（如果为空）
    if not result["text"]:
        text_parts = []
        if result["core_interests"]:
            text_parts.append(f"核心兴趣: {', '.join(result['core_interests'])}")
        if result["key_attributes"]:
            text_parts.append(f"关键属性: {', '.join(result['key_attributes'])}")
        if result["price_range"]:
            text_parts.append(f"价格范围: {result['price_range']}")
        if result["main_appeal"]:
            text_parts.append(f"主要吸引力: {result['main_appeal']}")
        if result["stage"]:
            text_parts.append(f"购买阶段: {result['stage']}")
        if result["use_case"]:
            text_parts.append(f"使用场景: {result['use_case']}")
        if result["engagement"]:
            text_parts.append(f"参与度: {result['engagement']}")
        if result["customer_portrait"]:
            text_parts.append(f"客户画像: {result['customer_portrait']}")
        if result["concerns"]:
            concerns_str = ', '.join(result["concerns"]) if isinstance(result["concerns"], list) else result["concerns"]
            text_parts.append(f"关注点: {concerns_str}")
        
        result["text"] = " | ".join(text_parts) if text_parts else output[:200]  # 如果都没有，使用原始output的前200字符

    return result


def analyze_cluster_characteristics(cluster_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析聚类的特征
    返回：购买阶段、价格偏好、用户喜好等
    """
    if not cluster_data:
        return {}
    
    # 统计购买阶段
    stages = [d.get("stage", "") for d in cluster_data if d.get("stage")]
    stage_distribution = Counter(stages)
    dominant_stage = max(stage_distribution.items(), key=lambda x: x[1])[0] if stage_distribution else ""
    
    # 统计价格范围
    price_ranges = [d.get("price_range", "") for d in cluster_data if d.get("price_range")]
    price_distribution = Counter(price_ranges)
    dominant_price = max(price_distribution.items(), key=lambda x: x[1])[0] if price_distribution else ""
    
    # 收集使用场景（用户需求）
    use_cases = [d.get("use_case", "") for d in cluster_data if d.get("use_case")]
    use_case_distribution = Counter(use_cases)
    dominant_use_case = max(use_case_distribution.items(), key=lambda x: x[1])[0] if use_case_distribution else ""
    
    # 收集核心兴趣（用户喜好）
    all_interests = []
    for d in cluster_data:
        interests = d.get("core_interests", [])
        if isinstance(interests, list):
            all_interests.extend(interests)
    interest_distribution = Counter(all_interests)
    top_interests = [item[0] for item in interest_distribution.most_common(5)]
    
    # 收集关键属性（产品偏好）
    all_attributes = []
    for d in cluster_data:
        attributes = d.get("key_attributes", [])
        if isinstance(attributes, list):
            all_attributes.extend(attributes)
    attribute_distribution = Counter(all_attributes)
    top_attributes = [item[0] for item in attribute_distribution.most_common(5)]
    
    # 收集主要吸引力
    appeals = [d.get("main_appeal", "") for d in cluster_data if d.get("main_appeal")]
    appeal_distribution = Counter(appeals)
    dominant_appeal = max(appeal_distribution.items(), key=lambda x: x[1])[0] if appeal_distribution else ""
    
    # 收集关注点（从concerns字段，如果没有则从其他字段推断）
    all_concerns = []
    for d in cluster_data:
        concerns = d.get("concerns", [])
        if concerns:
            if isinstance(concerns, list):
                all_concerns.extend(concerns)
            elif isinstance(concerns, str):
                all_concerns.append(concerns)
        
        # 如果没有concerns，从key_attributes推断关注点
        if not concerns:
            attributes = d.get("key_attributes", [])
            if isinstance(attributes, list) and attributes:
                # 根据属性推断关注点
                for attr in attributes:
                    attr_lower = str(attr).lower()
                    if "price" in attr_lower or "cost" in attr_lower or "价值" in str(attr):
                        all_concerns.append("price")
                    elif "quality" in attr_lower or "品质" in str(attr) or "质量" in str(attr):
                        all_concerns.append("quality")
                    elif "material" in attr_lower or "材质" in str(attr) or "silicone" in attr_lower:
                        all_concerns.append("material")
                    elif "realistic" in attr_lower or "realism" in attr_lower or "仿真" in str(attr) or "逼真" in str(attr):
                        all_concerns.append("realism")
                    elif "size" in attr_lower or "尺寸" in str(attr) or "inch" in attr_lower:
                        all_concerns.append("size")
                    elif "function" in attr_lower or "功能" in str(attr) or "interactive" in attr_lower:
                        all_concerns.append("function")
                    elif "craftsmanship" in attr_lower or "工艺" in str(attr) or "hand-painted" in attr_lower:
                        all_concerns.append("craftsmanship")
        
        # 如果还是没有，从text字段推断
        if not all_concerns:
            text = d.get("text", "").lower()
            if "price" in text or "cost" in text or "价值" in text or "价格" in text:
                all_concerns.append("price")
            elif "quality" in text or "品质" in text or "质量" in text:
                all_concerns.append("quality")
            elif "material" in text or "材质" in text or "silicone" in text:
                all_concerns.append("material")
            elif "realistic" in text or "realism" in text or "仿真" in text or "逼真" in text:
                all_concerns.append("realism")
            elif "size" in text or "尺寸" in text or "inch" in text:
                all_concerns.append("size")
            elif "function" in text or "功能" in text or "interactive" in text:
                all_concerns.append("function")
            elif "craftsmanship" in text or "工艺" in text:
                all_concerns.append("craftsmanship")
    
    concern_distribution = Counter(all_concerns)
    top_concerns = [item[0] for item in concern_distribution.most_common(5)]
    
    # 统计参与度
    engagements = [d.get("engagement", "") for d in cluster_data if d.get("engagement")]
    engagement_distribution = Counter(engagements)
    
    return {
        "purchase_stage": {
            "dominant": dominant_stage,
            "distribution": dict(stage_distribution)
        },
        "price_preference": {
            "dominant": dominant_price,
            "distribution": dict(price_distribution)
        },
        "user_needs": {
            "dominant_use_case": dominant_use_case,
            "use_case_distribution": dict(use_case_distribution)
        },
        "user_preferences": {
            "top_interests": top_interests,
            "interest_distribution": dict(interest_distribution),
            "top_attributes": top_attributes,
            "attribute_distribution": dict(attribute_distribution),
            "main_appeal": dominant_appeal
        },
        "concerns": {
            "top_concerns": top_concerns,
            "concern_distribution": dict(concern_distribution)
        },
        "engagement": {
            "distribution": dict(engagement_distribution)
        }
    }


def generate_cluster_name(cluster_data: List[Dict[str, Any]], cluster_id: int) -> str:
    """使用Gemini API为聚类生成名称"""
    if not cluster_data or len(cluster_data) == 0:
        return f"聚类 {cluster_id}"
    
    if not GEMINI_API_KEY:
        return f"聚类 {cluster_id}"
    
    try:
        sample_data = cluster_data[:10]
        
        # 统计信息
        stages = [d.get("stage", "") for d in sample_data if d.get("stage")]
        stage_counts = Counter(stages)
        dominant_stage = max(stage_counts.items(), key=lambda x: x[1])[0] if stage_counts else ""
        
        price_ranges = [d.get("price_range", "") for d in sample_data if d.get("price_range")]
        price_counts = Counter(price_ranges)
        dominant_price = max(price_counts.items(), key=lambda x: x[1])[0] if price_counts else ""
        
        use_cases = [d.get("use_case", "") for d in sample_data if d.get("use_case")]
        unique_use_cases = list(set(use_cases))[:3]
        
        portraits = [d.get("customer_portrait", "") for d in sample_data if d.get("customer_portrait")]
        unique_portraits = list(set(portraits))[:2]
        
        all_concerns = []
        for d in sample_data:
            concerns = d.get("concerns", [])
            if isinstance(concerns, list):
                all_concerns.extend(concerns)
            elif isinstance(concerns, str):
                all_concerns.append(concerns)
        unique_concerns = list(set(all_concerns))[:5]
        
        texts_summary = "\n".join([f"- {d.get('text', '')}" for d in sample_data if d.get('text')])
        
        prompt_parts = [
            "请分析以下用户意图数据，为这个聚类生成一个简洁的中文名称（不超过15个字）。",
            "",
            "名称应该综合考虑以下因素：",
            "1. 购买阶段：用户处于浏览、对比还是决策阶段",
            "2. 用户需求：用户的使用场景和核心需求（如礼物、收藏、陪伴等）",
            "3. 购买习惯：价格敏感度、关注点、参与度等",
            "",
            "命名示例：",
            "- 如果处于决策阶段且关注价格，可以叫'决策阶段·价格敏感型'",
            "- 如果处于浏览阶段且是礼物需求，可以叫'浏览阶段·礼物购买型'",
            "- 如果处于对比阶段且关注功能，可以叫'对比阶段·功能导向型'",
            "- 如果关注材质且是收藏需求，可以叫'材质关注·收藏型'",
            "- 如果价格范围是premium且参与度高，可以叫'高端价值·深度研究型'",
            "",
            "意图文本示例：",
            texts_summary
        ]
        
        if dominant_stage:
            prompt_parts.append(f"\n主要购买阶段: {dominant_stage}")
        if dominant_price:
            prompt_parts.append(f"主要价格范围: {dominant_price}")
        if unique_use_cases:
            prompt_parts.append(f"主要使用场景: {', '.join(unique_use_cases)}")
        if unique_concerns:
            prompt_parts.append(f"主要关注点: {', '.join(unique_concerns[:3])}")
        if unique_portraits:
            prompt_parts.append(f"客户特征: {unique_portraits[0]}")
        
        prompt_parts.append("\n请只返回聚类名称，不要返回其他内容：")
        prompt = "\n".join(prompt_parts)
        
        model_names = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    cluster_name = response.text.strip().strip('"').strip("'").strip()
                    if cluster_name.startswith("```"):
                        lines = cluster_name.split("\n")
                        cluster_name = "\n".join(lines[1:-1]) if len(lines) > 2 else cluster_name
                        cluster_name = cluster_name.strip()
                    if len(cluster_name) > 20:
                        cluster_name = cluster_name[:20]
                    return cluster_name if cluster_name else f"聚类 {cluster_id}"
            except Exception as e:
                if "404" not in str(e) and "not found" not in str(e).lower():
                    raise
                continue
        
        return f"聚类 {cluster_id}"
        
    except Exception as e:
        print(f"  生成聚类 {cluster_id} 名称时出错: {str(e)[:100]}")
        return f"聚类 {cluster_id}"


def analyze_and_sync_shop53():
    """分析shop53的聚类并同步到前端"""
    script_dir = Path(__file__).parent
    
    # 加载聚类结果
    results_file = script_dir / "output" / "clustering_results.json"
    if not results_file.exists():
        results_file = script_dir / "clustering_results.json"
    
    if not results_file.exists():
        print(f"错误: 找不到聚类结果文件")
        return
    
    print(f"读取聚类结果: {results_file}")
    with open(results_file, "r", encoding="utf-8") as f:
        clustering_results = json.load(f)
    
    shop_result = clustering_results.get("53")
    if not shop_result:
        print("错误: 找不到shop53的聚类结果")
        return
    
    # 加载原始数据
    data_dirs = [
        script_dir / "data_extract",
        script_dir.parent / "data_extract",
    ]
    
    data_dir = None
    for d in data_dirs:
        if d.exists():
            data_dir = d
            break
    
    if not data_dir:
        print("错误: 找不到数据目录")
        return
    
    data_file = data_dir / "extracted_data_shop_53.json"
    if not data_file.exists():
        print(f"错误: 找不到数据文件 {data_file}")
        return
    
    print(f"读取原始数据: {data_file}")
    with open(data_file, "r", encoding="utf-8") as f:
        shop_data = json.load(f)
    
    # 创建session_id到output的映射
    session_output_map = {}
    for record in shop_data:
        session_id = record.get("session_id", "")
        output = record.get("output", "")
        if session_id and output:
            session_output_map[session_id] = output
    
    # 获取聚类信息
    clustering_info = shop_result.get("clustering", {})
    labels = clustering_info.get("labels", [])
    n_clusters = clustering_info.get("n_clusters", 0)
    intention_clusters = shop_result.get("intention_clusters", {})
    
    print(f"\n分析shop53的聚类:")
    print(f"  聚类数: {n_clusters}")
    print(f"  意图数: {len(labels)}")
    
    # 按聚类组织数据
    cluster_data_map = defaultdict(list)
    
    # 优先从intention_clusters获取
    if intention_clusters:
        print("  从intention_clusters提取数据...")
        for cluster_id, intentions in intention_clusters.items():
            cluster_id_int = int(cluster_id)
            for intention in intentions:
                session_id = intention.get("session_id", "")
                if session_id in session_output_map:
                    output = session_output_map[session_id]
                    data = extract_text_from_output(output)
                    if data.get("text"):
                        cluster_data_map[cluster_id_int].append(data)
    
    # 如果intention_clusters为空或数据不足，从labels重建
    if not cluster_data_map or len(cluster_data_map) == 0:
        print("  从labels重建聚类数据...")
        print(f"    labels数量: {len(labels)}, shop_data数量: {len(shop_data)}")
        extracted_count = 0
        for idx, cluster_id in enumerate(labels):
            if idx < len(shop_data):
                record = shop_data[idx]
                output = record.get("output", "")
                if output:
                    data = extract_text_from_output(output)
                    # 只要有text字段（即使是构建的）或其他有效字段就添加
                    if data.get("text") or data.get("stage") or data.get("price_range") or data.get("use_case") or data.get("core_interests"):
                        cluster_data_map[int(cluster_id)].append(data)
                        extracted_count += 1
        print(f"    成功提取 {extracted_count} 条数据，分布在 {len(cluster_data_map)} 个聚类中")
    
    # 分析每个聚类并生成名称
    print(f"\n正在分析 {len(cluster_data_map)} 个聚类...")
    cluster_analyses = {}
    cluster_names = {}
    
    for cluster_id in sorted(cluster_data_map.keys()):
        cluster_data = cluster_data_map[cluster_id]
        print(f"\n分析聚类 {cluster_id} ({len(cluster_data)} 个意图)...")
        
        # 分析特征
        characteristics = analyze_cluster_characteristics(cluster_data)
        cluster_analyses[cluster_id] = characteristics
        
        # 生成名称（如果还没有）
        if "cluster_names" in clustering_info:
            cluster_names_dict = clustering_info.get("cluster_names", {})
            if cluster_id in cluster_names_dict:
                cluster_name = cluster_names_dict[cluster_id]
            else:
                print(f"  生成聚类名称...")
                cluster_name = generate_cluster_name(cluster_data, cluster_id)
                time.sleep(0.5)
        else:
            print(f"  生成聚类名称...")
            cluster_name = generate_cluster_name(cluster_data, cluster_id)
            time.sleep(0.5)
        
        cluster_names[cluster_id] = cluster_name
        print(f"  名称: {cluster_name}")
        print(f"  购买阶段: {characteristics.get('purchase_stage', {}).get('dominant', 'N/A')}")
        print(f"  价格偏好: {characteristics.get('price_preference', {}).get('dominant', 'N/A')}")
        print(f"  主要需求: {characteristics.get('user_needs', {}).get('dominant_use_case', 'N/A')}")
    
    # 更新聚类结果
    if "cluster_names" not in clustering_info:
        clustering_info["cluster_names"] = cluster_names
    else:
        clustering_info["cluster_names"].update(cluster_names)
    
    clustering_info["cluster_analyses"] = {str(k): v for k, v in cluster_analyses.items()}
    shop_result["clustering"] = clustering_info
    
    # 保存更新后的聚类结果
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(clustering_results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 聚类结果已更新: {results_file}")
    
    # 转换为前端格式
    print("\n正在转换为前端格式...")
    frontend_data = convert_to_frontend_format(shop_result, cluster_analyses, cluster_names, shop_data)
    
    # 保存前端数据
    dashboard_dir = script_dir.parent / "visualization_dashboard"
    output_file = dashboard_dir / "data_shop_53.js"
    
    generate_frontend_js(frontend_data, output_file)
    print(f"\n✅ 前端数据已生成: {output_file}")
    
    return True


def translate_stage_to_chinese(stage: str) -> str:
    """将英文购买阶段转换为中文"""
    stage_map = {
        "browsing": "浏览阶段",
        "comparing": "对比阶段",
        "deciding": "决策阶段",
        "browsing/comparing": "浏览对比阶段",
        "comparing/deciding": "对比决策阶段",
        "browsing/comparing/deciding": "浏览对比决策阶段",
        "deciding/researching": "决策研究阶段",
        "deciding/comparing": "决策对比阶段",
        "deciding/considering purchase": "决策考虑购买阶段",
        "deciding/purchasing": "决策购买阶段",
        "browsing/exploring": "浏览探索阶段",
    }
    return stage_map.get(stage, stage if stage else "浏览阶段")


def translate_price_to_chinese(price: str) -> str:
    """将英文价格偏好转换为中文"""
    price_map = {
        "budget": "预算型",
        "mid-range": "中端价值型",
        "premium": "高端价值型",
        "budget/mid-range": "预算中端型",
        "mid-range/premium": "中端高端型",
        "mid-range to premium": "中端到高端型",
    }
    return price_map.get(price, price if price else "高端价值型")


def translate_concern_to_chinese(concerns: List[str]) -> str:
    """将关注点列表转换为中文描述"""
    if not concerns:
        return "综合关注"
    
    # 统计最常见的关注点
    from collections import Counter
    concern_counts = Counter(concerns)
    
    if not concern_counts:
        return "综合关注"
    
    # 获取最常见的关注点
    top_concern = concern_counts.most_common(1)[0][0] if concern_counts else ""
    
    # 如果最常见的关注点占比超过30%，使用它
    total = sum(concern_counts.values())
    top_count = concern_counts.most_common(1)[0][1] if concern_counts else 0
    if top_count / total >= 0.3:
        # 将英文关注点转换为中文
        concern_map = {
            "price": "价格导向",
            "quality": "品质导向",
            "material": "材质导向",
            "function": "功能导向",
            "appearance": "外观导向",
            "size": "尺寸导向",
            "realism": "仿真导向",
            "interaction": "互动导向",
            "craftsmanship": "工艺导向",
            "safety": "安全导向",
        }
        
        # 检查是否包含关键词
        top_lower = top_concern.lower()
        for key, value in concern_map.items():
            if key in top_lower:
                return value
        
        # 如果关注点太多样（超过5种），返回"综合关注"
        if len(concern_counts) > 5:
            return "综合关注"
        
        # 否则返回原始值（可能是中文）
        return top_concern if top_concern else "综合关注"
    
    # 如果关注点太分散，返回"综合关注"
    return "综合关注"


def convert_to_frontend_format(shop_result, cluster_analyses, cluster_names, shop_data):
    """转换为前端需要的格式"""
    clustering_info = shop_result.get("clustering", {})
    labels = clustering_info.get("labels", [])
    intention_clusters = shop_result.get("intention_clusters", {})
    user_clusters = shop_result.get("user_clusters", {})
    
    # 构建businessInsights
    business_insights = []
    for cluster_id in sorted(cluster_analyses.keys()):
        analysis = cluster_analyses[cluster_id]
        cluster_name = cluster_names.get(cluster_id, f"聚类 {cluster_id}")
        
        intentions = intention_clusters.get(str(cluster_id), [])
        users = user_clusters.get(str(cluster_id), [])
        
        insight = {
            "cluster_id": str(cluster_id),
            "cluster_name": cluster_name,
            "full_label": cluster_name,
            "key_characteristics": {
                "segment_count": len(intentions),
                "user_count": len(users),
                "purchase_stage": analysis.get("purchase_stage", {}).get("dominant", ""),
                "price_sensitivity": analysis.get("price_preference", {}).get("dominant", ""),
                "user_needs": analysis.get("user_needs", {}).get("dominant_use_case", ""),
                "main_appeal": analysis.get("user_preferences", {}).get("main_appeal", ""),
            },
            "purchase_stage_analysis": analysis.get("purchase_stage", {}),
            "price_preference_analysis": analysis.get("price_preference", {}),
            "user_needs_analysis": analysis.get("user_needs", {}),
            "user_preferences_analysis": analysis.get("user_preferences", {}),
            "concerns_analysis": analysis.get("concerns", {}),
            "engagement_analysis": analysis.get("engagement", {}),
        }
        business_insights.append(insight)
    
    # 构建userPortraits
    user_portraits = []
    for cluster_id in sorted(cluster_analyses.keys()):
        analysis = cluster_analyses[cluster_id]
        cluster_name = cluster_names.get(cluster_id, f"聚类 {cluster_id}")
        intentions = intention_clusters.get(str(cluster_id), [])
        users = user_clusters.get(str(cluster_id), [])
        
        # 获取主要特征
        dominant_stage = analysis.get("purchase_stage", {}).get("dominant", "")
        dominant_price = analysis.get("price_preference", {}).get("dominant", "")
        top_concerns = analysis.get("concerns", {}).get("top_concerns", [])
        
        # 转换为中文
        stage_chinese = translate_stage_to_chinese(dominant_stage)
        price_chinese = translate_price_to_chinese(dominant_price)
        concern_chinese = translate_concern_to_chinese(top_concerns)
        
        # 获取用户需求（简化描述）
        dominant_use_case = analysis.get("user_needs", {}).get("dominant_use_case", "")
        # 简化use_case描述
        if "gift" in dominant_use_case.lower() or "礼物" in dominant_use_case:
            need_chinese = "礼物需求"
        elif "collect" in dominant_use_case.lower() or "收藏" in dominant_use_case:
            need_chinese = "收藏需求"
        elif "companion" in dominant_use_case.lower() or "陪伴" in dominant_use_case:
            need_chinese = "陪伴需求"
        elif "play" in dominant_use_case.lower() or "玩" in dominant_use_case:
            need_chinese = "玩耍需求"
        else:
            need_chinese = "综合需求"
        
        portrait = {
            "cluster_id": str(cluster_id),
            "cluster_name": cluster_name,
            "segment_count": len(intentions),
            "unique_users": len(users),
            "characteristics": {
                "stage": stage_chinese,
                "price": price_chinese,
                "concern": concern_chinese,
                "need": need_chinese,
                "product": "多产品比较",  # 默认值，可以根据实际数据调整
                "engagement": "快速浏览者",  # 默认值，可以根据实际数据调整
            },
            "intent_profile": {
                "purchase_stage": analysis.get("purchase_stage", {}).get("distribution", {}),
                "price_range": analysis.get("price_preference", {}).get("distribution", {}),
                "use_case": analysis.get("user_needs", {}).get("use_case_distribution", {}),
                "concerns": {c: 1 for c in top_concerns[:5]},  # 转换为字典格式
            },
            "product_preferences": {
                "top_interests": analysis.get("user_preferences", {}).get("top_interests", []),
                "top_attributes": analysis.get("user_preferences", {}).get("top_attributes", []),
            },
            "concerns": top_concerns,
        }
        user_portraits.append(portrait)
    
    # 构建stats
    stats = {
        "totalUsers": shop_result.get("n_users", 0),
        "totalSegments": shop_result.get("n_intentions", 0),
        "totalClusters": len(cluster_analyses),
    }
    
    return {
        "businessInsights": business_insights,
        "userPortraits": user_portraits,
        "stats": stats,
    }


def generate_frontend_js(frontend_data, output_file):
    """生成前端JavaScript文件"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("// 用户意图分析数据\n")
        f.write("// 自动生成，请勿手动编辑\n\n")
        
        f.write("// 业务洞察数据\n")
        f.write("const businessInsights = ")
        json.dump(frontend_data["businessInsights"], f, indent=2, ensure_ascii=False)
        f.write(";\n\n")
        
        f.write("// 用户画像数据\n")
        f.write("const userPortraits = ")
        json.dump(frontend_data["userPortraits"], f, indent=2, ensure_ascii=False)
        f.write(";\n\n")
        
        f.write("// 统计数据\n")
        f.write("const stats = ")
        json.dump(frontend_data["stats"], f, indent=2, ensure_ascii=False)
        f.write(";\n\n")
        
        f.write("// 数据加载完成\n")
        f.write('console.log("数据加载完成:", stats);\n')


def main():
    print("="*80)
    print("Shop53 聚类分析和前端同步")
    print("="*80)
    
    if not GEMINI_API_KEY:
        print("警告: 未设置GEMINI_API_KEY，将使用默认聚类名称")
    
    analyze_and_sync_shop53()
    
    print("\n" + "="*80)
    print("✅ 完成！")
    print("="*80)


if __name__ == "__main__":
    main()

