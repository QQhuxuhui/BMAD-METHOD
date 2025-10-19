// Zod schema definition for *.agent.yaml files
const { z } = require('zod');

const COMMAND_TARGET_KEYS = ['workflow', 'validate-workflow', 'exec', 'action', 'tmpl', 'data', 'run-workflow'];
const TRIGGER_PATTERN = /^\*?[a-z0-9]+(?:-[a-z0-9]+)*$/;
const KEBAB_CASE_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const BUILTIN_TRIGGER_PREFIX = '*';

// Public API ---------------------------------------------------------------

function agentSchema(options = {}) {
  const expectedModule = typeof options.module === 'string' && options.module.trim().length > 0 ? options.module.trim() : null;

  return z
    .object({
      agent: buildAgentSchema(expectedModule),
    })
    .strict()
    .superRefine((value, ctx) => {
      const seenTriggers = new Set();

      let index = 0;
      for (const item of value.agent.menu) {
        const triggerValue = item.trigger;

        if (!TRIGGER_PATTERN.test(triggerValue)) {
          ctx.addIssue({
            code: 'custom',
            path: ['agent', 'menu', index, 'trigger'],
            message: 'agent.menu[].trigger must be kebab-case (allowing an optional leading *)',
          });
          return;
        }

        const canonicalTrigger = triggerValue.startsWith(BUILTIN_TRIGGER_PREFIX) ? triggerValue.slice(1) : triggerValue;

        if (!KEBAB_CASE_PATTERN.test(canonicalTrigger)) {
          ctx.addIssue({
            code: 'custom',
            path: ['agent', 'menu', index, 'trigger'],
            message: 'agent.menu[].trigger must be kebab-case after removing the leading * prefix',
          });
          return;
        }

        if (seenTriggers.has(canonicalTrigger)) {
          ctx.addIssue({
            code: 'custom',
            path: ['agent', 'menu', index, 'trigger'],
            message: `agent.menu[].trigger duplicates "${canonicalTrigger}" within the same agent`,
          });
        } else {
          seenTriggers.add(canonicalTrigger);
        }
        index += 1;
      }
    });
}

module.exports = { agentSchema };

// Schema builders ----------------------------------------------------------

function buildAgentSchema(expectedModule) {
  return z
    .object({
      metadata: buildMetadataSchema(expectedModule),
      persona: buildPersonaSchema(),
      critical_actions: z.array(createNonEmptyString('agent.critical_actions[]')).optional(),
      menu: z.array(buildMenuItemSchema()).min(1, { message: 'agent.menu must include at least one entry' }),
      prompts: z.array(buildPromptSchema()).optional(),
    })
    .strict();
}

function buildMetadataSchema(expectedModule) {
  const schemaShape = {
    id: createNonEmptyString('agent.metadata.id'),
    name: createNonEmptyString('agent.metadata.name'),
    title: createNonEmptyString('agent.metadata.title'),
    icon: createNonEmptyString('agent.metadata.icon'),
    module: createNonEmptyString('agent.metadata.module').optional(),
  };

  return z
    .object(schemaShape)
    .strict()
    .superRefine((value, ctx) => {
      const moduleValue = typeof value.module === 'string' ? value.module.trim() : null;

      if (expectedModule && !moduleValue) {
        ctx.addIssue({
          code: 'custom',
          path: ['module'],
          message: 'module-scoped agents must declare agent.metadata.module',
        });
      } else if (!expectedModule && moduleValue) {
        ctx.addIssue({
          code: 'custom',
          path: ['module'],
          message: 'core agents must not include agent.metadata.module',
        });
      } else if (expectedModule && moduleValue !== expectedModule) {
        ctx.addIssue({
          code: 'custom',
          path: ['module'],
          message: `agent.metadata.module must equal "${expectedModule}"`,
        });
      }
    });
}

function buildPersonaSchema() {
  return z
    .object({
      role: createNonEmptyString('agent.persona.role'),
      identity: createNonEmptyString('agent.persona.identity'),
      communication_style: createNonEmptyString('agent.persona.communication_style'),
      principles: z
        .array(createNonEmptyString('agent.persona.principles[]'))
        .min(1, { message: 'agent.persona.principles must include at least one entry' }),
    })
    .strict();
}

function buildPromptSchema() {
  return z
    .object({
      id: createNonEmptyString('agent.prompts[].id'),
      content: z.string().refine((value) => value.trim().length > 0, {
        message: 'agent.prompts[].content must be a non-empty string',
      }),
      description: createNonEmptyString('agent.prompts[].description').optional(),
    })
    .strict();
}

function buildMenuItemSchema() {
  return z
    .object({
      trigger: createNonEmptyString('agent.menu[].trigger'),
      description: createNonEmptyString('agent.menu[].description'),
      workflow: createNonEmptyString('agent.menu[].workflow').optional(),
      'validate-workflow': createNonEmptyString('agent.menu[].validate-workflow').optional(),
      exec: createNonEmptyString('agent.menu[].exec').optional(),
      action: createNonEmptyString('agent.menu[].action').optional(),
      tmpl: createNonEmptyString('agent.menu[].tmpl').optional(),
      data: createNonEmptyString('agent.menu[].data').optional(),
      'run-workflow': createNonEmptyString('agent.menu[].run-workflow').optional(),
    })
    .strict()
    .superRefine((value, ctx) => {
      const hasCommandTarget = COMMAND_TARGET_KEYS.some((key) => {
        const commandValue = value[key];
        return typeof commandValue === 'string' && commandValue.trim().length > 0;
      });

      if (!hasCommandTarget) {
        ctx.addIssue({
          code: 'custom',
          message: 'agent.menu[] entries must include at least one command target field',
        });
      }
    });
}

// Primitive validators -----------------------------------------------------

function createNonEmptyString(label) {
  return z.string().refine((value) => value.trim().length > 0, {
    message: `${label} must be a non-empty string`,
  });
}
