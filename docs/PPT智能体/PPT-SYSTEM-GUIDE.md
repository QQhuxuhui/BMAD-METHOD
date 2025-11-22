# PPT智能体系统使用指南 (5-Stage Architecture)

**版本**: v1.0
**文档类型**: 系统使用指南
**适用场景**: 专业演示文稿创建（商业路演、产品发布、技术汇报）
**基于**: OpenSpec提案 `create-ppt-agent-system`

---

## 系统概述

PPT智能体系统是一个基于5-Stage工作流的多智能体协作系统，专门用于创建高质量、专业级别的演示文稿。与简化的单智能体模式（`PPT-AGENT.md`）不同，本系统提供：

- **系统化流程**: Story → Page → Visual → Content → File 五个阶段
- **专家库支持**: 5种叙事结构、12种页面类型、8个视觉主题、20个布局模板
- **最少人工干预**: 仅2个关键HITL点（故事确认 + 主题选择）
- **质量保证**: CRAP设计原则验证、自动质量检查、Fallback机制
- **时长**: 90-120分钟生成15-20页专业演示文稿

### 与单智能体模式对比

| 特性           | 单智能体模式 (PPT-AGENT.md) | 5-Stage系统（本文档）        |
| -------------- | --------------------------- | ---------------------------- |
| **适用场景**   | 公司内部汇报、简单介绍      | 商业路演、产品发布、专业汇报 |
| **智能体数量** | 1个PPT设计师                | 4核心 + 2辅助（6个）         |
| **HITL次数**   | 5-8次（每阶段确认）         | 2次（关键决策点）            |
| **设计规范**   | 固定（蓝黄白灰）            | 灵活（8个可选主题）          |
| **生成时长**   | 30-60分钟                   | 90-120分钟                   |
| **页面数量**   | 5-15页                      | 10-20页                      |
| **专家库**     | 无                          | 5叙事+12页面+8主题+20布局    |
| **质量验证**   | 人工审核                    | 自动CRAP验证+结构检查        |

---

## 系统架构

### 5-Stage 工作流

```
用户输入 (PPTDesignInputs - 8要素)
    ↓
Stage 1: Story Design (故事设计)
    ↓
Story Blueprint → HITL确认点1 →
    ↓
Stage 2: Page Planning (页面规划)
    ↓
Page Manifest →
    ↓
Stage 3: Visual Design (视觉设计)
    ↓
Visual Design Spec → HITL确认点2（主题选择A/B/C）→
    ↓
Stage 4: Content Production (内容生产)
    ↓
Slide Content Package →
    ↓
Stage 5: File Generation (文件生成)
    ↓
presentation.pptx 或 design_export.zip (Fallback)
```

### 智能体团队

#### 核心智能体（4个）

1. **Story Designer** (Stage 1)
   - **职责**: 分析需求、选择叙事结构、生成故事蓝图
   - **输入**: PPTDesignInputs (8要素)
   - **输出**: Story Blueprint (叙事类型、章节划分、页面分配)
   - **专家库**: 5种叙事结构、8种受众分析模板

2. **Page Planner** (Stage 2)
   - **职责**: 页面类型分配、信息架构设计
   - **输入**: Story Blueprint
   - **输出**: Page Manifest (15页详细规格)
   - **专家库**: 12种页面类型、15种布局模式

3. **Visual Stylist** (Stage 3)
   - **职责**: 推荐3个主题选项、匹配布局模板、定义设计标准
   - **输入**: Page Manifest
   - **输出**: Visual Design Spec (主题A/B/C、布局分配、设计标准)
   - **专家库**: 8个视觉主题、20个布局模板、CRAP验证规则

4. **File Generator** (Stage 5)
   - **职责**: 调用document-skills:pptx生成.pptx、质量验证、Fallback处理
   - **输入**: Slide Content Package + Visual Design Spec
   - **输出**: presentation.pptx 或 design_export.zip
   - **依赖**: document-skills:pptx (MCP技能)

#### 辅助智能体（2个，按需调用）

5. **Copywriter** (Stage 4辅助)
   - **职责**: 文案精简（3-5-15规则）、语气调整
   - **调用时机**: 内容生成需要优化时
   - **能力**: 提升简洁度>30%、可读性>90

6. **Chart Specialist** (Stage 4按需)
   - **职责**: 图表类型选择、数据格式化、颜色映射
   - **调用时机**: 页面包含图表时
   - **能力**: 图表类型准确率>90%

---

## 数据模型

### PPTDesignInputs（8要素输入）

这是启动系统的必需输入，定义了演示文稿的核心需求：

```yaml
ppt_design_inputs:
  # 1. 目的 - 决定叙事结构选择
  purpose: 'pitch_deck'
  # 可选值: pitch_deck, product_launch, technical_report, training, sales_proposal

  # 2. 受众 - 决定内容深度和风格
  audience:
    primary: 'investors'
    knowledge_level: 'business_professional' # technical_expert/business_professional/general

  # 3. 核心信息 - 决定章节和重点
  message:
    core_points:
      - 'problem_severity'
      - 'solution_innovation'
      - 'market_potential'

  # 4. 叙事偏好 - 影响故事结构
  narrative: 'problem-solution'
  # 可选值: problem-solution, timeline, feature-showcase, comparison, process

  # 5. 约束条件 - 控制范围和时长
  constraints:
    target_pages: 15 # 10-20页
    duration_minutes: 20 # 15-30分钟

  # 6. 视觉偏好 - 影响主题推荐
  visual_preference: 'professional'
  # 可选值: professional, modern, creative, academic, corporate

  # 7. 语气风格 - 影响文案生成（NEW）
  tone_of_voice: 'persuasive'
  # 可选值: formal, persuasive, casual, technical

  # 8. 语言 - 影响字体和字符限制（NEW）
  language: 'zh-CN'
  # 可选值: zh-CN, en-US, ja-JP
```

### 中间输出

#### Story Blueprint (Stage 1输出)

```yaml
story_blueprint:
  narrative_type: 'problem-solution'
  sections:
    - title: '我们解决的问题'
      key_messages: ['SME调度效率低', '80%手工作业', '年成本$2.3M']
      page_count: 3
      page_range: [2, 4]
    - title: '我们的AI解决方案'
      key_messages: ['多智能体架构', '85%自动化', '实时优化']
      page_count: 5
      page_range: [5, 9]
    # ... 更多章节
  total_pages: 15
  estimated_duration: 20
  hitl_confirmed: false # HITL确认点1
```

#### Page Manifest (Stage 2输出)

```yaml
page_manifest:
  total_pages: 15
  pages:
    - page_number: 7
      page_type: 'data-chart' # 12种页面类型之一
      layout_pattern: 'title+chart+insight'
      content_slots:
        title: { max_chars: 60, hierarchy: 'H1', content_hint: '自动化效率指标' }
        chart: { type: 'bar_chart', data_points: 3, chart_hint: 'Before/After/Target' }
        insight: { max_chars: 120, hierarchy: 'body', content_hint: '减少85%人工' }
        footnote: { max_chars: 80, hierarchy: 'caption', content_hint: '数据来源' }
      special_requirements: ['chart_generation']
    # ... 其他14页
```

#### Visual Design Spec (Stage 3输出)

```yaml
visual_design_spec:
  theme_options:
    A:
      name: 'Professional Dark'
      color_palette:
        primary: '#1A1A2E'
        accent: '#0F3460'
        text: '#FFFFFF'
      typography:
        heading_font: 'Montserrat Bold'
        body_font: 'Open Sans Regular'
    B: { ... } # Corporate Blue
    C: { ... } # Modern Light

  user_selected_theme: 'A' # HITL确认点2

  layout_assignments:
    - page_number: 7
      template_id: 'chart-dominant'
      template_structure: { ... }

  design_standards:
    typography: { ... }
    color_usage: { ... }
    spacing: { ... }
    crap_compliance:
      contrast: ['文本对比度≥7:1', '强调色<20%']
      repetition: ['H1统一字体', '边距一致']
      alignment: ['12栏网格对齐']
      proximity: ['相关元素<40px', '无关≥60px']
```

#### Slide Content Package (Stage 4输出)

```yaml
# slide_07_data_chart.yaml
slide:
  page_number: 7
  page_type: 'data-chart'
  text_content:
    title:
      text: '6个月实现85%自动化率'
      char_count: 38 # 在60限制内
      tone: 'persuasive'
  chart_config:
    chart_type: 'bar'
    data:
      categories: ['改造前(2024)', '当前(2025)', '目标(2025)']
      series: [{ name: '自动化率(%)', values: [15, 85, 95] }]
    colors: ['#16213E', '#0F3460', '#1A1A2E']
  layout_ref: 'Visual_Design_Spec.layout_assignments.page_7'
```

---

## 使用流程

### 步骤1: 准备输入数据

创建 `ppt_design_inputs.yaml` 文件：

```yaml
ppt_design_inputs:
  purpose: 'pitch_deck'
  audience:
    primary: 'investors'
    knowledge_level: 'business_professional'
  message:
    core_points:
      - '智能调度市场痛点'
      - 'AI多智能体解决方案'
      - '12B市场机会'
  narrative: 'problem-solution'
  constraints:
    target_pages: 15
    duration_minutes: 20
  visual_preference: 'professional'
  tone_of_voice: 'persuasive'
  language: 'zh-CN'
```

### 步骤2: 启动系统

```bash
# 调用PPT智能体系统入口
bmad-ppt create --input ppt_design_inputs.yaml
```

系统将自动执行Stage 1-5，仅在2个关键点暂停等待用户确认。

### 步骤3: HITL确认点1 - Story Blueprint

**时机**: Stage 1完成后（预计15分钟）

系统会展示Story Blueprint并询问：

```
📋 Story Blueprint 已生成（4个章节，15页）

章节结构：
1. 我们解决的问题 (3页)
   - SME调度效率低、80%手工作业、年成本$2.3M
2. 我们的AI解决方案 (5页)
   - 多智能体架构、85%自动化、实时优化
3. 市场机会 (4页)
   - $12B TAM、3个竞争对手、B2B SaaS模式
4. 融资需求 (3页)
   - $2M种子轮、18个月路线图、经验丰富团队

✅ 是否确认此故事结构？
   A. 确认，继续（推荐）
   B. 调整章节顺序
   C. 增加/删除章节
   D. 重新生成（提供新的narrative类型）
```

**建议**: 85%的场景选择A直接确认。系统基于专家库生成的故事结构通常合理。

### 步骤4: HITL确认点2 - 主题选择

**时机**: Stage 3完成后（预计45分钟）

系统会展示3个主题选项：

```
🎨 Visual Design: 3个主题选项

主题A: Professional Dark
- 色调: 深蓝 + 亮蓝强调
- 风格: 高对比、现代、技术感
- 适合: 科技创业公司路演
[缩略图预览]

主题B: Corporate Blue
- 色调: 海军蓝 + 橙色强调
- 风格: 传统、商务标准
- 适合: 保守型投资人
[缩略图预览]

主题C: Modern Light
- 色调: 炭灰 + 天蓝
- 风格: 简洁、现代、亲和
- 适合: 平衡专业性和亲和力
[缩略图预览]

✅ 请选择主题：
   A. Professional Dark
   B. Corporate Blue
   C. Modern Light
   D. 查看更多主题（专家库共8个）
```

**建议**: 根据受众特点选择。科技投资人→A，传统投资人→B，广泛受众→C。

### 步骤5: 等待生成完成

确认主题后，系统自动执行：

- Stage 4: Content Production（预计30分钟）
- Stage 5: File Generation（预计10分钟）

总耗时: 90-120分钟

### 步骤6: 获取输出

**成功场景（80%+概率）**:

```
✅ PPT生成成功！

📁 文件位置: ./output/presentation.pptx
📊 总页数: 15页
📏 文件大小: 3.2 MB
⏱️ 总耗时: 95分钟

质量报告:
- 页面数量: 15/15 ✅
- 结构完整性: 通过 ✅
- CRAP合规性: 87分 ✅
- 内容完整度: 93% ✅

🎯 建议: 可直接使用，或在PowerPoint中微调
```

**Fallback场景（<20%概率）**:

如果document-skills:pptx生成失败（如图表渲染超时），系统自动导出设计文档：

```
⚠️ PPTX自动生成失败，已导出设计文档包

📁 文件位置: ./output/design_export.zip

包含内容:
- 01_story_blueprint.yaml
- 02_page_manifest.yaml
- 03_visual_design_spec.yaml
- 04_slide_content/ (15个页面内容文件)
- assets/ (图表数据.csv + 图片)
- README.md (手动组装指南)

🎯 下一步:
1. 在PowerPoint中创建空白演示文稿
2. 导入"Professional Dark"主题配色
3. 按README.md指南逐页填充内容
4. 或联系技术支持调试生成错误
```

---

## 专家库详解

### 5种叙事结构

| 叙事类型             | 适用场景           | 章节模式                  | 页面分配建议 |
| -------------------- | ------------------ | ------------------------- | ------------ |
| **problem-solution** | 商业路演、技术提案 | 问题→解决方案→验证→行动   | 3:5:4:3      |
| **timeline**         | 产品发布、发展历程 | 过去→现在→未来            | 3:6:6        |
| **feature-showcase** | 产品介绍、功能演示 | 概述→功能1→功能2→...→总结 | 2:3:3:3:4    |
| **comparison**       | 竞品分析、方案对比 | 现状→选项A→选项B→推荐     | 3:4:4:4      |
| **process**          | 流程说明、方法论   | 步骤1→步骤2→...→结果      | 均分         |

### 12种页面类型

| 页面类型            | 用途               | 信息密度 | 典型布局        |
| ------------------- | ------------------ | -------- | --------------- |
| **cover**           | 封面               | 低       | 居中标题+副标题 |
| **agenda**          | 目录               | 中       | 编号列表        |
| **text-heavy**      | 问题描述、背景     | 高       | 3-5个要点       |
| **text-light**      | 概述、总结         | 低       | 1-2个核心观点   |
| **data-chart**      | 指标展示           | 中       | 标题+图表+洞察  |
| **data-table**      | 详细数据           | 高       | 标题+表格       |
| **image-focus**     | 产品截图、效果展示 | 低       | 大图+简短说明   |
| **quote**           | 客户评价、权威引用 | 低       | 引号+来源       |
| **section-divider** | 章节分隔           | 极低     | 章节标题+装饰   |
| **comparison**      | 对比分析           | 中       | 左右两栏        |
| **summary**         | 总结回顾           | 中       | 关键要点汇总    |
| **thank-you**       | 结束页             | 低       | 联系方式        |

### 8个视觉主题

| 主题名称              | 主色调        | 风格关键词         | 适合场景           | 覆盖率 |
| --------------------- | ------------- | ------------------ | ------------------ | ------ |
| **Professional Dark** | 深蓝 + 亮蓝   | 高对比、现代、科技 | 科技创业路演       | 25%    |
| **Modern Light**      | 炭灰 + 天蓝   | 简洁、现代、亲和   | 产品发布           | 20%    |
| **Corporate Blue**    | 海军蓝 + 橙色 | 传统、信赖、商务   | 企业对企业汇报     | 15%    |
| **Tech Green**        | 深绿 + 亮绿   | 创新、环保、增长   | 可持续技术方案     | 10%    |
| **Creative Gradient** | 紫-蓝渐变     | 创意、动态、年轻   | 创意产业、设计方案 | 10%    |
| **Academic Minimal**  | 灰 + 深蓝     | 简洁、严谨、学术   | 技术报告、研究成果 | 8%     |
| **Creative Bold**     | 多色 + 黑     | 大胆、活力、个性   | 品牌发布、营销方案 | 7%     |
| **Elegant Serif**     | 深灰 + 金     | 优雅、经典、高端   | 高端产品、奢侈品   | 5%     |

**注意**: 专家库覆盖约70%常见商业场景。行业特定主题（金融、医疗、教育）将在v2.0支持。

### 20个布局模板

平均每种页面类型有1.67个布局选项。关键模板示例：

**data-chart页面的2个布局**:

1. **chart-dominant**: 小标题(15%) + 大图表(65%) + 底部洞察(15%)
2. **chart-with-sidebar**: 左侧图表(60%) + 右侧要点(35%)

**text-heavy页面的2个布局**:

1. **title+3bullets**: 标题(20%) + 3个要点列表(70%)
2. **title+2columns**: 标题(20%) + 左右两栏文本(70%)

---

## Stage间反馈机制

虽然是线性工作流，但在2个关键点有限制的反馈循环（最多1次重试）：

### 反馈循环1: Visual Design → Page Planning

**触发条件**: 布局模板无法匹配页面类型

```yaml
# Stage 3发现问题
page_7:
  assigned_type: 'custom_diagram' # Page Planner分配
  issue: '专家库无此类型的布局模板'

# 反馈到Stage 2
feedback_to_stage_2:
  request: "将page_7重新分配为 'image-focus' 或 'text-heavy'"
  max_retries: 1

# Stage 2响应
revised_page_7:
  page_type: 'image-focus' # 改为有模板支持的类型
  layout_pattern: 'full-image+caption'
```

**Fallback**: 如果1次重试后仍无法匹配，分配最接近的布局并记录警告。

### 反馈循环2: Content Production → Page Planning

**触发条件**: 严重内容溢出（>40%超过max_chars）

```yaml
# Stage 4发现问题
page_5:
  max_chars: 300
  generated_chars: 450 # 超出50%
  after_copywriter_optimization: 420 # 仍超40%

# 反馈到Stage 2
feedback_to_stage_2:
  request: 'page_5内容溢出，需要: (A)增加max_chars到500, 或 (B)拆分为2页'
  max_retries: 1

# Stage 2响应
option_A: { max_chars: 500 } # 调整限制
option_B: { split_into: [page_5a, page_5b] } # 拆分页面
```

**Fallback**: 如果1次重试后仍溢出，执行激进的文案精简（保留核心30%）。

---

## 质量保证机制

### CRAP设计原则验证

系统在Stage 3自动验证4项设计原则：

1. **Contrast（对比）**
   - 检查: 文本-背景对比度≥7:1（WCAG AAA）
   - 检查: 强调色使用<20%每页面积

2. **Repetition（重复）**
   - 检查: 所有H1标题使用相同字体
   - 检查: 边距和间距值一致

3. **Alignment（对齐）**
   - 检查: 所有元素对齐到12栏网格
   - 检查: 文本对齐规则（左对齐正文、居中标题）

4. **Proximity（亲密性）**
   - 检查: 相关元素间距<40px
   - 检查: 无关内容间距≥60px

### 文件质量检查（Stage 5）

```yaml
quality_checks:
  critical: # 必须通过
    - page_count_match: actual == expected (0容错)
    - file_opens: PowerPoint/LibreOffice无错误打开
    - file_size: 0.5MB ≤ size ≤ 50MB

  non_critical: # 警告
    - content_completeness: ≥90%页面有标题
    - theme_consistency: 色彩和字体符合Visual Design Spec
```

**验收标准**:

- 所有critical检查必须通过
- 至少80%的non-critical检查通过
- 否则触发Fallback机制

---

## 常见问题

### Q1: 为什么需要90-120分钟？单智能体模式30分钟就能完成？

**答**: 5-Stage系统针对专业场景，包含：

- 5种叙事结构的专家库匹配（vs 固定结构）
- 12种页面类型的分类和布局匹配（vs 通用模板）
- 8个主题的A/B/C推荐和设计标准生成（vs 固定色系）
- CRAP原则验证和质量检查（vs 人工审核）

**权衡**: 时间换质量。适合需要一次性成功、无需大幅修改的专业场景。

### Q2: 只有2个HITL点够吗？如果中途想修改怎么办？

**答**: 2个HITL点是战略选择：

- **HITL点1（Story）**: 确定"说什么"，是后续所有阶段的基础
- **HITL点2（Visual）**: 确定"怎么呈现"，是视觉一致性的保证

**如果需要修改**:

- Stage 1-2修改: 重新运行系统（成本低，仅15分钟）
- Stage 3-4修改: 可在PowerPoint中手动调整（设计标准已定义）

### Q3: 专家库覆盖率70%，其他30%场景怎么办？

**答**:

- **不支持场景**: 行业特定主题（金融、医疗、教育）、高度定制化布局、特殊图表类型
- **v1.0应对**: Fallback机制导出design_export.zip，手动在PowerPoint中完成
- **v2.0计划**: 扩展专家库到12+行业主题、36+布局模板

### Q4: 如果document-skills:pptx失败，设计文档包能用吗？

**答**: 是的，design_export.zip包含：

- **完整设计规格**: Story Blueprint, Page Manifest, Visual Design Spec（YAML格式）
- **每页内容**: 15个slide_XX.yaml文件（文本、图表配置）
- **资产文件**: 图表数据(.csv)、图片(.png/.jpg)
- **组装指南**: README.md（PowerPoint + LibreOffice操作步骤）

**预计组装时长**: 有经验用户60-90分钟可手动完成。

### Q5: 能否跳过某个Stage或自定义工作流？

**答**: v1.0不支持，原因：

- 5-Stage是渐进式设计决策流程，每个Stage依赖前一个的输出
- 跳过Stage会导致信息缺失（如无Visual Spec，Content Production无法确定字体和颜色）

**v2.0计划**: 支持"快速模式"（合并Stage 1+2）和"专家模式"（手动提供中间输出）

---

## 与现有PPT-AGENT的关系

本系统（5-Stage）和现有PPT-AGENT.md是**互补**而非**替代**：

### 使用场景划分

**使用PPT-AGENT.md（单智能体模式）当**:

- 公司内部汇报、团队分享（受众已知、场景熟悉）
- 5-10页简单介绍
- 固定设计规范（蓝黄白灰色系）
- 需要快速迭代（30-60分钟）
- 允许人工审核和多次修改

**使用PPT-SYSTEM（5-Stage系统）当**:

- 商业路演、产品发布、技术汇报（受众多样、场景正式）
- 10-20页专业演示
- 需要设计灵活性（8个主题可选）
- 追求一次性成功率（>60%无需大改）
- 依赖系统化质量保证

### 技术栈对比

| 组件                 | PPT-AGENT | PPT-SYSTEM                |
| -------------------- | --------- | ------------------------- |
| 智能体               | 1个单体   | 4核心+2辅助               |
| 专家库               | 无        | 5叙事+12页面+8主题+20布局 |
| document-skills:pptx | ✅        | ✅                        |
| AskUserQuestion      | 多次      | 2次                       |
| 质量验证             | 人工      | 自动CRAP+结构检查         |
| Fallback             | 无        | design_export.zip         |

---

## 下一步

### 开始使用

1. **准备环境**: 确保BMAD-CORE v6 + document-skills:pptx已安装
2. **创建输入文件**: 参考本文"使用流程"章节
3. **运行系统**: `bmad-ppt create --input ppt_design_inputs.yaml`
4. **响应HITL**: 在2个确认点做出选择
5. **获取输出**: presentation.pptx或design_export.zip

### 扩展专家库

如需为特定行业添加主题：

1. 研究 `openspec/changes/create-ppt-agent-system/proposal.md`
2. 在 `expert-library/visual-design/themes/` 添加新主题YAML
3. 更新Visual Stylist的主题匹配逻辑
4. 运行验证测试

### 贡献反馈

- **Bug报告**: GitHub Issues
- **功能请求**: 提交OpenSpec提案
- **专家库贡献**: 提交Pull Request

---

## 参考资料

- **OpenSpec提案**: `/openspec/changes/create-ppt-agent-system/proposal.md`
- **能力规格**: `/openspec/changes/create-ppt-agent-system/specs/`
  - ppt-story-design/spec.md
  - ppt-page-planning/spec.md
  - ppt-visual-design/spec.md
  - ppt-content-production/spec.md
  - ppt-file-generation/spec.md
- **实施任务**: `/openspec/changes/create-ppt-agent-system/tasks.md`
- **单智能体模式**: `/docs/PPT智能体/PPT-AGENT.md`

---

**版本**: v1.0
**最后更新**: 2025-11-22
**维护者**: BMAD-PPT团队
