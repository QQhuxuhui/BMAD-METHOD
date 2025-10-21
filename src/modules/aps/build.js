#!/usr/bin/env node
/* eslint-disable unicorn/prefer-module, n/no-process-exit, unicorn/no-process-exit, unicorn/prefer-top-level-await */

/**
 * APS Module Build Script - v2.0 (YAML Architecture)
 *
 * Builds the APS module using YamlXmlBuilder for agent conversion
 * and copying other resources from src/modules/aps to bmad/aps
 *
 * Architecture:
 * - Source: src/modules/aps/ (development - YAML agents)
 * - Target: bmad/aps/ (distribution - Markdown agents)
 *
 * Usage:
 *   node src/modules/aps/build.js
 *   npm run build:aps
 */

const path = require('node:path');
const fs = require('fs-extra');
const chalk = require('chalk');
const crypto = require('node:crypto');

// Import YamlXmlBuilder
const PROJECT_ROOT = path.resolve(__dirname, '../../..');
const { YamlXmlBuilder } = require(path.join(PROJECT_ROOT, 'tools/cli/lib/yaml-xml-builder'));

// Paths
const SOURCE_DIR = path.join(PROJECT_ROOT, 'src/modules/aps');
const TARGET_DIR = path.join(PROJECT_ROOT, 'bmad/aps');

// Files and directories to copy (non-agent content)
const COPY_ITEMS = [
  'workflows',
  'templates',
  'tasks',
  'config.yaml',
  'README.md',
  'MIGRATION_GUIDE.md',
  '_module-installer',
];

// Files to exclude from distribution
const EXCLUDE_PATTERNS = [
  'build.js',
  'scripts/',
  'agents-md-backup/',
  '*.backup',
  '.DS_Store',
  'node_modules',
  'DEVELOPMENT.md',
];

/**
 * Calculate hash of a directory or file
 */
function calculateHash(filePath) {
  const hash = crypto.createHash('sha256');

  if (fs.statSync(filePath).isDirectory()) {
    const files = fs.readdirSync(filePath, { recursive: true });
    files.sort();

    for (const file of files) {
      const fullPath = path.join(filePath, file);
      if (fs.statSync(fullPath).isFile()) {
        hash.update(fs.readFileSync(fullPath));
      }
    }
  } else {
    hash.update(fs.readFileSync(filePath));
  }

  return hash.digest('hex').substring(0, 8);
}

/**
 * Build agent files using YamlXmlBuilder
 */
async function buildAgents(builder) {
  console.log(chalk.cyan('\nBuilding agent files (YAML → Markdown)...'));

  const sourceAgentsDir = path.join(SOURCE_DIR, 'agents');
  const targetAgentsDir = path.join(TARGET_DIR, 'agents');

  // Ensure target agents directory exists
  await fs.ensureDir(targetAgentsDir);

  // Find all .agent.yaml files
  const files = await fs.readdir(sourceAgentsDir);
  const yamlFiles = files.filter(f => f.endsWith('.agent.yaml'));

  let builtCount = 0;

  for (const yamlFile of yamlFiles) {
    const yamlPath = path.join(sourceAgentsDir, yamlFile);
    const agentName = yamlFile.replace('.agent.yaml', '');
    const mdPath = path.join(targetAgentsDir, `${agentName}.md`);

    try {
      // Build agent using YamlXmlBuilder
      await builder.buildAgent(yamlPath, null, mdPath, {
        includeMetadata: true,
      });

      const hash = calculateHash(yamlPath);
      console.log(chalk.green(`  ✓ ${agentName}`), chalk.dim(`(hash: ${hash})`));
      builtCount++;
    } catch (error) {
      console.log(chalk.red(`  ✗ ${agentName}: ${error.message}`));
    }
  }

  return builtCount;
}

/**
 * Copy non-agent resources
 */
async function copyResources() {
  console.log(chalk.cyan('\nCopying resources...'));
  let copiedCount = 0;

  for (const item of COPY_ITEMS) {
    const sourcePath = path.join(SOURCE_DIR, item);
    const targetPath = path.join(TARGET_DIR, item);

    if (!(await fs.pathExists(sourcePath))) {
      console.log(chalk.yellow(`  ⚠️  Skipping (not found): ${item}`));
      continue;
    }

    await fs.copy(sourcePath, targetPath, {
      filter: (src) => {
        // Filter out excluded patterns
        for (const pattern of EXCLUDE_PATTERNS) {
          if (src.includes(pattern.replace('/', path.sep))) {
            return false;
          }
        }
        return true;
      },
    });

    const hash = calculateHash(sourcePath);
    console.log(chalk.green(`  ✓ ${item}`), chalk.dim(`(hash: ${hash})`));
    copiedCount++;
  }

  return copiedCount;
}

/**
 * Main build function
 */
async function build() {
  console.log(chalk.cyan('\n🏗️  Building APS Module (v2.0 - YAML Architecture)\n'));
  console.log(chalk.dim(`Source: ${SOURCE_DIR}`));
  console.log(chalk.dim(`Target: ${TARGET_DIR}\n`));

  try {
    // Ensure target directory exists
    await fs.ensureDir(TARGET_DIR);

    // Clean target directory (except backup)
    console.log(chalk.yellow('Cleaning target directory...'));
    const existingItems = await fs.readdir(TARGET_DIR);

    for (const item of existingItems) {
      if (item.includes('.backup')) {
        console.log(chalk.dim(`  Preserving: ${item}`));
        continue;
      }

      const itemPath = path.join(TARGET_DIR, item);
      await fs.remove(itemPath);
      console.log(chalk.dim(`  Removed: ${item}`));
    }

    // Initialize YamlXmlBuilder
    const builder = new YamlXmlBuilder();

    // Build agents
    const agentCount = await buildAgents(builder);

    // Copy resources
    const resourceCount = await copyResources();

    // Generate build metadata
    const buildMeta = {
      module: 'aps',
      version: '1.0.0-alpha',
      buildTime: new Date().toISOString(),
      source: 'src/modules/aps',
      architecture: 'BMAD-METHOD v6 - YAML',
      sourceHash: calculateHash(SOURCE_DIR),
      agents: agentCount,
      resources: resourceCount,
    };

    const metaPath = path.join(TARGET_DIR, '.build-meta.json');
    await fs.writeJson(metaPath, buildMeta, { spaces: 2 });

    // Summary
    console.log(chalk.cyan('\n📊 Build Summary'));
    console.log(chalk.green(`  ✓ Built ${agentCount} agents (YAML → MD)`));
    console.log(chalk.green(`  ✓ Copied ${resourceCount} resource items`));
    console.log(chalk.dim(`  Build hash: ${buildMeta.sourceHash}`));
    console.log(chalk.dim(`  Build time: ${buildMeta.buildTime}`));

    // Verify critical files
    console.log(chalk.cyan('\n🔍 Verifying build...'));
    const criticalFiles = [
      'config.yaml',
      'README.md',
      'agents/orchestrator.md',
      'agents/algorithm-expert.md',
      'templates/algorithm-library',
      'workflows/scheduling-orchestration',
    ];

    let verifyCount = 0;
    for (const file of criticalFiles) {
      const filePath = path.join(TARGET_DIR, file);
      if (await fs.pathExists(filePath)) {
        console.log(chalk.green(`  ✓ ${file}`));
        verifyCount++;
      } else {
        console.log(chalk.red(`  ✗ ${file} - MISSING!`));
      }
    }

    if (verifyCount === criticalFiles.length) {
      console.log(chalk.green('\n✅ Build completed successfully!\n'));
      console.log(chalk.cyan('📝 Architecture Notes:'));
      console.log(chalk.dim('  - Agents: YAML (source) → Markdown (dist)'));
      console.log(chalk.dim('  - Build tool: YamlXmlBuilder'));
      console.log(chalk.dim('  - Activation blocks: Auto-generated\n'));
      return 0;
    } else {
      console.log(chalk.red('\n❌ Build verification failed!\n'));
      return 1;
    }
  } catch (error) {
    console.error(chalk.red('\n❌ Build failed:'), error.message);
    if (process.env.DEBUG) {
      console.error(error.stack);
    }
    return 1;
  }
}

// Run build
if (require.main === module) {
  build()
    .then((code) => process.exit(code)) // eslint-disable-line unicorn/no-process-exit
    .catch((error) => {
      console.error(error);
      process.exit(1); // eslint-disable-line unicorn/no-process-exit
    });
}

module.exports = { build };
