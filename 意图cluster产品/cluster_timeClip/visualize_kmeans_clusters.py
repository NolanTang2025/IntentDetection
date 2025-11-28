#!/usr/bin/env python3
"""
K-Means聚类结果散点图可视化
使用PCA或t-SNE降维到2D进行可视化
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

# 设置中文字体（如果系统支持）
try:
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

def load_cluster_data(shop_id):
    """加载聚类结果数据"""
    cluster_file = Path(f'business_cluster_results_shop_{shop_id}.json')
    if not cluster_file.exists():
        print(f"❌ 文件不存在: {cluster_file}")
        return None
    
    with open(cluster_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def extract_features(segments):
    """从segments中提取特征（支持电商和金融两种场景）"""
    # 检测是否为金融场景（通过检查是否有金融特征字段）
    is_financial = any('kyc_started' in seg or 'has_transaction' in seg for seg in segments)
    
    if is_financial:
        # 金融场景特征
        feature_cols = [
            'kyc_started',
            'kyc_event_count_log',
            'has_transaction',
            'transaction_completed',
            'payment_related_events_log',
            'recharge_related_events_log',
            'voucher_related_events_log',
            'intent_score',
            'duration_minutes_log',
            'record_count_log'
        ]
    else:
        # 电商场景特征
    feature_cols = [
        'intent_score',
        'purchase_stage',
        'product_preference',
        'concern_focus',
        'core_need',
        'price_sensitivity',
        'record_count_log',
        'duration_minutes_log'
    ]
    
    features = []
    cluster_labels = []
    
    for seg in segments:
        feature_vector = []
        for col in feature_cols:
            value = seg.get(col, 0)
            if isinstance(value, (int, float)):
                feature_vector.append(float(value))
            else:
                feature_vector.append(0.0)
        
        features.append(feature_vector)
        cluster_labels.append(seg.get('business_cluster', 0))
    
    return np.array(features), np.array(cluster_labels)

def plot_kmeans_scatter(shop_id, method='pca', figsize=(12, 10)):
    """绘制K-Means聚类散点图"""
    
    # 加载数据
    data = load_cluster_data(shop_id)
    if data is None:
        return
    
    segments = data.get('segments', [])
    if len(segments) == 0:
        print(f"❌ 店铺 {shop_id} 没有数据")
        return
    
    print(f"📊 正在为店铺 {shop_id} 生成散点图...")
    print(f"   数据量: {len(segments)} 个片段")
    
    # 提取特征
    X, y = extract_features(segments)
    print(f"   特征维度: {X.shape}")
    
    # 降维
    if method == 'pca':
        print("   使用PCA降维到2D...")
        reducer = PCA(n_components=2, random_state=42)
        X_reduced = reducer.fit_transform(X)
        explained_var = reducer.explained_variance_ratio_
        print(f"   前两个主成分解释的方差比例: {explained_var[0]:.2%}, {explained_var[1]:.2%}")
        print(f"   累计解释方差: {sum(explained_var):.2%}")
    elif method == 'tsne':
        print("   使用t-SNE降维到2D（这可能需要一些时间）...")
        reducer = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=1000)
        X_reduced = reducer.fit_transform(X)
    else:
        raise ValueError(f"未知的降维方法: {method}")
    
    # 创建图形
    fig, ax = plt.subplots(figsize=figsize)
    
    # 获取唯一的聚类ID
    unique_clusters = sorted(np.unique(y))
    n_clusters = len(unique_clusters)
    
    # 生成颜色映射
    colors = plt.cm.tab20(np.linspace(0, 1, n_clusters))
    
    # 为每个聚类绘制散点
    for i, cluster_id in enumerate(unique_clusters):
        mask = y == cluster_id
        cluster_points = X_reduced[mask]
        cluster_size = np.sum(mask)
        
        ax.scatter(
            cluster_points[:, 0],
            cluster_points[:, 1],
            c=[colors[i]],
            label=f'Cluster {cluster_id} (n={cluster_size})',
            alpha=0.6,
            s=50,
            edgecolors='black',
            linewidths=0.5
        )
    
    # 设置标题和标签
    method_name = 'PCA' if method == 'pca' else 't-SNE'
    ax.set_title(f'Shop {shop_id} - K-Means Clustering Scatter Plot ({method_name} Dimensionality Reduction)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(f'{method_name} First Dimension', fontsize=12)
    ax.set_ylabel(f'{method_name} Second Dimension', fontsize=12)
    
    # 添加图例
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, ncol=1)
    
    # 添加网格
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加统计信息
    stats_text = f'Total Segments: {len(segments)}\nClusters: {n_clusters}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # 保存图片
    output_file = f'kmeans_scatter_shop_{shop_id}_{method}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 散点图已保存: {output_file}")
    
    plt.close()
    
    return output_file

def plot_all_shops(shops=[28, 29, 39, 49, 53, 'YUP'], method='pca'):
    """为所有店铺生成散点图"""
    print("="*80)
    print(f"生成所有店铺的K-Means聚类散点图 (方法: {method.upper()})")
    print("="*80)
    
    results = []
    for shop_id in shops:
        try:
            output_file = plot_kmeans_scatter(shop_id, method=method)
            if output_file:
                results.append((shop_id, output_file))
        except Exception as e:
            print(f"❌ 店铺 {shop_id} 生成失败: {e}")
    
    print("\n" + "="*80)
    print("生成完成!")
    print("="*80)
    for shop_id, output_file in results:
        print(f"  店铺 {shop_id}: {output_file}")
    
    return results

if __name__ == '__main__':
    import sys
    
    # 默认使用PCA（更快），也可以使用t-SNE（更准确但更慢）
    method = 'pca'
    if len(sys.argv) > 1:
        method = sys.argv[1].lower()
        if method not in ['pca', 'tsne']:
            print("❌ 无效的方法，使用 'pca' 或 'tsne'")
            method = 'pca'
    
    # 生成所有店铺的散点图
    plot_all_shops(method=method)
    
    # 也可以单独生成某个店铺的图
    # plot_kmeans_scatter(28, method='pca')

