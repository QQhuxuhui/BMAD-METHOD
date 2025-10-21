# 专家库文档标准格式规范

## 文档结构标准

所有专家文档必须遵循以下标准格式：

````yaml
---
version: "4.0"
category: "theory-design" | "implementation" | "quality-assurance"
layer: 1 | 2 | 3
dependencies: ["expert1", "expert2"]
templates: ["template1.py", "template2.py"]
updated: "2024-12-22"
status: "active" | "draft" | "deprecated"
---

# 专家名称

## 专家身份与定位
- 专家角色定义
- 在V4.0架构中的位置
- 与其他专家的协作关系

## 核心能力规范
### V4.0新增能力
- 可执行规格输出能力
- Theory-to-Code转换能力

### 传统能力保留
- 原有专业能力描述

## 输入接口规范
### 标准输入格式
```yaml
input_format:
  type: "business_requirement" | "algorithm_spec" | "code_package"
  structure: "具体的输入数据结构"
  validation: "输入验证规则"
````

## 输出接口规范

### V4.0可执行输出

```yaml
output_format:
  type: "executable_specification" | "production_code" | "deployment_package"
  structure: "具体的输出数据结构"
  quality_gates: "质量验证标准"
```

## 协作流程定义

### 层内协作

- 同层专家协作机制
- 任务分配和同步方式

### 跨层协作

- 与上下游层的接口标准
- 质量门禁和验证流程

## 代码模板关联

### 关联模板列表

- template1.py: 描述和用途
- template2.py: 描述和用途

### 模板使用规范

- 如何选择合适的模板
- 模板参数配置方法

## 质量标准

### 输出质量要求

- 可执行性: >95%
- 完整性: >90%
- 一致性: 100%

### 性能指标

- 响应时间要求
- 资源使用限制

```

## 文件命名规范

```

docs/agents/
├── theory-design/
│ ├── system-orchestrator.md
│ ├── algorithm-expert.md
│ ├── constraint-expert.md
│ ├── objective-expert.md
│ ├── domain-expert.md
│ └── extension-expert.md
├── implementation/
│ ├── programming-architect.md
│ ├── algorithm-implementer.md
│ ├── data-model-specialist.md
│ └── integration-specialist.md
├── quality-assurance/
│ ├── test-designer.md
│ ├── code-reviewer.md
│ ├── performance-optimizer.md
│ └── deployment-specialist.md
└── templates/
├── genetic-algorithm-template.py
├── particle-swarm-optimization-template.py
└── constraint-handler-template.py

````

## 版本管理规范

### 版本号格式
- 主版本.次版本.修订版本 (如: 4.0.1)
- 主版本：架构重大变更
- 次版本：功能增加或重要修改
- 修订版本：bug修复和小幅改进

### 变更追踪
- 每次修改必须更新updated字段
- 重要变更需要在CHANGELOG中记录
- 保持与aps-scheduling-agents版本同步

## 转换映射规则

### 元数据映射
```yaml
docs_metadata → package_config:
  version → package.json.version
  category → agent.category
  dependencies → agent.dependencies
  templates → agent.templates
````

### 内容映射

```yaml
content_mapping:
  "# 专家名称" → agent.name
  "## 核心能力规范" → agent.capabilities
  "## 输入接口规范" → agent.input_interface
  "## 输出接口规范" → agent.output_interface
  "## 协作流程定义" → agent.collaboration_protocol
```

## 质量保证机制

### 文档验证

1. 格式完整性检查
2. 必填字段验证
3. 依赖关系检查
4. 模板文件存在性验证

### 转换验证

1. 转换前后语义一致性
2. 接口规范完整性
3. 质量标准符合性
4. 版本同步验证

这个标准确保了docs/agents作为唯一权威源的地位，同时为工程化转换提供了明确的规则和验证机制。
