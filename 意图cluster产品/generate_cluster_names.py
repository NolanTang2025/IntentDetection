#!/usr/bin/env python3
"""
聚类名称生成器
根据聚类的业务特征自动生成有意义的聚类名称
"""

import json
from pathlib import Path
from collections import Counter
import re


class ClusterNameGenerator:
    """聚类名称生成器"""
    
    # 阶段映射
    STAGE_MAP = {
        'browsing': '浏览阶段',
        'comparison': '对比阶段',
        'decision': '决策阶段',
        'Browsing Stage': '浏览阶段',
        'Comparison Stage': '对比阶段',
        'Decision Stage': '决策阶段',
        '浏览阶段': '浏览阶段',
        '对比阶段': '对比阶段',
        '决策阶段': '决策阶段',
    }
    
    # 价格敏感度映射
    PRICE_MAP = {
        'budget': '预算型',
        'mid-range': '中端型',
        'premium': '高端型',
        'Budget-Oriented': '预算型',
        'Mid-Range': '中端型',
        'High-Value': '高端型',
        '价格敏感': '预算型',
        '中端价值': '中端型',
        '高端价值': '高端型',
    }
    
    # 参与度映射
    ENGAGEMENT_MAP = {
        'Quick Browser': '快速浏览',
        'Medium Engagement': '中等参与',
        'Deep Researcher': '深度研究',
        '快速浏览': '快速浏览',
        '中等参与': '中等参与',
        '深度研究': '深度研究',
    }
    
    # 产品偏好映射
    PRODUCT_MAP = {
        'Z6 Preference': 'Z6偏好',
        'A1 Preference': 'A1偏好',
        'F1 Preference': 'F1偏好',
        'H02 Preference': 'H02偏好',
        'G1 Preference': 'G1偏好',
        'Multi-Product Comparison': '多产品比较',
    }
    
    # 关注点映射
    CONCERN_MAP = {
        'Function-Oriented': '功能导向',
        'Price-Oriented': '价格导向',
        'Comfort-Oriented': '舒适导向',
        'Effectiveness-Oriented': '效果导向',
        'Comprehensive Concerns': '综合关注',
    }
    
    # 核心需求映射
    NEED_MAP = {
        'Anti-snoring Needs': '止鼾需求',
        'Neck Pain Relief': '颈部疼痛缓解',
        'Sleep Quality Improvement': '睡眠质量改善',
        'Comprehensive Needs': '综合需求',
    }
    
    def __init__(self, language='zh'):
        """
        初始化生成器
        Args:
            language: 'zh' 中文, 'en' 英文
        """
        self.language = language
    
    def extract_characteristics(self, key_characteristics):
        """
        从 key_characteristics 中提取特征
        """
        characteristics = {
            'stage': None,
            'price': None,
            'engagement': None,
            'product': None,
            'concern': None,
            'need': None,
        }
        
        for char in key_characteristics:
            if not char:
                continue
            
            # 购买阶段
            if '购买阶段' in char or 'Purchase Stage' in char or 'purchase stage' in char.lower():
                stage = char.split(':')[1].strip() if ':' in char else None
                if stage:
                    characteristics['stage'] = self.STAGE_MAP.get(stage, stage)
            
            # 价格敏感度
            if '价格敏感度' in char or 'Price Sensitivity' in char or 'price sensitivity' in char.lower():
                price = char.split(':')[1].strip() if ':' in char else None
                if price:
                    characteristics['price'] = self.PRICE_MAP.get(price, price)
            
            # 参与度
            if '参与度' in char or 'Engagement' in char or 'engagement' in char.lower():
                engagement = char.split(':')[1].strip() if ':' in char else None
                if engagement:
                    characteristics['engagement'] = self.ENGAGEMENT_MAP.get(engagement, engagement)
            
            # 产品偏好
            if '产品偏好' in char or 'Product Preference' in char or 'product preference' in char.lower():
                product = char.split(':')[1].strip() if ':' in char else None
                if product:
                    characteristics['product'] = self.PRODUCT_MAP.get(product, product)
            
            # 关注点
            if '关注点' in char or 'Concerns' in char or 'concerns' in char.lower():
                concern = char.split(':')[1].strip() if ':' in char else None
                if concern:
                    characteristics['concern'] = self.CONCERN_MAP.get(concern, concern)
            
            # 核心需求
            if '核心需求' in char or 'Core Need' in char or 'core need' in char.lower():
                need = char.split(':')[1].strip() if ':' in char else None
                if need:
                    characteristics['need'] = self.NEED_MAP.get(need, need)
        
        return characteristics
    
    def generate_short_label(self, characteristics):
        """
        生成简短标签
        格式: 阶段·价格敏感度
        """
        parts = []
        
        # 阶段
        if characteristics.get('stage'):
            parts.append(characteristics['stage'])
        
        # 价格敏感度
        if characteristics.get('price'):
            parts.append(characteristics['price'])
        
        if not parts:
            return None
        
        return '·'.join(parts)
    
    def generate_full_label(self, characteristics):
        """
        生成完整标签
        格式: 阶段·价格敏感度·核心需求/产品偏好
        """
        parts = []
        
        # 阶段
        if characteristics.get('stage'):
            parts.append(characteristics['stage'])
        
        # 价格敏感度
        if characteristics.get('price'):
            parts.append(characteristics['price'])
        
        # 核心需求或产品偏好
        if characteristics.get('need'):
            parts.append(characteristics['need'])
        elif characteristics.get('product'):
            parts.append(characteristics['product'])
        elif characteristics.get('concern'):
            parts.append(characteristics['concern'])
        
        if not parts:
            return None
        
        return '·'.join(parts)
    
    def generate_user_segment_name(self, characteristics):
        """
        生成用户分群名称
        优先使用核心需求，其次使用产品偏好
        """
        if characteristics.get('need'):
            return characteristics['need'] + '用户'
        elif characteristics.get('product'):
            return characteristics['product'] + '用户'
        elif characteristics.get('concern'):
            return characteristics['concern'] + '用户'
        elif characteristics.get('stage'):
            return characteristics['stage'] + '用户'
        else:
            return '综合用户'
    
    def generate_cluster_name(self, cluster_id, characteristics):
        """
        生成聚类名称
        """
        short_label = self.generate_short_label(characteristics)
        if short_label:
            return short_label
        else:
            return f"聚类 {cluster_id}"
    
    def process_business_insights(self, business_insights):
        """
        处理业务洞察数据，生成聚类名称
        """
        updated_insights = []
        
        for insight in business_insights:
            cluster_id = insight.get('cluster_id', '')
            
            # 提取特征
            key_characteristics = insight.get('key_characteristics', [])
            characteristics = self.extract_characteristics(key_characteristics)
            
            # 生成名称
            cluster_name = self.generate_cluster_name(cluster_id, characteristics)
            user_segment_name = self.generate_user_segment_name(characteristics)
            full_label = self.generate_full_label(characteristics)
            
            # 更新 insight
            updated_insight = insight.copy()
            updated_insight['cluster_name'] = cluster_name
            updated_insight['user_segment_name'] = user_segment_name
            if full_label:
                updated_insight['full_label'] = full_label
            
            updated_insights.append(updated_insight)
        
        return updated_insights
    
    def process_multi_shop_data(self, input_file, output_file=None):
        """
        处理多店铺数据文件
        """
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"错误: 文件不存在 {input_file}")
            return False
        
        # 读取文件内容
        content = input_path.read_text(encoding='utf-8')
        
        # 提取 shopData 对象
        # 查找 shopData[shopId] = { ... } 的模式
        shop_data_pattern = r'shopData\[(\d+|"YUP")\]\s*=\s*({[^}]+(?:{[^}]+}[^}]*)*})'
        
        # 更简单的方法：直接解析 JavaScript 对象
        # 提取所有 shopData[XX] = {...} 块
        shop_blocks = re.findall(r'shopData\[(\d+|"YUP")\]\s*=\s*(\{[^}]*(?:\{[^}]*\}[^}]*)*\})', content, re.DOTALL)
        
        print(f"找到 {len(shop_blocks)} 个店铺数据块")
        
        # 处理每个店铺
        updated_content = content
        for shop_id, shop_data_str in shop_blocks:
            try:
                # 解析 JSON (需要处理 JavaScript 注释和尾随逗号)
                shop_data_str_clean = shop_data_str
                # 移除注释
                shop_data_str_clean = re.sub(r'//.*?$', '', shop_data_str_clean, flags=re.MULTILINE)
                # 移除尾随逗号
                shop_data_str_clean = re.sub(r',\s*}', '}', shop_data_str_clean)
                shop_data_str_clean = re.sub(r',\s*]', ']', shop_data_str_clean)
                
                shop_data = json.loads(shop_data_str_clean)
                
                # 处理 businessInsights
                if 'businessInsights' in shop_data:
                    updated_insights = self.process_business_insights(shop_data['businessInsights'])
                    shop_data['businessInsights'] = updated_insights
                    
                    # 更新内容
                    # 这里需要更复杂的替换逻辑，暂时先输出到新文件
                    print(f"  处理店铺 {shop_id}: {len(updated_insights)} 个聚类")
            
            except Exception as e:
                print(f"  处理店铺 {shop_id} 时出错: {e}")
                continue
        
        return True


def main():
    """主函数"""
    import sys
    
    # 默认处理 multi_shop_data.js
    input_file = Path(__file__).parent / 'visualization_dashboard' / 'multi_shop_data.js'
    
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"错误: 文件不存在 {input_file}")
        return
    
    generator = ClusterNameGenerator(language='zh')
    
    # 读取并解析文件
    content = input_file.read_text(encoding='utf-8')
    
    # 提取所有 shopData[XX] 定义
    # 使用更精确的正则表达式
    pattern = r'shopData\[(\d+|"YUP")\]\s*=\s*(\{[^}]*(?:\{[^}]*\}[^}]*)*\})'
    
    matches = list(re.finditer(pattern, content, re.DOTALL))
    print(f"找到 {len(matches)} 个店铺数据定义")
    
    # 处理每个匹配
    offset = 0
    for match in matches:
        shop_id = match.group(1).strip('"')
        shop_data_str = match.group(2)
        
        try:
            # 清理 JavaScript 代码
            shop_data_str_clean = shop_data_str
            # 移除单行注释
            shop_data_str_clean = re.sub(r'//.*?$', '', shop_data_str_clean, flags=re.MULTILINE)
            # 移除尾随逗号
            shop_data_str_clean = re.sub(r',(\s*[}\]])', r'\1', shop_data_str_clean)
            
            # 解析 JSON
            shop_data = json.loads(shop_data_str_clean)
            
            # 处理 businessInsights
            if 'businessInsights' in shop_data and isinstance(shop_data['businessInsights'], list):
                updated_insights = generator.process_business_insights(shop_data['businessInsights'])
                
                # 生成新的 JavaScript 代码
                updated_str = json.dumps(updated_insights, ensure_ascii=False, indent=2)
                # 转换为 JavaScript 格式
                updated_str = updated_str.replace('"', '"').replace('"', '"')
                
                # 替换原内容
                # 这里需要找到 businessInsights 的准确位置
                print(f"处理店铺 {shop_id}: {len(updated_insights)} 个聚类")
                for i, insight in enumerate(updated_insights):
                    print(f"  Cluster {insight['cluster_id']}: {insight['cluster_name']} / {insight['user_segment_name']}")
        
        except Exception as e:
            print(f"处理店铺 {shop_id} 时出错: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n建议: 手动更新 multi_shop_data.js 文件中的 cluster_name, user_segment_name 和 full_label 字段")


if __name__ == '__main__':
    main()

