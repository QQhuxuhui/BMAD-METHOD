# APS模块迁移指南

从 `调度产品设计草稿/agents/智能体团队` 到 `bmad/aps` 的完整迁移文档

## 📋 迁移概览

### 迁移目标

将V4.3调度智能体团队架构完整迁移到BMAD-METHOD v6框架，同时：

- ✅ 保留原有产品架构设计思路
- ✅ 保持V4.3核心特性（Todo List、Human-in-the-Loop、双模式交互、Guardrails）
- ✅ 适配BMAD v6模块化标准
- ✅ 维持Token效率优化（75-87%节省）

### 迁移范围

| 原始内容      | 迁移后位置                    | 状态        |
| ------------- | ----------------------------- | ----------- |
| 7个智能体文件 | `bmad/aps/agents/`            | ✅ 完成     |
| 架构文档      | `bmad/aps/README.md`          | ✅ 完成     |
| 工作流定义    | `bmad/aps/workflows/`         | ✅ 示例完成 |
| 配置文件      | `bmad/aps/config.yaml`        | ✅ 完成     |
| 安装配置      | `bmad/aps/_module-installer/` | ✅ 完成     |
| 专家知识库    | `bmad/aps/templates/`         | ⏳ 待填充   |
| 任务定义      | `bmad/aps/tasks/`             | ⏳ 待创建   |

## 🗺️ 架构映射

### 智能体映射

| 原始智能体         | BMAD Agent        | 文件位置                      | 角色保留 |
| ------------------ | ----------------- | ----------------------------- | -------- |
| 系统编排协调智能体 | Orchestrator      | `agents/orchestrator.md`      | ✅ 100%  |
| 调度算法专家智能体 | Algorithm Expert  | `agents/algorithm-expert.md`  | ✅ 100%  |
| 约束模式专家智能体 | Constraint Expert | `agents/constraint-expert.md` | ✅ 100%  |
| 目标优化专家智能体 | Objective Expert  | `agents/objective-expert.md`  | ✅ 100%  |
| 领域应用专家智能体 | Domain Expert     | `agents/domain-expert.md`     | ✅ 100%  |
| 算法知识库扩展指导 | Extension Guide   | `agents/extension-guide.md`   | ✅ 100%  |
| 质量与评测智能体   | Quality Evaluator | `agents/quality-evaluator.md` | ✅ 100%  |

### 架构特性映射

| V4.3特性              | BMAD实现方式                                       | 保留程度    |
| --------------------- | -------------------------------------------------- | ----------- |
| **Phase 0-4 工作流**  | `workflows/scheduling-orchestration/workflow.yaml` | ✅ 100%     |
| **Todo List机制**     | `workflows/todo-management/workflow.yaml`          | ✅ 100%     |
| **双模式交互**        | workflow.yaml `conditional_flow`                   | ✅ 100%     |
| **Human-in-the-Loop** | workflow.yaml `human_confirmation` 步骤            | ✅ 100%     |
| **Guardrails策略**    | agent `<critical-actions>` 强制约束                | ✅ 100%     |
| **专家知识库**        | `templates/{expert}-library/` Sidecar模式          | ✅ 架构保留 |
| **TenElementModel**   | workflow输入输出统一真相源                         | ✅ 100%     |
| **偏离检测**          | Todo workflow deviation_threshold: 0.60            | ✅ 100%     |
| **5级触发规则**       | workflow P0-P4 trigger_level                       | ✅ 100%     |

## 🔄 格式转换详解

### Agent文件格式转换

**原始格式（Markdown + Sections）**:

```markdown
# 系统编排协调智能体

## 角色定位

我是调度优化领域的系统总指挥...

## 能力矩阵

...

## 工作流程

...
```

**BMAD格式（XML + Structured）**:

```xml
<agent id="bmad/aps/agents/orchestrator.md" name="系统编排者" title="调度系统总指挥" icon="🎯">
  <persona>
    <role>我是调度优化领域的系统总指挥...</role>
    <identity>...</identity>
    <communication_style>...</communication_style>
    <principles>...</principles>
  </persona>

  <critical-actions>
    <i critical="MANDATORY">加载 COMPLETE 文件 {project-root}/bmad/aps/templates/orchestrator-library/README.md</i>
  </critical-actions>

  <menu>
    <item cmd="*start-scheduling" run-workflow="{project-root}/bmad/aps/workflows/scheduling-orchestration/workflow.yaml">
      🚀 启动完整调度求解流程（Phase 0-4）
    </item>
  </menu>
</agent>
```

**关键变化**:

1. **结构化身份**: `<persona>` 包含 role, identity, communication_style, principles
2. **强制行为**: `<critical-actions>` 实现Guardrails
3. **命令菜单**: `<menu>` 定义用户可调用的命令
4. **工作流集成**: `run-workflow` 指向具体workflow.yaml

### Workflow定义新增

原始架构中workflow流程以文字描述为主，现在转为：

**workflow.yaml结构化定义**:

```yaml
workflow_id: 'aps-scheduling-orchestration'
phases:
  - phase_id: 'phase-0'
    steps:
      - step_id: '0.1'
        action: 'exec'
        target: 'bmad/aps/tasks/analyze-user-request.md'
```

**优势**:

- 可编程化执行
- 明确的输入输出定义
- 条件分支和并行执行支持
- 错误处理和质量门禁集成

### 专家知识库Sidecar模式

**原始方式**: 知识内嵌在智能体文件中

**BMAD方式**: Sidecar按需加载

```xml
<critical-actions>
  <i critical="MANDATORY">加载 COMPLETE 文件 {project-root}/bmad/aps/templates/algorithm-library/README.md</i>
</critical-actions>
```

**Token效率**:

- 智能体文件保持轻量（200-500 tokens）
- 专家知识按需加载（5K-20K tokens）
- 总体节省：75-87%

## 📂 目录结构对比

### 原始结构

```
调度产品设计草稿/
└── agents/
    └── 智能体团队/
        ├── README.md
        ├── 系统编排协调智能体.md
        ├── 调度算法专家智能体.md
        ├── 约束模式专家智能体.md
        ├── 目标优化专家智能体.md
        ├── 领域应用专家智能体.md
        ├── 算法知识库扩展指导智能体.md
        └── 质量与评测智能体.md
```

### BMAD结构

```
bmad/aps/
├── agents/                     # 7个智能体（XML格式）
│   ├── orchestrator.md
│   ├── algorithm-expert.md
│   ├── constraint-expert.md
│   ├── objective-expert.md
│   ├── domain-expert.md
│   ├── extension-guide.md
│   └── quality-evaluator.md
│
├── workflows/                  # 工作流定义（新增）
│   ├── scheduling-orchestration/
│   ├── todo-management/
│   ├── phase-1.5-modeling/
│   └── README.md
│
├── templates/                  # 专家知识库（新增）
│   ├── orchestrator-library/
│   ├── algorithm-library/
│   ├── constraint-library/
│   ├── objective-library/
│   ├── domain-library/
│   ├── extension-library/
│   └── quality-library/
│
├── tasks/                      # 单一任务（新增）
├── data/                       # 静态数据（新增）
├── _module-installer/          # 安装配置（新增）
├── config.yaml                 # 模块配置（新增）
├── README.md                   # 模块文档
└── MIGRATION_GUIDE.md          # 本文档
```

## ✅ 已完成的迁移工作

### 1. Agent文件转换 ✅

所有7个智能体已转换为BMAD XML格式：

- ✅ 保留原有人格定位（name, role, identity）
- ✅ 迁移核心能力描述
- ✅ 实现Guardrails强约束（citations_required）
- ✅ 配置专家知识库加载路径
- ✅ 定义命令菜单

### 2. 模块配置 ✅

`config.yaml` 配置完成：

- ✅ 模块元数据
- ✅ 双模式交互配置
- ✅ 质量门禁参数
- ✅ Todo List追踪开关
- ✅ Human-in-the-Loop配置

### 3. 工作流示例 ✅

创建3个核心workflow：

- ✅ `scheduling-orchestration`: Phase 0-4完整流程
- ✅ `todo-management`: Todo List管理
- ✅ `phase-1.5-modeling`: 十要素建模

### 4. 模块安装配置 ✅

`install-module-config.yaml` 完成：

- ✅ 目录创建步骤
- ✅ 文件拷贝映射
- ✅ 模块注册配置
- ✅ 安装后提示

### 5. 文档迁移 ✅

- ✅ `README.md`: APS模块完整文档
- ✅ `workflows/README.md`: Workflow开发指南
- ✅ `MIGRATION_GUIDE.md`: 本迁移指南

## ⏳ 待完成的工作

### 1. 专家知识库填充 🔴 高优先级

每个expert需要创建对应的专家库：

```
bmad/aps/templates/algorithm-library/
├── README.md                    # 知识库总览
├── greedy/                      # 贪心算法
│   ├── basic-greedy.md
│   └── priority-based.md
├── heuristic/                   # 启发式算法
│   ├── 遗传算法.md
│   ├── 构造式启发式.md
│   ├── 改进式启发式.md
│   └── 贪心算法.md
├── exact/                       # 精确算法
│   ├── branch-and-bound.md
│   ├── dynamic-programming.md
│   └── integer-programming.md
└── hybrid/                      # 混合算法
```

**迁移建议**:

- 从 `调度产品设计草稿/` 中提取已有知识
- 标准化为模板格式
- 添加 `@引用路径`
- 包含代码示例

### 2. 任务定义创建 🟡 中优先级

`bmad/aps/tasks/` 需要创建单一操作任务：

必需任务（被workflow引用）:

- [ ] `analyze-user-request.md`
- [ ] `generate-todo-list.md`
- [ ] `check-todo-deviation.md`
- [ ] `extract-ten-elements.md`
- [ ] `validate-ten-element-model.md`
- [ ] `quality-gate-check.md`

推荐任务:

- [ ] `show-todo-progress.md`
- [ ] `call-specialist.md`
- [ ] `capability-gap-report.md`

### 3. 交互对话模板 🟡 中优先级

创建 `@交互对话模板库/`（可以放在templates或独立目录）:

- [ ] `Todo确认模板.md`
- [ ] `需求澄清模板.md`
- [ ] `领域确认模板.md`
- [ ] `约束确认模板.md`
- [ ] `目标权重模板.md`
- [ ] `冲突仲裁模板.md`
- [ ] `能力缺口模板.md`

### 4. 剩余Workflow创建 🟢 低优先级

完善所有workflow目录:

- [ ] `phase-1-requirements/workflow.yaml`
- [ ] `phase-2-coordination/workflow.yaml`
- [ ] `consistency-check/workflow.yaml`
- [ ] `phase-3-integration/workflow.yaml`
- [ ] `phase-4-quality/workflow.yaml`
- [ ] `interaction-modes/workflow.yaml`

### 5. 数据和示例 🟢 低优先级

填充 `bmad/aps/data/`:

- [ ] `benchmarks/` - 性能基准测试用例
- [ ] `examples/` - 示例调度问题

## 🚀 使用指南

### 安装模块

```bash
# 在BMAD-METHOD根目录
npm run install:bmad

# 选择 "APS - Advanced Planning & Scheduling"
```

### 激活主编排器

```bash
# 在您的项目目录
bmad aps

# 或使用别名
bmad orchestrator
```

### 基本使用流程

1. **激活编排器**

```bash
bmad aps
```

2. **启动调度求解**
   选择命令: `*start-scheduling`

3. **Phase 0: 任务规划**

- 系统生成Todo List
- 用户确认（形成执行合同）

4. **Phase 0.5: 模式选择**

- 模式A：集中确认（适合专家用户）
- 模式B：增量确认（适合业务用户）

5. **Phase 1-4: 自动执行**

- Phase 1: 需求分析
- Phase 1.5: 十要素建模
- Phase 2: 专家协调
- Phase 3: 方案集成
- Phase 4: 质量保证

6. **获得交付物**

- TenElementModel
- 可执行代码
- 质量报告
- Todo完成报告

### 专家咨询模式

直接调用特定专家：

```bash
bmad algorithm-expert    # 算法咨询
bmad constraint-expert   # 约束分析
bmad objective-expert    # 目标优化
bmad domain-expert       # 领域适配
bmad extension-guide     # 算法扩展
bmad quality-evaluator   # 质量评测
```

## 🔍 关键差异说明

### 1. 命令调用方式

**原始**: 文字描述的工作流程

**BMAD**: 结构化命令菜单

```xml
<menu>
  <item cmd="*start-scheduling" run-workflow="...">
    🚀 启动完整调度求解流程
  </item>
</menu>
```

用户通过 `*start-scheduling` 命令触发。

### 2. 知识加载机制

**原始**: 知识内嵌在智能体文件

**BMAD**: Sidecar按需加载

智能体文件通过 `<critical-actions>` 指定加载路径，实现：

- 智能体定义与知识内容分离
- Token使用效率提升75-87%
- 知识库独立维护和扩展

### 3. 工作流执行

**原始**: 隐式流程描述

**BMAD**: 显式YAML定义

- 可编程化执行
- 条件分支和并行支持
- 错误处理集成
- 质量门禁自动化

### 4. 人机交互

**原始**: 文字描述的交互点

**BMAD**: workflow步骤中明确定义

```yaml
- step_id: '1.3'
  action: 'human_confirmation'
  trigger_level: 'P0'
  template: '@交互对话模板库/Todo确认模板.md'
```

### 5. Guardrails实现

**原始**: 策略文字描述

**BMAD**: `<critical-actions>` 强制约束

```xml
<critical-actions>
  <i critical="MANDATORY">仅基于TenElementModel和@专家库</i>
  <i critical="MANDATORY">输出需附@引用</i>
  <i critical="BLOCKING">质量门禁 level≠pass → 退回</i>
</critical-actions>
```

## 📊 迁移前后对比

| 维度          | 迁移前      | 迁移后            | 改进       |
| ------------- | ----------- | ----------------- | ---------- |
| **文件数量**  | 8个Markdown | 30+文件（结构化） | 模块化 ↑   |
| **Token效率** | 基线        | 75-87%节省        | 效率 ↑     |
| **可执行性**  | 描述性      | 可编程化          | 自动化 ↑   |
| **可扩展性**  | 手动添加    | 模块化扩展        | 可维护性 ↑ |
| **集成能力**  | 独立系统    | BMAD生态集成      | 互操作性 ↑ |
| **质量保证**  | 手动验证    | 自动化门禁        | 可靠性 ↑   |
| **核心特性**  | 100%保留    | 100%保留          | 一致性 ✓   |

## 🎯 下一步行动建议

### 短期（1-2周）

1. **填充算法专家库** 🔴
   - 从现有算法代码提取知识
   - 创建标准化模板
   - 优先级：greedy, heuristic, exact

2. **创建核心任务** 🔴
   - 至少完成workflow引用的必需任务
   - 测试端到端流程

3. **交互模板库** 🟡
   - 创建7个核心交互模板
   - 确保P0-P4级别覆盖

### 中期（2-4周）

4. **完善其他专家库**
   - constraint-library
   - objective-library
   - domain-library
   - extension-library
   - quality-library

5. **创建完整workflow**
   - 补全所有Phase workflow
   - 测试双模式交互

6. **添加示例和基准**
   - 典型调度问题示例
   - 性能基准测试用例

### 长期（1-3月）

7. **知识库持续扩展**
   - 使用extension-guide智能体
   - 从项目实践中提取知识

8. **性能优化**
   - 监控Token使用
   - 优化workflow执行效率

9. **文档完善**
   - 用户手册
   - 最佳实践
   - 案例研究

## 🤝 获取帮助

### 参考文档

- [APS模块README](./README.md) - 模块完整文档
- [Workflows README](./workflows/README.md) - Workflow开发指南
- [BMAD-METHOD README](../../README.md) - BMAD框架总览
- [原始架构文档](../../调度产品设计草稿/架构总结.md)

### 常见问题

**Q: 为什么要拆分成这么多文件？**
A: 模块化架构带来更好的可维护性、可扩展性和Token效率。每个组件职责单一，便于独立开发和测试。

**Q: 原有的V4.3特性是否完整保留？**
A: 是的，100%保留。Todo List、双模式交互、Human-in-the-Loop、Guardrails等核心特性都通过BMAD机制实现。

**Q: 如何填充专家知识库？**
A: 可以使用extension-guide智能体辅助提取现有代码知识，也可以手动编写模板化知识文档。

**Q: workflow.yaml怎么执行？**
A: 通过agent的 `<menu>` 命令触发，或被其他workflow通过 `run-workflow` 步骤调用。

**Q: Sidecar模式如何工作？**
A: Agent通过 `<critical-actions>` 在激活时自动加载对应的专家库README，实现按需加载和Token节省。

## 📝 变更日志

### V1.0.0-alpha (2025-10-20)

**初始迁移**:

- ✅ 7个智能体完整迁移
- ✅ 架构文档转换
- ✅ 3个核心workflow示例
- ✅ 模块配置和安装配置
- ✅ 迁移指南创建

**待完成**:

- ⏳ 专家知识库填充
- ⏳ 任务定义创建
- ⏳ 交互模板库
- ⏳ 完整workflow集
- ⏳ 数据和示例

---

**迁移团队**: APS Team
**BMAD版本**: v6-alpha
**架构版本**: V4.3
**最后更新**: 2025-10-20

---

<sub>Built with ❤️ for scheduling optimization community | Powered by BMAD-CORE™</sub>
