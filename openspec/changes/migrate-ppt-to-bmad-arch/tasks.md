# 实施任务清单 (Implementation Tasks)

**Change ID**: `migrate-ppt-to-bmad-arch`
**项目**: PPT智能体系统BMAD架构迁移
**版本**: v1.0
**开始日期**: 2025-11-23
**预计完成**: 2025-11-25 (2个工作日)

---

## 总体里程碑

| 里程碑 | 时间 | 交付物 | 状态 |
|--------|------|--------|------|
| **M1**: 源码迁移完成 | Day 1 上午 | 源码目录 + 资源复制 | ⏳ Pending |
| **M2**: Agents转换完成 | Day 1 下午 | 8个YAML agents | ⏳ Pending |
| **M3**: 构建系统工作 | Day 2 上午 | build.js + npm script | ⏳ Pending |
| **M4**: 框架集成完成 | Day 2 下午 | Slash Commands + 测试通过 | ⏳ Pending |

---

## Day 1 上午: 源码目录迁移 (3小时)

### TASK-001: 创建源码目录结构

**优先级**: P0
**时间**: 15分钟
**依赖**: 无

**步骤**:
- [ ] 创建`src/modules/ppt/`根目录
- [ ] 创建子目录：`agents/`, `agents/helpers/`, `workflows/`, `expert-library/`, `schemas/`, `_module-installer/`
- [ ] 验证目录权限（可读可写）

**验收标准**:
```bash
test -d src/modules/ppt/agents
test -d src/modules/ppt/agents/helpers
test -d src/modules/ppt/workflows
test -d src/modules/ppt/expert-library
test -d src/modules/ppt/schemas
test -d src/modules/ppt/_module-installer
```

**交付物**: 完整的源码目录结构

---

### TASK-002: 备份现有bmad/ppt目录

**优先级**: P0
**时间**: 10分钟
**依赖**: 无

**步骤**:
- [ ] 执行`cp -r bmad/ppt bmad/ppt.backup-$(date +%Y%m%d)`
- [ ] 验证备份完整性（文件数量和大小）
- [ ] 记录备份路径到日志

**验收标准**:
```bash
test -d bmad/ppt.backup-20251123
diff -r bmad/ppt bmad/ppt.backup-20251123
```

**交付物**: 完整备份目录

---

### TASK-003: 复制资源文件到源码目录

**优先级**: P0
**时间**: 30分钟
**依赖**: TASK-001

**步骤**:
- [ ] 复制`bmad/ppt/expert-library/` → `src/modules/ppt/expert-library/`
- [ ] 复制`bmad/ppt/schemas/` → `src/modules/ppt/schemas/`
- [ ] 复制`bmad/ppt/workflows/` → `src/modules/ppt/workflows/`
- [ ] 复制`bmad/ppt/config.yaml` → `src/modules/ppt/config.yaml`
- [ ] 复制`bmad/ppt/_module-installer/` → `src/modules/ppt/_module-installer/`
- [ ] 验证每个目录的完整性（使用diff）

**验收标准**:
```bash
diff -r bmad/ppt/expert-library src/modules/ppt/expert-library
diff -r bmad/ppt/schemas src/modules/ppt/schemas
diff bmad/ppt/config.yaml src/modules/ppt/config.yaml
test $? -eq 0  # 所有diff应返回0（无差异）
```

**交付物**: 完整的资源文件副本

---

### TASK-004: 创建源码README文档

**优先级**: P2
**时间**: 20分钟
**依赖**: TASK-001

**步骤**:
- [ ] 创建`src/modules/ppt/README.md`
- [ ] 添加章节：Architecture、Development Workflow、Build System
- [ ] 说明与`bmad/ppt/`的关系（源码vs分发）
- [ ] 添加构建命令说明

**验收标准**:
```bash
test -f src/modules/ppt/README.md
grep -q "Development Workflow" src/modules/ppt/README.md
grep -q "Build System" src/modules/ppt/README.md
grep -q "npm run build:ppt" src/modules/ppt/README.md
```

**交付物**: 开发者文档

---

### TASK-005: 验证资源完整性

**优先级**: P0
**时间**: 15分钟
**依赖**: TASK-003

**步骤**:
- [ ] 执行完整性验证脚本（检查关键文件清单）
- [ ] 验证YAML文件格式有效性
- [ ] 检查目录结构完整性
- [ ] 生成验证报告

**验收标准**:
```bash
# 验证关键文件存在
test -f src/modules/ppt/config.yaml
test -f src/modules/ppt/workflows/ppt-creator-workflow.yaml
test -d src/modules/ppt/expert-library/story-design
test -d src/modules/ppt/expert-library/page-planning
test -d src/modules/ppt/expert-library/visual-design

# 验证文件数量
test $(find src/modules/ppt/expert-library -name "*.yaml" | wc -l) -gt 30
```

**交付物**: 验证通过报告

---

## Day 1 下午: Agent格式转换 (3-4小时)

### TASK-006: 转换story-designer agent

**优先级**: P0
**时间**: 30分钟
**依赖**: TASK-005

**步骤**:
- [ ] 阅读`bmad/ppt/agents/story-designer.md`
- [ ] 创建`src/modules/ppt/agents/story-designer.agent.yaml`
- [ ] 添加metadata（id, name, title, icon, module）
- [ ] 添加persona（role, identity, communication_style, principles）
- [ ] 添加critical_actions（至少4条）
- [ ] 添加menu（至少3个选项）
- [ ] 验证YAML语法
- [ ] 参考`src/modules/aps/agents/orchestrator.agent.yaml`格式

**验收标准**:
```bash
test -f src/modules/ppt/agents/story-designer.agent.yaml
node -e "
const yaml = require('js-yaml');
const fs = require('fs');
const agent = yaml.load(fs.readFileSync('src/modules/ppt/agents/story-designer.agent.yaml', 'utf8'));
if (!agent.agent.metadata) throw new Error('Missing metadata');
if (!agent.agent.persona) throw new Error('Missing persona');
if (!agent.agent.critical_actions || agent.agent.critical_actions.length < 4) throw new Error('Insufficient critical_actions');
if (!agent.agent.menu || agent.agent.menu.length < 3) throw new Error('Insufficient menu');
console.log('✅ story-designer agent valid');
"
```

**交付物**: `story-designer.agent.yaml`

---

### TASK-007: 转换page-planner agent

**优先级**: P0
**时间**: 30分钟
**依赖**: TASK-006

**步骤**:
- [ ] 同TASK-006，转换`page-planner.md` → `page-planner.agent.yaml`
- [ ] 验证Stage 2相关的critical_actions
- [ ] 验证page-planning expert-library引用路径

**验收标准**:
```bash
test -f src/modules/ppt/agents/page-planner.agent.yaml
grep -q "page-planning" src/modules/ppt/agents/page-planner.agent.yaml
```

**交付物**: `page-planner.agent.yaml`

---

### TASK-008: 转换visual-stylist agent

**优先级**: P0
**时间**: 30分钟
**依赖**: TASK-006

**步骤**:
- [ ] 同TASK-006，转换`visual-stylist.md` → `visual-stylist.agent.yaml`
- [ ] 验证theme和layout相关的menu选项
- [ ] 验证visual-design expert-library引用

**验收标准**:
```bash
test -f src/modules/ppt/agents/visual-stylist.agent.yaml
grep -q "visual-design" src/modules/ppt/agents/visual-stylist.agent.yaml
```

**交付物**: `visual-stylist.agent.yaml`

---

### TASK-009: 转换content-producer agent

**优先级**: P0
**时间**: 30分钟
**依赖**: TASK-006

**步骤**:
- [ ] 同TASK-006，转换`content-producer.md` → `content-producer.agent.yaml`
- [ ] 验证helpers调用逻辑（copywriter、chart-specialist）
- [ ] 验证content-production expert-library引用

**验收标准**:
```bash
test -f src/modules/ppt/agents/content-producer.agent.yaml
grep -q "copywriter" src/modules/ppt/agents/content-producer.agent.yaml
grep -q "chart-specialist" src/modules/ppt/agents/content-producer.agent.yaml
```

**交付物**: `content-producer.agent.yaml`

---

### TASK-010: 转换file-generator agent

**优先级**: P0
**时间**: 20分钟
**依赖**: TASK-006

**步骤**:
- [ ] 同TASK-006，转换`file-generator.md` → `file-generator.agent.yaml`
- [ ] 简化版本（file-generator逻辑较简单）

**验收标准**:
```bash
test -f src/modules/ppt/agents/file-generator.agent.yaml
grep -q "file-generation" src/modules/ppt/agents/file-generator.agent.yaml
```

**交付物**: `file-generator.agent.yaml`

---

### TASK-011: 转换helpers agents

**优先级**: P1
**时间**: 30分钟
**依赖**: TASK-006

**步骤**:
- [ ] 转换`helpers/copywriter.md` → `helpers/copywriter.agent.yaml`
- [ ] 转换`helpers/chart-specialist.md` → `helpers/chart-specialist.agent.yaml`
- [ ] 简化版本（helper agents功能单一）

**验收标准**:
```bash
test -f src/modules/ppt/agents/helpers/copywriter.agent.yaml
test -f src/modules/ppt/agents/helpers/chart-specialist.agent.yaml
```

**交付物**: 2个helper agents

---

### TASK-012: 创建ppt-master主入口agent

**优先级**: P0
**时间**: 40分钟
**依赖**: TASK-005

**步骤**:
- [ ] 创建`src/modules/ppt/agents/ppt-master.agent.yaml`
- [ ] 设计主菜单结构（8个选项）
- [ ] 添加完整workflow入口（*create-ppt）
- [ ] 添加5个单阶段agent入口
- [ ] 添加辅助功能入口（*load-example、*check-status）
- [ ] 验证所有menu路径引用正确

**验收标准**:
```bash
test -f src/modules/ppt/agents/ppt-master.agent.yaml
grep -q "create-ppt" src/modules/ppt/agents/ppt-master.agent.yaml
grep -q "story-design" src/modules/ppt/agents/ppt-master.agent.yaml
grep -q "page-plan" src/modules/ppt/agents/ppt-master.agent.yaml
grep -q "visual-design" src/modules/ppt/agents/ppt-master.agent.yaml
grep -q "content-produce" src/modules/ppt/agents/ppt-master.agent.yaml
grep -q "file-generate" src/modules/ppt/agents/ppt-master.agent.yaml
grep -q "load-example" src/modules/ppt/agents/ppt-master.agent.yaml
grep -q "check-status" src/modules/ppt/agents/ppt-master.agent.yaml
```

**交付物**: `ppt-master.agent.yaml`（主入口Agent）

---

### TASK-013: 验证所有agents YAML格式

**优先级**: P0
**时间**: 15分钟
**依赖**: TASK-012

**步骤**:
- [ ] 批量验证所有8个`.agent.yaml`文件
- [ ] 检查YAML语法有效性
- [ ] 验证schema结构完整性
- [ ] 生成验证报告

**验收标准**:
```bash
test $(find src/modules/ppt/agents -name "*.agent.yaml" | wc -l) -eq 8

# 批量YAML语法验证
for f in src/modules/ppt/agents/**/*.agent.yaml; do
  node -e "
    const yaml = require('js-yaml');
    const fs = require('fs');
    try {
      yaml.load(fs.readFileSync('$f', 'utf8'));
      console.log('✅ $f valid');
    } catch(e) {
      console.error('❌ $f invalid:', e.message);
      process.exit(1);
    }
  "
done
```

**交付物**: 所有agents验证通过

---

## Day 2 上午: 构建系统集成 (3小时)

### TASK-014: 创建build.js构建脚本

**优先级**: P0
**时间**: 1.5小时
**依赖**: TASK-013

**步骤**:
- [ ] 创建`src/modules/ppt/build.js`
- [ ] 参考`src/modules/aps/build.js`实现
- [ ] 导入`YamlXmlBuilder`工具
- [ ] 实现`buildAgents()`函数（YAML→Markdown转换）
- [ ] 实现`copyResources()`函数（复制workflows、expert-library等）
- [ ] 实现`generateBuildMeta()`函数（生成`.build-meta.json`）
- [ ] 实现`verifyBuild()`函数（验证关键文件）
- [ ] 添加错误处理和日志输出

**验收标准**:
```bash
test -f src/modules/ppt/build.js
node src/modules/ppt/build.js
test $? -eq 0  # 构建成功
```

**交付物**: `build.js`构建脚本

---

### TASK-015: 测试构建系统

**优先级**: P0
**时间**: 30分钟
**依赖**: TASK-014

**步骤**:
- [ ] 执行`node src/modules/ppt/build.js`
- [ ] 验证`bmad/ppt/agents/`包含8个`.md`文件
- [ ] 验证所有`.md`文件包含XML activation blocks
- [ ] 验证`.build-meta.json`格式正确
- [ ] 验证资源文件已复制（expert-library、schemas等）

**验收标准**:
```bash
test $(find bmad/ppt/agents -name "*.md" | wc -l) -eq 8
test -f bmad/ppt/.build-meta.json

# 验证XML结构
grep -q '<agent id=' bmad/ppt/agents/story-designer.md
grep -q '<activation critical="MANDATORY">' bmad/ppt/agents/story-designer.md
grep -q '<persona>' bmad/ppt/agents/story-designer.md
grep -q '<menu>' bmad/ppt/agents/story-designer.md

# 验证资源复制
diff -r src/modules/ppt/expert-library bmad/ppt/expert-library
test $? -eq 0
```

**交付物**: 构建产物验证通过

---

### TASK-016: 集成到package.json

**优先级**: P0
**时间**: 10分钟
**依赖**: TASK-015

**步骤**:
- [ ] 编辑`package.json`
- [ ] 在`scripts`中添加`"build:ppt": "node src/modules/ppt/build.js"`
- [ ] 测试`npm run build:ppt`

**验收标准**:
```bash
grep -q '"build:ppt"' package.json
npm run build:ppt
test $? -eq 0
```

**交付物**: npm script配置

---

### TASK-017: 验证生成的agents符合BMAD规范

**优先级**: P0
**时间**: 30分钟
**依赖**: TASK-015

**步骤**:
- [ ] 手动检查生成的`bmad/ppt/agents/ppt-master.md`
- [ ] 验证XML结构完整性
- [ ] 验证activation blocks正确
- [ ] 验证menu结构正确
- [ ] 对比与APS agents的格式一致性

**验收标准**:
```bash
# 验证ppt-master XML结构
grep -q '<agent id="bmad/ppt/agents/ppt-master.md"' bmad/ppt/agents/ppt-master.md
grep -q '<activation critical="MANDATORY">' bmad/ppt/agents/ppt-master.md
grep -q '<persona>' bmad/ppt/agents/ppt-master.md
grep -q '<menu>' bmad/ppt/agents/ppt-master.md
grep -q '<item cmd="\*create-ppt"' bmad/ppt/agents/ppt-master.md
```

**交付物**: BMAD规范合规验证报告

---

## Day 2 下午: 框架集成与测试 (3小时)

### TASK-018: 创建Slash Commands

**优先级**: P0
**时间**: 20分钟
**依赖**: TASK-017

**步骤**:
- [ ] 创建`.claude/commands/bmad/`目录（如不存在）
- [ ] 创建6个命令文件：
  - `ppt.md` → `@/bmad/ppt/agents/ppt-master.md`
  - `ppt-story.md` → `@/bmad/ppt/agents/story-designer.md`
  - `ppt-page.md` → `@/bmad/ppt/agents/page-planner.md`
  - `ppt-visual.md` → `@/bmad/ppt/agents/visual-stylist.md`
  - `ppt-content.md` → `@/bmad/ppt/agents/content-producer.md`
  - `ppt-file.md` → `@/bmad/ppt/agents/file-generator.md`

**验收标准**:
```bash
test $(find .claude/commands/bmad -name "ppt*.md" | wc -l) -eq 6
grep -q '@/bmad/ppt/agents/ppt-master.md' .claude/commands/bmad/ppt.md
grep -q '@/bmad/ppt/agents/story-designer.md' .claude/commands/bmad/ppt-story.md
```

**交付物**: 6个Slash Command文件

---

### TASK-019: 注册workflow到manifest

**优先级**: P0
**时间**: 10分钟
**依赖**: TASK-017

**步骤**:
- [ ] 编辑`bmad/_cfg/workflow-manifest.csv`
- [ ] 添加行：`"ppt-creator","Complete 5-stage PPT creation: Story → Pages → Visual → Content → File. 8 themes, 20 layouts, HITL at 2 key points","ppt","bmad/ppt/workflows/ppt-creator-workflow.yaml"`
- [ ] 验证CSV格式正确

**验收标准**:
```bash
grep -q 'ppt-creator' bmad/_cfg/workflow-manifest.csv
grep -q 'bmad/ppt/workflows/ppt-creator-workflow.yaml' bmad/_cfg/workflow-manifest.csv
```

**交付物**: Workflow注册条目

---

### TASK-020: 升级安装器

**优先级**: P0
**时间**: 1小时
**依赖**: TASK-018, TASK-019

**步骤**:
- [ ] 编辑`src/modules/ppt/_module-installer/installer.js`
- [ ] 添加`triggerBuild()`函数
- [ ] 添加`registerToBMAD()`函数
  - 创建Slash Commands逻辑
  - 注册Workflow逻辑
- [ ] 更新主`install()`函数调用新函数
- [ ] 添加错误处理和友好日志
- [ ] 复制到`bmad/ppt/_module-installer/`（构建时）

**验收标准**:
```bash
test -f src/modules/ppt/_module-installer/installer.js
grep -q 'triggerBuild' src/modules/ppt/_module-installer/installer.js
grep -q 'registerToBMAD' src/modules/ppt/_module-installer/installer.js
```

**交付物**: 升级版installer.js

---

### TASK-021: 测试完整安装流程

**优先级**: P0
**时间**: 30分钟
**依赖**: TASK-020

**步骤**:
- [ ] 清理环境（删除`.claude/commands/bmad/ppt*.md`）
- [ ] 执行`bash bmad/ppt/_module-installer/install.sh`
- [ ] 验证构建自动触发
- [ ] 验证Slash Commands创建
- [ ] 验证Workflow注册
- [ ] 检查日志输出清晰性

**验收标准**:
```bash
bash bmad/ppt/_module-installer/install.sh
test $? -eq 0

# 验证结果
test $(find .claude/commands/bmad -name "ppt*.md" | wc -l) -eq 6
test $(find bmad/ppt/agents -name "*.md" | wc -l) -eq 8
grep -q 'ppt-creator' bmad/_cfg/workflow-manifest.csv
```

**交付物**: 安装流程验证通过

---

### TASK-022: Slash Command激活测试

**优先级**: P0
**时间**: 20分钟
**依赖**: TASK-021

**步骤**:
- [ ] 在Claude Code中测试`/bmad-ppt`
- [ ] 验证ppt-master主菜单显示
- [ ] 测试`/bmad-ppt-story`
- [ ] 验证story-designer agent激活
- [ ] 测试其他4个单阶段命令

**验收标准**:
- `/bmad-ppt` → 显示主菜单，包含8个选项
- `/bmad-ppt-story` → 激活story-designer agent
- 所有6个命令均可正常激活

**交付物**: Slash Command功能验证通过

---

### TASK-023: 端到端PPT创建测试

**优先级**: P0
**时间**: 40分钟
**依赖**: TASK-022

**步骤**:
- [ ] 使用`/bmad-ppt`启动
- [ ] 选择`*create-ppt`（完整workflow）
- [ ] 使用quickstart示例输入
- [ ] 完成5阶段流程
- [ ] 验证生成的PPTX质量
- [ ] 对比迁移前后生成结果一致性

**验收标准**:
- 5阶段workflow正常运行
- Story Blueprint、Page Manifest、Visual Design Spec正常生成
- 最终PPTX文件生成成功
- 文件质量与迁移前一致

**交付物**: E2E测试通过报告

---

### TASK-024: 回归测试

**优先级**: P0
**时间**: 30分钟
**依赖**: TASK-023

**步骤**:
- [ ] 使用相同的quickstart-input.yaml
- [ ] 对比迁移前后生成的PPTX
- [ ] 验证内容结构一致
- [ ] 验证视觉设计一致
- [ ] 验证文件元数据一致

**验收标准**:
- Story Blueprint结构相同
- Page Manifest内容相同
- Visual Design Spec相同
- 生成的PPTX内容和格式完全一致

**交付物**: 回归测试通过报告

---

### TASK-025: 文档更新

**优先级**: P2
**时间**: 30分钟
**依赖**: TASK-024

**步骤**:
- [ ] 更新`bmad/ppt/README.md`（添加架构说明）
- [ ] 创建`MIGRATION_GUIDE.md`（迁移指南）
- [ ] 更新主项目README（如需要）
- [ ] 添加开发流程文档（build→test→install）

**验收标准**:
```bash
test -f bmad/ppt/README.md
test -f docs/ppt-agent-system/MIGRATION_GUIDE.md
grep -q "BMAD-METHOD v6" bmad/ppt/README.md
grep -q "npm run build:ppt" docs/ppt-agent-system/MIGRATION_GUIDE.md
```

**交付物**: 完整文档更新

---

## 验收测试场景

### 场景1: 构建系统验证

**Given**: 源码目录`src/modules/ppt/`已完成
**When**: 执行`npm run build:ppt`
**Then**:
- 构建成功，无错误
- `bmad/ppt/agents/`包含8个`.md`文件
- `.build-meta.json`格式正确
- 资源文件完整复制

**验证命令**:
```bash
npm run build:ppt
test $? -eq 0
test $(find bmad/ppt/agents -name "*.md" | wc -l) -eq 8
test -f bmad/ppt/.build-meta.json
```

---

### 场景2: Slash Command集成验证

**Given**: 安装器已运行
**When**: 在Claude Code中输入`/bmad-ppt`
**Then**:
- 激活ppt-master agent
- 显示主菜单（8个选项）
- 可选择完整workflow或单阶段agent

**手动验证**:
- `/bmad-ppt` → 主菜单显示
- `/bmad-ppt-story` → Story Designer激活
- `/bmad-ppt-page` → Page Planner激活
- 其他命令同理

---

### 场景3: 端到端PPT创建验证

**Given**: PPT模块已安装
**When**: 执行完整5阶段workflow
**Then**:
- Story Design阶段完成（Story Blueprint生成）
- Page Planning阶段完成（Page Manifest生成）
- Visual Design阶段完成（Visual Design Spec生成）
- Content Production阶段完成（Slide Content Package生成）
- File Generation阶段完成（PPTX文件生成）
- 生成的PPTX质量与迁移前一致

**手动验证**:
```
/bmad-ppt
→ 选择 *create-ppt
→ 输入quickstart示例
→ 确认Story (HITL)
→ 确认Visual Theme (HITL)
→ 获得最终PPTX文件
→ 对比文件质量
```

---

## 风险缓解措施

**备份策略**:
- ✅ 所有操作前备份`bmad/ppt/`
- ✅ 保留备份至少7天
- ✅ 文档化回滚步骤

**测试策略**:
- ✅ 每完成一个Agent就测试构建
- ✅ 增量验证，及时发现问题
- ✅ 端到端测试确保功能无变化

**质量门禁**:
- ✅ M1完成前：源码目录和资源验证通过
- ✅ M2完成前：所有8个agents YAML格式验证通过
- ✅ M3完成前：构建系统正常工作，生成文件符合规范
- ✅ M4完成前：E2E测试和回归测试通过

---

## 依赖关系图

```
TASK-001 (创建目录)
    ↓
TASK-002 (备份)
    ↓
TASK-003 (复制资源)
    ↓
TASK-005 (验证资源)
    ↓
TASK-006~012 (转换agents) → 并行执行
    ↓
TASK-013 (验证agents)
    ↓
TASK-014 (创建build.js)
    ↓
TASK-015 (测试构建)
    ↓
TASK-016 (npm集成)
    ↓
TASK-017 (验证BMAD规范)
    ↓
TASK-018 (Slash Commands)
    ↓
TASK-019 (注册workflow)
    ↓
TASK-020 (升级installer)
    ↓
TASK-021 (测试安装)
    ↓
TASK-022 (测试命令)
    ↓
TASK-023 (E2E测试)
    ↓
TASK-024 (回归测试)
    ↓
TASK-025 (文档更新)
    ↓
✅ 迁移完成
```

---

## 完成标准

**架构合规性**:
- [x] 源码目录`src/modules/ppt/`结构完整
- [x] 所有8个agents转换为YAML格式
- [x] 构建系统正常工作
- [x] 生成的agents符合BMAD XML规范

**功能完整性**:
- [x] 所有现有PPT功能保持不变
- [x] 5阶段workflow正常运行
- [x] 生成的PPTX质量一致

**框架集成**:
- [x] 6个Slash Commands可用
- [x] Workflow已注册
- [x] 安装器支持构建和注册

**质量验证**:
- [x] 构建无错误
- [x] E2E测试通过
- [x] 回归测试通过
- [x] 文档完整

---

_此任务清单由OpenSpec系统生成 - 2025-11-23_
