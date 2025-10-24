# Task: Save Solution Document

**任务ID**: `save-solution-document`
**版本**: V4.3
**用途**: Phase 3 Step 3.3 - 将完整方案保存为Markdown文档，作为独立交付物

## 输入

```yaml
inputs:
  - integrated_solution: 完整方案对象
  - consistency_validation: 一致性验证结果
  - ten_element_model: TenElementModel对象（用于生成附录）
  - output_folder: 输出目录路径
  - docs_folder: 文档子目录名称
  - include_metadata: 是否包含元数据（默认true）
  - include_data_sources: 是否包含数据来源标注（默认true）
```

## 🚨 强制要求（MANDATORY）

### 1. 必须使用IDE的Write工具

**CRITICAL**: 此任务执行时，AI必须实际调用IDE提供的Write工具来保存文件，而不是仅输出Markdown内容。

```
适用于所有IDE:
- Claude Code: 使用 Write 工具
- Cursor: 使用 Write 工具
- Windsurf: 使用 Write 工具
- 其他IDE: 使用对应的文件写入工具
```

### 2. 保存后必须验证

保存文件后，必须验证：

- ✓ 文件已创建
- ✓ 文件大小 > 最小阈值（5KB）
- ✓ 文件可读取
- ✓ Markdown格式正确

验证失败则抛出错误，阻断流程。

### 3. 文件命名规范

```python
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"solution_document_{timestamp}.md"
# 例如: solution_document_20251024_143530.md
```

## 处理逻辑

### 步骤1: 准备输出目录

```python
import os
from pathlib import Path

def prepare_output_directory(output_folder, docs_folder):
    """
    创建输出目录结构（如果不存在）

    Returns:
        dict: 目录路径信息
    """
    base_path = Path(output_folder)
    docs_path = base_path / docs_folder

    # 创建目录
    docs_path.mkdir(parents=True, exist_ok=True)

    print(f"✓ 文档目录已准备: {docs_path}")

    return {
        "base": str(base_path),
        "docs": str(docs_path)
    }
```

### 步骤2: 生成Markdown文档内容

````python
def generate_solution_markdown(
    integrated_solution,
    consistency_validation,
    ten_element_model,
    include_metadata=True,
    include_data_sources=True
):
    """
    将方案对象转换为格式化的Markdown文档

    Returns:
        str: Markdown文档内容
    """
    from datetime import datetime

    md_content = []

    # ====== 文档头部 ======
    md_content.append("# 调度优化方案\n")
    md_content.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_content.append(f"**版本**: {integrated_solution['metadata']['version']}\n")
    md_content.append(f"**Phase**: {integrated_solution['metadata']['phase']}\n")
    md_content.append("\n---\n\n")

    # ====== 数据来源 ======
    if include_data_sources:
        md_content.append("## 📊 数据来源\n\n")

        data_sources = integrated_solution['metadata']['data_sources']

        md_content.append("### TenElementModel\n\n")
        md_content.append(f"- **来源文件**: `{data_sources['ten_element_model']['source_file']}`\n")
        md_content.append(f"- **时间戳**: {data_sources['ten_element_model']['timestamp']}\n")
        md_content.append(f"- **Hash**: `{data_sources['ten_element_model']['hash']}`\n")
        md_content.append(f"- **版本**: {data_sources['ten_element_model']['version']}\n\n")

        md_content.append("### 专家分析结果\n\n")
        md_content.append(f"- **来源文件**: `{data_sources['expert_analyses']['source_file']}`\n")
        md_content.append(f"- **时间戳**: {data_sources['expert_analyses']['timestamp']}\n")
        md_content.append(f"- **Hash**: `{data_sources['expert_analyses']['hash']}`\n")
        md_content.append(f"- **版本**: {data_sources['expert_analyses']['version']}\n\n")

        md_content.append("---\n\n")

    # ====== 目录 ======
    md_content.append("## 📋 目录\n\n")
    md_content.append("1. [问题定义与建模](#1-问题定义与建模)\n")
    md_content.append("2. [领域适配方案](#2-领域适配方案)\n")
    md_content.append("3. [约束处理策略](#3-约束处理策略)\n")
    md_content.append("4. [目标优化策略](#4-目标优化策略)\n")
    md_content.append("5. [算法选择与配置](#5-算法选择与配置)\n")
    md_content.append("6. [实现路线图](#6-实现路线图)\n")
    if include_metadata:
        md_content.append("7. [附录: TenElementModel完整定义](#7-附录-tenelementmodel完整定义)\n")
    md_content.append("\n---\n\n")

    # ====== 第1章: 问题定义与建模 ======
    md_content.append("## 1. 问题定义与建模\n\n")
    problem_def = integrated_solution['sections']['1_problem_definition']

    md_content.append("### 1.1 决策变量\n\n")
    md_content.append(f"**数据来源**: {problem_def['sections']['decision_variables']['source']}\n\n")
    for dv in problem_def['sections']['decision_variables']['content']:
        md_content.append(f"- **{dv.get('name', 'Unknown')}**: {dv.get('description', '')}\n")
        md_content.append(f"  - 类型: {dv.get('type', '')}\n")
        md_content.append(f"  - 域: {dv.get('domain', '')}\n\n")

    md_content.append("### 1.2 参数\n\n")
    md_content.append(f"**数据来源**: {problem_def['sections']['parameters']['source']}\n\n")
    for param in problem_def['sections']['parameters']['content']:
        md_content.append(f"- **{param.get('name', 'Unknown')}**: {param.get('description', '')}\n")
        md_content.append(f"  - 来源: {param.get('source', '')}\n\n")

    md_content.append("### 1.3 约束清单\n\n")
    md_content.append(f"**数据来源**: {problem_def['sections']['constraints']['source']}\n\n")
    for constraint in problem_def['sections']['constraints']['content']:
        md_content.append(f"- **{constraint.get('name', 'Unknown')}**: {constraint.get('description', '')}\n")
        md_content.append(f"  - 类型: {constraint.get('type', '')}\n\n")

    md_content.append("### 1.4 优化目标\n\n")
    md_content.append(f"**数据来源**: {problem_def['sections']['objectives']['source']}\n\n")
    for obj in problem_def['sections']['objectives']['content']:
        md_content.append(f"- **{obj.get('name', 'Unknown')}**: {obj.get('description', '')}\n")
        md_content.append(f"  - 优化方向: {obj.get('direction', '')}\n\n")

    md_content.append("### 1.5 时间模型\n\n")
    md_content.append(f"**数据来源**: {problem_def['sections']['time_model']['source']}\n\n")
    time_model = problem_def['sections']['time_model']['content']
    md_content.append(f"- **规划周期**: {time_model.get('horizon', '')}\n")
    md_content.append(f"- **时间粒度**: {time_model.get('granularity', '')}\n")
    md_content.append(f"- **时间类型**: {time_model.get('type', '')}\n\n")

    md_content.append("---\n\n")

    # ====== 第2章: 领域适配方案 ======
    md_content.append("## 2. 领域适配方案\n\n")
    domain_adapt = integrated_solution['sections']['2_domain_adaptation']

    md_content.append("### 2.1 行业特点\n\n")
    industry = domain_adapt['sections']['industry_characteristics']
    md_content.append(f"**数据来源**: {industry['source']}\n")
    md_content.append(f"**引用**: `{industry['reference']}`\n\n")
    md_content.append(f"- **行业**: {industry['content'].get('industry_name', '')}\n")
    md_content.append(f"- **特征**: {industry['content'].get('characteristics', '')}\n\n")

    md_content.append("### 2.2 业务规则\n\n")
    business_rules = domain_adapt['sections']['business_rules']
    md_content.append(f"**数据来源**: {business_rules['source']}\n")
    md_content.append(f"**引用**: `{business_rules['reference']}`\n\n")
    for rule in business_rules['content']:
        md_content.append(f"- **{rule.get('name', '')}**: {rule.get('description', '')}\n\n")

    md_content.append("### 2.3 领域特定约束\n\n")
    domain_constraints = domain_adapt['sections']['domain_constraints']
    md_content.append(f"**数据来源**: {domain_constraints['source']}\n")
    md_content.append(f"**引用**: `{domain_constraints['reference']}`\n")
    md_content.append(f"**映射**: {domain_constraints['mapping_to_model']}\n\n")
    for dc in domain_constraints['content']:
        md_content.append(f"- {dc}\n")
    md_content.append("\n")

    md_content.append("### 2.4 适配建议\n\n")
    adaptations = domain_adapt['sections']['adaptation_suggestions']
    md_content.append(f"**数据来源**: {adaptations['source']}\n\n")
    for adapt in adaptations['content']:
        md_content.append(f"- {adapt}\n")
    md_content.append("\n")

    md_content.append("---\n\n")

    # ====== 第3章: 约束处理策略 ======
    md_content.append("## 3. 约束处理策略\n\n")
    constraint_strategy = integrated_solution['sections']['3_constraint_strategy']

    md_content.append("### 3.1 约束分类\n\n")
    classification = constraint_strategy['sections']['constraint_classification']
    md_content.append(f"**数据来源**: {classification['source']}\n")
    md_content.append(f"**引用**: `{classification['reference']}`\n\n")

    md_content.append("#### 硬约束\n\n")
    for hc in classification['hard_constraints']:
        md_content.append(f"- {hc}\n")
    md_content.append("\n")

    md_content.append("#### 软约束\n\n")
    for sc in classification['soft_constraints']:
        md_content.append(f"- {sc}\n")
    md_content.append("\n")

    md_content.append("### 3.2 处理方法\n\n")
    methods = constraint_strategy['sections']['handling_methods']

    md_content.append("#### 硬约束处理\n\n")
    hard_method = methods['hard_constraint_strategy']
    md_content.append(f"- **方法**: {hard_method['method']}\n")
    md_content.append(f"- **说明**: {hard_method['description']}\n")
    md_content.append(f"- **数据来源**: {hard_method['source']}\n")
    md_content.append(f"- **引用**:\n")
    for cite in hard_method['citations']:
        md_content.append(f"  - {cite}\n")
    md_content.append("\n")

    md_content.append("#### 软约束处理\n\n")
    soft_method = methods['soft_constraint_strategy']
    md_content.append(f"- **方法**: {soft_method['method']}\n")
    md_content.append(f"- **说明**: {soft_method['description']}\n")
    md_content.append(f"- **数据来源**: {soft_method['source']}\n")
    md_content.append(f"- **引用**:\n")
    for cite in soft_method['citations']:
        md_content.append(f"  - {cite}\n")
    md_content.append("\n")

    md_content.append("### 3.3 验证方法\n\n")
    validation = constraint_strategy['sections']['validation_approach']
    md_content.append(f"**数据来源**: {validation['source']}\n\n")
    for val in validation['content']:
        md_content.append(f"- {val}\n")
    md_content.append("\n")

    md_content.append("---\n\n")

    # ====== 第4章: 目标优化策略 ======
    md_content.append("## 4. 目标优化策略\n\n")
    objective_strategy = integrated_solution['sections']['4_objective_strategy']

    md_content.append("### 4.1 目标优先级\n\n")
    hierarchy = objective_strategy['sections']['objective_hierarchy']
    md_content.append(f"**数据来源**: {hierarchy['source']}\n")
    md_content.append(f"**引用**: `{hierarchy['reference']}`\n\n")

    md_content.append("#### 主目标\n\n")
    primary = hierarchy['primary_objective']
    md_content.append(f"- **{primary.get('name', '')}**: {primary.get('description', '')}\n\n")

    md_content.append("#### 次要目标\n\n")
    for sec in hierarchy['secondary_objectives']:
        md_content.append(f"- **{sec.get('name', '')}**: {sec.get('description', '')}\n")
    md_content.append("\n")

    md_content.append("### 4.2 多目标处理\n\n")
    multi_obj = objective_strategy['sections']['multi_objective_handling']
    md_content.append(f"**数据来源**: {multi_obj['source']}\n\n")
    md_content.append(f"- **方法**: {multi_obj['approach']}\n")
    md_content.append(f"- **权重**: {multi_obj['weights']}\n")
    md_content.append(f"- **理由**: {multi_obj['justification']}\n")
    md_content.append(f"- **引用**:\n")
    for cite in multi_obj['citations']:
        md_content.append(f"  - {cite}\n")
    md_content.append("\n")

    md_content.append("### 4.3 目标函数设计\n\n")
    obj_func = objective_strategy['sections']['objective_function_design']
    md_content.append(f"**数据来源**: {obj_func['source']}\n")
    md_content.append(f"**引用**: `{obj_func['reference']}`\n\n")
    md_content.append(f"**公式**: {obj_func['formulation']}\n\n")
    md_content.append("**设计考虑**:\n\n")
    for consider in obj_func['considerations']:
        md_content.append(f"- {consider}\n")
    md_content.append("\n")

    md_content.append("---\n\n")

    # ====== 第5章: 算法选择与配置 ======
    md_content.append("## 5. 算法选择与配置\n\n")
    algorithm_selection = integrated_solution['sections']['5_algorithm_selection']

    md_content.append("### 5.1 选定算法\n\n")
    selected = algorithm_selection['sections']['selected_algorithm']
    md_content.append(f"**算法名称**: {selected['algorithm_name']}\n\n")
    md_content.append(f"**算法类型**: {selected['algorithm_type']}\n\n")
    md_content.append(f"**选择理由**: {selected['selection_rationale']}\n\n")

    # 增强：添加详细的引用块
    md_content.append("**📖 专家库引用**:\n\n")
    citations = selected.get('citations', [])
    if citations:
        for cite in citations:
            md_content.append(f"- `{cite}`\n")
    else:
        md_content.append("- _(未提供专家库引用)_\n")
    md_content.append("\n")

    # 增强：添加数据来源块
    md_content.append("**📍 数据来源**:\n\n")
    md_content.append(f"- **Phase**: {selected['source']}\n")

    # 如果有 source_metadata，显示详细信息
    if 'source_metadata' in selected:
        meta = selected['source_metadata']
        md_content.append(f"- **状态文件**: `{meta.get('state_file', 'N/A')}`\n")
        md_content.append(f"- **字段路径**: `{meta.get('field_path', 'N/A')}`\n")
        md_content.append(f"- **时间戳**: {meta.get('timestamp', 'N/A')}\n")
        md_content.append(f"- **Hash**: `{meta.get('hash', 'N/A')}`\n")
    else:
        md_content.append(f"- **引用**: `{selected['reference']}`\n")

    # 增强：添加置信度（如果有）
    if 'confidence' in selected and selected['confidence'] > 0:
        md_content.append(f"- **置信度**: {selected['confidence']:.2f}\n")

    md_content.append("\n")
    md_content.append("**🔗 详细追溯**: 见 [附录A2 - 5.1](#a2-详细引用映射表)\n\n")
    md_content.append("---\n\n")

    md_content.append("### 5.2 算法配置\n\n")
    config = algorithm_selection['sections']['algorithm_configuration']
    md_content.append(f"**数据来源**: {config['source']}\n")
    md_content.append(f"**引用**: `{config['reference']}`\n\n")

    # 增强：显示source_metadata（如果有）
    if 'source_metadata' in config:
        meta = config['source_metadata']
        md_content.append(f"**📍 来源**: `{meta.get('state_file', 'N/A')}::{meta.get('field_path', 'N/A')}`\n\n")

    md_content.append("**参数配置**:\n\n")
    md_content.append("| 参数 | 值 | 理由 | 专家库引用 |\n")
    md_content.append("|------|---|------|----------|\n")

    # 增强：参数表格中包含专家库引用
    param_citations = config.get('parameter_citations', {})
    for param_name, param_value in config['parameters'].items():
        justification = config['parameter_justification'].get(param_name, '')
        param_cite = param_citations.get(param_name, '')

        if param_cite:
            cite_str = f"`{param_cite}`"
        else:
            cite_str = "-"

        md_content.append(f"| {param_name} | {param_value} | {justification} | {cite_str} |\n")
    md_content.append("\n")

    md_content.append("### 5.3 优化建议\n\n")
    optimizations = algorithm_selection['sections']['optimization_suggestions']
    md_content.append(f"**数据来源**: {optimizations['source']}\n\n")
    for opt in optimizations['content']:
        md_content.append(f"- {opt}\n")
    md_content.append("\n")

    md_content.append("### 5.4 预期性能\n\n")
    performance = algorithm_selection['sections']['expected_performance']
    md_content.append(f"**数据来源**: {performance['source']}\n\n")
    md_content.append(f"- **时间复杂度**: {performance['time_complexity']}\n")
    md_content.append(f"- **空间复杂度**: {performance['space_complexity']}\n")
    md_content.append(f"- **解质量预期**: {performance['solution_quality']}\n\n")

    md_content.append("---\n\n")

    # ====== 第6章: 实现路线图 ======
    md_content.append("## 6. 实现路线图\n\n")
    roadmap = integrated_solution['sections']['6_implementation_roadmap']

    md_content.append("### 6.1 架构设计\n\n")
    arch = roadmap['sections']['architecture_design']
    md_content.append("**模块列表**:\n\n")
    for module in arch['modules']:
        md_content.append(f"- {module}\n")
    md_content.append(f"\n**模块关系**: {arch['module_relationships']}\n\n")

    md_content.append("### 6.2 数据结构设计\n\n")
    data_struct = roadmap['sections']['data_structure_design']
    md_content.append(f"- **决策变量结构**: {data_struct['decision_variable_structure']}\n")
    md_content.append(f"- **参数结构**: {data_struct['parameter_structure']}\n")
    md_content.append(f"- **解结构**: {data_struct['solution_structure']}\n\n")

    md_content.append("### 6.3 实现阶段\n\n")
    phases = roadmap['sections']['implementation_phases']
    for phase_info in phases['phases']:
        md_content.append(f"#### {phase_info['phase']}: {phase_info['name']}\n\n")
        md_content.append("**任务**:\n\n")
        for task in phase_info['tasks']:
            md_content.append(f"- {task}\n")
        md_content.append("\n")

    md_content.append("### 6.4 关键函数列表\n\n")
    functions = roadmap['sections']['key_functions']
    for func in functions['functions']:
        md_content.append(f"- `{func}`\n")
    md_content.append("\n")

    md_content.append("---\n\n")

    # ====== 附录: TenElementModel ======
    if include_metadata:
        md_content.append("## 7. 附录: TenElementModel完整定义\n\n")
        md_content.append("```yaml\n")
        import yaml
        md_content.append(yaml.dump(ten_element_model, allow_unicode=True, sort_keys=False))
        md_content.append("```\n\n")

    # ====== 一致性验证报告 ======
    md_content.append("---\n\n")
    md_content.append("## 一致性验证报告\n\n")
    md_content.append(f"**验证状态**: {consistency_validation.get('status', 'PASS')}\n")
    md_content.append(f"**验证时间**: {consistency_validation.get('timestamp', '')}\n\n")
    if consistency_validation.get('issues'):
        md_content.append("**发现问题**:\n\n")
        for issue in consistency_validation['issues']:
            md_content.append(f"- {issue}\n")
    else:
        md_content.append("✓ 未发现一致性问题\n")
    md_content.append("\n")

    # ====== 新增：附录A1 - 数据来源概览 ======
    md_content.append("---\n\n")
    md_content.append("## 附录A1: 数据来源概览\n\n")
    md_content.append("本方案的所有数据来自以下状态文件，确保完整可追溯。\n\n")

    # Phase 1.5: TenElementModel
    md_content.append("### Phase 1.5: TenElementModel (十要素建模)\n\n")
    data_sources = integrated_solution['metadata']['data_sources']
    tem_source = data_sources.get('ten_element_model', {})
    md_content.append(f"- **文件路径**: `aps-outputs/states/{tem_source.get('source_file', 'N/A')}`\n")
    md_content.append(f"- **时间戳**: {tem_source.get('timestamp', 'N/A')}\n")
    md_content.append(f"- **Hash**: `{tem_source.get('hash', 'N/A')}`\n")
    md_content.append(f"- **版本**: {tem_source.get('version', 'N/A')}\n")
    md_content.append(f"- **包含内容**: 10要素完整定义（决策变量、参数、约束、目标等）\n\n")

    # Phase 2: 专家分析
    md_content.append("### Phase 2: 专家分析结果\n\n")
    expert_source = data_sources.get('expert_analyses', {})
    md_content.append(f"- **文件路径**: `aps-outputs/states/{expert_source.get('source_file', 'N/A')}`\n")
    md_content.append(f"- **时间戳**: {expert_source.get('timestamp', 'N/A')}\n")
    md_content.append(f"- **Hash**: `{expert_source.get('hash', 'N/A')}`\n")
    md_content.append(f"- **版本**: {expert_source.get('version', 'N/A')}\n")
    md_content.append(f"- **包含内容**:\n")
    md_content.append(f"  - 领域专家分析 (domain_analysis)\n")
    md_content.append(f"  - 约束专家分析 (constraint_analysis)\n")
    md_content.append(f"  - 目标专家分析 (objective_analysis)\n")
    md_content.append(f"  - 算法专家分析 (algorithm_recommendations)\n")
    md_content.append(f"  - 一致性报告 (consistency_report)\n\n")

    # ====== 新增：附录A2 - 详细引用映射表 ======
    md_content.append("---\n\n")
    md_content.append("## 附录A2: 详细引用映射表\n\n")
    md_content.append("以下表格提供了方案中每个关键决策的完整追溯信息，包括状态文件字段路径和专家库引用。\n\n")

    # 生成引用映射表
    md_content.append("### 5. 算法选择与配置\n\n")
    md_content.append("| 项目 | 值 | 状态文件字段路径 | 专家库引用 | 置信度 |\n")
    md_content.append("|------|---|----------------|-----------|--------|\n")

    # 5.1 算法选择
    algorithm_selection = integrated_solution['sections']['5_algorithm_selection']
    selected = algorithm_selection['sections']['selected_algorithm']
    algo_name = selected.get('algorithm_name', 'N/A')
    field_path = selected.get('source_metadata', {}).get('field_path', 'N/A') if 'source_metadata' in selected else 'N/A'
    citations = selected.get('citations', [])
    cite_str = citations[0] if citations else '-'
    confidence = selected.get('confidence', 0.0)
    md_content.append(f"| 算法名称 | {algo_name} | `{field_path}` | `{cite_str}` | {confidence:.2f} |\n")

    # 5.2 算法参数
    config = algorithm_selection['sections']['algorithm_configuration']
    param_citations = config.get('parameter_citations', {})
    for param_name, param_value in config.get('parameters', {}).items():
        param_field_path = f"{config.get('source_metadata', {}).get('field_path', 'N/A')}.{param_name}"
        param_cite = param_citations.get(param_name, '-')
        md_content.append(f"| {param_name} | {param_value} | `{param_field_path}` | `{param_cite}` | - |\n")

    md_content.append("\n")

    # 3. 约束处理策略
    md_content.append("### 3. 约束处理策略\n\n")
    md_content.append("| 项目 | 方法/策略 | 状态文件字段路径 | 专家库引用 | 置信度 |\n")
    md_content.append("|------|----------|----------------|-----------|--------|\n")

    constraint_strategy = integrated_solution['sections']['3_constraint_strategy']
    methods = constraint_strategy['sections']['handling_methods']

    # 硬约束处理
    hard_method = methods['hard_constraint_strategy']
    hard_field = hard_method.get('source_metadata', {}).get('field_path', 'N/A') if 'source_metadata' in hard_method else 'N/A'
    hard_cites = hard_method.get('citations', [])
    hard_cite_str = hard_cites[0] if hard_cites else '-'
    hard_conf = hard_method.get('confidence', 0.0)
    md_content.append(f"| 硬约束处理 | {hard_method.get('method', 'N/A')} | `{hard_field}` | `{hard_cite_str}` | {hard_conf:.2f} |\n")

    # 软约束处理
    soft_method = methods['soft_constraint_strategy']
    soft_field = soft_method.get('source_metadata', {}).get('field_path', 'N/A') if 'source_metadata' in soft_method else 'N/A'
    soft_cites = soft_method.get('citations', [])
    soft_cite_str = soft_cites[0] if soft_cites else '-'
    soft_conf = soft_method.get('confidence', 0.0)
    md_content.append(f"| 软约束处理 | {soft_method.get('method', 'N/A')} | `{soft_field}` | `{soft_cite_str}` | {soft_conf:.2f} |\n")

    md_content.append("\n")

    # 4. 目标优化策略
    md_content.append("### 4. 目标优化策略\n\n")
    md_content.append("| 项目 | 值/方法 | 状态文件字段路径 | 专家库引用 | 置信度 |\n")
    md_content.append("|------|--------|----------------|-----------|--------|\n")

    objective_strategy = integrated_solution['sections']['4_objective_strategy']

    # 主目标
    hierarchy = objective_strategy['sections']['objective_hierarchy']
    primary_obj = hierarchy.get('primary_objective', {})
    obj_field = hierarchy.get('source_metadata', {}).get('field_path', 'N/A') if 'source_metadata' in hierarchy else 'N/A'
    md_content.append(f"| 主目标 | {primary_obj.get('name', 'N/A')} | `{obj_field}` | - | - |\n")

    # 多目标处理
    multi_obj = objective_strategy['sections']['multi_objective_handling']
    multi_field = multi_obj.get('source_metadata', {}).get('field_path', 'N/A') if 'source_metadata' in multi_obj else 'N/A'
    multi_cites = multi_obj.get('citations', [])
    multi_cite_str = multi_cites[0] if multi_cites else '-'
    multi_conf = multi_obj.get('confidence', 0.0)
    md_content.append(f"| 多目标方法 | {multi_obj.get('approach', 'N/A')} | `{multi_field}` | `{multi_cite_str}` | {multi_conf:.2f} |\n")

    md_content.append("\n")
    md_content.append("**说明**: \n")
    md_content.append("- 置信度范围 0.0-1.0，值越高表示该决策的可信度越高\n")
    md_content.append("- 状态文件字段路径格式: `state_data.专家分析.具体字段`\n")
    md_content.append("- 专家库引用格式: `@库名/分类/具体文件.md`\n\n")

    # ====== 文档尾部 ======
    md_content.append("---\n\n")
    md_content.append(f"**文档生成**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_content.append(f"**BMAD版本**: v6-alpha\n")
    md_content.append(f"**APS模块版本**: V4.3\n\n")

    return "".join(md_content)
````

### 步骤3: 使用Write工具保存文件

````markdown
## 🚨 CRITICAL STEP - 文件保存执行

**必须实际执行文件保存操作**，而非仅输出Markdown内容。

### 保存步骤：

1. **生成文件名**：
   ```python
   from datetime import datetime
   timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
   filename = f"solution_document_{timestamp}.md"
   ```
````

2. **确定完整路径**：

   ```python
   file_path = f"{output_folder}/{docs_folder}/{filename}"
   # 例如: aps-outputs/docs/solution_document_20251024_143530.md
   ```

3. **使用IDE Write工具保存**：

   ```
   IDE Tool: Write
   File Path: {file_path}
   Content: {markdown_content}
   ```

4. **记录保存确认**：
   ```
   ✓ 方案文档已保存: {file_path} ({file_size} bytes)
   ```

````

### 步骤4: 验证文件已保存

```python
import os

def verify_file_saved(file_path, min_size=5120):
    """
    验证文件已成功保存

    Args:
        file_path: 文件路径
        min_size: 最小文件大小（bytes），默认5KB

    Returns:
        dict: 验证结果
    """
    verification_result = {
        "file_saved": False,
        "file_exists": False,
        "file_size": 0,
        "file_readable": False,
        "markdown_valid": False,
        "issues": []
    }

    # 检查文件存在
    if not os.path.exists(file_path):
        verification_result["issues"].append(f"文件不存在: {file_path}")
        return verification_result

    verification_result["file_exists"] = True

    # 检查文件大小
    file_size = os.path.getsize(file_path)
    verification_result["file_size"] = file_size

    if file_size < min_size:
        verification_result["issues"].append(
            f"文件太小: {file_size} bytes (最小要求: {min_size} bytes)"
        )
        return verification_result

    # 检查文件可读
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        verification_result["file_readable"] = True
    except Exception as e:
        verification_result["issues"].append(f"文件不可读: {e}")
        return verification_result

    # 验证Markdown格式
    if content.startswith("# ") and "##" in content:
        verification_result["markdown_valid"] = True
    else:
        verification_result["issues"].append("Markdown格式可能不正确")

    # 全部通过
    if (verification_result["file_exists"] and
        verification_result["file_readable"] and
        verification_result["markdown_valid"] and
        file_size >= min_size):
        verification_result["file_saved"] = True

    return verification_result
````

### 步骤5: 生成文件元数据

```python
def generate_file_metadata(file_path, verification_result):
    """
    生成文件元数据

    Returns:
        dict: 文件元数据
    """
    from datetime import datetime
    import hashlib

    file_metadata = {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "file_size": verification_result["file_size"],
        "saved_at": datetime.now().isoformat(),
        "format": "markdown",
        "verification_passed": verification_result["file_saved"]
    }

    # 计算文件hash
    if verification_result["file_saved"]:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        file_metadata["hash"] = file_hash

    return file_metadata
```

## 输出

```yaml
outputs:
  solution_document_path:
    type: string
    description: 方案文档的完整路径
    example: 'aps-outputs/docs/solution_document_20251024_143530.md'

  solution_document_content:
    type: string
    description: 方案文档的Markdown内容

  verification_result:
    type: object
    description: 文件保存验证结果
    structure:
      file_saved: boolean
      file_exists: boolean
      file_size: integer
      file_readable: boolean
      markdown_valid: boolean
      issues: array

  file_metadata:
    type: object
    description: 文件元数据
    structure:
      file_path: string
      file_name: string
      file_size: integer
      saved_at: string (ISO8601)
      format: string
      hash: string (MD5)
```

## 质量检查

- [ ] 输出目录已创建
- [ ] Markdown文档包含所有6个核心章节
- [ ] 数据来源已标注（文件名、时间戳、hash）
- [ ] 所有引用都清晰可见
- [ ] 文件已使用Write工具保存
- [ ] 文件大小 >= 5KB
- [ ] 文件可读且格式正确
- [ ] 验证结果显示file_saved = true

## 引用

- @编排协调专家库/文档格式规范
- @输出管理规范/Markdown模板

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 强制文件保存 + 验证，方案文档作为独立交付物
