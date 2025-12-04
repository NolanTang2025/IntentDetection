#!/usr/bin/env python3
"""
自动运行聚类脚本，自动读取API key
"""
import os
import sys
from pathlib import Path

def find_api_key():
    """从多个位置查找API key"""
    # 方法1: 从环境变量读取
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        return api_key, "环境变量"
    
    # 方法2: 从 .env 文件读取
    script_dir = Path(__file__).parent
    env_files = [
        script_dir / ".env",
        script_dir.parent / ".env",
    ]
    
    for env_file in env_files:
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            # 支持 GEMINI_API_KEY=value 或 GEMINI_API_KEY='value' 或 GEMINI_API_KEY="value"
                            key_value = line.split("=", 1)[1].strip()
                            # 移除引号
                            if (key_value.startswith('"') and key_value.endswith('"')) or \
                               (key_value.startswith("'") and key_value.endswith("'")):
                                key_value = key_value[1:-1]
                            if key_value:
                                return key_value, f".env文件 ({env_file})"
            except Exception as e:
                continue
    
    # 方法3: 从用户主目录的配置文件读取
    home_env = Path.home() / ".gemini_api_key"
    if home_env.exists():
        try:
            with open(home_env, "r", encoding="utf-8") as f:
                api_key = f.read().strip()
                if api_key:
                    return api_key, "用户主目录配置文件"
        except Exception:
            pass
    
    return None, None

def main():
    print("=" * 60)
    print("意图聚类脚本 - 自动运行")
    print("=" * 60)
    print()
    
    # 检查命令行参数
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        print(f"✓ 从命令行参数读取API key: {api_key[:15]}...")
        print()
        os.environ["GEMINI_API_KEY"] = api_key
        # 直接使用命令行参数的API key
    else:
        # 查找API key
        api_key, source = find_api_key()
        
        if not api_key:
            print("❌ 未找到 GEMINI_API_KEY")
            print()
            print("请设置API key，方式之一：")
            print("  1. 命令行参数: python3 run_clustering.py 'your-api-key'")
            print("  2. 在当前shell中设置: export GEMINI_API_KEY='your-api-key'")
            print("  3. 创建 intention_cluster/.env 文件，添加: GEMINI_API_KEY='your-api-key'")
            print("  4. 创建 ~/.gemini_api_key 文件，写入API key")
            print()
            return 1
        
        print(f"✓ 找到API key: {api_key[:15]}... (来源: {source})")
        print()
        os.environ["GEMINI_API_KEY"] = api_key
    
    # 设置环境变量
    os.environ["GEMINI_API_KEY"] = api_key
    
    # 导入并运行聚类脚本
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 添加项目根目录到Python路径
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 切换到脚本目录
    os.chdir(script_dir.parent)
    
    # 导入并运行main函数
    sys.path.insert(0, str(script_dir))
    from user_clustering import main as clustering_main
    
    print("开始运行聚类脚本...")
    print()
    
    try:
        clustering_main()
        return 0
    except KeyboardInterrupt:
        print("\n\n用户中断")
        return 130
    except Exception as e:
        print(f"\n\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

