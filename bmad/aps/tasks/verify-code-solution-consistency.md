# Task: Verify Code-Solution Consistency

**任务ID**: `verify-code-solution-consistency`
**版本**: V4.4.1
**用途**: Phase 3 Step 3.6.5 - 验证生成的代码与用户确认的方案完全一致，避免大模型幻觉

## 输入

```yaml
inputs:
  - implementation_code: 生成的代码
  - user_approved_solution: 用户确认的方案
  - solution_document_path: 方案文档路径
```

## 🚨 强制要求（MANDATORY）

### 1. Workflow级别强制验证

**CRITICAL**: 本任务是Phase 3的关键质量门禁，类似于状态管理中的`post_action_verify`机制。

```yaml
verification_principle:
  critical: true
  blocking: true
  理念: 'Workflow控制，不依赖大模型自觉'

  类比:
    状态管理: mandatory_save + post_action_verify
    代码一致性: mandatory_verification + post_generation_verify
```

### 2. 验证失败必须阻断

如果发现代码与方案不一致，必须：

- 阻断workflow执行
- 提供详细的不一致报告
- 要求修复后重试
- 最多重试3次

## 处理逻辑

### 步骤1: 验证文件头部引用标记

```python
import re

def verify_file_header_references(implementation_code):
    """
    验证代码文件头部是否包含完整的方案追溯信息

    Returns:
        dict: 验证结果
    """
    header = implementation_code[:1000]  # 文件头部前1000字符

    checks = {
        "solution_document_reference": False,
        "solution_hash": False,
        "data_sources": False,
        "code_composition": False
    }

    # 检查1: 方案文档引用
    if re.search(r'方案文档:\s*solution_document', header):
        checks["solution_document_reference"] = True

    # 检查2: 方案Hash
    if re.search(r'Hash:\s*[a-f0-9]{16}', header):
        checks["solution_hash"] = True

    # 检查3: 数据来源
    if 'TenElementModel' in header and 'phase_1_5_state' in header:
        checks["data_sources"] = True

    # 检查4: 代码组成说明
    if '代码组成' in header or '第1部分' in header:
        checks["code_composition"] = True

    result = {
        "all_passed": all(checks.values()),
        "checks": checks,
        "issues": [k for k, v in checks.items() if not v]
    }

    if result["all_passed"]:
        print("✓ 文件头部引用标记完整")
    else:
        print(f"✗ 文件头部引用标记不完整: {result['issues']}")

    return result
```

### 步骤1.5: 验证专家库引用完整性（V4.4.1新增）

```python
import re

def verify_expert_library_citations(implementation_code):
    """
    验证代码中的专家库引用完整性

    方案依据: @bmad/aps/tasks/generate-code-from-solution.md Line 86-114
    验证要求:
    - 专家库引用 >= 3处
    - 格式: @xxx库/yyy/zzz.md
    - 至少涵盖2个不同的专家库类型

    V4.4.1新增: 修复专家库引用缺失问题

    Returns:
        dict: 验证结果
    """
    print("\n" + "="*70)
    print("🔍 验证专家库引用完整性...")
    print("="*70)

    # 查找所有专家库引用（格式：@xxx库/yyy）
    expert_pattern = r'@[^/\s]+库/[^\s]+'
    citations = re.findall(expert_pattern, implementation_code)

    # 去重并统计
    unique_citations = list(set(citations))

    # 识别专家库类型
    expected_libraries = ['算法库', '约束库', '目标库', '领域库', '建模库']
    found_libraries = set()

    for citation in unique_citations:
        for lib in expected_libraries:
            if lib in citation:
                found_libraries.add(lib)

    # 统计结果
    result = {
        "total_citations": len(citations),
        "unique_citations": len(unique_citations),
        "citations_list": unique_citations,
        "found_libraries": list(found_libraries),
        "library_count": len(found_libraries)
    }

    # 验证1: 至少3处引用
    if result["total_citations"] < 3:
        result["passed"] = False
        result["error"] = f"专家库引用不足！要求>=3处，实际{result['total_citations']}处"
        result["severity"] = "critical"
        print(f"  ❌ 专家库引用不足: {result['total_citations']}/3")
        print(f"  找到的引用: {result['citations_list']}")
        return result

    # 验证2: 至少2个不同专家库
    if result["library_count"] < 2:
        result["passed"] = False
        result["error"] = f"专家库覆盖不足！至少需要引用2个不同专家库，实际{result['library_count']}个"
        result["severity"] = "major"
        print(f"  ❌ 专家库覆盖不足: {result['library_count']}/2")
        print(f"  已覆盖: {result['found_libraries']}")
        return result

    # 验证3: 检查引用格式
    invalid_citations = []
    for citation in unique_citations:
        # 检查是否符合格式 @xxx库/yyy
        if not re.match(r'@[^/\s]+库/[^\s]+', citation):
            invalid_citations.append(citation)

    if invalid_citations:
        result["passed"] = False
        result["error"] = f"发现格式错误的引用: {invalid_citations}"
        result["severity"] = "minor"
        result["invalid_citations"] = invalid_citations
        print(f"  ⚠️  格式错误的引用: {invalid_citations}")

    # 所有验证通过
    result["passed"] = True
    print(f"  ✓ 专家库引用数量: {result['total_citations']}处（要求>=3）")
    print(f"  ✓ 专家库类型覆盖: {result['library_count']}个（要求>=2）")
    print(f"  ✓ 已覆盖的专家库: {', '.join(result['found_libraries'])}")
    print(f"  ✓ 引用列表: ")
    for i, citation in enumerate(unique_citations[:10], 1):  # 最多显示10个
        print(f"      {i}. {citation}")
    if len(unique_citations) > 10:
        print(f"      ... 还有 {len(unique_citations) - 10} 个引用")

    print("="*70)

    return result
```

### 步骤2: 验证算法一致性

```python
def verify_algorithm_consistency(implementation_code, user_approved_solution):
    """
    验证代码使用的算法与方案一致

    方案依据: solution_document Section 5.1
    """
    # 从方案中提取算法选择
    algorithm_selection = user_approved_solution['sections']['5_algorithm_selection']
    expected_algorithm = algorithm_selection['sections']['selected_algorithm']['algorithm_name']

    # 标准化算法名称
    algorithm_keywords = {
        "genetic": ["genetic", "ga", "遗传"],
        "tabu": ["tabu", "禁忌"],
        "simulated_annealing": ["annealing", "sa", "模拟退火"],
        "particle_swarm": ["pso", "particle", "粒子群"]
    }

    # 识别代码中的算法
    code_lower = implementation_code.lower()
    detected_algorithms = []

    for algo_type, keywords in algorithm_keywords.items():
        for keyword in keywords:
            if keyword in code_lower:
                detected_algorithms.append(algo_type)
                break

    # 检查是否匹配
    expected_lower = expected_algorithm.lower()
    matched = False

    for detected in detected_algorithms:
        for keyword in algorithm_keywords.get(detected, []):
            if keyword in expected_lower:
                matched = True
                break

    if not matched:
        return {
            "consistent": False,
            "issue": f"代码中检测到算法 {detected_algorithms}，但方案要求 '{expected_algorithm}'",
            "severity": "critical",
            "expected": expected_algorithm,
            "actual": detected_algorithms
        }

    print(f"✓ 算法一致性验证通过: {expected_algorithm}")
    return {"consistent": True}
```

### 步骤3: 验证参数一致性

```python
def verify_parameters_consistency(implementation_code, user_approved_solution):
    """
    验证代码中的参数配置与方案一致

    方案依据: solution_document Section 5.2
    """
    # 从方案中提取参数
    algorithm_selection = user_approved_solution['sections']['5_algorithm_selection']
    expected_params = algorithm_selection['sections']['algorithm_configuration']['parameters']

    param_checks = []

    for param_name, expected_value in expected_params.items():
        # 检查代码中是否使用了正确的参数值
        # 匹配模式: param_name = expected_value 或 param_name=expected_value
        patterns = [
            f"{param_name}\\s*=\\s*{expected_value}",
            f"self\\.{param_name}\\s*=\\s*{expected_value}",
            f'"{param_name}"\\s*:\\s*{expected_value}',
            f"'{param_name}'\\s*:\\s*{expected_value}"
        ]

        found = False
        for pattern in patterns:
            if re.search(pattern, implementation_code):
                found = True
                break

        param_checks.append({
            "parameter": param_name,
            "expected": expected_value,
            "found": found,
            "status": "OK" if found else "MISSING"
        })

        if found:
            print(f"✓ 参数 {param_name}={expected_value} 验证通过")
        else:
            print(f"✗ 参数 {param_name}={expected_value} 未找到或不一致")

    # 汇总结果
    missing_params = [p for p in param_checks if p["status"] == "MISSING"]

    if missing_params:
        return {
            "consistent": False,
            "issues": missing_params,
            "severity": "high",
            "message": f"以下参数与方案不一致: {[p['parameter'] for p in missing_params]}"
        }

    print(f"✓ 参数一致性验证通过: {len(param_checks)}个参数全部匹配")
    return {
        "consistent": True,
        "verified_params": param_checks
    }
```

### 步骤4: 验证约束策略一致性

```python
def verify_constraint_strategy_consistency(implementation_code, user_approved_solution):
    """
    验证代码的约束处理策略与方案一致

    方案依据: solution_document Section 3.2
    """
    # 从方案中提取约束策略
    constraint_strategy = user_approved_solution['sections']['3_constraint_strategy']
    handling = constraint_strategy['sections']['handling_methods']

    hard_method = handling['hard_constraint_strategy']['method']
    soft_method = handling['soft_constraint_strategy']['method']

    checks = []

    # 检查硬约束方法
    if hard_method.lower() == "repair":
        if "repair" in implementation_code.lower():
            checks.append({
                "item": "硬约束处理方法",
                "expected": "repair",
                "status": "OK"
            })
            print("✓ 硬约束repair方法验证通过")
        else:
            checks.append({
                "item": "硬约束处理方法",
                "expected": "repair",
                "status": "MISSING",
                "issue": "方案要求repair方法，但代码中未找到"
            })
            print("✗ 硬约束repair方法未找到")

    # 检查软约束方法
    if soft_method.lower() == "penalty":
        if "penalty" in implementation_code.lower():
            checks.append({
                "item": "软约束处理方法",
                "expected": "penalty",
                "status": "OK"
            })
            print("✓ 软约束penalty方法验证通过")
        else:
            checks.append({
                "item": "软约束处理方法",
                "expected": "penalty",
                "status": "MISSING",
                "issue": "方案要求penalty方法，但代码中未找到"
            })
            print("✗ 软约束penalty方法未找到")

    # 汇总
    missing = [c for c in checks if c["status"] == "MISSING"]

    if missing:
        return {
            "consistent": False,
            "issues": missing,
            "severity": "high"
        }

    return {"consistent": True, "checks": checks}
```

### 步骤5: 验证目标函数一致性

```python
def verify_objective_consistency(implementation_code, user_approved_solution):
    """
    验证代码的目标函数与方案一致

    方案依据: solution_document Section 4.2
    """
    # 从方案中提取目标策略
    objective_strategy = user_approved_solution['sections']['4_objective_strategy']
    multi_obj = objective_strategy['sections']['multi_objective_handling']

    approach = multi_obj['approach']
    weights = multi_obj.get('weights', {})

    checks = []

    # 检查多目标方法
    if approach == "weighted_sum":
        if "weighted" in implementation_code.lower() or "weight" in implementation_code.lower():
            checks.append({
                "item": "多目标方法",
                "expected": "weighted_sum",
                "status": "OK"
            })
            print("✓ 多目标weighted_sum方法验证通过")
        else:
            checks.append({
                "item": "多目标方法",
                "expected": "weighted_sum",
                "status": "MISSING"
            })
            print("✗ 多目标方法未找到")

    # 检查权重值（如果方案中定义了）
    if weights:
        weight_str = str(weights)
        # 简化检查：至少权重相关的数字出现在代码中
        checks.append({
            "item": "目标权重",
            "expected": weights,
            "status": "OK" if any(str(w) in implementation_code for w in weights.values()) else "WARNING"
        })

    missing = [c for c in checks if c["status"] == "MISSING"]

    if missing:
        return {"consistent": False, "issues": missing, "severity": "medium"}

    return {"consistent": True, "checks": checks}
```

### 步骤6: 验证引用标记完整性

```python
def verify_reference_markers_completeness(implementation_code):
    """
    验证代码是否包含足够的引用标记

    检查引用标记的密度和完整性
    """
    checks = {
        "file_header_present": False,
        "section_references_count": 0,
        "expert_library_citations_count": 0,
        "state_file_references": False,
        "confidence_values": False
    }

    # 检查文件头部
    if "方案追溯信息" in implementation_code[:500] or "solution_document" in implementation_code[:500]:
        checks["file_header_present"] = True

    # 检查Section引用数量
    checks["section_references_count"] = len(re.findall(r'方案.*Section \d', implementation_code))

    # 检查专家库引用数量
    checks["expert_library_citations_count"] = len(re.findall(r'@\w+-library/', implementation_code))

    # 检查状态文件引用
    if 'phase_2_state' in implementation_code or 'phase_1_5_state' in implementation_code:
        checks["state_file_references"] = True

    # 检查置信度信息
    if '置信度' in implementation_code or 'confidence' in implementation_code:
        checks["confidence_values"] = True

    # 评估完整性
    issues = []

    if not checks["file_header_present"]:
        issues.append("缺少文件头部引用信息")

    if checks["section_references_count"] < 5:
        issues.append(f"Section引用过少（{checks['section_references_count']}个，建议至少5个）")

    if checks["expert_library_citations_count"] < 3:
        issues.append(f"专家库引用过少（{checks['expert_library_citations_count']}个，建议至少3个）")

    if not checks["state_file_references"]:
        issues.append("缺少状态文件引用")

    result = {
        "complete": len(issues) == 0,
        "checks": checks,
        "issues": issues
    }

    if result["complete"]:
        print(f"✓ 引用标记完整性验证通过")
        print(f"  - Section引用: {checks['section_references_count']}处")
        print(f"  - 专家库引用: {checks['expert_library_citations_count']}处")
    else:
        print(f"✗ 引用标记不完整: {issues}")

    return result
```

### 步骤7: 验证专家库引用的使用

```python
def verify_expert_library_usage(implementation_code, user_approved_solution):
    """
    验证代码是否正确引用了专家库，而不是AI自己重新编写

    核心检查: 算法核心代码应该来自专家库，不是AI生成
    """
    # 从方案中获取专家库引用
    algorithm_selection = user_approved_solution['sections']['5_algorithm_selection']
    expected_citations = algorithm_selection['sections']['selected_algorithm'].get('citations', [])

    if not expected_citations:
        return {
            "valid": True,
            "warning": "方案中未提供专家库引用，无法验证"
        }

    # 检查代码中是否标注了这些引用
    found_citations = []
    missing_citations = []

    for citation in expected_citations:
        if citation in implementation_code:
            found_citations.append(citation)
        else:
            missing_citations.append(citation)

    if missing_citations:
        return {
            "valid": False,
            "issue": "代码未标注专家库引用，可能是AI自己编写的",
            "missing_citations": missing_citations,
            "severity": "high"
        }

    # 检查是否标明"引用自专家库"
    keywords = ["引用自专家库", "专家库来源", "来源: @", "引用自 @"]
    has_library_statement = any(kw in implementation_code for kw in keywords)

    if not has_library_statement:
        return {
            "valid": False,
            "issue": "代码未明确标注来自专家库",
            "severity": "medium"
        }

    print(f"✓ 专家库引用验证通过: {len(found_citations)}个引用")
    return {"valid": True, "found_citations": found_citations}
```

### 步骤8: 生成一致性检查报告

```python
from datetime import datetime

def generate_consistency_report(all_checks):
    """
    生成完整的一致性检查报告

    Returns:
        dict: 一致性报告
    """
    report = {
        "metadata": {
            "verified_at": datetime.now().isoformat(),
            "version": "4.4.1",
            "phase": "Phase 3 Step 3.6.5"
        },

        "overall_status": "PASS",

        "checks": {
            "file_header": all_checks["file_header"],
            "algorithm_consistency": all_checks["algorithm"],
            "parameters_consistency": all_checks["parameters"],
            "constraint_strategy": all_checks["constraint_strategy"],
            "objective_consistency": all_checks["objective"],
            "reference_markers": all_checks["reference_markers"],
            "expert_library_usage": all_checks["expert_library"]
        },

        "summary": {
            "total_checks": len(all_checks),
            "passed_checks": 0,
            "failed_checks": 0,
            "warnings": 0
        },

        "issues_found": [],
        "inconsistencies": []
    }

    # 汇总结果
    for check_name, check_result in all_checks.items():
        if isinstance(check_result, dict):
            if check_result.get("consistent") == True or check_result.get("valid") == True or check_result.get("all_passed") == True or check_result.get("complete") == True:
                report["summary"]["passed_checks"] += 1
            elif check_result.get("consistent") == False or check_result.get("valid") == False:
                report["summary"]["failed_checks"] += 1
                report["issues_found"].append({
                    "check": check_name,
                    "issue": check_result.get("issue", "Unknown issue"),
                    "severity": check_result.get("severity", "unknown")
                })

                # 记录不一致项
                if "inconsistencies" not in report:
                    report["inconsistencies"] = []
                report["inconsistencies"].append(check_result)

    # 确定总体状态
    if report["summary"]["failed_checks"] > 0:
        high_severity = any(i.get("severity") == "critical" for i in report["issues_found"])
        report["overall_status"] = "FAIL" if high_severity else "WARNING"
    else:
        report["overall_status"] = "PASS"

    # 生成建议
    report["recommendations"] = []

    if report["overall_status"] == "FAIL":
        report["recommendations"].append({
            "priority": "critical",
            "action": "必须修复代码使其严格遵循方案，不允许偏离用户确认的方案",
            "trigger": "block_and_retry"
        })
    elif report["overall_status"] == "WARNING":
        report["recommendations"].append({
            "priority": "high",
            "action": "建议增强引用标记，提高可追溯性",
            "trigger": "可继续但需要注意"
        })
    else:
        report["recommendations"].append({
            "priority": "low",
            "action": "所有检查通过，代码与方案一致",
            "trigger": "继续流程"
        })

    print("━━━━━━━━━━━━━━━━━━━━━━━━")
    print("代码-方案一致性检查报告")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"总体状态: {report['overall_status']}")
    print(f"通过检查: {report['summary']['passed_checks']}/{report['summary']['total_checks']}")
    print(f"发现问题: {report['summary']['failed_checks']}个")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")

    return report
```

## 输出

```yaml
outputs:
  consistency_check_result:
    type: object
    description: 一致性检查结果
    structure:
      metadata: 元数据
      overall_status: string (PASS/WARNING/FAIL)
      checks: object (各项检查结果)
      summary: object (统计信息)
      issues_found: array (发现的问题列表)
      inconsistencies: array (不一致项详情)
      recommendations: array (建议)

  inconsistencies_found:
    type: array
    description: 不一致项列表（用于workflow error_message）
```

## 质量门禁

```yaml
verification_gate:
  critical: true
  check: "consistency_check_result.overall_status == 'PASS'"
  on_fail: 'block_and_retry'
  max_retries: 3

  error_handling:
    FAIL:
      action: '阻断workflow，必须修复'
      message: '代码与方案存在严重不一致'
    WARNING:
      action: '可选继续，但建议修复'
      message: '代码与方案存在部分不一致'
    PASS:
      action: '继续流程'
      message: '代码与方案完全一致'
```

## 质量检查

- [ ] 文件头部引用标记完整
- [ ] 算法与方案一致（算法名称匹配）
- [ ] 参数与方案一致（所有参数值匹配）
- [ ] 约束策略与方案一致（repair/penalty方法存在）
- [ ] 目标函数与方案一致（weighted_sum方法存在）
- [ ] Section引用 >= 5处
- [ ] 专家库引用 >= 3处
- [ ] 包含状态文件引用
- [ ] 标明了专家库来源（不是AI生成）

## 引用

- @质量评测专家库/验证标准
- @编排协调专家库/一致性检查方法

---

**创建**: 2025-10-24
**最后更新**: 2025-11-03 (V4.4.1)
**BMAD版本**: v6-alpha
**核心机制**: Workflow级别强制验证，确保代码与方案一致，避免大模型幻觉

## 版本历史

### V4.4.1 (2025-11-03) - 专家库引用验证增强

**问题**: 缺少对代码中专家库引用完整性的强制验证

**修复内容**:

1. ✅ 新增 `verify_expert_library_citations()` 函数（步骤1.5）
   - 验证专家库引用数量（要求 >= 3处）
   - 验证专家库类型覆盖（要求 >= 2个不同专家库）
   - 验证引用格式正确性（@xxx库/yyy/zzz.md）
   - 提供详细的验证报告和错误提示

2. ✅ 补充现有 `verify_expert_library_usage()` 函数（步骤7）
   - 原功能：验证方案中的引用是否出现在代码中
   - 新功能：补充验证代码引用的总体完整性

3. ✅ 更新质量检查清单
   - 明确了"专家库引用 >= 3处"的要求
   - 与generate-code-from-solution.md的要求保持一致

**方案依据**:

- @bmad/aps/tasks/generate-code-from-solution.md Line 86-114 (引用标记要求)
- 与代码生成任务的引用检查逻辑保持一致

**符合BMAD规范**:

- ✅ 添加了版本标注（V4.4.1）
- ✅ 添加了详细的验证逻辑和错误提示
- ✅ 与代码生成任务形成完整的生成-验证闭环
- ✅ 保持了Workflow级别强制验证机制

### V4.3 (2025-10-24) - 初始版本

- 实现基础的代码-方案一致性验证
- 包含算法、参数、约束、目标的一致性检查
- 建立Workflow级别强制验证机制
