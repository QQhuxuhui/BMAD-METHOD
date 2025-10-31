# Task: Verify Phase Prerequisites

**任务ID**: `verify-phase-prerequisites`
**版本**: V4.3
**用途**: 在Phase执行前验证所有前置依赖Phase的状态文件完整性，确保workflow状态链完整

## 🚨 核心目标

**在每个Phase开始前，强制验证所有依赖的前置Phase状态文件已存在且有效。任何依赖缺失或无效都将阻断流程。**

这是防止状态文件缺失导致系统崩溃的关键防护机制。

## 输入

```yaml
inputs:
  - current_phase_id: 当前要执行的Phase标识 (如 "phase_1", "phase_2")
  - state_folder: 状态文件目录路径
  - strict_mode: 严格模式 (true则任何警告也阻断，默认false)
```

## Phase依赖关系图

```python
# 定义每个Phase的前置依赖关系
PHASE_DEPENDENCIES = {
    "phase_0": [],  # 第一个Phase，无依赖
    "phase_0_5": ["phase_0"],
    "phase_1": ["phase_0", "phase_0_5"],
    "phase_1_5": ["phase_0", "phase_0_5", "phase_1"],
    "phase_2": ["phase_0", "phase_0_5", "phase_1", "phase_1_5"],
    "phase_3": ["phase_0", "phase_0_5", "phase_1", "phase_1_5", "phase_2"],
    "phase_4": ["phase_0", "phase_0_5", "phase_1", "phase_1_5", "phase_2", "phase_3"]
}

# Phase的必需交付物字段定义
PHASE_REQUIRED_DELIVERABLES = {
    "phase_0": ["confirmed_todo_list", "baseline_contract", "tracker_initialized"],
    "phase_0_5": ["selected_mode", "workflow_configuration", "phase_plan"],
    "phase_1": ["requirement_analysis", "clarified_requirements", "deviation_score"],
    "phase_1_5": ["ten_element_model", "model_baseline", "model_hash"],
    "phase_2": ["domain_analysis", "constraint_analysis", "objective_analysis", "algorithm_recommendations", "consistency_report"],
    "phase_3": ["integrated_solution", "implementation_code", "code_traceability", "saved_files"],
    "phase_4": ["quality_report", "gate_status", "todo_completion_status"]
}
```

## 处理逻辑

### 步骤1: 获取当前Phase的前置依赖列表

```python
def get_phase_prerequisites(current_phase_id):
    """
    获取当前Phase的前置依赖列表

    Args:
        current_phase_id: 当前Phase标识

    Returns:
        list: 前置依赖Phase列表

    Raises:
        ValueError: 无效的phase_id
    """
    if current_phase_id not in PHASE_DEPENDENCIES:
        raise ValueError(
            f"❌ 无效的Phase ID: {current_phase_id}\n"
            f"有效的Phase ID: {list(PHASE_DEPENDENCIES.keys())}"
        )

    prerequisites = PHASE_DEPENDENCIES[current_phase_id]

    if not prerequisites:
        print(f"✓ {current_phase_id} 无前置依赖")
        return []

    print(f"✓ {current_phase_id} 依赖 {len(prerequisites)} 个前置Phase: {prerequisites}")
    return prerequisites
```

### 步骤2: 验证每个前置Phase的状态文件存在性

```python
import os
from pathlib import Path

def verify_prerequisites_existence(prerequisites, state_folder):
    """
    验证所有前置Phase状态文件是否存在

    Args:
        prerequisites: 前置Phase列表
        state_folder: 状态目录

    Returns:
        dict: 验证结果

    Raises:
        FileNotFoundError: 任何前置状态文件缺失
    """
    verification = {
        "all_present": True,
        "missing": [],
        "present": [],
        "details": {}
    }

    for phase_id in prerequisites:
        # 查找该Phase的状态文件（latest或最新时间戳）
        state_path = Path(state_folder)

        # 优先查找latest链接
        latest_file = state_path / f"{phase_id}_state_latest.yaml"

        if latest_file.exists():
            verification["present"].append(phase_id)
            verification["details"][phase_id] = {
                "status": "present",
                "file_path": str(latest_file),
                "file_type": "latest_link"
            }
            print(f"  ✓ {phase_id}: 存在 (latest)")
            continue

        # 查找时间戳文件
        pattern = f"{phase_id}_state_*.yaml"
        matching_files = sorted(state_path.glob(pattern), reverse=True)

        if matching_files:
            latest_file = matching_files[0]
            verification["present"].append(phase_id)
            verification["details"][phase_id] = {
                "status": "present",
                "file_path": str(latest_file),
                "file_type": "timestamped"
            }
            print(f"  ✓ {phase_id}: 存在 (时间戳文件)")
            continue

        # 查找标准文件
        standard_file = state_path / f"{phase_id}_state.yaml"
        if standard_file.exists():
            verification["present"].append(phase_id)
            verification["details"][phase_id] = {
                "status": "present",
                "file_path": str(standard_file),
                "file_type": "standard"
            }
            print(f"  ✓ {phase_id}: 存在 (标准文件)")
            continue

        # 文件缺失
        verification["all_present"] = False
        verification["missing"].append(phase_id)
        verification["details"][phase_id] = {
            "status": "missing",
            "file_path": None
        }
        print(f"  ✗ {phase_id}: 缺失")

    # 如果有缺失，立即阻断
    if not verification["all_present"]:
        error_message = f"""
❌ CRITICAL ERROR: 前置Phase状态文件缺失！

缺失的Phase: {verification['missing']}

当前要执行的Phase: {current_phase_id}
依赖的前置Phase: {prerequisites}
已存在的Phase: {verification['present']}
缺失的Phase: {verification['missing']}

状态目录: {state_folder}

可能原因:
1. 前置Phase尚未执行完成
2. 前置Phase执行时文件保存失败
3. 状态文件被误删除
4. 状态目录路径配置错误

解决方案:
- 请从第一个缺失的Phase ({verification['missing'][0]}) 重新开始执行工作流
- 或检查状态目录是否存在且有访问权限
- 或检查 config.yaml 中的 state_folder 配置

⛔ 流程已阻断，无法继续执行 {current_phase_id}
"""
        raise FileNotFoundError(error_message)

    return verification
```

### 步骤3: 验证每个前置Phase状态文件的完整性

```python
import yaml
import json

def verify_prerequisites_integrity(present_phases, details, state_folder):
    """
    验证所有前置Phase状态文件的完整性

    Args:
        present_phases: 存在的Phase列表
        details: Phase详情
        state_folder: 状态目录

    Returns:
        dict: 完整性验证结果

    Raises:
        ValueError: 任何状态文件损坏或无效
    """
    integrity_results = {
        "all_valid": True,
        "valid": [],
        "invalid": [],
        "details": {}
    }

    for phase_id in present_phases:
        file_path = details[phase_id]["file_path"]

        try:
            # 检查1: 文件大小
            file_size = os.path.getsize(file_path)
            if file_size < 10:
                raise ValueError(f"文件过小: {file_size} bytes")

            # 检查2: 文件可读
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查3: YAML格式有效
            data = yaml.safe_load(content)

            # 检查4: 数据结构有效
            if not isinstance(data, dict):
                raise ValueError("数据不是字典类型")

            if "phase_id" not in data:
                raise ValueError("缺少phase_id字段")

            if "state_data" not in data:
                raise ValueError("缺少state_data字段")

            # 检查5: phase_id匹配
            if data["phase_id"] != phase_id:
                raise ValueError(f"phase_id不匹配: 期望{phase_id}, 实际{data['phase_id']}")

            # 检查6: 验证必需交付物字段
            state_data = data.get("state_data", {})
            required_deliverables = PHASE_REQUIRED_DELIVERABLES.get(phase_id, [])
            missing_deliverables = []

            for deliverable in required_deliverables:
                if deliverable not in state_data:
                    missing_deliverables.append(deliverable)

            if missing_deliverables:
                raise ValueError(f"缺少必需交付物: {missing_deliverables}")

            # 所有检查通过
            integrity_results["valid"].append(phase_id)
            integrity_results["details"][phase_id] = {
                "status": "valid",
                "file_size": file_size,
                "checks_passed": [
                    "file_size_ok",
                    "file_readable",
                    "yaml_valid",
                    "structure_valid",
                    "phase_id_match",
                    "deliverables_complete"
                ]
            }
            print(f"  ✓ {phase_id}: 完整性验证通过 ({file_size} bytes)")

        except Exception as e:
            # 验证失败
            integrity_results["all_valid"] = False
            integrity_results["invalid"].append(phase_id)
            integrity_results["details"][phase_id] = {
                "status": "invalid",
                "error": str(e)
            }
            print(f"  ✗ {phase_id}: 完整性验证失败 - {e}")

    # 如果有无效文件，立即阻断
    if not integrity_results["all_valid"]:
        error_message = f"""
❌ CRITICAL ERROR: 前置Phase状态文件损坏或无效！

无效的Phase: {integrity_results['invalid']}

详细错误:
"""
        for phase_id in integrity_results["invalid"]:
            error_details = integrity_results["details"][phase_id]
            error_message += f"\n  - {phase_id}: {error_details['error']}"

        error_message += f"""

解决方案:
- 删除损坏的状态文件
- 从第一个无效的Phase ({integrity_results['invalid'][0]}) 重新执行工作流

⛔ 流程已阻断，无法继续执行
"""
        raise ValueError(error_message)

    return integrity_results
```

### 步骤4: 生成验证报告

```python
from datetime import datetime

def generate_prerequisite_verification_report(
    current_phase_id,
    prerequisites,
    existence_check,
    integrity_check
):
    """
    生成前置依赖验证报告

    Args:
        current_phase_id: 当前Phase
        prerequisites: 前置依赖列表
        existence_check: 存在性检查结果
        integrity_check: 完整性检查结果

    Returns:
        dict: 验证报告
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "current_phase_id": current_phase_id,
        "prerequisites_count": len(prerequisites),
        "prerequisites": prerequisites,
        "verification_result": "PASS",
        "summary": {
            "all_prerequisites_present": existence_check["all_present"],
            "all_prerequisites_valid": integrity_check["all_valid"],
            "total_prerequisites": len(prerequisites),
            "present_count": len(existence_check["present"]),
            "missing_count": len(existence_check["missing"]),
            "valid_count": len(integrity_check["valid"]),
            "invalid_count": len(integrity_check["invalid"])
        },
        "details": {
            "existence_check": existence_check,
            "integrity_check": integrity_check
        }
    }

    # 最终判定
    if report["summary"]["all_prerequisites_present"] and report["summary"]["all_prerequisites_valid"]:
        report["verification_result"] = "PASS"
        report["message"] = f"✅ 所有前置依赖验证通过，{current_phase_id} 可以安全执行"
    else:
        report["verification_result"] = "FAIL"
        report["message"] = f"❌ 前置依赖验证失败，{current_phase_id} 无法执行"

    return report
```

## 输出

```yaml
outputs:
  verification_report:
    type: object
    required: true
    structure:
      timestamp: string
      current_phase_id: string
      prerequisites_count: integer
      prerequisites: array
      verification_result: string # PASS | FAIL
      message: string
      summary:
        all_prerequisites_present: boolean
        all_prerequisites_valid: boolean
        total_prerequisites: integer
        present_count: integer
        missing_count: integer
        valid_count: integer
        invalid_count: integer
      details: object
    description: '前置依赖验证报告'

  all_prerequisites_valid:
    type: boolean
    required: true
    description: '所有前置依赖是否有效'

  can_proceed:
    type: boolean
    required: true
    description: '当前Phase是否可以继续执行'
```

## 示例输出

### 示例1: 验证通过

```json
{
  "verification_report": {
    "timestamp": "2025-10-29T10:00:00.000000",
    "current_phase_id": "phase_2",
    "prerequisites_count": 4,
    "prerequisites": ["phase_0", "phase_0_5", "phase_1", "phase_1_5"],
    "verification_result": "PASS",
    "message": "✅ 所有前置依赖验证通过，phase_2 可以安全执行",
    "summary": {
      "all_prerequisites_present": true,
      "all_prerequisites_valid": true,
      "total_prerequisites": 4,
      "present_count": 4,
      "missing_count": 0,
      "valid_count": 4,
      "invalid_count": 0
    },
    "details": {
      "existence_check": {
        "all_present": true,
        "missing": [],
        "present": ["phase_0", "phase_0_5", "phase_1", "phase_1_5"]
      },
      "integrity_check": {
        "all_valid": true,
        "invalid": [],
        "valid": ["phase_0", "phase_0_5", "phase_1", "phase_1_5"]
      }
    }
  },
  "all_prerequisites_valid": true,
  "can_proceed": true
}
```

### 示例2: 验证失败（文件缺失）

```json
{
  "verification_report": {
    "timestamp": "2025-10-29T10:00:00.000000",
    "current_phase_id": "phase_3",
    "prerequisites_count": 5,
    "prerequisites": ["phase_0", "phase_0_5", "phase_1", "phase_1_5", "phase_2"],
    "verification_result": "FAIL",
    "message": "❌ 前置依赖验证失败，phase_3 无法执行",
    "summary": {
      "all_prerequisites_present": false,
      "all_prerequisites_valid": false,
      "total_prerequisites": 5,
      "present_count": 4,
      "missing_count": 1,
      "valid_count": 0,
      "invalid_count": 0
    },
    "details": {
      "existence_check": {
        "all_present": false,
        "missing": ["phase_2"],
        "present": ["phase_0", "phase_0_5", "phase_1", "phase_1_5"]
      }
    }
  },
  "all_prerequisites_valid": false,
  "can_proceed": false
}
```

## 质量检查

执行此任务后，必须确认：

- [ ] 当前Phase的前置依赖列表已获取
- [ ] 🚨 **所有前置状态文件存在性已检查（缺失必阻断）**
- [ ] 🚨 **所有前置状态文件完整性已验证（损坏必阻断）**
- [ ] 🚨 **所有必需交付物字段已验证**
- [ ] 验证报告已生成
- [ ] 所有输出字段已返回
- [ ] 验证失败时流程已阻断

## 错误处理

### 前置状态文件缺失

```yaml
scenario: 任何前置Phase状态文件不存在
action:
  - 抛出 FileNotFoundError
  - 包含详细错误信息（缺失的Phase列表）
  - 阻断workflow执行
  - 提供恢复建议（从哪个Phase重新执行）
  - 返回错误码 ERR_PREREQUISITE_MISSING
```

### 前置状态文件损坏

```yaml
scenario: 任何前置Phase状态文件无法解析或字段缺失
action:
  - 抛出 ValueError
  - 记录详细错误（Phase ID、错误原因）
  - 阻断workflow执行
  - 建议删除损坏文件并重新执行
  - 返回错误码 ERR_PREREQUISITE_INVALID
```

### Phase ID无效

```yaml
scenario: 提供的phase_id不在依赖关系图中
action:
  - 抛出 ValueError
  - 列出有效的Phase ID列表
  - 阻断workflow执行
  - 返回错误码 ERR_INVALID_PHASE_ID
```

## 使用示例

### 在workflow.yaml中使用

```yaml
# Phase 2开始前的前置验证
- step_id: '2.0-prerequisite-check'
  name: '验证Phase 2的前置依赖'
  action: 'exec'
  target: 'bmad/aps/tasks/verify-phase-prerequisites.md'
  inputs:
    - current_phase_id: 'phase_2'
    - state_folder: '${config.state_management.state_folder}'
    - strict_mode: false
  outputs:
    - verification_report
    - all_prerequisites_valid # 必须为true，否则阻断
    - can_proceed # 必须为true，否则阻断

# 只有前置验证通过，才执行Phase 2
- step_id: '2.1'
  name: 'Phase 2: 专家协调'
  condition: 'all_prerequisites_valid == true'
  action: 'run-workflow'
  target: 'bmad/aps/workflows/phase-2-coordination/workflow.yaml'
```

## 与其他任务的关系

```
verify-phase-prerequisites.md (本任务)
  ↓ 调用
verify-state-integrity.md (用于深度检查)
  ↓ 依赖
load-phase-state.md (用于加载和验证单个状态)
  ↓ 依赖
save-phase-state.md (前置Phase必须已保存状态)
```

## 引用

- @编排协调专家库/状态管理规范
- @编排协调专家库/Phase依赖关系图
- @质量评测专家库/前置依赖验证标准
- BMAD-METHOD v6 架构规范: Workflow状态链完整性
- Phase 0-4 完整流程定义

---

**创建**: 2025-10-29
**BMAD版本**: v6-alpha
**核心机制**: 前置依赖强制验证，确保Phase执行顺序正确且状态链完整
**关键作用**: 防止状态文件缺失导致的系统崩溃，是workflow健壮性的关键防护
**使用场景**: 每个Phase开始前必须执行（Phase 0除外）
