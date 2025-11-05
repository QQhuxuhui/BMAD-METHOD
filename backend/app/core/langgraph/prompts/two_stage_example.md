# 两阶段提示词框架 - 使用示例

本文档通过一个完整的示例，演示如何使用两阶段提示词框架来调用智能体。

## 示例场景

**用户需求**: "我需要为一个有50个配送点的物流公司设计车辆路径规划方案，有10辆车，每辆车容量1000kg，要求在8小时内完成所有配送。"

## 阶段1: 任务理解和知识检索

### 输入给智能体的Prompt

```markdown
# 阶段1: 任务理解和知识检索

## 角色定义

你是算法专家（Algorithm Expert），负责选择合适的优化算法并给出算法参数建议。

## 任务输入

**用户需求**:
```

我需要为一个有50个配送点的物流公司设计车辆路径规划方案，有10辆车，每辆车容量1000kg，要求在8小时内完成所有配送。

````

**上下文信息**:
```json
{
  "problem_domain": "vehicle_routing",
  "scale": "medium",
  "constraints_mentioned": ["capacity", "time_limit"],
  "optimization_goals": ["minimize_cost", "complete_all_deliveries"]
}
````

## 你的目标

在第一阶段，你需要：

1. **理解任务**: 深入分析用户需求，识别关键要素
2. **识别知识需求**: 确定需要哪些专家知识来完成任务
3. **规划检索策略**: 决定从哪些专家库中检索什么知识

## 可用专家库

你可以访问以下专家库：

- algorithm-library: 算法专家库（包含各类优化算法）
- constraint-library: 约束专家库（包含各类约束建模方法）
- objective-library: 目标专家库（包含各类优化目标）
- domain-library: 领域专家库（包含领域特定知识）
- code-implementation-library: 代码实现库
- quality-library: 质量评估库
- orchestrator-library: 编排器库
- modeling-library: 建模库

## 输出要求

请以JSON格式输出你的分析结果：

[JSON格式见模板]

## 开始分析

现在，请基于上述输入，进行任务理解和知识需求分析。

````

### 智能体的Stage1输出

```json
{
  "task_understanding": {
    "problem_type": "车辆路径规划问题（CVRP - 容量约束车辆路径问题）",
    "key_requirements": [
      "50个配送点（中等规模）",
      "10辆配送车辆",
      "车辆容量约束：1000kg/车",
      "时间约束：8小时内完成"
    ],
    "constraints": [
      "容量约束：每辆车载重不超过1000kg",
      "时间约束：总配送时间≤8小时",
      "每个配送点必须被访问且仅被访问一次",
      "所有车辆从同一配送中心出发并返回"
    ],
    "success_criteria": [
      "所有配送点完成配送",
      "满足容量和时间约束",
      "总配送成本（距离/时间）最小化",
      "车辆利用率合理"
    ]
  },
  "knowledge_needed": [
    {
      "library": "algorithm-library",
      "category": "meta-heuristic",
      "specific_topics": ["遗传算法", "禁忌搜索", "模拟退火"],
      "reason": "CVRP是NP-hard问题，50个配送点属于中等规模，需要元启发式算法在合理时间内找到高质量解"
    },
    {
      "library": "domain-library",
      "category": "vehicle",
      "specific_topics": ["车辆路径规划", "VRP变种", "实践经验"],
      "reason": "需要VRP领域的最佳实践、常见陷阱和成功案例"
    },
    {
      "library": "constraint-library",
      "category": "capacity",
      "specific_topics": ["车辆容量约束"],
      "reason": "需要正确建模和处理容量约束"
    }
  ],
  "retrieval_strategy": {
    "search_keywords": ["车辆路径", "CVRP", "遗传算法", "容量约束", "VRP"],
    "priority_libraries": ["algorithm-library", "domain-library", "constraint-library"],
    "expected_knowledge_points": 5
  }
}
````

## 知识检索阶段（系统自动）

基于Stage1的输出，系统使用LibraryLoader检索相关知识：

```python
from backend.app.core.langgraph.library_loader import get_library_loader

loader = get_library_loader()

# 根据retrieval_strategy检索知识
retrieved_knowledge = {}

for need in stage1_output.knowledge_needed:
    library_data = loader.load_library(need.library)
    # 根据search_keywords搜索相关内容
    search_results = loader.search_knowledge(
        query=" ".join(stage1_output.retrieval_strategy.search_keywords),
        library_name=need.library
    )
    retrieved_knowledge[need.library] = search_results[:3]  # 取前3个结果
```

## 阶段2: 知识应用和输出生成

### 输入给智能体的Prompt

```markdown
# 阶段2: 知识应用和输出生成

## 角色定义

你是算法专家（Algorithm Expert），负责选择合适的优化算法并给出算法参数建议。

## 任务上下文

**原始需求**:
```

我需要为一个有50个配送点的物流公司设计车辆路径规划方案，有10辆车，每辆车容量1000kg，要求在8小时内完成所有配送。

````

**阶段1的分析结果**:
```json
{
  "task_understanding": { /* ... */ },
  "knowledge_needed": [ /* ... */ ],
  "retrieval_strategy": { /* ... */ }
}
````

## 检索到的专家知识

### 来自 algorithm-library/meta-heuristic/遗传算法.md

```markdown
# 遗传算法 (Genetic Algorithm)

## 适用场景

- 问题规模：20-500个决策变量
- NP-hard组合优化问题
- 需要在合理时间内找到高质量解（不要求全局最优）

## 推荐参数

对于VRP问题：

- 种群大小：50-200（取决于问题规模）
- 迭代次数：300-1000代
- 交叉率：0.7-0.9
- 变异率：0.05-0.2

## 编码方式

VRP问题推荐使用：

- 基于排列的编码
- 每个染色体表示一个完整的配送方案
- 使用分隔符区分不同车辆的路线

...
```

### 来自 domain-library/vehicle/VRP领域适配器.md

```markdown
# 车辆路径规划领域适配器

## CVRP最佳实践

1. **容量约束处理**
   - 在路径构造时实时检查容量
   - 超出容量时分配到新车辆
   - 考虑货物可分割性

2. **时间复杂度考虑**
   - 50个配送点：建议使用元启发式
   - 100+配送点：考虑混合算法或分解方法
   - 500+配送点：必须使用大规模优化技术

3. **实际应用建议**
   - 考虑实际路网距离，不只是欧几里得距离
   - 预留20%的时间缓冲应对突发情况
   - 车辆利用率目标值：75-85%

...
```

## 你的目标

在第二阶段，你需要：

1. **应用知识**: 将检索到的专家知识应用到具体任务中
2. **生成方案**: 基于专家知识，生成满足需求的解决方案
3. **溯源引用**: 对所有使用的知识点进行@引用标注

[输出要求和格式见模板]

## 开始生成方案

现在，请基于检索到的专家知识，生成满足用户需求的解决方案。

````

### 智能体的Stage2输出

```json
{
  "solution": {
    "approach": "采用遗传算法（GA）求解容量约束车辆路径规划问题（CVRP）",
    "justification": "基于专家库知识，50个配送点属于中等规模NP-hard问题。遗传算法在此规模下表现优异，能在30-60秒内找到接近最优的解。专家库指出GA对VRP问题的参数设置有成熟经验，且容量约束可以通过修复算子有效处理。",
    "references": [
      "@backend/knowledge_base/aps/algorithm-library/meta-heuristic/遗传算法.md",
      "@backend/knowledge_base/aps/domain-library/vehicle/VRP领域适配器.md",
      "@backend/knowledge_base/aps/constraint-library/capacity/车辆容量约束.md"
    ]
  },
  "details": {
    "algorithm_name": "遗传算法（Genetic Algorithm）",
    "algorithm_category": "元启发式算法",
    "parameters": {
      "population_size": 100,
      "generations": 500,
      "crossover_rate": 0.8,
      "mutation_rate": 0.1,
      "selection_method": "锦标赛选择（tournament size=5）",
      "elitism_rate": 0.05
    },
    "encoding": {
      "type": "基于排列的编码",
      "description": "染色体为配送点的排列，使用虚拟分隔符'0'划分车辆路线",
      "example": "[3,7,12,0,5,9,14,0,1,8,...]"
    },
    "operators": {
      "crossover": {
        "name": "顺序交叉（Order Crossover, OX）",
        "reason": "保持排列合法性，适合VRP问题",
        "reference": "@backend/knowledge_base/aps/algorithm-library/meta-heuristic/遗传算法.md#OX交叉"
      },
      "mutation": {
        "name": "混合变异（交换变异+逆序变异）",
        "probability": "10%交换，5%逆序",
        "reason": "增加种群多样性，跳出局部最优"
      },
      "repair": {
        "name": "容量修复算子",
        "description": "检查每条路线容量，超出则将部分配送点转移到新路线",
        "reference": "@backend/knowledge_base/aps/constraint-library/capacity/车辆容量约束.md"
      }
    },
    "fitness_function": {
      "objective": "最小化总行驶距离",
      "penalty": "容量超出惩罚：10000 * 超出量"
    },
    "expected_performance": {
      "runtime": "30-60秒",
      "solution_quality": "距离最优解5-10%以内",
      "success_rate": ">95%找到可行解"
    },
    "implementation_note": "建议使用Python的DEAP库或自定义实现"
  },
  "confidence": {
    "level": "high",
    "reasoning": "遗传算法是VRP问题的经典成熟方法，专家库提供的参数设置经过实践验证。该规模问题有大量成功案例，算法选择和参数配置都有充分的理论和实践支持。"
  },
  "assumptions": [
    "假设配送点之间的距离已知（欧几里得距离或路网距离）",
    "假设所有配送点的需求量已知且不超过单车容量",
    "假设车辆速度恒定（用于时间估算）",
    "假设不考虑交通拥堵、天气等动态因素"
  ],
  "limitations": [
    "遗传算法不保证找到全局最优解，仅能找到高质量的近似解",
    "解的质量对参数设置敏感，可能需要针对具体数据调优",
    "对于>200个配送点的大规模问题，可能需要考虑混合算法或分解方法",
    "未考虑时间窗约束、多车型、动态需求等复杂因素"
  ]
}
````

## 完整调用流程代码示例

````python
import json
from backend.app.core.langgraph.library_loader import get_library_loader

class TwoStageAgentInvoker:
    """两阶段智能体调用器"""

    def __init__(self, agent_name: str, agent_role: str):
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.loader = get_library_loader()

    def invoke(self, user_requirement: str, context_data: dict = None) -> dict:
        """完整的两阶段调用流程

        Returns:
            Stage2的输出（最终方案）
        """
        # Stage 1: 任务理解和知识检索
        stage1_prompt = self._build_stage1_prompt(user_requirement, context_data)
        stage1_output = self._call_llm(stage1_prompt)  # 调用LLM

        # 知识检索
        retrieved_knowledge = self._retrieve_knowledge(stage1_output)

        # Stage 2: 知识应用和输出生成
        stage2_prompt = self._build_stage2_prompt(
            user_requirement,
            stage1_output,
            retrieved_knowledge
        )
        stage2_output = self._call_llm(stage2_prompt)  # 再次调用LLM

        return stage2_output

    def _build_stage1_prompt(self, user_requirement: str, context_data: dict) -> str:
        """构建Stage1提示词"""
        # 读取stage1模板
        with open("backend/app/core/langgraph/prompts/stage1_template.md") as f:
            template = f.read()

        # 替换占位符
        libraries = self.loader.list_libraries()
        libraries_str = "\\n".join([f"- {lib}" for lib in libraries])

        prompt = template.replace("{AGENT_NAME}", self.agent_name)
        prompt = prompt.replace("{AGENT_ROLE}", self.agent_role)
        prompt = prompt.replace("{USER_REQUIREMENT}", user_requirement)
        prompt = prompt.replace("{CONTEXT_DATA}", json.dumps(context_data or {}, indent=2, ensure_ascii=False))
        prompt = prompt.replace("{AVAILABLE_LIBRARIES}", libraries_str)

        return prompt

    def _retrieve_knowledge(self, stage1_output: dict) -> dict:
        """基于Stage1输出检索知识"""
        retrieved = {}

        for need in stage1_output["knowledge_needed"]:
            library_name = need["library"]
            keywords = stage1_output["retrieval_strategy"]["search_keywords"]

            # 搜索该库
            results = self.loader.search_knowledge(
                query=" ".join(keywords),
                library_name=library_name
            )

            # 获取具体文件内容
            contents = []
            for result in results[:3]:  # 取前3个结果
                content = self.loader.get_library_content(
                    library_name=result["library"],
                    file_path=result["file"]
                )
                contents.append({
                    "file": f"{result['library']}/{result['file']}",
                    "content": content[:2000]  # 限制长度
                })

            retrieved[library_name] = contents

        return retrieved

    def _build_stage2_prompt(self, user_requirement: str, stage1_output: dict, retrieved_knowledge: dict) -> str:
        """构建Stage2提示词"""
        # 读取stage2模板
        with open("backend/app/core/langgraph/prompts/stage2_template.md") as f:
            template = f.read()

        # 格式化检索到的知识
        knowledge_str = ""
        for library, contents in retrieved_knowledge.items():
            knowledge_str += f"\\n### 来自 {library}\\n\\n"
            for item in contents:
                knowledge_str += f"**{item['file']}**:\\n```markdown\\n{item['content']}\\n```\\n\\n"

        # 替换占位符
        prompt = template.replace("{AGENT_NAME}", self.agent_name)
        prompt = prompt.replace("{AGENT_ROLE}", self.agent_role)
        prompt = prompt.replace("{USER_REQUIREMENT}", user_requirement)
        prompt = prompt.replace("{STAGE1_OUTPUT}", json.dumps(stage1_output, indent=2, ensure_ascii=False))
        prompt = prompt.replace("{RETRIEVED_KNOWLEDGE}", knowledge_str)
        prompt = prompt.replace("{AGENT_SPECIFIC_GUIDANCE}", self._get_agent_guidance())

        return prompt

    def _get_agent_guidance(self) -> str:
        """获取智能体专属指导"""
        # 可以从专门的配置文件读取
        return f"{self.agent_name}的专属指导..."

    def _call_llm(self, prompt: str) -> dict:
        """调用LLM（实际实现需要调用具体的模型）"""
        # 示例：调用OpenAI或其他模型
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return json.loads(response.choices[0].message.content)
        pass


# 使用示例
if __name__ == "__main__":
    invoker = TwoStageAgentInvoker(
        agent_name="算法专家",
        agent_role="选择合适的优化算法并给出算法参数建议"
    )

    result = invoker.invoke(
        user_requirement="我需要为一个有50个配送点的物流公司设计车辆路径规划方案...",
        context_data={
            "problem_domain": "vehicle_routing",
            "scale": "medium"
        }
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
````

## 总结

两阶段提示词框架的核心优势：

1. **结构化推理**: 将复杂任务分解为理解和执行两个阶段
2. **知识驱动**: 基于专家库的实际知识，而不是LLM的内部知识
3. **可溯源性**: 所有建议都有明确的知识库引用
4. **灵活性**: 可以根据Stage1的分析动态检索所需知识
5. **质量保证**: Stage1确保正确理解问题，Stage2确保知识正确应用

---

**创建日期**: 2025-11-05
**最后更新**: 2025-11-05
**版本**: 1.0
