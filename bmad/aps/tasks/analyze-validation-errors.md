# Task: Analyze Validation Errors

**任务ID**: `analyze-validation-errors`
**版本**: V1.0 (V4.4新增)
**用途**: Phase 3 Step 3.6.7 - 分析代码验证错误，生成结构化的修复策略

## 背景

在V4.4之前，代码验证失败后只能简单重试，没有针对性的修复策略。本任务负责：

1. 解析验证报告中的错误类型和详情
2. 根据错误类型生成修复策略
3. 确定需要重新生成的代码组件
4. 提供增强的prompt指导

## 输入

```yaml
inputs:
  - validation_report: 代码验证报告（来自validate-code-completeness.md）
  - implementation_code: 当前生成的代码
  - ten_element_model: TenElementModel对象
  - user_approved_solution: 用户确认的方案
  - retry_count: 当前重试次数（默认0）
```

## 核心功能

### 1. 错误分类和优先级排序

```python
def classify_validation_errors(validation_report):
    """
    对验证错误进行分类和优先级排序

    Returns:
        dict: 分类后的错误信息
    """
    classified_errors = {
        "critical": [],  # 阻断性错误，必须修复
        "major": [],     # 重要错误，影响功能
        "minor": []      # 次要错误，可能影响质量
    }

    error_priority_map = {
        "TODO_FOUND": "critical",
        "EMPTY_IMPLEMENTATION": "critical",
        "NOT_IMPLEMENTED": "critical",
        "SYNTAX_ERROR": "critical",
        "MISSING_DATA_LOADER": "critical",
        "MISSING_CONSTRAINT": "major",
        "MISSING_OBJECTIVE": "major",
        "MISSING_DECISION_VARIABLE": "major",
        "MISSING_PARAMETER": "minor",
        "PLACEHOLDER_DATA": "minor",
        "CODE_SMELL": "minor"
    }

    for level_result in validation_report.get("levels", []):
        for error in level_result.get("errors", []):
            error_type = error.get("type")
            priority = error_priority_map.get(error_type, "minor")

            classified_errors[priority].append({
                "type": error_type,
                "message": error.get("message"),
                "details": error,
                "validation_level": level_result.get("level")
            })

    print("=" * 70)
    print("错误分类统计")
    print("=" * 70)
    print(f"Critical错误: {len(classified_errors['critical'])} 个")
    print(f"Major错误: {len(classified_errors['major'])} 个")
    print(f"Minor错误: {len(classified_errors['minor'])} 个")
    print("=" * 70)

    return classified_errors
```

### 2. 生成修复策略

```python
def generate_fix_strategy(classified_errors, ten_element_model, retry_count):
    """
    根据错误类型生成具体的修复策略

    Returns:
        dict: 修复策略
    """
    fix_strategy = {
        "strategy_type": None,  # full_regenerate | component_regenerate | incremental_fix
        "actions": [],
        "enhanced_prompts": [],
        "component_targets": [],
        "confidence": 0.0
    }

    critical_errors = classified_errors.get("critical", [])
    major_errors = classified_errors.get("major", [])

    # 策略1: 全量重新生成（Critical错误较多或语法错误）
    if len(critical_errors) > 3 or any(e["type"] == "SYNTAX_ERROR" for e in critical_errors):
        fix_strategy["strategy_type"] = "full_regenerate"
        fix_strategy["confidence"] = 0.4  # 低置信度，可能需要人工介入

        fix_strategy["actions"].append({
            "action": "regenerate_all",
            "reason": f"发现{len(critical_errors)}个严重错误，建议完全重新生成",
            "target": "bmad/aps/tasks/generate-code-from-solution.md",
            "enhanced_prompt": True
        })

        # 构建增强prompt
        error_summary = "\n".join([
            f"- {e['type']}: {e['message']}"
            for e in critical_errors[:5]  # 最多显示5个
        ])

        fix_strategy["enhanced_prompts"].append({
            "phase": "code_generation",
            "additional_instructions": f"""
⚠️ 警告：之前生成的代码存在以下严重问题（重试次数: {retry_count}）:

{error_summary}

请特别注意：
1. 不要使用TODO、pass或NotImplementedError
2. 确保所有组件都完整实现
3. 严格遵循TenElementModel和方案文档
4. 每个函数都必须有完整的实现体
"""
        })

        return fix_strategy

    # 策略2: 组件级重新生成（缺少特定组件）
    missing_components = []
    for error in critical_errors + major_errors:
        if error["type"] == "MISSING_DATA_LOADER":
            missing_components.append({
                "component": "data_loading_module",
                "task": "bmad/aps/tasks/generate-data-loader.md",
                "reason": "数据加载模块缺失"
            })
        elif error["type"] == "MISSING_CONSTRAINT":
            constraint_name = error["details"].get("constraint", "unknown")
            missing_components.append({
                "component": f"constraint_{constraint_name}",
                "task": "generate-code-from-solution.md#step_3.3",
                "reason": f"约束函数缺失: {constraint_name}"
            })
        elif error["type"] == "MISSING_OBJECTIVE":
            objective_name = error["details"].get("objective", "unknown")
            missing_components.append({
                "component": f"objective_{objective_name}",
                "task": "generate-code-from-solution.md#step_3.4",
                "reason": f"目标函数缺失: {objective_name}"
            })

    if missing_components:
        fix_strategy["strategy_type"] = "component_regenerate"
        fix_strategy["confidence"] = 0.7  # 中等置信度
        fix_strategy["component_targets"] = missing_components

        for component in missing_components:
            fix_strategy["actions"].append({
                "action": "regenerate_component",
                "component": component["component"],
                "target": component["task"],
                "reason": component["reason"]
            })

        return fix_strategy

    # 策略3: 增量修复（只有Minor错误或少量Major错误）
    if len(critical_errors) == 0 and len(major_errors) <= 2:
        fix_strategy["strategy_type"] = "incremental_fix"
        fix_strategy["confidence"] = 0.9  # 高置信度

        fix_strategy["actions"].append({
            "action": "apply_incremental_fixes",
            "reason": "只有少量非严重错误，可以增量修复",
            "fixes": []
        })

        # 为每个错误生成具体的修复指令
        for error in major_errors + classified_errors.get("minor", []):
            if error["type"] == "MISSING_PARAMETER":
                param_name = error["details"].get("parameter")
                fix_strategy["actions"][0]["fixes"].append({
                    "type": "add_parameter",
                    "parameter": param_name,
                    "instruction": f"添加参数: {param_name}"
                })
            elif error["type"] == "PLACEHOLDER_DATA":
                pattern = error["details"].get("pattern")
                fix_strategy["actions"][0]["fixes"].append({
                    "type": "remove_placeholder",
                    "pattern": pattern,
                    "instruction": f"移除占位数据: {pattern}"
                })

        return fix_strategy

    # 默认策略：组件重新生成
    fix_strategy["strategy_type"] = "component_regenerate"
    fix_strategy["confidence"] = 0.6
    fix_strategy["actions"].append({
        "action": "regenerate_with_guidance",
        "reason": "错误类型复杂，建议基于错误指导重新生成关键组件"
    })

    return fix_strategy
```

### 3. 生成修复报告

```python
from datetime import datetime

def generate_fix_report(classified_errors, fix_strategy, retry_count):
    """
    生成详细的修复分析报告

    Returns:
        dict: 修复报告
    """
    report = {
        "metadata": {
            "analyzed_at": datetime.now().isoformat(),
            "retry_count": retry_count,
            "version": "V4.4"
        },

        "error_summary": {
            "total_errors": (
                len(classified_errors["critical"]) +
                len(classified_errors["major"]) +
                len(classified_errors["minor"])
            ),
            "critical_count": len(classified_errors["critical"]),
            "major_count": len(classified_errors["major"]),
            "minor_count": len(classified_errors["minor"])
        },

        "fix_strategy": fix_strategy,

        "recommendations": [],

        "should_retry": True,
        "should_escalate_to_human": False
    }

    # 决定是否应该继续自动修复
    if retry_count >= 2:
        report["should_escalate_to_human"] = True
        report["should_retry"] = False
        report["recommendations"].append({
            "priority": "critical",
            "recommendation": "已重试2次仍失败，建议人工介入",
            "action": "human_intervention"
        })
    elif fix_strategy["confidence"] < 0.5:
        report["should_escalate_to_human"] = True
        report["should_retry"] = False
        report["recommendations"].append({
            "priority": "high",
            "recommendation": "修复置信度低，建议人工介入或调整方案",
            "action": "human_review"
        })
    else:
        report["recommendations"].append({
            "priority": "medium",
            "recommendation": f"使用{fix_strategy['strategy_type']}策略自动修复",
            "action": "auto_fix"
        })

    # 打印报告摘要
    print("\n" + "=" * 70)
    print("修复策略分析报告")
    print("=" * 70)
    print(f"错误总数: {report['error_summary']['total_errors']}")
    print(f"  - Critical: {report['error_summary']['critical_count']}")
    print(f"  - Major: {report['error_summary']['major_count']}")
    print(f"  - Minor: {report['error_summary']['minor_count']}")
    print(f"\n修复策略: {fix_strategy['strategy_type']}")
    print(f"置信度: {fix_strategy['confidence'] * 100:.0f}%")
    print(f"重试次数: {retry_count}")
    print(f"\n建议动作: {report['recommendations'][0]['action']}")

    if report["should_escalate_to_human"]:
        print("\n⚠️  需要人工介入")
    else:
        print(f"\n✓ 将执行 {len(fix_strategy['actions'])} 个修复动作")

    print("=" * 70 + "\n")

    return report
```

### 4. 主分析函数

```python
def analyze_validation_errors(
    validation_report,
    implementation_code,
    ten_element_model,
    user_approved_solution,
    retry_count=0
):
    """
    完整的验证错误分析流程

    Args:
        validation_report: 验证报告
        implementation_code: 当前代码
        ten_element_model: 十要素模型
        user_approved_solution: 用户方案
        retry_count: 重试次数

    Returns:
        dict: 分析结果和修复策略
    """
    print("\n" + "=" * 70)
    print("开始分析验证错误")
    print("=" * 70)

    # 步骤1: 分类错误
    classified_errors = classify_validation_errors(validation_report)

    # 步骤2: 生成修复策略
    fix_strategy = generate_fix_strategy(
        classified_errors,
        ten_element_model,
        retry_count
    )

    # 步骤3: 生成修复报告
    fix_report = generate_fix_report(
        classified_errors,
        fix_strategy,
        retry_count
    )

    return {
        "classified_errors": classified_errors,
        "fix_strategy": fix_strategy,
        "fix_report": fix_report
    }
```

## 输出

```yaml
outputs:
  classified_errors:
    type: object
    description: 分类后的错误信息
    structure:
      critical: array
      major: array
      minor: array

  fix_strategy:
    type: object
    description: 修复策略
    structure:
      strategy_type: string (full_regenerate | component_regenerate | incremental_fix)
      actions: array
      enhanced_prompts: array
      component_targets: array
      confidence: float (0.0-1.0)

  fix_report:
    type: object
    description: 完整的分析报告
    structure:
      metadata: object
      error_summary: object
      fix_strategy: object
      recommendations: array
      should_retry: boolean
      should_escalate_to_human: boolean
```

## 修复策略类型说明

### 1. full_regenerate (全量重新生成)

**触发条件**:

- Critical错误 > 3个
- 存在SYNTAX_ERROR
- 代码结构性问题

**修复动作**:

- 完全重新执行generate-code-from-solution.md
- 使用增强的prompt（包含错误提示）
- 调整生成参数

### 2. component_regenerate (组件级重新生成)

**触发条件**:

- 缺少特定组件（MISSING_DATA_LOADER, MISSING_CONSTRAINT等）
- Critical错误 ≤ 3个
- 错误集中在某些组件

**修复动作**:

- 只重新生成缺失的组件
- 保留正确的代码部分
- 重新组装代码

### 3. incremental_fix (增量修复)

**触发条件**:

- 没有Critical错误
- Major错误 ≤ 2个
- 都是可以快速修复的小问题

**修复动作**:

- 应用文本替换修复
- 添加缺失的参数
- 移除占位符数据

## 人工介入触发条件

```yaml
escalate_to_human:
  - retry_count >= 2
  - fix_strategy.confidence < 0.5
  - 存在无法自动修复的错误类型
  - 用户请求人工审核
```

## 质量检查

- [ ] 所有错误都已分类
- [ ] 修复策略清晰可执行
- [ ] 置信度评估合理
- [ ] 人工介入条件明确
- [ ] 报告信息完整

## 引用

- @质量评测专家库/错误分析方法
- @编排协调专家库/修复策略设计

---

**创建**: 2025-11-03
**BMAD版本**: v6-alpha (V4.4)
**核心机制**: 错误分析与修复策略生成，支持验证-修复闭环
