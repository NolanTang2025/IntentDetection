#!/usr/bin/env python3
"""
意图聚类脚本
1. 读取每个店铺的数据
2. 对每个session的意图数据进行embedding（不聚合用户）
3. 对所有意图进行聚类
4. 将聚类结果分配给对应的用户
"""

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import google.generativeai as genai
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

# 配置 Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def extract_text_from_output(output: str) -> str:
    """
    从output字段中提取用于embedding的文本
    将JSON格式的意图数据转换为文本描述
    """
    if not output or output.strip() == "":
        return ""

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
                    text_parts.append(f"价格范围: {pf['price_range']}")
                if "main_appeal" in pf:
                    text_parts.append(f"主要吸引力: {pf['main_appeal']}")

            # 购买信号
            if "purchase_signals" in intent:
                ps = intent["purchase_signals"]
                if "stage" in ps:
                    text_parts.append(f"购买阶段: {ps['stage']}")

            # 行为摘要
            if "behavior_summary" in intent:
                bs = intent["behavior_summary"]
                if "engagement" in bs:
                    text_parts.append(f"参与度: {bs['engagement']}")

            # 匹配分析
            if "match_analysis" in intent:
                ma = intent["match_analysis"]
                if "customer_portrait" in ma:
                    text_parts.append(f"客户画像: {ma['customer_portrait']}")
                if "use_case" in ma:
                    text_parts.append(f"使用场景: {ma['use_case']}")

        return " | ".join(text_parts) if text_parts else output

    except (json.JSONDecodeError, ValueError, TypeError):
        # 如果解析失败，返回原始文本
        return output


def get_embedding(
    text: str, model: str = "models/embedding-001", use_mock: bool = False
) -> List[float]:
    """
    使用Gemini API获取文本的embedding向量
    """
    if not text or text.strip() == "":
        return None

    if use_mock:
        raise ValueError("不允许使用模拟embedding，请配置正确的API密钥")

    if not GEMINI_API_KEY:
        raise ValueError("未设置GEMINI_API_KEY环境变量")

    try:
        # 使用Gemini embedding API
        result = genai.embed_content(
            model=model,
            content=text,
            task_type="clustering"
        )
        # Gemini API返回格式: {'embedding': [...]}
        if result and "embedding" in result:
            return result["embedding"]
        else:
            return None
    except Exception as e:
        error_msg = str(e)
        print(f"获取embedding时出错: {error_msg[:200]}")
        raise  # 抛出异常，让调用者处理


def generate_cluster_name(cluster_texts: List[str], cluster_id: int) -> str:
    """
    使用Gemini API为聚类生成名称
    基于聚类中的意图文本，生成一个概括性的名称
    """
    if not cluster_texts or len(cluster_texts) == 0:
        return f"聚类 {cluster_id}"
    
    if not GEMINI_API_KEY:
        return f"聚类 {cluster_id}"
    
    try:
        # 收集聚类的代表性文本（最多取前10个，避免prompt过长）
        sample_texts = cluster_texts[:10]
        texts_summary = "\n".join([f"- {text}" for text in sample_texts])
        
        # 构建prompt
        prompt = f"""请分析以下用户意图文本，为这个聚类生成一个简洁的中文名称（不超过15个字）。
名称应该概括这些意图的共同特点，例如：
- 如果都是关于价格和优惠的，可以叫"价格敏感型"
- 如果都是关于产品功能的，可以叫"功能导向型"
- 如果都是关于礼物购买的，可以叫"礼物购买型"
- 如果都是关于产品材质的，可以叫"材质关注型"

意图文本示例：
{texts_summary}

请只返回聚类名称，不要返回其他内容："""
        
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


def prepare_intention_data(shop_data: List[Dict]) -> List[Dict]:
    """
    准备意图数据，不进行用户聚合
    返回: [{session_id, user_id, timestamp, text, original_output}, ...]
    """
    intention_records = []
    
    for record in shop_data:
        session_id = record.get("session_id", "")
        user_id = record.get("user_id", "")
        timestamp = record.get("timestamp", "")
        output = record.get("output", "")
        
        if not output or not output.strip():
            continue
            
        # 提取文本用于embedding
        text = extract_text_from_output(output)
        if not text or text.strip() == "":
            continue
            
        intention_records.append({
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "text": text,
            "original_output": output,
        })
    
    return intention_records


def cluster_intentions(
    embeddings: np.ndarray,
    method: str = "kmeans",
    n_clusters: int = None,
) -> Dict[str, Any]:
    """
    对意图进行聚类
    """
    if len(embeddings) < 2:
        return {"labels": [0] * len(embeddings), "n_clusters": 1, "method": method}

    if method == "kmeans":
        if n_clusters is None:
            # 自动选择聚类数（使用肘部法则的简化版本）
            n_clusters = min(8, max(2, len(embeddings) // 3))

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)

        # 计算轮廓系数（需要至少2个不同的标签，且标签数要少于样本数）
        unique_labels = set(labels)
        if len(unique_labels) > 1 and len(unique_labels) < len(embeddings):
            try:
                silhouette = silhouette_score(embeddings, labels)
            except ValueError:
                silhouette = -1
        else:
            silhouette = -1

        return {
            "labels": labels.tolist(),
            "n_clusters": n_clusters,
            "method": "kmeans",
            "silhouette_score": silhouette,
            "centroids": kmeans.cluster_centers_.tolist(),
        }

    elif method == "dbscan":
        dbscan = DBSCAN(eps=0.5, min_samples=2)
        labels = dbscan.fit_predict(embeddings)

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

        return {
            "labels": labels.tolist(),
            "n_clusters": n_clusters,
            "method": "dbscan",
            "n_noise": int(list(labels).count(-1)),
        }

    else:
        raise ValueError(f"不支持的聚类方法: {method}")


def process_shop(
    shop_id: str, data_dir: Path, use_mock_embedding: bool = False
) -> Dict[str, Any]:
    """
    处理单个店铺的数据
    """
    json_file = data_dir / f"extracted_data_shop_{shop_id}.json"

    if not json_file.exists():
        print(f"警告: 找不到文件 {json_file}")
        return None

    print(f"\n处理店铺 {shop_id}...")
    print(f"读取文件: {json_file}")

    # 读取数据
    with open(json_file, "r", encoding="utf-8") as f:
        shop_data = json.load(f)

    print(f"找到 {len(shop_data)} 条记录")

    # 准备意图数据（不聚合用户）
    intention_records = prepare_intention_data(shop_data)
    print(f"准备聚类 {len(intention_records)} 个意图")

    if len(intention_records) < 2:
        print(f"警告: 店铺 {shop_id} 的有效意图数少于2，无法进行聚类")
        return {"shop_id": shop_id, "n_intentions": len(intention_records), "clustering": None}

    # 获取每个意图的embedding
    print("正在获取embedding...")
    intention_embeddings = []
    valid_records = []
    failed_count = 0

    for i, record in enumerate(intention_records, 1):
        text = record["text"]
        try:
            embedding = get_embedding(text, use_mock=use_mock_embedding)
            if embedding:
                intention_embeddings.append(embedding)
                valid_records.append(record)
                if i % 10 == 0:
                    print(f"  已处理 {i}/{len(intention_records)} 个意图")
                time.sleep(0.1)  # 避免API限流
            else:
                failed_count += 1
        except Exception as e:
            print(f"  处理第 {i} 个意图时出错: {str(e)[:100]}")
            failed_count += 1
            # 如果是API错误，直接抛出异常
            if "API" in str(e) or "quota" in str(e).lower() or "429" in str(e):
                raise

    print(f"成功获取 {len(intention_embeddings)} 个意图的embedding")
    if failed_count > 0:
        print(f"失败 {failed_count} 个意图")

    if len(intention_embeddings) < 2:
        print(f"警告: 店铺 {shop_id} 的有效意图数少于2，无法进行聚类")
        return {"shop_id": shop_id, "n_intentions": len(intention_embeddings), "clustering": None}

    # 准备聚类数据
    embeddings_array = np.array(intention_embeddings)

    print(f"Embedding维度: {embeddings_array.shape}")

    # 进行聚类
    print("正在进行意图聚类...")
    clustering_result = cluster_intentions(embeddings_array, method="kmeans")

    # 统计每个用户属于哪些聚类
    user_cluster_mapping = defaultdict(lambda: {"clusters": set(), "sessions": []})
    
    for idx, record in enumerate(valid_records):
        cluster_id = clustering_result["labels"][idx]
        user_id = record["user_id"]
        
        user_cluster_mapping[user_id]["clusters"].add(cluster_id)
        user_cluster_mapping[user_id]["sessions"].append({
            "session_id": record["session_id"],
            "timestamp": record["timestamp"],
            "cluster_id": cluster_id,
        })

    # 组织结果
    result = {
        "shop_id": shop_id,
        "n_intentions": len(intention_embeddings),
        "n_sessions": len(shop_data),
        "n_users": len(user_cluster_mapping),
        "embedding_dim": embeddings_array.shape[1],
        "clustering": clustering_result,
        "intention_clusters": {},
        "user_clusters": {},
    }

    # 按聚类组织意图（用于分析）
    cluster_texts_map = defaultdict(list)  # 用于收集每个聚类的文本
    
    for idx, record in enumerate(valid_records):
        cluster_id = clustering_result["labels"][idx]
        if cluster_id not in result["intention_clusters"]:
            result["intention_clusters"][cluster_id] = []
        
        result["intention_clusters"][cluster_id].append({
            "session_id": record["session_id"],
            "user_id": record["user_id"],
            "timestamp": record["timestamp"],
        })
        
        # 收集该聚类的文本用于生成名称
        cluster_texts_map[cluster_id].append(record["text"])

    # 将聚类分配给用户
    for user_id, data in user_cluster_mapping.items():
        clusters = sorted(list(data["clusters"]))
        # 用户可能属于多个聚类，记录主要聚类（最常见的聚类）
        cluster_counts = {}
        for session in data["sessions"]:
            cid = session["cluster_id"]
            cluster_counts[cid] = cluster_counts.get(cid, 0) + 1
        
        # 找到最常见的聚类作为主要聚类
        primary_cluster = max(cluster_counts.items(), key=lambda x: x[1])[0] if cluster_counts else clusters[0] if clusters else None
        
        if primary_cluster not in result["user_clusters"]:
            result["user_clusters"][primary_cluster] = []
        
        result["user_clusters"][primary_cluster].append({
            "user_id": user_id,
            "session_count": len(data["sessions"]),
            "all_clusters": clusters,  # 用户所属的所有聚类
            "cluster_counts": cluster_counts,  # 每个聚类的session数量
        })

    print(f"聚类完成: {clustering_result['n_clusters']} 个聚类")
    if "silhouette_score" in clustering_result:
        print(f"轮廓系数: {clustering_result['silhouette_score']:.3f}")
    
    # 为每个聚类生成名称
    print("\n正在为聚类生成名称...")
    cluster_names = {}
    for cluster_id in range(clustering_result['n_clusters']):
        cluster_texts = cluster_texts_map.get(cluster_id, [])
        if cluster_texts:
            print(f"  生成聚类 {cluster_id} 的名称...")
            cluster_name = generate_cluster_name(cluster_texts, cluster_id)
            cluster_names[cluster_id] = cluster_name
            print(f"    聚类 {cluster_id}: {cluster_name}")
            time.sleep(0.5)  # 避免API限流
        else:
            cluster_names[cluster_id] = f"聚类 {cluster_id}"
    
    # 将聚类名称添加到结果中
    result["cluster_names"] = cluster_names
    clustering_result["cluster_names"] = cluster_names

    return result


def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    # 尝试两个可能的数据目录位置
    data_dir = script_dir / "data_extract"
    if not data_dir.exists():
        # 如果当前目录下没有，尝试父目录
        data_dir = script_dir.parent / "data_extract"

    if not data_dir.exists():
        print(f"错误: 找不到数据目录 {data_dir}")
        return

    # 检查API密钥
    if not GEMINI_API_KEY:
        print("错误: 未设置GEMINI_API_KEY环境变量")
        print("请运行: export GEMINI_API_KEY='your-api-key'")
        return

    # 显示使用的API key（前15个字符）
    print(f"使用的API key: {GEMINI_API_KEY[:15]}...")
    
    # 强制只处理 shop 53
    shop_ids = ["53"]
    print(f"将处理店铺: {shop_ids}")

    # 测试API连接
    print("\n正在测试API连接...")
    try:
        test_result = get_embedding("test", use_mock=False)
        if test_result:
            print(f"✓ API连接成功！Embedding维度: {len(test_result)}")
        else:
            print("✗ API调用失败：返回结果为空")
            print("将继续尝试处理店铺 53...")
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"⚠ API配额限制: {error_msg[:150]}")
            print("将尝试继续处理，如果遇到配额问题将停止")
        else:
            print(f"⚠ API测试警告: {error_msg[:150]}")
            print("将继续尝试处理店铺 53...")

    # 处理店铺
    all_results = {}

    for shop_id in shop_ids:
        try:
            print(f"\n{'='*60}")
            print(f"开始处理店铺 {shop_id}")
            print(f"{'='*60}")
            result = process_shop(shop_id, data_dir, use_mock_embedding=False)
            if result:
                all_results[shop_id] = result
                print(f"\n✓ 店铺 {shop_id} 处理完成！")
        except Exception as e:
            error_msg = str(e)
            print(f"\n✗ 处理店铺 {shop_id} 时出错: {error_msg[:300]}")
            if "429" in error_msg or "quota" in error_msg.lower():
                print("\n错误原因：API配额已用尽")
                print("解决方案：")
                print("  1. 等待配额重置（通常每天重置）")
                print("  2. 检查配额使用情况: https://ai.dev/usage?tab=rate-limit")
                print("  3. 升级到付费计划")
            print("\n无法继续处理，请检查API配置后重试")
            return

    # 保存结果到脚本所在目录的 output 文件夹
    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)  # 确保输出目录存在
    output_file = output_dir / "clustering_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n所有结果已保存到 {output_file}")

    # 打印摘要
    print("\n=== 聚类结果摘要 ===")
    for shop_id, result in all_results.items():
        if result["clustering"]:
            print(f"\n店铺 {shop_id}:")
            print(f"  意图数: {result.get('n_intentions', result.get('n_users', 0))}")
            print(f"  会话数: {result['n_sessions']}")
            print(f"  用户数: {result.get('n_users', 0)}")
            print(f"  聚类数: {result['clustering']['n_clusters']}")
            if "silhouette_score" in result["clustering"]:
                print(f"  轮廓系数: {result['clustering']['silhouette_score']:.3f}")
            print(f"  各聚类的意图数:")
            for cluster_id, intentions in sorted(result["intention_clusters"].items()):
                print(f"    聚类 {cluster_id}: {len(intentions)} 个意图")
            print(f"  各聚类分配的用户数:")
            for cluster_id, users in sorted(result["user_clusters"].items()):
                print(f"    聚类 {cluster_id}: {len(users)} 个用户")


if __name__ == "__main__":
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "../k8s/gcr-key.json")
    main()
