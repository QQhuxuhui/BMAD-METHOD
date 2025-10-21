# APS Tasks

单一操作任务定义目录，供workflow调用的原子级任务。

## 任务概览

Tasks是workflow的基本执行单元，每个task执行一个特定的、明确的操作。

### 核心任务（已创建）

| 任务文件                        | 用途           | Phase     | 状态 |
| ------------------------------- | -------------- | --------- | ---- |
| `generate-todo-list.md`         | 生成Todo List  | Phase 0   | ✅   |
| `check-todo-deviation.md`       | 偏离检测       | Phase 0-4 | ✅   |
| `validate-ten-element-model.md` | 十要素模型验证 | Phase 1.5 | ✅   |
| `quality-gate-check.md`         | 质量门禁判断   | Phase 4   | ✅   |

### 待创建任务

**Phase 0相关**:

- [ ] `analyze-user-request.md` - 初步需求分析
- [ ] `initialize-todo-tracker.md` - 初始化追踪器
- [ ] `present-interaction-modes.md` - 呈现模式对比
- [ ] `configure-workflow-mode.md` - 配置工作流模式

**Phase 1相关**:

- [ ] `requirement-deep-analysis.md` - 深度需求理解
- [ ] `generate-clarification-questions.md` - 生成澄清问题

**Phase 1.5相关**:

- [ ] `extract-ten-elements.md` - 提取十要素
- [ ] `draft-ten-element-model.md` - 起草模型
- [ ] `finalize-ten-element-model.md` - 固化模型
- [ ] `generate-model-documentation.md` - 生成模型文档

**Phase 2相关**:

- [ ] `call-domain-expert.md` - 调用领域专家
- [ ] `call-constraint-expert.md` - 调用约束专家
- [ ] `call-objective-expert.md` - 调用目标专家
- [ ] `call-algorithm-expert.md` - 调用算法专家
- [ ] `cross-expert-consistency-check.md` - 跨专家一致性

**Phase 3相关**:

- [ ] `integrate-expert-analyses.md` - 融合专家分析
- [ ] `final-consistency-check.md` - 最终一致性检查
- [ ] `generate-complete-code.md` - 生成完整代码

**Phase 4相关**:

- [ ] `syntax-check.md` - 语法检查
- [ ] `logic-verification.md` - 逻辑验证
- [ ] `consistency-check.md` - 一致性检查
- [ ] `benchmark-evaluation.md` - 基准评测
- [ ] `check-todo-completion.md` - Todo完成度检查

**通用任务**:

- [ ] `show-todo-progress.md` - 显示Todo进度
- [ ] `call-specialist.md` - 调用专家（通用）
- [ ] `capability-gap-report.md` - 能力缺口报告
- [ ] `update-todo-progress.md` - 更新Todo进度

## 任务文件结构

每个任务文件应包含：

````markdown
# Task: [任务名称]

**任务ID**: `task-id`
**版本**: V4.3
**用途**: [简要说明]

## 输入

```yaml
inputs:
  - input_1: 描述
  - input_2: 描述
```
````

## 处理逻辑

### 步骤1: [步骤名]

[详细说明]

### 步骤2: [步骤名]

[详细说明]

## 输出

```yaml
outputs:
  output_1:
    type: string
    description: 描述
```

## 示例

[输入输出示例]

## 质量检查

- [ ] 检查项1
- [ ] 检查项2

## 引用

- @知识模块库/...
- @专家库/...

---

**创建**: 2025-10-20
**BMAD版本**: v6-alpha

````

## 任务分类

### 1. 数据处理任务
- 提取、转换、验证数据
- 示例：`extract-ten-elements`, `parse-user-request`

### 2. 验证任务
- 检查、验证、评估
- 示例：`validate-ten-element-model`, `quality-gate-check`

### 3. 协调任务
- 调用agent、workflow
- 示例：`call-domain-expert`, `orchestrate-phase-2`

### 4. 报告任务
- 生成报告、文档、可视化
- 示例：`generate-model-documentation`, `capability-gap-report`

### 5. 追踪任务
- 状态更新、进度追踪
- 示例：`update-todo-progress`, `check-todo-deviation`

## Workflow调用方式

### 方式1: exec动作

```yaml
- step_id: '1.1'
  name: '生成Todo List'
  action: 'exec'
  target: 'bmad/aps/tasks/generate-todo-list.md'
  inputs:
    - user_request
    - initial_understanding
  outputs:
    - todo_items
    - estimated_timeline
````

### 方式2: Agent命令调用

```yaml
- step_id: '4.1'
  name: '质量验证'
  action: 'exec'
  agent: 'bmad/aps/agents/quality-evaluator.md'
  command: '*validate-all'
  inputs:
    - complete_code
```

### 方式3: 条件执行

```yaml
- step_id: '1.2'
  name: '需求澄清'
  action: 'conditional_exec'
  condition: 'confidence < 0.70'
  target: 'bmad/aps/tasks/generate-clarification-questions.md'
```

## 任务开发指南

### 创建新任务

1. **确定任务范围**
   - 单一职责原则
   - 明确输入输出
   - 可独立测试

2. **编写任务文件**
   - 使用标准模板
   - 详细描述处理逻辑
   - 提供示例

3. **添加引用**
   - 引用相关知识库
   - 标注依赖

4. **质量检查**
   - 逻辑清晰
   - 可执行性
   - 错误处理

### 任务命名规范

- 使用kebab-case：`generate-todo-list`
- 动词开头：`check-`, `generate-`, `validate-`
- 描述性：清晰说明任务做什么

### 任务复杂度

**简单任务** (< 5步骤):

- 单一数据转换
- 简单验证
- 状态更新

**中等任务** (5-10步骤):

- 多步骤处理
- 条件分支
- 聚合计算

**复杂任务** (> 10步骤):

- 应拆分为多个任务
- 或提升为workflow

## 质量标准

所有任务必须满足：

- [ ] 输入输出明确定义
- [ ] 处理逻辑详细说明
- [ ] 包含示例
- [ ] 错误处理完整
- [ ] 引用完整（Guardrails）
- [ ] 可测试性

## 测试建议

每个任务应配备：

1. **单元测试**
   - 测试各步骤逻辑
   - 边界条件测试
   - 错误处理测试

2. **集成测试**
   - 在workflow中测试
   - 验证输入输出对接
   - 端到端流程测试

3. **性能测试**
   - 大规模数据测试
   - 时间复杂度验证

## 参考资源

- [Workflow README](../workflows/README.md)
- [APS Module README](../README.md)
- [BMAD Task Patterns](../../bmm/tasks/)

---

**版本**: V4.3
**最后更新**: 2025-10-20
**维护**: APS Team
