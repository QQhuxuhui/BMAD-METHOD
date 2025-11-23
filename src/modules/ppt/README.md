# PPT智能体系统 - 源码目录

**模块**: PPT Creator
**版本**: 1.0.0
**架构**: BMAD-METHOD v6 (YAML-based agents)
**状态**: 生产就绪

---

## 目录说明

这是PPT智能体系统的**源码目录**，遵循BMAD标准架构规范。

```
src/modules/ppt/                    # 源码根目录
├── agents/                         # Agent定义（YAML格式）
│   ├── ppt-master.agent.yaml       # 主入口Agent
│   ├── story-designer.agent.yaml   # Stage 1: 故事设计
│   ├── page-planner.agent.yaml     # Stage 2: 页面规划
│   ├── visual-stylist.agent.yaml   # Stage 3: 视觉设计
│   ├── content-producer.agent.yaml # Stage 4: 内容生产
│   ├── file-generator.agent.yaml   # Stage 5: 文件生成
│   └── helpers/                    # 辅助Agents
│       ├── copywriter.agent.yaml
│       └── chart-specialist.agent.yaml
├── workflows/                      # Workflow定义
├── expert-library/                 # 专家知识库
├── schemas/                        # 数据Schema定义
├── config.yaml                     # 模块配置
├── build.js                        # 构建脚本
├── README.md                       # 本文档
└── _module-installer/              # 安装器
    └── installer.js
```

---

## 架构说明

### 源码 vs 分发目录

**源码目录** (`src/modules/ppt/`):
- 开发时编辑的YAML格式agents
- 版本控制的原始文件
- 构建脚本和配置

**分发目录** (`bmad/ppt/`):
- **自动生成**的Markdown格式agents（包含XML结构）
- 构建产物，不应手动编辑
- 实际被BMAD框架加载的文件

**关系**: `src/modules/ppt/` --[build.js]--> `bmad/ppt/`

---

## 开发工作流

### 1. 修改Agent

编辑YAML源文件：
```bash
# 修改某个agent
vim src/modules/ppt/agents/story-designer.agent.yaml
```

### 2. 构建模块

将YAML转换为Markdown（XML格式）：
```bash
# 方式1: 使用npm script
npm run build:ppt

# 方式2: 直接执行构建脚本
node src/modules/ppt/build.js
```

### 3. 测试验证

```bash
# 检查生成的文件
ls -la bmad/ppt/agents/

# 验证XML结构
grep -A 5 '<agent id=' bmad/ppt/agents/story-designer.md

# 测试Slash Command
/bmad-ppt
```

### 4. 版本控制

```bash
# 仅提交源码，不提交构建产物
git add src/modules/ppt/
git commit -m "feat(ppt): update story-designer agent"

# 构建产物由CI/CD或安装器自动生成
```

---

## 构建系统

### 构建脚本功能

`build.js` 执行以下操作：

1. **转换Agents**: YAML → Markdown (XML格式)
   - 使用 `YamlXmlBuilder` 工具
   - 生成符合BMAD规范的XML结构

2. **复制资源**:
   - workflows/
   - expert-library/
   - schemas/
   - config.yaml

3. **生成元数据**:
   - `.build-meta.json` (构建时间、版本、哈希等)

4. **验证完整性**:
   - 检查关键文件存在
   - 验证XML结构正确

### 构建输出

```
bmad/ppt/
├── agents/                     # 生成的Markdown agents
│   ├── ppt-master.md           # 包含<agent>...</agent> XML结构
│   ├── story-designer.md
│   └── ...
├── workflows/                  # 从src复制
├── expert-library/             # 从src复制
├── schemas/                    # 从src复制
├── config.yaml                 # 从src复制
└── .build-meta.json            # 构建元数据
```

---

## Agent格式说明

### YAML格式 (源码)

```yaml
agent:
  metadata:
    id: bmad/ppt/agents/story-designer.md
    name: Story Designer
    title: PPT故事设计师
    icon: 📖
    module: ppt

  persona:
    role: PPT创建系统Stage 1的专家Agent...
    identity: 拥有丰富的叙事设计经验...
    communication_style: 专业、结构化...
    principles: 坚持"受众优先"原则...

  critical_actions:
    - 加载配置 {project-root}/bmad/ppt/config.yaml
    - 加载叙事模板库...
    - 所有推荐必须引用@模板路径

  menu:
    - description: 🚀 开始Story设计
      trigger: start-design
      workflow: "{project-root}/bmad/ppt/workflows/..."
```

### Markdown格式 (构建产物)

```markdown
<agent id="bmad/ppt/agents/story-designer.md">

<activation critical="MANDATORY">
<instructions>
加载配置 {project-root}/bmad/ppt/config.yaml
...
</instructions>
</activation>

<persona>
<role>PPT创建系统Stage 1的专家Agent...</role>
...
</persona>

<menu>
<item cmd="*start-design">🚀 开始Story设计</item>
...
</menu>

</agent>
```

---

## 与BMAD框架集成

### Slash Commands

创建后可用的命令：

```bash
/bmad-ppt           # 主入口（ppt-master）
/bmad-ppt-story     # Story设计
/bmad-ppt-page      # 页面规划
/bmad-ppt-visual    # 视觉设计
/bmad-ppt-content   # 内容生产
/bmad-ppt-file      # 文件生成
```

### Workflow注册

在 `bmad/_cfg/workflow-manifest.csv`:
```csv
"ppt-creator","Complete 5-stage PPT creation workflow","ppt","bmad/ppt/workflows/ppt-creator-workflow.yaml"
```

---

## 安装流程

```bash
# 1. 运行安装器
bash bmad/ppt/_module-installer/install.sh

# 安装器会自动：
# - 触发构建（npm run build:ppt）
# - 创建Slash Commands
# - 注册Workflow到manifest
# - 验证安装完整性
```

---

## 参考资料

**架构参考**:
- `src/modules/aps/` - APS模块（相同架构）
- `src/modules/aps/build.js` - 构建脚本参考

**文档**:
- `docs/ppt-agent-system/bmad-integration-plan.md` - 迁移计划
- `openspec/changes/migrate-ppt-to-bmad-arch/` - OpenSpec提案

**工具**:
- `tools/cli/lib/yaml-xml-builder.js` - YAML→XML构建工具

---

## 常见问题

**Q: 为什么要分离源码和分发目录？**
A: 遵循软件工程最佳实践，源码易于编辑和版本控制，分发产物自动化生成，确保一致性。

**Q: 可以直接编辑 bmad/ppt/agents/*.md 吗？**
A: 不建议。这些是构建产物，下次构建时会被覆盖。应编辑 src/modules/ppt/agents/*.agent.yaml。

**Q: 如何添加新的Agent？**
A: 在 src/modules/ppt/agents/ 创建新的 .agent.yaml 文件，参考现有agent格式，然后运行 npm run build:ppt。

**Q: 构建失败怎么办？**
A: 检查YAML语法是否正确，路径引用是否存在，查看构建日志定位具体错误。

---

**维护者**: BMAD Team
**最后更新**: 2025-11-23
**架构版本**: BMAD-METHOD v6
