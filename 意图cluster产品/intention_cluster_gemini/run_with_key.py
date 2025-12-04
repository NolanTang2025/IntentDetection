#!/usr/bin/env python3
"""
交互式运行聚类脚本，允许用户输入API key
"""
import os
import sys
from pathlib import Path

def get_api_key_interactive():
    """交互式获取API key"""
    print("=" * 60)
    print("意图聚类脚本 - 交互式运行")
    print("=" * 60)
    print()
    
    # 检查现有的API key
    current_key = os.environ.get("GEMINI_API_KEY", "")
    if current_key:
        print(f"当前环境变量中的API key: {current_key[:15]}...")
        print()
        use_current = input("是否使用当前API key? (y/n, 默认n): ").strip().lower()
        if use_current == 'y':
            return current_key
    
    print("请输入你的Gemini API key (以AIzaSy开头):")
    print("提示: 如果你之前check_api.py成功，可以在那个终端查看API key")
    api_key = input("API key: ").strip()
    
    if not api_key:
        print("❌ 未输入API key")
        return None
    
    if not api_key.startswith("AIzaSy"):
        print("⚠️  警告: API key格式可能不正确（应以AIzaSy开头）")
        confirm = input("是否继续? (y/n): ").strip().lower()
        if confirm != 'y':
            return None
    
    return api_key

def main():
    api_key = get_api_key_interactive()
    
    if not api_key:
        print("\n❌ 未提供有效的API key，退出")
        return 1
    
    print(f"\n✓ 使用API key: {api_key[:15]}...")
    print()
    
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

