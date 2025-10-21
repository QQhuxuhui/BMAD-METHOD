#!/usr/bin/env python3
"""
Generate comprehensive KNOWLEDGE_MODULE_INDEX.md
"""

from pathlib import Path
import re

# Category info
CATEGORIES = {
    'algorithm-library': {
        'chinese': '算法库 (Algorithm Library)',
        'expert': '张效率 (Algorithm Expert)',
        'readme': 'bmad/aps/templates/algorithm-library/README.md',
        'subcats': {
            'exact': '精确算法 (Exact Algorithms)',
            'heuristic': '启发式算法 (Heuristic Algorithms)',
            'meta-heuristic': '元启发式算法 (Meta-Heuristic Algorithms)'
        }
    },
    'constraint-library': {
        'chinese': '约束库 (Constraint Library)',
        'expert': '李严谨 (Constraint Expert)',
        'readme': 'bmad/aps/templates/constraint-library/README.md',
        'subcats': {
            'capacity': '容量约束 (Capacity Constraints)',
            'temporal': '时间约束 (Temporal Constraints)',
            'spatial': '空间约束 (Spatial Constraints)',
            'logical': '逻辑约束 (Logical Constraints)',
            'business-rules': '业务规则 (Business Rules)'
        }
    },
    'objective-library': {
        'chinese': '目标库 (Objective Library)',
        'expert': '王目标 (Objective Expert)',
        'readme': 'bmad/aps/templates/objective-library/README.md',
        'subcats': {
            'cost': '成本目标 (Cost Objectives)',
            'time': '时间目标 (Time Objectives)',
            'efficiency': '效率目标 (Efficiency Objectives)',
            'quality': '质量目标 (Quality Objectives)',
            'sustainability': '可持续性目标 (Sustainability Objectives)',
            'multi-objective': '多目标优化 (Multi-Objective Optimization)'
        }
    },
    'domain-library': {
        'chinese': '领域库 (Domain Library)',
        'expert': '赵领域 (Domain Expert)',
        'readme': 'bmad/aps/templates/domain-library/README.md',
        'subcats': {
            'vehicle': '车辆调度 (Vehicle Scheduling)',
            'production': '生产调度 (Production Scheduling)',
            'service': '服务调度 (Service Scheduling)',
            'project': '项目调度 (Project Scheduling)',
            'supply-chain': '供应链调度 (Supply Chain Scheduling)'
        }
    },
    'quality-library': {
        'chinese': '质量评估库 (Quality Library)',
        'expert': '质量与评测智能体 (Quality Expert)',
        'readme': 'bmad/aps/templates/quality-library/README.md',
        'subcats': {
            'benchmark': '基准评测 (Benchmark)',
            'report': '报告聚合 (Report Aggregation)',
            'consistency': '约束一致性 (Consistency Checking)',
            'syntax': '语法检查 (Syntax Checking)',
            'logic': '逻辑验证 (Logic Validation)'
        }
    },
    'orchestrator-library': {
        'chinese': '系统编排库 (Orchestrator Library)',
        'expert': '系统编排协调智能体 (CoreOrchestrator)',
        'readme': 'bmad/aps/templates/orchestrator-library/README.md',
        'subcats': {
            'decision': '决策策略 (Decision Strategies)',
            'collaboration': '编排模式 (Collaboration Patterns)',
            'integration': '集成优化 (Integration Optimization)',
            'risk': '风险控制 (Risk Control)'
        }
    },
    'modeling-library': {
        'chinese': '建模库 (Modeling Library)',
        'expert': '系统编排协调智能体 (CoreOrchestrator)',
        'readme': 'bmad/aps/templates/modeling-library/README.md (待创建)',
        'subcats': {
            'core': '核心建模模块 (Core Modeling Modules)'
        }
    },
    'collaboration': {
        'chinese': '协作机制 (Collaboration Mechanisms)',
        'expert': '系统编排协调智能体 (CoreOrchestrator)',
        'readme': 'bmad/aps/templates/collaboration/README.md (待创建)',
        'subcats': {}
    },
    'examples': {
        'chinese': '实例化案例 (Example Cases)',
        'expert': '所有专家智能体',
        'readme': 'bmad/aps/templates/examples/README.md (待创建)',
        'subcats': {}
    }
}

def get_files_by_category(templates_dir):
    """Get all markdown files organized by category"""
    files_by_cat = {}

    for cat_dir in templates_dir.iterdir():
        if not cat_dir.is_dir():
            continue

        cat_name = cat_dir.name
        files_by_cat[cat_name] = {}

        # Check if has subcategories
        has_subcats = any(d.is_dir() for d in cat_dir.iterdir())

        if has_subcats:
            for subcat_dir in cat_dir.iterdir():
                if subcat_dir.is_dir():
                    subcat_name = subcat_dir.name
                    files = [f for f in subcat_dir.glob('*.md') if f.name != 'README.md']
                    if files:
                        files_by_cat[cat_name][subcat_name] = sorted(files, key=lambda x: x.name)
        else:
            # Direct files in category
            files = [f for f in cat_dir.glob('*.md') if f.name != 'README.md']
            if files:
                files_by_cat[cat_name]['_root'] = sorted(files, key=lambda x: x.name)

    return files_by_cat

def generate_table_row(filename, cat, subcat):
    """Generate a table row for a file"""
    file_base = filename.replace('.md', '')

    # English path
    if cat in ['collaboration', 'examples']:
        eng_path = f'@专家库/{cat}/{file_base}.md'
    else:
        cat_short = cat.replace('-library', '库')
        eng_path = f'@专家库/{cat_short}/{subcat}/{file_base}.md'

    # Chinese path
    cat_info = CATEGORIES.get(cat, {})
    cat_chinese = cat_info.get('chinese', cat)

    if cat in ['collaboration', 'examples']:
        chi_path = f'@专家库/{cat_chinese}/{filename}'
    else:
        subcats = cat_info.get('subcats', {})
        subcat_info = subcats.get(subcat, subcat)
        # Extract Chinese part
        subcat_chinese = subcat_info.split('(')[0].strip() if '(' in subcat_info else subcat_info
        chi_path = f'@专家库/{cat_chinese}/{subcat_chinese}/{filename}'

    # File path
    if cat in ['collaboration', 'examples']:
        file_path = f'`bmad/aps/templates/{cat}/{filename}`'
    else:
        file_path = f'`bmad/aps/templates/{cat}/{subcat}/{filename}`'

    return f"| {file_base}   | `{eng_path}` | `{chi_path}` | {file_path} |"

def generate_index():
    """Generate the complete index content"""
    templates_dir = Path('/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/bmad/aps/templates')
    files_by_cat = get_files_by_category(templates_dir)

    content = """# 知识模块路径索引 - Knowledge Module Path Index

**版本**: v2.0
**更新日期**: 2025-10-21
**模块**: BMAD APS (Advanced Planning & Scheduling)

本文档提供所有已迁移知识模块的路径映射索引，帮助智能体正确引用知识模块。

---

## 📋 路径引用规范

### 标准引用格式

```yaml
@专家库/<category>/<path>/<filename>.md
```

### 支持的引用路径类型

1. **英文路径** (推荐): `@专家库/算法库/heuristic/遗传算法.md`
2. **中文路径** (别名): `@专家库/调度算法专家库/启发式算法/遗传算法.md`
3. **实际文件路径**: `bmad/aps/templates/algorithm-library/heuristic/遗传算法.md`

---

"""

    # Generate sections for each category
    for cat, cat_info in CATEGORIES.items():
        if cat not in files_by_cat or not files_by_cat[cat]:
            continue

        cat_files = files_by_cat[cat]
        total_files = sum(len(files) for files in cat_files.values())

        content += f"## 🗂️ {cat_info['chinese']}\n\n"

        # Add subcategory sections
        for subcat_key, subcat_name in cat_info.get('subcats', {}).items():
            if subcat_key not in cat_files:
                continue

            content += f"### {subcat_name}\n\n"
            content += "| 模块名称       | 英文路径                                         | 中文路径别名                                   | 实际文件路径                                                    |\n"
            content += "| -------------- | ------------------------------------------------ | ---------------------------------------------- | --------------------------------------------------------------- |\n"

            for file_path in cat_files[subcat_key]:
                row = generate_table_row(file_path.name, cat, subcat_key)
                content += row + "\n"

            content += "\n"

        # Handle root files (for collaboration and examples)
        if '_root' in cat_files:
            content += "| 模块名称       | 英文路径                                         | 中文路径别名                                   | 实际文件路径                                                    |\n"
            content += "| -------------- | ------------------------------------------------ | ---------------------------------------------- | --------------------------------------------------------------- |\n"

            for file_path in cat_files['_root']:
                row = generate_table_row(file_path.name, cat, '_root')
                content += row + "\n"

            content += "\n"

        content += f"**专家**: {cat_info['expert']}\n"
        content += f"**主入口**: `{cat_info['readme']}`\n"
        content += f"**文件数量**: {total_files} 个\n\n"
        content += "---\n\n"

    # Add reference guidelines
    content += """## 🎯 智能体引用规范

### 在智能体Prompt中引用

```xml
<i critical="MANDATORY">
  每个推荐必须附@引用，如: @专家库/算法库/heuristic/遗传算法.md
</i>
```

### 在TenElementModel中引用

```yaml
5_algorithm:
  name: '遗传算法'
  type: 'heuristic'
  citation: '@专家库/算法库/heuristic/遗传算法.md'
  configuration:
    population_size: 100
    crossover_rate: 0.8
    mutation_rate: 0.05
```

---

## 📊 统计信息

"""

    # Add statistics
    total_count = 0
    for cat, cat_files in files_by_cat.items():
        cat_total = sum(len(files) for files in cat_files.values())
        total_count += cat_total

        cat_info = CATEGORIES.get(cat, {})
        cat_name = cat_info.get('chinese', cat)
        content += f"- **{cat_name}**: {cat_total} 个文件\n"

    content += f"\n**总计**: {total_count} 个知识模块文件\n\n---\n\n"

    # Add update history
    content += """## 📝 更新历史

| 日期       | 版本 | 更新内容                           |
| ---------- | ---- | ---------------------------------- |
| 2025-10-21 | v2.0 | 完整迁移专家库，包含87个知识模块    |
| 2025-10-21 | v1.0 | 初始版本，包含12个已迁移知识模块    |

---

## 🔗 相关文档

- [APS模块README](../README.md)
- [算法库README](./algorithm-library/README.md)
- [约束库README](./constraint-library/README.md)
- [APS配置文件](../config.yaml)
- [迁移指南](../MIGRATION_GUIDE.md)
"""

    return content

def main():
    """Main function"""
    content = generate_index()

    output_file = Path('/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/bmad/aps/templates/KNOWLEDGE_MODULE_INDEX.md')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Generated comprehensive index at: {output_file}")
    print(f"   Total content length: {len(content)} characters")

if __name__ == '__main__':
    main()
