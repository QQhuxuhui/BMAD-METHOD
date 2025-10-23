# Task: Finalize Ten Element Model

**任务ID**: `finalize-ten-element-model`
**版本**: V4.3
**用途**: Phase 1.5.6 - 固化TenElementModel，作为后续Phase的统一真相源

## 输入

```yaml
inputs:
  - ten_element_model_adjusted: 整合用户反馈后的十要素模型
  - user_selections: 用户的选择记录
  - user_feedback: 用户的反馈意见
```

## 处理逻辑

### 步骤1: 冻结模型版本

```python
from datetime import datetime
import hashlib
import json

def freeze_model_version(ten_element_model_adjusted):
    """
    冻结模型版本，防止后续意外修改
    """
    frozen_model = {
        **ten_element_model_adjusted,
        "frozen": True,
        "frozen_at": datetime.now().isoformat(),
        "version": "1.0",
        "status": "finalized"
    }

    return frozen_model
```

### 步骤2: 生成模型哈希

```python
def generate_model_hash(frozen_model):
    """
    生成模型内容的哈希值用于版本控制和完整性验证
    """
    # 排除元数据字段
    model_content = {
        k: v for k, v in frozen_model.items()
        if k not in ["frozen_at", "model_hash", "version"]
    }

    # 生成JSON字符串（保证顺序）
    content_str = json.dumps(model_content, sort_keys=True, ensure_ascii=False)

    # 计算哈希
    hash_obj = hashlib.sha256(content_str.encode('utf-8'))
    model_hash = hash_obj.hexdigest()[:16]  # 使用前16个字符

    return model_hash
```

### 步骤3: 创建基线

```python
def create_baseline(frozen_model, model_hash):
    """
    创建模型基线用于后续一致性检查
    """
    baseline = {
        "model_hash": model_hash,
        "created_at": frozen_model["frozen_at"],
        "version": frozen_model["version"],
        "element_summary": {
            "decision_variables": len(frozen_model.get("decision_variables", [])),
            "parameters": len(frozen_model.get("parameters", [])),
            "constraints": len(frozen_model.get("constraints", [])),
            "objectives": len(frozen_model.get("objectives", [])),
            "algorithm": frozen_model.get("algorithm", {}).get("name"),
            "time_model": frozen_model.get("time_model", {}).get("type"),
            "uncertainty": frozen_model.get("uncertainty", {}).get("type"),
            "solver_config": frozen_model.get("solver_config", {}).get("solver"),
            "input_data": frozen_model.get("input_data", {}).get("format"),
            "output_format": frozen_model.get("output_format", {}).get("structure")
        },
        "citations": extract_all_citations(frozen_model)
    }

    return baseline

def extract_all_citations(model):
    """提取模型中的所有引用"""
    citations = []

    # 从各个元素中提取citations字段
    for key, value in model.items():
        if isinstance(value, dict) and "citation" in value:
            citations.append(value["citation"])
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and "citation" in item:
                    citations.append(item["citation"])

    return list(set(citations))  # 去重
```

### 步骤4: 启用追踪

```python
def enable_tracking(frozen_model, baseline):
    """
    启用模型追踪机制
    """
    tracking_metadata = {
        "tracking_enabled": True,
        "baseline_hash": baseline["model_hash"],
        "change_log": [],
        "validation_status": "pending",
        "usage_count": 0,
        "last_accessed": None
    }

    return tracking_metadata
```

### 步骤5: 生成模型元数据

```python
def generate_model_metadata(frozen_model, model_hash, baseline, tracking_metadata):
    """
    生成完整的模型元数据
    """
    metadata = {
        "model_id": f"tem_{model_hash}",
        "model_version": frozen_model["version"],
        "model_hash": model_hash,
        "created_at": frozen_model["frozen_at"],
        "frozen": True,
        "baseline": baseline,
        "tracking": tracking_metadata,
        "provenance": {
            "created_by": "APS Orchestrator",
            "workflow_mode": frozen_model.get("workflow_mode"),
            "user_selections": frozen_model.get("user_selections_summary")
        },
        "quality_indicators": {
            "completeness": check_completeness(frozen_model),
            "consistency": check_consistency(frozen_model),
            "citation_coverage": check_citation_coverage(frozen_model)
        }
    }

    return metadata

def check_completeness(model):
    """检查模型完整性"""
    required_elements = [
        "decision_variables", "parameters", "constraints",
        "objectives", "algorithm", "time_model",
        "solver_config", "input_data", "output_format"
    ]

    missing = [e for e in required_elements if not model.get(e)]

    return {
        "complete": len(missing) == 0,
        "missing_elements": missing,
        "score": (len(required_elements) - len(missing)) / len(required_elements)
    }

def check_consistency(model):
    """检查模型内部一致性"""
    issues = []

    # 示例：检查算法是否与约束兼容
    # 实际实现中会有更复杂的一致性检查逻辑

    return {
        "consistent": len(issues) == 0,
        "issues": issues
    }

def check_citation_coverage(model):
    """检查引用覆盖度"""
    total_elements = 0
    cited_elements = 0

    # 遍历所有元素检查是否有citation
    for key in ["constraints", "objectives", "algorithm"]:
        if key in model:
            total_elements += 1
            if isinstance(model[key], dict) and "citation" in model[key]:
                cited_elements += 1
            elif isinstance(model[key], list):
                for item in model[key]:
                    total_elements += 1
                    if isinstance(item, dict) and "citation" in item:
                        cited_elements += 1

    coverage = cited_elements / total_elements if total_elements > 0 else 0

    return {
        "coverage": coverage,
        "cited_elements": cited_elements,
        "total_elements": total_elements
    }
```

## 输出

```yaml
outputs:
  ten_element_model:
    type: object
    required: true
    description: '固化后的十要素模型（统一真相源）'
    structure:
      frozen: true
      frozen_at: string
      version: string
      model_hash: string
      decision_variables: array
      parameters: array
      constraints: array
      objectives: array
      algorithm: object
      time_model: object
      uncertainty: object
      solver_config: object
      input_data: object
      output_format: object

  model_version:
    type: string
    description: '模型版本号'

  model_hash:
    type: string
    description: '模型内容哈希值'

  model_baseline:
    type: object
    description: '模型基线用于后续一致性检查'
```

## 示例输出

```json
{
  "ten_element_model": {
    "frozen": true,
    "frozen_at": "2025-10-21T16:40:00",
    "version": "1.0",
    "model_hash": "a3f8c9d2e5b7a1f4",
    "status": "finalized",
    "decision_variables": [...],
    "parameters": [...],
    "constraints": [...],
    "objectives": [...],
    "algorithm": {...},
    "time_model": {...},
    "uncertainty": {...},
    "solver_config": {...},
    "input_data": {...},
    "output_format": {...},
    "metadata": {
      "model_id": "tem_a3f8c9d2e5b7a1f4",
      "baseline": {...},
      "tracking": {...},
      "provenance": {...},
      "quality_indicators": {
        "completeness": {
          "complete": true,
          "missing_elements": [],
          "score": 1.0
        },
        "consistency": {
          "consistent": true,
          "issues": []
        },
        "citation_coverage": {
          "coverage": 0.95,
          "cited_elements": 19,
          "total_elements": 20
        }
      }
    }
  },
  "model_version": "1.0",
  "model_hash": "a3f8c9d2e5b7a1f4",
  "model_baseline": {
    "model_hash": "a3f8c9d2e5b7a1f4",
    "created_at": "2025-10-21T16:40:00",
    "version": "1.0",
    "element_summary": {
      "decision_variables": 5,
      "parameters": 12,
      "constraints": 8,
      "objectives": 2,
      "algorithm": "genetic_algorithm",
      "time_model": "discrete",
      "uncertainty": "stochastic",
      "solver_config": "custom",
      "input_data": "json",
      "output_format": "structured"
    },
    "citations": [
      "@专家库/算法库/heuristic/遗传算法.md",
      "@专家库/约束库/temporal/time-window-constraint.md"
    ]
  }
}
```

## 质量检查

- [ ] 模型已冻结（frozen=true）
- [ ] 哈希值正确生成
- [ ] 基线数据完整
- [ ] 追踪机制已启用
- [ ] 完整性检查通过
- [ ] 引用覆盖度 > 90%

## 引用

- @建模专家库/十要素建模流程
- @编排协调专家库/模型版本管理
- V4.3架构规范: TenElementModel固化机制

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: 模型固化与版本控制，确保统一真相源
