#!/usr/bin/env python3
"""
脚本用于从 raw_data1106.csv 中提取：
1. name 为 "analyze_intent_and_rate_tags" 的记录
2. output 字段的值，只保留到 "match_analysis" 部分结束
3. userId, sessionId, timestamp 的值
"""

import csv
import json
import re
from pathlib import Path

def extract_output_until_match_analysis(output_text):
    """
    从 output 文本中提取到 match_analysis 部分结束为止的内容。
    如果 output 是 JSON 格式，尝试解析并只保留到 match_analysis 的部分。
    """
    if not output_text or output_text.strip() == '':
        return ''
    
    # CSV 中的字符串可能被转义，需要先解码
    # 如果包含转义的引号，先处理
    if '\\"' in output_text or '\\n' in output_text:
        # 尝试解码转义字符
        try:
            # Python 的字符串字面量解码
            cleaned = output_text.encode().decode('unicode_escape')
        except:
            cleaned = output_text
    else:
        cleaned = output_text
    
    # 移除可能的代码块标记（如 ```json 和 ```）
    cleaned = cleaned.strip()
    has_code_block = False
    if cleaned.startswith('```'):
        has_code_block = True
        # 找到第一个 ``` 和最后一个 ```
        first_backtick = cleaned.find('```')
        if first_backtick != -1:
            # 跳过开头的 ```json 或 ```
            next_newline = cleaned.find('\n', first_backtick)
            if next_newline != -1:
                cleaned = cleaned[next_newline + 1:]
            else:
                cleaned = cleaned[first_backtick + 3:]
        
        # 移除结尾的 ```
        if cleaned.rstrip().endswith('```'):
            cleaned = cleaned.rstrip()[:-3].rstrip()
    
    # 首先尝试用字符串方法：找到 tags 位置并截取到它之前
    tags_pos = cleaned.find('"tags"')
    match_analysis_pos = cleaned.find('"match_analysis"')
    
    if tags_pos != -1 and match_analysis_pos != -1 and tags_pos > match_analysis_pos:
        # 找到 tags 之前的内容
        before_tags = cleaned[:tags_pos].rstrip()
        
        # 找到 intent_score（如果存在）
        intent_score_pos = before_tags.find('"intent_score"')
        if intent_score_pos != -1:
            # 找到 intent_score 的值（通常是数字）
            colon_pos = before_tags.find(':', intent_score_pos)
            if colon_pos != -1:
                # 跳过空格，找到数字
                value_start = colon_pos + 1
                while value_start < len(before_tags) and before_tags[value_start] in ' \n\t':
                    value_start += 1
                # 找到数字结束
                value_end = value_start
                while value_end < len(before_tags) and (before_tags[value_end].isdigit() or before_tags[value_end] == '.'):
                    value_end += 1
                # intent_score 值后可能是逗号，然后是 tags
                # 我们需要移除逗号，然后添加 } 来结束整个 JSON 对象
                # 找到逗号位置
                comma_pos = value_end
                while comma_pos < len(before_tags) and before_tags[comma_pos] in ' \n\t':
                    comma_pos += 1
                if comma_pos < len(before_tags) and before_tags[comma_pos] == ',':
                    # 移除逗号，添加 }
                    result = before_tags[:comma_pos].rstrip() + '\n}'
                    if has_code_block:
                        result = '```json\n' + result + '\n```'
                    return result
                else:
                    # 如果没有逗号，直接添加 }
                    result = before_tags[:value_end].rstrip() + '\n}'
                    if has_code_block:
                        result = '```json\n' + result + '\n```'
                    return result
        
        # 如果没有 intent_score 或找不到，找到最后一个 }
        # 查找 "\n}" 模式（JSON 对象结束）
        last_brace = before_tags.rfind('\n}')
        if last_brace != -1:
            result = before_tags[:last_brace + 2].rstrip()
            if has_code_block:
                result = '```json\n' + result + '\n```'
            return result
        # 如果找不到 \n}，找最后一个 }
        last_brace = before_tags.rfind('}')
        if last_brace != -1:
            result = before_tags[:last_brace + 1].rstrip()
            if has_code_block:
                result = '```json\n' + result + '\n```'
            return result
    
    # 如果字符串方法失败，尝试解析 JSON
    try:
        data = json.loads(cleaned)
        
        # 如果包含 intent 字段，只保留到 match_analysis
        if isinstance(data, dict) and 'intent' in data:
            intent = data['intent']
            if isinstance(intent, dict) and 'match_analysis' in intent:
                # 创建一个新的数据结构，只包含到 match_analysis 的部分
                filtered_data = {
                    'intent': {
                        'core_interests': intent.get('core_interests', []),
                        'product_focus': intent.get('product_focus', {}),
                        'purchase_signals': intent.get('purchase_signals', {}),
                        'behavior_summary': intent.get('behavior_summary', {}),
                        'match_analysis': intent.get('match_analysis', {})
                    }
                }
                # 如果有 intent_score，也保留（但确保没有 tags）
                if 'intent_score' in data and 'tags' not in str(data.get('intent_score', '')):
                    filtered_data['intent_score'] = data['intent_score']
                
                result = json.dumps(filtered_data, indent=2, ensure_ascii=False)
                # 如果原来有代码块标记，加上
                if has_code_block:
                    result = '```json\n' + result + '\n```'
                return result
            else:
                # 如果没有 match_analysis，返回原始 JSON（但移除 tags）
                if 'tags' in data:
                    data = {k: v for k, v in data.items() if k != 'tags'}
                result = json.dumps(data, indent=2, ensure_ascii=False)
                if has_code_block:
                    result = '```json\n' + result + '\n```'
                return result
        else:
            # 如果没有 intent，返回原始 JSON（但移除 tags）
            if isinstance(data, dict) and 'tags' in data:
                data = {k: v for k, v in data.items() if k != 'tags'}
            result = json.dumps(data, indent=2, ensure_ascii=False)
            if has_code_block:
                result = '```json\n' + result + '\n```'
            return result
    
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        # 如果解析失败，尝试用字符串方法找到 match_analysis 部分
        # 查找 "match_analysis" 及其内容，直到对象结束
        match_pos = cleaned.find('"match_analysis"')
        if match_pos != -1:
            # 找到 match_analysis 对象的开始位置（第一个 {）
            start_pos = cleaned.find('{', match_pos)
            if start_pos != -1:
                # 计算括号匹配，找到 match_analysis 对象的结束位置
                brace_count = 0
                in_string = False
                escape_next = False
                
                for i in range(start_pos, len(cleaned)):
                    char = cleaned[i]
                    
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                # 找到 match_analysis 对象结束位置
                                match_analysis_end = i + 1
                                # 找到 intent 对象的结束（在 match_analysis 之后）
                                # 查找 "}\n  }" 模式（intent 对象结束）
                                intent_end_pattern = cleaned.find('\n  }', match_analysis_end)
                                if intent_end_pattern != -1:
                                    intent_end = intent_end_pattern + 4  # 包含 "}\n  }"
                                    # 检查是否有 intent_score
                                    score_pos = cleaned.find('"intent_score"', match_analysis_end)
                                    if score_pos != -1 and score_pos < intent_end_pattern:
                                        # 找到包含 intent_score 的完整结构
                                        # 查找最外层的 } 来结束整个 JSON
                                        final_brace = cleaned.find('\n}', intent_end_pattern)
                                        if final_brace != -1:
                                            result = cleaned[:final_brace + 2].rstrip()
                                            if has_code_block:
                                                result = '```json\n' + result + '\n```'
                                            return result
                                    
                                    # 如果没有 intent_score，直接截取到 intent 结束
                                    result = cleaned[:intent_end].rstrip()
                                    if has_code_block:
                                        result = '```json\n' + result + '\n```'
                                    return result
                                
                                # 如果找不到 intent 结束，至少截取到 match_analysis 结束
                                result = cleaned[:match_analysis_end].rstrip()
                                if has_code_block:
                                    result = '```json\n' + result + '\n```'
                                return result
        
        # 如果找不到，返回原始文本（但尝试移除 tags 部分）
        if '"tags"' in cleaned:
            tags_pos = cleaned.find('"tags"')
            if tags_pos != -1:
                # 找到 tags 之前的最后一个 }
                before_tags = cleaned[:tags_pos].rstrip()
                # 找到 before_tags 中最后一个完整的 JSON 结构
                last_brace = before_tags.rfind('\n}')
                if last_brace != -1:
                    result = before_tags[:last_brace + 2].rstrip()
                    if has_code_block:
                        result = '```json\n' + result + '\n```'
                    return result
        
        # 如果都找不到，返回原始文本
        return output_text

def main():
    input_file = Path('raw_data1106.csv')
    output_file = Path('extracted_data.csv')
    
    if not input_file.exists():
        print(f"错误: 找不到文件 {input_file}")
        return
    
    results = []
    
    print(f"正在读取 {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是表头）
            # 检查 name 是否为 "analyze_intent_and_rate_tags"
            if row.get('name') == 'analyze_intent_and_rate_tags':
                # 提取所需字段
                user_id = row.get('userId', '')
                session_id = row.get('sessionId', '')
                timestamp = row.get('timestamp', '')
                output = row.get('output', '')
                
                # 处理 output，只保留到 match_analysis 部分
                filtered_output = extract_output_until_match_analysis(output)
                
                results.append({
                    'user_id': user_id,
                    'session_id': session_id,
                    'timestamp': timestamp,
                    'output': filtered_output
                })
                
                print(f"处理第 {row_num} 行: user_id={user_id}, session_id={session_id}")
    
    # 写入结果到新的 CSV 文件
    print(f"\n找到 {len(results)} 条记录")
    print(f"正在写入结果到 {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        if results:
            fieldnames = ['user_id', 'session_id', 'timestamp', 'output']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    
    print(f"完成! 结果已保存到 {output_file}")
    
    # 同时保存为 JSON 格式（可选，便于查看）
    json_output_file = Path('extracted_data.json')
    with open(json_output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"JSON 格式结果已保存到 {json_output_file}")

if __name__ == '__main__':
    main()

