# Task: Verify Deliverables Saved

**任务ID**: `verify-deliverables-saved`
**版本**: V4.3
**用途**: Phase 4 - 验证所有交付物已保存到输出目录（质量门禁6前置检查）

## 输入

```yaml
inputs:
  - saved_files: Phase 3生成并保存的文件路径清单
  - output_folder: 输出目录路径（从config.yaml加载）
  - deliverable_manifest: 文件清单元数据
```

## 验证标准

### 1. 必需交付物清单

```yaml
required_deliverables:
  ten_element_model:
    file_pattern: 'ten_element_model_*.yaml'
    location: '{output_folder}/models/'
    min_size: 1024 # bytes
    description: '十要素模型YAML导出'
    critical: true

  complete_code:
    file_pattern: 'scheduling_solution_*.py'
    location: '{output_folder}/models/'
    min_size: 2048
    description: '完整可执行代码'
    critical: true

  code_documentation:
    file_pattern: 'solution_documentation_*.md'
    location: '{output_folder}/docs/'
    min_size: 512
    description: '代码使用文档'
    critical: true

  readme:
    file_pattern: 'README.md'
    location: '{output_folder}/'
    min_size: 256
    description: '项目README'
    critical: false

  file_manifest:
    file_pattern: 'file_manifest_*.json'
    location: '{output_folder}/'
    min_size: 128
    description: '文件清单元数据'
    critical: false
```

### 2. 可选交付物（如已生成则需验证）

```yaml
optional_deliverables:
  quality_report:
    file_pattern: 'quality_report_*.json'
    location: '{output_folder}/reports/'
    min_size: 256

  todo_completion_report:
    file_pattern: 'todo_completion_*.json'
    location: '{output_folder}/reports/'
    min_size: 128

  benchmark_results:
    file_pattern: 'benchmark_*.json'
    location: '{output_folder}/reports/'
    min_size: 128
```

## 处理逻辑

### 步骤1: 检查输出目录结构

```python
import os
from pathlib import Path

def verify_directory_structure(output_folder):
    """
    验证输出目录结构完整性
    """
    required_dirs = ["models", "docs", "reports"]
    base_path = Path(output_folder)

    structure_check = {
        "base_exists": base_path.exists(),
        "subdirs": {}
    }

    for subdir in required_dirs:
        dir_path = base_path / subdir
        structure_check["subdirs"][subdir] = {
            "exists": dir_path.exists(),
            "is_directory": dir_path.is_dir() if dir_path.exists() else False,
            "writable": os.access(str(dir_path), os.W_OK) if dir_path.exists() else False
        }

    return structure_check
```

### 步骤2: 逐个验证交付物

```python
import glob

def verify_deliverable(deliverable_config, output_folder):
    """
    验证单个交付物

    Args:
        deliverable_config: 交付物配置
        output_folder: 输出目录

    Returns:
        dict: 验证结果
    """
    file_pattern = deliverable_config["file_pattern"]
    location = deliverable_config["location"].format(output_folder=output_folder)
    min_size = deliverable_config["min_size"]

    # 搜索匹配的文件
    search_pattern = os.path.join(location, file_pattern)
    matching_files = glob.glob(search_pattern)

    if not matching_files:
        return {
            "found": False,
            "valid": False,
            "message": f"未找到文件: {search_pattern}",
            "matched_files": []
        }

    # 验证第一个匹配文件（通常按时间戳排序后的最新文件）
    file_path = sorted(matching_files)[-1]  # 最新文件

    # 检查文件大小
    file_size = os.path.getsize(file_path)
    if file_size < min_size:
        return {
            "found": True,
            "valid": False,
            "message": f"文件过小: {file_size} bytes < {min_size} bytes",
            "file_path": file_path,
            "file_size": file_size
        }

    # 检查文件可读性
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            _ = f.read(10)  # 读取前10个字符
    except Exception as e:
        return {
            "found": True,
            "valid": False,
            "message": f"文件不可读: {str(e)}",
            "file_path": file_path
        }

    return {
        "found": True,
        "valid": True,
        "message": "验证通过",
        "file_path": file_path,
        "file_size": file_size
    }
```

### 步骤3: 聚合验证结果

```python
def verify_all_deliverables(required_deliverables, optional_deliverables, output_folder):
    """
    验证所有交付物

    Returns:
        dict: 聚合验证结果
    """
    results = {
        "all_required_valid": True,
        "required_results": {},
        "optional_results": {},
        "summary": {
            "total_required": len(required_deliverables),
            "required_passed": 0,
            "required_failed": 0,
            "total_optional": len(optional_deliverables),
            "optional_passed": 0
        }
    }

    # 验证必需交付物
    for name, config in required_deliverables.items():
        result = verify_deliverable(config, output_folder)
        results["required_results"][name] = result

        if result["valid"]:
            results["summary"]["required_passed"] += 1
        else:
            results["summary"]["required_failed"] += 1
            results["all_required_valid"] = False

    # 验证可选交付物
    for name, config in optional_deliverables.items():
        result = verify_deliverable(config, output_folder)
        results["optional_results"][name] = result

        if result["valid"]:
            results["summary"]["optional_passed"] += 1

    return results
```

### 步骤4: 生成验证报告

```python
def generate_verification_report(verification_results):
    """
    生成易读的验证报告
    """
    report = []

    report.append("=" * 60)
    report.append("交付物验证报告")
    report.append("=" * 60)
    report.append("")

    # 必需交付物
    report.append("## 必需交付物")
    report.append("")
    for name, result in verification_results["required_results"].items():
        status = "✓" if result["valid"] else "✗"
        report.append(f"{status} {name}")
        if result["valid"]:
            report.append(f"   路径: {result['file_path']}")
            report.append(f"   大小: {result['file_size']} bytes")
        else:
            report.append(f"   {result['message']}")
        report.append("")

    # 可选交付物
    if verification_results["optional_results"]:
        report.append("## 可选交付物")
        report.append("")
        for name, result in verification_results["optional_results"].items():
            status = "✓" if result["valid"] else "-"
            report.append(f"{status} {name}")
            if result["valid"]:
                report.append(f"   路径: {result['file_path']}")
            report.append("")

    # 汇总
    summary = verification_results["summary"]
    report.append("=" * 60)
    report.append("验证汇总")
    report.append("=" * 60)
    report.append(f"必需交付物: {summary['required_passed']}/{summary['total_required']} 通过")
    if summary["required_failed"] > 0:
        report.append(f"失败项: {summary['required_failed']}")
    report.append(f"可选交付物: {summary['optional_passed']}/{summary['total_optional']} 已保存")
    report.append("")

    # 最终结论
    if verification_results["all_required_valid"]:
        report.append("✓ 所有必需交付物验证通过，可以进入质量门禁")
    else:
        report.append("✗ 存在未通过的必需交付物，阻断质量门禁")
        report.append("   请运行 generate-complete-code 任务重新生成并保存文件")

    report.append("=" * 60)

    return "\n".join(report)
```

## 输出

```yaml
outputs:
  verification_results:
    type: object
    required: true
    structure:
      all_required_valid: boolean
      required_results: object
      optional_results: object
      summary: object

  verification_report:
    type: string
    description: '易读的验证报告文本'

  deliverable_check:
    type: object
    description: '供质量门禁6使用的验证数据'
    structure:
      all_saved: boolean
      all_paths_accessible: boolean
      completeness: boolean
      naming_compliant: boolean
      file_list: array
```

## 示例输出

```json
{
  "verification_results": {
    "all_required_valid": true,
    "required_results": {
      "ten_element_model": {
        "found": true,
        "valid": true,
        "message": "验证通过",
        "file_path": "aps-outputs/models/ten_element_model_20251021_143022.yaml",
        "file_size": 3256
      },
      "complete_code": {
        "found": true,
        "valid": true,
        "message": "验证通过",
        "file_path": "aps-outputs/models/scheduling_solution_20251021_143022.py",
        "file_size": 8432
      }
    },
    "summary": {
      "total_required": 3,
      "required_passed": 3,
      "required_failed": 0,
      "total_optional": 2,
      "optional_passed": 1
    }
  },
  "deliverable_check": {
    "all_saved": true,
    "all_paths_accessible": true,
    "completeness": true,
    "naming_compliant": true,
    "file_list": [
      "aps-outputs/models/ten_element_model_20251021_143022.yaml",
      "aps-outputs/models/scheduling_solution_20251021_143022.py",
      "aps-outputs/docs/solution_documentation_20251021_143022.md"
    ]
  }
}
```

## 质量检查

- [ ] 所有必需交付物已验证
- [ ] 文件路径真实存在
- [ ] 文件大小符合最小要求
- [ ] 文件可读性已检查
- [ ] 验证报告清晰易读
- [ ] deliverable_check数据格式正确

## 引用

- @质量评测专家库/交付物验证标准
- @输出管理规范/文件保存要求
- V4.3架构规范: 质量门禁6前置验证

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: 交付物持久化验证，质量门禁6的前置条件
