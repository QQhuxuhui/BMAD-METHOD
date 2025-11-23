# PPT智能体系统 BMAD架构集成方案

**创建日期**: 2025-11-23
**状态**: 待实施
**优先级**: 高

---

## 问题概述

当前的PPT智能体系统虽然功能完整，但**未完全符合BMAD-METHOD的架构规范**，导致无法像其他BMAD模块一样安装到Claude Code等客户端中使用。

## 架构符合性分析

### ✅ 已符合的部分

1. **模块目录结构**: `bmad/ppt/` 符合标准
2. **Workflow YAML**: `ppt-creator-workflow.yaml` 格式正确
3. **配置文件**: `config.yaml` 符合规范
4. **专家库**: `expert-library/` 数据结构完整
5. **安装器**: `_module-installer/install.sh` 存在

### ❌ 需要改造的部分

#### 1. Agent格式不符合BMAD规范

**当前格式**（简单Markdown）：

```markdown
# Story Designer Agent

## 角色定位

你是Story Designer,PPT创建系统Stage 1的专家Agent...
```

**应该是**（BMAD XML格式）：

```xml
<agent id="bmad/ppt/agents/story-designer.md"
       name="Story Designer"
       title="PPT Story Designer - Narrative Structure Expert"
       icon="📖">
  <activation critical="MANDATORY">
    <step n="1">Load persona from this current agent file</step>
    <step n="2">Load {project-root}/bmad/ppt/config.yaml</step>
    <step n="3">Show greeting and menu</step>
    <step n="4">WAIT for user input</step>
  </activation>

  <persona>
    <role>Story Designer - Narrative Structure Expert</role>
    <identity>Expert in converting user requirements into structured Story Blueprints...</identity>
    <communication_style>Professional, strategic, consultative...</communication_style>
  </persona>

  <menu>
    <item cmd="*start-design" action="workflow">Start Story Design</item>
    <item cmd="*load-example" action="load-example">Load Example Input</item>
    <item cmd="*help">Show Menu</item>
    <item cmd="*exit">Exit</item>
  </menu>
</agent>
```

**需要重构的Agents**（6个主Agent + 2个Helper）：

- `story-designer.md`
- `page-planner.md`
- `visual-stylist.md`
- `content-producer.md`
- `file-generator.md`
- `helpers/copywriter.md`
- `helpers/chart-specialist.md`

#### 2. 缺少主入口Agent

需要创建 `bmad/ppt/agents/ppt-master.md` 作为PPT模块的主入口Agent：

```xml
<agent id="bmad/ppt/agents/ppt-master.md"
       name="PPT Master"
       title="PPT智能体系统 - 主控制器"
       icon="🎯">
  <activation critical="MANDATORY">
    <step n="1">Load config from {project-root}/bmad/ppt/config.yaml</step>
    <step n="2">Initialize state directory</step>
    <step n="3">Show welcome message and main menu</step>
    <step n="4">WAIT for user selection</step>
  </activation>

  <persona>
    <role>PPT Master Orchestrator</role>
    <identity>Master coordinator for the PPT Agent System...</identity>
  </persona>

  <menu>
    <item cmd="*create-ppt" workflow="ppt-creator-workflow.yaml">
      Create New PPT (完整5阶段流程)
    </item>
    <item cmd="*story-design" agent="story-designer.md">
      Stage 1: Story Design Only
    </item>
    <item cmd="*page-plan" agent="page-planner.md">
      Stage 2: Page Planning Only
    </item>
    <item cmd="*visual-design" agent="visual-stylist.md">
      Stage 3: Visual Design Only
    </item>
    <item cmd="*content-produce" agent="content-producer.md">
      Stage 4: Content Production Only
    </item>
    <item cmd="*file-generate" agent="file-generator.md">
      Stage 5: File Generation Only
    </item>
    <item cmd="*load-example" action="load-quickstart">
      Load Quick Start Example
    </item>
    <item cmd="*help">Show Menu</item>
    <item cmd="*exit">Exit</item>
  </menu>
</agent>
```

#### 3. Slash Command集成

需要在 `.claude/commands/bmad/` 创建slash command文件：

**文件**: `.claude/commands/bmad/ppt.md`

```markdown
@/bmad/ppt/agents/ppt-master.md
```

**文件**: `.claude/commands/bmad/ppt-story.md`

```markdown
@/bmad/ppt/agents/story-designer.md
```

**文件**: `.claude/commands/bmad/ppt-page.md`

```markdown
@/bmad/ppt/agents/page-planner.md
```

**文件**: `.claude/commands/bmad/ppt-visual.md`

```markdown
@/bmad/ppt/agents/visual-stylist.md
```

**文件**: `.claude/commands/bmad/ppt-content.md`

```markdown
@/bmad/ppt/agents/content-producer.md
```

**文件**: `.claude/commands/bmad/ppt-file.md`

```markdown
@/bmad/ppt/agents/file-generator.md
```

#### 4. 模块注册

在 `bmad/_cfg/workflow-manifest.csv` 添加：

```csv
"ppt-creator","Complete 5-stage PPT creation workflow: Story Design → Page Planning → Visual Design → Content Production → File Generation. Supports 8 themes, 20 layouts, HITL confirmation at 2 key points.","ppt","bmad/ppt/workflows/ppt-creator-workflow.yaml"
```

#### 5. 更新安装脚本

`bmad/ppt/_module-installer/install.sh` 需要添加BMAD集成步骤：

```bash
# 新增函数: 注册到BMAD框架
register_to_bmad() {
    print_info "注册到BMAD框架..."

    # 1. 创建slash commands
    mkdir -p .claude/commands/bmad

    cat > .claude/commands/bmad/ppt.md << 'EOF'
@/bmad/ppt/agents/ppt-master.md
EOF

    # 2. 注册workflow到manifest
    if ! grep -q "ppt-creator" bmad/_cfg/workflow-manifest.csv; then
        echo '"ppt-creator","Complete 5-stage PPT creation workflow","ppt","bmad/ppt/workflows/ppt-creator-workflow.yaml"' >> bmad/_cfg/workflow-manifest.csv
    fi

    print_success "BMAD框架注册完成 ✓"
}
```

---

## 改造实施计划

### 阶段1: Agent重构（核心）

**任务**: 将8个agents重构为BMAD XML格式

**时间估算**: 2-3小时

**关键点**:

- 保持现有功能逻辑不变
- 添加XML activation结构
- 添加menu系统
- 添加persona定义

### 阶段2: 主入口Agent创建

**任务**: 创建 `ppt-master.md`

**时间估算**: 30分钟

**关键点**:

- 提供完整workflow入口
- 提供单阶段Agent入口
- 集成示例加载功能

### 阶段3: Claude Code集成

**任务**: 创建slash commands并注册workflow

**时间估算**: 30分钟

**关键点**:

- 在 `.claude/commands/bmad/` 创建命令文件
- 更新 `workflow-manifest.csv`
- 更新 `task-manifest.csv`（如需要）

### 阶段4: 安装器升级

**任务**: 更新 `install.sh` 支持BMAD集成

**时间估算**: 1小时

**关键点**:

- 添加BMAD注册步骤
- 添加slash command创建
- 添加manifest更新

### 阶段5: 测试验证

**任务**: 完整测试BMAD集成流程

**时间估算**: 1小时

**测试场景**:

1. 使用 `/bmad-ppt` 启动PPT模块
2. 从主菜单选择完整workflow
3. 从主菜单选择单阶段Agent
4. 验证状态管理和数据流
5. 验证PPTX生成

---

## 使用方式对比

### 改造前（当前）

```bash
# 必须手动运行安装脚本
bash bmad/ppt/_module-installer/install.sh

# 然后手动告诉Claude
claude "请使用PPT智能体系统，基于 quickstart-input.yaml 生成演示文稿"
```

### 改造后（符合BMAD规范）

```bash
# 安装模块（一次性）
bash bmad/ppt/_module-installer/install.sh

# 使用slash command激活
/bmad-ppt                    # 启动PPT Master
/bmad-ppt-story              # 直接启动Story Designer
/bmad-ppt-visual             # 直接启动Visual Stylist

# 或在bmad-master中选择
/bmad-master
> 选择PPT模块 -> 进入ppt-master菜单
```

---

## 改造收益

### 1. **标准化集成**

- 符合BMAD架构规范
- 与其他模块（bmb、core、aps）一致的使用体验

### 2. **便捷访问**

- 通过slash command快速激活
- 无需手动告知Claude使用哪个系统

### 3. **框架感知**

- 在 `/bmad-master` 的模块列表中显示
- workflow在 `*list-workflows` 中可见

### 4. **专业体验**

- Agent persona系统
- 菜单驱动交互
- 状态管理和上下文保持

### 5. **可扩展性**

- 未来可添加更多PPT相关workflows
- 可集成到更大的文档生成系统

---

## 风险评估

### 低风险项

- ✅ Agent重构（逻辑不变，只改格式）
- ✅ Slash command创建（纯新增）
- ✅ Manifest注册（纯新增）

### 中风险项

- ⚠️ 主入口Agent创建（需要设计良好的menu结构）
- ⚠️ 安装器更新（需要兼容已安装场景）

### 缓解措施

1. **保留原有文件**: 重构前先备份
2. **增量测试**: 每完成一个Agent就测试
3. **文档更新**: 同步更新用户指南

---

## 后续优化方向

### v1.1 增强功能

1. **Task分解**: 将一些工具函数提取为独立tasks
2. **Helper Agent优化**: copywriter和chart-specialist也使用XML格式
3. **状态持久化**: 集成Serena MCP做会话管理

### v1.2 生态集成

1. **与document-skills深度集成**: 探索更多文档格式
2. **模板市场**: 支持用户自定义theme和layout
3. **协作模式**: 多人协作创建PPT

---

## 决策请求

**是否立即开始BMAD架构改造？**

- ✅ **立即开始**: 完整改造，使PPT模块符合BMAD标准
- ⏸️ **暂缓**: 先完成其他优先级更高的任务
- 📝 **部分实施**: 只做关键改造（如主Agent + slash command）

请指示下一步行动。
