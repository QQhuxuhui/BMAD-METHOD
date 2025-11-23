# Spec: Agent格式转换 (Agent Conversion)

**Capability ID**: `agent-conversion`
**Change**: `migrate-ppt-to-bmad-arch`
**Status**: Proposed

---

## ADDED Requirements

### Requirement: Add BMAD Standard Components

All converted agents MUST include BMAD standard components (metadata, persona, critical_actions, menu).

**ID**: `agent-conversion-004`
**Priority**: P0 (Critical)

**Acceptance Criteria**:

- Metadata完整（id, name, title, icon, module）
- Persona结构化（role, identity, communication_style, principles）
- Critical_actions明确（至少3条）
- Menu可用（至少2个选项）

#### Scenario: 验证page-planner标准组件

**Given**: page-planner agent需要符合BMAD规范
**When**: 检查YAML结构
**Then**:

- `metadata.id` = "bmad/ppt/agents/page-planner.md"
- `metadata.module` = "ppt"
- `metadata.icon` = "📄"
- `persona.role`描述Stage 2职责
- `critical_actions`包含加载page-planning expert-library
- `menu`包含至少start-planning选项

**Validation**:

```bash
node -e "
const yaml = require('js-yaml');
const fs = require('fs');
const agent = yaml.load(fs.readFileSync('src/modules/ppt/agents/page-planner.agent.yaml', 'utf8'));
const meta = agent.agent.metadata;
if (meta.id !== 'bmad/ppt/agents/page-planner.md') throw new Error('Invalid metadata.id');
if (meta.module !== 'ppt') throw new Error('Invalid metadata.module');
if (!meta.icon) throw new Error('Missing icon');
if (!agent.agent.persona.role) throw new Error('Missing persona.role');
if (!agent.agent.critical_actions || agent.agent.critical_actions.length < 3) throw new Error('Insufficient critical_actions');
if (!agent.agent.menu || agent.agent.menu.length < 2) throw new Error('Insufficient menu items');
console.log('✅ BMAD standard components validated');
"
```

---

## MODIFIED Requirements

无（现有agents不被修改，仅创建新格式文件）

---

## REMOVED Requirements

无（旧的Markdown agents保留作为备份）

---

## Cross-References

**依赖于**:

- `source-migration` - 需要源码目录已创建

**被依赖于**:

- `build-system` - 构建系统将编译这些YAML agents

**相关Specs**:

- `build-system/spec.md` - 定义YAML→Markdown转换逻辑
- `slash-command-integration/spec.md` - Slash commands引用生成的agents

---

## Implementation Notes

**转换清单**（8个agents）:

| 序号 | 原文件                      | 新文件                              | 复杂度 | 优先级 |
| ---- | --------------------------- | ----------------------------------- | ------ | ------ |
| 1    | story-designer.md           | story-designer.agent.yaml           | 中     | P0     |
| 2    | page-planner.md             | page-planner.agent.yaml             | 中     | P0     |
| 3    | visual-stylist.md           | visual-stylist.agent.yaml           | 中     | P0     |
| 4    | content-producer.md         | content-producer.agent.yaml         | 中     | P0     |
| 5    | file-generator.md           | file-generator.agent.yaml           | 低     | P0     |
| 6    | helpers/copywriter.md       | helpers/copywriter.agent.yaml       | 低     | P1     |
| 7    | helpers/chart-specialist.md | helpers/chart-specialist.agent.yaml | 低     | P1     |
| 8    | (新增)                      | ppt-master.agent.yaml               | 中     | P0     |

**YAML模板结构**:

```yaml
agent:
  metadata:
    id: 'bmad/ppt/agents/{agent-name}.md'
    name: '{Agent Display Name}'
    title: '{Agent Full Title}'
    icon: '{Emoji}'
    module: 'ppt'

  persona:
    role: '{One-line role description}'
    identity: >-
      {Multi-line identity and expertise description}
    communication_style: >-
      {Communication approach and interaction patterns}
    principles: >-
      {Core principles and constraints}

  critical_actions:
    - '加载配置 {project-root}/bmad/ppt/config.yaml'
    - '加载专家库 {project-root}/bmad/ppt/expert-library/{stage}/'
    - '初始化状态目录 {project-root}/bmad/ppt/state/'
    - '{Stage-specific critical action}'

  menu:
    - description: '{Menu item description}'
      trigger: '{command-trigger}'
      workflow: '{workflow-path}' # or exec: "{task-path}" or agent: "{agent-path}"
```

---

## Testing Strategy

**单元测试**:

- YAML语法验证（js-yaml解析）
- Schema结构验证
- 必需字段存在性验证

**集成测试**:

- Agent加载测试（通过构建系统）
- Menu命令触发测试
- Workflow引用路径验证

**验收测试**:

- 手动激活每个agent
- 验证Menu显示正确
- 验证Critical actions执行
- 对比原agent功能一致性

---

_此spec由OpenSpec系统生成 - 2025-11-23_
