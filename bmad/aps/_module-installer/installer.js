const chalk = require('chalk');
const path = require('node:path');
const fs = require('fs-extra');
const yaml = require('js-yaml');
const { XmlHandler } = require('../../../../tools/cli/lib/xml-handler');

/**
 * APS Module Installer
 * Custom installer that copies files from bmad/aps/ (where they currently reside)
 * and generates config.yaml based on user's configuration choices
 *
 * @param {Object} options - Installation options
 * @param {string} options.projectRoot - The root directory of the target project
 * @param {Object} options.config - Module configuration from install-menu-config.yaml
 * @param {Array<string>} options.installedIDEs - Array of IDE codes that were installed
 * @param {Object} options.logger - Logger instance for output
 * @returns {Promise<boolean>} - Success status
 */
async function install(options) {
  const { projectRoot, config, installedIDEs, logger } = options;

  try {
    logger.log(chalk.blue('🏗️  Installing APS Module...'));

    // Source: bmad/aps in the framework repository
    // Target: bmad/aps in the user's project
    const frameworkRoot = path.resolve(__dirname, '../../../..');
    const sourceDir = path.join(frameworkRoot, 'bmad', 'aps');
    const targetDir = path.join(projectRoot, 'bmad', 'aps');

    // Ensure source directory exists
    if (!(await fs.pathExists(sourceDir))) {
      throw new Error(`APS source directory not found at: ${sourceDir}`);
    }

    logger.log(chalk.cyan(`  Copying APS files from: ${sourceDir}`));
    logger.log(chalk.cyan(`  Installing to: ${targetDir}`));

    // Create target directory
    await fs.ensureDir(targetDir);

    // Copy all files from bmad/aps/ to user project
    // Exclude _module-installer directory and template config.yaml
    const filesToCopy = await getFilesToCopy(sourceDir);

    for (const file of filesToCopy) {
      const srcFile = path.join(sourceDir, file);
      const destFile = path.join(targetDir, file);

      await fs.ensureDir(path.dirname(destFile));
      await fs.copy(srcFile, destFile, { overwrite: true });
    }

    logger.log(chalk.cyan(`  ✓ Copied ${filesToCopy.length} files`));

    // Process agent files to inject activation blocks
    await processAgentFiles(targetDir, logger);

    // Generate config.yaml from collected configuration
    await generateConfigYaml(targetDir, config, logger);

    // Create output directories
    await createOutputDirectories(projectRoot, config, logger);

    // Setup IDE configurations for APS module
    await setupIDEConfigurations(projectRoot, targetDir, installedIDEs, logger);

    logger.log(chalk.green('✓ APS Module installation complete'));
    logger.log(chalk.cyan('\n📚 Next steps:'));
    logger.log(chalk.cyan('  1. Populate expert libraries in bmad/aps/templates/'));
    logger.log(chalk.cyan('  2. Create task definitions in bmad/aps/tasks/'));
    logger.log(chalk.cyan('  3. Run: bmad aps (to activate the orchestrator)'));

    return true;
  } catch (error) {
    logger.error(chalk.red(`Error installing APS module: ${error.message}`));
    logger.error(chalk.dim(error.stack));
    return false;
  }
}

/**
 * Get list of files to copy (excluding certain directories/files)
 */
async function getFilesToCopy(sourceDir) {
  const files = [];

  async function walk(dir, baseDir = dir) {
    const entries = await fs.readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.relative(baseDir, fullPath);

      // Skip _module-installer directory
      if (entry.name === '_module-installer') {
        continue;
      }

      // Skip template config.yaml (we'll generate a real one)
      if (relativePath === 'config.yaml') {
        continue;
      }

      if (entry.isDirectory()) {
        await walk(fullPath, baseDir);
      } else {
        files.push(relativePath);
      }
    }
  }

  await walk(sourceDir);
  return files;
}

/**
 * Generate config.yaml from user's configuration choices
 */
async function generateConfigYaml(targetDir, userConfig, logger) {
  logger.log(chalk.cyan('  Generating config.yaml...'));

  const config = {
    module_name: 'Advanced Planning & Scheduling',
    module_code: 'aps',
    version: '1.0.0-alpha',

    // User Configuration
    user_name: userConfig.user_name || 'User',
    communication_language: userConfig.communication_language || 'Chinese',

    // Module Settings
    orchestration_mode: userConfig.orchestration_mode || 'centralized',
    confidence_threshold: 0.7,
    todo_tracking_enabled: userConfig.enable_todo_tracking !== false,
    human_in_loop_enabled: userConfig.enable_human_in_loop !== false,

    // Output Paths
    output_folder: userConfig.output_folder || 'aps-outputs',
    models_folder: userConfig.models_output_location || 'aps-outputs/models',
    workflows_folder: 'workflows',
    reports_folder: userConfig.reports_output_location || 'aps-outputs/reports',

    // Quality Gates
    quality_gates: {
      syntax_check: true,
      logic_verification: true,
      constraint_consistency: true,
      benchmark_evaluation: true,
      citation_required: true,
    },

    // Expert Library Paths
    expert_libraries: {
      orchestrator: 'templates/orchestrator-library',
      algorithm: 'templates/algorithm-library',
      constraint: 'templates/constraint-library',
      objective: 'templates/objective-library',
      domain: 'templates/domain-library',
      extension: 'templates/extension-library',
      quality: 'templates/quality-library',
      modeling: 'templates/modeling-library',
      collaboration: 'templates/collaboration',
      examples: 'templates/examples',
    },

    // Interaction Modes
    interaction_modes: {
      mode_a: {
        name: '集中确认模式',
        description: '快速高效，全局视角',
        estimated_time: '20-25分钟',
        user_type: '专家用户',
      },
      mode_b: {
        name: '增量确认模式',
        description: '渐进式，上下文丰富',
        estimated_time: '30-40分钟',
        user_type: '业务用户',
      },
    },

    // Phase Configuration
    phases: {
      phase_0: {
        name: '任务规划',
        enabled: true,
        todo_generation: true,
      },
      phase_0_5: {
        name: '交互模式选择',
        enabled: true,
        mode_selection: true,
      },
      phase_1: {
        name: '需求分析',
        enabled: true,
        deviation_detection: true,
      },
      phase_1_5: {
        name: '十要素建模',
        enabled: true,
        user_confirmation_required: true,
      },
      phase_2: {
        name: '专家协调',
        enabled: true,
        consistency_check: true,
      },
      phase_3: {
        name: '方案集成',
        enabled: true,
        conflict_resolution: true,
      },
      phase_4: {
        name: '质量保证',
        enabled: true,
        quality_gates: true,
      },
    },
  };

  const configPath = path.join(targetDir, 'config.yaml');
  const yamlContent = yaml.dump(config, {
    indent: 2,
    lineWidth: -1,
    noRefs: true,
  });

  // Add header comment
  const header = '# APS Module Configuration\n' + '# Advanced Planning & Scheduling Module for BMAD-CORE v6\n\n';

  await fs.writeFile(configPath, header + yamlContent, 'utf8');
  logger.log(chalk.cyan('  ✓ Generated config.yaml'));
}

/**
 * Create output directories
 */
async function createOutputDirectories(projectRoot, userConfig, logger) {
  logger.log(chalk.cyan('  Creating output directories...'));

  const outputDirs = [
    userConfig.models_output_location || 'aps-outputs/models',
    userConfig.reports_output_location || 'aps-outputs/reports',
    'aps-outputs/workflows',
  ];

  for (const dir of outputDirs) {
    const fullPath = path.join(projectRoot, dir);
    await fs.ensureDir(fullPath);
  }

  logger.log(chalk.cyan('  ✓ Created output directories'));
}

/**
 * Process agent files to inject activation blocks
 */
async function processAgentFiles(targetDir, logger) {
  logger.log(chalk.cyan('  Processing agent files...'));

  const agentsPath = path.join(targetDir, 'agents');

  if (!(await fs.pathExists(agentsPath))) {
    logger.log(chalk.yellow('  ⚠ No agents directory found'));
    return;
  }

  const xmlHandler = new XmlHandler();
  const agentFiles = await fs.readdir(agentsPath);
  let processedCount = 0;

  for (const agentFile of agentFiles) {
    if (!agentFile.endsWith('.md')) continue;

    const agentPath = path.join(agentsPath, agentFile);
    let content = await fs.readFile(agentPath, 'utf8');

    // Check if content has agent XML and no activation block
    if (content.includes('<agent') && !content.includes('<activation')) {
      // Inject the activation block
      content = xmlHandler.injectActivationSimple(content);
      await fs.writeFile(agentPath, content, 'utf8');
      processedCount++;
    }
  }

  logger.log(chalk.cyan(`  ✓ Processed ${processedCount} agent files`));
}

/**
 * Setup IDE configurations for APS module
 */
async function setupIDEConfigurations(projectRoot, apsDir, installedIDEs, logger) {
  // Skip if no IDEs were installed
  if (!installedIDEs || installedIDEs.length === 0) {
    logger.log(chalk.dim('  ⓘ No IDE configurations to update (no IDEs were selected during installation)'));
    return;
  }

  logger.log(chalk.cyan('  Setting up IDE configurations for APS module...'));

  try {
    // Import IDE manager to get IDE instances
    const { IdeManager } = require('../../../../tools/cli/installers/lib/ide/manager');
    const ideManager = new IdeManager();

    const bmadDir = path.join(projectRoot, 'bmad');

    // Setup each installed IDE
    for (const ideCode of installedIDEs) {
      try {
        // Use IdeManager.setup() method which handles IDE lookup and execution
        const result = await ideManager.setup(ideCode, projectRoot, bmadDir, {
          selectedModules: ['aps'],
          skipManifest: true, // Don't regenerate manifest, just update IDE configs
        });

        if (result.success) {
          logger.log(chalk.dim(`  ✓ Updated ${ideCode} configuration`));
        } else if (result.reason === 'unsupported') {
          logger.log(chalk.dim(`  ⓘ ${ideCode} not yet supported (skipping)`));
        } else {
          logger.log(chalk.yellow(`  ⚠ Failed to setup ${ideCode}: ${result.error || 'Unknown error'}`));
        }
      } catch (ideError) {
        logger.log(chalk.yellow(`  ⚠ Failed to setup ${ideCode}: ${ideError.message}`));
        // Don't fail the entire installation if one IDE setup fails
      }
    }

    logger.log(chalk.cyan(`  ✓ IDE configurations updated for ${installedIDEs.length} IDE(s)`));
  } catch (error) {
    logger.log(chalk.yellow(`  ⚠ IDE configuration setup failed: ${error.message}`));
    logger.log(chalk.dim('  You may need to manually run the installation to update IDE configurations'));
    // Don't throw - IDE setup failure shouldn't block module installation
  }
}

module.exports = { install };
