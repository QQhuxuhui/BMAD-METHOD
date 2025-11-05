#!/usr/bin/env python3
"""
更新专家库引用路径的脚本
将旧的中文引用格式更新为新的英文路径格式
"""

import os
import re
from pathlib import Path

# 定义路径映射（中文名 -> 英文目录名）
PATH_MAPPINGS = {
    # 简短格式（带"库"字）
    "@专家库/algorithm库/": "@backend/knowledge_base/aps/algorithm-library/",
    "@专家库/constraint库/": "@backend/knowledge_base/aps/constraint-library/",
    "@专家库/objective库/": "@backend/knowledge_base/aps/objective-library/",
    "@专家库/domain库/": "@backend/knowledge_base/aps/domain-library/",
    "@专家库/code库/": "@backend/knowledge_base/aps/code-implementation-library/",
    "@专家库/quality库/": "@backend/knowledge_base/aps/quality-library/",
    "@专家库/orchestrator库/": "@backend/knowledge_base/aps/orchestrator-library/",
    "@专家库/modeling库/": "@backend/knowledge_base/aps/modeling-library/",

    # 简短格式
    "@专家库/算法库/": "@backend/knowledge_base/aps/algorithm-library/",
    "@专家库/约束库/": "@backend/knowledge_base/aps/constraint-library/",
    "@专家库/目标库/": "@backend/knowledge_base/aps/objective-library/",
    "@专家库/领域库/": "@backend/knowledge_base/aps/domain-library/",
    "@专家库/代码库/": "@backend/knowledge_base/aps/code-implementation-library/",
    "@专家库/质量库/": "@backend/knowledge_base/aps/quality-library/",
    "@专家库/编排库/": "@backend/knowledge_base/aps/orchestrator-library/",
    "@专家库/建模库/": "@backend/knowledge_base/aps/modeling-library/",

    # 完整格式（带"专家库"后缀）
    "@专家库/调度算法专家库/": "@backend/knowledge_base/aps/algorithm-library/",
    "@专家库/算法专家库/": "@backend/knowledge_base/aps/algorithm-library/",
    "@专家库/约束模式专家库/": "@backend/knowledge_base/aps/constraint-library/",
    "@专家库/约束专家库/": "@backend/knowledge_base/aps/constraint-library/",
    "@专家库/目标函数专家库/": "@backend/knowledge_base/aps/objective-library/",
    "@专家库/目标专家库/": "@backend/knowledge_base/aps/objective-library/",
    "@专家库/领域应用专家库/": "@backend/knowledge_base/aps/domain-library/",
    "@专家库/领域专家库/": "@backend/knowledge_base/aps/domain-library/",
    "@专家库/代码实现专家库/": "@backend/knowledge_base/aps/code-implementation-library/",
    "@专家库/代码专家库/": "@backend/knowledge_base/aps/code-implementation-library/",
    "@专家库/质量评估专家库/": "@backend/knowledge_base/aps/quality-library/",
    "@专家库/编排专家库/": "@backend/knowledge_base/aps/orchestrator-library/",
    "@专家库/建模专家库/": "@backend/knowledge_base/aps/modeling-library/",

    # 其他相关名称映射
    "@专家库/优化技术专家库/": "@backend/knowledge_base/aps/algorithm-library/",
    "@专家库/问题分解专家库/": "@backend/knowledge_base/aps/modeling-library/",
    "@专家库/验证评估专家库/": "@backend/knowledge_base/aps/quality-library/",
    "@专家库/系统编排专家库/": "@backend/knowledge_base/aps/orchestrator-library/",
    "@专家库/建模模块/": "@backend/knowledge_base/aps/modeling-library/",
    "@专家库/collaboration/": "@backend/knowledge_base/aps/orchestrator-library/",
}

def update_file_references(file_path: Path) -> int:
    """更新单个文件中的引用路径

    Args:
        file_path: 文件路径

    Returns:
        更新的引用数量
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        update_count = 0

        # 应用所有路径映射
        for old_path, new_path in PATH_MAPPINGS.items():
            if old_path in content:
                content = content.replace(old_path, new_path)
                update_count += content.count(new_path) - original_content.count(new_path)

        # 如果有更新，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return update_count

        return 0

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    """主函数"""
    base_dir = Path("backend/knowledge_base/aps")

    if not base_dir.exists():
        print(f"目录不存在: {base_dir}")
        return

    total_files = 0
    total_updates = 0

    # 遍历所有markdown文件
    for file_path in base_dir.rglob("*.md"):
        updates = update_file_references(file_path)
        if updates > 0:
            total_files += 1
            total_updates += updates
            print(f"✓ {file_path.relative_to(base_dir)}: {updates} 个引用已更新")

    print(f"\n完成！共更新 {total_files} 个文件，{total_updates} 处引用")

if __name__ == "__main__":
    main()
