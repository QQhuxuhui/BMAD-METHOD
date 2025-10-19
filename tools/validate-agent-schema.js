/**
 * Agent Schema Validator CLI
 *
 * Scans all *.agent.yaml files in src/{core,modules/*}/agents/
 * and validates them against the Zod schema.
 *
 * Usage: node test/validate-agent-schema.js
 * Exit codes: 0 = success, 1 = validation failures
 */

const { glob } = require('glob');
const yaml = require('js-yaml');
const fs = require('node:fs');
const path = require('node:path');
const { validateAgentFile } = require('./schema/agent.js');

/**
 * Main validation routine
 */
async function main() {
  console.log('🔍 Scanning for agent files...\n');

  // Find all agent files
  const agentFiles = await glob('src/{core,modules/*}/agents/*.agent.yaml', {
    cwd: path.join(__dirname, '..'),
    absolute: true,
  });

  if (agentFiles.length === 0) {
    console.log('⚠️  No agent files found.');
    process.exit(0);
  }

  console.log(`Found ${agentFiles.length} agent file(s)\n`);

  const errors = [];

  // Validate each file
  for (const filePath of agentFiles) {
    const relativePath = path.relative(process.cwd(), filePath);

    try {
      const fileContent = fs.readFileSync(filePath, 'utf8');
      const agentData = yaml.load(fileContent);

      // Convert absolute path to relative src/ path for module detection
      const srcRelativePath = relativePath.startsWith('src/')
        ? relativePath
        : path.relative(path.join(__dirname, '..'), filePath).replaceAll('\\', '/');

      const result = validateAgentFile(srcRelativePath, agentData);

      if (result.success) {
        console.log(`✅ ${relativePath}`);
      } else {
        errors.push({
          file: relativePath,
          issues: result.error.issues,
        });
      }
    } catch (error) {
      errors.push({
        file: relativePath,
        issues: [
          {
            code: 'parse_error',
            message: `Failed to parse YAML: ${error.message}`,
            path: [],
          },
        ],
      });
    }
  }

  // Report errors
  if (errors.length > 0) {
    console.log('\n❌ Validation failed for the following files:\n');

    for (const { file, issues } of errors) {
      console.log(`\n📄 ${file}`);
      for (const issue of issues) {
        const pathString = issue.path.length > 0 ? issue.path.join('.') : '(root)';
        console.log(`   Path: ${pathString}`);
        console.log(`   Error: ${issue.message}`);
        if (issue.code) {
          console.log(`   Code: ${issue.code}`);
        }
      }
    }

    console.log(`\n\n💥 ${errors.length} file(s) failed validation`);
    process.exit(1);
  }

  console.log(`\n✨ All ${agentFiles.length} agent file(s) passed validation!\n`);
  process.exit(0);
}

// Run
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
