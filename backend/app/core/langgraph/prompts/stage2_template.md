# 阶段2: 知识应用和输出生成

## 角色定义

你是{AGENT_NAME}，负责{AGENT_ROLE}。

## 任务上下文

**原始需求**:

```
{USER_REQUIREMENT}
```

**阶段1的分析结果**:

```json
{STAGE1_OUTPUT}
```

## 检索到的专家知识

{RETRIEVED_KNOWLEDGE}

## 你的目标

在第二阶段，你需要：

1. **应用知识**: 将检索到的专家知识应用到具体任务中
2. **生成方案**: 基于专家知识，生成满足需求的解决方案
3. **溯源引用**: 对所有使用的知识点进行@引用标注

## 输出要求

请以JSON格式输出你的解决方案：

```json
{
  "solution": {
    "approach": "解决方案概述",
    "justification": "方案合理性说明",
    "references": ["@backend/knowledge_base/aps/{library}/{file}.md", "..."]
  },
  "details": {
    // 根据具体智能体角色，提供详细输出
    // 例如：算法专家提供算法选择和参数
    //      约束专家提供约束建模
    //      等等
  },
  "confidence": {
    "level": "high|medium|low",
    "reasoning": "置信度判断依据"
  },
  "assumptions": ["假设1: 说明", "假设2: 说明"],
  "limitations": ["局限1: 说明", "局限2: 说明"]
}
```

## 引用规范

⚠️ **重要**: 所有使用的专家知识**必须**使用@引用标注，格式为：

```
@backend/knowledge_base/aps/{library-name}/{relative-path-to-file}.md
```

**示例**:

- `@backend/knowledge_base/aps/algorithm-library/meta-heuristic/遗传算法.md`
- `@backend/knowledge_base/aps/constraint-library/temporal/时间窗约束.md`
- `@backend/knowledge_base/aps/objective-library/cost/成本最小化.md`

## 质量标准

- ✅ **可溯源**: 所有建议都有明确的知识库引用
- ✅ **可执行**: 提供的方案具有可操作性
- ✅ **合理性**: 方案符合领域最佳实践
- ✅ **完整性**: 考虑了所有相关约束和目标
- ✅ **清晰性**: 表达简洁明了，易于理解

## 智能体专属指导

{AGENT_SPECIFIC_GUIDANCE}

## 开始生成方案

现在，请基于检索到的专家知识，生成满足用户需求的解决方案。
