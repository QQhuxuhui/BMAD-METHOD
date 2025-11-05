# 两阶段提示词框架 - 数据传递格式

本文档定义了Stage 1和Stage 2之间的数据传递格式（JSON Schema）。

## Stage 1 输出格式

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["task_understanding", "knowledge_needed", "retrieval_strategy"],
  "properties": {
    "task_understanding": {
      "type": "object",
      "required": ["problem_type", "key_requirements"],
      "properties": {
        "problem_type": {
          "type": "string",
          "description": "问题类型（如：车辆路径规划、生产调度等）"
        },
        "key_requirements": {
          "type": "array",
          "items": { "type": "string" },
          "description": "关键需求列表"
        },
        "constraints": {
          "type": "array",
          "items": { "type": "string" },
          "description": "约束条件列表"
        },
        "success_criteria": {
          "type": "array",
          "items": { "type": "string" },
          "description": "成功标准列表"
        }
      }
    },
    "knowledge_needed": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["library", "category", "reason"],
        "properties": {
          "library": {
            "type": "string",
            "enum": [
              "algorithm-library",
              "constraint-library",
              "objective-library",
              "domain-library",
              "code-implementation-library",
              "quality-library",
              "orchestrator-library",
              "modeling-library"
            ],
            "description": "需要检索的专家库名称"
          },
          "category": {
            "type": "string",
            "description": "知识类别（如：meta-heuristic, temporal, cost等）"
          },
          "specific_topics": {
            "type": "array",
            "items": { "type": "string" },
            "description": "具体主题列表"
          },
          "reason": {
            "type": "string",
            "description": "为什么需要这些知识"
          }
        }
      }
    },
    "retrieval_strategy": {
      "type": "object",
      "required": ["search_keywords", "priority_libraries"],
      "properties": {
        "search_keywords": {
          "type": "array",
          "items": { "type": "string" },
          "description": "搜索关键词列表"
        },
        "priority_libraries": {
          "type": "array",
          "items": { "type": "string" },
          "description": "优先检索的专家库"
        },
        "expected_knowledge_points": {
          "type": "integer",
          "minimum": 1,
          "description": "预期检索的知识点数量"
        }
      }
    }
  }
}
```

### 示例

```json
{
  "task_understanding": {
    "problem_type": "车辆路径规划问题（VRP）",
    "key_requirements": ["50个配送点", "10辆配送车辆", "每个车辆容量1000kg", "需在8小时内完成配送"],
    "constraints": ["时间窗约束：每个配送点有指定的服务时间窗", "容量约束：不能超过车辆载重", "工作时间约束：驾驶员工作时间不超过8小时"],
    "success_criteria": ["总配送成本最小化", "满足所有时间窗约束", "车辆利用率>80%"]
  },
  "knowledge_needed": [
    {
      "library": "algorithm-library",
      "category": "meta-heuristic",
      "specific_topics": ["遗传算法", "禁忌搜索"],
      "reason": "VRP是NP-hard问题，规模较大（50点），需要元启发式算法"
    },
    {
      "library": "constraint-library",
      "category": "temporal",
      "specific_topics": ["时间窗约束"],
      "reason": "需要建模和处理时间窗约束"
    },
    {
      "library": "domain-library",
      "category": "vehicle",
      "specific_topics": ["车辆路径规划领域知识"],
      "reason": "需要VRP领域的最佳实践和经验"
    }
  ],
  "retrieval_strategy": {
    "search_keywords": ["车辆路径", "时间窗", "遗传算法", "VRP"],
    "priority_libraries": ["algorithm-library", "domain-library", "constraint-library"],
    "expected_knowledge_points": 5
  }
}
```

## Stage 2 输出格式

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["solution", "details", "confidence"],
  "properties": {
    "solution": {
      "type": "object",
      "required": ["approach", "justification", "references"],
      "properties": {
        "approach": {
          "type": "string",
          "description": "解决方案概述"
        },
        "justification": {
          "type": "string",
          "description": "方案合理性说明"
        },
        "references": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^@backend/knowledge_base/aps/[a-z-]+/.+\\.md$"
          },
          "description": "知识库引用列表，必须是@引用格式"
        }
      }
    },
    "details": {
      "type": "object",
      "description": "根据具体智能体角色的详细输出，结构因智能体而异",
      "additionalProperties": true
    },
    "confidence": {
      "type": "object",
      "required": ["level", "reasoning"],
      "properties": {
        "level": {
          "type": "string",
          "enum": ["high", "medium", "low"],
          "description": "置信度级别"
        },
        "reasoning": {
          "type": "string",
          "description": "置信度判断依据"
        }
      }
    },
    "assumptions": {
      "type": "array",
      "items": { "type": "string" },
      "description": "方案的假设条件"
    },
    "limitations": {
      "type": "array",
      "items": { "type": "string" },
      "description": "方案的局限性"
    }
  }
}
```

### 示例（算法专家的输出）

```json
{
  "solution": {
    "approach": "采用遗传算法（GA）求解带时间窗的车辆路径规划问题",
    "justification": "问题规模为50个配送点，属于中等规模NP-hard问题。遗传算法在此规模下能在合理时间内找到高质量解，且能有效处理时间窗约束。",
    "references": [
      "@backend/knowledge_base/aps/algorithm-library/meta-heuristic/遗传算法.md",
      "@backend/knowledge_base/aps/constraint-library/temporal/时间窗约束.md",
      "@backend/knowledge_base/aps/domain-library/vehicle/VRP领域适配器.md"
    ]
  },
  "details": {
    "algorithm_name": "遗传算法（Genetic Algorithm）",
    "parameters": {
      "population_size": 100,
      "generations": 500,
      "crossover_rate": 0.8,
      "mutation_rate": 0.1,
      "selection_method": "锦标赛选择"
    },
    "encoding": "基于排列的编码方式",
    "operators": {
      "crossover": "顺序交叉（OX）",
      "mutation": "交换变异"
    },
    "time_complexity": "O(G * P * N^2)，其中G=迭代次数，P=种群大小，N=配送点数",
    "expected_runtime": "约30-60秒（50个配送点）"
  },
  "confidence": {
    "level": "high",
    "reasoning": "遗传算法是VRP问题的经典方法，在类似规模问题上有大量成功应用案例。专家库提供了完整的算法实现指导和参数调优经验。"
  },
  "assumptions": ["假设车辆速度恒定为60km/h", "假设配送点之间的距离可通过欧几里得距离或实际路网计算", "假设不考虑交通拥堵和天气因素"],
  "limitations": ["遗传算法的解质量依赖参数调优", "对于超大规模问题（>200点）可能需要混合算法", "不保证找到全局最优解"]
}
```

## 数据流转流程

```
用户需求 →
Stage 1 (任务理解) →
  输出: Stage1Output (JSON) →
    知识检索 (LibraryLoader) →
      检索到的知识文本 →
        Stage 2 (知识应用) →
          输出: Stage2Output (JSON) →
            最终方案
```

## 智能体间协作

在LangGraph工作流中，8个智能体的输出会被编排器收集和整合：

```json
{
  "orchestrator_output": "工作流整体方案",
  "algorithm_expert_output": {
    /* Stage2Output */
  },
  "constraint_expert_output": {
    /* Stage2Output */
  },
  "objective_expert_output": {
    /* Stage2Output */
  },
  "domain_expert_output": {
    /* Stage2Output */
  },
  "code_impl_expert_output": {
    /* Stage2Output */
  },
  "quality_expert_output": {
    /* Stage2Output */
  }
}
```

## 验证规则

### Stage 1 输出验证

- ✅ 必须包含`task_understanding`, `knowledge_needed`, `retrieval_strategy`
- ✅ `knowledge_needed`数组不能为空
- ✅ `library`字段必须是有效的专家库名称
- ✅ `search_keywords`至少包含1个关键词

### Stage 2 输出验证

- ✅ 必须包含`solution`, `details`, `confidence`
- ✅ `references`数组不能为空
- ✅ 所有引用必须符合`@backend/knowledge_base/aps/{library}/{path}.md`格式
- ✅ 引用的文件必须真实存在于知识库中
- ✅ `confidence.level`必须是"high", "medium", "low"之一

## 实现建议

### Python类定义

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class TaskUnderstanding(BaseModel):
    problem_type: str
    key_requirements: List[str]
    constraints: List[str] = []
    success_criteria: List[str] = []

class KnowledgeNeed(BaseModel):
    library: str
    category: str
    specific_topics: List[str] = []
    reason: str

class RetrievalStrategy(BaseModel):
    search_keywords: List[str]
    priority_libraries: List[str]
    expected_knowledge_points: int = 5

class Stage1Output(BaseModel):
    task_understanding: TaskUnderstanding
    knowledge_needed: List[KnowledgeNeed]
    retrieval_strategy: RetrievalStrategy

class Solution(BaseModel):
    approach: str
    justification: str
    references: List[str] = Field(..., pattern=r'^@backend/knowledge_base/aps/')

class Confidence(BaseModel):
    level: Literal["high", "medium", "low"]
    reasoning: str

class Stage2Output(BaseModel):
    solution: Solution
    details: Dict[str, Any]
    confidence: Confidence
    assumptions: List[str] = []
    limitations: List[str] = []
```

---

**创建日期**: 2025-11-05
**最后更新**: 2025-11-05
**版本**: 1.0
