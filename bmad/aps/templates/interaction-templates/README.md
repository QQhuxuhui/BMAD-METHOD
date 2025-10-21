# 交互对话模板库 - Interaction Templates

**版本**: V4.3
**用途**: Human-in-the-Loop交互的标准化模板

## 📚 模板概览

### 已创建模板

| 模板文件                        | 触发级别 | 使用场景              | 预计时间 | 状态 |
| ------------------------------- | -------- | --------------------- | -------- | ---- |
| `todo-confirmation-template.md` | P0       | Phase 0 Todo List确认 | 2-3分钟  | ✅   |
| `mode-selection-template.md`    | P0       | Phase 0.5 模式选择    | 2-3分钟  | ✅   |
| `capability-gap-template.md`    | P3       | 能力缺口报告          | 5-10分钟 | ✅   |

### 待创建模板

**P0级别（强制）**:

- [ ] `requirement-clarification-template.md` - 需求澄清
- [ ] `domain-confirmation-template.md` - 领域识别确认
- [ ] `ten-element-complete-confirmation-template.md` - 完整十要素确认（模式A）
- [ ] `ten-element-framework-confirmation-template.md` - 框架十要素确认（模式B）
- [ ] `constraint-confirmation-template.md` - 约束确认（模式B）
- [ ] `objective-weight-template.md` - 目标权重确认
- [ ] `algorithm-confirmation-template.md` - 算法选择确认（模式B）
- [ ] `delivery-confirmation-template.md` - 最终交付确认

**P1级别（低置信度）**:

- [ ] `low-confidence-alert-template.md` - 置信度<0.70告警

**P2级别（冲突）**:

- [ ] `conflict-arbitration-template.md` - 专家建议冲突仲裁

**P4级别（用户主动）**:

- [ ] `user-pause-template.md` - 用户主动暂停

## 🎯 模板体系

### V4.3 Human-in-the-Loop机制

```yaml
interaction_triggers:
  P0_mandatory:
    description: '强制要求用户确认的关键决策点'
    examples:
      - Todo List确认
      - 模式选择
      - 十要素建模确认
      - 约束/目标/算法确认（模式B）
      - 最终交付确认
    bypass: false

  P1_low_confidence:
    description: '置信度<0.70时触发'
    trigger_condition: 'confidence < 0.70'
    examples:
      - 需求模糊
      - 多种可能方案
      - 缺少关键信息
    bypass: false

  P2_conflict:
    description: '专家建议冲突时触发'
    trigger_condition: 'has_expert_conflicts'
    examples:
      - 算法选择冲突
      - 约束与目标矛盾
    bypass: false

  P3_capability_gap:
    description: '能力缺口检测触发'
    trigger_condition: 'knowledge_not_in_library'
    examples:
      - 特殊领域
      - 罕见约束组合
      - 创新性需求
    bypass: false

  P4_user_initiated:
    description: '用户主动暂停'
    trigger_condition: 'user_request_pause'
    examples:
      - 需要思考
      - 咨询他人
      - 准备补充信息
    bypass: true
```

### 模板标准结构

每个交互模板应包含：

````markdown
# 交互模板: [模板名称]

**模板ID**: `template-id`
**触发级别**: P0 | P1 | P2 | P3 | P4
**使用场景**: [使用场景描述]
**预计时间**: [时间]

## 模板目标

[交互目标]

## 触发条件

[什么情况下使用此模板]

## 交互流程

### 步骤1: [第一步]

```markdown
[展示给用户的内容]
```
````

### 步骤2: [询问]

```markdown
[询问用户的问题]
```

### 步骤3: [处理反馈]

**场景A**: [处理方式A]
**场景B**: [处理方式B]

## 输出格式

[数据结构定义]

## 质量检查

- [ ] 检查项

## 相关流程

[上下游关系]

## V4.3特性说明

[体现的核心机制]

````

## 🔄 双模式差异

### 模式A（集中确认）

**交互点更少，但每次更深入**:
- Phase 1.5: 一次性确认完整十要素
- Phase 2: 一次性查看所有专家结果
- 冲突仲裁: 集中处理

**使用模板**:
- `ten-element-complete-confirmation-template.md`
- `conflict-arbitration-template.md`（如需要）

### 模式B（增量确认）

**交互点更多，但每次更简单**:
- Phase 1.5: 仅确认框架
- Phase 2.1-2.4: 每个专家结果单独确认
- 细节确认: 分散到各专家环节

**使用模板**:
- `ten-element-framework-confirmation-template.md`
- `domain-confirmation-template.md`
- `constraint-confirmation-template.md`
- `objective-weight-template.md`
- `algorithm-confirmation-template.md`

## 📊 模板设计原则

### 1. 清晰性 (Clarity)
- 使用简单直白的语言
- 视觉符号增强可读性(✅⏳🔄📊)
- 结构化展示信息

### 2. 选择性 (Choice)
- 提供明确的选项
- 说明每个选项的含义和影响
- 允许用户提问或要求更多信息

### 3. 透明性 (Transparency)
- 说明为什么需要用户确认
- 展示决策的影响范围
- 明确时间成本

### 4. 引导性 (Guidance)
- 提供推荐选项（如适用）
- 说明推荐理由
- 允许用户选择其他选项

### 5. 记录性 (Documentation)
- 所有用户决策都要记录
- 包含在输出数据结构中
- 可追溯审计

## 💬 交互风格指南

### 语气
- **专业但友好**: 避免过于技术化或过于随意
- **尊重用户**: 认可用户的决策权
- **耐心引导**: 特别是模式B，需要详细解释

### 格式
- **Markdown**: 使用标题、列表、表格组织信息
- **视觉符号**: ✅❌⏳🔄📊💡⚠️等增强可读性
- **代码块**: 用于展示结构化数据或配置

### 提问方式
- **明确选项**: 列出所有可能的回复
- **开放补充**: 允许用户提出未预见的问题
- **确认理解**: 总结用户反馈确保理解正确

## 🛠️ 模板开发指南

### 创建新模板

1. **确定触发场景**
   - 哪个Phase？
   - 什么条件触发？
   - P0-P4级别？

2. **设计交互流程**
   - 展示什么信息？
   - 询问什么问题？
   - 可能的用户反馈场景？

3. **定义输出格式**
   - YAML结构
   - 包含所有决策信息
   - 可序列化保存

4. **编写模板文件**
   - 使用标准结构
   - 提供完整示例
   - 质量检查清单

5. **集成到workflow**
   - 在workflow.yaml中引用
   - 配置触发条件
   - 测试交互流程

### 测试模板

- [ ] 模拟用户选择每个选项
- [ ] 验证输出格式正确
- [ ] 检查边界情况
- [ ] 确保用户体验流畅

## 📦 使用示例

### Workflow中引用

```yaml
- step_id: '0.3'
  name: '用户确认Todo List'
  action: 'human_confirmation'
  trigger_level: 'P0'
  confirmation_type: 'todo_contract'
  template: '@交互对话模板库/todo-confirmation-template.md'
  inputs:
    - todo_list
    - estimated_timeline
  outputs:
    - confirmed_todo_list
    - user_adjustments
````

### Agent中引用

```xml
<critical-actions>
  <i>如需用户确认，使用 @交互对话模板库/[template].md</i>
</critical-actions>
```

## 🎓 最佳实践

### ✅ 推荐做法

1. **预设选项**: 提供2-4个明确选项
2. **推荐标注**: 标明推荐选项并说明理由
3. **时间透明**: 告知每个选择的时间成本
4. **允许回退**: 用户可以重新选择
5. **记录决策**: 所有交互结果都要保存

### ❌ 避免做法

1. **过多选项**: 超过5个选项会让用户困惑
2. **模糊问题**: "您觉得怎么样？"太开放
3. **技术术语**: 过多专业术语影响理解
4. **隐藏影响**: 不说明选择的后果
5. **强制选择**: 不允许用户暂停或询问

## 📈 性能指标

### 目标指标

- **理解度**: 用户第一次就理解>90%
- **决策时间**: 符合预计时间范围
- **后悔率**: <5%用户请求回退修改
- **满意度**: >85%用户反馈满意

### 监控指标

- 每个模板的使用频率
- 平均决策时间
- 回退/修改频率
- 用户反馈评分

## 🚀 未来扩展

### 计划添加

1. **多语言支持**: 中英文切换
2. **个性化**: 根据用户历史调整交互风格
3. **智能推荐**: 基于问题特征智能推荐选项
4. **可视化**: 图表辅助决策
5. **语音交互**: 支持语音输入确认

## 📚 参考资源

- [APS Module README](../../README.md)
- [Workflows README](../../workflows/README.md)
- [V4.3架构文档](../../../../调度产品设计草稿/架构总结.md)

---

**版本**: V4.3
**最后更新**: 2025-10-20
**维护**: APS Team
**核心机制**: Human-in-the-Loop, 5级触发规则
