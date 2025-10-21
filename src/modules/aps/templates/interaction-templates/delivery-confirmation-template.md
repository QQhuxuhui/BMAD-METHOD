# 交付确认模板

**模板ID**: `delivery-confirmation-template`
**版本**: V4.3
**用途**: Phase 4.5 - 交付确认（P0强制触发）
**触发级别**: P0 (MANDATORY)

## 使用场景

当完成质量门禁验证后，在最终交付前必须向用户展示完整的交付物清单并获得确认。

## 交互对话结构

### 第一部分: 交付物清单展示

```markdown
---
## 🎉 调度优化解决方案已准备就绪

{user_name}，我们已完成您的调度优化需求，以下是完整的交付物清单：

### 📦 交付物清单

#### 1. 核心模型与代码

**十要素模型（TenElementModel）**
- 📄 文件路径: `{ten_element_model_path}`
- 📊 文件大小: {ten_element_model_size_kb} KB
- 🔗 模型哈希: {model_hash}
- ✅ 状态: 已验证

**完整求解代码**
- 📄 文件路径: `{complete_code_path}`
- 📊 文件大小: {complete_code_size_kb} KB
- 📏 代码行数: {total_lines} 行
- ✅ 状态: 已验证（语法正确、逻辑完整、引用合规）

#### 2. 文档与使用说明

**解决方案文档**
- 📄 文件路径: `{documentation_path}`
- 📊 文件大小: {documentation_size_kb} KB
- 📖 包含内容:
  - 问题概述
  - 解决方案架构
  - 代码使用说明
  - 环境依赖
  - 输入/输出格式
  - 性能预期

**项目README**
- 📄 文件路径: `{readme_path}`
- ✅ 状态: 已生成

#### 3. 质量报告

**质量验证报告**
- 📄 文件路径: `{quality_report_path}`
- 📊 质量门禁: 6/6 通过
- ✅ 关键指标:
  - 引用合规性: ✓ 通过
  - 语法正确性: ✓ 通过
  - 逻辑完整性: ✓ 通过
  - 约束一致性: ✓ 通过
  - 基准评测: ✓ {benchmark_status}
  - 交付物持久化: ✓ 通过

**Todo完成度报告**
- 📄 文件路径: `{todo_completion_path}`
- ✅ 完成度: {todo_completion_percentage}%
- 📋 任务统计: {completed_tasks}/{total_tasks} 已完成

#### 4. 元数据

**文件清单**
- 📄 文件路径: `{manifest_path}`
- 🕒 生成时间: {timestamp}
- 🔄 工作流模式: {workflow_mode}

---

### 📁 完整输出目录结构

```
{output_folder}/
├── models/
│   ├── ten_element_model_{timestamp}.yaml
│   └── scheduling_solution_{timestamp}.py
├── docs/
│   └── solution_documentation_{timestamp}.md
├── reports/
│   ├── quality_report_{timestamp}.json
│   └── todo_completion_{timestamp}.json
├── README.md
└── file_manifest_{timestamp}.json
```

---
```

### 第二部分: 解决方案概要

```markdown
### 🎯 解决方案概要

**问题类型**: {problem_domain}
**问题规模**: {problem_scale}

**关键要素**:
- 决策变量: {decision_variables_count} 个
- 约束条件: {constraints_count} 个
- 优化目标: {objectives_description}
- 选用算法: {algorithm_name} (@引用: {algorithm_citation})

**性能预期**:
- 预计求解时间: {expected_solving_time}
- 解质量预期: {expected_solution_quality}
- 适用规模: {applicable_scale}

**引用知识模块**:
{citations_list}

---
```

### 第三部分: 下一步建议

```markdown
### 🚀 下一步建议

#### 立即可执行

1. **运行求解代码**
   ```bash
   cd {output_folder}
   python models/scheduling_solution_{timestamp}.py
   ```

2. **查看文档**
   ```bash
   cat docs/solution_documentation_{timestamp}.md
   ```

3. **验证环境依赖**
   ```bash
   {dependency_check_command}
   ```

#### 进一步优化（可选）

- 📊 **性能调优**: 调整算法参数以适配实际数据规模
- 🔧 **约束微调**: 根据实际业务规则细化约束条件
- 📈 **基准测试**: 在真实数据上运行并对比效果
- 🔄 **持续集成**: 将代码集成到现有系统

#### 知识扩展（可选）

- 📚 **算法库扩展**: 如需添加新算法，运行 `bmad extension-guide`
- 🏗️ **领域适配**: 如需其他领域问题，运行 `bmad domain-expert`
- ✅ **质量提升**: 如需更高质量标准，参考质量报告建议

---
```

### 第四部分: 用户确认请求

```markdown
### ✅ 交付确认

请确认以下事项：

**1. 文件已保存**
- [ ] 我已在 `{output_folder}` 目录中看到所有交付物

**2. 文档已查阅**
- [ ] 我已阅读解决方案文档，了解使用方式

**3. 质量报告已确认**
- [ ] 我已查看质量报告，6个质量门禁全部通过

**4. 下一步明确**
- [ ] 我知道如何运行代码和进行下一步

---

**请选择**:

[a] ✅ 确认交付，我满意这个解决方案
[b] 📝 需要微调（请说明需要调整的地方）
[c] 📊 查看详细质量报告
[d] 💾 导出交付物到其他位置
[e] ❓ 我有问题需要咨询

> 您的选择: _____

---
```

## 用户响应处理

### 响应 [a] - 确认交付

```yaml
action: "finalize_delivery"
steps:
  - 记录用户确认时间
  - 生成最终交付报告
  - 标记工作流完成
  - 感谢用户并提供后续支持方式

output_message: |
  🎉 太好了！交付已完成。

  **交付摘要**:
  - 交付时间: {delivery_timestamp}
  - 输出目录: {output_folder}
  - 文件清单: {manifest_path}

  **后续支持**:
  如您在使用过程中遇到任何问题，可以：
  1. 重新激活编排器: `bmad aps`
  2. 咨询特定专家: `bmad algorithm-expert` 或其他专家
  3. 扩展知识库: `bmad extension-guide`

  感谢您使用APS模块，祝求解顺利！ 🚀
```

### 响应 [b] - 需要微调

```yaml
action: "collect_adjustment_requests"
steps:
  - 询问用户具体需要调整什么（算法/约束/目标/其他）
  - 根据调整类型调用相应专家
  - 重新生成代码
  - 重新验证质量门禁
  - 再次进入交付确认

output_message: |
  好的，请告诉我需要调整什么：

  1. 算法选择或参数
  2. 约束条件
  3. 优化目标或权重
  4. 代码结构或注释
  5. 文档内容
  6. 其他（请说明）

  > 您的调整需求: _____
```

### 响应 [c] - 查看详细质量报告

```yaml
action: "display_quality_report"
steps:
  - 读取质量报告文件
  - 格式化展示6个质量门禁详情
  - 展示后返回交付确认

output_format: |
  ## 🛡️ 详细质量报告

  ### 门禁1: 引用合规性 ✓ 通过
  {citation_compliance_details}

  ### 门禁2: 语法正确性 ✓ 通过
  {syntax_validity_details}

  ### 门禁3: 逻辑完整性 ✓ 通过
  {logic_integrity_details}

  ### 门禁4: 约束一致性 ✓ 通过
  {constraint_consistency_details}

  ### 门禁5: 基准评测 ✓ 通过
  {benchmark_performance_details}

  ### 门禁6: 交付物持久化 ✓ 通过
  {deliverable_persistence_details}

  ---

  [返回交付确认] [退出查看]
```

### 响应 [d] - 导出到其他位置

```yaml
action: "export_deliverables"
steps:
  - 询问目标导出路径
  - 复制所有交付物到新路径
  - 验证复制成功
  - 更新文件清单
  - 返回交付确认

output_message: |
  请输入导出目标路径（绝对路径）:

  > 目标路径: _____

  [开始导出] [取消]
```

### 响应 [e] - 咨询问题

```yaml
action: "handle_questions"
steps:
  - 收集用户问题
  - 根据问题类型调用相应专家或提供文档链接
  - 回答完毕后返回交付确认

output_message: |
  我很乐意回答您的问题！

  常见问题：
  1. 如何修改算法参数？
  2. 如何添加新的约束？
  3. 如何处理不同的输入数据格式？
  4. 如何解读求解结果？
  5. 如何集成到现有系统？

  或者直接提出您的问题：

  > 您的问题: _____
```

## 模板变量说明

```yaml
required_variables:
  # 用户信息
  user_name: "用户名称（从config.yaml加载）"

  # 文件路径
  ten_element_model_path: "十要素模型文件路径"
  complete_code_path: "完整代码文件路径"
  documentation_path: "文档文件路径"
  quality_report_path: "质量报告路径"
  todo_completion_path: "Todo完成度报告路径"
  manifest_path: "文件清单路径"
  readme_path: "README路径"
  output_folder: "输出目录"

  # 文件元数据
  timestamp: "生成时间戳"
  model_hash: "模型哈希值"
  workflow_mode: "工作流模式（mode_a/mode_b）"

  # 文件大小（KB）
  ten_element_model_size_kb: "模型文件大小"
  complete_code_size_kb: "代码文件大小"
  documentation_size_kb: "文档文件大小"

  # 代码统计
  total_lines: "代码总行数"

  # 解决方案信息
  problem_domain: "问题领域"
  problem_scale: "问题规模"
  decision_variables_count: "决策变量数量"
  constraints_count: "约束数量"
  objectives_description: "目标描述"
  algorithm_name: "算法名称"
  algorithm_citation: "算法引用"

  # 性能预期
  expected_solving_time: "预计求解时间"
  expected_solution_quality: "预期解质量"
  applicable_scale: "适用规模"

  # 质量状态
  benchmark_status: "基准测试状态"

  # Todo统计
  todo_completion_percentage: "完成度百分比"
  completed_tasks: "已完成任务数"
  total_tasks: "总任务数"

  # 引用列表
  citations_list: "引用的知识模块列表"

  # 其他
  dependency_check_command: "依赖检查命令"
```

## 质量检查

- [ ] 所有交付物路径正确展示
- [ ] 文件大小和元数据准确
- [ ] 用户选项清晰明确
- [ ] 响应处理逻辑完整
- [ ] 下一步建议实用可行
- [ ] 支持微调和问题咨询
- [ ] 变量替换无遗漏

## 引用

- @编排协调专家库/交付确认流程
- @质量评测专家库/质量报告展示
- @交互对话模板库/用户确认模式
- V4.3架构规范: Phase 4.5交付确认

---

**创建**: 2025-10-21
**BMAD版本**: v6-alpha
**核心机制**: P0强制用户确认，展示完整交付物清单，确保用户满意度
