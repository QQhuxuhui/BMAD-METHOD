# Database Schema

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    INDEX idx_email (email)
);

-- 工作流执行表
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    thread_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL,
    current_phase VARCHAR(10) NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0.0,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- 智能体执行表
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    token_count INTEGER DEFAULT 0,
    model_used VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    INDEX idx_workflow_id (workflow_id)
);

-- 人工确认表
CREATE TABLE human_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    approval_point VARCHAR(10) NOT NULL,
    context_data JSONB NOT NULL,
    decision VARCHAR(20),
    feedback TEXT,
    modified_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    decided_at TIMESTAMP,
    INDEX idx_workflow_id (workflow_id)
);

-- 模型配置表
CREATE TABLE model_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    provider VARCHAR(20) NOT NULL,
    api_base_url VARCHAR(500) NOT NULL,
    api_key VARCHAR(500) NOT NULL,
    model_version VARCHAR(100) NOT NULL,
    max_tokens INTEGER DEFAULT 4096,
    temperature DECIMAL(3, 2) DEFAULT 0.7,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 10
);
```

---
