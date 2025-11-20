#!/usr/bin/env python3
"""
聚类结果可视化工具
"""

import json
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

def analyze_clusters():
    """分析并可视化聚类结果"""
    
    # 读取结果
    with open('cluster_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    segments = data['segments']
    df = pd.DataFrame(segments)
    
    print("="*80)
    print("聚类分析统计")
    print("="*80)
    
    # 基本统计
    print(f"\n总片段数: {len(segments)}")
    print(f"总用户数: {df['user_id'].nunique()}")
    print(f"平均片段时长: {df['duration_minutes'].mean():.2f} 分钟")
    print(f"平均片段记录数: {df['record_count'].mean():.2f}")
    
    # KMeans 聚类统计
    print(f"\nKMeans 聚类统计:")
    kmeans_clusters = Counter(df['kmeans_cluster'])
    print(f"  聚类数: {len(kmeans_clusters)}")
    for cluster_id, count in sorted(kmeans_clusters.items()):
        print(f"    聚类 {cluster_id}: {count} 个片段 ({count/len(segments)*100:.1f}%)")
    
    # DBSCAN 聚类统计
    print(f"\nDBSCAN 聚类统计:")
    dbscan_clusters = Counter(df['dbscan_cluster'])
    noise_count = dbscan_clusters.get(-1, 0)
    print(f"  聚类数: {len([k for k in dbscan_clusters.keys() if k != -1])}")
    print(f"  噪声点: {noise_count} ({noise_count/len(segments)*100:.1f}%)")
    for cluster_id, count in sorted(dbscan_clusters.items()):
        if cluster_id != -1:
            print(f"    聚类 {cluster_id}: {count} 个片段 ({count/len(segments)*100:.1f}%)")
    
    # 每个聚类的关键词提取（简化版）
    print(f"\n各KMeans聚类的主要意图主题（前5个）:")
    for cluster_id in sorted(kmeans_clusters.keys()):
        cluster_segments = df[df['kmeans_cluster'] == cluster_id]
        if len(cluster_segments) > 0:
            # 提取文本中的关键词（简单方法：取最常见的词）
            all_text = ' '.join(cluster_segments['text'].astype(str))
            words = all_text.lower().split()
            # 过滤常见词
            common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were']
            words = [w for w in words if len(w) > 3 and w not in common_words]
            word_counts = Counter(words)
            top_words = [word for word, count in word_counts.most_common(5)]
            print(f"  聚类 {cluster_id} ({len(cluster_segments)} 个片段): {', '.join(top_words)}")
    
    # 保存统计报告
    with open('cluster_statistics.txt', 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("聚类分析统计报告\n")
        f.write("="*80 + "\n\n")
        f.write(f"总片段数: {len(segments)}\n")
        f.write(f"总用户数: {df['user_id'].nunique()}\n")
        f.write(f"平均片段时长: {df['duration_minutes'].mean():.2f} 分钟\n")
        f.write(f"平均片段记录数: {df['record_count'].mean():.2f}\n\n")
        
        f.write("KMeans 聚类分布:\n")
        for cluster_id, count in sorted(kmeans_clusters.items()):
            f.write(f"  聚类 {cluster_id}: {count} 个片段 ({count/len(segments)*100:.1f}%)\n")
        
        f.write("\n各聚类主要意图主题:\n")
        for cluster_id in sorted(kmeans_clusters.keys()):
            cluster_segments = df[df['kmeans_cluster'] == cluster_id]
            if len(cluster_segments) > 0:
                all_text = ' '.join(cluster_segments['text'].astype(str))
                words = all_text.lower().split()
                common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were']
                words = [w for w in words if len(w) > 3 and w not in common_words]
                word_counts = Counter(words)
                top_words = [word for word, count in word_counts.most_common(10)]
                f.write(f"  聚类 {cluster_id}: {', '.join(top_words)}\n")
    
    print(f"\n统计报告已保存到: cluster_statistics.txt")
    
    # 尝试创建可视化图表
    try:
        # 聚类大小分布
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # KMeans 聚类大小
        cluster_sizes = [kmeans_clusters.get(i, 0) for i in range(max(kmeans_clusters.keys())+1)]
        axes[0].bar(range(len(cluster_sizes)), cluster_sizes)
        axes[0].set_xlabel('聚类 ID')
        axes[0].set_ylabel('片段数')
        axes[0].set_title('KMeans 聚类大小分布')
        axes[0].grid(True, alpha=0.3)
        
        # 片段时长分布
        axes[1].hist(df['duration_minutes'], bins=50, edgecolor='black', alpha=0.7)
        axes[1].set_xlabel('时长 (分钟)')
        axes[1].set_ylabel('片段数')
        axes[1].set_title('片段时长分布')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('cluster_visualization.png', dpi=150, bbox_inches='tight')
        print("可视化图表已保存到: cluster_visualization.png")
        plt.close()
    except Exception as e:
        print(f"创建可视化图表时出错: {e}")

if __name__ == '__main__':
    analyze_clusters()

