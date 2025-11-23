# Spec: 安装器升级 (Installer Upgrade)

**Capability ID**: `installer-upgrade`
**Change**: `migrate-ppt-to-bmad-arch`
**Status**: Proposed

---

## ADDED Requirements

### Requirement: Update Installer File Location

The installer file location MUST be updated to follow the source-distribution separation pattern.

**ID**: `installer-upgrade-mod-001`
**Priority**: P0 (Critical)

**Acceptance Criteria**:

- 两个位置的安装器保持同步
- 用户仍从`bmad/ppt/_module-installer/`执行安装

#### Scenario: 安装器文件在两个位置保持同步

**Given**: 构建系统已配置
**When**: 执行`npm run build:ppt`
**Then**:

- `src/modules/ppt/_module-installer/`内容被复制到`bmad/ppt/_module-installer/`
- 两个目录的installer.js内容完全一致

**Validation**:

```bash
diff src/modules/ppt/_module-installer/installer.js bmad/ppt/_module-installer/installer.js
test $? -eq 0
```

---

## Cross-References

**依赖于**:

- `build-system` - 需要调用构建脚本
- `slash-command-integration` - 需要创建命令文件

**被依赖于**:

- 无（这是最后一步）

---

## Implementation Notes

**关键函数结构**:

```javascript
// src/modules/ppt/_module-installer/installer.js

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
    'ppt-file.md': '@/bmad/ppt/agents/file-generator.md',
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
      await fs.appendFile(
        manifestPath,
        '\n"ppt-creator","Complete 5-stage PPT creation workflow","ppt","bmad/ppt/workflows/ppt-creator-workflow.yaml"',
      );
      console.log(chalk.green('  ✓ Registered ppt-creator workflow'));
    } else {
      console.log(chalk.dim('  ℹ️  Workflow already registered'));
    }
  }

  console.log(chalk.green('✅ BMAD框架注册完成\n'));
}

async function install() {
  // ... 现有逻辑 ...

  await triggerBuild(); // 新增
  await registerToBMAD(); // 新增

  // ... 后续逻辑 ...
}
```

---

_此spec由OpenSpec系统生成 - 2025-11-23_
