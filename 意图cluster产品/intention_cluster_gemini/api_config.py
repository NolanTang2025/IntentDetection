#!/usr/bin/env python3
"""
API配置管理脚本
允许用户设置和测试API key
"""
import os
import sys
from pathlib import Path

def set_api_key():
    """交互式设置API key"""
    print("=" * 60)
    print("Gemini API Key 配置工具")
    print("=" * 60)
    print()
    
    # 检查现有的API key
    current_key = os.environ.get("GEMINI_API_KEY", "")
    if current_key:
        print(f"当前环境变量中的API key: {current_key[:15]}...")
        print()
    
    # 提示用户输入新的API key
    print("请输入你的Gemini API key (或按Enter使用当前环境变量):")
    new_key = input().strip()
    
    if not new_key:
        if current_key:
            print(f"使用当前API key: {current_key[:15]}...")
            return current_key
        else:
            print("❌ 未输入API key，且环境变量中也未设置")
            return None
    else:
        print(f"✓ 已设置新的API key: {new_key[:15]}...")
        return new_key

def test_api_key(api_key):
    """测试API key是否可用"""
    print("\n正在测试API连接...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        result = genai.embed_content(
            model="models/embedding-001",
            content="test",
            task_type="clustering"
        )
        
        if result and 'embedding' in result:
            print(f"✓ API连接成功！")
            print(f"✓ Embedding维度: {len(result['embedding'])}")
            return True
        else:
            print("✗ API响应异常")
            return False
    except Exception as e:
        error_msg = str(e)
        print(f"✗ API测试失败: {error_msg[:200]}")
        if "429" in error_msg or "quota" in error_msg.lower():
            print("⚠ 配额已用尽，请检查配额或使用其他API key")
        return False

def save_to_env_file(api_key):
    """保存API key到.env文件"""
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"
    
    try:
        # 读取现有内容
        existing_lines = []
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip().startswith("GEMINI_API_KEY="):
                        existing_lines.append(line.rstrip())
        
        # 添加新的API key
        existing_lines.append(f"GEMINI_API_KEY={api_key}")
        
        # 写入文件
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("\n".join(existing_lines) + "\n")
        
        print(f"\n✓ API key已保存到: {env_file}")
        return True
    except Exception as e:
        print(f"\n⚠ 保存到.env文件失败: {e}")
        return False

if __name__ == "__main__":
    api_key = set_api_key()
    if api_key:
        # 测试API key
        if test_api_key(api_key):
            # 询问是否保存
            print("\n是否保存API key到配置文件? (y/n): ", end="")
            save = input().strip().lower()
            if save == 'y':
                save_to_env_file(api_key)
            else:
                print("\n提示：可以手动运行以下命令设置环境变量:")
                print(f"export GEMINI_API_KEY='{api_key}'")
        else:
            print("\n⚠ API key测试失败，但你可以继续尝试运行聚类脚本")
            print(f"export GEMINI_API_KEY='{api_key}'")
    else:
        print("\n❌ 未设置API key")
        sys.exit(1)

