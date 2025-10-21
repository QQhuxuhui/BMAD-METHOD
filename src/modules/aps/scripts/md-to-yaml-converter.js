#!/usr/bin/env node
/* eslint-disable unicorn/prefer-module, unicorn/prefer-string-slice, unicorn/prefer-top-level-await */

/**
 * MD to YAML Converter for APS Agents
 *
 * Converts APS agent Markdown files (with XML) to YAML format
 * to match the BMAD-METHOD v6 architecture standard.
 */

const fs = require('fs-extra');
const path = require('node:path');
const yaml = require('js-yaml');

class MDToYAMLConverter {
  /**
   * Extract text content from XML tag
   */
  extractTag(content, tagName) {
    const openTag = `<${tagName}>`;
    const closeTag = `</${tagName}>`;

    const start = content.indexOf(openTag);
    if (start === -1) return null;

    const end = content.indexOf(closeTag, start);
    if (end === -1) return null;

    return content.substring(start + openTag.length, end).trim();
  }

  /**
   * Extract agent metadata from <agent> tag attributes
   */
  extractMetadata(content) {
    const agentTagMatch = content.match(/<agent\s+([^>]+)>/);
    if (!agentTagMatch) {
      throw new Error('No <agent> tag found');
    }

    const attrs = agentTagMatch[1];
    const metadata = {};

    // Extract attributes
    const idMatch = attrs.match(/id="([^"]+)"/);
    const nameMatch = attrs.match(/name="([^"]+)"/);
    const titleMatch = attrs.match(/title="([^"]+)"/);
    const iconMatch = attrs.match(/icon="([^"]+)"/);

    if (idMatch) metadata.id = idMatch[1];
    if (nameMatch) metadata.name = nameMatch[1];
    if (titleMatch) metadata.title = titleMatch[1];
    if (iconMatch) metadata.icon = iconMatch[1];

    // Add module (always aps for APS agents)
    metadata.module = 'aps';

    return metadata;
  }

  /**
   * Extract persona section
   */
  extractPersona(content) {
    const personaContent = this.extractTag(content, 'persona');
    if (!personaContent) return null;

    const persona = {};

    // Extract role
    const role = this.extractTag(personaContent, 'role');
    if (role) persona.role = role;

    // Extract identity
    const identity = this.extractTag(personaContent, 'identity');
    if (identity) persona.identity = identity;

    // Extract communication_style
    const commStyle = this.extractTag(personaContent, 'communication_style');
    if (commStyle) persona.communication_style = commStyle;

    // Extract principles
    const principles = this.extractTag(personaContent, 'principles');
    if (principles) persona.principles = principles;

    return persona;
  }

  /**
   * Extract critical actions
   */
  extractCriticalActions(content) {
    const criticalActionsContent = this.extractTag(content, 'critical-actions');
    if (!criticalActionsContent) return [];

    const actions = [];

    // Match all <i>...</i> tags
    const iTagRegex = /<i[^>]*>(.*?)<\/i>/gs;
    let match;

    while ((match = iTagRegex.exec(criticalActionsContent)) !== null) {
      const actionText = match[1].trim();
      if (actionText) {
        actions.push(actionText);
      }
    }

    return actions;
  }

  /**
   * Extract menu items
   */
  extractMenu(content) {
    const menuContent = this.extractTag(content, 'menu');
    if (!menuContent) return [];

    const menuItems = [];

    // Match all <item>...</item> tags
    const itemRegex = /<item\s+([^>]+)>(.*?)<\/item>/gs;
    let match;

    while ((match = itemRegex.exec(menuContent)) !== null) {
      const attrs = match[1];
      const description = match[2].trim();

      // Skip help and exit (auto-injected)
      if (description.includes('显示所有') || description.includes('退出')) {
        continue;
      }

      const item = { description };

      // Extract cmd (trigger)
      const cmdMatch = attrs.match(/cmd="([^"]+)"/);
      if (cmdMatch) {
        let trigger = cmdMatch[1];
        // Remove * prefix
        if (trigger.startsWith('*')) {
          trigger = trigger.substring(1);
        }
        item.trigger = trigger;
      }

      // Extract workflow/exec/tmpl
      const workflowMatch = attrs.match(/(?:run-)?workflow="([^"]+)"/);
      const execMatch = attrs.match(/exec="([^"]+)"/);
      const tmplMatch = attrs.match(/tmpl="([^"]+)"/);

      if (workflowMatch) item.workflow = workflowMatch[1];
      if (execMatch) item.exec = execMatch[1];
      if (tmplMatch) item.tmpl = tmplMatch[1];

      menuItems.push(item);
    }

    return menuItems;
  }

  /**
   * Convert MD file to YAML structure
   */
  convertFile(mdFilePath) {
    const content = fs.readFileSync(mdFilePath, 'utf8');

    // Extract XML content between <agent> and </agent> tags
    const agentStart = content.indexOf('<agent');
    const agentEnd = content.indexOf('</agent>');

    if (agentStart === -1 || agentEnd === -1) {
      throw new Error('No <agent> tag found in MD file');
    }

    // Extract the complete agent XML (including the closing tag)
    const xmlContent = content.substring(agentStart, agentEnd + '</agent>'.length);

    // Build YAML structure
    const agent = {
      metadata: this.extractMetadata(xmlContent),
      persona: this.extractPersona(xmlContent),
    };

    // Add critical actions if any
    const criticalActions = this.extractCriticalActions(xmlContent);
    if (criticalActions.length > 0) {
      agent.critical_actions = criticalActions;
    }

    // Add menu
    const menu = this.extractMenu(xmlContent);
    if (menu.length > 0) {
      agent.menu = menu;
    }

    return { agent };
  }

  /**
   * Convert all agents in a directory
   */
  async convertDirectory(sourceDir, targetDir) {
    console.log(`Converting agents from ${sourceDir} to ${targetDir}\n`);

    // Ensure target directory exists
    await fs.ensureDir(targetDir);

    // Find all .md files in source directory
    const files = await fs.readdir(sourceDir);
    const mdFiles = files.filter(f => f.endsWith('.md'));

    const results = [];

    for (const mdFile of mdFiles) {
      const mdPath = path.join(sourceDir, mdFile);
      const yamlFileName = mdFile.replace('.md', '.agent.yaml');
      const yamlPath = path.join(targetDir, yamlFileName);

      try {
        console.log(`Converting: ${mdFile} → ${yamlFileName}`);

        // Convert
        const yamlStructure = this.convertFile(mdPath);

        // Generate YAML content
        let yamlContent = '# APS Agent Definition\n';
        yamlContent += `# Converted from ${mdFile}\n\n`;
        yamlContent += yaml.dump(yamlStructure, {
          indent: 2,
          lineWidth: 120,
          noRefs: true,
        });

        // Write YAML file
        await fs.writeFile(yamlPath, yamlContent, 'utf8');

        console.log(`  ✓ Generated: ${yamlPath}\n`);
        results.push({ file: mdFile, status: 'success' });
      } catch (error) {
        console.error(`  ✗ Error: ${error.message}\n`);
        results.push({ file: mdFile, status: 'error', error: error.message });
      }
    }

    return results;
  }
}

// Main execution
async function main() {
  const converter = new MDToYAMLConverter();

  const SOURCE_DIR = path.join(__dirname, '../agents');
  const TARGET_DIR = path.join(__dirname, '../agents-yaml');

  console.log('APS Agent MD → YAML Converter\n');
  console.log('=' .repeat(60) + '\n');

  const results = await converter.convertDirectory(SOURCE_DIR, TARGET_DIR);

  // Summary
  console.log('=' .repeat(60));
  console.log('\nConversion Summary:');
  console.log(`  Total files: ${results.length}`);
  console.log(`  Success: ${results.filter(r => r.status === 'success').length}`);
  console.log(`  Errors: ${results.filter(r => r.status === 'error').length}`);

  if (results.some(r => r.status === 'error')) {
    console.log('\nFailed files:');
    results.filter(r => r.status === 'error').forEach(r => {
      console.log(`  - ${r.file}: ${r.error}`);
    });
  }

  console.log('');
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { MDToYAMLConverter };
