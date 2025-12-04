#!/usr/bin/env python3
"""
检查Gemini API密钥是否设置并测试连接
"""

import os
import sys

def check_api_key():
    print("=" * 70)
    print("Gemini API 密钥检查工具")
    print("=" * 70)
    
    # 方法1: 检查环境变量
    print("\n[方法1] 检查环境变量 GEMINI_API_KEY")
    env_key = os.getenv('GEMINI_API_KEY', '')
    if env_key:
        if env_key == 'YOUR_GEMINI_API_KEY':
            print("   ✗ 未设置（仍为默认占位符）")
            env_key = None
        else:
            print(f"   ✓ 已设置")
            print(f"   密钥长度: {len(env_key)} 字符")
            print(f"   前10个字符: {env_key[:10]}...")
    else:
        print("   ✗ 未设置")
        env_key = None
    
    # 方法2: 检查脚本中的硬编码值
    print("\n[方法2] 检查脚本中的硬编码值")
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'user_clustering.py')
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")' in content:
                print("   ℹ 脚本使用环境变量（推荐方式）")
            elif 'GEMINI_API_KEY = "' in content and 'YOUR_GEMINI_API_KEY' not in content:
                # 尝试提取硬编码的密钥
                import re
                match = re.search(r'GEMINI_API_KEY\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    hardcoded_key = match.group(1)
                    if hardcoded_key and hardcoded_key != 'YOUR_GEMINI_API_KEY':
                        print(f"   ✓ 脚本中硬编码了密钥 (长度: {len(hardcoded_key)})")
                        if not env_key:
                            env_key = hardcoded_key
                    else:
                        print("   ✗ 脚本中仍为默认占位符")
                else:
                    print("   ℹ 未找到硬编码密钥")
    except Exception as e:
        print(f"   ⚠ 无法读取脚本: {e}")
    
    # 方法3: 测试API连接
    print("\n[方法3] 测试API连接")
    if not env_key:
        print("   ✗ 无法测试（未找到有效的API密钥）")
        print("\n" + "=" * 70)
        print("如何设置API密钥:")
        print("=" * 70)
        print("\n方法1: 设置环境变量（推荐，临时）")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        print("\n方法2: 设置环境变量（永久，添加到 ~/.zshrc）")
        print("  echo 'export GEMINI_API_KEY=\"your-api-key-here\"' >> ~/.zshrc")
        print("  source ~/.zshrc")
        print("\n方法3: 在脚本中直接设置")
        print("  编辑 user_clustering.py 第23行，改为:")
        print("  GEMINI_API_KEY = 'your-api-key-here'")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=env_key)
        
        # 尝试一个简单的embedding调用
        print("   正在测试API连接...")
        result = genai.embed_content(
            model="models/embedding-001",
            content="test",
            task_type="clustering"
        )
        
        if result and 'embedding' in result:
            embedding_dim = len(result['embedding'])
            print(f"   ✓ API连接成功！")
            print(f"   ✓ Embedding维度: {embedding_dim}")
            print(f"   ✓ 可以使用真实API进行聚类")
            return True
        else:
            print("   ⚠ API响应异常")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ✗ API连接失败: {error_msg[:200]}...")  # 限制输出长度
        
        print("\n   可能的原因:")
        
        if "429" in error_msg or "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
            print("   ⚠ API配额已用完（免费层限制）")
            print("\n   问题分析:")
            if "embed_content_free_tier" in error_msg:
                print("   - Gemini免费层可能不包含embedding功能")
                print("   - 或者免费层的embedding配额已用完")
            print("\n   解决方案:")
            print("   1. 检查配额使用情况:")
            print("      https://ai.dev/usage?tab=rate-limit")
            print("   2. 等待配额重置（通常是每天重置）")
            print("   3. 升级到付费计划以获得更多配额")
            print("   4. 使用模拟embedding继续测试（脚本已支持）")
            print("\n   临时方案：使用模拟embedding")
            print("   运行聚类脚本时会自动使用模拟embedding")
            
        elif "leaked" in error_msg.lower() or ("403" in error_msg and "leaked" in error_msg.lower()):
            print("   ⚠ API密钥已被标记为泄露，需要更换新密钥")
            print("   解决方案:")
            print("   1. 访问 https://aistudio.google.com/apikey")
            print("   2. 删除或撤销当前密钥")
            print("   3. 创建新的API密钥")
            print("   4. 使用新密钥重新设置")
        elif "401" in error_msg or "invalid" in error_msg.lower():
            print("   1. API密钥无效或格式错误")
            print("   2. 请检查密钥是否正确复制")
        elif "permission" in error_msg.lower() or ("403" in error_msg and "permission" in error_msg.lower()):
            print("   1. API密钥没有embedding权限")
            print("   2. 请确保密钥有正确的权限")
        else:
            print("   1. API密钥无效或已过期")
            print("   2. 网络连接问题")
            print("   3. API服务暂时不可用")
        
        return False


if __name__ == '__main__':
    success = check_api_key()
    sys.exit(0 if success else 1)

