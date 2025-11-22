# PPT智能体系统 - 用户使用指南

**版本**: v1.0
**创建日期**: 2025-11-22

---

## 概述

PPT智能体系统是一个AI驱动的演示文稿自动化解决方案，通过5阶段工作流帮助用户快速创建专业的PowerPoint演示文稿。

### 核心特性

- **5阶段智能工作流**: Story Design → Page Planning → Visual Design → Content Production → File Generation
- **2个人机交互点**: 确认叙事结构和选择视觉主题
- **8种视觉主题**: 覆盖商务、科技、学术等场景
- **20种布局模板**: 适配12种页面类型
- **智能内容生成**: 自动生成标题、正文、图表配置

---

## Quick Start (快速开始)

### 第1步: 准备输入文件

创建一个YAML格式的输入文件，描述您的演示需求：

```yaml
# my-presentation.yaml
purpose: pitch_deck # 演示目的: pitch_deck/product_launch/technical_report

audience:
  primary: investors # 主要受众
  knowledge_level: business_professional # 知识水平
  pain_points: # 受众关注点
    - ROI证明
    - 市场规模

message:
  core_points: # 核心信息点
    - 市场痛点严重性
    - 解决方案创新性
    - 市场潜力巨大

constraints:
  target_pages: 15 # 目标页数 (10-30)
  duration_minutes: 20 # 演讲时长

visual_preference: professional # 视觉风格: professional/creative/tech

tone_of_voice: persuasive # 语气: formal/persuasive/casual/technical

language: zh-CN # 语言: zh-CN/en-US
```

### 第2步: 启动生成流程

```bash
# 使用Claude Code启动PPT生成
claude "请使用PPT智能体系统，基于 my-presentation.yaml 生成演示文稿"
```

### 第3步: 确认Story Blueprint

系统将生成叙事结构蓝图，您需要确认或修改：

```
╔══════════════════════════════════════════════════╗
║  📋 Story Blueprint 确认                          ║
╠══════════════════════════════════════════════════╣
║  叙事结构: Problem-Solution                       ║
║                                                  ║
║  Section 1: 问题陈述 (3页)                        ║
║  Section 2: 解决方案 (4页)                        ║
║  Section 3: 价值主张 (3页)                        ║
║  ...                                             ║
║                                                  ║
║  总页数: 15页                                     ║
║                                                  ║
║  [✅ 确认] [✏️ 修改] [🔄 重新生成]                 ║
╚══════════════════════════════════════════════════╝
```

**选择**:

- **确认继续**: 接受当前结构，进入下一阶段
- **修改结构**: 调整章节数量、页数分配
- **重新生成**: 使用不同叙事结构重新生成

### 第4步: 选择视觉主题

系统将推荐3个视觉主题供选择：

```
╔══════════════════════════════════════════════════╗
║  🎨 选择视觉主题                                  ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  [Theme A]        [Theme B]        [Theme C]     ║
║  Professional     Modern Light     Corporate     ║
║  Dark                              Blue          ║
║                                                  ║
║  深色背景          浅色清新          专业蓝色      ║
║  高对比度          现代科技          企业风格      ║
║                                                  ║
║  [选择A]          [选择B]          [选择C]       ║
╚══════════════════════════════════════════════════╝
```

### 第5步: 等待生成完成

系统将自动完成内容生成和文件导出：

```
🚀 PPT生成进度

Stage 1 [✅] → Stage 2 [✅] → Stage 3 [✅] → Stage 4 [🔄] → Stage 5 [⏳]

████████████████████░░░░░░░░░░  65%

当前: Stage 4 - Content Production
任务: 生成Slide 10/15内容

⏱️ 已用时间: 45分钟 | 预计剩余: 25分钟
```

### 第6步: 获取输出文件

生成完成后，您将获得：

```
output/
├── presentation.pptx      # PowerPoint文件
├── quality_report.yaml    # 质量验证报告
└── thumbnails.jpg         # 缩略图预览
```

---

## 使用场景示例

### 场景1: 商务推介 (Business Pitch)

**适用场景**: 向投资人、合作伙伴进行商业计划演示

```yaml
# business-pitch.yaml
purpose: pitch_deck
audience:
  primary: investors
  knowledge_level: business_professional
  pain_points:
    - ROI证明
    - 市场规模验证
    - 团队能力展示
message:
  core_points:
    - 市场痛点严重性
    - 解决方案创新性
    - 市场潜力巨大
    - 团队执行能力强
  key_data:
    - metric: market_size
      value: '100亿美元'
      context: TAM(总体可达市场)
    - metric: growth_rate
      value: 85
      context: 年增长率%
constraints:
  target_pages: 15
  duration_minutes: 20
visual_preference: professional
tone_of_voice: persuasive
language: zh-CN
```

**推荐主题**: Professional Dark, Corporate Blue

**预期输出**: 15页专业商务风格PPT

### 场景2: 产品发布 (Product Launch)

**适用场景**: 向客户介绍新产品功能和价值

```yaml
# product-launch.yaml
purpose: product_launch
audience:
  primary: customers
  knowledge_level: intermediate
  pain_points:
    - 易用性
    - 性价比
    - 技术支持
message:
  core_points:
    - 产品核心功能
    - 客户价值主张
    - 竞争优势
  key_data:
    - metric: user_satisfaction
      value: 95
      context: 客户满意度%
constraints:
  target_pages: 20
  duration_minutes: 30
visual_preference: creative
tone_of_voice: persuasive
language: zh-CN
```

**推荐主题**: Modern Light, Creative Gradient

**预期输出**: 20页现代创意风格PPT

### 场景3: 技术报告 (Technical Report)

**适用场景**: 向技术团队汇报系统架构和性能指标

```yaml
# technical-report.yaml
purpose: technical_report
audience:
  primary: technical_team
  knowledge_level: technical_expert
  pain_points:
    - 性能指标
    - 可扩展性
    - 可维护性
message:
  core_points:
    - 架构设计
    - 性能指标
    - 实现细节
  key_data:
    - metric: latency_p99
      value: 50
      context: ms
    - metric: throughput
      value: 10000
      context: req/s
constraints:
  target_pages: 12
  duration_minutes: 15
visual_preference: tech
tone_of_voice: technical
language: en-US
```

**推荐主题**: Academic Minimal, Tech Green

**预期输出**: 12页技术风格PPT（英文）

---

## 输入参数详解

### purpose (演示目的)

| 值                 | 描述              | 推荐叙事结构     |
| ------------------ | ----------------- | ---------------- |
| `pitch_deck`       | 商业推介/融资演示 | Problem-Solution |
| `product_launch`   | 产品发布/功能介绍 | Feature-Showcase |
| `technical_report` | 技术报告/系统汇报 | Process          |
| `training`         | 培训材料/教学演示 | Timeline         |
| `sales_proposal`   | 销售提案/客户演示 | Comparison       |

### audience (受众)

```yaml
audience:
  primary: 'investors' # 主要受众群体
  # 可选值: investors, customers, technical_team, executives, general_public

  knowledge_level: 'business_professional' # 专业水平
  # 可选值: beginner, intermediate, business_professional, technical_expert

  pain_points: # 受众关注的痛点问题 (1-5个)
    - '问题1'
    - '问题2'
```

### message (核心信息)

```yaml
message:
  core_points: # 核心信息点 (3-5个)
    - '信息点1'
    - '信息点2'

  key_data: # 关键数据 (可选，用于图表)
    - metric: '指标名称'
      value: 数值或"字符串"
      context: '单位或说明'
```

### constraints (约束条件)

```yaml
constraints:
  target_pages: 15 # 目标页数 (5-30)
  duration_minutes: 20 # 演讲时长 (5-60分钟)
  brand_guidelines: 'path/to/guidelines.pdf' # 品牌指南 (可选)
```

### visual_preference (视觉偏好)

| 值             | 描述         | 对应主题                          |
| -------------- | ------------ | --------------------------------- |
| `professional` | 专业商务风格 | Professional Dark, Corporate Blue |
| `creative`     | 创意设计风格 | Creative Gradient, Creative Bold  |
| `tech`         | 科技现代风格 | Tech Green, Modern Light          |
| `academic`     | 学术简约风格 | Academic Minimal, Elegant Serif   |

### tone_of_voice (语气)

| 值           | 描述     | 适用场景           |
| ------------ | -------- | ------------------ |
| `formal`     | 正式严肃 | 企业汇报, 学术演讲 |
| `persuasive` | 有说服力 | 商业推介, 销售提案 |
| `casual`     | 轻松随意 | 团队分享, 内部培训 |
| `technical`  | 技术专业 | 技术报告, 架构评审 |

### language (语言)

| 值      | 描述     | 字体         | 字符限制   |
| ------- | -------- | ------------ | ---------- |
| `zh-CN` | 简体中文 | Noto Sans SC | ~15字符/行 |
| `en-US` | 美式英语 | Inter, Arial | ~60字符/行 |

---

## 常见问题 (FAQ)

### Q1: 生成一个PPT需要多长时间?

**A**: 根据页数不同，大约需要60-120分钟：

- 10-15页: 60-75分钟
- 15-20页: 75-100分钟
- 20-30页: 100-120分钟

包含2次人机交互等待时间（每次约2-5分钟）。

### Q2: 如果对生成的结构不满意怎么办?

**A**: 在HITL-1（Story Blueprint确认）阶段，您可以：

1. **修改结构**: 调整章节数量和页数分配
2. **重新生成**: 选择不同的叙事结构重新生成
3. **最多重试3次**: 如果仍不满意，可以调整输入参数后重新开始

### Q3: 支持哪些图表类型?

**A**: 当前版本支持4种基础图表：

- **柱状图 (Bar Chart)**: 适合类别对比
- **折线图 (Line Chart)**: 适合趋势展示
- **饼图 (Pie Chart)**: 适合占比分析
- **表格 (Table)**: 适合详细数据展示

### Q4: 可以使用自己的品牌颜色吗?

**A**: 当前版本提供8种预设主题，暂不支持自定义品牌颜色。如需品牌定制：

1. 选择最接近的预设主题
2. 在生成的PPTX文件中手动调整颜色
3. 等待v2.0版本的品牌主题定制功能

### Q5: 生成失败怎么办?

**A**: 如果PPTX生成失败，系统会自动：

1. **重试3次**: 使用不同的布局调整策略
2. **导出设计文档**: 如果仍失败，导出`design_export.zip`

使用`design_export.zip`您可以：

- 参考配置手动创建PowerPoint
- 使用Google Slides等工具
- 联系技术支持获取帮助

### Q6: 如何优化生成效果?

**A**: 以下建议可以提升生成质量：

1. **明确受众**: 详细描述受众特征和关注点
2. **提供数据**: 在`key_data`中提供具体数字，系统会自动生成图表
3. **控制页数**: 建议10-20页，过多页数可能影响质量
4. **选择合适主题**: 根据场景选择匹配的视觉风格

### Q7: 支持哪些语言?

**A**: 当前版本支持：

- **简体中文 (zh-CN)**: 完整支持，使用思源黑体
- **美式英语 (en-US)**: 完整支持，使用Inter字体

其他语言（日语、韩语等）将在v2.0版本支持。

### Q8: 生成的PPT可以编辑吗?

**A**: 是的，生成的`.pptx`文件是标准PowerPoint格式，可以在以下软件中编辑：

- Microsoft PowerPoint (推荐)
- Google Slides
- LibreOffice Impress
- Apple Keynote (需导入)

---

## 故障排除

### 问题1: "Content Overflow" 错误

**症状**: Stage 5生成失败，提示内容溢出

**原因**: 某些页面的文本内容超出布局边界

**解决方案**:

1. 系统会自动重试（最多3次）
2. 如果仍失败，检查输入中是否有过长的描述
3. 减少`core_points`数量或简化描述

### 问题2: 主题选择后页面显示异常

**症状**: 部分页面布局混乱或颜色不一致

**原因**: 特定页面类型与布局模板不匹配

**解决方案**:

1. 在生成的PPTX中手动调整
2. 尝试选择不同的主题重新生成
3. 报告问题以便后续版本修复

### 问题3: 生成时间过长

**症状**: 总时间超过120分钟

**原因**: 页数过多或网络/系统负载高

**解决方案**:

1. 减少目标页数至20页以内
2. 检查网络连接稳定性
3. 避开系统高峰时段

### 问题4: HITL超时

**症状**: 系统提示"HITL响应超时"

**原因**: 5分钟内未做出选择

**解决方案**:

1. 系统会自动选择默认选项继续
2. 如需修改，可在生成完成后手动调整
3. 或重新开始生成流程

---

## 输出文件说明

### presentation.pptx

主要输出文件，标准PowerPoint格式。

**文件特点**:

- 16:9宽屏比例
- 包含完整内容和样式
- 可直接用于演示
- 可编辑修改

### quality_report.yaml

质量验证报告，包含：

```yaml
validation_summary:
  overall_passed: true
  page_count: 15
  file_size_kb: 127
  checks_passed: 10
  warnings: 1

validation_details:
  - level: 'Level 1'
    name: 'File Basics'
    passed: true

  - level: 'Level 3'
    name: 'Content Accuracy'
    passed: true
    warnings:
      - 'Slide 7: Text slightly exceeds recommended length'
```

### design_export.zip (仅Fallback时)

如果PPTX生成失败，系统会导出设计文档包：

```
design_export.zip
├── README.md              # 使用说明
├── METADATA.yaml          # 元数据
├── 1_inputs/              # 用户输入
├── 2_story_design/        # Stage 1输出
├── 3_page_planning/       # Stage 2输出
├── 4_visual_design/       # Stage 3输出
│   ├── visual-design-spec.yaml
│   ├── color-palette.md   # 人类可读色板
│   └── typography.md      # 人类可读字体规范
├── 5_content/             # Stage 4输出
│   └── slides-content.md  # 人类可读内容
└── logs/                  # 错误日志
```

---

## 支持与反馈

### 获取帮助

- **文档**: 查阅本用户指南
- **FAQ**: 查看常见问题解答
- **故障排除**: 按照故障排除步骤自助解决

### 反馈渠道

- **GitHub Issues**: https://github.com/QQhuxuhui/BMAD-METHOD/issues
- **功能建议**: 在Issues中提交Feature Request
- **Bug报告**: 在Issues中提交Bug Report

### 版本信息

- **当前版本**: v1.0
- **发布日期**: 2025-11-22
- **下一版本**: v2.0 (计划支持品牌定制、更多语言)

---

**文档维护**: PPT Agent System Team
**最后更新**: 2025-11-22
