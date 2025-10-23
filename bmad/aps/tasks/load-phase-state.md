# Task: Load Phase State

**任务ID**: `load-phase-state`
**版本**: V4.3
**用途**: 加载上一个Phase的持久化状态，作为当前Phase的输入依据

## 输入

```yaml
inputs:
  - phase_id: 要加载的Phase标识 (如 "phase_0", "phase_1")
  - state_folder: 状态文件目录路径
  - required: 是否必需 (true则缺失时阻断流程，默认true)
  - use_latest: 是否使用latest链接 (默认true)
  - format: 期望的文件格式 (yaml|json，默认yaml)
```

## 🚨 强制要求 (MANDATORY)

### 1. 文件缺失必须阻断流程

如果`required=true`且状态文件不存在，**必须抛出异常并阻断workflow执行**，不允许继续。

```yaml
error_handling:
  on_file_missing:
    action: 'block_workflow'
    error_type: 'FileNotFoundError'
    error_level: 'CRITICAL'
    recovery_hint: '请从Phase {phase_id}重新执行'
```

### 2. 必须使用IDE的Read工具

加载文件时，必须实际调用IDE提供的Read工具，而不是仅输出Python代码示例。

### 3. 必须验证文件完整性

加载前必须验证：

- ✓ 文件存在
- ✓ 文件大小合理
- ✓ 文件可读取
- ✓ 内容格式正确

任何验证失败都必须抛出异常。

## 处理逻辑

### 步骤1: 确定要加载的文件路径

```python
import os
from pathlib import Path

def determine_file_path(phase_id, state_folder, use_latest=True, format='yaml'):
    """
    确定要加载的状态文件路径

    Args:
        phase_id: Phase标识
        state_folder: 状态目录
        use_latest: 是否使用latest链接
        format: 文件格式

    Returns:
        str: 文件路径
    """
    base_path = Path(state_folder)

    if use_latest:
        # 优先使用latest链接
        latest_file = base_path / f"{phase_id}_state_latest.{format}"
        if latest_file.exists():
            print(f"✓ 使用latest链接: {latest_file}")
            return str(latest_file)

    # 如果没有latest，查找最新的时间戳文件
    pattern = f"{phase_id}_state_*.{format}"
    matching_files = sorted(base_path.glob(pattern), reverse=True)

    if matching_files:
        latest_file = matching_files[0]
        print(f"✓ 使用最新文件: {latest_file}")
        return str(latest_file)

    # 尝试无时间戳的文件名
    fallback_file = base_path / f"{phase_id}_state.{format}"
    if fallback_file.exists():
        print(f"✓ 使用标准文件: {fallback_file}")
        return str(fallback_file)

    return None
```

### 步骤2: 🚨 检查文件是否存在

```python
def check_state_file_exists(phase_id, file_path, required=True):
    """
    检查状态文件是否存在

    Args:
        phase_id: Phase标识
        file_path: 文件路径
        required: 是否必需

    Returns:
        tuple: (文件路径或None, 是否存在)

    Raises:
        FileNotFoundError: 当required=True且文件不存在时
    """
    if file_path is None or not os.path.exists(file_path):
        if required:
            error_message = f"""
❌ CRITICAL ERROR: Phase {phase_id} 状态文件缺失！

文件路径: {file_path if file_path else 'N/A'}

可能原因:
1. Phase {phase_id} 尚未执行完成
2. Phase {phase_id} 执行时文件保存失败
3. 状态文件被误删除
4. 状态目录路径配置错误

解决方案:
- 请从 Phase {phase_id} 重新开始执行工作流
- 或检查状态目录是否存在且有访问权限
- 或检查 config.yaml 中的 state_folder 配置

当前状态目录: {os.path.dirname(file_path) if file_path else 'N/A'}
"""
            raise FileNotFoundError(error_message)
        else:
            print(f"⚠ 状态文件不存在（非必需）: {file_path}")
            return None, False

    print(f"✓ 状态文件存在: {file_path}")
    return file_path, True
```

### 步骤3: 验证文件完整性

```python
def verify_state_file_integrity(file_path, format='yaml'):
    """
    验证状态文件的完整性

    Args:
        file_path: 文件路径
        format: 期望的格式

    Returns:
        dict: 验证结果

    Raises:
        ValueError: 文件损坏
        IOError: 文件不可读
    """
    verification = {
        "file_path": file_path,
        "checks": {}
    }

    # 检查1: 是否为文件（非目录）
    if not os.path.isfile(file_path):
        raise ValueError(f"❌ 路径不是文件: {file_path}")
    verification["checks"]["is_file"] = True

    # 检查2: 文件大小
    file_size = os.path.getsize(file_path)
    if file_size < 10:  # 至少10字节
        raise ValueError(
            f"❌ 文件可能损坏: 大小仅 {file_size} bytes\n"
            f"文件: {file_path}"
        )
    verification["checks"]["size_valid"] = True
    verification["file_size"] = file_size

    # 检查3: 文件可读性
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if not first_line:
                raise ValueError("文件为空")
    except UnicodeDecodeError:
        raise IOError(f"❌ 文件编码错误，无法以UTF-8读取: {file_path}")
    except Exception as e:
        raise IOError(f"❌ 文件不可读: {e}")
    verification["checks"]["readable"] = True

    # 检查4: 格式初步验证（检查扩展名）
    expected_ext = f".{format}"
    if not file_path.endswith(expected_ext):
        print(f"⚠ 文件扩展名不匹配: 期望{expected_ext}，实际{os.path.splitext(file_path)[1]}")
    verification["checks"]["extension_match"] = file_path.endswith(expected_ext)

    verification["all_checks_passed"] = all(verification["checks"].values())

    print(f"✓ 文件完整性验证通过: {file_path} ({file_size} bytes)")
    return verification
```

### 步骤4: 🚨 使用Read工具加载文件

**CRITICAL STEP - 必须实际执行文件读取**

此步骤AI必须调用IDE的Read工具，格式如下：

```
IDE Tool: Read
File Path: {file_path}
```

**示例执行步骤**：

```python
# 1. 准备文件路径
file_path = f"{state_folder}/{phase_id}_state_latest.yaml"

# 2. 🚨 调用Read工具（伪代码，实际使用IDE工具）
# Read Tool:
#   file_path: {file_path}

# 3. Read工具返回文件内容
# file_content = <Read工具返回的内容>
```

### 步骤5: 解析并验证状态数据

```python
import yaml
import json

def parse_and_validate_state(file_content, format='yaml', phase_id=None):
    """
    解析并验证状态数据

    Args:
        file_content: 文件内容（字符串）
        format: 文件格式
        phase_id: 期望的Phase ID（用于验证）

    Returns:
        dict: 解析后的状态数据

    Raises:
        ValueError: 解析失败或验证失败
    """
    # 解析文件内容
    try:
        if format == 'yaml':
            data = yaml.safe_load(file_content)
        elif format == 'json':
            data = json.loads(file_content)
        else:
            raise ValueError(f"不支持的格式: {format}")

        print(f"✓ 状态数据已解析 ({format}格式)")

    except yaml.YAMLError as e:
        raise ValueError(f"❌ YAML解析失败: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ JSON解析失败: {e}")
    except Exception as e:
        raise ValueError(f"❌ 状态数据解析失败: {e}")

    # 验证数据结构
    if not isinstance(data, dict):
        raise ValueError(f"❌ 状态数据必须是字典类型，当前类型: {type(data)}")

    # 验证必需字段
    if "phase_id" not in data:
        raise ValueError("❌ 状态数据缺少 'phase_id' 字段")

    if "state_data" not in data:
        raise ValueError("❌ 状态数据缺少 'state_data' 字段")

    # 验证phase_id是否匹配（如果提供）
    if phase_id and data["phase_id"] != phase_id:
        raise ValueError(
            f"❌ Phase ID不匹配: 期望 {phase_id}，实际 {data['phase_id']}"
        )

    print(f"✓ 状态数据验证通过: phase_id={data['phase_id']}")
    return data
```

### 步骤6: 提取状态数据和元数据

```python
def extract_state_and_metadata(parsed_data):
    """
    从解析后的数据中提取状态数据和元数据

    Args:
        parsed_data: 解析后的完整数据

    Returns:
        tuple: (state_data, metadata)
    """
    state_data = parsed_data.get("state_data", {})
    metadata = parsed_data.get("metadata", {})

    print(f"✓ 状态数据提取完成: {len(state_data)} 个字段")

    if metadata:
        print(f"  - 时间戳: {metadata.get('timestamp', 'N/A')}")
        print(f"  - 版本: {metadata.get('version', 'N/A')}")
        print(f"  - 字段: {metadata.get('fields', [])}")

    return state_data, metadata
```

### 步骤7: 验证状态数据的业务完整性

```python
def validate_business_completeness(phase_id, state_data, metadata):
    """
    验证状态数据的业务完整性（可选但推荐）

    Args:
        phase_id: Phase标识
        state_data: 状态数据
        metadata: 元数据

    Returns:
        dict: 验证结果
    """
    validation_result = {
        "phase_id": phase_id,
        "checks": {},
        "warnings": []
    }

    # 检查1: 状态数据不为空
    if not state_data:
        validation_result["warnings"].append("状态数据为空")
    validation_result["checks"]["not_empty"] = bool(state_data)

    # 检查2: 元数据存在
    if not metadata:
        validation_result["warnings"].append("缺少元数据")
    validation_result["checks"]["has_metadata"] = bool(metadata)

    # 检查3: 字段数量与元数据声明一致
    if metadata and "field_count" in metadata:
        expected_count = metadata["field_count"]
        actual_count = len(state_data)
        if expected_count != actual_count:
            validation_result["warnings"].append(
                f"字段数量不匹配: 期望{expected_count}，实际{actual_count}"
            )
        validation_result["checks"]["field_count_match"] = (expected_count == actual_count)

    # 检查4: 元数据声明的字段都存在
    if metadata and "fields" in metadata:
        declared_fields = set(metadata["fields"])
        actual_fields = set(state_data.keys())
        missing_fields = declared_fields - actual_fields
        if missing_fields:
            validation_result["warnings"].append(
                f"缺少声明的字段: {missing_fields}"
            )
        validation_result["checks"]["all_fields_present"] = not bool(missing_fields)

    validation_result["all_checks_passed"] = all(validation_result["checks"].values())

    if validation_result["warnings"]:
        for warning in validation_result["warnings"]:
            print(f"⚠ {warning}")

    print(f"✓ 业务完整性验证完成")
    return validation_result
```

### 步骤8: 记录加载操作到清单

```python
def log_load_operation(phase_id, file_path, state_folder):
    """
    记录加载操作到清单（用于审计）

    Args:
        phase_id: Phase标识
        file_path: 加载的文件路径
        state_folder: 状态目录

    Returns:
        bool: 是否成功记录
    """
    from datetime import datetime

    manifest_path = os.path.join(state_folder, "phase_state_manifest.json")

    try:
        # 加载现有清单
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        else:
            print("⚠ 清单文件不存在，跳过加载日志记录")
            return False

        # 添加加载记录
        if "load_history" not in manifest:
            manifest["load_history"] = []

        manifest["load_history"].append({
            "phase_id": phase_id,
            "file_path": file_path,
            "loaded_at": datetime.now().isoformat(),
            "operation": "load"
        })

        # 保存清单
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"✓ 加载操作已记录到清单")
        return True

    except Exception as e:
        print(f"⚠ 清单记录失败（非致命）: {e}")
        return False
```

## 输出

```yaml
outputs:
  state_data:
    type: object
    required: true
    description: '加载的状态数据（不包含元数据）'
    example:
      confirmed_todo_list: [...]
      baseline_contract: { ... }
      tracker_initialized: { ... }

  metadata:
    type: object
    required: false
    description: '状态数据的元数据'
    structure:
      timestamp: string
      version: string
      bmad_version: string
      state_schema_version: string
      field_count: integer
      fields: array

  load_success:
    type: boolean
    required: true
    description: '是否加载成功'

  file_metadata:
    type: object
    required: true
    structure:
      file_path: string
      file_size: integer
      format: string
      loaded_at: string
    description: '加载的文件元数据'

  verification_result:
    type: object
    structure:
      all_checks_passed: boolean
      checks: object
      warnings: array
    description: '验证结果'
```

## 示例输出

```json
{
  "state_data": {
    "confirmed_todo_list": [
      {
        "phase": "Phase 0",
        "tasks": ["需求理解与初步分析", "生成Todo List"]
      }
    ],
    "baseline_contract": {
      "hash": "e4b3c2a1d5f6",
      "similarity_threshold": 0.6,
      "created_at": "2025-10-23T14:30:22"
    },
    "tracker_initialized": {
      "tracker_id": "todo_tracker_001",
      "baseline_set": true,
      "deviation_detection_enabled": true
    }
  },
  "metadata": {
    "timestamp": "2025-10-23T14:30:22.123456",
    "version": "4.3",
    "bmad_version": "v6-alpha",
    "state_schema_version": "1.0",
    "field_count": 3,
    "fields": ["confirmed_todo_list", "baseline_contract", "tracker_initialized"]
  },
  "load_success": true,
  "file_metadata": {
    "file_path": "aps-outputs/states/phase_0_state_latest.yaml",
    "file_size": 1256,
    "format": "yaml",
    "loaded_at": "2025-10-23T15:12:45.678901"
  },
  "verification_result": {
    "all_checks_passed": true,
    "checks": {
      "not_empty": true,
      "has_metadata": true,
      "field_count_match": true,
      "all_fields_present": true
    },
    "warnings": []
  }
}
```

## 质量检查

执行此任务后，必须确认：

- [ ] 文件路径已确定（latest或最新时间戳）
- [ ] 🚨 **文件存在性已检查（缺失时已阻断）**
- [ ] 文件完整性已验证
- [ ] 🚨 **Read工具已实际调用**
- [ ] 状态数据已成功解析
- [ ] 必需字段已验证
- [ ] Phase ID已匹配
- [ ] 状态数据已提取
- [ ] 业务完整性已验证
- [ ] 所有输出字段已返回

## 错误处理

### 文件缺失（required=true）

```yaml
scenario: 状态文件不存在且required=true
action:
  - 抛出 FileNotFoundError
  - 包含详细错误信息和恢复建议
  - 阻断workflow执行
  - 返回错误码 ERR_STATE_FILE_MISSING
```

### 文件损坏

```yaml
scenario: 文件存在但无法解析
action:
  - 抛出 ValueError
  - 记录详细错误（文件路径、大小、格式）
  - 建议检查文件完整性
  - 建议从备份恢复或重新执行Phase
```

### Phase ID不匹配

```yaml
scenario: 加载的文件phase_id与期望不符
action:
  - 抛出 ValueError
  - 说明期望vs实际的phase_id
  - 建议检查文件路径或重新执行
```

### 字段缺失

```yaml
scenario: 元数据声明的字段在state_data中不存在
action:
  - 记录警告（非致命）
  - 继续加载已有字段
  - 在verification_result中标记warnings
  - 建议用户检查Phase执行是否完整
```

## 使用示例

### 示例1: Phase 1加载Phase 0状态

```yaml
# 在workflow.yaml中
- step_id: '1.0'
  name: '加载Phase 0状态'
  action: 'exec'
  target: 'bmad/aps/tasks/load-phase-state.md'
  inputs:
    - phase_id: 'phase_0'
    - state_folder: '${config.state_management.state_folder}'
    - required: true
    - use_latest: true
  outputs:
    - baseline_contract # 从文件加载
    - confirmed_todo_list # 从文件加载
    - load_success
```

### 示例2: 加载可选状态

```yaml
- step_id: '2.0'
  name: '尝试加载缓存数据（可选）'
  action: 'exec'
  target: 'bmad/aps/tasks/load-phase-state.md'
  inputs:
    - phase_id: 'phase_cache'
    - state_folder: '${config.state_management.state_folder}'
    - required: false # 不存在也不报错
    - use_latest: true
  outputs:
    - cached_data # 可能为null
    - load_success # false if not found
```

## 引用

- @编排协调专家库/状态管理规范
- @质量评测专家库/数据验证标准
- BMAD-METHOD v6 架构规范: Workflow状态加载
- IDE兼容性指南: 跨IDE文件读取

---

**创建**: 2025-10-23
**BMAD版本**: v6-alpha
**核心机制**: 状态加载 + 强制验证，确保Phase间依赖完整性
**可靠性**: 文件缺失阻断机制，避免脏数据传递
