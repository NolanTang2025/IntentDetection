#!/usr/bin/env python3
"""
合并 Shop 53 用户轨迹中连续相同聚类的意图
当用户路径中的连续几条意图都属于同一个聚类时，将这些意图合并为一个segment展示
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
DASHBOARD_DIR = BASE_DIR / 'visualization_dashboard'
CLUSTER_DIR = BASE_DIR / 'cluster_timeClip'

def merge_consecutive_clusters(trajectories):
    """合并用户轨迹中连续相同聚类的意图"""
    merged_trajectories = []
    
    for trajectory in trajectories:
        user_id = trajectory['user_id']
        segments = trajectory.get('segments', [])
        
        if not segments:
            merged_trajectories.append(trajectory)
            continue
        
        # 按时间排序
        segments.sort(key=lambda x: x.get('start_time', ''))
        
        # 合并连续相同聚类的segment
        merged_segments = []
        current_segment = None
        
        for segment in segments:
            cluster_id = str(segment.get('cluster_id', ''))
            
            if current_segment is None:
                # 第一个segment
                current_segment = segment.copy()
                current_segment['merged_count'] = 1
                current_segment['original_segments'] = [segment.get('segment_id', '')]
            elif current_segment.get('cluster_id') == cluster_id:
                # 相同聚类，合并
                current_segment['merged_count'] = current_segment.get('merged_count', 1) + 1
                current_segment['original_segments'].append(segment.get('segment_id', ''))
                
                # 更新结束时间（使用最新的）
                current_segment['end_time'] = segment.get('end_time', current_segment.get('end_time', ''))
                
                # 累加时长和记录数
                current_segment['duration_seconds'] = (current_segment.get('duration_seconds', 0) or 0) + (segment.get('duration_seconds', 0) or 0)
                current_segment['duration_minutes'] = current_segment.get('duration_minutes', 0) + segment.get('duration_minutes', 0)
                current_segment['record_count'] = current_segment.get('record_count', 0) + segment.get('record_count', 0)
                
                # 更新segment_id（使用合并后的标识）
                current_segment['segment_id'] = f"{user_id}_merged_{cluster_id}_{len(merged_segments)}"
            else:
                # 不同聚类，保存当前segment，开始新的segment
                merged_segments.append(current_segment)
                current_segment = segment.copy()
                current_segment['merged_count'] = 1
                current_segment['original_segments'] = [segment.get('segment_id', '')]
        
        # 添加最后一个segment
        if current_segment is not None:
            merged_segments.append(current_segment)
        
        # 更新segment_index
        for idx, seg in enumerate(merged_segments):
            seg['segment_index'] = idx
        
        # 重新计算统计信息
        unique_clusters = set(str(seg.get('cluster_id', '')) for seg in merged_segments)
        total_duration = sum(seg.get('duration_seconds', 0) or 0 for seg in merged_segments)
        total_records = sum(seg.get('record_count', 0) for seg in merged_segments)
        
        merged_trajectory = {
            'user_id': user_id,
            'segment_count': len(merged_segments),
            'unique_clusters': len(unique_clusters),
            'cluster_ids': sorted(list(unique_clusters)),
            'total_duration': total_duration,
            'total_records': total_records,
            'segments': merged_segments
        }
        
        merged_trajectories.append(merged_trajectory)
    
    return merged_trajectories

def update_shop53_data():
    """更新 Shop 53 的数据，合并连续相同聚类的意图"""
    print("=" * 80)
    print("合并 Shop 53 用户轨迹中连续相同聚类的意图")
    print("=" * 80)
    
    # 读取 data_shop_53.js
    data_file = DASHBOARD_DIR / 'data_shop_53.js'
    if not data_file.exists():
        print(f"❌ 错误: 找不到文件 {data_file}")
        return False
    
    print(f"\n[1/4] 读取 data_shop_53.js...")
    with open(data_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 userTrajectories
    trajectories_match = re.search(r'const userTrajectories = (\[.*?\]);', content, re.DOTALL)
    if not trajectories_match:
        print("❌ 错误: 无法找到 userTrajectories 数据")
        return False
    
    trajectories_str = trajectories_match.group(1)
    trajectories = json.loads(trajectories_str)
    
    print(f"  ✓ 找到 {len(trajectories)} 个用户轨迹")
    
    # 统计合并前的信息
    total_segments_before = sum(t.get('segment_count', 0) for t in trajectories)
    print(f"  ✓ 合并前总片段数: {total_segments_before}")
    
    # 合并连续相同聚类的意图
    print(f"\n[2/4] 合并连续相同聚类的意图...")
    merged_trajectories = merge_consecutive_clusters(trajectories)
    
    # 统计合并后的信息
    total_segments_after = sum(t.get('segment_count', 0) for t in merged_trajectories)
    reduction = total_segments_before - total_segments_after
    reduction_percent = (reduction / total_segments_before * 100) if total_segments_before > 0 else 0
    
    print(f"  ✓ 合并后总片段数: {total_segments_after}")
    print(f"  ✓ 减少了 {reduction} 个片段 ({reduction_percent:.1f}%)")
    
    # 检查合并效果
    merged_count = 0
    for traj in merged_trajectories:
        for seg in traj.get('segments', []):
            if seg.get('merged_count', 1) > 1:
                merged_count += 1
    
    print(f"  ✓ 有 {merged_count} 个合并后的segment（包含多个原始意图）")
    
    # 备份原文件
    print(f"\n[3/4] 备份原文件...")
    backup_file = data_file.with_suffix('.js.bak_merge')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ 已备份到: {backup_file}")
    
    # 更新文件内容
    print(f"\n[4/4] 更新 data_shop_53.js...")
    new_trajectories_str = json.dumps(merged_trajectories, indent=2, ensure_ascii=False)
    new_content = content.replace(
        f'const userTrajectories = {trajectories_str};',
        f'const userTrajectories = {new_trajectories_str};'
    )
    
    with open(data_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✓ 已更新: {data_file}")
    
    # 更新 multi_shop_data.js
    print(f"\n[5/5] 更新 multi_shop_data.js...")
    multi_shop_file = DASHBOARD_DIR / 'multi_shop_data.js'
    if multi_shop_file.exists():
        with open(multi_shop_file, 'r', encoding='utf-8') as f:
            multi_content = f.read()
        
        # 查找 shop 53 的 userTrajectories
        shop53_pattern = r'(shopData\[["\']?53["\']?\]\s*=\s*\{[^;]*?userTrajectories:\s*)(\[.*?\])([^;]*?\};)'
        shop53_match = re.search(shop53_pattern, multi_content, re.DOTALL)
        
        if shop53_match:
            new_multi_content = multi_content.replace(
                shop53_match.group(2),
                new_trajectories_str
            )
            
            # 备份
            backup_multi = multi_shop_file.with_suffix('.js.bak_merge')
            with open(backup_multi, 'w', encoding='utf-8') as f:
                f.write(multi_content)
            
            with open(multi_shop_file, 'w', encoding='utf-8') as f:
                f.write(new_multi_content)
            
            print(f"  ✓ 已更新: {multi_shop_file}")
        else:
            print(f"  ⚠️  未找到 shop 53 的 userTrajectories，需要重新生成 multi_shop_data.js")
    
    print("\n" + "=" * 80)
    print("✅ Shop 53 用户轨迹合并完成！")
    print("=" * 80)
    print(f"\n合并统计:")
    print(f"  合并前片段数: {total_segments_before}")
    print(f"  合并后片段数: {total_segments_after}")
    print(f"  减少片段数: {reduction} ({reduction_percent:.1f}%)")
    print(f"  合并后的segment数: {merged_count}")
    
    return True

if __name__ == '__main__':
    update_shop53_data()

