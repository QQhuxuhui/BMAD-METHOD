# 知识库迁移指南

本文档记录了BMAD-METHOD专家库从`bmad/aps/templates/`迁移到`backend/knowledge_base/aps/`的完整过程，以及LibraryLoader和两阶段提示词框架的使用方法。

**迁移日期**: 2025-11-05
**Story**: 1.5.0 - 专家库迁移和加载器实现
**版本**: 1.0

---

## 目录

1. [迁移概述](#迁移概述)
2. [专家库目录结构](#专家库目录结构)
3. [迁移统计](#迁移统计)
4. [README.md索引格式规范](#readmemd索引格式规范)
5. [LibraryLoader使用方法](#libraryloader使用方法)
6. [两阶段提示词框架使用指南](#两阶段提示词框架使用指南)
7. [代码示例](#代码示例)
8. [故障排除](#故障排除)

---

## 迁移概述

### 迁移目标

将原BMAD-METHOD的专家库迁移到LangGraph架构下，支持动态知识加载和"Agent as Doc"理念。

### 迁移范围

**源位置**: `bmad/aps/templates/`
**目标位置**: `backend/knowledge_base/aps/`

**迁移的专家库** (8个):

1. **algorithm-library** - 算法专家库
2. **constraint-library** - 约束专家库
3. **objective-library** - 目标专家库
4. **domain-library** - 领域专家库
5. **code-implementation-library** - 代码实现库
6. **quality-library** - 质量评估库
7. **orchestrator-library** - 编排器知识库
8. **modeling-library** - 建模库

### 迁移变更

1. **目录位置变更**: 从`bmad/aps/templates/`移动到`backend/knowledge_base/aps/`
2. **引用路径更新**: 所有`@专家库/xxx`引用更新为`@backend/knowledge_base/aps/xxx`
3. **名称映射**:
   - `code-patterns-library` → `code-implementation-library`
   - `quality-criteria-library` → `quality-library`
4. **引用标准化**: 共更新493处@引用路径

---

## 专家库目录结构

### 完整目录树

```
backend/
└── knowledge_base/
    └── aps/
        ├── algorithm-library/          # 算法专家库
        │   ├── README.md               # 知识索引（必需）
        │   ├── meta-heuristic/         # 元启发式算法
        │   │   ├── 遗传算法.md
        │   │   ├── 模拟退火.md
        │   │   ├── 禁忌搜索.md
        │   │   ├── 粒子群算法.md
        │   │   └── 蚁群算法.md
        │   ├── exact/                  # 精确算法
        │   │   ├── 分支定界.md
        │   │   ├── 整数规划.md
        │   │   └── 动态规划.md
        │   └── heuristic/              # 启发式算法
        │       ├── 贪心算法.md
        │       ├── 构造式启发式.md
        │       └── 改进式启发式.md
        │
        ├── constraint-library/         # 约束专家库
        │   ├── README.md
        │   ├── temporal/               # 时间约束
        │   │   ├── 时间窗约束.md
        │   │   ├── 工作时间约束.md
        │   │   ├── 截止期约束.md
        │   │   └── 时序依赖约束.md
        │   ├── capacity/               # 容量约束
        │   │   ├── 车辆容量约束.md
        │   │   ├── 仓库容量约束.md
        │   │   └── 资源容量约束.md
        │   ├── spatial/                # 空间约束
        │   │   ├── 距离约束.md
        │   │   ├── 地理位置约束.md
        │   │   └── 服务范围约束.md
        │   ├── logical/                # 逻辑约束
        │   │   ├── 互斥约束.md
        │   │   ├── 依赖约束.md
        │   │   └── 优先级约束.md
        │   └── business-rules/         # 业务规则约束
        │       ├── 合规性约束.md
        │       ├── 成本约束.md
        │       └── 服务质量约束.md
        │
        ├── objective-library/          # 目标专家库
        │   ├── README.md
        │   ├── cost/                   # 成本目标
        │   │   ├── 总成本目标.md
        │   │   ├── 运营成本目标.md
        │   │   └── 资源成本目标.md
        │   ├── time/                   # 时间目标
        │   │   ├── 最大完成时间目标.md
        │   │   ├── 总延迟时间目标.md
        │   │   └── 加权延迟目标.md
        │   ├── efficiency/             # 效率目标
        │   │   ├── 资源利用率目标.md
        │   │   ├── 负载均衡目标.md
        │   │   └── 吞吐量目标.md
        │   ├── quality/                # 质量目标
        │   │   ├── 客户满意度目标.md
        │   │   ├── 服务质量目标.md
        │   │   └── 准确率目标.md
        │   ├── sustainability/         # 可持续性目标
        │   │   ├── 能耗目标.md
        │   │   └── 碳排放目标.md
        │   └── multi-objective/        # 多目标优化
        │       ├── 加权优化方法.md
        │       └── 帕累托前沿.md
        │
        ├── domain-library/             # 领域专家库
        │   ├── README.md
        │   ├── vehicle/                # 车辆路径规划
        │   │   ├── VRP领域适配器.md
        │   │   ├── vehicle-routing-domain.md
        │   │   └── 冷链物流最佳实践.md
        │   ├── production/             # 生产调度
        │   │   ├── 生产调度适配器.md
        │   │   └── JIT生产最佳实践.md
        │   ├── supply-chain/           # 供应链
        │   │   ├── 供应链调度适配器.md
        │   │   └── VMI协同库存管理.md
        │   ├── service/                # 服务调度
        │   │   ├── 人员排班适配器.md
        │   │   └── SLA服务质量管理.md
        │   └── project/                # 项目管理
        │       ├── 项目调度适配器.md
        │       └── 敏捷开发最佳实践.md
        │
        ├── code-implementation-library/ # 代码实现库
        │   └── README.md
        │
        ├── quality-library/            # 质量评估库
        │   ├── README.md
        │   ├── syntax/                 # 语法检查
        │   │   └── Python语法检查器.md
        │   ├── logic/                  # 逻辑验证
        │   │   └── 逻辑验证器.md
        │   ├── consistency/            # 一致性检查
        │   │   └── 约束一致性检查器.md
        │   ├── benchmark/              # 基准测试
        │   │   └── 基准运行器.md
        │   └── report/                 # 报告生成
        │       └── 报告聚合器.md
        │
        ├── orchestrator-library/       # 编排器知识库
        │   ├── README.md
        │   ├── collaboration/          # 协作模式
        │   │   ├── 串行协作模式.md
        │   │   ├── 并行协作模式.md
        │   │   └── 混合协作模式.md
        │   ├── decision/               # 决策策略
        │   │   ├── 专家选择策略.md
        │   │   ├── 复杂度评估策略.md
        │   │   ├── 冲突解决策略.md
        │   │   └── 质量评估策略.md
        │   ├── integration/            # 集成策略
        │   │   ├── 方案融合策略.md
        │   │   ├── 一致性保证策略.md
        │   │   └── 迭代优化策略.md
        │   └── risk/                   # 风险管理
        │       ├── 风险识别矩阵.md
        │       └── 风险控制策略.md
        │
        └── modeling-library/           # 建模库
            └── core/
                ├── ten-element-modeling.md
                ├── time-model.md
                └── uncertainty-modeling.md
```

### 库的作用

| 库名称 | 英文名                      | 作用                         | 对应智能体                 |
| ------ | --------------------------- | ---------------------------- | -------------------------- |
| 算法库 | algorithm-library           | 提供各类优化算法的知识和参数 | Algorithm Expert           |
| 约束库 | constraint-library          | 提供约束建模和处理方法       | Constraint Expert          |
| 目标库 | objective-library           | 提供优化目标的定义和评估     | Objective Expert           |
| 领域库 | domain-library              | 提供特定领域的最佳实践       | Domain Expert              |
| 代码库 | code-implementation-library | 提供代码实现模式             | Code Implementation Expert |
| 质量库 | quality-library             | 提供质量评估标准             | Quality Expert             |
| 编排库 | orchestrator-library        | 提供工作流编排知识           | Orchestrator               |
| 建模库 | modeling-library            | 提供问题建模方法             | (通用)                     |

---

## 迁移统计

### 文件统计

```
总计迁移的库: 8个
总计迁移的文件: 约150+ markdown文件
总计代码行数: 约50,000+ 行

文件类型分布:
- README.md: 8个（每个库1个）
- 知识点文档: 142个
- 总大小: 约5MB
```

### 引用更新统计

```
引用路径更新统计:
- 第1轮更新: 13个文件, 97处引用
- 第2轮更新: 58个文件, 182处引用
- 第3轮更新: 76个文件, 214处引用
- 总计: 147个文件, 493处引用更新
```

### 引用模式映射

| 旧引用格式                | 新引用格式                                        |
| ------------------------- | ------------------------------------------------- |
| `@专家库/算法库/`         | `@backend/knowledge_base/aps/algorithm-library/`  |
| `@专家库/约束库/`         | `@backend/knowledge_base/aps/constraint-library/` |
| `@专家库/目标库/`         | `@backend/knowledge_base/aps/objective-library/`  |
| `@专家库/领域库/`         | `@backend/knowledge_base/aps/domain-library/`     |
| `@专家库/调度算法专家库/` | `@backend/knowledge_base/aps/algorithm-library/`  |
| `@专家库/约束模式专家库/` | `@backend/knowledge_base/aps/constraint-library/` |

---

## README.md索引格式规范

每个专家库必须包含一个`README.md`文件，作为该库的知识索引。

### 标准格式

```markdown
# {库名称}

**专家**: {专家名称}
**版本**: {版本号}
**用途**: {一句话描述}

## 知识库结构

[目录树]

## 知识目录

### {分类1}

- **{知识点标题}** [@{文件路径}]
  描述: {简要描述（1-2句话）}

### {分类2}

- **{知识点标题}** [@{文件路径}]
  描述: {简要描述}

## 使用场景

- 场景1: {描述}
- 场景2: {描述}

## 参考资料

- {外部参考链接}
```

### 关键要素

1. **@引用路径**: 每个知识点必须有`@{相对路径}`标记
   - 格式: `@backend/knowledge_base/aps/{library}/{category}/{file}.md`
   - 示例: `@backend/knowledge_base/aps/algorithm-library/meta-heuristic/遗传算法.md`

2. **结构化分类**: 使用二级标题(`##`)组织知识分类

3. **简要描述**: 每个知识点提供1-2句话的描述，说明该知识的作用

4. **使用场景**: 明确该库的适用场景，帮助智能体判断是否需要检索

### 示例: algorithm-library/README.md

```markdown
# 算法专家知识库 - Algorithm Library

**专家**: 张效率 (Algorithm Expert)
**版本**: V4.2
**用途**: 调度算法推荐、复杂度分析、性能优化、代码生成

## 知识目录

### 元启发式算法

- **遗传算法** [@backend/knowledge_base/aps/algorithm-library/meta-heuristic/遗传算法.md]
  描述: 基于自然选择的优化算法，适用于中大规模NP-hard问题

- **模拟退火** [@backend/knowledge_base/aps/algorithm-library/meta-heuristic/模拟退火.md]
  描述: 基于物理退火过程的全局优化算法，适用于连续和离散优化

### 精确算法

- **分支定界** [@backend/knowledge_base/aps/algorithm-library/exact/分支定界.md]
  描述: 系统搜索最优解的精确方法，保证找到全局最优解

## 使用场景

- 当用户需要选择优化算法时，根据问题规模和特征推荐合适算法
- 当用户需要算法参数调优时，提供经验参数和调优策略
- 当用户需要算法性能评估时，提供复杂度分析和预期运行时间
```

---

## LibraryLoader使用方法

### 基本用法

```python
from backend.app.core.langgraph.library_loader import LibraryLoader, get_library_loader

# 方式1: 创建新实例
loader = LibraryLoader()

# 方式2: 使用单例（推荐）
loader = get_library_loader()

# 列出所有库
libraries = loader.list_libraries()
print(libraries)
# 输出: ['algorithm-library', 'constraint-library', ...]

# 加载一个库
lib_data = loader.load_library("algorithm-library")
print(f"库名称: {lib_data['name']}")
print(f"文件数: {len(lib_data['files'])}")
print(f"README长度: {len(lib_data['readme'])} 字符")

# 获取特定文件内容
content = loader.get_library_content(
    library_name="algorithm-library",
    file_path="meta-heuristic/遗传算法.md"
)
print(content[:200])  # 打印前200字符

# 搜索知识
results = loader.search_knowledge("遗传算法")
for result in results[:3]:
    print(f"{result['library']}/{result['file']}: {result['match_count']} 次匹配")

# 清空缓存（需要时）
loader.clear_cache()
```

### 高级用法

#### 1. 在特定库中搜索

```python
# 只在算法库中搜索
results = loader.search_knowledge(
    query="遗传算法",
    library_name="algorithm-library"
)
```

#### 2. 批量加载多个库

```python
libraries_to_load = ["algorithm-library", "constraint-library", "objective-library"]

knowledge_base = {}
for lib_name in libraries_to_load:
    knowledge_base[lib_name] = loader.load_library(lib_name)

print(f"已加载 {len(knowledge_base)} 个专家库")
```

#### 3. 缓存管理

```python
# 检查缓存大小
cache_size = loader.get_cache_size()
print(f"缓存中有 {cache_size} 个文件")

# 清空缓存（当知识库内容更新时）
loader.clear_cache()
```

### API文档

#### `LibraryLoader.__init__(base_path: str = "backend/knowledge_base/aps")`

初始化加载器。

**参数**:

- `base_path`: 专家库根目录路径（可选，默认为`backend/knowledge_base/aps`）

**异常**:

- `FileNotFoundError`: 如果base_path不存在

---

#### `LibraryLoader.list_libraries() -> List[str]`

列出所有可用的专家库。

**返回**: 库名称列表（按字母顺序排序）

---

#### `LibraryLoader.load_library(library_name: str) -> Dict[str, Any]`

加载指定专家库。

**参数**:

- `library_name`: 库名称（如 "algorithm-library"）

**返回**: 字典，包含:

- `name`: 库名称
- `path`: 库路径
- `readme`: README内容
- `files`: 文件列表
- `content`: 文件内容字典 {相对路径: 内容}

**异常**:

- `FileNotFoundError`: 如果库不存在
- `ValueError`: 如果库名称无效

---

#### `LibraryLoader.get_library_content(library_name: str, file_path: str) -> str`

获取库中特定文件内容。

**参数**:

- `library_name`: 库名称
- `file_path`: 相对文件路径（相对于库根目录）

**返回**: 文件内容字符串

**异常**:

- `FileNotFoundError`: 如果文件不存在

---

#### `LibraryLoader.search_knowledge(query: str, library_name: Optional[str] = None) -> List[Dict]`

搜索知识库。

**参数**:

- `query`: 搜索关键词
- `library_name`: 限定搜索的库（可选，不指定则搜索所有库）

**返回**: 匹配的知识点列表，按匹配次数降序排序，每项包含:

- `library`: 库名称
- `file`: 文件路径
- `title`: 匹配的标题
- `content`: 匹配的内容片段
- `match_count`: 匹配次数

---

#### `LibraryLoader.clear_cache()`

清空缓存。

---

#### `LibraryLoader.get_cache_size() -> int`

获取缓存中的文件数量。

---

#### `get_library_loader(base_path: Optional[str] = None) -> LibraryLoader`

获取全局LibraryLoader实例（单例模式）。

**参数**:

- `base_path`: 可选的自定义基础路径

**返回**: LibraryLoader实例

---

## 两阶段提示词框架使用指南

### 框架概述

两阶段提示词框架将智能体的推理过程分为两个阶段：

1. **阶段1: 任务理解和知识检索**
   - 智能体分析任务需求
   - 识别需要的专家知识
   - 规划知识检索策略

2. **阶段2: 知识应用和输出生成**
   - 智能体基于检索到的知识
   - 生成满足需求的解决方案
   - 所有输出都有明确的@引用溯源

### 快速开始

```python
from backend.app.core.langgraph.library_loader import get_library_loader

# 1. 初始化加载器
loader = get_library_loader()

# 2. 准备用户需求
user_requirement = "我需要为50个配送点设计车辆路径规划方案"

# 3. 构建Stage1提示词
with open("backend/app/core/langgraph/prompts/stage1_template.md") as f:
    stage1_template = f.read()

stage1_prompt = stage1_template.replace("{AGENT_NAME}", "算法专家")
stage1_prompt = stage1_prompt.replace("{AGENT_ROLE}", "选择优化算法")
stage1_prompt = stage1_prompt.replace("{USER_REQUIREMENT}", user_requirement)
# ... 替换其他占位符

# 4. 调用LLM获取Stage1输出
stage1_output = call_llm(stage1_prompt)  # 返回JSON

# 5. 基于Stage1输出检索知识
retrieved_knowledge = {}
for need in stage1_output["knowledge_needed"]:
    results = loader.search_knowledge(
        query=" ".join(stage1_output["retrieval_strategy"]["search_keywords"]),
        library_name=need["library"]
    )
    retrieved_knowledge[need["library"]] = results[:3]

# 6. 构建Stage2提示词
with open("backend/app/core/langgraph/prompts/stage2_template.md") as f:
    stage2_template = f.read()

stage2_prompt = stage2_template.replace("{AGENT_NAME}", "算法专家")
# ... 替换其他占位符，包括检索到的知识

# 7. 调用LLM获取Stage2输出（最终方案）
stage2_output = call_llm(stage2_prompt)
```

### 详细说明

详见: `backend/app/core/langgraph/prompts/two_stage_example.md`

---

## 代码示例

### 示例1: 搜索并加载相关知识

```python
from backend.app.core.langgraph.library_loader import get_library_loader

loader = get_library_loader()

# 用户需求
query = "车辆路径规划 时间窗约束"

# 搜索相关知识
results = loader.search_knowledge(query)

# 打印前5个最相关的结果
for i, result in enumerate(results[:5], 1):
    print(f"{i}. {result['library']}/{result['file']}")
    print(f"   匹配次数: {result['match_count']}")
    print(f"   内容片段: {result['content'][:100]}...")
    print()
```

### 示例2: 加载多个库并提取特定知识

```python
loader = get_library_loader()

# 需要的库
libraries = ["algorithm-library", "constraint-library", "domain-library"]

# 加载并提取
knowledge = {}
for lib in libraries:
    lib_data = loader.load_library(lib)
    knowledge[lib] = {
        "readme": lib_data["readme"],
        "files_count": len(lib_data["files"]),
        "sample_files": lib_data["files"][:3]  # 前3个文件
    }

# 打印摘要
for lib, data in knowledge.items():
    print(f"\\n{lib}:")
    print(f"  文件数: {data['files_count']}")
    print(f"  示例文件: {data['sample_files']}")
```

### 示例3: 验证@引用的有效性

```python
import re

def validate_references(text: str, loader):
    """验证文本中的所有@引用是否有效"""
    # 提取所有@引用
    pattern = r'@backend/knowledge_base/aps/([^/]+)/(.+?\\.md)'
    matches = re.findall(pattern, text)

    invalid_refs = []
    for library, file_path in matches:
        try:
            loader.get_library_content(library, file_path)
        except FileNotFoundError:
            invalid_refs.append(f"@backend/knowledge_base/aps/{library}/{file_path}")

    return invalid_refs

# 使用
loader = get_library_loader()
text = """
根据@backend/knowledge_base/aps/algorithm-library/meta-heuristic/遗传算法.md的建议...
参考@backend/knowledge_base/aps/constraint-library/temporal/时间窗约束.md...
"""

invalid = validate_references(text, loader)
if invalid:
    print("发现无效引用:")
    for ref in invalid:
        print(f"  - {ref}")
else:
    print("所有引用都有效")
```

---

## 故障排除

### 问题1: FileNotFoundError - 找不到知识库路径

**错误信息**:

```
FileNotFoundError: Cannot find knowledge base at backend/knowledge_base/aps
```

**解决方法**:

1. 检查当前工作目录是否在项目根目录
2. 使用绝对路径初始化:
   ```python
   from pathlib import Path
   base_path = Path(__file__).parent.parent.parent / "knowledge_base" / "aps"
   loader = LibraryLoader(str(base_path))
   ```

---

### 问题2: 搜索结果为空

**可能原因**:

1. 关键词拼写错误
2. 知识库中确实没有相关内容

**解决方法**:

1. 尝试更通用的关键词
2. 检查库是否正确加载:

   ```python
   libraries = loader.list_libraries()
   print("可用的库:", libraries)

   lib_data = loader.load_library("algorithm-library")
   print("文件列表:", lib_data["files"])
   ```

---

### 问题3: UnicodeDecodeError

**错误信息**:

```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**解决方法**:
LibraryLoader会自动尝试GB18030编码。如果还有问题，检查文件编码并转换为UTF-8:

```bash
iconv -f GB18030 -t UTF-8 file.md > file_utf8.md
```

---

### 问题4: 缓存导致的过期数据

**症状**: 更新了知识库文件，但加载的还是旧内容

**解决方法**:

```python
loader.clear_cache()
# 然后重新加载
lib_data = loader.load_library("algorithm-library")
```

---

### 问题5: @引用格式错误

**错误示例**:

```
@专家库/算法库/遗传算法.md  # 旧格式，不再使用
@algorithm-library/遗传算法.md  # 缺少backend/knowledge_base/aps前缀
```

**正确格式**:

```
@backend/knowledge_base/aps/algorithm-library/meta-heuristic/遗传算法.md
```

---

## 附录

### A. 迁移脚本

迁移过程使用的脚本保存在 `scripts/update_library_references.py`。

### B. 测试文件

单元测试文件: `backend/tests/unit/test_library_loader.py`
测试覆盖率: 35个测试，100%通过

### C. 相关文档

- 两阶段提示词框架: `backend/app/core/langgraph/prompts/data_transfer_format.md`
- 使用示例: `backend/app/core/langgraph/prompts/two_stage_example.md`
- Story 1.5.0: `docs/stories/1.5.0.story.md`

### D. 联系方式

如有问题或建议，请提交Issue或联系开发团队。

---

**文档版本**: 1.0
**最后更新**: 2025-11-05
**维护者**: Claude Code (Dev Agent)
