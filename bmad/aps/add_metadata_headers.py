#!/usr/bin/env python3
"""
Batch add BMAD v6 metadata headers to expert library files
"""

import os
import re
from pathlib import Path

# Category mapping for Chinese/English names and owners
CATEGORY_MAPPING = {
    'algorithm-library': {
        'chinese': '调度算法专家库',
        'owner': '调度算法专家智能体 (Algorithm Expert)',
        'subcategories': {
            'exact': {'chinese': '精确算法', 'english': 'exact'},
            'heuristic': {'chinese': '启发式算法', 'english': 'heuristic'},
            'meta-heuristic': {'chinese': '元启发式算法', 'english': 'meta-heuristic'}
        }
    },
    'constraint-library': {
        'chinese': '约束模式专家库',
        'owner': '约束模式专家智能体 (Constraint Expert)',
        'subcategories': {
            'capacity': {'chinese': '容量约束', 'english': 'capacity'},
            'temporal': {'chinese': '时间约束', 'english': 'temporal'},
            'spatial': {'chinese': '空间约束', 'english': 'spatial'},
            'logical': {'chinese': '逻辑约束', 'english': 'logical'},
            'business-rules': {'chinese': '业务规则', 'english': 'business-rules'}
        }
    },
    'objective-library': {
        'chinese': '目标函数专家库',
        'owner': '目标优化专家智能体 (Objective Expert)',
        'subcategories': {
            'cost': {'chinese': '成本目标', 'english': 'cost'},
            'time': {'chinese': '时间目标', 'english': 'time'},
            'efficiency': {'chinese': '效率目标', 'english': 'efficiency'},
            'quality': {'chinese': '质量目标', 'english': 'quality'},
            'sustainability': {'chinese': '可持续性目标', 'english': 'sustainability'},
            'multi-objective': {'chinese': '多目标优化', 'english': 'multi-objective'}
        }
    },
    'domain-library': {
        'chinese': '领域应用专家库',
        'owner': '领域应用专家智能体 (Domain Expert)',
        'subcategories': {
            'vehicle': {'chinese': '车辆调度', 'english': 'vehicle'},
            'production': {'chinese': '生产调度', 'english': 'production'},
            'service': {'chinese': '服务调度', 'english': 'service'},
            'project': {'chinese': '项目调度', 'english': 'project'},
            'supply-chain': {'chinese': '供应链调度', 'english': 'supply-chain'}
        }
    },
    'validation-library': {
        'chinese': '验证评估专家库',
        'owner': '验证评估专家智能体 (Validation Expert)',
        'subcategories': {
            'benchmark': {'chinese': '基准评测', 'english': 'benchmark'},
            'report': {'chinese': '报告聚合', 'english': 'report'},
            'consistency': {'chinese': '约束一致性', 'english': 'consistency'},
            'syntax': {'chinese': '语法检查', 'english': 'syntax'},
            'logic': {'chinese': '逻辑验证', 'english': 'logic'}
        }
    },
    'orchestration-library': {
        'chinese': '系统编排专家库',
        'owner': '系统编排协调智能体 (CoreOrchestrator)',
        'subcategories': {
            'decision': {'chinese': '决策策略', 'english': 'decision'},
            'collaboration': {'chinese': '编排模式', 'english': 'collaboration'},
            'integration': {'chinese': '集成优化', 'english': 'integration'},
            'risk': {'chinese': '风险控制', 'english': 'risk'}
        }
    }
}

def check_has_header(file_path):
    """Check if file already has BMAD header"""
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        return 'Powered by BMAD-CORE' in first_line

def generate_header(file_path, category, subcategory, filename):
    """Generate BMAD v6 metadata header"""

    # Get category info
    cat_info = CATEGORY_MAPPING.get(category, {})
    chinese_cat = cat_info.get('chinese', category)
    owner = cat_info.get('owner', 'Unknown Expert')

    # Get subcategory info
    subcat_info = cat_info.get('subcategories', {}).get(subcategory, {})
    chinese_subcat = subcat_info.get('chinese', subcategory)
    english_subcat = subcat_info.get('english', subcategory)

    # Remove .md extension for aliases
    file_base = filename.replace('.md', '')

    # Build module ID
    module_id = f"bmad/aps/templates/{category}/{subcategory}/{filename}"

    # Build aliases
    english_alias = f"@专家库/{category.replace('-library', '库')}/{english_subcat}/{file_base}.md"
    chinese_alias = f"@专家库/{chinese_cat}/{chinese_subcat}/{file_base}.md"

    header = f"""<!-- Powered by BMAD-CORE™ -->
<!-- Module ID: {module_id} -->
<!-- Aliases: {english_alias}, {chinese_alias} -->
<!-- Version: v1.0 -->
<!-- Owner: {owner} -->

"""

    return header

def add_header_to_file(file_path):
    """Add BMAD v6 header to a single file"""

    # Parse file path
    path_parts = Path(file_path).parts

    # Find category and subcategory
    templates_idx = path_parts.index('templates')
    category = path_parts[templates_idx + 1]
    subcategory = path_parts[templates_idx + 2]
    filename = path_parts[-1]

    # Check if already has header
    if check_has_header(file_path):
        print(f"  ✓ {filename} already has header, skipping")
        return False

    # Read original content
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Generate header
    header = generate_header(file_path, category, subcategory, filename)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(header + original_content)

    print(f"  ✓ Added header to {filename}")
    return True

def main():
    """Main function to process all files"""

    templates_dir = Path('/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/bmad/aps/templates')

    # Find all markdown files (excluding README.md)
    md_files = []
    for category_dir in templates_dir.iterdir():
        if category_dir.is_dir():
            for subcat_dir in category_dir.iterdir():
                if subcat_dir.is_dir():
                    for md_file in subcat_dir.glob('*.md'):
                        if md_file.name != 'README.md':
                            md_files.append(md_file)

    print(f"Found {len(md_files)} markdown files to process\n")

    # Process by category
    for category in CATEGORY_MAPPING.keys():
        category_files = [f for f in md_files if f'/{category}/' in str(f)]
        if not category_files:
            continue

        print(f"\n📁 Processing {category} ({len(category_files)} files):")

        added_count = 0
        for file_path in sorted(category_files):
            if add_header_to_file(str(file_path)):
                added_count += 1

        print(f"   Added headers to {added_count} files")

    print(f"\n✅ Processing complete!")

if __name__ == '__main__':
    main()
