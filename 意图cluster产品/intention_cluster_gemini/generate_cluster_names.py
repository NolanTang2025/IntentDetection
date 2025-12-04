#!/usr/bin/env python3
"""
为现有聚类结果生成聚类名称
读取聚类结果文件，使用Gemini API为每个聚类生成名称
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

import google.generativeai as genai

# 配置 Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def extract_text_from_output(output: str) -> Dict[str, Any]:
    """
    从output字段中提取用于分析的文本和结构化信息
    返回包含文本描述和结构化信息的字典
    """
    if not output or output.strip() == "":
        return {"text": "", "stage": "", "concerns": [], "use_case": "", "price_range": "", "engagement": ""}

    result = {
        "text": "",
        "stage": "",
        "concerns": [],
        "use_case": "",
        "price_range": "",
        "engagement": "",
        "customer_portrait": ""
    }

    # 尝试解析JSON
    try:
        # 清理可能的代码块标记
        cleaned = output.strip()
        if cleaned.startswith("```"):
            first_newline = cleaned.find("\n")
            if first_newline != -1:
                cleaned = cleaned[first_newline + 1 :]
            if cleaned.rstrip().endswith("```"):
                cleaned = cleaned.rstrip()[:-3].rstrip()

        data = json.loads(cleaned)

        # 提取关键信息构建文本
        text_parts = []

        if isinstance(data, dict) and "intent" in data:
            intent = data["intent"]

            # 核心兴趣
            if "core_interests" in intent and intent["core_interests"]:
                text_parts.append(f"核心兴趣: {', '.join(intent['core_interests'])}")

            # 产品关注点
            if "product_focus" in intent:
                pf = intent["product_focus"]
                if "key_attributes" in pf and pf["key_attributes"]:
                    text_parts.append(f"关键属性: {', '.join(pf['key_attributes'])}")
                if "price_range" in pf:
                    price_range = pf["price_range"]
                    result["price_range"] = price_range
                    text_parts.append(f"价格范围: {price_range}")
                if "main_appeal" in pf:
                    text_parts.append(f"主要吸引力: {pf['main_appeal']}")

            # 购买信号（重点提取购买阶段和关注点）
            if "purchase_signals" in intent:
                ps = intent["purchase_signals"]
                if "stage" in ps:
                    stage = ps["stage"]
                    result["stage"] = stage
                    text_parts.append(f"购买阶段: {stage}")
                if "concerns" in ps:
                    concerns = ps["concerns"]
                    if isinstance(concerns, list):
                        result["concerns"] = concerns
                        text_parts.append(f"关注点: {', '.join(concerns)}")
                    elif isinstance(concerns, str):
                        result["concerns"] = [concerns]
                        text_parts.append(f"关注点: {concerns}")

            # 行为摘要（提取参与度）
            if "behavior_summary" in intent:
                bs = intent["behavior_summary"]
                if "engagement" in bs:
                    engagement = bs["engagement"]
                    result["engagement"] = engagement
                    text_parts.append(f"参与度: {engagement}")

            # 匹配分析（提取使用场景和客户画像 - 反映需求和购买习惯）
            if "match_analysis" in intent:
                ma = intent["match_analysis"]
                if "customer_portrait" in ma:
                    customer_portrait = ma["customer_portrait"]
                    result["customer_portrait"] = customer_portrait
                    text_parts.append(f"客户画像: {customer_portrait}")
                if "use_case" in ma:
                    use_case = ma["use_case"]
                    result["use_case"] = use_case
                    text_parts.append(f"使用场景: {use_case}")

        result["text"] = " | ".join(text_parts) if text_parts else output
        return result

    except (json.JSONDecodeError, ValueError, TypeError):
        # 如果解析失败，返回原始文本
        result["text"] = output
        return result


def generate_cluster_name(cluster_data: List[Dict[str, Any]], cluster_id: int) -> str:
    """
    使用Gemini API为聚类生成名称
    基于聚类中的意图文本、购买阶段、需求和购买习惯，生成一个概括性的名称
    
    cluster_data: 包含text、stage、concerns、use_case等信息的字典列表
    """
    if not cluster_data or len(cluster_data) == 0:
        return f"聚类 {cluster_id}"
    
    if not GEMINI_API_KEY:
        print(f"  警告: 未设置GEMINI_API_KEY，使用默认名称")
        return f"聚类 {cluster_id}"
    
    try:
        # 收集聚类的代表性数据（最多取前10个，避免prompt过长）
        sample_data = cluster_data[:10]
        
        # 统计购买阶段分布
        stages = [d.get("stage", "") for d in sample_data if d.get("stage")]
        stage_counts = {}
        for stage in stages:
            if stage:
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
        dominant_stage = max(stage_counts.items(), key=lambda x: x[1])[0] if stage_counts else ""
        
        # 统计价格范围
        price_ranges = [d.get("price_range", "") for d in sample_data if d.get("price_range")]
        price_counts = {}
        for pr in price_ranges:
            if pr:
                price_counts[pr] = price_counts.get(pr, 0) + 1
        dominant_price = max(price_counts.items(), key=lambda x: x[1])[0] if price_counts else ""
        
        # 收集使用场景（反映用户需求）
        use_cases = [d.get("use_case", "") for d in sample_data if d.get("use_case")]
        unique_use_cases = list(set(use_cases))[:3]  # 最多3个
        
        # 收集客户画像（反映购买习惯）
        portraits = [d.get("customer_portrait", "") for d in sample_data if d.get("customer_portrait")]
        unique_portraits = list(set(portraits))[:2]  # 最多2个
        
        # 收集关注点
        all_concerns = []
        for d in sample_data:
            concerns = d.get("concerns", [])
            if isinstance(concerns, list):
                all_concerns.extend(concerns)
            elif isinstance(concerns, str):
                all_concerns.append(concerns)
        unique_concerns = list(set(all_concerns))[:5]  # 最多5个
        
        # 构建文本摘要
        texts_summary = "\n".join([f"- {d.get('text', '')}" for d in sample_data if d.get('text')])
        
        # 构建包含更多信息的prompt
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
        
        # 添加结构化信息
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
        
        # 尝试使用不同的Gemini模型（按优先级）
        model_names = [
            "gemini-2.5-flash",  # 最新快速模型，推荐用于生成名称
            "gemini-2.5-pro",    # 最新强大模型
            "gemini-2.0-flash",  # 备选快速模型
            "gemini-1.5-flash",  # 旧版本快速模型
            "gemini-1.5-pro",    # 旧版本强大模型
        ]
        
        model = None
        response = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    break
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg.lower():
                    # 模型不存在，尝试下一个
                    continue
                else:
                    # 其他错误，直接抛出
                    raise
        
        if not response or not response.text:
            print(f"  警告: 无法使用Gemini API生成聚类名称，使用默认名称")
            return f"聚类 {cluster_id}"
        
        # 提取名称（去除可能的引号、空格等）
        cluster_name = response.text.strip()
        cluster_name = cluster_name.strip('"').strip("'").strip()
        
        # 移除可能的markdown格式
        if cluster_name.startswith("```"):
            lines = cluster_name.split("\n")
            cluster_name = "\n".join(lines[1:-1]) if len(lines) > 2 else cluster_name
            cluster_name = cluster_name.strip()
        
        # 限制长度
        if len(cluster_name) > 20:
            cluster_name = cluster_name[:20]
        
        return cluster_name if cluster_name else f"聚类 {cluster_id}"
        
    except Exception as e:
        error_msg = str(e)
        print(f"  生成聚类 {cluster_id} 名称时出错: {error_msg[:100]}")
        # 如果所有模型都失败，返回默认名称
        return f"聚类 {cluster_id}"


def load_clustering_results(results_file: Path) -> Dict[str, Any]:
    """加载聚类结果文件"""
    with open(results_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_shop_data(data_file: Path) -> List[Dict]:
    """加载店铺原始数据"""
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_names_for_shop(
    shop_id: str,
    clustering_results: Dict[str, Any],
    shop_data: List[Dict]
) -> Dict[int, str]:
    """
    为单个店铺的聚类生成名称
    返回: {cluster_id: cluster_name}
    """
    shop_result = clustering_results.get(shop_id)
    if not shop_result:
        print(f"警告: 找不到店铺 {shop_id} 的聚类结果")
        return {}
    
    clustering_info = shop_result.get("clustering")
    if not clustering_info:
        print(f"警告: 店铺 {shop_id} 没有聚类信息")
        return {}
    
    labels = clustering_info.get("labels", [])
    n_clusters = clustering_info.get("n_clusters", 0)
    
    if n_clusters == 0:
        print(f"警告: 店铺 {shop_id} 的聚类数为0")
        return {}
    
    print(f"\n处理店铺 {shop_id}:")
    print(f"  聚类数: {n_clusters}")
    print(f"  意图数: {len(labels)}")
    
    # 创建session_id到output的映射
    session_output_map = {}
    for record in shop_data:
        session_id = record.get("session_id", "")
        output = record.get("output", "")
        if session_id and output:
            session_output_map[session_id] = output
    
    # 按聚类组织意图数据（包含文本和结构化信息）
    cluster_data_map = defaultdict(list)
    
    # 从intention_clusters中获取每个聚类的session信息
    intention_clusters = shop_result.get("intention_clusters", {})
    
    for cluster_id, intentions in intention_clusters.items():
        cluster_id_int = int(cluster_id)
        for intention in intentions:
            session_id = intention.get("session_id", "")
            if session_id in session_output_map:
                output = session_output_map[session_id]
                data = extract_text_from_output(output)
                if data.get("text"):
                    cluster_data_map[cluster_id_int].append(data)
    
    # 如果intention_clusters为空，尝试从labels和原始数据重建
    if not cluster_data_map:
        print("  从labels重建聚类数据...")
        for idx, cluster_id in enumerate(labels):
            if idx < len(shop_data):
                record = shop_data[idx]
                output = record.get("output", "")
                if output:
                    data = extract_text_from_output(output)
                    if data.get("text"):
                        cluster_data_map[int(cluster_id)].append(data)
    
    # 为每个聚类生成名称
    cluster_names = {}
    print(f"\n正在为 {len(cluster_data_map)} 个聚类生成名称...")
    
    for cluster_id in sorted(cluster_data_map.keys()):
        cluster_data = cluster_data_map[cluster_id]
        print(f"  生成聚类 {cluster_id} 的名称（{len(cluster_data)} 个意图）...")
        cluster_name = generate_cluster_name(cluster_data, cluster_id)
        cluster_names[cluster_id] = cluster_name
        print(f"    → {cluster_name}")
        time.sleep(0.5)  # 避免API限流
    
    return cluster_names


def main():
    """主函数"""
    script_dir = Path(__file__).parent
    
    # 查找聚类结果文件
    results_files = [
        script_dir / "output" / "clustering_results.json",
        script_dir / "clustering_results.json",
    ]
    
    results_file = None
    for f in results_files:
        if f.exists():
            results_file = f
            break
    
    if not results_file:
        print(f"错误: 找不到聚类结果文件")
        print(f"请检查以下位置:")
        for f in results_files:
            print(f"  - {f}")
        return
    
    print(f"读取聚类结果文件: {results_file}")
    clustering_results = load_clustering_results(results_file)
    
    # 检查API密钥
    if not GEMINI_API_KEY:
        print("错误: 未设置GEMINI_API_KEY环境变量")
        print("请运行: export GEMINI_API_KEY='your-api-key'")
        return
    
    print(f"使用的API key: {GEMINI_API_KEY[:15]}...")
    
    # 查找数据目录
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
        print(f"错误: 找不到数据目录")
        return
    
    # 处理每个店铺
    all_cluster_names = {}
    
    for shop_id in clustering_results.keys():
        print(f"\n{'='*60}")
        print(f"处理店铺 {shop_id}")
        print(f"{'='*60}")
        
        # 加载店铺数据
        data_file = data_dir / f"extracted_data_shop_{shop_id}.json"
        if not data_file.exists():
            print(f"警告: 找不到数据文件 {data_file}")
            continue
        
        shop_data = load_shop_data(data_file)
        
        # 生成聚类名称
        cluster_names = generate_names_for_shop(shop_id, clustering_results, shop_data)
        all_cluster_names[shop_id] = cluster_names
        
        # 更新聚类结果
        if shop_id in clustering_results:
            shop_result = clustering_results[shop_id]
            if "clustering" in shop_result:
                shop_result["clustering"]["cluster_names"] = cluster_names
            if "cluster_names" not in shop_result:
                shop_result["cluster_names"] = cluster_names
    
    # 保存更新后的结果
    output_file = results_file
    print(f"\n保存更新后的聚类结果到: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clustering_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 完成！已为所有聚类生成名称")
    print("\n聚类名称摘要:")
    for shop_id, names in all_cluster_names.items():
        print(f"\n店铺 {shop_id}:")
        for cluster_id, name in sorted(names.items()):
            print(f"  聚类 {cluster_id}: {name}")


if __name__ == "__main__":
    main()

