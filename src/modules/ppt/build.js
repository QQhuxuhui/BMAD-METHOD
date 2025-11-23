/* eslint-disable unicorn/prefer-module, n/no-process-exit, unicorn/prefer-top-level-await */

/**
 * PPT Module Build Script - v1.0 (YAML Architecture)
 *
 * Builds the PPT module using YamlXmlBuilder for agent conversion
 * and copying other resources from src/modules/ppt to bmad/ppt
 *
 * Architecture:
 * - Source: src/modules/ppt/ (development - YAML agents)
 * - Target: bmad/ppt/ (distribution - Markdown agents)
 *
 * Usage:
 *   node src/modules/ppt/build.js
 *   npm run build:ppt
 */

const path = require('node:path');
const fs = require('fs-extra');
const chalk = require('chalk');
const crypto = require('node:crypto');

// Import YamlXmlBuilder
const PROJECT_ROOT = path.resolve(__dirname, '../../..');
const { YamlXmlBuilder } = require(path.join(PROJECT_ROOT, 'tools/cli/lib/yaml-xml-builder'));

// Paths
const SOURCE_DIR = path.join(PROJECT_ROOT, 'src/modules/ppt');
const TARGET_DIR = path.join(PROJECT_ROOT, 'bmad/ppt');

// Files and directories to copy (non-agent content)
const COPY_ITEMS = [
  'workflows',
  'expert-library',
  'schemas',
  'config.yaml',
  'README.md',
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

  return hash.digest('hex').slice(0, 8);
}

/**
 * Recursively find all .agent.yaml files
 */
async function findAgentFiles(dir, basePath = '') {
  const results = [];
  const items = await fs.readdir(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = await fs.stat(fullPath);

    if (stat.isDirectory()) {
      const subResults = await findAgentFiles(fullPath, path.join(basePath, item));
      results.push(...subResults);
    } else if (item.endsWith('.agent.yaml')) {
      results.push({
        yamlPath: fullPath,
        relativePath: path.join(basePath, item),
        agentName: item.replace('.agent.yaml', ''),
        mdName: item.replace('.agent.yaml', '.md'),
      });
    }
  }

  return results;
}

/**
 * Build agent files using YamlXmlBuilder
 */
async function buildAgents(builder) {
  console.log(chalk.cyan('\n🔨 Building agent files (YAML → Markdown)...'));

  const sourceAgentsDir = path.join(SOURCE_DIR, 'agents');
  const targetAgentsDir = path.join(TARGET_DIR, 'agents');

  // Ensure target agents directory exists
  await fs.ensureDir(targetAgentsDir);
  await fs.ensureDir(path.join(targetAgentsDir, 'helpers'));

  // Find all .agent.yaml files (including in subdirectories)
  const agentFiles = await findAgentFiles(sourceAgentsDir);

  console.log(chalk.dim(`  Found ${agentFiles.length} agent files`));

  let builtCount = 0;
  const errors = [];

  for (const { yamlPath, relativePath, agentName, mdName } of agentFiles) {
    try {
      // Determine target path (preserve subdirectory structure)
      const relativeDir = path.dirname(relativePath);
      const targetSubDir = path.join(targetAgentsDir, relativeDir);
      await fs.ensureDir(targetSubDir);

      const mdPath = path.join(targetSubDir, mdName);

      // Build agent using YamlXmlBuilder
      await builder.buildAgent(yamlPath, null, mdPath, {
        includeMetadata: true,
      });

      const hash = calculateHash(yamlPath);
      const displayPath = relativePath.replace('.agent.yaml', '');
      console.log(chalk.green(`  ✓ ${displayPath}`), chalk.dim(`(hash: ${hash})`));
      builtCount++;
    } catch (error) {
      const displayPath = relativePath.replace('.agent.yaml', '');
      console.log(chalk.red(`  ✗ ${displayPath}: ${error.message}`));
      errors.push({ agent: agentName, error: error.message });
    }
  }

  if (errors.length > 0) {
    console.log(chalk.red(`\n⚠️  Build errors: ${errors.length}`));
    for (const { agent, error } of errors) {
      console.log(chalk.red(`  - ${agent}: ${error}`));
    }
  }

  return builtCount;
}

/**
 * Copy non-agent resources
 */
async function copyResources() {
  console.log(chalk.cyan('\n📦 Copying resources...'));
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
 * Verify build output
 */
async function verifyBuild() {
  console.log(chalk.cyan('\n🔍 Verifying build...'));

  const checks = [
    { path: path.join(TARGET_DIR, 'agents/ppt-master.md'), name: 'ppt-master.md' },
    { path: path.join(TARGET_DIR, 'agents/story-designer.md'), name: 'story-designer.md' },
    { path: path.join(TARGET_DIR, 'agents/page-planner.md'), name: 'page-planner.md' },
    { path: path.join(TARGET_DIR, 'agents/visual-stylist.md'), name: 'visual-stylist.md' },
    { path: path.join(TARGET_DIR, 'agents/content-producer.md'), name: 'content-producer.md' },
    { path: path.join(TARGET_DIR, 'agents/file-generator.md'), name: 'file-generator.md' },
    {
      path: path.join(TARGET_DIR, 'agents/helpers/copywriter.md'),
      name: 'helpers/copywriter.md',
    },
    {
      path: path.join(TARGET_DIR, 'agents/helpers/chart-specialist.md'),
      name: 'helpers/chart-specialist.md',
    },
    { path: path.join(TARGET_DIR, 'config.yaml'), name: 'config.yaml' },
    { path: path.join(TARGET_DIR, 'expert-library'), name: 'expert-library/' },
    { path: path.join(TARGET_DIR, 'schemas'), name: 'schemas/' },
    { path: path.join(TARGET_DIR, 'workflows'), name: 'workflows/' },
  ];

  let allValid = true;

  for (const { path: checkPath, name } of checks) {
    if (await fs.pathExists(checkPath)) {
      console.log(chalk.green(`  ✓ ${name}`));
    } else {
      console.log(chalk.red(`  ✗ ${name} (missing)`));
      allValid = false;
    }
  }

  // Verify XML structure in agents
  console.log(chalk.cyan('\n🔍 Verifying XML structure...'));

  const agentFiles = [
    'agents/ppt-master.md',
    'agents/story-designer.md',
    'agents/page-planner.md',
    'agents/visual-stylist.md',
    'agents/content-producer.md',
    'agents/file-generator.md',
    'agents/helpers/copywriter.md',
    'agents/helpers/chart-specialist.md',
  ];

  for (const agentFile of agentFiles) {
    const agentPath = path.join(TARGET_DIR, agentFile);
    if (await fs.pathExists(agentPath)) {
      const content = await fs.readFile(agentPath, 'utf-8');

      // Check for XML structure
      const hasAgentTag = content.includes('<agent id=');
      const hasActivation = content.includes('<activation');
      const hasPersona = content.includes('<persona>');
      const hasMenu = content.includes('<menu>');

      if (hasAgentTag && hasActivation && hasPersona && hasMenu) {
        console.log(chalk.green(`  ✓ ${agentFile} (valid XML)`));
      } else {
        console.log(chalk.yellow(`  ⚠️  ${agentFile} (incomplete XML structure)`));
        allValid = false;
      }
    }
  }

  return allValid;
}

/**
 * Generate build metadata
 */
async function generateBuildMeta() {
  console.log(chalk.cyan('\n📝 Generating build metadata...'));

  const buildMeta = {
    module: 'ppt',
    version: '1.0.0',
    buildTime: new Date().toISOString(),
    source: 'src/modules/ppt',
    architecture: 'BMAD-METHOD v6 - YAML',
    sourceHash: calculateHash(SOURCE_DIR),
    agents: 8,
    resources: 6,
    buildStatus: 'success',
  };

  const metaPath = path.join(TARGET_DIR, '.build-meta.json');
  await fs.writeJson(metaPath, buildMeta, { spaces: 2 });

  console.log(chalk.green('  ✓ .build-meta.json'));
  console.log(chalk.dim(`  Source hash: ${buildMeta.sourceHash}`));
  console.log(chalk.dim(`  Build time: ${buildMeta.buildTime}`));

  return buildMeta;
}

/**
 * Main build function
 */
async function build() {
  const startTime = Date.now();

  console.log(chalk.cyan('\n🚀 Building PPT Module (v1.0 - YAML Architecture)\n'));
  console.log(chalk.dim(`Source: ${SOURCE_DIR}`));
  console.log(chalk.dim(`Target: ${TARGET_DIR}\n`));

  try {
    // Ensure target directory exists
    await fs.ensureDir(TARGET_DIR);

    // Clean target directory (except backup and state)
    console.log(chalk.yellow('🧹 Cleaning target directory...'));
    const existingItems = await fs.readdir(TARGET_DIR);

    for (const item of existingItems) {
      if (item.includes('.backup') || item === 'state') {
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
    await generateBuildMeta();

    // Verify build
    const isValid = await verifyBuild();

    // Summary
    const buildTime = ((Date.now() - startTime) / 1000).toFixed(2);

    console.log(chalk.cyan('\n' + '═'.repeat(60)));
    console.log(chalk.green('✅ Build completed successfully!'));
    console.log(chalk.cyan('═'.repeat(60)));
    console.log(chalk.white(`  Agents built: ${agentCount}`));
    console.log(chalk.white(`  Resources copied: ${resourceCount}`));
    console.log(chalk.white(`  Build time: ${buildTime}s`));
    console.log(chalk.white(`  Validation: ${isValid ? '✓ Passed' : '⚠️  Issues detected'}`));
    console.log(chalk.cyan('═'.repeat(60) + '\n'));

    if (!isValid) {
      console.log(chalk.yellow('⚠️  Build completed with warnings. Please review verification output.\n'));
      process.exit(1);
    }

    process.exit(0);
  } catch (error) {
    console.log(chalk.red('\n❌ Build failed!'));
    console.log(chalk.red(`Error: ${error.message}`));
    console.log(chalk.dim(error.stack));
    process.exit(1);
  }
}

// Run build if executed directly
if (require.main === module) {
  build();
}

module.exports = { build };
