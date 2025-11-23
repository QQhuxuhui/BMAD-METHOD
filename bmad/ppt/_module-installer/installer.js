/* eslint-disable unicorn/prefer-module, n/no-process-exit */

/**
 * PPT Module Installer
 *
 * Handles installation of the PPT Creator module:
 * - Triggers build (npm run build:ppt)
 * - Creates Slash Commands
 * - Registers workflow to manifest
 * - Verifies installation
 */

const path = require('node:path');
const fs = require('fs-extra');
const chalk = require('chalk');
const { execSync } = require('node:child_process');

// Detect PROJECT_ROOT based on current location
// This installer can run from src/modules/ppt/_module-installer or bmad/ppt/_module-installer
const possibleRoots = [
  path.resolve(__dirname, '../../../..'),  // from src/modules/ppt/_module-installer
  path.resolve(__dirname, '../../..')      // from bmad/ppt/_module-installer
];

let PROJECT_ROOT;
for (const root of possibleRoots) {
  if (fs.existsSync(path.join(root, 'package.json'))) {
    PROJECT_ROOT = root;
    break;
  }
}

if (!PROJECT_ROOT) {
  console.error('Error: Could not find project root');
  process.exit(1);
}

/**
 * Trigger build
 */
async function triggerBuild() {
  console.log(chalk.cyan('\n🏗️  构建PPT模块...'));

  const buildScript = path.join(PROJECT_ROOT, 'src/modules/ppt/build.js');
  if (await fs.pathExists(buildScript)) {
    try {
      execSync('npm run build:ppt', {
        cwd: PROJECT_ROOT,
        stdio: 'inherit'
      });
      console.log(chalk.green('✅ 构建完成\n'));
    } catch (error) {
      throw new Error(`构建失败: ${error.message}`);
    }
  } else {
    console.log(chalk.yellow('⚠️  未找到构建脚本，跳过构建\n'));
  }
}

/**
 * Register to BMAD framework
 */
async function registerToBMAD() {
  console.log(chalk.cyan('📋 注册到BMAD框架...'));

  // 1. Create Slash Commands
  const commandsDir = path.join(PROJECT_ROOT, '.claude/commands/bmad');
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
    const filePath = path.join(commandsDir, filename);
    await fs.writeFile(filePath, content);
    const cmdName = filename.replace('.md', '');
    console.log(chalk.green(`  ✓ Created /bmad-${cmdName}`));
  }

  // 2. Register Workflow
  const manifestPath = path.join(PROJECT_ROOT, 'bmad/_cfg/workflow-manifest.csv');
  if (await fs.pathExists(manifestPath)) {
    const content = await fs.readFile(manifestPath, 'utf-8');
    if (!content.includes('ppt-creator')) {
      await fs.appendFile(manifestPath,
        '\n"ppt-creator","Complete 5-stage PPT creation: Story → Pages → Visual → Content → File. 8 themes, 20 layouts, HITL at 2 key points","ppt","bmad/ppt/workflows/ppt-creator-workflow.yaml"'
      );
      console.log(chalk.green('  ✓ Registered ppt-creator workflow'));
    } else {
      console.log(chalk.dim('  - ppt-creator workflow already registered'));
    }
  }

  console.log(chalk.green('✅ BMAD框架注册完成\n'));
}

/**
 * Verify installation
 */
async function verifyInstallation() {
  console.log(chalk.cyan('🔍 验证安装...'));

  const checks = [
    { path: 'bmad/ppt/agents/ppt-master.md', name: 'ppt-master agent' },
    { path: 'bmad/ppt/agents/story-designer.md', name: 'story-designer agent' },
    { path: 'bmad/ppt/config.yaml', name: 'config file' },
    { path: 'bmad/ppt/expert-library', name: 'expert library' },
    { path: 'bmad/ppt/workflows/ppt-creator-workflow.yaml', name: 'workflow' },
    { path: '.claude/commands/bmad/ppt.md', name: '/bmad-ppt command' },
    { path: '.claude/commands/bmad/ppt-story.md', name: '/bmad-ppt-story command' },
  ];

  let allValid = true;

  for (const { path: checkPath, name } of checks) {
    const fullPath = path.join(PROJECT_ROOT, checkPath);
    if (await fs.pathExists(fullPath)) {
      console.log(chalk.green(`  ✓ ${name}`));
    } else {
      console.log(chalk.red(`  ✗ ${name} (missing)`));
      allValid = false;
    }
  }

  return allValid;
}

/**
 * Main install function
 */
async function install() {
  console.log(chalk.cyan('\n' + '═'.repeat(60)));
  console.log(chalk.cyan('📦 PPT Creator Module Installation'));
  console.log(chalk.cyan('═'.repeat(60) + '\n'));

  try {
    // Trigger build
    await triggerBuild();

    // Register to BMAD
    await registerToBMAD();

    // Verify installation
    const isValid = await verifyInstallation();

    // Summary
    console.log(chalk.cyan('\n' + '═'.repeat(60)));
    if (isValid) {
      console.log(chalk.green('✅ PPT模块安装成功！'));
      console.log(chalk.cyan('═'.repeat(60)));
      console.log(chalk.white('\n可用命令:'));
      console.log(chalk.white('  /bmad-ppt           - PPT创建系统主入口'));
      console.log(chalk.white('  /bmad-ppt-story     - Story设计 (Stage 1)'));
      console.log(chalk.white('  /bmad-ppt-page      - Page规划 (Stage 2)'));
      console.log(chalk.white('  /bmad-ppt-visual    - Visual设计 (Stage 3)'));
      console.log(chalk.white('  /bmad-ppt-content   - Content生产 (Stage 4)'));
      console.log(chalk.white('  /bmad-ppt-file      - File生成 (Stage 5)'));
      console.log(chalk.cyan('\n' + '═'.repeat(60) + '\n'));
      process.exit(0);
    } else {
      console.log(chalk.yellow('⚠️  安装完成但存在警告'));
      console.log(chalk.cyan('═'.repeat(60) + '\n'));
      process.exit(1);
    }
  } catch (error) {
    console.log(chalk.red('\n❌ 安装失败！'));
    console.log(chalk.red(`Error: ${error.message}`));
    console.log(chalk.dim(error.stack));
    process.exit(1);
  }
}

// Run install if executed directly
if (require.main === module) {
  install();
}

module.exports = { install, triggerBuild, registerToBMAD };
