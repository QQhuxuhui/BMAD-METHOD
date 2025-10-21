# Task: Configure Workflow Mode

**任务ID**: `configure-workflow-mode`
**版本**: V4.3
**用途**: Phase 0.5.3 - 根据用户选择配置工作流模式

## 输入

```yaml
inputs:
  - selected_mode: 用户选择的模式（mode_a | mode_b）
  - initial_understanding: Phase 0初步分析结果
```

## 处理逻辑

### 步骤1: 解析用户选择

```python
def parse_user_selection(selected_mode):
    """
    解析并验证用户选择
    """
    valid_modes = ["mode_a", "mode_b"]

    if selected_mode not in valid_modes:
        raise ValueError(f"无效的模式选择: {selected_mode}")

    mode_config = {
        "mode_a": {
            "name": "集中确认模式",
            "code": "mode_a",
            "confirmation_style": "complete",
            "expert_calling": "parallel",
            "estimated_time": "70-95分钟"
        },
        "mode_b": {
            "name": "增量确认模式",
            "code": "mode_b",
            "confirmation_style": "incremental",
            "expert_calling": "sequential",
            "estimated_time": "95-130分钟"
        }
    }

    return mode_config[selected_mode]
```

### 步骤2: 配置Phase执行计划

```python
def configure_phase_plan(mode_config):
    """
    根据模式配置Phase执行计划
    """
    if mode_config["code"] == "mode_a":
        phase_plan = {
            "phase_1.5": {
                "confirmation_type": "complete_model",
                "template": "@交互对话模板库/完整十要素确认模板.md",
                "estimated_time": "10-15分钟",
                "show_details": True,
                "show_alternatives": True
            },
            "phase_2": {
                "execution_mode": "parallel",
                "experts": [
                    "domain-expert",
                    "constraint-expert",
                    "objective-expert",
                    "algorithm-expert"
                ],
                "estimated_time": "10-15分钟",
                "consistency_check": "after_all"
            }
        }
    else:  # mode_b
        phase_plan = {
            "phase_1.5": {
                "confirmation_type": "framework_only",
                "template": "@交互对话模板库/框架十要素确认模板.md",
                "estimated_time": "5-8分钟",
                "show_details": False,
                "show_structure_only": True
            },
            "phase_2": {
                "execution_mode": "sequential",
                "sub_phases": [
                    {
                        "id": "2.1",
                        "expert": "domain-expert",
                        "confirmation_required": True,
                        "template": "@交互对话模板库/领域确认模板.md",
                        "estimated_time": "5-8分钟"
                    },
                    {
                        "id": "2.2",
                        "expert": "constraint-expert",
                        "confirmation_required": True,
                        "template": "@交互对话模板库/约束确认模板.md",
                        "estimated_time": "10-15分钟"
                    },
                    {
                        "id": "2.3",
                        "expert": "objective-expert",
                        "confirmation_required": True,
                        "template": "@交互对话模板库/目标权重模板.md",
                        "estimated_time": "8-12分钟"
                    },
                    {
                        "id": "2.4",
                        "expert": "algorithm-expert",
                        "confirmation_required": True,
                        "template": "@交互对话模板库/算法确认模板.md",
                        "estimated_time": "5-8分钟"
                    },
                    {
                        "id": "2.5",
                        "name": "跨专家一致性校验",
                        "estimated_time": "3-5分钟"
                    }
                ],
                "estimated_time": "31-48分钟"
            }
        }

    return phase_plan
```

### 步骤3: 配置交互策略

```python
def configure_interaction_strategy(mode_config):
    """
    配置人机交互策略
    """
    if mode_config["code"] == "mode_a":
        strategy = {
            "confirmation_points": [
                "phase_0.3",   # Todo List确认
                "phase_1.5.2", # 完整TenElementModel确认
                "phase_4.5"    # 交付确认
            ],
            "detail_level": "high",
            "allow_mid_phase_adjustment": False,
            "context_presentation": "all_at_once"
        }
    else:  # mode_b
        strategy = {
            "confirmation_points": [
                "phase_0.3",   # Todo List确认
                "phase_1.5.2", # 十要素框架确认
                "phase_2.1",   # 领域确认
                "phase_2.2",   # 约束确认
                "phase_2.3",   # 目标确认
                "phase_2.4",   # 算法确认
                "phase_4.5"    # 交付确认
            ],
            "detail_level": "progressive",
            "allow_mid_phase_adjustment": True,
            "context_presentation": "incremental"
        }

    return strategy
```

### 步骤4: 生成工作流配置

```python
def generate_workflow_configuration(mode_config, phase_plan, interaction_strategy):
    """
    生成完整的工作流配置
    """
    workflow_config = {
        "selected_mode": mode_config["code"],
        "mode_name": mode_config["name"],
        "confirmation_style": mode_config["confirmation_style"],
        "expert_calling": mode_config["expert_calling"],
        "estimated_total_time": mode_config["estimated_time"],
        "phase_plan": phase_plan,
        "interaction_strategy": interaction_strategy,
        "configuration_timestamp": datetime.now().isoformat()
    }

    return workflow_config
```

### 步骤5: 更新全局配置

```python
def update_global_config(workflow_config):
    """
    更新全局配置（写入config.yaml）
    """
    # 这里模拟更新配置的逻辑
    # 实际实现中会修改 bmad/aps/config.yaml 中的 interaction_mode 字段

    config_update = {
        "interaction_mode": workflow_config["selected_mode"],
        "last_configured": workflow_config["configuration_timestamp"]
    }

    return config_update
```

## 输出

```yaml
outputs:
  workflow_configuration:
    type: object
    structure:
      selected_mode: string
      mode_name: string
      confirmation_style: string
      expert_calling: string
      estimated_total_time: string
      phase_plan: object
      interaction_strategy: object
      configuration_timestamp: string

  phase_plan:
    type: object
    description: "Phase执行计划详情"

  config_updated:
    type: boolean
    description: "全局配置是否已更新"
```

## 示例输出

### 模式A配置示例

```json
{
  "workflow_configuration": {
    "selected_mode": "mode_a",
    "mode_name": "集中确认模式",
    "confirmation_style": "complete",
    "expert_calling": "parallel",
    "estimated_total_time": "70-95分钟",
    "phase_plan": {
      "phase_1.5": {
        "confirmation_type": "complete_model",
        "template": "@交互对话模板库/完整十要素确认模板.md",
        "estimated_time": "10-15分钟",
        "show_details": true,
        "show_alternatives": true
      },
      "phase_2": {
        "execution_mode": "parallel",
        "experts": [
          "domain-expert",
          "constraint-expert",
          "objective-expert",
          "algorithm-expert"
        ],
        "estimated_time": "10-15分钟",
        "consistency_check": "after_all"
      }
    },
    "interaction_strategy": {
      "confirmation_points": [
        "phase_0.3",
        "phase_1.5.2",
        "phase_4.5"
      ],
      "detail_level": "high",
      "allow_mid_phase_adjustment": false,
      "context_presentation": "all_at_once"
    },
    "configuration_timestamp": "2025-10-21T16:35:00"
  },
  "phase_plan": {...},
  "config_updated": true
}
```

### 模式B配置示例

```json
{
  "workflow_configuration": {
    "selected_mode": "mode_b",
    "mode_name": "增量确认模式",
    "confirmation_style": "incremental",
    "expert_calling": "sequential",
    "estimated_total_time": "95-130分钟",
    "phase_plan": {
      "phase_1.5": {
        "confirmation_type": "framework_only",
        "template": "@交互对话模板库/框架十要素确认模板.md",
        "estimated_time": "5-8分钟",
        "show_details": false,
        "show_structure_only": true
      },
      "phase_2": {
        "execution_mode": "sequential",
        "sub_phases": [
          {
            "id": "2.1",
            "expert": "domain-expert",
            "confirmation_required": true,
            "template": "@交互对话模板库/领域确认模板.md",
            "estimated_time": "5-8分钟"
          }
        ],
        "estimated_time": "31-48分钟"
      }
    },
    "interaction_strategy": {
      "confirmation_points": [
        "phase_0.3",
        "phase_1.5.2",
        "phase_2.1",
        "phase_2.2",
        "phase_2.3",
        "phase_2.4",
        "phase_4.5"
      ],
      "detail_level": "progressive",
      "allow_mid_phase_adjustment": true,
      "context_presentation": "incremental"
    },
    "configuration_timestamp": "2025-10-21T16:35:00"
  },
  "phase_plan": {...},
  "config_updated": true
}
```

## 质量检查

- [ ] 模式选择有效
- [ ] Phase计划完整
- [ ] 交互策略合理
- [ ] 配置时间戳正确
- [ ] 全局配置已更新

## 引用

- @编排协调专家库/工作流配置管理
- V4.3架构规范: 双模式交互配置
- @配置管理规范/动态配置更新

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: 动态工作流配置，支持双模式切换
