# Task: Save Solution Document

**任务ID**: `save-solution-document`
**版本**: V4.3
**用途**: Phase 3 Step 3.3 - 将完整方案保存为Markdown文档，作为独立交付物

---

## 🚨🚨🚨 CRITICAL WARNING - 必读 🚨🚨🚨

### ⚠️ 此任务必须生成两个特定文件

**1. ✅ `solution_document_{timestamp}.md` - 完整方案文档（6章节+附录）**
   - **文件名格式**: `solution_document_YYYYMMDD_HHMMSS.md`
   - **不是** `README.md`（那是用户手册）
   - **不是** `user_manual.md`
   - **不是** `documentation.md`
   - **必须是** `solution_document_` 开头的时间戳文件

**2. ✅ `solution_data_{timestamp}.yaml` - 结构化方案数据**
   - **文件名格式**: `solution_data_YYYYMMDD_HHMMSS.yaml`
   - 包含完整的 TenElementModel 和 integrated_solution
   - 支持独立的代码生成流程

### ❌ 严禁的行为

- **❌ 不要生成 README.md 作为替代**
- **❌ 不要跳过方案文档生成步骤**
- **❌ 不要在本任务完成前生成代码**
- **❌ 不要只输出 Markdown 内容而不保存文件**

### ✅ 执行顺序（强制）

```
1. 生成完整的方案文档内容（包含全部6个章节和附录）
2. 使用 Write 工具保存 solution_document_{timestamp}.md
3. 验证 Markdown 文件已成功保存
4. 验证文件包含所有必需章节
5. 使用 Write 工具保存 solution_data_{timestamp}.yaml
6. 验证 YAML 文件已成功保存
7. 返回验证结果（包含 content_validation）
```

### 🔒 阻断机制

如果以上文件未正确保存，**Phase 3 将无法继续到代码生成阶段**。

Workflow 的 post_action_verify 会检查：
- ✓ 文件名是否以 `solution_document_` 开头
- ✓ 文件是否包含全部 7 个必需章节
- ✓ YAML 文件是否成功保存

**任何检查失败都会阻断流程！**

---

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

### 步骤3.5: 🚨 使用Write工具保存Markdown文件（带自动重试）

**CRITICAL STEP - 必须实际执行文件写入 + 验证 + 失败重试**

此步骤AI必须调用IDE的Write工具，并在保存后立即验证，失败则自动重试。

**完整保存流程（包含重试逻辑）**：

```python
def save_solution_document_with_retry(file_path, markdown_content, max_retries=3):
    """
    保存方案文档Markdown文件，失败时自动重试

    这是方案文档保存的最严格验证机制（7层验证）

    Args:
        file_path: Markdown文件路径
        markdown_content: Markdown内容
        max_retries: 最大重试次数（默认3次）

    Returns:
        dict: 保存结果

    Raises:
        RuntimeError: 所有重试均失败
    """
    import time
    import os

    retry_delays = [1, 5, 10]  # 指数退避：1秒，5秒，10秒

    for attempt in range(max_retries):
        try:
            print(f"🔄 尝试保存Markdown文件 (第 {attempt + 1}/{max_retries} 次)...")

            # 1. 🚨 调用Write工具保存文件
            # IDE Tool: Write
            #   file_path: {file_path}
            #   content: {markdown_content}
            # 注意：实际执行时，AI必须调用IDE的Write工具，而非Python代码

            # 模拟保存操作（实际中由IDE工具完成）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"✓ Markdown文件写入完成: {file_path}")

            # 2. 立即验证文件已成功保存（7层验证）
            verification = verify_markdown_saved_immediately(file_path)

            if verification["all_checks_passed"]:
                print(f"✅ Markdown保存成功并验证通过 (尝试 {attempt + 1} 次)")
                return {
                    "success": True,
                    "file_path": file_path,
                    "attempts": attempt + 1,
                    "verification": verification
                }
            else:
                # 验证失败，准备重试
                failed_checks = [k for k, v in verification["checks"].items() if not v]
                print(f"⚠ Markdown验证失败: {failed_checks}")
                raise ValueError(f"Markdown验证失败: {failed_checks}")

        except Exception as e:
            print(f"❌ Markdown保存失败 (尝试 {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                # 还有重试机会
                delay = retry_delays[attempt]
                print(f"⏳ {delay}秒后重试...")
                time.sleep(delay)
            else:
                # 所有重试均失败
                error_message = f"""
❌ CRITICAL ERROR: 方案文档(Markdown)保存失败！

文件路径: {file_path}
尝试次数: {max_retries}
最后错误: {e}

可能原因:
1. 磁盘空间不足
2. 文件权限问题
3. 目录不存在或不可写
4. 文件系统故障
5. 内容生成不完整（缺少必需章节）

建议操作:
1. 检查磁盘剩余空间: df -h
2. 检查目录权限: ls -la {os.path.dirname(file_path)}
3. 检查目录是否存在: ls -d {os.path.dirname(file_path)}
4. 验证Markdown内容是否包含所有7个必需章节

⛔ 流程已阻断，无法继续执行。请解决上述问题后重新开始。
"""
                raise RuntimeError(error_message)

    # 不应该到达这里
    raise RuntimeError("Markdown保存逻辑错误")


def verify_markdown_saved_immediately(file_path, min_size=1024):
    """
    保存Markdown后立即验证文件（用于重试逻辑）

    7层验证（方案文档最严格）:
    L1: 文件存在 (exists)
    L2: 是否为文件 (is_file)
    L3: 文件名格式 (filename_valid) - 防止生成README.md
    L4: 文件大小 (size_valid, min=1024) - 比Phase状态更严格
    L5: 文件可读 (readable)
    L6: Markdown格式 (markdown_valid)
    L7: 内容结构 (has_all_sections) - 7个必需章节

    Args:
        file_path: Markdown文件路径
        min_size: 最小文件大小（默认1KB）

    Returns:
        dict: 验证结果
    """
    verification = {
        "file_path": file_path,
        "checks": {},
        "all_checks_passed": False
    }

    try:
        # L1: 检查文件存在
        if not os.path.exists(file_path):
            verification["checks"]["exists"] = False
            return verification
        verification["checks"]["exists"] = True

        # L2: 检查是否为文件
        if not os.path.isfile(file_path):
            verification["checks"]["is_file"] = False
            return verification
        verification["checks"]["is_file"] = True

        # L3: 检查文件名格式（防止生成README.md等错误文件）
        filename = os.path.basename(file_path)
        if not filename.startswith("solution_document_"):
            verification["checks"]["filename_valid"] = False
            verification["filename_error"] = f"文件名不符合规范: {filename}"
            return verification
        verification["checks"]["filename_valid"] = True

        # L4: 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size < min_size:
            verification["checks"]["size_valid"] = False
            verification["file_size"] = file_size
            return verification
        verification["checks"]["size_valid"] = True
        verification["file_size"] = file_size

        # L5: 检查文件可读
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content:
            verification["checks"]["readable"] = False
            return verification
        verification["checks"]["readable"] = True

        # L6: 检查Markdown格式
        if not (content.startswith("# ") and "##" in content):
            verification["checks"]["markdown_valid"] = False
            return verification
        verification["checks"]["markdown_valid"] = True

        # L7: 检查内容结构（7个必需章节）
        required_sections = [
            "## 1. 问题定义与建模",
            "## 2. 领域适配方案",
            "## 3. 约束处理策略",
            "## 4. 目标优化策略",
            "## 5. 算法选择与配置",
            "## 6. 实现路线图",
            "## 7. 附录: TenElementModel完整定义"
        ]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            verification["checks"]["has_all_sections"] = False
            verification["missing_sections"] = missing_sections
            return verification
        verification["checks"]["has_all_sections"] = True

        # 所有检查通过
        verification["all_checks_passed"] = True
        return verification

    except Exception as e:
        verification["checks"]["exception"] = str(e)
        verification["all_checks_passed"] = False
        return verification
```

### 步骤4: 验证文件已保存（外部验证接口）

```python
import os

def verify_file_saved(file_path, min_size=1024):
    """
    验证文件已成功保存（增强版：包含内容结构验证）

    Args:
        file_path: 文件路径
        min_size: 最小文件大小（bytes），默认1KB（仅用于防止空文件）

    Returns:
        dict: 验证结果
            - file_saved: 总体是否通过
            - file_exists: 文件是否存在
            - file_size: 文件大小
            - file_readable: 文件是否可读
            - markdown_valid: Markdown格式是否有效
            - content_validation: 内容结构验证结果（新增）
                - has_required_sections: 是否包含所有必需章节
                - missing_sections: 缺失的章节列表
            - issues: 问题列表
    """
    verification_result = {
        "file_saved": False,
        "file_exists": False,
        "file_size": 0,
        "file_readable": False,
        "markdown_valid": False,
        "content_validation": {
            "has_required_sections": False,
            "missing_sections": []
        },
        "issues": []
    }

    # 检查文件存在
    if not os.path.exists(file_path):
        verification_result["issues"].append(f"文件不存在: {file_path}")
        return verification_result

    verification_result["file_exists"] = True

    # 检查文件名格式（防止生成README.md等错误文件）
    filename = os.path.basename(file_path)
    if not filename.startswith("solution_document_"):
        verification_result["issues"].append(
            f"文件名不符合规范: {filename} (应为 solution_document_{{timestamp}}.md)"
        )
        # 文件名错误是严重问题，直接返回
        return verification_result

    # 检查文件大小（仅用于防止空文件）
    file_size = os.path.getsize(file_path)
    verification_result["file_size"] = file_size

    if file_size < min_size:
        verification_result["issues"].append(
            f"文件太小: {file_size} bytes (最小要求: {min_size} bytes，可能是空文件)"
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

    # ✅ 核心新增：验证内容结构完整性
    required_sections = [
        "## 1. 问题定义与建模",
        "## 2. 领域适配方案",
        "## 3. 约束处理策略",
        "## 4. 目标优化策略",
        "## 5. 算法选择与配置",
        "## 6. 实现路线图",
        "## 7. 附录: TenElementModel完整定义"
    ]

    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    if missing_sections:
        verification_result["content_validation"]["missing_sections"] = missing_sections
        verification_result["issues"].append(
            f"缺少必需章节: {', '.join(missing_sections)}"
        )
        verification_result["issues"].append(
            "提示: 方案文档不是用户手册(README.md)，而是包含6个技术章节的完整设计文档"
        )
    else:
        verification_result["content_validation"]["has_required_sections"] = True

    # 全部通过的条件（移除文件大小检查）
    if (verification_result["file_exists"] and
        verification_result["file_readable"] and
        verification_result["markdown_valid"] and
        verification_result["content_validation"]["has_required_sections"]):
        verification_result["file_saved"] = True

    return verification_result
````

### 步骤4.5: 🚨 保存YAML格式的方案数据（带自动重试）

**目的**: 支持独立的代码生成，只需方案文件即可生成代码

**CRITICAL**: 此步骤必须包含自动重试机制，确保YAML文件100%可靠保存

```python
import yaml
import time
import os

def save_solution_data_yaml_with_retry(integrated_solution, ten_element_model, output_folder, docs_folder, timestamp, max_retries=3):
    """
    保存方案的结构化数据为YAML格式，失败时自动重试

    这是方案数据YAML保存机制（5层验证）

    Args:
        integrated_solution: 完整方案对象
        ten_element_model: TenElementModel对象
        output_folder: 输出目录
        docs_folder: 文档子目录
        timestamp: 时间戳
        max_retries: 最大重试次数（默认3次）

    Returns:
        dict: YAML文件保存结果

    Raises:
        RuntimeError: 所有重试均失败
    """
    retry_delays = [1, 5, 10]  # 指数退避：1秒，5秒，10秒

    # 准备YAML数据
    solution_data = {
        "solution_metadata": integrated_solution.get("metadata", {}),
        "solution_sections": integrated_solution.get("sections", {}),
        "ten_element_model": ten_element_model,
        "references": integrated_solution.get("references", {}),
        "traceability": integrated_solution.get("traceability", {}),
        "citations_summary": integrated_solution.get("citations_summary", {})
    }

    # 生成文件路径
    yaml_filename = f"solution_data_{timestamp}.yaml"
    yaml_path = f"{output_folder}/{docs_folder}/{yaml_filename}"

    # 序列化为YAML
    yaml_content = yaml.dump(solution_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"✓ YAML数据已准备: {len(yaml_content)} bytes")

    for attempt in range(max_retries):
        try:
            print(f"🔄 尝试保存YAML文件 (第 {attempt + 1}/{max_retries} 次)...")

            # 1. 🚨 调用Write工具保存YAML文件
            # IDE Tool: Write
            #   file_path: {yaml_path}
            #   content: {yaml_content}
            # 注意：实际执行时，AI必须调用IDE的Write工具，而非Python代码

            # 模拟保存操作（实际中由IDE工具完成）
            with open(yaml_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)

            print(f"✓ YAML文件写入完成: {yaml_path}")

            # 2. 立即验证文件已成功保存（5层验证）
            verification = verify_yaml_saved_immediately(yaml_path)

            if verification["all_checks_passed"]:
                yaml_size = os.path.getsize(yaml_path)
                print(f"✅ YAML保存成功并验证通过 (尝试 {attempt + 1} 次)")
                return {
                    "yaml_saved": True,
                    "yaml_path": yaml_path,
                    "yaml_size": yaml_size,
                    "attempts": attempt + 1,
                    "verification": verification
                }
            else:
                # 验证失败，准备重试
                failed_checks = [k for k, v in verification["checks"].items() if not v]
                print(f"⚠ YAML验证失败: {failed_checks}")
                raise ValueError(f"YAML验证失败: {failed_checks}")

        except Exception as e:
            print(f"❌ YAML保存失败 (尝试 {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                # 还有重试机会
                delay = retry_delays[attempt]
                print(f"⏳ {delay}秒后重试...")
                time.sleep(delay)
            else:
                # 所有重试均失败
                error_message = f"""
❌ CRITICAL ERROR: 方案数据(YAML)保存失败！

文件路径: {yaml_path}
尝试次数: {max_retries}
最后错误: {e}

可能原因:
1. 磁盘空间不足
2. 文件权限问题
3. 目录不存在或不可写
4. 文件系统故障
5. YAML序列化失败

建议操作:
1. 检查磁盘剩余空间: df -h
2. 检查目录权限: ls -la {os.path.dirname(yaml_path)}
3. 检查目录是否存在: ls -d {os.path.dirname(yaml_path)}
4. 验证solution_data对象是否完整

⛔ 流程已阻断，无法继续执行。请解决上述问题后重新开始。
"""
                raise RuntimeError(error_message)

    # 不应该到达这里
    raise RuntimeError("YAML保存逻辑错误")


def verify_yaml_saved_immediately(file_path, min_size=100):
    """
    保存YAML后立即验证文件（用于重试逻辑）

    5层验证（YAML数据文件）:
    L1: 文件存在 (exists)
    L2: 文件大小 (size_valid, min=100)
    L3: 文件可读 (readable)
    L4: YAML格式 (yaml_valid)
    L5: 必需键存在 (has_required_keys)

    Args:
        file_path: YAML文件路径
        min_size: 最小文件大小（默认100 bytes）

    Returns:
        dict: 验证结果
    """
    verification = {
        "file_path": file_path,
        "checks": {},
        "all_checks_passed": False
    }

    try:
        # L1: 检查文件存在
        if not os.path.exists(file_path):
            verification["checks"]["exists"] = False
            return verification
        verification["checks"]["exists"] = True

        # L2: 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size < min_size:
            verification["checks"]["size_valid"] = False
            verification["file_size"] = file_size
            return verification
        verification["checks"]["size_valid"] = True
        verification["file_size"] = file_size

        # L3: 检查文件可读
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content:
            verification["checks"]["readable"] = False
            return verification
        verification["checks"]["readable"] = True

        # L4: 检查YAML格式
        yaml_data = yaml.safe_load(content)
        if not isinstance(yaml_data, dict):
            verification["checks"]["yaml_valid"] = False
            return verification
        verification["checks"]["yaml_valid"] = True

        # L5: 检查必需键存在
        required_keys = ["solution_metadata", "solution_sections", "ten_element_model"]
        missing_keys = []
        for key in required_keys:
            if key not in yaml_data:
                missing_keys.append(key)

        if missing_keys:
            verification["checks"]["has_required_keys"] = False
            verification["missing_keys"] = missing_keys
            return verification
        verification["checks"]["has_required_keys"] = True

        # 所有检查通过
        verification["all_checks_passed"] = True
        return verification

    except Exception as e:
        verification["checks"]["exception"] = str(e)
        verification["all_checks_passed"] = False
        return verification
```

**🚨 强制要求**：
- 必须使用 `save_solution_data_yaml_with_retry()` 函数，不允许直接保存YAML文件
- 验证失败必须重试，所有重试失败必须阻断流程
- 不允许跳过验证步骤

### 步骤5: 生成文件元数据

```python
def generate_file_metadata(file_path, verification_result, yaml_result=None):
    """
    生成文件元数据

    Returns:
        dict: 文件元数据
    """
    from datetime import datetime
    import hashlib

    file_metadata = {
        "markdown_file": {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": verification_result["file_size"],
            "saved_at": datetime.now().isoformat(),
            "format": "markdown",
            "verification_passed": verification_result["file_saved"]
        }
    }

    # 计算Markdown文件hash
    if verification_result["file_saved"]:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        file_metadata["markdown_file"]["hash"] = file_hash

    # 添加YAML文件元数据（如果有）
    if yaml_result and yaml_result.get("yaml_saved"):
        file_metadata["yaml_file"] = {
            "file_path": yaml_result["yaml_path"],
            "file_name": os.path.basename(yaml_result["yaml_path"]),
            "file_size": yaml_result["yaml_size"],
            "format": "yaml",
            "purpose": "结构化数据，支持独立代码生成"
        }

        # 计算YAML文件hash
        with open(yaml_result["yaml_path"], 'rb') as f:
            yaml_hash = hashlib.md5(f.read()).hexdigest()
        file_metadata["yaml_file"]["hash"] = yaml_hash

    return file_metadata
```

## 输出

```yaml
outputs:
  solution_document_path:
    type: string
    description: 方案文档的完整路径（Markdown格式）
    example: 'aps-outputs/docs/solution_document_20251024_143530.md'

  solution_data_path:
    type: string
    description: 方案数据的完整路径（YAML格式，新增）
    example: 'aps-outputs/docs/solution_data_20251024_143530.yaml'
    purpose: 支持独立代码生成，包含完整的方案对象和TenElementModel

  solution_document_content:
    type: string
    description: 方案文档的Markdown内容

  verification_result:
    type: object
    description: 文件保存验证结果（包含Markdown和YAML）
    structure:
      markdown_file:
        file_saved: boolean # 总体是否通过所有检查
        file_exists: boolean
        file_size: integer
        file_readable: boolean
        markdown_valid: boolean
        content_validation: # ✅ 新增：内容结构验证
          has_required_sections: boolean
          missing_sections: array # 缺失的章节列表
        issues: array
      yaml_file:
        yaml_saved: boolean
        yaml_path: string
        yaml_size: integer
        error: string (如果失败)

  yaml_save_result:
    type: object
    description: YAML文件保存结果（已合并到verification_result中）
    deprecated: true
    note: 使用 verification_result.yaml_file 代替

  file_metadata:
    type: object
    description: 文件元数据（包含Markdown和YAML）
    structure:
      markdown_file:
        file_path: string
        file_name: string
        file_size: integer
        saved_at: string (ISO8601)
        format: string
        hash: string (MD5)
      yaml_file:
        file_path: string
        file_name: string
        file_size: integer
        format: string
        purpose: string
        hash: string (MD5)
```

## 质量检查

### 🔴 P0 - 关键检查（阻断级别）

- [ ] **文件名格式正确**: solution_document_{timestamp}.md （不是README.md）
- [ ] **包含所有7个必需章节**:
  - [ ] 1. 问题定义与建模
  - [ ] 2. 领域适配方案
  - [ ] 3. 约束处理策略
  - [ ] 4. 目标优化策略
  - [ ] 5. 算法选择与配置
  - [ ] 6. 实现路线图
  - [ ] 7. 附录: TenElementModel完整定义
- [ ] **content_validation.has_required_sections = true**
- [ ] **Markdown文件已使用Write工具保存**
- [ ] **YAML文件已使用Write工具保存**

### 🟡 P1 - 重要检查

- [ ] 输出目录已创建
- [ ] 数据来源已标注（文件名、时间戳、hash）
- [ ] 所有引用都清晰可见
- [ ] Markdown文件可读且格式正确
- [ ] Markdown验证结果显示 markdown_file.file_saved = true
- [ ] YAML文件包含完整的方案对象和TenElementModel
- [ ] YAML文件可被解析
- [ ] YAML验证结果显示 yaml_file.yaml_saved = true

### 🟢 P2 - 可选检查

- [ ] Markdown文件大小合理（通常 > 10KB）
- [ ] 包含图表或表格
- [ ] 包含追溯性映射表（附录A2）

## 引用

- @编排协调专家库/文档格式规范
- @输出管理规范/Markdown模板

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 强制文件保存 + 验证，方案文档作为独立交付物
