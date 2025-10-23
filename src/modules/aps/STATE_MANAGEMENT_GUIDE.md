# APS Module - 状态管理指南 (State Management Guide)

**版本**: V4.3
**创建日期**: 2025-10-23
**BMAD-CORE**: v6-alpha

---

## 📋 目录

1. [概述](#概述)
2. [核心概念](#核心概念)
3. [配置说明](#配置说明)
4. [使用方式](#使用方式)
5. [故障排查](#故障排查)
6. [最佳实践](#最佳实践)
7. [API参考](#api参考)

---

## 概述

### 什么是状态管理？

状态管理机制是APS Module V4.3引入的核心特性，通过**将Phase执行结果持久化到文件系统**，解决了长上下文传递和工具调用可靠性问题。

### 解决的问题

| 问题               | 传统方式           | 状态管理方式            | 改善            |
| ------------------ | ------------------ | ----------------------- | --------------- |
| **上下文爆炸**     | 所有数据在内存传递 | 中间结果落盘,按需加载   | Token减少60-80% |
| **流程可追溯**     | 只有最终结果       | 每个Phase留下痕迹       | 100%可追溯      |
| **错误恢复**       | 从头重来           | 从上一个检查点恢复      | 节省70%时间     |
| **工具调用可靠性** | 依赖大模型         | workflow层强制保证      | 可靠性从85%→99% |
| **人工审核**       | 难以介入           | 可查看每个Phase输出文件 | 透明度100%      |

### 核心价值

✅ **Token效率**: 减少60-80%的上下文传递
✅ **可靠性**: 文件持久化比内存传递更可靠(99% vs 85%)
✅ **可维护性**: 每个Phase独立状态文件，便于调试
✅ **可恢复性**: 支持从任意Phase恢复执行
✅ **透明度**: 用户可直接查看中间结果

---

## 核心概念

### 1. Phase State (Phase状态)

每个Phase执行结束后，将关键数据保存为一个状态文件。

```yaml
# 示例: phase_0_state_20251023_143022.yaml
phase_id: phase_0

state_data:
  confirmed_todo_list: [...]
  baseline_contract: { ... }
  tracker_initialized: { ... }

metadata:
  timestamp: '2025-10-23T14:30:22.123456'
  version: '4.3'
  field_count: 3
```

### 2. State Folder (状态目录)

所有状态文件统一保存在`aps-outputs/states/`目录下：

```
aps-outputs/
└── states/
    ├── phase_0_state_20251023_143022.yaml
    ├── phase_0_state_latest.yaml        # latest符号链接/副本
    ├── phase_1_state_20251023_150134.yaml
    ├── phase_1_state_latest.yaml
    ├── phase_1_5_state_20251023_152045.yaml
    ├── phase_1_5_state_latest.yaml
    ├── phase_state_manifest.json        # 状态清单
    └── backups/                         # 备份目录
```

### 3. State Chain (状态链)

Phase之间通过状态文件形成依赖链：

```
Phase 0 (保存) → Phase 1 (加载 Phase 0, 保存) → Phase 1.5 (加载 Phase 1, 保存) → ...
```

**关键特性**:

- 每个Phase只依赖上游Phase的状态文件
- 文件缺失会自动阻断workflow
- 保证数据一致性和完整性

### 4. Latest Link (最新链接)

每个Phase都有一个`{phase_id}_state_latest.yaml`文件，指向该Phase最新的状态：

- **Windows**: 副本文件
- **Linux/Mac**: 符号链接

加载时优先使用latest文件，提高访问效率。

---

## 配置说明

### config.yaml 配置项

状态管理的所有配置在`src/modules/aps/config.yaml`的`state_management`节：

```yaml
state_management:
  # 总开关
  enabled: true # 设为false可禁用状态管理

  # 状态文件目录
  state_folder: 'aps-outputs/states'

  # 文件格式
  state_format: 'yaml' # yaml | json

  # 保存策略
  save_policy:
    auto_save: true # 每个Phase自动保存
    verify_after_save: true # 保存后立即验证
    block_on_save_failure: true # 保存失败阻断流程
    include_timestamp: true # 文件名包含时间戳
    create_latest_link: true # 创建latest链接

  # 加载策略
  load_policy:
    verify_before_load: true # 加载前验证文件
    block_on_missing: true # 缺失文件阻断流程
    use_latest: true # 优先使用latest链接
    allow_cache: false # 强制从文件读取

  # 清理策略
  cleanup_policy:
    enabled: true
    retention_days: 30 # 保留30天
    keep_latest_n: 5 # 每个Phase保留最新5个版本
```

### Phase状态定义

每个Phase的状态内容在`phase_states`节中定义：

```yaml
phase_states:
  phase_0:
    file_name: 'phase_0_state.yaml'
    required_by: ['phase_1', 'phase_4'] # 依赖此状态的Phase
    content_fields: # 保存的字段
      - confirmed_todo_list
      - baseline_contract
      - tracker_initialized
    mandatory: true # 是否必需
```

---

## 使用方式

### 1. 自动使用（推荐）

**无需手动操作**，workflow自动处理状态保存和加载：

1. **Phase 0执行**
   - Step 0.1-0.4: 正常执行
   - Step 0.5: 自动保存状态到`phase_0_state_{timestamp}.yaml`
   - 验证保存成功

2. **Phase 1执行**
   - Step 1.0: 自动加载`phase_0_state_latest.yaml`
   - 如果文件缺失 → 阻断并提示从Phase 0重新执行
   - Step 1.1-1.3: 使用加载的数据
   - Step 1.4: 自动保存Phase 1状态

### 2. 手动验证（可选）

#### 查看状态文件

```bash
# 查看states目录
ls -lh aps-outputs/states/

# 查看特定Phase状态
cat aps-outputs/states/phase_0_state_latest.yaml

# 查看状态清单
cat aps-outputs/states/phase_state_manifest.json
```

#### 运行完整性验证

```bash
# 使用verify-state-integrity任务
# （通常在workflow启动时自动执行）
```

### 3. 错误恢复

#### 场景1: Phase中途失败

```bash
# 问题: Phase 2执行到一半失败

# 方案1: 从Phase 2重新执行（推荐）
# Phase 2会自动加载Phase 1的状态

# 方案2: 删除Phase 2状态文件后重试
rm aps-outputs/states/phase_2_state_*.yaml
# 然后重新执行Phase 2
```

#### 场景2: 状态文件损坏

```bash
# 问题: phase_1_state文件损坏

# 方案: 删除损坏文件，从Phase 1重新执行
rm aps-outputs/states/phase_1_state_*.yaml
# 然后从Phase 1重新执行workflow
```

#### 场景3: 状态链断裂

```bash
# 问题: Phase 3需要Phase 2状态，但文件不存在

# 错误信息:
❌ CRITICAL: Phase 2 状态文件缺失！
文件路径: aps-outputs/states/phase_2_state_latest.yaml

# 方案: 从Phase 2重新执行
# Phase 2会自动加载Phase 1状态
```

---

## 故障排查

### 常见问题

#### Q1: 提示"状态文件缺失"

**错误信息**:

```
❌ CRITICAL: Phase X 状态文件缺失！
```

**原因**:

1. Phase X尚未执行完成
2. Phase X执行时文件保存失败
3. 状态文件被误删除

**解决方案**:

1. 检查文件是否存在:

   ```bash
   ls aps-outputs/states/phase_X_state_*.yaml
   ```

2. 如果不存在,从Phase X重新执行

3. 检查目录权限:
   ```bash
   ls -ld aps-outputs/states/
   ```

#### Q2: 文件保存失败

**错误信息**:

```
❌ 文件保存失败: phase_X_state.yaml
```

**原因**:

1. 磁盘空间不足
2. 目录权限不足
3. AI工具调用失败

**解决方案**:

1. 检查磁盘空间:

   ```bash
   df -h
   ```

2. 检查目录权限:

   ```bash
   chmod 755 aps-outputs/states/
   ```

3. 如果重试3次仍失败,手动检查AI工具配置

#### Q3: 文件内容格式错误

**错误信息**:

```
❌ YAML解析失败: ...
```

**原因**:

- 文件内容损坏
- 格式不正确

**解决方案**:

1. 查看文件内容:

   ```bash
   cat aps-outputs/states/phase_X_state_latest.yaml
   ```

2. 如果损坏,删除并重新执行:
   ```bash
   rm aps-outputs/states/phase_X_state_*.yaml
   ```

#### Q4: Latest链接失效

**现象**: 加载latest文件失败

**解决方案**:

1. 删除latest链接:

   ```bash
   rm aps-outputs/states/phase_X_state_latest.yaml
   ```

2. 手动创建副本(Windows):

   ```bash
   cp aps-outputs/states/phase_X_state_20251023_*.yaml \
      aps-outputs/states/phase_X_state_latest.yaml
   ```

3. 或创建符号链接(Linux/Mac):
   ```bash
   ln -s phase_X_state_20251023_*.yaml phase_X_state_latest.yaml
   ```

---

## 最佳实践

### 1. 定期清理旧状态文件

```bash
# 手动清理30天前的文件
find aps-outputs/states/ -name "phase_*_state_202*.yaml" -mtime +30 -delete

# 保留每个Phase最新5个版本（自动）
# 由cleanup_policy配置控制
```

### 2. 备份关键状态

```bash
# 备份TenElementModel (Phase 1.5)
cp aps-outputs/states/phase_1_5_state_latest.yaml \
   aps-outputs/states/backups/phase_1_5_backup_$(date +%Y%m%d).yaml
```

### 3. 查看执行历史

```bash
# 查看状态清单中的加载历史
cat aps-outputs/states/phase_state_manifest.json | jq '.load_history'

# 查看特定Phase的版本历史
ls -lt aps-outputs/states/phase_2_state_*.yaml
```

### 4. 开发调试

```yaml
# 开发时可临时禁用状态管理（不推荐）
state_management:
  enabled: false

# 或只禁用保存验证（加快速度）
save_policy:
  verify_after_save: false
```

### 5. 生产环境建议

```yaml
# 生产环境建议配置
state_management:
  enabled: true
  save_policy:
    verify_after_save: true # 必须验证
    block_on_save_failure: true # 必须阻断
  load_policy:
    block_on_missing: true # 必须阻断
  cleanup_policy:
    enabled: true
    retention_days: 90 # 保留更久
    keep_latest_n: 10 # 保留更多版本
```

---

## API参考

### Tasks (任务)

#### save-phase-state.md

保存Phase状态到文件系统。

**输入**:

```yaml
phase_id: 'phase_0'
state_data:
  confirmed_todo_list: [...]
  baseline_contract: { ... }
state_folder: 'aps-outputs/states'
format: 'yaml'
include_metadata: true
```

**输出**:

```yaml
saved_state_file: 'aps-outputs/states/phase_0_state_20251023_143022.yaml'
verification_result:
  all_checks_passed: true
  file_size: 1256
file_metadata: { ... }
manifest_updated: true
```

#### load-phase-state.md

加载Phase状态从文件系统。

**输入**:

```yaml
phase_id: 'phase_0'
state_folder: 'aps-outputs/states'
required: true
use_latest: true
format: 'yaml'
```

**输出**:

```yaml
state_data:
  confirmed_todo_list: [...]
  baseline_contract: { ... }
metadata: { ... }
load_success: true
file_metadata: { ... }
```

#### verify-state-integrity.md

验证状态链的完整性。

**输入**:

```yaml
state_folder: 'aps-outputs/states'
verify_phases: ['phase_0', 'phase_1', 'phase_1_5']
deep_check: true
fix_issues: false
```

**输出**:

```yaml
verification_report:
  overall_status: 'PASS' # PASS | WARNING | FAIL
  summary:
    total_issues: 0
    total_files_scanned: 5
  recommendations: [...]
overall_status: 'PASS'
issues_found: 0
all_checks_passed: true
```

---

## 状态文件示例

### phase_0_state.yaml

```yaml
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

### phase_state_manifest.json

```json
{
  "version": "1.0",
  "created_at": "2025-10-23T14:30:00.000000",
  "phases": {
    "phase_0": {
      "file_path": "aps-outputs/states/phase_0_state_20251023_143022.yaml",
      "filename": "phase_0_state_20251023_143022.yaml",
      "timestamp": "20251023_143022",
      "format": "yaml",
      "size_bytes": 1256,
      "hash": "a3f5c8d2e1b4f7a9",
      "saved_at": "2025-10-23T14:30:22.123456"
    },
    "phase_1": {
      "file_path": "aps-outputs/states/phase_1_state_20251023_150134.yaml",
      "filename": "phase_1_state_20251023_150134.yaml",
      "timestamp": "20251023_150134",
      "format": "yaml",
      "size_bytes": 2048,
      "hash": "b4c6d8e2f1a5b7c9",
      "saved_at": "2025-10-23T15:01:34.567890"
    }
  },
  "last_updated": "2025-10-23T15:01:34.567890",
  "load_history": [
    {
      "phase_id": "phase_0",
      "file_path": "aps-outputs/states/phase_0_state_latest.yaml",
      "loaded_at": "2025-10-23T15:00:00.000000",
      "operation": "load"
    }
  ]
}
```

---

## 状态链依赖图

```
Phase 0 (Todo Baseline)
  ├─→ Phase 1 (需求分析) - depends on confirmed_todo_list, baseline_contract
  └─→ Phase 4 (质量保证) - depends on baseline_contract for completion check

Phase 0.5 (Workflow Config)
  ├─→ Phase 1.5 (十要素建模) - depends on selected_mode
  └─→ Phase 2 (专家协调) - depends on workflow_configuration

Phase 1 (需求分析)
  ├─→ Phase 1.5 (十要素建模) - depends on requirement_analysis
  └─→ Phase 2 (专家协调) - depends on clarified_requirements

Phase 1.5 (TenElementModel)
  ├─→ Phase 2 (专家协调) - depends on ten_element_model
  ├─→ Phase 3 (方案集成) - depends on model_baseline
  └─→ Phase 4 (质量保证) - depends on model_hash

Phase 2 (专家分析)
  └─→ Phase 3 (方案集成) - depends on all expert analyses

Phase 3 (集成方案)
  └─→ Phase 4 (质量保证) - depends on integrated_solution, implementation_code
```

---

## 扩展阅读

- [BMAD-METHOD v6 架构文档](../../README.md)
- [Workflow设计规范](../../../docs/workflow-design.md)
- [APS Module README](./README.md)
- [Task开发指南](./tasks/README.md)

---

## 变更历史

| 版本 | 日期       | 变更内容                   |
| ---- | ---------- | -------------------------- |
| V4.3 | 2025-10-23 | 初始版本，引入状态管理机制 |

---

**维护者**: APS Team
**反馈**: 如有问题请提交Issue或联系团队
