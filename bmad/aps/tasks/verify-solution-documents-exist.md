# Task: Verify Solution Documents Exist

**任务ID**: `verify-solution-documents-exist`
**版本**: V4.3
**用途**: Phase 3 Step 3.4.5 - 代码生成前的最后一道防线，确保方案文档完整存在

---

## 🛡️ 任务目的

在进入代码生成阶段（Step 3.5）之前，执行**最后的终极验证**，确保方案文档已经完整生成并符合所有要求。

这是一个**阻断级检查点**，如果验证失败，workflow必须停止，不允许进入代码生成阶段。

---

## 输入

```yaml
inputs:
  - solution_document_path: 方案文档路径（来自Step 3.3）
  - solution_data_path: 方案数据路径（来自Step 3.3）
  - output_folder: 输出目录路径
```

---

## 处理逻辑

### 步骤1: 验证Markdown方案文档

```python
import os

def verify_markdown_document(solution_document_path):
    """
    验证Markdown方案文档的存在性和完整性

    Returns:
        dict: 验证结果
    """
    result = {
        "markdown_exists": False,
        "markdown_path": solution_document_path,
        "markdown_size": 0,
        "filename_valid": False,
        "has_all_sections": False,
        "missing_sections": [],
        "issues": []
    }

    # 检查1: 文件存在
    if not os.path.exists(solution_document_path):
        result["issues"].append(f"❌ 方案文档不存在: {solution_document_path}")
        return result

    result["markdown_exists"] = True
    result["markdown_size"] = os.path.getsize(solution_document_path)

    # 检查2: 文件名格式
    filename = os.path.basename(solution_document_path)
    if not filename.startswith("solution_document_"):
        result["issues"].append(
            f"❌ 文件名格式错误: {filename} (应为 solution_document_{{timestamp}}.md)"
        )
        return result

    result["filename_valid"] = True

    # 检查3: 读取文件内容
    try:
        with open(solution_document_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result["issues"].append(f"❌ 无法读取文件: {e}")
        return result

    # 检查4: 内容结构完整性
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
        result["missing_sections"] = missing_sections
        result["issues"].append(
            f"❌ 缺少必需章节: {', '.join(missing_sections)}"
        )
        result["issues"].append(
            "提示: 方案文档必须包含6个技术章节和1个附录，不是简单的用户手册"
        )
        return result

    result["has_all_sections"] = True

    return result
```

### 步骤2: 验证YAML方案数据

```python
def verify_yaml_data(solution_data_path):
    """
    验证YAML方案数据的存在性和可解析性

    Returns:
        dict: 验证结果
    """
    result = {
        "yaml_exists": False,
        "yaml_path": solution_data_path,
        "yaml_size": 0,
        "yaml_parseable": False,
        "has_required_keys": False,
        "issues": []
    }

    # 检查1: 文件存在
    if not os.path.exists(solution_data_path):
        result["issues"].append(f"❌ 方案数据文件不存在: {solution_data_path}")
        return result

    result["yaml_exists"] = True
    result["yaml_size"] = os.path.getsize(solution_data_path)

    # 检查2: YAML可解析
    try:
        import yaml
        with open(solution_data_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        result["yaml_parseable"] = True
    except Exception as e:
        result["issues"].append(f"❌ YAML文件解析失败: {e}")
        return result

    # 检查3: 包含必需的键
    required_keys = [
        "solution_metadata",
        "solution_sections",
        "ten_element_model"
    ]

    missing_keys = []
    for key in required_keys:
        if key not in data:
            missing_keys.append(key)

    if missing_keys:
        result["issues"].append(
            f"❌ YAML数据缺少必需键: {', '.join(missing_keys)}"
        )
        return result

    result["has_required_keys"] = True

    return result
```

### 步骤3: 生成终极验证报告

```python
def generate_final_verification(markdown_result, yaml_result):
    """
    生成终极验证报告

    Returns:
        dict: 终极验证结果
    """
    final_verification = {
        "overall_status": "PASS" if (
            markdown_result["has_all_sections"] and
            yaml_result["has_required_keys"]
        ) else "FAIL",

        "markdown_verification": markdown_result,
        "yaml_verification": yaml_result,

        "all_checks_passed": (
            markdown_result["markdown_exists"] and
            markdown_result["filename_valid"] and
            markdown_result["has_all_sections"] and
            yaml_result["yaml_exists"] and
            yaml_result["yaml_parseable"] and
            yaml_result["has_required_keys"]
        ),

        "summary": {
            "markdown_exists": markdown_result["markdown_exists"],
            "markdown_size": markdown_result["markdown_size"],
            "yaml_exists": yaml_result["yaml_exists"],
            "yaml_size": yaml_result["yaml_size"],
            "has_all_sections": markdown_result["has_all_sections"],
            "missing_sections": markdown_result["missing_sections"]
        },

        "blocking_issues": []
    }

    # 收集所有阻断问题
    if markdown_result["issues"]:
        final_verification["blocking_issues"].extend(markdown_result["issues"])

    if yaml_result["issues"]:
        final_verification["blocking_issues"].extend(yaml_result["issues"])

    return final_verification
```

---

## 输出

```yaml
outputs:
  final_verification:
    type: object
    description: 终极验证结果
    structure:
      overall_status: string # "PASS" 或 "FAIL"
      all_checks_passed: boolean

      markdown_verification:
        markdown_exists: boolean
        markdown_size: integer
        filename_valid: boolean
        has_all_sections: boolean
        missing_sections: array
        issues: array

      yaml_verification:
        yaml_exists: boolean
        yaml_size: integer
        yaml_parseable: boolean
        has_required_keys: boolean
        issues: array

      summary:
        markdown_exists: boolean
        markdown_size: integer
        yaml_exists: boolean
        yaml_size: integer
        has_all_sections: boolean
        missing_sections: array

      blocking_issues: array # 所有阻断性问题的列表
```

---

## 验证门禁（Verification Gate）

此任务的结果将触发workflow的验证门禁：

```yaml
verification_gate:
  critical: true
  checks:
    - 'final_verification.markdown_exists == true'
    - 'final_verification.yaml_exists == true'
    - 'final_verification.has_all_sections == true'
    - 'final_verification.all_checks_passed == true'
  on_fail: 'block_with_error'
  error_message: |
    ❌ 方案文档验证失败，无法进入代码生成阶段！

    请确保以下文件存在且完整：
    1. solution_document_*.md (包含6个技术章节 + 附录)
    2. solution_data_*.yaml (包含完整方案对象)

    阻断问题:
    ${final_verification.blocking_issues}
```

---

## 失败处理

### 如果验证失败

1. **阻断流程**: workflow必须停止在此步骤
2. **显示错误**: 清晰显示所有阻断性问题
3. **指导修复**: 提示用户检查Step 3.3的执行情况
4. **不允许跳过**: 这是强制性检查，不能绕过

### 错误消息示例

```
❌ 方案文档验证失败！

阻断问题:
1. ❌ 方案文档文件名格式错误: README.md (应为 solution_document_{timestamp}.md)
2. ❌ 缺少必需章节: ## 5. 算法选择与配置, ## 6. 实现路线图

说明:
- 方案文档不是用户手册(README.md)
- 必须包含完整的6个技术章节和附录
- 请检查 Step 3.3 是否正确执行

解决方案:
- 重新执行 Step 3.3 (保存方案交付物)
- 或从 Phase 3 重新开始
```

---

## 质量检查

- [ ] 验证逻辑覆盖所有关键检查点
- [ ] 错误消息清晰且可操作
- [ ] 验证门禁配置正确
- [ ] 阻断机制有效
- [ ] 不允许绕过检查

---

## 引用

- @编排协调专家库/质量门禁规范
- @工作流管理/验证检查点最佳实践

---

**创建**: 2025-10-27
**BMAD版本**: v6-alpha
**核心机制**: 代码生成前的最后防线，强制验证方案文档完整性
