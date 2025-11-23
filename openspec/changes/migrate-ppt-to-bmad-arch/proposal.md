# Proposal: 将PPT智能体系统迁移到BMAD标准架构

**Change ID**: `migrate-ppt-to-bmad-arch`
**Type**: Architecture Migration
**Status**: Proposed
**Date**: 2025-11-23
**Priority**: High

---

## Executive Summary

将当前的PPT智能体系统从**直接分发目录开发模式**重构为**符合BMAD-METHOD v6架构规范**的标准模块，实现与APS、BMB等模块的架构一致性。

**核心改造**：
1. 源码迁移：`bmad/ppt/` → `src/modules/ppt/`（开发源码）
2. Agent格式：简单Markdown → YAML格式（`.agent.yaml`）
3. 构建系统：新增构建脚本实现YAML→Markdown自动转换
4. 框架集成：创建主入口Agent + Slash Commands + Workflow注册

**架构对齐率**：从当前30%提升至100%（完全符合BMAD规范）

---

## Why

### 当前问题

**架构不一致性**：
```
APS模块（符合规范）:
  src/modules/aps/          ← 源码目录
    ├── agents/*.agent.yaml ← YAML源码
    └── build.js            ← 构建脚本
  bmad/aps/                 ← 编译产物
    └── agents/*.md         ← 生成的XML Markdown

PPT模块（不符合规范）❌:
  bmad/ppt/                 ← 直接在分发目录开发
    ├── agents/*.md         ← 简单Markdown（非XML格式）
    └── 无构建系统
```

**具体问题**：

1. **开发模式不规范**：
   - 在分发目录（`bmad/ppt/`）直接开发，违反"源码-编译-分发"分离原则
   - 缺少版本控制和构建历史追溯

2. **Agent格式不标准**：
   - 使用简单Markdown格式，缺少BMAD标准的XML activation blocks
   - 缺少Menu系统、Persona定义、Critical Actions等标准组件
   - 无法享受BMAD框架的Agent加载、状态管理等能力

3. **缺少主入口Agent**：
   - 没有统一的模块入口点（`ppt-master.md`）
   - 无法通过Slash Command便捷激活（如`/bmad-ppt`）

4. **未集成到BMAD框架**：
   - 未注册到`workflow-manifest.csv`
   - 不在`/bmad-master`模块列表中显示
   - 使用体验与其他BMAD模块不一致

5. **安装器不完整**：
   - 缺少构建步骤触发
   - 缺少BMAD框架注册逻辑

### 改造收益

**标准化**：
- ✅ 与APS、BMB、BMM等模块架构完全一致
- ✅ 遵循BMAD-METHOD v6规范（YAML agents + build system）

**可维护性**：
- ✅ YAML格式更易编辑和版本控制
- ✅ 源码与产物分离，构建历史可追溯
- ✅ 自动化构建流程减少人工错误

**用户体验**：
- ✅ 通过Slash Command快速激活（`/bmad-ppt`）
- ✅ 在BMAD Master中统一访问
- ✅ 标准化的Menu驱动交互

**可扩展性**：
- ✅ 易于添加新Agent或修改现有Agent
- ✅ 支持多环境构建（开发、测试、生产）
- ✅ 便于集成CI/CD流程

---

## What Changes

### 变更范围

此变更**不改变PPT智能体的核心功能**，仅进行架构迁移和格式转换。

**5个主要变更领域**：

1. **源码目录迁移** (`source-migration`)
   - 创建`src/modules/ppt/`完整源码目录
   - 迁移所有资源文件（expert-library、schemas、workflows等）

2. **构建系统集成** (`build-system`)
   - 创建`build.js`构建脚本
   - 实现YAML→Markdown自动转换
   - 集成到npm scripts（`npm run build:ppt`）

3. **Agent格式转换** (`agent-conversion`)
   - 将8个简单Markdown agents转换为YAML格式
   - 添加XML activation blocks、Menu、Persona等标准组件
   - 创建主入口Agent（`ppt-master.agent.yaml`）

4. **Slash Command集成** (`slash-command-integration`)
   - 创建6个Slash Command文件（`.claude/commands/bmad/`）
   - 注册workflow到`workflow-manifest.csv`

5. **安装器升级** (`installer-upgrade`)
   - 升级`installer.js`支持构建触发
   - 添加BMAD框架注册逻辑

### 影响的文件

**新增目录**：
```
src/modules/ppt/                          # 全新源码目录
  ├── agents/                             # YAML agents
  │   ├── ppt-master.agent.yaml           # 新增：主入口Agent
  │   ├── story-designer.agent.yaml       # 转换自现有.md
  │   ├── page-planner.agent.yaml
  │   ├── visual-stylist.agent.yaml
  │   ├── content-producer.agent.yaml
  │   ├── file-generator.agent.yaml
  │   └── helpers/
  │       ├── copywriter.agent.yaml
  │       └── chart-specialist.agent.yaml
  ├── workflows/                          # 从bmad/ppt/复制
  ├── expert-library/                     # 从bmad/ppt/复制
  ├── schemas/                            # 从bmad/ppt/复制
  ├── config.yaml                         # 从bmad/ppt/复制
  ├── build.js                            # 新增：构建脚本
  ├── README.md
  └── _module-installer/
      └── installer.js                    # 升级版本
```

**新增Slash Commands**：
```
.claude/commands/bmad/
  ├── ppt.md              # @/bmad/ppt/agents/ppt-master.md
  ├── ppt-story.md
  ├── ppt-page.md
  ├── ppt-visual.md
  ├── ppt-content.md
  └── ppt-file.md
```

**修改文件**：
```
package.json                              # 添加 build:ppt script
bmad/_cfg/workflow-manifest.csv           # 注册 ppt-creator workflow
```

**编译产物**（自动生成）：
```
bmad/ppt/                                 # 保留，但变为构建产物
  ├── agents/*.md                         # 从YAML自动生成
  ├── .build-meta.json                    # 新增：构建元数据
  └── ... (其他资源从src复制)
```

---

## Proposed Solution

### 架构设计原则

1. **零功能变更**：
   - 保持所有现有PPT功能和工作流逻辑不变
   - 用户交互体验保持一致（除了新增便捷入口）

2. **参考APS模块**：
   - 完全遵循`src/modules/aps/`的架构模式
   - 复用`YamlXmlBuilder`构建工具
   - 保持BMAD模块间一致性

3. **增量迁移**：
   - 保留现有`bmad/ppt/`作为备份（`.backup`）
   - 构建系统生成新产物到`bmad/ppt/`
   - 验证通过后再清理旧文件

4. **自动化优先**：
   - 所有Agent转换通过构建脚本自动化
   - 集成到npm scripts和安装器流程
   - 支持CI/CD集成

### 实施阶段

**阶段1：源码目录迁移**（2-3小时）
- 创建`src/modules/ppt/`目录结构
- 复制所有资源文件（expert-library、schemas、workflows等）
- 验证资源完整性

**阶段2：Agent格式转换**（3-4小时）
- 将8个agents从简单Markdown转换为YAML格式
- 添加metadata、persona、critical_actions、menu等标准组件
- 创建主入口Agent（`ppt-master.agent.yaml`）
- 参考格式：`src/modules/aps/agents/orchestrator.agent.yaml`

**阶段3：构建系统集成**（2小时）
- 创建`src/modules/ppt/build.js`（参考`src/modules/aps/build.js`）
- 实现YAML→Markdown转换逻辑
- 添加构建验证和元数据生成
- 集成到`package.json`的scripts

**阶段4：框架集成**（1小时）
- 创建6个Slash Command文件
- 注册workflow到`workflow-manifest.csv`
- 更新BMAD Master模块列表（如需要）

**阶段5：安装器升级**（1-2小时）
- 升级`installer.js`添加构建触发
- 添加BMAD框架注册函数
- 测试安装流程

**阶段6：测试验证**（2小时）
- 完整构建流程测试
- Slash Command激活测试
- 端到端PPT创建流程测试
- 回归测试确保功能无变化

**总计时间**：12-15小时（约2个工作日）

### 技术实现细节

#### 1. YAML Agent格式示例

**当前格式**（`bmad/ppt/agents/story-designer.md`）：
```markdown
# Story Designer Agent

## 角色定位
你是Story Designer,PPT创建系统Stage 1的专家Agent...

## 核心能力
1. **叙事结构推荐** - 从5种叙事模板中选择...
```

**目标格式**（`src/modules/ppt/agents/story-designer.agent.yaml`）：
```yaml
agent:
  metadata:
    id: bmad/ppt/agents/story-designer.md
    name: Story Designer
    title: PPT故事设计师 - 叙事结构专家
    icon: 📖
    module: ppt

  persona:
    role: PPT创建系统Stage 1的专家Agent，负责将用户需求转化为Story Blueprint
    identity: >-
      拥有丰富的叙事设计经验，精通5种叙事模板（问题-解决、时间线、
      对比分析、金字塔、故事弧），能够根据受众特征和演示目的设计最优的
      内容结构。擅长将复杂信息转化为引人入胜的叙事框架。
    communication_style: >-
      专业、结构化、注重受众需求分析。通过HITL机制在关键决策点
      与用户确认叙事结构选择，确保方案符合用户期望。
    principles: >-
      坚持"受众优先"原则，所有叙事结构推荐必须基于@expert-library
      知识库，不做主观臆断。遇到超出5种标准模板的需求时，
      输出能力缺口报告并建议最接近的解决方案。

  critical_actions:
    - 加载配置 {project-root}/bmad/ppt/config.yaml
    - 加载叙事模板库 {project-root}/bmad/ppt/expert-library/story-design/
    - 初始化状态目录 {project-root}/bmad/ppt/state/
    - 所有叙事结构推荐必须引用@模板路径
    - 在Story Blueprint确认前启用HITL机制

  menu:
    - description: 🚀 开始Story设计（完整流程）
      trigger: start-design
      workflow: "{project-root}/bmad/ppt/workflows/ppt-creator-workflow.yaml#stage-1"

    - description: 📚 浏览可用叙事模板
      trigger: show-templates
      exec: "{project-root}/bmad/ppt/tasks/show-narrative-templates.md"

    - description: 📊 验证Story Blueprint
      trigger: validate-blueprint
      exec: "{project-root}/bmad/ppt/tasks/validate-story-blueprint.md"

    - description: 💾 保存Story Blueprint
      trigger: save-blueprint
      exec: "{project-root}/bmad/ppt/tasks/save-story-blueprint.md"

    - description: 📂 加载示例输入
      trigger: load-example
      exec: "{project-root}/bmad/ppt/tasks/load-story-example.md"
```

#### 2. 构建脚本实现

**文件**：`src/modules/ppt/build.js`（参考`src/modules/aps/build.js`）

**关键功能**：
- 使用`YamlXmlBuilder`将`.agent.yaml`转换为`.md`
- 复制非Agent资源（workflows、expert-library等）
- 生成构建元数据（`.build-meta.json`）
- 验证关键文件完整性

**核心代码框架**：
```javascript
const { YamlXmlBuilder } = require(path.join(PROJECT_ROOT, 'tools/cli/lib/yaml-xml-builder'));

async function buildAgents(builder) {
  const sourceAgentsDir = path.join(SOURCE_DIR, 'agents');
  const targetAgentsDir = path.join(TARGET_DIR, 'agents');

  const yamlFiles = await findYamlFiles(sourceAgentsDir);

  for (const yamlFile of yamlFiles) {
    await builder.buildAgent(yamlPath, null, mdPath, {
      includeMetadata: true
    });
  }
}

async function copyResources() {
  const COPY_ITEMS = [
    'workflows', 'expert-library', 'schemas',
    'config.yaml', 'README.md', '_module-installer'
  ];
  // 复制逻辑...
}

async function build() {
  const builder = new YamlXmlBuilder();
  await buildAgents(builder);
  await copyResources();
  await generateBuildMeta();
  await verifyBuild();
}
```

#### 3. 主入口Agent设计

**文件**：`src/modules/ppt/agents/ppt-master.agent.yaml`

**功能**：
- 提供PPT模块统一入口
- 菜单驱动的交互体验
- 支持完整workflow和单阶段Agent两种模式

**Menu结构**：
```yaml
menu:
  # 完整流程
  - description: 🚀 创建新PPT（完整5阶段流程）
    trigger: create-ppt
    workflow: "{project-root}/bmad/ppt/workflows/ppt-creator-workflow.yaml"

  # 单阶段入口
  - description: 📖 Stage 1: Story设计
    trigger: story-design
    agent: "{project-root}/bmad/ppt/agents/story-designer.md"

  - description: 📄 Stage 2: 页面规划
    trigger: page-plan
    agent: "{project-root}/bmad/ppt/agents/page-planner.md"

  - description: 🎨 Stage 3: 视觉设计
    trigger: visual-design
    agent: "{project-root}/bmad/ppt/agents/visual-stylist.md"

  - description: ✍️ Stage 4: 内容生产
    trigger: content-produce
    agent: "{project-root}/bmad/ppt/agents/content-producer.md"

  - description: 📦 Stage 5: 文件生成
    trigger: file-generate
    agent: "{project-root}/bmad/ppt/agents/file-generator.md"

  # 辅助功能
  - description: 📂 加载快速开始示例
    trigger: load-example
    exec: "{project-root}/bmad/ppt/tasks/load-quickstart-example.md"

  - description: 🔍 查看当前状态
    trigger: check-status
    exec: "{project-root}/bmad/ppt/tasks/check-ppt-status.md"
```

#### 4. Slash Command集成

**创建命令文件**（`.claude/commands/bmad/`）：

```bash
# ppt.md
@/bmad/ppt/agents/ppt-master.md

# ppt-story.md
@/bmad/ppt/agents/story-designer.md

# ppt-page.md
@/bmad/ppt/agents/page-planner.md

# ppt-visual.md
@/bmad/ppt/agents/visual-stylist.md

# ppt-content.md
@/bmad/ppt/agents/content-producer.md

# ppt-file.md
@/bmad/ppt/agents/file-generator.md
```

**注册Workflow**（`bmad/_cfg/workflow-manifest.csv`）：
```csv
"ppt-creator","Complete 5-stage PPT creation: Story → Pages → Visual → Content → File. 8 themes, 20 layouts, HITL at 2 key points","ppt","bmad/ppt/workflows/ppt-creator-workflow.yaml"
```

#### 5. 安装器升级

**文件**：`src/modules/ppt/_module-installer/installer.js`

**新增函数**：
```javascript
async function registerToBMAD() {
  console.log(chalk.cyan('\n📋 注册到BMAD框架...'));

  // 1. 创建Slash Commands
  const commandsDir = path.join(projectRoot, '.claude/commands/bmad');
  await fs.ensureDir(commandsDir);

  const commands = {
    'ppt.md': '@/bmad/ppt/agents/ppt-master.md',
    'ppt-story.md': '@/bmad/ppt/agents/story-designer.md',
    'ppt-page.md': '@/bmad/ppt/agents/page-planner.md',
    'ppt-visual.md': '@/bmad/ppt/agents/visual-stylist.md',
    'ppt-content.md': '@/bmad/ppt/agents/content-producer.md',
    'ppt-file.md': '@/bmad/ppt/agents/file-generator.md'
  };

  for (const [filename, content] of Object.entries(commands)) {
    await fs.writeFile(path.join(commandsDir, filename), content);
    console.log(chalk.green(`  ✓ Created /bmad-${filename.replace('.md', '')}`));
  }

  // 2. 注册Workflow
  const manifestPath = path.join(projectRoot, 'bmad/_cfg/workflow-manifest.csv');
  if (await fs.pathExists(manifestPath)) {
    const content = await fs.readFile(manifestPath, 'utf-8');
    if (!content.includes('ppt-creator')) {
      await fs.appendFile(manifestPath,
        '\n"ppt-creator","Complete 5-stage PPT creation workflow","ppt","bmad/ppt/workflows/ppt-creator-workflow.yaml"'
      );
      console.log(chalk.green('  ✓ Registered ppt-creator workflow'));
    }
  }

  console.log(chalk.green('✅ BMAD框架注册完成\n'));
}

async function triggerBuild() {
  console.log(chalk.cyan('\n🏗️  构建PPT模块...'));

  const buildScript = path.join(projectRoot, 'src/modules/ppt/build.js');
  if (await fs.pathExists(buildScript)) {
    const { build } = require(buildScript);
    const exitCode = await build();
    if (exitCode !== 0) {
      throw new Error('构建失败');
    }
    console.log(chalk.green('✅ 构建完成\n'));
  } else {
    console.log(chalk.yellow('⚠️  未找到构建脚本，跳过构建\n'));
  }
}

async function install() {
  // ... 现有逻辑 ...

  // 新增：触发构建
  await triggerBuild();

  // 新增：注册到BMAD
  await registerToBMAD();

  // ... 后续逻辑 ...
}
```

---

## Migration Strategy

### 迁移步骤

**步骤1：备份现有系统**
```bash
# 备份当前bmad/ppt/目录
cp -r bmad/ppt bmad/ppt.backup-$(date +%Y%m%d)
```

**步骤2：创建源码目录**
```bash
# 创建src/modules/ppt/目录结构
mkdir -p src/modules/ppt/{agents/helpers,workflows,expert-library,schemas,_module-installer}

# 复制资源文件
cp -r bmad/ppt/expert-library src/modules/ppt/
cp -r bmad/ppt/schemas src/modules/ppt/
cp -r bmad/ppt/workflows src/modules/ppt/
cp bmad/ppt/config.yaml src/modules/ppt/
```

**步骤3：转换Agent格式**
```bash
# 手动转换8个agents从.md到.agent.yaml
# 参考 src/modules/aps/agents/orchestrator.agent.yaml 格式
```

**步骤4：创建构建系统**
```bash
# 创建build.js
# 参考 src/modules/aps/build.js

# 测试构建
node src/modules/ppt/build.js

# 添加到package.json
npm run build:ppt
```

**步骤5：集成到BMAD框架**
```bash
# 创建Slash Commands
# 注册Workflow到manifest.csv
# 升级安装器
```

**步骤6：验证测试**
```bash
# 完整安装流程测试
bash bmad/ppt/_module-installer/install.sh

# Slash Command测试
/bmad-ppt

# 端到端流程测试
/bmad-ppt → *create-ppt → 完成5阶段流程
```

### 回滚计划

如果迁移失败，可快速回滚：

1. 恢复备份目录：
   ```bash
   rm -rf bmad/ppt
   cp -r bmad/ppt.backup-20251123 bmad/ppt
   ```

2. 删除源码目录：
   ```bash
   rm -rf src/modules/ppt
   ```

3. 移除Slash Commands：
   ```bash
   rm -f .claude/commands/bmad/ppt*.md
   ```

4. 恢复manifest.csv（移除ppt-creator行）

### 风险评估

**低风险**：
- ✅ Agent格式转换（逻辑不变，仅格式）
- ✅ 资源文件复制（无修改）
- ✅ Slash Command创建（纯新增）

**中风险**：
- ⚠️ 构建脚本实现（参考APS，风险可控）
- ⚠️ 安装器升级（需充分测试）

**缓解措施**：
- 完整备份现有系统
- 增量测试（每完成一个Agent就构建测试）
- 保留回滚路径
- 完整的端到端测试

---

## Impact Analysis

### 对用户的影响

**正面影响**：
- ✅ 更便捷的访问方式（Slash Commands）
- ✅ 统一的BMAD使用体验
- ✅ 更清晰的菜单驱动交互

**无影响**：
- ✅ 所有现有功能保持不变
- ✅ 工作流逻辑完全一致
- ✅ 输出结果质量不变

**需要适应**：
- ⚠️ 新增的主入口Agent（可选使用）
- ⚠️ Slash Command激活方式（可选，仍支持旧方式）

### 对开发的影响

**开发体验提升**：
- ✅ YAML格式更易编辑和维护
- ✅ 源码与产物分离，版本控制更清晰
- ✅ 自动化构建减少手工错误

**开发流程变化**：
```
旧流程:
  编辑 bmad/ppt/agents/*.md → 直接使用

新流程:
  编辑 src/modules/ppt/agents/*.agent.yaml → npm run build:ppt → 使用
```

**CI/CD集成**：
```yaml
# GitHub Actions示例
- name: Build PPT Module
  run: npm run build:ppt

- name: Verify Build
  run: test -f bmad/ppt/.build-meta.json
```

### 对性能的影响

**构建时间**：
- 初次构建：约10-15秒（8个agents转换 + 资源复制）
- 增量构建：约3-5秒（仅变更的agents）

**运行时性能**：
- 无影响（生成的Markdown格式与之前一致）

---

## Success Metrics

**完成标准**：

1. **架构合规性**：
   - [ ] 源码目录`src/modules/ppt/`结构完整
   - [ ] 所有8个agents转换为YAML格式
   - [ ] 构建系统正常工作（`npm run build:ppt`）
   - [ ] 生成的agents符合BMAD XML规范

2. **功能完整性**：
   - [ ] 所有现有PPT功能保持不变
   - [ ] 5阶段workflow正常运行
   - [ ] 生成的PPTX质量与之前一致

3. **框架集成**：
   - [ ] 6个Slash Commands可用（`/bmad-ppt`等）
   - [ ] Workflow已注册到manifest.csv
   - [ ] 在BMAD Master中可见（如适用）

4. **质量验证**：
   - [ ] 构建无错误和警告
   - [ ] 端到端测试通过（3个场景）
   - [ ] 回归测试通过（确保无功能变化）

5. **文档完善**：
   - [ ] README.md更新（说明新的开发流程）
   - [ ] MIGRATION_GUIDE.md创建（迁移指南）
   - [ ] 构建文档更新

**验收测试场景**：

1. **构建测试**：
   ```bash
   npm run build:ppt
   # 验证：bmad/ppt/agents/下生成8个.md文件
   # 验证：.build-meta.json包含正确的元数据
   ```

2. **Slash Command测试**：
   ```bash
   /bmad-ppt
   # 验证：显示主菜单
   # 验证：可选择完整workflow或单阶段agent
   ```

3. **端到端PPT创建**：
   ```bash
   /bmad-ppt → *create-ppt
   # 场景1：产品发布PPT（15页）
   # 场景2：技术报告PPT（20页）
   # 场景3：销售演示PPT（12页）
   # 验证：生成的PPTX质量与迁移前一致
   ```

4. **回归测试**：
   - 使用相同输入（quickstart-input.yaml）
   - 对比迁移前后生成的PPTX
   - 验证：内容结构、视觉设计、文件质量完全一致

---

## Timeline

**总工期**：2个工作日（12-15小时）

**详细时间线**：

| 阶段 | 任务 | 时间 | 交付物 |
|------|------|------|--------|
| **Day 1 上午** | 源码目录迁移 + Agent格式转换（前4个） | 3小时 | `src/modules/ppt/`目录 + 4个YAML agents |
| **Day 1 下午** | Agent格式转换（后4个） + 主入口Agent | 3小时 | 8个YAML agents + ppt-master |
| **Day 2 上午** | 构建系统 + 框架集成 | 3小时 | build.js + Slash Commands |
| **Day 2 下午** | 安装器升级 + 测试验证 | 3小时 | 升级的installer + 完整测试 |

**里程碑**：
- ✅ **M1**（Day 1结束）：所有agents转换完成，构建系统可工作
- ✅ **M2**（Day 2中午）：框架集成完成，可通过Slash Command激活
- ✅ **M3**（Day 2结束）：完整测试通过，迁移完成

---

## Open Questions

1. **是否保留旧的激活方式**？
   - 问题：除了新的Slash Command，是否仍支持旧的手动激活方式？
   - 建议：保留，作为fallback机制

2. **构建触发时机**？
   - 问题：何时自动触发构建？安装时？git commit时？
   - 建议：安装时触发 + 开发者手动触发（`npm run build:ppt`）

3. **是否需要Husky集成**？
   - 问题：是否在pre-commit hook中自动构建PPT模块？
   - 建议：暂不集成，避免影响提交速度（开发者按需构建）

4. **辅助Tasks是否需要创建**？
   - 问题：是否创建`tasks/show-narrative-templates.md`等辅助task文件？
   - 建议：在Agent的menu中引用但暂不创建，作为后续优化项

5. **是否需要更新BMAD Master**？
   - 问题：是否需要修改`bmad/core/agents/bmad-master.md`以显示PPT模块？
   - 建议：取决于BMAD Master的当前实现，如有模块列表则添加

---

## Alternatives Considered

### 替代方案1：保持现状

**方案**：不进行架构迁移，继续在`bmad/ppt/`直接开发

**优点**：
- 无需迁移工作量
- 无短期风险

**缺点**：
- 架构不一致性持续存在
- 技术债累积
- 未来维护成本高
- 无法享受BMAD框架能力

**决策**：❌ 不采纳（架构一致性优先级更高）

### 替代方案2：仅格式转换，不迁移源码

**方案**：将agents转换为XML Markdown格式，但仍在`bmad/ppt/`开发

**优点**：
- 工作量减半
- 部分架构对齐

**缺点**：
- 仍违反"源码-产物"分离原则
- 无法享受构建系统优势
- 不彻底，未来仍需二次迁移

**决策**：❌ 不采纳（架构对齐应一步到位）

### 替代方案3：完全重写PPT模块

**方案**：从零重写PPT模块，直接按BMAD规范开发

**优点**：
- 架构完美
- 无历史包袱

**缺点**：
- 工作量巨大（估计2周以上）
- 高风险（功能可能不完整）
- 浪费现有开发成果

**决策**：❌ 不采纳（迁移方案性价比更高）

### 选择当前方案的理由

**当前方案（架构迁移）** 是最佳平衡：
- ✅ 架构完全对齐（100%符合BMAD规范）
- ✅ 工作量可控（2个工作日）
- ✅ 低风险（功能逻辑不变）
- ✅ 保留现有开发成果
- ✅ 为未来扩展打好基础

---

## References

**参考模块**：
- `src/modules/aps/` - APS模块完整架构
- `src/modules/aps/build.js` - 构建脚本参考
- `src/modules/aps/agents/orchestrator.agent.yaml` - YAML Agent格式参考

**相关文档**：
- `docs/ppt-agent-system/bmad-integration-plan.md` - 原始改造计划
- `openspec/changes/create-ppt-agent-system/` - PPT系统创建提案
- `openspec/project.md` - BMAD项目架构约定

**工具文档**：
- `tools/cli/lib/yaml-xml-builder.js` - YAML→XML构建工具
- `package.json` - npm scripts配置参考

---

## Appendix

### A. Agent转换对照表

| 现有文件 | 新文件 | 转换复杂度 | 预计时间 |
|---------|--------|-----------|----------|
| `bmad/ppt/agents/story-designer.md` | `src/modules/ppt/agents/story-designer.agent.yaml` | 中 | 30分钟 |
| `bmad/ppt/agents/page-planner.md` | `src/modules/ppt/agents/page-planner.agent.yaml` | 中 | 30分钟 |
| `bmad/ppt/agents/visual-stylist.md` | `src/modules/ppt/agents/visual-stylist.agent.yaml` | 中 | 30分钟 |
| `bmad/ppt/agents/content-producer.md` | `src/modules/ppt/agents/content-producer.agent.yaml` | 中 | 30分钟 |
| `bmad/ppt/agents/file-generator.md` | `src/modules/ppt/agents/file-generator.agent.yaml` | 低 | 20分钟 |
| `bmad/ppt/agents/helpers/copywriter.md` | `src/modules/ppt/agents/helpers/copywriter.agent.yaml` | 低 | 15分钟 |
| `bmad/ppt/agents/helpers/chart-specialist.md` | `src/modules/ppt/agents/helpers/chart-specialist.agent.yaml` | 低 | 15分钟 |
| - | `src/modules/ppt/agents/ppt-master.agent.yaml` | 中 | 40分钟 |
| **总计** | **8个文件** | - | **3小时** |

### B. 构建系统关键文件

**package.json新增**：
```json
{
  "scripts": {
    "build:ppt": "node src/modules/ppt/build.js"
  }
}
```

**构建元数据示例**（`.build-meta.json`）：
```json
{
  "module": "ppt",
  "version": "1.0.0",
  "buildTime": "2025-11-23T10:30:00.000Z",
  "source": "src/modules/ppt",
  "architecture": "BMAD-METHOD v6 - YAML",
  "sourceHash": "a1b2c3d4",
  "agents": 8,
  "resources": 6
}
```

### C. 验收测试Checklist

**构建验证**：
- [ ] `npm run build:ppt` 无错误
- [ ] `bmad/ppt/agents/` 包含8个.md文件
- [ ] 所有.md文件包含XML activation blocks
- [ ] `.build-meta.json` 存在且格式正确

**功能验证**：
- [ ] `/bmad-ppt` 显示主菜单
- [ ] `/bmad-ppt-story` 启动Story Designer
- [ ] 完整workflow可运行（5阶段）
- [ ] 生成的PPTX与迁移前一致

**集成验证**：
- [ ] `workflow-manifest.csv` 包含ppt-creator
- [ ] Slash Commands全部创建（6个）
- [ ] 安装器运行成功
- [ ] 构建触发正常

**文档验证**：
- [ ] README.md更新
- [ ] 开发流程文档完整
- [ ] 示例输入可用

---

**提案状态**：✅ 完整提交，等待审批

**下一步行动**：
1. 审批此提案
2. 创建对应的tasks.md和specs/
3. 开始实施迁移

---

_此提案由BMAD架构分析自动生成 - 2025-11-23_
