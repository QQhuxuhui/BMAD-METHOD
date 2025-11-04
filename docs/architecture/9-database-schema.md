# 9. Database Schema

## 9.1 PostgreSQL表结构

```sql
-- workflows表
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'running', 'paused', 'completed', 'failed')),
    current_phase VARCHAR(10) CHECK (current_phase IN ('P0', 'P1', 'P2', 'P2.5', 'P3', 'P4')),
    config JSONB NOT NULL,
    checkpoint_id VARCHAR(255),
    human_confirmation_required BOOLEAN DEFAULT false,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_started_at ON workflows(started_at DESC);

-- agent_executions表
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN (
        'orchestrator', 'algorithm', 'constraint', 'objective',
        'domain', 'code_implementation', 'extension', 'quality'
    )),
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    input JSONB NOT NULL,
    output JSONB,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration NUMERIC(10, 2),
    token_usage JSONB,
    error JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_executions_workflow_id ON agent_executions(workflow_id);
CREATE INDEX idx_agent_executions_agent_type ON agent_executions(agent_type);

-- agent_messages表
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_execution_id UUID NOT NULL REFERENCES agent_executions(id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('text', 'thought', 'result', 'error', 'system')),
    content TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_agent_messages_agent_execution_id ON agent_messages(agent_execution_id);
CREATE INDEX idx_agent_messages_workflow_id ON agent_messages(workflow_id);

-- human_confirmations表
CREATE TABLE human_confirmations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    trigger_point VARCHAR(10) NOT NULL CHECK (trigger_point IN ('P1', 'P2', 'P2.5')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'approved', 'rejected', 'modified', 'timeout')),
    context JSONB NOT NULL,
    decision JSONB,
    requested_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    responded_at TIMESTAMP WITH TIME ZONE,
    timeout INTEGER NOT NULL DEFAULT 3600,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_human_confirmations_workflow_id ON human_confirmations(workflow_id);
CREATE INDEX idx_human_confirmations_status ON human_confirmations(status);

-- model_configs表
CREATE TABLE model_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('qwen', 'glm', 'deepseek')),
    model_name VARCHAR(255) NOT NULL,
    deployment_type VARCHAR(50) NOT NULL CHECK (deployment_type IN ('local_vllm', 'local_ollama', 'cloud_api')),
    endpoint TEXT NOT NULL,
    api_key TEXT,
    enabled BOOLEAN DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 0,
    config JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(provider, model_name)
);

CREATE INDEX idx_model_configs_enabled ON model_configs(enabled);
CREATE INDEX idx_model_configs_priority ON model_configs(priority DESC);
```

---
