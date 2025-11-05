#!/usr/bin/env python3
"""快速测试library_loader功能"""

import sys
sys.path.insert(0, '/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD')

from backend.app.core.langgraph.library_loader import LibraryLoader

def test_library_loader():
    print("=== 测试LibraryLoader ===\n")

    # 初始化
    loader = LibraryLoader()
    print(f"✓ LibraryLoader初始化成功")
    print(f"  基础路径: {loader.base_path}\n")

    # 列出所有库
    libraries = loader.list_libraries()
    print(f"✓ 找到 {len(libraries)} 个专家库:")
    for lib in libraries:
        print(f"  - {lib}")
    print()

    # 加载一个库
    if libraries:
        test_lib = libraries[0]
        print(f"✓ 加载测试库: {test_lib}")
        lib_data = loader.load_library(test_lib)
        print(f"  文件数: {len(lib_data['files'])}")
        print(f"  README长度: {len(lib_data['readme'])} 字符")
        print()

    # 搜索功能
    print("✓ 搜索测试 (关键词: '算法'):")
    results = loader.search_knowledge("算法")
    print(f"  找到 {len(results)} 个结果")
    if results:
        print(f"  第一个结果: {results[0]['library']}/{results[0]['file']}")
    print()

    print("=== 所有测试通过! ===")

if __name__ == "__main__":
    try:
        test_library_loader()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
