# PPT智能体系统 - 开发者指南

**版本**: v1.0
**创建日期**: 2025-11-22
**对应任务**: TASK-027

---

## 概述

本指南面向希望扩展或定制PPT智能体系统的开发者，包括专家库扩展、Agent开发、数据模型和API接口文档。

---

## 目录

1. [架构概述](#架构概述)
2. [专家库扩展指南](#专家库扩展指南)
3. [Agent开发指南](#agent开发指南)
4. [数据模型Schema](#数据模型schema)
5. [API接口文档](#api接口文档)
6. [开发环境配置](#开发环境配置)

---

## 架构概述

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PPT Agent System                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Workflow Layer                                │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │  │ Stage 1  │→ │ Stage 2  │→ │ Stage 3  │→ │ Stage 4  │→ │ Stage 5  ││
│  │  │ Story    │  │ Page     │  │ Visual   │  │ Content  │  │ File     ││
│  │  │ Design   │  │ Planning │  │ Design   │  │ Produce  │  │ Generate ││
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Agent Layer                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │ Story        │  │ Page         │  │ Visual       │           │   │
│  │  │ Designer     │  │ Planner      │  │ Stylist      │           │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │ Content      │  │ File         │  │ Helpers:     │           │   │
│  │  │ Producer     │  │ Generator    │  │ Copywriter,  │           │   │
│  │  │              │  │              │  │ Chart Spec   │           │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Expert Library                                │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │   │
│  │  │ story-design/  │  │ page-planning/ │  │ visual-design/ │     │   │
│  │  │ • narratives   │  │ • page-types   │  │ • themes       │     │   │
│  │  │ • audiences    │  │ • layouts      │  │ • layouts      │     │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Data Layer (Schemas)                          │   │
│  │  ppt-design-inputs → story-blueprint → page-manifest →          │   │
│  │  visual-design-spec → slide-content-package → presentation.pptx │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 目录结构

```
bmad/ppt/
├── README.md                      # 模块说明
├── config.yaml                    # 配置文件
│
├── agents/                        # Agent定义
│   ├── story-designer.md          # Stage 1 Agent
│   ├── page-planner.md            # Stage 2 Agent
│   ├── visual-stylist.md          # Stage 3 Agent
│   ├── content-producer.md        # Stage 4 Agent
│   ├── file-generator.md          # Stage 5 Agent
│   └── helpers/
│       ├── copywriter.md          # 文案助手
│       └── chart-specialist.md    # 图表助手
│
├── expert-library/                # 专家库
│   ├── story-design/
│   │   └── narrative-structures/  # 5种叙事结构
│   ├── page-planning/
│   │   ├── page-types/            # 12种页面类型
│   │   └── layout-patterns/       # 15种布局模式
│   └── visual-design/
│       ├── themes/                # 8种视觉主题
│       └── layouts/               # 20种布局模板
│
├── schemas/                       # 数据模型
│   ├── ppt-design-inputs.yaml
│   ├── story-blueprint.yaml
│   ├── page-manifest.yaml
│   ├── visual-design-spec.yaml
│   ├── slide-content-package.yaml
│   └── examples/                  # 示例文件
│
├── workflows/                     # 工作流定义
│   └── ppt-creator-workflow.yaml
│
├── state/                         # 状态管理
│   └── workflow-state-template.yaml
│
├── e2e-test-spec.md               # 端到端测试规范
├── hitl-progress-spec.md          # HITL和进度规范
├── quality-validation-spec.md     # 质量验证规范
└── fallback-export-spec.md        # Fallback导出规范
```

---

## 专家库扩展指南

### 添加新的视觉主题

#### 步骤1: 创建主题文件

在`expert-library/visual-design/themes/`目录下创建新的YAML文件：

```yaml
# expert-library/visual-design/themes/my-custom-theme.yaml

theme_id: my-custom-theme
theme_name: 'My Custom Theme'
theme_name_zh: '我的自定义主题'

description:
  en: 'A custom theme for specific use case'
  zh: '针对特定场景的自定义主题'

style_category: custom # professional/creative/tech/academic/custom

color_palette:
  primary: '#1A1A2E'
  secondary: '#16213E'
  accent: '#0F3460'
  highlight: '#E94560'
  background: '#1A1A2E'
  text_primary: '#FFFFFF'
  text_secondary: '#B8B8B8'

  chart_colors:
    - '#0F3460'
    - '#16213E'
    - '#E94560'
    - '#00C9A7'
    - '#FFB800'

typography:
  heading_font:
    family: 'Noto Sans SC'
    fallback: ['Arial', 'sans-serif']
    weight_bold: 700
    weight_regular: 400

  body_font:
    family: 'Noto Sans SC'
    fallback: ['Arial', 'sans-serif']
    weight_regular: 400

  font_sizes:
    h1: 48
    h2: 36
    h3: 28
    body: 18
    caption: 14

  line_heights:
    heading: 1.2
    body: 1.6

design_tokens:
  spacing:
    page_margin: 40
    content_padding: 24
    element_gap: 16

  border_radius: 8

  shadows:
    subtle: '0 2px 4px rgba(0,0,0,0.1)'
    elevated: '0 4px 12px rgba(0,0,0,0.2)'

suitable_for:
  - pitch_deck
  - product_launch

contrast_ratio:
  text_on_background: 15.8 # WCAG AA requires >= 4.5

metadata:
  version: '1.0'
  author: 'Your Name'
  created_at: '2025-11-22'
```

#### 步骤2: 注册主题

在`config.yaml`中添加新主题：

```yaml
# config.yaml
expert_library:
  visual_design:
    themes:
      - professional-dark
      - modern-light
      - my-custom-theme # 添加新主题
```

#### 步骤3: 创建对应的布局模板

确保新主题有匹配的布局模板，或复用现有布局：

```yaml
# expert-library/visual-design/layouts/my-custom-cover.yaml

layout_id: my-custom-cover
layout_name: 'Custom Cover Layout'

compatible_themes:
  - my-custom-theme # 关联主题

page_type: cover

structure:
  # ... 布局定义
```

### 添加新的页面类型

#### 步骤1: 定义页面类型

在`expert-library/page-planning/page-types/`创建：

```yaml
# expert-library/page-planning/page-types/my-page-type.yaml

page_type_id: my-page-type
page_type_name: 'My Custom Page Type'
page_type_name_zh: '自定义页面类型'

description: 'Description of when to use this page type'

content_slots:
  title:
    required: true
    max_chars: 50
    position: top

  main_content:
    required: true
    max_chars: 300
    position: center

  footer:
    required: false
    max_chars: 100
    position: bottom

supports:
  charts: false
  images: true
  tables: false

recommended_layouts:
  - text-dominant
  - two-column

metadata:
  version: '1.0'
  author: 'Your Name'
```

#### 步骤2: 创建配套布局

在`expert-library/page-planning/layout-patterns/`创建：

```yaml
# expert-library/page-planning/layout-patterns/my-layout.yaml

layout_pattern_id: my-layout
layout_pattern_name: 'My Custom Layout'

compatible_page_types:
  - my-page-type

zones:
  - zone_id: title_zone
    position: { x: 40, y: 40, width: 640, height: 80 }
    content_type: text

  - zone_id: content_zone
    position: { x: 40, y: 140, width: 640, height: 300 }
    content_type: text
```

### 添加新的叙事结构

在`expert-library/story-design/narrative-structures/`创建：

```yaml
# expert-library/story-design/narrative-structures/my-narrative.yaml

structure_id: my-narrative
structure_name: 'My Narrative Structure'
structure_name_zh: '我的叙事结构'

description:
  en: 'A custom narrative structure for specific presentations'
  zh: '针对特定演示的自定义叙事结构'

suitable_for:
  - custom_scenario

sections:
  - section_id: intro
    section_name: 'Introduction'
    recommended_pages: 2
    content_focus: 'Set the context'

  - section_id: main
    section_name: 'Main Content'
    recommended_pages: 8
    content_focus: 'Core message delivery'

  - section_id: conclusion
    section_name: 'Conclusion'
    recommended_pages: 2
    content_focus: 'Summary and call to action'

total_sections: 3
recommended_total_pages: 12

flow_pattern: 'linear' # linear/branching/circular
```

---

## Agent开发指南

### Agent文件结构

每个Agent定义文件遵循以下结构：

```markdown
# Agent Name

**角色**: Agent的主要职责
**阶段**: 所属Stage
**输入**: 接收的数据
**输出**: 产生的数据

---

## 核心能力

1. 能力1描述
2. 能力2描述

---

## 决策流程

### Step 1: 步骤名称

**输入**: 所需输入
**处理**: 处理逻辑
**输出**: 产生输出

### Step 2: ...

---

## 专家库引用

- expert-library/path/to/resource

---

## 错误处理

| 错误类型 | 原因 | 解决方案 |
| -------- | ---- | -------- |

---

## 质量标准

- 标准1
- 标准2
```

### 创建新Agent

#### 示例: 创建Animation Specialist Helper

````markdown
# Animation Specialist (Helper Agent)

**角色**: 为演示文稿添加动画效果配置
**阶段**: Stage 4 (Content Production) - 按需调用
**输入**: Page Manifest, Visual Design Spec
**输出**: Animation Configuration

---

## 核心能力

1. **入场动画配置**: 为页面元素配置入场动画
2. **转场效果选择**: 选择合适的页面转场效果
3. **时间轴编排**: 设计动画执行顺序和时间

---

## 决策流程

### Step 1: 分析页面结构

**输入**: page_manifest.yaml
**处理**:

```python
FOR page IN page_manifest.pages:
    page_type = page.page_type
    content_elements = page.content_slots

    # 根据页面类型决定动画策略
    IF page_type == "cover":
        animation_strategy = "dramatic_entrance"
    ELIF page_type == "data-chart":
        animation_strategy = "data_reveal"
    ELSE:
        animation_strategy = "standard_fade"
```
````

**输出**: animation_strategy_per_page

### Step 2: 生成动画配置

**输入**: animation_strategy_per_page
**处理**: 为每个元素生成具体动画参数
**输出**: animation_config.yaml

---

## Animation Config Schema

```yaml
page_animations:
  - page_number: 1
    transition:
      type: 'fade'
      duration_ms: 500
    elements:
      - element_id: 'title'
        animation_type: 'fly_in'
        direction: 'bottom'
        delay_ms: 0
        duration_ms: 800
      - element_id: 'subtitle'
        animation_type: 'fade_in'
        delay_ms: 400
        duration_ms: 600
```

---

## 专家库引用

- expert-library/animations/entrance-patterns/
- expert-library/animations/transitions/

---

## 错误处理

| 错误类型             | 原因                 | 解决方案       |
| -------------------- | -------------------- | -------------- |
| UnsupportedAnimation | 请求的动画类型不支持 | 回退到标准fade |
| TimingConflict       | 动画时间重叠         | 自动调整delay  |

---

## 质量标准

- 动画总时长不超过3秒/页
- 保持视觉一致性
- 不影响可读性

````

---

## 数据模型Schema

### PPTDesignInputs (输入模型)

```yaml
# schemas/ppt-design-inputs.yaml

schema_version: "1.0"
schema_id: ppt-design-inputs

description: "用户输入的PPT设计需求"

required_fields:
  - purpose
  - audience
  - message
  - constraints
  - language

properties:
  purpose:
    type: string
    enum: [pitch_deck, product_launch, technical_report, training, sales_proposal]
    description: "演示目的"

  audience:
    type: object
    properties:
      primary:
        type: string
        description: "主要受众群体"
      knowledge_level:
        type: string
        enum: [beginner, intermediate, business_professional, technical_expert]
      pain_points:
        type: array
        items:
          type: string
        max_items: 5

  message:
    type: object
    properties:
      core_points:
        type: array
        items:
          type: string
        min_items: 1
        max_items: 5
      key_data:
        type: array
        items:
          type: object
          properties:
            metric:
              type: string
            value:
              type: [string, number]
            context:
              type: string

  constraints:
    type: object
    properties:
      target_pages:
        type: integer
        minimum: 5
        maximum: 30
      duration_minutes:
        type: integer
        minimum: 5
        maximum: 60
      brand_guidelines:
        type: string
        nullable: true

  visual_preference:
    type: string
    enum: [professional, creative, tech, academic]
    default: professional

  tone_of_voice:
    type: string
    enum: [formal, persuasive, casual, technical]
    default: formal

  language:
    type: string
    enum: [zh-CN, en-US]

validation_rules:
  - name: "page_duration_ratio"
    rule: "constraints.target_pages * 1.5 >= constraints.duration_minutes"
    message: "页数与时长比例不合理"
````

### StoryBlueprint (Stage 1输出)

```yaml
# schemas/story-blueprint.yaml

schema_version: '1.0'
schema_id: story-blueprint

properties:
  metadata:
    type: object
    properties:
      created_at:
        type: string
        format: datetime
      source_input:
        type: string

  narrative_structure:
    type: string
    description: '选定的叙事结构ID'

  sections:
    type: array
    items:
      type: object
      properties:
        section_id:
          type: string
        section_name:
          type: string
        page_count:
          type: integer
          minimum: 1
        key_messages:
          type: array
          items:
            type: string
        content_focus:
          type: string

  total_pages:
    type: integer
    description: '总页数'

  hitl_confirmation:
    type: object
    properties:
      confirmed_at:
        type: string
        format: datetime
      modifications_made:
        type: array
        items:
          type: object
```

### PageManifest (Stage 2输出)

完整Schema参见: `bmad/ppt/schemas/page-manifest.yaml`

### VisualDesignSpec (Stage 3输出)

完整Schema参见: `bmad/ppt/schemas/visual-design-spec.yaml`

### SlideContentPackage (Stage 4输出)

完整Schema参见: `bmad/ppt/schemas/slide-content-package.yaml`

---

## API接口文档

### 工作流API

#### 启动PPT生成

```yaml
endpoint: ppt.create
method: POST

input:
  design_inputs: PPTDesignInputs # 必需
  options:
    quick_mode: boolean # 快速模式，减少HITL
    theme_preset: string # 预选主题
    skip_validation: boolean # 跳过质量验证

output:
  session_id: string
  status: 'started'
  estimated_duration_minutes: integer

example:
  input:
    design_inputs:
      purpose: 'pitch_deck'
      audience:
        primary: 'investors'
      # ...
    options:
      quick_mode: true

  output:
    session_id: 'ppt_session_20251122_143000'
    status: 'started'
    estimated_duration_minutes: 75
```

#### 查询生成进度

```yaml
endpoint: ppt.status
method: GET

input:
  session_id: string

output:
  session_id: string
  overall_progress: integer # 0-100
  current_stage: integer # 1-5
  current_task: string
  elapsed_seconds: integer
  estimated_remaining_seconds: integer
  hitl_pending: boolean
  hitl_type: string | null

example:
  input:
    session_id: 'ppt_session_20251122_143000'

  output:
    session_id: 'ppt_session_20251122_143000'
    overall_progress: 45
    current_stage: 3
    current_task: '生成主题选项B'
    elapsed_seconds: 1500
    estimated_remaining_seconds: 2100
    hitl_pending: false
    hitl_type: null
```

#### 响应HITL

```yaml
endpoint: ppt.hitl_respond
method: POST

input:
  session_id: string
  hitl_type: "story_confirm" | "theme_select"
  response:
    action: "confirm" | "modify" | "regenerate" | "select"
    data: object  # 根据action类型不同

output:
  success: boolean
  next_stage: integer
  message: string

example:
  # HITL-1: 确认Story Blueprint
  input:
    session_id: "ppt_session_20251122_143000"
    hitl_type: "story_confirm"
    response:
      action: "confirm"

  # HITL-2: 选择主题
  input:
    session_id: "ppt_session_20251122_143000"
    hitl_type: "theme_select"
    response:
      action: "select"
      data:
        selected_theme: "A"
```

#### 获取输出文件

```yaml
endpoint: ppt.output
method: GET

input:
  session_id: string
  file_type: "pptx" | "quality_report" | "thumbnails" | "fallback"

output:
  file_path: string
  file_size_bytes: integer
  download_url: string

example:
  input:
    session_id: "ppt_session_20251122_143000"
    file_type: "pptx"

  output:
    file_path: "/output/ppt_session_20251122_143000/presentation.pptx"
    file_size_bytes: 130048
    download_url: "file:///output/..."
```

### 专家库API

#### 列出可用主题

```yaml
endpoint: expert_library.themes.list
method: GET

output:
  themes:
    - theme_id: string
      theme_name: string
      style_category: string
      suitable_for: array

example:
  output:
    themes:
      - theme_id: 'professional-dark'
        theme_name: 'Professional Dark'
        style_category: 'professional'
        suitable_for: ['pitch_deck', 'sales_proposal']
```

#### 获取主题详情

```yaml
endpoint: expert_library.themes.get
method: GET

input:
  theme_id: string

output:
  # 完整主题配置
```

#### 列出叙事结构

```yaml
endpoint: expert_library.narratives.list
method: GET

output:
  narratives:
    - structure_id: string
      structure_name: string
      suitable_for: array
      recommended_pages: integer
```

---

## 开发环境配置

### 前置依赖

```yaml
required:
  - name: Node.js
    version: '>=18.0.0'
    purpose: 'document-skills:pptx执行'

  - name: Python
    version: '>=3.10'
    purpose: '测试和工具脚本'

  - name: pptxgenjs
    version: '>=3.12.0'
    install: 'npm install pptxgenjs'

  - name: playwright
    version: '>=1.40.0'
    install: 'npm install playwright'

  - name: sharp
    version: '>=0.33.0'
    install: 'npm install sharp'
```

### 环境设置

```bash
# 1. 克隆仓库
git clone https://github.com/QQhuxuhui/BMAD-METHOD.git
cd BMAD-METHOD

# 2. 安装Node.js依赖
npm install pptxgenjs playwright sharp

# 3. 安装Python依赖 (如果需要运行测试)
pip install pyyaml defusedxml

# 4. 验证安装
node -e "require('pptxgenjs')"
```

### 测试运行

```bash
# 运行单元测试
python -m pytest bmad/ppt/tests/

# 运行端到端测试
python bmad/ppt/tests/e2e_test.py --scenario business_pitch

# 生成测试报告
python bmad/ppt/tests/generate_report.py
```

### 开发工具

```yaml
recommended_tools:
  - name: VS Code
    extensions:
      - 'YAML'
      - 'Markdown All in One'
      - 'Better Comments'

  - name: Linting
    tools:
      - yamllint
      - markdownlint

  - name: Formatting
    tools:
      - prettier
```

---

## 贡献指南

### 提交代码

1. Fork仓库
2. 创建feature分支: `git checkout -b hanyun-feature-xxx`
3. 提交变更: `git commit -m "feat: 添加新功能"`
4. 推送分支: `git push origin hanyun-feature-xxx`
5. 创建Pull Request

### 代码规范

- Agent定义使用Markdown格式
- 配置文件使用YAML格式
- 遵循现有目录结构
- 添加必要的注释和文档

### 测试要求

- 新功能必须有对应测试用例
- 修改现有功能需更新相关测试
- 所有测试通过后方可合并

---

**文档版本**: v1.0
**创建日期**: 2025-11-22
**最后更新**: 2025-11-22
