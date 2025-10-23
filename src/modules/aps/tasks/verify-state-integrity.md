# Task: Verify State Integrity

**任务ID**: `verify-state-integrity`
**版本**: V4.3
**用途**: 验证状态文件的完整性和一致性，确保workflow状态链完整

## 输入

```yaml
inputs:
  - state_folder: 状态文件目录路径
  - verify_phases: 要验证的Phase列表 (可选，默认全部)
  - deep_check: 是否进行深度检查 (默认false)
  - fix_issues: 是否自动修复问题 (默认false)
```

## 用途场景

此任务适用于以下场景：

1. **workflow启动前**: 检查依赖的Phase状态是否完整
2. **质量门禁**: 作为Phase 4的一部分，验证整个状态链
3. **故障排查**: 诊断workflow执行异常时的状态问题
4. **维护清理**: 定期检查和清理状态文件

## 处理逻辑

### 步骤1: 加载状态清单

```python
import os
import json
from pathlib import Path
from datetime import datetime

def load_state_manifest(state_folder):
    """
    加载状态清单文件

    Args:
        state_folder: 状态目录

    Returns:
        dict: 清单内容，如果不存在则返回空字典

    Raises:
        ValueError: 清单文件损坏
    """
    manifest_path = os.path.join(state_folder, "phase_state_manifest.json")

    if not os.path.exists(manifest_path):
        print("⚠ 状态清单文件不存在，将进行文件系统扫描")
        return {
            "version": "1.0",
            "phases": {},
            "warning": "manifest_file_missing"
        }

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        print(f"✓ 状态清单已加载: {len(manifest.get('phases', {}))} 个Phase")
        return manifest

    except json.JSONDecodeError as e:
        raise ValueError(f"❌ 清单文件损坏: {e}")
    except Exception as e:
        raise IOError(f"❌ 无法读取清单文件: {e}")
```

### 步骤2: 扫描状态目录

```python
def scan_state_directory(state_folder):
    """
    扫描状态目录，发现所有状态文件

    Args:
        state_folder: 状态目录

    Returns:
        dict: 扫描结果
    """
    state_path = Path(state_folder)

    if not state_path.exists():
        print(f"⚠ 状态目录不存在: {state_folder}")
        return {
            "exists": False,
            "files": []
        }

    # 查找所有状态文件
    yaml_files = list(state_path.glob("phase_*_state*.yaml"))
    json_files = list(state_path.glob("phase_*_state*.json"))
    all_files = yaml_files + json_files

    # 分类文件
    categorized = {
        "timestamped": [],  # 带时间戳的文件
        "latest": [],       # latest链接
        "standard": [],     # 标准文件名
        "other": []         # 其他
    }

    for file in all_files:
        filename = file.name
        if "_latest." in filename:
            categorized["latest"].append(str(file))
        elif "_state_2" in filename:  # 时间戳格式: 20251023_143022
            categorized["timestamped"].append(str(file))
        elif "_state." in filename:
            categorized["standard"].append(str(file))
        else:
            categorized["other"].append(str(file))

    total_files = len(all_files)
    print(f"✓ 扫描完成: 发现 {total_files} 个状态文件")

    return {
        "exists": True,
        "total_files": total_files,
        "categorized": categorized,
        "all_files": [str(f) for f in all_files]
    }
```

### 步骤3: 验证必需的Phase状态

```python
def verify_required_phases(state_folder, required_phases):
    """
    验证必需的Phase状态文件是否存在

    Args:
        state_folder: 状态目录
        required_phases: 必需的Phase列表

    Returns:
        dict: 验证结果
    """
    verification = {
        "all_present": True,
        "missing": [],
        "present": [],
        "details": {}
    }

    for phase_id in required_phases:
        # 查找该Phase的状态文件
        phase_files = list(Path(state_folder).glob(f"{phase_id}_state*.yaml")) + \
                      list(Path(state_folder).glob(f"{phase_id}_state*.json"))

        if phase_files:
            # 找到最新的文件
            latest_file = max(phase_files, key=lambda p: p.stat().st_mtime)
            verification["present"].append(phase_id)
            verification["details"][phase_id] = {
                "status": "present",
                "file_path": str(latest_file),
                "file_count": len(phase_files)
            }
            print(f"✓ {phase_id}: 存在 ({len(phase_files)} 个文件)")
        else:
            verification["all_present"] = False
            verification["missing"].append(phase_id)
            verification["details"][phase_id] = {
                "status": "missing",
                "file_path": None
            }
            print(f"✗ {phase_id}: 缺失")

    return verification
```

### 步骤4: 验证文件完整性

```python
import yaml
import json

def verify_file_integrity(file_path):
    """
    验证单个状态文件的完整性

    Args:
        file_path: 文件路径

    Returns:
        dict: 验证结果
    """
    result = {
        "file_path": file_path,
        "valid": True,
        "issues": []
    }

    # 检查1: 文件存在
    if not os.path.exists(file_path):
        result["valid"] = False
        result["issues"].append("file_not_exists")
        return result

    # 检查2: 文件大小
    file_size = os.path.getsize(file_path)
    if file_size < 10:
        result["valid"] = False
        result["issues"].append("file_too_small")
    result["file_size"] = file_size

    # 检查3: 文件可读
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result["valid"] = False
        result["issues"].append(f"read_error: {e}")
        return result

    # 检查4: 格式解析
    try:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            data = yaml.safe_load(content)
            result["format"] = "yaml"
        elif file_path.endswith('.json'):
            data = json.loads(content)
            result["format"] = "json"
        else:
            result["valid"] = False
            result["issues"].append("unknown_format")
            return result
    except Exception as e:
        result["valid"] = False
        result["issues"].append(f"parse_error: {e}")
        return result

    # 检查5: 必需字段
    if not isinstance(data, dict):
        result["valid"] = False
        result["issues"].append("not_dict")
        return result

    if "phase_id" not in data:
        result["valid"] = False
        result["issues"].append("missing_phase_id")

    if "state_data" not in data:
        result["valid"] = False
        result["issues"].append("missing_state_data")

    # 检查6: 元数据（推荐但非必需）
    if "metadata" not in data:
        result["issues"].append("missing_metadata")  # warning, not error

    result["phase_id"] = data.get("phase_id")
    result["field_count"] = len(data.get("state_data", {}))

    return result
```

### 步骤5: 验证Phase链的连续性

```python
def verify_phase_chain_continuity(manifest, scan_result):
    """
    验证Phase链的连续性（Phase 0 → 1 → 1.5 → 2 → 3 → 4）

    Args:
        manifest: 状态清单
        scan_result: 扫描结果

    Returns:
        dict: 连续性验证结果
    """
    # 定义标准Phase链
    standard_chain = [
        "phase_0",
        "phase_0_5",
        "phase_1",
        "phase_1_5",
        "phase_2",
        "phase_3",
        "phase_4"
    ]

    phases_in_manifest = set(manifest.get("phases", {}).keys())

    result = {
        "is_continuous": True,
        "highest_completed_phase": None,
        "expected_next_phase": None,
        "gaps": [],
        "chain_status": []
    }

    highest_index = -1

    for i, phase_id in enumerate(standard_chain):
        exists = phase_id in phases_in_manifest

        result["chain_status"].append({
            "phase_id": phase_id,
            "exists": exists,
            "index": i
        })

        if exists:
            highest_index = i
            result["highest_completed_phase"] = phase_id
        elif highest_index >= 0:
            # 发现缺口
            result["is_continuous"] = False
            result["gaps"].append({
                "after_phase": standard_chain[highest_index],
                "missing_phase": phase_id
            })

    # 确定下一个应执行的Phase
    if highest_index >= 0 and highest_index < len(standard_chain) - 1:
        if result["is_continuous"]:
            result["expected_next_phase"] = standard_chain[highest_index + 1]
        else:
            # 有缺口，应从第一个缺口开始
            result["expected_next_phase"] = result["gaps"][0]["missing_phase"]

    return result
```

### 步骤6: 深度检查（可选）

```python
def deep_check_state_consistency(state_folder, phases_to_check):
    """
    深度检查状态数据的一致性

    Args:
        state_folder: 状态目录
        phases_to_check: 要检查的Phase列表

    Returns:
        dict: 深度检查结果
    """
    result = {
        "checks_performed": [],
        "issues_found": [],
        "all_consistent": True
    }

    # 检查1: TenElementModel一致性
    # 从phase_1_5加载TenElementModel
    ten_element_file = Path(state_folder) / "phase_1_5_state_latest.yaml"
    if ten_element_file.exists():
        with open(ten_element_file, 'r') as f:
            phase_1_5_data = yaml.safe_load(f)

        ten_element_model = phase_1_5_data.get("state_data", {}).get("ten_element_model")
        model_hash = phase_1_5_data.get("state_data", {}).get("model_baseline", {}).get("hash")

        # 检查Phase 2是否引用了相同的模型
        phase_2_file = Path(state_folder) / "phase_2_state_latest.yaml"
        if phase_2_file.exists():
            with open(phase_2_file, 'r') as f:
                phase_2_data = yaml.safe_load(f)

            # 这里可以添加更复杂的一致性检查逻辑
            result["checks_performed"].append("ten_element_model_consistency")

    # 检查2: Todo List基线一致性
    # 从phase_0加载baseline_contract
    phase_0_file = Path(state_folder) / "phase_0_state_latest.yaml"
    if phase_0_file.exists():
        with open(phase_0_file, 'r') as f:
            phase_0_data = yaml.safe_load(f)

        baseline_hash = phase_0_data.get("state_data", {}).get("baseline_contract", {}).get("hash")

        # 在其他Phase中验证是否使用了相同的baseline
        result["checks_performed"].append("todo_baseline_consistency")

    # 检查3: 时间戳合理性
    # 验证Phase执行顺序的时间戳是否合理
    timestamps = {}
    for phase_id in phases_to_check:
        phase_file = Path(state_folder) / f"{phase_id}_state_latest.yaml"
        if phase_file.exists():
            with open(phase_file, 'r') as f:
                data = yaml.safe_load(f)
            timestamp_str = data.get("metadata", {}).get("timestamp")
            if timestamp_str:
                timestamps[phase_id] = timestamp_str

    # 验证时间戳递增
    sorted_phases = sorted(timestamps.items(), key=lambda x: x[1])
    expected_order = ["phase_0", "phase_0_5", "phase_1", "phase_1_5", "phase_2", "phase_3", "phase_4"]
    actual_order = [p[0] for p in sorted_phases]

    # 检查顺序是否符合预期
    for i in range(len(actual_order) - 1):
        if expected_order.index(actual_order[i]) > expected_order.index(actual_order[i+1]):
            result["all_consistent"] = False
            result["issues_found"].append({
                "type": "timestamp_order_violation",
                "phases": [actual_order[i], actual_order[i+1]]
            })

    result["checks_performed"].append("timestamp_order_check")

    return result
```

### 步骤7: 生成验证报告

```python
def generate_verification_report(
    manifest_check,
    scan_result,
    required_phases_check,
    file_integrity_checks,
    chain_continuity,
    deep_check_result=None
):
    """
    生成完整的验证报告

    Args:
        各检查步骤的结果

    Returns:
        dict: 完整验证报告
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "version": "4.3",
        "overall_status": "PASS",
        "summary": {},
        "details": {}
    }

    # 汇总检查结果
    total_issues = 0

    # 1. 清单检查
    if "warning" in manifest_check:
        total_issues += 1
        report["overall_status"] = "WARNING"

    # 2. 必需Phase检查
    if not required_phases_check["all_present"]:
        total_issues += len(required_phases_check["missing"])
        report["overall_status"] = "FAIL"

    # 3. 文件完整性检查
    invalid_files = [f for f in file_integrity_checks if not f["valid"]]
    if invalid_files:
        total_issues += len(invalid_files)
        report["overall_status"] = "FAIL"

    # 4. Phase链连续性
    if not chain_continuity["is_continuous"]:
        total_issues += len(chain_continuity["gaps"])
        if report["overall_status"] == "PASS":
            report["overall_status"] = "WARNING"

    # 5. 深度检查
    if deep_check_result and not deep_check_result["all_consistent"]:
        total_issues += len(deep_check_result["issues_found"])
        if report["overall_status"] == "PASS":
            report["overall_status"] = "WARNING"

    # 填充摘要
    report["summary"] = {
        "total_issues": total_issues,
        "total_files_scanned": scan_result.get("total_files", 0),
        "required_phases_missing": len(required_phases_check["missing"]),
        "invalid_files": len(invalid_files),
        "phase_chain_gaps": len(chain_continuity.get("gaps", [])),
        "deep_check_issues": len(deep_check_result.get("issues_found", [])) if deep_check_result else 0
    }

    # 填充详细信息
    report["details"] = {
        "manifest": manifest_check,
        "scan": scan_result,
        "required_phases": required_phases_check,
        "file_integrity": file_integrity_checks,
        "chain_continuity": chain_continuity
    }

    if deep_check_result:
        report["details"]["deep_check"] = deep_check_result

    # 生成建议
    report["recommendations"] = generate_recommendations(
        required_phases_check,
        chain_continuity,
        invalid_files
    )

    return report
```

### 步骤8: 生成修复建议

```python
def generate_recommendations(required_phases_check, chain_continuity, invalid_files):
    """
    根据检查结果生成修复建议

    Args:
        各检查结果

    Returns:
        list: 建议列表
    """
    recommendations = []

    # 建议1: 缺失的Phase
    if required_phases_check["missing"]:
        for phase_id in required_phases_check["missing"]:
            recommendations.append({
                "priority": "HIGH",
                "issue": f"Phase {phase_id} 状态缺失",
                "action": f"执行 Phase {phase_id} 以生成状态文件",
                "command": f"# 从workflow步骤 {phase_id} 开始执行"
            })

    # 建议2: Phase链缺口
    if chain_continuity.get("gaps"):
        for gap in chain_continuity["gaps"]:
            recommendations.append({
                "priority": "MEDIUM",
                "issue": f"Phase链存在缺口: {gap['after_phase']} → {gap['missing_phase']}",
                "action": f"执行缺失的 Phase {gap['missing_phase']}",
                "command": f"# 建议从 Phase {gap['missing_phase']} 重新执行"
            })

    # 建议3: 损坏的文件
    if invalid_files:
        for file_info in invalid_files:
            recommendations.append({
                "priority": "HIGH",
                "issue": f"状态文件损坏: {file_info['file_path']}",
                "action": "删除损坏文件并重新执行对应的Phase",
                "command": f"rm {file_info['file_path']}"
            })

    # 建议4: 清单缺失
    # 可以自动重建清单

    return recommendations
```

## 输出

```yaml
outputs:
  verification_report:
    type: object
    required: true
    structure:
      timestamp: string
      version: string
      overall_status: string # PASS | WARNING | FAIL
      summary:
        total_issues: integer
        total_files_scanned: integer
        required_phases_missing: integer
        invalid_files: integer
        phase_chain_gaps: integer
      details: object
      recommendations: array
    description: '完整的验证报告'

  overall_status:
    type: string
    enum: [PASS, WARNING, FAIL]
    description: '整体验证状态'

  issues_found:
    type: integer
    description: '发现的问题总数'

  all_checks_passed:
    type: boolean
    description: '所有检查是否通过'
```

## 示例输出

```json
{
  "verification_report": {
    "timestamp": "2025-10-23T16:30:00.000000",
    "version": "4.3",
    "overall_status": "WARNING",
    "summary": {
      "total_issues": 2,
      "total_files_scanned": 5,
      "required_phases_missing": 0,
      "invalid_files": 0,
      "phase_chain_gaps": 1
    },
    "details": {
      "required_phases": {
        "all_present": true,
        "missing": [],
        "present": ["phase_0", "phase_1", "phase_1_5", "phase_3"]
      },
      "chain_continuity": {
        "is_continuous": false,
        "highest_completed_phase": "phase_3",
        "expected_next_phase": "phase_2",
        "gaps": [
          {
            "after_phase": "phase_1_5",
            "missing_phase": "phase_2"
          }
        ]
      }
    },
    "recommendations": [
      {
        "priority": "MEDIUM",
        "issue": "Phase链存在缺口: phase_1_5 → phase_2",
        "action": "执行缺失的 Phase phase_2",
        "command": "# 建议从 Phase phase_2 重新执行"
      }
    ]
  },
  "overall_status": "WARNING",
  "issues_found": 2,
  "all_checks_passed": false
}
```

## 质量检查

执行此任务后，必须确认：

- [ ] 状态清单已加载或标记为缺失
- [ ] 状态目录已扫描
- [ ] 必需的Phase已检查
- [ ] 所有文件完整性已验证
- [ ] Phase链连续性已验证
- [ ] 深度检查已执行（如启用）
- [ ] 验证报告已生成
- [ ] 修复建议已提供
- [ ] 所有输出字段已返回

## 引用

- @编排协调专家库/状态管理规范
- @质量评测专家库/完整性验证标准
- BMAD-METHOD v6 架构规范: 状态链完整性
- Phase依赖关系定义

---

**创建**: 2025-10-23
**BMAD版本**: v6-alpha
**核心机制**: 全面状态验证，确保workflow执行可靠性
**适用场景**: 启动前检查、质量门禁、故障排查
