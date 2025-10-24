# Task: Integrate Solution

**任务ID**: `integrate-solution`
**版本**: V4.3
**用途**: Phase 3 Step 3.1 - 融合TenElementModel和专家分析，生成完整的调度优化方案（纯方案，不含代码）

## 输入

```yaml
inputs:
  # 从Phase 1.5状态文件加载
  - ten_element_model: TenElementModel对象
  - model_baseline: 模型基线
  - model_hash: 模型哈希值

  # 从Phase 2状态文件加载
  - domain_analysis: 领域专家分析结果
  - constraint_analysis: 约束专家分析结果
  - objective_analysis: 目标专家分析结果
  - algorithm_recommendations: 算法专家推荐
  - consistency_report: 一致性报告

  # 元数据
  - phase_1_5_metadata: Phase 1.5元数据
  - phase_2_metadata: Phase 2元数据
```

## 🚨 强制要求（MANDATORY）

### 1. 数据来源必须是状态文件

**CRITICAL**: 本任务的所有输入数据必须来自Phase 1.5和Phase 2的状态文件，不允许使用内存上下文或假设数据。

```yaml
data_source_requirement:
  critical: true
  allowed_sources:
    - phase_1_5_state_latest.yaml
    - phase_2_state_latest.yaml
  forbidden_sources:
    - memory_context
    - assumptions
    - hallucinations
```

### 2. 只输出方案，不生成代码

本任务**只生成调度优化方案文档**，不生成任何可执行代码。代码生成由后续Step 3.5完成。

```yaml
output_constraint:
  allowed:
    - 方案描述
    - 设计决策
    - 实现路线图
    - 架构设计
  forbidden:
    - Python代码
    - 可执行代码
    - 代码片段（除非作为示例说明）
```

### 3. 所有决策必须有依据

方案中的每个决策点都必须标注来源：

```markdown
示例:
决策: 使用Tabu Search算法
依据: @算法专家分析 - algorithm_recommendations.selected_algorithm
引用: phase_2_state.state_data.algorithm_recommendations
```

## 处理逻辑

### 步骤1: 验证输入数据完整性

```python
def validate_input_data(inputs):
    """
    验证所有必需的输入数据已提供且格式正确

    Args:
        inputs: 输入数据字典

    Raises:
        ValueError: 数据缺失或格式错误

    Returns:
        dict: 验证报告
    """
    validation_report = {
        "all_valid": True,
        "checks": []
    }

    # 验证TenElementModel
    required_fields = [
        "ten_element_model",
        "model_baseline",
        "model_hash",
        "domain_analysis",
        "constraint_analysis",
        "objective_analysis",
        "algorithm_recommendations"
    ]

    for field in required_fields:
        if field not in inputs or inputs[field] is None:
            validation_report["all_valid"] = False
            validation_report["checks"].append({
                "field": field,
                "status": "MISSING",
                "message": f"必需字段 {field} 缺失"
            })
        else:
            validation_report["checks"].append({
                "field": field,
                "status": "OK",
                "message": f"字段 {field} 存在"
            })

    if not validation_report["all_valid"]:
        raise ValueError(
            "输入数据验证失败。请确保Phase 1.5和Phase 2的状态文件已正确加载。"
        )

    print("✓ 输入数据验证通过")
    return validation_report
```

### 步骤2: 提取数据来源信息

```python
def extract_data_sources(phase_1_5_metadata, phase_2_metadata):
    """
    提取数据来源信息，用于方案文档的可追溯性

    Returns:
        dict: 数据来源信息
    """
    data_sources = {
        "ten_element_model": {
            "source_file": f"phase_1_5_state_{phase_1_5_metadata.get('timestamp', 'unknown')}.yaml",
            "timestamp": phase_1_5_metadata.get("timestamp"),
            "hash": phase_1_5_metadata.get("hash"),
            "version": phase_1_5_metadata.get("version", "4.3")
        },
        "expert_analyses": {
            "source_file": f"phase_2_state_{phase_2_metadata.get('timestamp', 'unknown')}.yaml",
            "timestamp": phase_2_metadata.get("timestamp"),
            "hash": phase_2_metadata.get("hash"),
            "version": phase_2_metadata.get("version", "4.3")
        }
    }

    print(f"✓ 数据来源: TenElementModel from {data_sources['ten_element_model']['source_file']}")
    print(f"✓ 数据来源: 专家分析 from {data_sources['expert_analyses']['source_file']}")

    return data_sources
```

### 步骤3: 融合方案各部分

#### 3.1 问题定义与建模总结

```python
def integrate_problem_definition(ten_element_model):
    """
    基于TenElementModel生成问题定义部分

    Returns:
        dict: 问题定义部分
    """
    problem_definition = {
        "title": "问题定义与建模",
        "sections": {
            "decision_variables": {
                "title": "决策变量",
                "content": ten_element_model.get("decision_variables", []),
                "source": "TenElementModel - Element 1"
            },
            "parameters": {
                "title": "参数",
                "content": ten_element_model.get("parameters", []),
                "source": "TenElementModel - Element 2"
            },
            "constraints": {
                "title": "约束清单",
                "content": ten_element_model.get("constraints", []),
                "source": "TenElementModel - Element 3"
            },
            "objectives": {
                "title": "优化目标",
                "content": ten_element_model.get("objectives", []),
                "source": "TenElementModel - Element 4"
            },
            "time_model": {
                "title": "时间模型",
                "content": ten_element_model.get("time_model", {}),
                "source": "TenElementModel - Element 6"
            }
        }
    }

    print("✓ 问题定义部分融合完成")
    return problem_definition
```

#### 3.2 领域适配方案

```python
def integrate_domain_adaptation(domain_analysis, ten_element_model):
    """
    融合领域专家分析，生成领域适配方案

    Returns:
        dict: 领域适配方案
    """
    domain_adaptation = {
        "title": "领域适配方案",
        "sections": {
            "industry_characteristics": {
                "title": "行业特点",
                "content": domain_analysis.get("industry_identification", {}),
                "source": "Phase 2 - 领域专家分析",
                "reference": "phase_2_state.domain_analysis.industry_identification"
            },
            "business_rules": {
                "title": "业务规则",
                "content": domain_analysis.get("business_rules", []),
                "source": "Phase 2 - 领域专家分析",
                "reference": "phase_2_state.domain_analysis.business_rules"
            },
            "domain_constraints": {
                "title": "领域特定约束",
                "content": domain_analysis.get("domain_constraints", []),
                "source": "Phase 2 - 领域专家分析",
                "reference": "phase_2_state.domain_analysis.domain_constraints",
                "mapping_to_model": "映射到TenElementModel约束清单"
            },
            "adaptation_suggestions": {
                "title": "适配建议",
                "content": domain_analysis.get("adaptation_suggestions", []),
                "source": "Phase 2 - 领域专家分析"
            }
        }
    }

    print("✓ 领域适配方案融合完成")
    return domain_adaptation
```

#### 3.3 约束处理策略

```python
def integrate_constraint_strategy(constraint_analysis, ten_element_model):
    """
    融合约束专家分析，生成约束处理策略

    Returns:
        dict: 约束处理策略
    """
    constraint_strategy = {
        "title": "约束处理策略",
        "sections": {
            "constraint_classification": {
                "title": "约束分类",
                "hard_constraints": constraint_analysis.get("hard_constraints", []),
                "soft_constraints": constraint_analysis.get("soft_constraints", []),
                "source": "Phase 2 - 约束专家分析",
                "reference": "phase_2_state.constraint_analysis"
            },
            "handling_methods": {
                "title": "处理方法",
                "hard_constraint_strategy": {
                    "method": constraint_analysis.get("hard_constraint_method", "repair"),
                    "description": "硬约束处理策略",
                    "citations": constraint_analysis.get("hard_constraint_citations", []),
                    "source": "@约束专家库"
                },
                "soft_constraint_strategy": {
                    "method": constraint_analysis.get("soft_constraint_method", "penalty"),
                    "description": "软约束处理策略",
                    "citations": constraint_analysis.get("soft_constraint_citations", []),
                    "source": "@约束专家库"
                }
            },
            "validation_approach": {
                "title": "验证方法",
                "content": constraint_analysis.get("validation_methods", []),
                "source": "Phase 2 - 约束专家分析"
            },
            "conflict_resolution": {
                "title": "冲突解决",
                "content": constraint_analysis.get("conflict_resolution", {}),
                "source": "Phase 2 - 约束专家分析"
            }
        }
    }

    print("✓ 约束处理策略融合完成")
    return constraint_strategy
```

#### 3.4 目标优化策略

```python
def integrate_objective_strategy(objective_analysis, ten_element_model):
    """
    融合目标专家分析，生成目标优化策略

    Returns:
        dict: 目标优化策略
    """
    objective_strategy = {
        "title": "目标优化策略",
        "sections": {
            "objective_hierarchy": {
                "title": "目标优先级",
                "primary_objective": objective_analysis.get("primary_objective", {}),
                "secondary_objectives": objective_analysis.get("secondary_objectives", []),
                "source": "Phase 2 - 目标专家分析",
                "reference": "phase_2_state.objective_analysis"
            },
            "multi_objective_handling": {
                "title": "多目标处理",
                "approach": objective_analysis.get("multi_objective_approach", "weighted_sum"),
                "weights": objective_analysis.get("objective_weights", {}),
                "justification": objective_analysis.get("weight_justification", ""),
                "source": "Phase 2 - 目标专家分析",
                "citations": objective_analysis.get("objective_citations", [])
            },
            "objective_function_design": {
                "title": "目标函数设计",
                "formulation": objective_analysis.get("objective_formulation", ""),
                "considerations": objective_analysis.get("design_considerations", []),
                "source": "Phase 2 - 目标专家分析",
                "reference": "@目标专家库"
            }
        }
    }

    print("✓ 目标优化策略融合完成")
    return objective_strategy
```

#### 3.5 算法选择与配置

```python
def integrate_algorithm_selection(algorithm_recommendations, ten_element_model):
    """
    融合算法专家推荐，生成算法选择与配置方案

    Returns:
        dict: 算法选择与配置
    """
    algorithm_selection = {
        "title": "算法选择与配置",
        "sections": {
            "selected_algorithm": {
                "title": "选定算法",
                "algorithm_name": algorithm_recommendations.get("selected_algorithm", ""),
                "algorithm_type": algorithm_recommendations.get("algorithm_type", ""),
                "selection_rationale": algorithm_recommendations.get("selection_rationale", ""),
                "source": "Phase 2 - 算法专家分析",
                "reference": "phase_2_state.algorithm_recommendations.selected_algorithm",
                "citations": algorithm_recommendations.get("algorithm_citations", [])
            },
            "algorithm_configuration": {
                "title": "算法配置",
                "parameters": algorithm_recommendations.get("recommended_parameters", {}),
                "parameter_justification": algorithm_recommendations.get("parameter_justification", {}),
                "source": "Phase 2 - 算法专家分析",
                "reference": "@算法专家库"
            },
            "optimization_suggestions": {
                "title": "优化建议",
                "content": algorithm_recommendations.get("optimization_suggestions", []),
                "source": "Phase 2 - 算法专家分析"
            },
            "expected_performance": {
                "title": "预期性能",
                "time_complexity": algorithm_recommendations.get("time_complexity", ""),
                "space_complexity": algorithm_recommendations.get("space_complexity", ""),
                "solution_quality": algorithm_recommendations.get("solution_quality_expectation", ""),
                "source": "Phase 2 - 算法专家分析"
            }
        }
    }

    print("✓ 算法选择与配置融合完成")
    return algorithm_selection
```

#### 3.6 实现路线图

```python
def create_implementation_roadmap(ten_element_model, all_analyses):
    """
    基于TenElementModel和所有专家分析，创建实现路线图

    Returns:
        dict: 实现路线图
    """
    implementation_roadmap = {
        "title": "实现路线图",
        "sections": {
            "architecture_design": {
                "title": "架构设计",
                "modules": [
                    "数据模型模块",
                    "约束验证模块",
                    "目标函数模块",
                    "算法核心模块",
                    "求解器入口模块",
                    "结果输出模块"
                ],
                "module_relationships": "模块间依赖关系图"
            },
            "data_structure_design": {
                "title": "数据结构设计",
                "decision_variable_structure": "基于TenElementModel决策变量设计",
                "parameter_structure": "基于TenElementModel参数设计",
                "solution_structure": "解决方案数据结构"
            },
            "implementation_phases": {
                "title": "实现阶段",
                "phases": [
                    {
                        "phase": "Phase 1",
                        "name": "数据模型实现",
                        "tasks": ["定义决策变量类", "定义参数类", "定义解决方案类"]
                    },
                    {
                        "phase": "Phase 2",
                        "name": "约束与目标实现",
                        "tasks": ["实现约束验证函数", "实现目标函数", "集成多目标处理"]
                    },
                    {
                        "phase": "Phase 3",
                        "name": "算法核心实现",
                        "tasks": ["实现算法主体", "实现邻域操作", "实现停止准则"]
                    },
                    {
                        "phase": "Phase 4",
                        "name": "集成与测试",
                        "tasks": ["集成所有模块", "单元测试", "集成测试", "性能测试"]
                    }
                ]
            },
            "key_functions": {
                "title": "关键函数列表",
                "functions": [
                    "initialize_solution()",
                    "validate_constraints(solution)",
                    "calculate_objective(solution)",
                    "generate_neighbor(solution)",
                    "accept_solution(new_solution, current_solution)",
                    "solve(problem_data)"
                ]
            }
        }
    }

    print("✓ 实现路线图创建完成")
    return implementation_roadmap
```

### 步骤4: 生成完整方案对象

```python
from datetime import datetime

def generate_integrated_solution(
    problem_definition,
    domain_adaptation,
    constraint_strategy,
    objective_strategy,
    algorithm_selection,
    implementation_roadmap,
    data_sources,
    ten_element_model
):
    """
    将所有部分组合成完整的方案对象

    Returns:
        dict: 完整的集成方案对象
    """
    integrated_solution = {
        "metadata": {
            "title": "调度优化方案",
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "phase": "Phase 3 - 方案集成",
            "data_sources": data_sources
        },

        "sections": {
            "1_problem_definition": problem_definition,
            "2_domain_adaptation": domain_adaptation,
            "3_constraint_strategy": constraint_strategy,
            "4_objective_strategy": objective_strategy,
            "5_algorithm_selection": algorithm_selection,
            "6_implementation_roadmap": implementation_roadmap
        },

        "references": {
            "ten_element_model": {
                "source_file": data_sources["ten_element_model"]["source_file"],
                "hash": data_sources["ten_element_model"]["hash"]
            },
            "expert_analyses": {
                "source_file": data_sources["expert_analyses"]["source_file"],
                "hash": data_sources["expert_analyses"]["hash"]
            }
        },

        "traceability": {
            "model_to_solution": "TenElementModel → 方案各章节的映射关系",
            "analyses_to_solution": "专家分析 → 方案各章节的映射关系"
        }
    }

    print("✓ 完整方案对象生成完成")
    return integrated_solution
```

### 步骤5: 生成方案元数据

```python
def generate_solution_metadata(integrated_solution, ten_element_model, all_analyses):
    """
    生成方案元数据，用于后续步骤

    Returns:
        dict: 方案元数据
    """
    solution_metadata = {
        "generated_at": datetime.now().isoformat(),
        "version": "1.0",
        "phase": "Phase 3 Step 3.1",

        "statistics": {
            "total_sections": len(integrated_solution["sections"]),
            "decision_variables_count": len(ten_element_model.get("decision_variables", [])),
            "constraints_count": len(ten_element_model.get("constraints", [])),
            "objectives_count": len(ten_element_model.get("objectives", []))
        },

        "completeness": {
            "problem_definition": True,
            "domain_adaptation": True,
            "constraint_strategy": True,
            "objective_strategy": True,
            "algorithm_selection": True,
            "implementation_roadmap": True
        },

        "quality_indicators": {
            "all_sections_present": True,
            "all_references_valid": True,
            "traceability_complete": True
        }
    }

    return solution_metadata
```

## 输出

```yaml
outputs:
  integrated_solution:
    type: object
    description: 完整的方案对象（不含代码）
    structure:
      metadata: 方案元数据
      sections:
        1_problem_definition: 问题定义与建模总结
        2_domain_adaptation: 领域适配方案
        3_constraint_strategy: 约束处理策略
        4_objective_strategy: 目标优化策略
        5_algorithm_selection: 算法选择与配置
        6_implementation_roadmap: 实现路线图
      references: 数据来源引用
      traceability: 可追溯性映射

  solution_metadata:
    type: object
    description: 方案元数据
    structure:
      generated_at: 生成时间
      version: 版本号
      statistics: 统计信息
      completeness: 完整性检查
      quality_indicators: 质量指标
```

## 质量检查

- [ ] 所有输入数据来自状态文件
- [ ] 方案包含6个核心部分
- [ ] 每个决策点都有明确依据
- [ ] 所有引用都标注来源
- [ ] 数据来源可追溯（文件名、时间戳、hash）
- [ ] 没有生成任何代码
- [ ] 实现路线图清晰可行
- [ ] 与TenElementModel一致

## 引用

- @编排协调专家库/方案融合规范
- @算法专家库/算法选择指南
- @约束专家库/约束处理策略
- @目标专家库/多目标优化方法
- @领域专家库/领域适配方法

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 基于状态文件的方案融合，方案与代码分离
