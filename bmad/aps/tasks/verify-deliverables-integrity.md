# Task: Verify Deliverables Integrity

**任务ID**: `verify-deliverables-integrity`
**版本**: V4.3
**用途**: Phase 3 Step 3.7 - 验证所有交付物已保存且格式正确

## 输入

```yaml
inputs:
  - saved_files: 保存的文件路径清单
  - deliverable_manifest: 交付物清单
  - output_folder: 输出目录路径
```

## 🚨 强制要求（MANDATORY）

### 1. 必须验证所有交付物

本任务是Phase 3的最后一道质量门禁，必须验证：

```yaml
validation_checklist:
  file_existence:
    - 所有文件必须存在
    - 文件路径必须正确

  file_size:
    - 所有文件大小必须 >= 最小阈值

  file_format:
    - Python代码语法正确
    - YAML格式正确
    - Markdown格式正确
    - JSON格式正确

  content_integrity:
    - 代码包含方案引用
    - TenElementModel完整
    - 可追溯性映射完整
```

### 2. 验证失败必须阻断

如果任何验证失败，必须：

- 抛出异常
- 阻断workflow
- 提供详细的错误信息和修复建议

## 处理逻辑

### 步骤1: 验证文件存在性

```python
import os
from pathlib import Path

def verify_files_existence(saved_files):
    """
    验证所有文件是否存在

    Returns:
        dict: 验证结果
    """
    existence_check = {
        "all_exist": True,
        "missing_files": [],
        "existing_files": []
    }

    for file_type, file_path in saved_files.items():
        if file_path is None:  # README可能为None
            continue

        if os.path.exists(file_path):
            existence_check["existing_files"].append({
                "type": file_type,
                "path": file_path
            })
            print(f"✓ 文件存在: {file_path}")
        else:
            existence_check["all_exist"] = False
            existence_check["missing_files"].append({
                "type": file_type,
                "path": file_path
            })
            print(f"✗ 文件缺失: {file_path}")

    if not existence_check["all_exist"]:
        raise FileNotFoundError(
            f"以下文件缺失: {existence_check['missing_files']}"
        )

    print(f"✓ 文件存在性验证通过: {len(existence_check['existing_files'])}个文件")
    return existence_check
```

### 步骤2: 验证文件大小

```python
def verify_files_size(saved_files):
    """
    验证所有文件大小是否符合要求

    Returns:
        dict: 验证结果
    """
    min_sizes = {
        "complete_code": 2048,
        "ten_element_model_export": 1024,
        "code_traceability": 512,
        "code_documentation": 1024,
        "deliverable_manifest": 256,
        "readme": 512,
        "solution_document_path": 5120
    }

    size_check = {
        "all_valid": True,
        "invalid_files": [],
        "valid_files": []
    }

    for file_type, file_path in saved_files.items():
        if file_path is None:
            continue

        min_size = min_sizes.get(file_type, 100)
        actual_size = os.path.getsize(file_path)

        if actual_size < min_size:
            size_check["all_valid"] = False
            size_check["invalid_files"].append({
                "type": file_type,
                "path": file_path,
                "actual_size": actual_size,
                "min_size": min_size,
                "issue": f"文件太小: {actual_size} < {min_size} bytes"
            })
            print(f"✗ 文件太小: {file_path} ({actual_size} < {min_size} bytes)")
        else:
            size_check["valid_files"].append({
                "type": file_type,
                "path": file_path,
                "size": actual_size
            })
            print(f"✓ 文件大小OK: {file_path} ({actual_size} bytes)")

    if not size_check["all_valid"]:
        raise ValueError(
            f"以下文件大小不符合要求: {size_check['invalid_files']}"
        )

    print(f"✓ 文件大小验证通过")
    return size_check
```

### 步骤3: 验证文件格式

```python
def verify_file_formats(saved_files):
    """
    验证所有文件格式是否正确

    Returns:
        dict: 验证结果
    """
    format_check = {
        "all_valid": True,
        "invalid_files": [],
        "valid_files": []
    }

    # 验证Python文件
    if "complete_code" in saved_files and saved_files["complete_code"]:
        try:
            with open(saved_files["complete_code"], 'r', encoding='utf-8') as f:
                code_content = f.read()

            # 简单的语法检查
            import ast
            ast.parse(code_content)

            format_check["valid_files"].append({
                "type": "complete_code",
                "format": "Python",
                "status": "OK"
            })
            print(f"✓ Python代码格式正确")
        except SyntaxError as e:
            format_check["all_valid"] = False
            format_check["invalid_files"].append({
                "type": "complete_code",
                "format": "Python",
                "issue": f"语法错误: {e}"
            })
            print(f"✗ Python代码语法错误: {e}")

    # 验证YAML文件
    yaml_files = ["ten_element_model_export", "code_traceability"]
    for file_type in yaml_files:
        if file_type in saved_files and saved_files[file_type]:
            try:
                import yaml
                with open(saved_files[file_type], 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)

                format_check["valid_files"].append({
                    "type": file_type,
                    "format": "YAML",
                    "status": "OK"
                })
                print(f"✓ YAML格式正确: {file_type}")
            except yaml.YAMLError as e:
                format_check["all_valid"] = False
                format_check["invalid_files"].append({
                    "type": file_type,
                    "format": "YAML",
                    "issue": f"YAML格式错误: {e}"
                })
                print(f"✗ YAML格式错误: {file_type} - {e}")

    # 验证JSON文件
    if "deliverable_manifest" in saved_files and saved_files["deliverable_manifest"]:
        try:
            import json
            with open(saved_files["deliverable_manifest"], 'r', encoding='utf-8') as f:
                json.load(f)

            format_check["valid_files"].append({
                "type": "deliverable_manifest",
                "format": "JSON",
                "status": "OK"
            })
            print(f"✓ JSON格式正确")
        except json.JSONDecodeError as e:
            format_check["all_valid"] = False
            format_check["invalid_files"].append({
                "type": "deliverable_manifest",
                "format": "JSON",
                "issue": f"JSON格式错误: {e}"
            })
            print(f"✗ JSON格式错误: {e}")

    # 验证Markdown文件
    md_files = ["code_documentation", "solution_document_path", "readme"]
    for file_type in md_files:
        if file_type in saved_files and saved_files[file_type]:
            try:
                with open(saved_files[file_type], 'r', encoding='utf-8') as f:
                    md_content = f.read()

                # 简单检查是否包含Markdown标记
                if "#" in md_content or "**" in md_content or "-" in md_content:
                    format_check["valid_files"].append({
                        "type": file_type,
                        "format": "Markdown",
                        "status": "OK"
                    })
                    print(f"✓ Markdown格式正确: {file_type}")
                else:
                    format_check["all_valid"] = False
                    format_check["invalid_files"].append({
                        "type": file_type,
                        "format": "Markdown",
                        "issue": "文件不包含Markdown标记"
                    })
            except Exception as e:
                format_check["all_valid"] = False
                format_check["invalid_files"].append({
                    "type": file_type,
                    "format": "Markdown",
                    "issue": f"读取失败: {e}"
                })

    if not format_check["all_valid"]:
        raise ValueError(
            f"以下文件格式不正确: {format_check['invalid_files']}"
        )

    print(f"✓ 文件格式验证通过")
    return format_check
```

### 步骤4: 验证内容完整性

```python
def verify_content_integrity(saved_files, deliverable_manifest):
    """
    验证文件内容的完整性

    Returns:
        dict: 验证结果
    """
    integrity_check = {
        "all_valid": True,
        "issues": [],
        "validations": []
    }

    # 验证代码包含方案引用
    if "complete_code" in saved_files and saved_files["complete_code"]:
        with open(saved_files["complete_code"], 'r', encoding='utf-8') as f:
            code_content = f.read()

        # 检查是否包含方案引用
        if "方案依据" in code_content or "solution_document" in code_content:
            integrity_check["validations"].append({
                "item": "代码方案引用",
                "status": "OK"
            })
            print("✓ 代码包含方案引用")
        else:
            integrity_check["all_valid"] = False
            integrity_check["issues"].append({
                "item": "代码方案引用",
                "issue": "代码中未找到方案引用标注"
            })
            print("✗ 代码中未找到方案引用")

    # 验证TenElementModel包含10个要素
    if "ten_element_model_export" in saved_files and saved_files["ten_element_model_export"]:
        import yaml
        with open(saved_files["ten_element_model_export"], 'r', encoding='utf-8') as f:
            ten_element_model = yaml.safe_load(f)

        # 检查是否包含关键要素
        required_elements = [
            "decision_variables",
            "parameters",
            "constraints",
            "objectives"
        ]

        missing_elements = []
        for element in required_elements:
            if element not in ten_element_model or not ten_element_model[element]:
                missing_elements.append(element)

        if not missing_elements:
            integrity_check["validations"].append({
                "item": "TenElementModel完整性",
                "status": "OK"
            })
            print("✓ TenElementModel包含所有必需要素")
        else:
            integrity_check["all_valid"] = False
            integrity_check["issues"].append({
                "item": "TenElementModel完整性",
                "issue": f"缺少要素: {missing_elements}"
            })
            print(f"✗ TenElementModel缺少要素: {missing_elements}")

    # 验证可追溯性映射完整
    if "code_traceability" in saved_files and saved_files["code_traceability"]:
        import yaml
        with open(saved_files["code_traceability"], 'r', encoding='utf-8') as f:
            traceability = yaml.safe_load(f)

        # 检查是否包含必需的映射
        if "mappings" in traceability and traceability["mappings"]:
            integrity_check["validations"].append({
                "item": "代码可追溯性",
                "status": "OK"
            })
            print("✓ 代码可追溯性映射完整")
        else:
            integrity_check["all_valid"] = False
            integrity_check["issues"].append({
                "item": "代码可追溯性",
                "issue": "可追溯性映射缺失或为空"
            })
            print("✗ 可追溯性映射不完整")

    # 验证交付物清单与实际文件一致
    import json
    if "deliverable_manifest" in saved_files and saved_files["deliverable_manifest"]:
        with open(saved_files["deliverable_manifest"], 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        # 检查清单中列出的文件是否都存在
        manifest_files_exist = True
        for deliverable_name, deliverable_info in manifest.get("deliverables", {}).items():
            file_path = deliverable_info.get("file_path", "")
            if file_path and not os.path.exists(file_path):
                manifest_files_exist = False
                integrity_check["issues"].append({
                    "item": "交付物清单一致性",
                    "issue": f"清单中的文件不存在: {file_path}"
                })

        if manifest_files_exist:
            integrity_check["validations"].append({
                "item": "交付物清单一致性",
                "status": "OK"
            })
            print("✓ 交付物清单与实际文件一致")
        else:
            integrity_check["all_valid"] = False

    if not integrity_check["all_valid"]:
        raise ValueError(
            f"内容完整性验证失败: {integrity_check['issues']}"
        )

    print(f"✓ 内容完整性验证通过")
    return integrity_check
```

### 步骤5: 生成完整性验证报告

```python
from datetime import datetime

def generate_integrity_report(
    existence_check,
    size_check,
    format_check,
    integrity_check,
    saved_files
):
    """
    生成完整的完整性验证报告

    Returns:
        dict: 完整性报告
    """
    report = {
        "version": "1.0",
        "verified_at": datetime.now().isoformat(),
        "overall_status": "PASS",

        "summary": {
            "total_files": len([f for f in saved_files.values() if f is not None]),
            "all_checks_passed": True
        },

        "checks": {
            "file_existence": {
                "status": "PASS" if existence_check["all_exist"] else "FAIL",
                "existing_files": len(existence_check["existing_files"]),
                "missing_files": len(existence_check["missing_files"])
            },
            "file_size": {
                "status": "PASS" if size_check["all_valid"] else "FAIL",
                "valid_files": len(size_check["valid_files"]),
                "invalid_files": len(size_check["invalid_files"])
            },
            "file_format": {
                "status": "PASS" if format_check["all_valid"] else "FAIL",
                "valid_files": len(format_check["valid_files"]),
                "invalid_files": len(format_check["invalid_files"])
            },
            "content_integrity": {
                "status": "PASS" if integrity_check["all_valid"] else "FAIL",
                "validations": len(integrity_check["validations"]),
                "issues": len(integrity_check["issues"])
            }
        },

        "issues_found": [],
        "recommendations": []
    }

    # 汇总问题
    all_checks_passed = (
        existence_check["all_exist"] and
        size_check["all_valid"] and
        format_check["all_valid"] and
        integrity_check["all_valid"]
    )

    if not all_checks_passed:
        report["overall_status"] = "FAIL"
        report["summary"]["all_checks_passed"] = False

        # 收集所有问题
        if existence_check["missing_files"]:
            report["issues_found"].extend(existence_check["missing_files"])
        if size_check["invalid_files"]:
            report["issues_found"].extend(size_check["invalid_files"])
        if format_check["invalid_files"]:
            report["issues_found"].extend(format_check["invalid_files"])
        if integrity_check["issues"]:
            report["issues_found"].extend(integrity_check["issues"])

        # 生成修复建议
        report["recommendations"].append("请检查上述问题并修复")
        report["recommendations"].append("建议从Step 3.6重新执行保存交付物流程")
    else:
        report["recommendations"].append("所有验证通过，交付物完整且正确")

    return report
```

## 输出

```yaml
outputs:
  integrity_check_result:
    type: object
    description: 完整性检查结果
    structure:
      version: string
      verified_at: string (ISO8601)
      overall_status: string (PASS/FAIL)
      summary:
        total_files: integer
        all_checks_passed: boolean
      checks:
        file_existence: object
        file_size: object
        file_format: object
        content_integrity: object
      issues_found: array
      recommendations: array

  issues_found:
    type: array
    description: 发现的问题列表
```

## 质量门禁

本任务是Phase 3的关键质量门禁：

```yaml
verification_gate:
  critical: true
  check: 'integrity_check_result.all_valid == true'
  on_fail: 'block_delivery'
  error_message: '交付物完整性验证失败，无法交付'
```

如果验证失败：

- workflow必须阻断
- 不允许进入Phase 4
- 必须修复问题后重新验证

## 质量检查

- [ ] 所有文件存在
- [ ] 所有文件大小符合要求
- [ ] Python代码语法正确
- [ ] YAML格式正确
- [ ] JSON格式正确
- [ ] Markdown格式正确
- [ ] 代码包含方案引用
- [ ] TenElementModel完整
- [ ] 可追溯性映射完整
- [ ] 交付物清单一致

## 引用

- @质量评测专家库/验证标准
- @编排协调专家库/质量门禁规范

---

**创建**: 2025-10-24
**BMAD版本**: v6-alpha
**核心机制**: 交付物完整性验证，Phase 3质量门禁
