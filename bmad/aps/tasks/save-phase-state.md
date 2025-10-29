# Task: Save Phase State

**任务ID**: `save-phase-state`
**版本**: V4.3
**用途**: 通用的Phase状态持久化任务，将Phase执行结果保存到文件系统

## 输入

```yaml
inputs:
  - phase_id: Phase标识 (如 "phase_0", "phase_1")
  - state_data: 要保存的状态数据 (dict)
  - state_folder: 状态文件目录路径
  - format: 保存格式 (yaml|json，默认yaml)
  - include_metadata: 是否包含元数据 (默认true)
```

## 🚨 强制要求 (MANDATORY)

### 1. 必须使用IDE的Write工具

**CRITICAL**: 此任务执行时，AI必须实际调用IDE提供的Write工具来保存文件，而不是仅输出Python代码示例。

```
适用于所有IDE:
- Claude Code: 使用 Write 工具
- Cursor: 使用 Write 工具
- Windsurf: 使用 Write 工具
- 其他IDE: 使用对应的文件写入工具
```

### 2. 保存后必须验证

保存每个文件后，必须验证：

- ✓ 文件已创建
- ✓ 文件大小 > 最小阈值
- ✓ 文件可读取
- ✓ 内容格式正确

验证失败则抛出错误，阻断流程。

## 处理逻辑

### 步骤1: 验证输入完整性

```python
def validate_inputs(phase_id, state_data, state_folder):
    """
    验证输入参数的有效性

    Args:
        phase_id: Phase标识
        state_data: 状态数据
        state_folder: 状态文件目录

    Raises:
        ValueError: 参数无效时抛出

    Returns:
        bool: 验证通过返回True
    """
    # 验证phase_id
    if not phase_id or not isinstance(phase_id, str):
        raise ValueError("phase_id必须是非空字符串")

    # 验证phase_id格式
    valid_phase_ids = [
        "phase_0", "phase_0_5", "phase_1", "phase_1_5",
        "phase_2", "phase_3", "phase_4"
    ]
    if phase_id not in valid_phase_ids:
        raise ValueError(f"无效的phase_id: {phase_id}，必须是: {valid_phase_ids}")

    # 验证state_data
    if not state_data:
        raise ValueError("state_data不能为空")

    if not isinstance(state_data, dict):
        raise TypeError(f"state_data必须是字典类型，当前类型: {type(state_data)}")

    # 验证state_folder
    if not state_folder or not isinstance(state_folder, str):
        raise ValueError("state_folder必须是非空字符串")

    print(f"✓ 输入验证通过: phase_id={phase_id}, state_data包含{len(state_data)}个字段")
    return True
```

### 步骤2: 准备输出目录结构

```python
import os
from pathlib import Path
from datetime import datetime

def prepare_state_directory(state_folder):
    """
    创建状态文件目录结构（如果不存在）

    Args:
        state_folder: 状态目录路径

    Returns:
        dict: 目录路径信息
    """
    base_path = Path(state_folder)

    # 创建主目录
    base_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ 状态目录已创建/验证: {base_path}")

    # 创建备份目录
    backup_path = base_path / "backups"
    backup_path.mkdir(exist_ok=True)
    print(f"✓ 备份目录已创建/验证: {backup_path}")

    return {
        "base": str(base_path),
        "backups": str(backup_path)
    }
```

### 步骤3: 生成状态文件路径

```python
def generate_state_file_path(phase_id, state_folder, format='yaml', include_timestamp=True):
    """
    生成状态文件的完整路径

    Args:
        phase_id: Phase标识
        state_folder: 状态目录
        format: 文件格式 (yaml|json)
        include_timestamp: 是否在文件名中包含时间戳

    Returns:
        dict: 包含文件路径信息
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if include_timestamp:
        filename = f"{phase_id}_state_{timestamp}.{format}"
        latest_link = f"{phase_id}_state_latest.{format}"
    else:
        filename = f"{phase_id}_state.{format}"
        latest_link = None

    file_path = os.path.join(state_folder, filename)

    result = {
        "file_path": file_path,
        "filename": filename,
        "timestamp": timestamp,
        "format": format
    }

    if latest_link:
        result["latest_link"] = os.path.join(state_folder, latest_link)

    print(f"✓ 状态文件路径: {file_path}")
    return result
```

### 步骤4: 构建完整状态数据结构

```python
def build_complete_state(phase_id, state_data, include_metadata=True):
    """
    构建完整的状态数据结构（包含元数据）

    Args:
        phase_id: Phase标识
        state_data: 用户提供的状态数据
        include_metadata: 是否包含元数据

    Returns:
        dict: 完整的状态数据
    """
    complete_state = {
        "phase_id": phase_id,
        "state_data": state_data
    }

    if include_metadata:
        complete_state["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "version": "4.3",
            "bmad_version": "v6-alpha",
            "state_schema_version": "1.0",
            "field_count": len(state_data),
            "fields": list(state_data.keys())
        }

    return complete_state
```

### 步骤5: 序列化状态数据

```python
import yaml
import json

def serialize_state_data(state_data, format='yaml'):
    """
    将状态数据序列化为指定格式

    Args:
        state_data: 状态数据
        format: 目标格式 (yaml|json)

    Returns:
        str: 序列化后的字符串

    Raises:
        ValueError: 不支持的格式
    """
    try:
        if format == 'yaml':
            # 使用safe_dump确保安全性
            serialized = yaml.safe_dump(
                state_data,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )
        elif format == 'json':
            # 使用indent=2提高可读性
            serialized = json.dumps(
                state_data,
                ensure_ascii=False,
                indent=2
            )
        else:
            raise ValueError(f"不支持的格式: {format}，必须是 yaml 或 json")

        print(f"✓ 状态数据已序列化为 {format} 格式 ({len(serialized)} 字符)")
        return serialized

    except Exception as e:
        raise RuntimeError(f"序列化失败: {e}")
```

### 步骤6: 🚨 使用Write工具保存文件（带自动重试）

**CRITICAL STEP - 必须实际执行文件写入 + 验证 + 失败重试**

此步骤AI必须调用IDE的Write工具，并在保存后立即验证，失败则自动重试。

**完整保存流程（包含重试逻辑）**：

```python
def save_state_with_retry(file_path, content, max_retries=3):
    """
    保存状态文件，失败时自动重试

    Args:
        file_path: 文件路径
        content: 文件内容
        max_retries: 最大重试次数（默认3次）

    Returns:
        dict: 保存结果

    Raises:
        RuntimeError: 所有重试均失败
    """
    import time

    retry_delays = [1, 5, 10]  # 指数退避：1秒，5秒，10秒

    for attempt in range(max_retries):
        try:
            print(f"🔄 尝试保存文件 (第 {attempt + 1}/{max_retries} 次)...")

            # 1. 🚨 调用Write工具保存文件
            # IDE Tool: Write
            #   file_path: {file_path}
            #   content: {content}
            # 注意：实际执行时，AI必须调用IDE的Write工具，而非Python代码

            # 模拟保存操作（实际中由IDE工具完成）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ 文件写入完成: {file_path}")

            # 2. 立即验证文件已成功保存
            verification = verify_file_saved_immediately(file_path)

            if verification["all_checks_passed"]:
                print(f"✅ 保存成功并验证通过 (尝试 {attempt + 1} 次)")
                return {
                    "success": True,
                    "file_path": file_path,
                    "attempts": attempt + 1,
                    "verification": verification
                }
            else:
                # 验证失败，准备重试
                failed_checks = [k for k, v in verification["checks"].items() if not v]
                print(f"⚠ 验证失败: {failed_checks}")
                raise ValueError(f"验证失败: {failed_checks}")

        except Exception as e:
            print(f"❌ 保存失败 (尝试 {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                # 还有重试机会
                delay = retry_delays[attempt]
                print(f"⏳ {delay}秒后重试...")
                time.sleep(delay)
            else:
                # 所有重试均失败
                error_message = f"""
❌ CRITICAL ERROR: 状态文件保存失败！

文件路径: {file_path}
尝试次数: {max_retries}
最后错误: {e}

可能原因:
1. 磁盘空间不足
2. 文件权限问题
3. 目录不存在或不可写
4. 文件系统故障

建议操作:
1. 检查磁盘剩余空间: df -h
2. 检查目录权限: ls -la {os.path.dirname(file_path)}
3. 检查目录是否存在: ls -d {os.path.dirname(file_path)}
4. 尝试手动创建测试文件: touch {file_path}_test

⛔ 流程已阻断，无法继续执行。请解决上述问题后重新开始。
"""
                raise RuntimeError(error_message)

    # 不应该到达这里
    raise RuntimeError("保存逻辑错误")


def verify_file_saved_immediately(file_path, min_size=50):
    """
    保存后立即验证文件（用于重试逻辑）

    Args:
        file_path: 文件路径
        min_size: 最小文件大小

    Returns:
        dict: 验证结果
    """
    verification = {
        "file_path": file_path,
        "checks": {},
        "all_checks_passed": False
    }

    try:
        # 检查1: 文件存在
        if not os.path.exists(file_path):
            verification["checks"]["exists"] = False
            return verification
        verification["checks"]["exists"] = True

        # 检查2: 是否为文件
        if not os.path.isfile(file_path):
            verification["checks"]["is_file"] = False
            return verification
        verification["checks"]["is_file"] = True

        # 检查3: 文件大小
        file_size = os.path.getsize(file_path)
        if file_size < min_size:
            verification["checks"]["size_valid"] = False
            verification["file_size"] = file_size
            return verification
        verification["checks"]["size_valid"] = True
        verification["file_size"] = file_size

        # 检查4: 文件可读
        with open(file_path, 'r', encoding='utf-8') as f:
            first_char = f.read(1)
            if not first_char:
                verification["checks"]["readable"] = False
                return verification
        verification["checks"]["readable"] = True

        # 检查5: 格式验证
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            import yaml
            yaml.safe_load(content)
        elif file_path.endswith('.json'):
            import json
            json.loads(content)

        verification["checks"]["format_valid"] = True

        # 所有检查通过
        verification["all_checks_passed"] = True
        return verification

    except Exception as e:
        verification["checks"]["exception"] = str(e)
        verification["all_checks_passed"] = False
        return verification
```

**🚨 强制要求**：
- 必须使用 `save_state_with_retry()` 函数，不允许直接保存文件
- 验证失败必须重试，所有重试失败必须阻断流程
- 不允许跳过验证步骤

### 步骤7: 验证结果确认

```python
def verify_file_saved(file_path, min_size=50):
    """
    验证文件已成功保存并符合要求（外部验证接口）

    Args:
        file_path: 文件路径
        min_size: 最小文件大小（bytes）

    Returns:
        dict: 验证结果

    Note:
        此函数是公共接口，调用 verify_file_saved_immediately() 进行实际验证
        区别在于此函数可以抛出异常，而 immediately 版本返回结果字典
    """
    verification = verify_file_saved_immediately(file_path, min_size)

    if not verification["all_checks_passed"]:
        failed_checks = [k for k, v in verification["checks"].items() if not v]
        raise RuntimeError(f"文件验证失败: {failed_checks}")

    print(f"✓ 文件验证通过: {file_path} ({verification.get('file_size', 0)} bytes)")
    return verification
```

### 步骤8: 更新状态清单 (Manifest)

```python
def update_state_manifest(phase_id, file_info, state_folder):
    """
    更新状态文件清单

    Args:
        phase_id: Phase标识
        file_info: 文件信息
        state_folder: 状态目录

    Returns:
        dict: 更新后的清单
    """
    import hashlib

    manifest_path = os.path.join(state_folder, "phase_state_manifest.json")

    # 加载现有清单或创建新清单
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    else:
        manifest = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "phases": {}
        }

    # 计算文件hash
    with open(file_info["file_path"], 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()[:16]

    # 更新清单
    manifest["phases"][phase_id] = {
        "file_path": file_info["file_path"],
        "filename": file_info["filename"],
        "timestamp": file_info["timestamp"],
        "format": file_info["format"],
        "size_bytes": os.path.getsize(file_info["file_path"]),
        "hash": file_hash,
        "saved_at": datetime.now().isoformat()
    }

    manifest["last_updated"] = datetime.now().isoformat()

    # 保存清单
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"✓ 状态清单已更新: {manifest_path}")
    return manifest
```

### 步骤9: 创建"latest"符号链接（可选）

```python
def create_latest_link(file_path, latest_link_path):
    """
    创建指向最新状态文件的符号链接或副本

    Args:
        file_path: 实际文件路径
        latest_link_path: latest链接路径

    Returns:
        bool: 是否成功创建
    """
    try:
        # 如果latest文件已存在，先删除
        if os.path.exists(latest_link_path):
            os.remove(latest_link_path)

        # 在Windows上使用复制，Unix上使用符号链接
        import shutil
        import platform

        if platform.system() == 'Windows':
            shutil.copy2(file_path, latest_link_path)
            print(f"✓ 已创建latest副本: {latest_link_path}")
        else:
            os.symlink(file_path, latest_link_path)
            print(f"✓ 已创建latest符号链接: {latest_link_path}")

        return True
    except Exception as e:
        print(f"⚠ latest链接创建失败（非致命）: {e}")
        return False
```

## 输出

```yaml
outputs:
  saved_state_file:
    type: string
    required: true
    description: '保存的状态文件完整路径'
    example: 'aps-outputs/states/phase_0_state_20251023_143022.yaml'

  verification_result:
    type: object
    required: true
    structure:
      all_checks_passed: boolean
      file_path: string
      file_size: integer
      checks:
        exists: boolean
        is_file: boolean
        size_valid: boolean
        readable: boolean
        format_valid: boolean
    description: '文件验证结果'

  file_metadata:
    type: object
    structure:
      filename: string
      timestamp: string
      format: string
      size_bytes: integer
      hash: string
    description: '文件元数据'

  manifest_updated:
    type: boolean
    description: '状态清单是否已更新'

  latest_link_created:
    type: boolean
    description: 'latest链接是否已创建'
```

## 示例输出

```json
{
  "saved_state_file": "aps-outputs/states/phase_0_state_20251023_143022.yaml",
  "verification_result": {
    "all_checks_passed": true,
    "file_path": "aps-outputs/states/phase_0_state_20251023_143022.yaml",
    "file_size": 1256,
    "checks": {
      "exists": true,
      "is_file": true,
      "size_valid": true,
      "readable": true,
      "format_valid": true
    }
  },
  "file_metadata": {
    "filename": "phase_0_state_20251023_143022.yaml",
    "timestamp": "20251023_143022",
    "format": "yaml",
    "size_bytes": 1256,
    "hash": "a3f5c8d2e1b4f7a9"
  },
  "manifest_updated": true,
  "latest_link_created": true
}
```

## 示例状态文件内容

```yaml
# phase_0_state_20251023_143022.yaml

phase_id: phase_0

state_data:
  confirmed_todo_list:
    - phase: 'Phase 0'
      tasks:
        - '需求理解与初步分析'
        - '生成Todo List'
        - '用户确认Todo List'
        - '初始化TodoTracker'
    - phase: 'Phase 1'
      tasks:
        - '需求深度理解'
        - '用户澄清'
        - 'TodoTracker偏离检测'

  baseline_contract:
    hash: 'e4b3c2a1d5f6'
    similarity_threshold: 0.60
    created_at: '2025-10-23T14:30:22'

  tracker_initialized:
    tracker_id: 'todo_tracker_001'
    baseline_set: true
    deviation_detection_enabled: true

metadata:
  timestamp: '2025-10-23T14:30:22.123456'
  version: '4.3'
  bmad_version: 'v6-alpha'
  state_schema_version: '1.0'
  field_count: 3
  fields:
    - confirmed_todo_list
    - baseline_contract
    - tracker_initialized
```

## 质量检查

执行此任务后，必须确认：

- [ ] 输入参数已验证
- [ ] 状态目录已创建
- [ ] 文件路径已生成
- [ ] 状态数据已序列化
- [ ] 🚨 **Write工具已实际调用并成功**
- [ ] 文件已通过所有验证检查
- [ ] 状态清单已更新
- [ ] latest链接已创建（如适用）
- [ ] 所有输出字段已返回

## 错误处理

### 文件保存失败

```yaml
scenario: Write工具执行失败
action:
  - 记录详细错误信息
  - 重试最多3次（间隔1s, 5s, 10s）
  - 仍失败则抛出异常，阻断workflow
  - 返回错误码和建议
```

### 验证失败

```yaml
scenario: 文件验证不通过
action:
  - 删除不完整文件
  - 记录失败原因
  - 抛出异常，阻断workflow
  - 提示用户检查磁盘空间和权限
```

### 清单更新失败

```yaml
scenario: manifest.json写入失败
action:
  - 记录警告（非致命错误）
  - 文件仍然有效
  - 下次执行时重建清单
```

## 引用

- @编排协调专家库/状态管理规范
- @质量评测专家库/文件验证标准
- BMAD-METHOD v6 架构规范: Workflow状态持久化
- IDE兼容性指南: 跨IDE文件写入

---

**创建**: 2025-10-23
**BMAD版本**: v6-alpha
**核心机制**: 状态持久化 + 强制验证，确保Phase间数据可靠传递
**Token效率**: 减少60-80%上下文传递
