# Task: Generate Todo List

**任务ID**: `generate-todo-list`
**版本**: V4.3
**用途**: Phase 0 - 从用户需求生成结构化Todo List

## 输入

```yaml
inputs:
  - user_request: 用户的原始调度需求描述
  - initial_understanding: Phase 0初步分析结果
```

## 处理逻辑

### 步骤1: 需求分解

分析用户需求，识别关键任务和里程碑：

```
用户需求 → 任务分解
  ├─ 识别主要Phase (Phase 0-4)
  ├─ 提取关键决策点
  ├─ 识别专家调用需求
  └─ 估算时间成本
```

### 步骤2: 任务结构化

按照Phase组织任务：

**Phase 0: 任务规划**

- [ ] 需求理解与初步分析
- [ ] 生成Todo List
- [ ] 用户确认Todo List
- [ ] 初始化TodoTracker

**Phase 0.5: 双模式交互选择**

- [ ] 呈现模式对比
- [ ] 用户选择交互模式
- [ ] 配置工作流

**Phase 1: 需求分析**

- [ ] 需求深度理解
- [ ] 用户澄清（如需要）
- [ ] TodoTracker偏离检测

**Phase 1.5: 十要素建模**

- [ ] 初步建模
- [ ] 用户确认TenElementModel
- [ ] 固化TenElementModel

**Phase 2: 专家协调**

- [ ] 调用领域专家
- [ ] 调用约束专家
- [ ] 调用目标专家
- [ ] 调用算法专家
- [ ] 跨专家一致性校验

**Phase 3: 方案集成**

- [ ] 方案融合
- [ ] 一致性最终检查
- [ ] 生成完整代码

**Phase 4: 质量保证**

- [ ] 质量全面验证
- [ ] 质量门禁判断
- [ ] Todo完成度检查
- [ ] 交付确认

### 步骤3: 添加任务属性

为每个任务标注：

```yaml
task_attributes:
  priority: P0 | P1 | P2 | P3 | P4
  estimated_duration: 时间估算（分钟）
  dependencies: 依赖的前置任务
  success_criteria: 成功标准
  human_confirmation_required: true | false
```

### 步骤4: 时间估算

基于用户选择的模式（如已知）或双模式预估：

```yaml
estimated_timeline:
  mode_a:
    total_time: '70-95分钟'
    phase_breakdown:
      phase_0: '5-8分钟'
      phase_0.5: '2-3分钟'
      phase_1: '10-15分钟'
      phase_1.5: '10-15分钟'
      phase_2: '10-15分钟'
      phase_3: '15-20分钟'
      phase_4: '9-12分钟'

  mode_b:
    total_time: '95-130分钟'
    phase_breakdown:
      phase_0: '5-8分钟'
      phase_0.5: '2-3分钟'
      phase_1: '10-15分钟'
      phase_1.5: '5-8分钟'
      phase_2: '31-48分钟'
      phase_3: '15-20分钟'
      phase_4: '9-12分钟'
```

### 步骤5: 依赖关系映射

```yaml
dependencies:
  phase_1: [phase_0, phase_0.5]
  phase_1.5: [phase_1]
  phase_2: [phase_1.5]
  phase_3: [phase_2]
  phase_4: [phase_3]
```

## 输出

```yaml
outputs:
  todo_items:
    type: array
    structure:
      - phase: 'Phase ID'
        phase_name: 'Phase名称'
        tasks:
          - task_id: '任务ID'
            task_name: '任务名称'
            priority: 'P0-P4'
            estimated_duration: '时间（分钟）'
            dependencies: ['依赖任务ID']
            success_criteria: '成功标准'
            human_confirmation: boolean

  estimated_timeline:
    type: object
    structure:
      mode_a: { ... }
      mode_b: { ... }

  dependencies:
    type: object
    description: '任务依赖关系图'
```

## 示例输出

```json
{
  "todo_items": [
    {
      "phase": "phase-0",
      "phase_name": "Phase 0: 任务规划",
      "estimated_time": "5-8分钟",
      "tasks": [
        {
          "task_id": "task-0.1",
          "task_name": "需求理解与初步分析",
          "priority": "P0",
          "estimated_duration": "2-3分钟",
          "dependencies": [],
          "success_criteria": "明确问题域和关键需求",
          "human_confirmation": false
        },
        {
          "task_id": "task-0.2",
          "task_name": "生成Todo List",
          "priority": "P0",
          "estimated_duration": "1-2分钟",
          "dependencies": ["task-0.1"],
          "success_criteria": "完整任务清单生成",
          "human_confirmation": false
        },
        {
          "task_id": "task-0.3",
          "task_name": "用户确认Todo List",
          "priority": "P0",
          "estimated_duration": "2-3分钟",
          "dependencies": ["task-0.2"],
          "success_criteria": "用户确认并形成执行合同",
          "human_confirmation": true
        }
      ]
    }
  ],
  "estimated_timeline": {
    "mode_a": {
      "total": "70-95分钟",
      "confidence": 0.85
    },
    "mode_b": {
      "total": "95-130分钟",
      "confidence": 0.8
    }
  }
}
```

## 质量检查

- [ ] 所有Phase都有对应任务
- [ ] 关键决策点标记为P0
- [ ] 时间估算合理
- [ ] 依赖关系无循环
- [ ] 成功标准明确可验证

## 引用

- @知识模块库/任务规划模板
- @编排协调专家库/Phase分解方法论

---

**创建**: 2025-10-20
**BMAD版本**: v6-alpha
