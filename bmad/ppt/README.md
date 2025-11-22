# PPT Creator Module

5阶段智能PPT创建系统,通过渐进式设计决策自动化专业演示文稿创建。

## 概述

PPT Creator采用线性创意流程,与优化导向的工作流不同,遵循自然的创作过程:

```
Story Design → Page Planning → Visual Design → Content Production → File Generation
```

**预计时间**: 60-90分钟(快速模式)

## 工作流阶段

### Stage 1: Story Design (故事设计)

- **Agent**: Story Designer
- **输入**: 用户需求(自然语言)
- **输出**: Story Blueprint (叙事结构 + 章节 + 关键要点)
- **HITL**: ✓ 用户确认故事结构

### Stage 2: Page Planning (页面规划)

- **Agent**: Page Planner
- **输入**: Story Blueprint
- **输出**: Page Manifest (页面类型 + 信息架构)

### Stage 3: Visual Design (视觉设计)

- **Agent**: Visual Stylist
- **输入**: Page Manifest + 品牌指南(可选)
- **输出**: Visual Design Spec (主题 + 布局 + 设计标准)
- **HITL**: ✓ 用户选择主题(A/B/C)

### Stage 4: Content Production (内容制作)

- **Agent**: Content Producer
- **Helpers**: Copywriter (文案润色), Chart Specialist (数据图表)
- **输入**: Page Manifest + Visual Spec
- **输出**: Complete Slide Content (文本 + 图表 + 资源)

### Stage 5: File Generation (文件生成)

- **Agent**: File Generator
- **输入**: Complete Slide Content
- **输出**: presentation.pptx + quality_report
- **Fallback**: 导出design_export.zip(如生成失败)

## 数据模型

### PPTDesignInputs (8个核心要素)

```yaml
purpose: 'pitch_deck' # 演示目的
audience: # 目标受众
  primary: 'investors'
  knowledge_level: 'business_professional'
message: # 核心信息
  core_points: ['problem', 'solution', 'market']
narrative: 'problem-solution' # 叙事结构
constraints: # 约束条件
  target_pages: 15
  duration_minutes: 20
visual_preference: 'professional' # 视觉偏好
tone_of_voice: 'persuasive' # 语气风格
language: 'zh-CN' # 语言
```

## 专家库

- **故事设计**: 5种叙事结构, 8个受众模板, 6种内容组织模式
- **页面规划**: 12种页面类型, 15种布局模式
- **视觉设计**: 8个视觉主题, 20个布局模板

## 支持范围

### MVP v1.0

- 10-20页中型演示文稿
- 3个场景: Business pitch, Product launch, Technical report
- 8个通用视觉主题
- 基础图表: bar, line, pie, table
- 语言: 中文(zh-CN) + 英文(en-US)

## 质量指标

- 设计一致性 >85%
- 内容清晰度 >90%
- 生成成功率 >80%
- 用户满意度 >80%

## 依赖

- **外部**: document-skills:pptx
- **内部**: BMAD-CORE v6

## 目录结构

```
bmad/ppt/
├── agents/           # Agent定义
├── workflows/        # 工作流定义
├── expert-library/   # 专家库
│   ├── story-design/
│   ├── page-planning/
│   ├── visual-design/
│   └── content-production/
├── schemas/          # 数据模型Schema
├── state/            # 状态管理
├── _module-installer/
├── config.yaml
└── README.md
```

## 版本

- **当前版本**: v1.0.0
- **开始日期**: 2025-11-22
