# APS Module - IDE Compatibility Guide

## 问题描述

APS 模块在不同 IDE 中测试时，发现交付物落地行为存在差异：

- **Claude Code** ✅ 交付物可以成功保存到输出目录
- **Trae** ✅ 交付物可以成功保存到输出目录
- **Cursor** ❌ 交付物无法落地，文件未保存

## 根本原因

### 1. 隐式指令 vs 显式工具调用

**原有设计**：在 `tasks/generate-complete-code.md` 中，文件保存逻辑使用 Python 代码示例描述：

```python
# 原有写法（隐式指令）
with open(code_path, 'w', encoding='utf-8') as f:
    f.write(generate_complete_code(...))
```

这种写法的问题：
- **Claude Code/Trae**: 能够理解隐式意图，自动使用 `Write` 工具保存文件 ✅
- **Cursor**: 可能将其理解为"输出示例代码"而非"执行文件保存操作" ❌

### 2. 缺少明确的 IDE 工具调用指令

不同 IDE 对 AI 的指令理解方式不同：
- **Claude Code**: 高度智能化，能理解隐式意图并自动选择工具
- **Cursor**: 需要更明确的工具调用指令

## 解决方案

### v4.4 更新（2025-10-22）

在源文件 `src/modules/aps/tasks/generate-complete-code.md` 中添加了**明确的 IDE 工具调用指令**：

#### 1. 新增"IDE 工具调用指令"章节

```markdown
### 1.1 IDE 工具调用指令（跨 IDE 兼容）

**🚨 CRITICAL - 文件保存方法**：

不同 IDE 中，AI 必须使用 IDE 提供的**文件写入工具**来保存文件，而不是输出 Python 代码示例。

**指令**：
1. **Claude Code/Cursor/Windsurf/其他 IDE**: 使用 `Write` 工具保存文件
2. **文件路径**: 必须使用完整的绝对路径或项目相对路径
3. **保存顺序**: 按照以下顺序逐个保存，每保存一个文件后验证成功
```

#### 2. 修改"保存所有文件"步骤

**原有（隐式）**:
```python
def save_all_deliverables(...):
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(...)
```

**新版（显式）**:
```markdown
**🚨 CRITICAL INSTRUCTIONS - 文件保存执行步骤**：

此步骤必须实际执行文件保存操作，而非仅输出代码。所有 AI 必须：

1. **使用 IDE 提供的 Write 工具**，不得使用 Python 代码示例替代
2. **按顺序保存**以下所有文件
3. **每保存一个文件后立即验证**文件已成功创建

#### 3.2 使用 Write 工具保存文件

**文件 1: 完整代码**
```
IDE Tool: Write
File Path: {output_folder}/models/scheduling_solution_{timestamp}.py
Content: [生成的完整调度算法 Python 代码]
```
```

#### 3. Orchestrator 规则更新

在 `orchestrator.agent.yaml` 中添加了明确的文件保存规则：

```yaml
- 🚨 FILE SAVING RULE: When tasks require saving files, you MUST use the
  IDE's Write tool to actually save files. Do NOT only output Python code
  examples. For all IDEs (Claude Code, Cursor, Windsurf, etc.), use the
  Write tool with full file paths.
```

## 验证测试

### 测试场景

1. **安装 APS 模块**到测试项目
2. **启动完整调度流程** (`*start-scheduling`)
3. **Phase 3.3** 执行 "生成完整代码并保存"
4. **检查输出目录**是否包含以下文件：
   - `{output_folder}/models/scheduling_solution_{timestamp}.py`
   - `{output_folder}/models/ten_element_model_{timestamp}.yaml`
   - `{output_folder}/docs/solution_documentation_{timestamp}.md`
   - `{output_folder}/file_manifest_{timestamp}.json`

### 预期结果

在所有 IDE（Claude Code、Trae、Cursor、Windsurf）中：
- ✅ 所有交付物文件成功保存到输出目录
- ✅ Phase 4.1.5 验证通过（所有必需交付物已保存）
- ✅ Phase 4.2 质量门禁6 通过（deliverables_saved: true）

## 技术细节

### IDE 工具使用差异

| IDE | Write 工具支持 | 隐式意图理解 | 需要显式指令 |
|-----|---------------|-------------|-------------|
| Claude Code | ✅ 完全支持 | ✅ 强 | ❌ 否 |
| Trae | ✅ 完全支持 | ✅ 强 | ❌ 否 |
| Cursor | ✅ 完全支持 | ⚠️ 中等 | ✅ 是 |
| Windsurf | ✅ 完全支持 | ⚠️ 待测试 | ✅ 推荐 |

### 最佳实践

**为了最大化跨 IDE 兼容性，在编写 Task 文件时：**

1. **明确工具调用**：使用 `IDE Tool: Write` 格式明确指示
2. **避免隐式依赖**：不要依赖 AI 的隐式理解能力
3. **分步验证**：每保存一个文件后验证成功
4. **清晰路径**：使用完整的相对路径或绝对路径

**示例（推荐）**：
```markdown
### 步骤: 保存文件

**🚨 CRITICAL**: 使用 Write 工具保存文件

**文件 1**:
```
IDE Tool: Write
File Path: {output_folder}/models/solution.py
Content: [完整代码]
```
```

**示例（不推荐）**：
```python
# 不推荐：隐式指令
with open(f"{output_folder}/models/solution.py", 'w') as f:
    f.write(code)
```

## 版本历史

- **v4.4** (2025-10-22): 添加明确的 IDE 工具调用指令，修复 Cursor 兼容性问题
- **v4.3** (2025-10-21): 原始版本，使用 Python 代码示例描述保存逻辑

## 相关文件

- 源文件: `src/modules/aps/tasks/generate-complete-code.md`
- 分发版: `bmad/aps/tasks/generate-complete-code.md`
- Orchestrator: `src/modules/aps/agents/orchestrator.agent.yaml`
- Workflow: `src/modules/aps/workflows/scheduling-orchestration/workflow.yaml`

---

**BMAD-METHOD v6 - APS Module**
**Architecture Compliance: ✅ v6 Standards**
