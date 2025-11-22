# PPT智能体系统 - 端到端测试规范

**版本**: v1.0
**创建日期**: 2025-11-22
**对应任务**: TASK-021, TASK-022, TASK-028

---

## 概述

本规范定义PPT智能体系统的端到端测试流程，包括3个核心测试场景、测试指标和验收标准。

### 测试目标

1. 验证5-Stage工作流完整性
2. 验证3个核心场景的生成能力
3. 测量系统性能和成功率
4. 验证质量指标达标

---

## 测试场景定义

### 场景1: Business Pitch Deck (商务推介)

**输入文件**: `schemas/examples/business-pitch-input.yaml`

**测试配置**:

```yaml
scenario_id: E2E-001
scenario_name: Business Pitch Deck
input_file: business-pitch-input.yaml
expected_output:
  total_pages: 15
  narrative_structure: problem-solution
  visual_theme: Professional Dark
  language: zh-CN
  tone: persuasive
```

**预期输出**:

| 阶段    | 输出物               | 验证点                              |
| ------- | -------------------- | ----------------------------------- |
| Stage 1 | story-blueprint.yaml | 5个section, 15页分配                |
| Stage 2 | page-manifest.yaml   | 15页manifest, 每页有page_type       |
| Stage 3 | visual-design-spec   | Professional Dark主题, 布局匹配     |
| Stage 4 | slide-content/       | 15个slide content文件, 字符限制合规 |
| Stage 5 | presentation.pptx    | 15页PPTX文件, 质量验证通过          |

**关键验证点**:

- [ ] Story Blueprint包含problem-solution叙事结构
- [ ] Page Manifest包含cover, agenda, data-chart, summary页面类型
- [ ] Visual Design Spec选择Professional Dark主题
- [ ] 所有slide content符合max_chars限制
- [ ] PPTX文件可以正常打开
- [ ] 所有中文正确显示

### 场景2: Product Launch (产品发布)

**输入文件**: `schemas/examples/product-launch-input.yaml`

**测试配置**:

```yaml
scenario_id: E2E-002
scenario_name: Product Launch
input_file: product-launch-input.yaml
expected_output:
  total_pages: 20
  narrative_structure: feature-showcase
  visual_theme: Modern Light
  language: zh-CN
  tone: persuasive
```

**预期输出**:

| 阶段    | 输出物               | 验证点                            |
| ------- | -------------------- | --------------------------------- |
| Stage 1 | story-blueprint.yaml | feature-showcase结构, 20页        |
| Stage 2 | page-manifest.yaml   | 20页manifest, 包含image-focus类型 |
| Stage 3 | visual-design-spec   | Modern Light主题                  |
| Stage 4 | slide-content/       | 20个slide content文件             |
| Stage 5 | presentation.pptx    | 20页PPTX文件                      |

**关键验证点**:

- [ ] Story Blueprint包含feature-showcase叙事结构
- [ ] Page Manifest包含product-demo, feature-highlight页面
- [ ] Visual Design Spec选择Modern Light或Creative系主题
- [ ] slide content包含客户满意度数据可视化配置
- [ ] PPTX文件包含至少2个图表

### 场景3: Technical Report (技术报告)

**输入文件**: `schemas/examples/technical-report-input.yaml`

**测试配置**:

```yaml
scenario_id: E2E-003
scenario_name: Technical Report
input_file: technical-report-input.yaml
expected_output:
  total_pages: 12
  narrative_structure: process
  visual_theme: Academic Minimal
  language: en-US
  tone: technical
```

**预期输出**:

| 阶段    | 输出物               | 验证点                           |
| ------- | -------------------- | -------------------------------- |
| Stage 1 | story-blueprint.yaml | process叙事结构, 12页            |
| Stage 2 | page-manifest.yaml   | 12页manifest, 包含data-table类型 |
| Stage 3 | visual-design-spec   | Academic Minimal主题             |
| Stage 4 | slide-content/       | 12个slide content文件, 英文      |
| Stage 5 | presentation.pptx    | 12页PPTX文件, 英文内容           |

**关键验证点**:

- [ ] Story Blueprint包含process叙事结构
- [ ] Page Manifest包含process-flow, data-table页面
- [ ] Visual Design Spec选择Academic Minimal或Tech Green主题
- [ ] slide content为英文, 使用technical tone
- [ ] PPTX文件所有英文正确显示
- [ ] 包含性能指标表格(latency, throughput, availability)

---

## 测试执行流程

### 阶段1: 测试准备

```yaml
preparation_steps:
  - step: 1
    action: 清理测试环境
    command: rm -rf /tmp/ppt-e2e-test/

  - step: 2
    action: 创建测试目录结构
    command: |
      mkdir -p /tmp/ppt-e2e-test/{scenario1,scenario2,scenario3}
      mkdir -p /tmp/ppt-e2e-test/logs
      mkdir -p /tmp/ppt-e2e-test/reports

  - step: 3
    action: 复制输入文件
    command: |
      cp bmad/ppt/schemas/examples/*.yaml /tmp/ppt-e2e-test/

  - step: 4
    action: 验证依赖
    checks:
      - document-skills:pptx可用
      - Node.js环境可用
      - Python 3.10+可用
```

### 阶段2: 单场景执行

```yaml
execution_flow:
  - stage: 'Stage 1 - Story Design'
    input: ppt-design-inputs.yaml
    agent: story-designer.md
    output: story-blueprint.yaml
    timing: record_start_time()
    hitl_point: true # HITL确认Story Blueprint

  - stage: 'Stage 2 - Page Planning'
    input: story-blueprint.yaml
    agent: page-planner.md
    output: page-manifest.yaml
    timing: record_elapsed()

  - stage: 'Stage 3 - Visual Design'
    input: page-manifest.yaml
    agent: visual-stylist.md
    output: visual-design-spec.yaml
    hitl_point: true # HITL选择主题A/B/C
    timing: record_elapsed()

  - stage: 'Stage 4 - Content Production'
    input: page-manifest.yaml + visual-design-spec.yaml
    agent: content-producer.md
    output: slide-content-package/
    timing: record_elapsed()

  - stage: 'Stage 5 - File Generation'
    input: slide-content-package/
    agent: file-generator.md
    output: presentation.pptx
    timing: record_elapsed()
    quality_validation: true
```

### 阶段3: 结果收集

```yaml
result_collection:
  timing_metrics:
    - stage_1_duration_seconds
    - stage_2_duration_seconds
    - stage_3_duration_seconds
    - stage_4_duration_seconds
    - stage_5_duration_seconds
    - total_duration_seconds
    - hitl_wait_time_seconds

  quality_metrics:
    - page_count_accuracy: (expected - actual) / expected
    - file_size_kb
    - validation_passed: boolean
    - warning_count

  token_metrics:
    - stage_1_tokens
    - stage_2_tokens
    - stage_3_tokens
    - stage_4_tokens
    - stage_5_tokens
    - total_tokens
```

---

## 测试验证规则

### 自动化验证

#### 页面数量验证

```python
def validate_page_count(pptx_path, expected_count):
    """验证PPTX页面数量"""
    with zipfile.ZipFile(pptx_path, 'r') as zf:
        slide_files = [f for f in zf.namelist()
                      if f.startswith('ppt/slides/slide')
                      and f.endswith('.xml')]
        actual_count = len(slide_files)

    return {
        'passed': actual_count == expected_count,
        'expected': expected_count,
        'actual': actual_count,
        'difference': actual_count - expected_count
    }
```

#### 文件结构验证

```python
def validate_file_structure(scenario_dir):
    """验证输出文件结构完整性"""
    required_files = [
        'story-blueprint.yaml',
        'page-manifest.yaml',
        'visual-design-spec.yaml',
        'slide-content-package/manifest.yaml',
        'presentation.pptx'  # 或 design_export.zip
    ]

    missing = []
    for f in required_files:
        path = os.path.join(scenario_dir, f)
        if not os.path.exists(path):
            missing.append(f)

    return {
        'passed': len(missing) == 0,
        'missing_files': missing
    }
```

#### 主题一致性验证

```python
def validate_theme_consistency(visual_spec, slide_content_dir):
    """验证视觉一致性"""
    expected_colors = visual_spec['color_palette']['primary']

    # 检查每个slide content的颜色引用
    inconsistencies = []
    for slide_file in os.listdir(slide_content_dir):
        with open(os.path.join(slide_content_dir, slide_file)) as f:
            slide_data = yaml.safe_load(f)
            if slide_data.get('chart_config'):
                chart_colors = slide_data['chart_config'].get('colors', [])
                # 验证颜色是否在主题色板中
                for color in chart_colors:
                    if color not in visual_spec['color_palette']['all_colors']:
                        inconsistencies.append({
                            'slide': slide_file,
                            'color': color,
                            'issue': 'not_in_palette'
                        })

    return {
        'passed': len(inconsistencies) == 0,
        'inconsistencies': inconsistencies
    }
```

### 人工验证清单

#### 视觉质量检查

- [ ] 封面设计专业，标题清晰可读
- [ ] 颜色搭配和谐，符合主题风格
- [ ] 字体大小层级分明，易于阅读
- [ ] 布局合理，内容不拥挤
- [ ] 图表清晰，数据可读
- [ ] 无明显的设计瑕疵（对齐、间距）

#### 内容质量检查

- [ ] 标题简洁有力，概括页面内容
- [ ] 正文精简，符合PPT展示规范
- [ ] 数据准确，图表配置正确
- [ ] 叙事结构连贯，符合选定结构
- [ ] 语言风格一致，符合tone_of_voice

#### 功能完整性检查

- [ ] 所有页面可正常显示
- [ ] 动画（如有）正常播放
- [ ] 文件可以在PowerPoint/Google Slides中编辑
- [ ] 无文件损坏或乱码

---

## 性能基准 (TASK-022)

### 时间指标

| 指标              | 最低要求 | 目标值     | 上限      |
| ----------------- | -------- | ---------- | --------- |
| Stage 1 耗时      | N/A      | 10-15 min  | 20 min    |
| Stage 2 耗时      | N/A      | 10-15 min  | 20 min    |
| Stage 3 耗时      | N/A      | 15-20 min  | 30 min    |
| Stage 4 耗时      | N/A      | 20-30 min  | 45 min    |
| Stage 5 耗时      | N/A      | 5-10 min   | 15 min    |
| **总耗时** (15页) | 60 min   | 60-90 min  | 120 min   |
| **总耗时** (20页) | 75 min   | 75-100 min | 150 min   |
| HITL等待时间      | N/A      | <5 min/次  | 10 min/次 |

### 成功率指标

| 指标           | 最低要求 | 目标值 |
| -------------- | -------- | ------ |
| PPTX生成成功率 | 80%      | 90%+   |
| 质量验证通过率 | 90%      | 100%   |
| 一次性成功率   | 60%      | 75%+   |
| Fallback触发率 | <20%     | <10%   |

### Token消耗指标

| 场景                  | 预估Token | 上限 |
| --------------------- | --------- | ---- |
| 15页 Business Pitch   | 20-30K    | 50K  |
| 20页 Product Launch   | 30-40K    | 70K  |
| 12页 Technical Report | 15-25K    | 40K  |

---

## 测试报告模板

### 单场景测试报告

```yaml
# E2E测试报告 - 场景1: Business Pitch

test_metadata:
  scenario_id: E2E-001
  scenario_name: Business Pitch Deck
  test_date: 2025-11-22
  tester: [Claude/Human]

input_summary:
  input_file: business-pitch-input.yaml
  purpose: pitch_deck
  audience: investors
  target_pages: 15
  language: zh-CN

execution_timeline:
  stage_1:
    start_time: '10:00:00'
    end_time: '10:12:35'
    duration_seconds: 755
    hitl_triggered: true
    hitl_wait_seconds: 120
    output_validated: true

  stage_2:
    start_time: '10:14:35'
    end_time: '10:26:10'
    duration_seconds: 695
    output_validated: true

  stage_3:
    start_time: '10:26:10'
    end_time: '10:42:45'
    duration_seconds: 995
    hitl_triggered: true
    hitl_wait_seconds: 90
    user_selected_theme: 'A' # Professional Dark
    output_validated: true

  stage_4:
    start_time: '10:43:15'
    end_time: '11:08:30'
    duration_seconds: 1515
    pages_generated: 15
    charts_generated: 3
    output_validated: true

  stage_5:
    start_time: '11:08:30'
    end_time: '11:15:45'
    duration_seconds: 435
    retry_count: 0
    output_validated: true

results:
  total_duration_seconds: 4545 # 75.75 minutes
  hitl_total_wait_seconds: 210
  actual_work_time_seconds: 4335 # 72.25 minutes

  output_files:
    - story-blueprint.yaml: 45 lines
    - page-manifest.yaml: 320 lines
    - visual-design-spec.yaml: 180 lines
    - slide-content-package/: 15 files
    - presentation.pptx: 127 KB

  quality_validation:
    level_1_passed: true
    level_2_passed: true
    level_3_passed: true
    level_4_passed: true
    overall_passed: true
    warnings: 0

  page_count:
    expected: 15
    actual: 15
    accuracy: 100%

token_consumption:
  stage_1: 4500
  stage_2: 5200
  stage_3: 6800
  stage_4: 12000
  stage_5: 3500
  total: 32000

manual_review:
  visual_quality_score: 85/100
  content_quality_score: 90/100
  overall_satisfaction: 87/100
  issues_found:
    - severity: minor
      description: 'Slide 7 标题略长，建议精简'
    - severity: minor
      description: '图表配色可更鲜明'

conclusion:
  status: PASSED
  summary: |
    Business Pitch场景测试通过。
    总耗时75分钟，在目标范围内。
    质量验证全部通过，无重试。
    人工评审评分87分，达到≥80分标准。
```

### 汇总测试报告

```yaml
# E2E测试汇总报告

test_suite:
  name: PPT Agent System E2E Tests
  version: v1.0
  date: 2025-11-22
  scenarios_count: 3

results_summary:
  total_scenarios: 3
  passed: 3
  failed: 0
  success_rate: 100%

  scenarios:
    - id: E2E-001
      name: Business Pitch Deck
      status: PASSED
      duration_min: 75
      quality_score: 87

    - id: E2E-002
      name: Product Launch
      status: PASSED
      duration_min: 95
      quality_score: 84

    - id: E2E-003
      name: Technical Report
      status: PASSED
      duration_min: 55
      quality_score: 89

performance_metrics:
  average_duration_min: 75
  min_duration_min: 55
  max_duration_min: 95

  success_rates:
    pptx_generation: 100%
    quality_validation: 100%
    first_attempt: 67% # 2/3场景一次成功

  token_consumption:
    total: 85000
    average_per_scenario: 28333

quality_metrics:
  average_visual_score: 87
  average_content_score: 88
  average_overall_score: 87

  validation_stats:
    level_1_pass_rate: 100%
    level_2_pass_rate: 100%
    level_3_pass_rate: 100%
    level_4_pass_rate: 100%

issues_summary:
  critical: 0
  major: 0
  minor: 5
  suggestions: 3

conclusion:
  overall_status: PASSED
  meets_acceptance_criteria: true
  recommendation: '系统已达到v1.0发布标准'
```

---

## 回归测试清单 (TASK-028)

### 功能回归测试

| 测试项                | 测试方法                | 验收标准              |
| --------------------- | ----------------------- | --------------------- |
| Stage 1 Story Design  | 执行3种叙事结构测试     | 全部生成正确Blueprint |
| Stage 2 Page Planning | 验证12种页面类型分配    | 类型分配正确          |
| Stage 3 Visual Design | 测试8个视觉主题         | 主题正确应用          |
| Stage 4 Content       | 验证字符限制合规        | 100%合规              |
| Stage 5 File Gen      | 测试PPTX生成            | ≥90%成功率            |
| HITL触发点1           | 测试Story Blueprint确认 | 可正常确认/修改       |
| HITL触发点2           | 测试主题A/B/C选择       | 可正常选择            |
| Fallback机制          | 模拟生成失败            | 正确导出design_export |
| Quality Validation    | 测试4级验证             | 验证逻辑正确          |

### 边界条件测试

| 测试项     | 输入条件            | 预期结果           |
| ---------- | ------------------- | ------------------ |
| 最小页数   | target_pages: 5     | 正常生成5页PPT     |
| 最大页数   | target_pages: 30    | 正常生成30页PPT    |
| 无图表场景 | key_data: []        | 生成纯文本PPT      |
| 多图表场景 | 10个图表配置        | 所有图表正确生成   |
| 超长文本   | 500字正文           | 自动分页或截断     |
| 特殊字符   | 包含emoji和特殊符号 | 正确显示或安全替换 |

### 性能回归测试

| 测试项          | 基准值     | 允许偏差 |
| --------------- | ---------- | -------- |
| 15页PPT生成时间 | 75分钟     | ±15分钟  |
| Token消耗       | 30K tokens | ±10K     |
| PPTX文件大小    | 100-200 KB | <500 KB  |
| 内存占用        | <500 MB    | <1 GB    |

---

## 测试环境要求

### 软件依赖

```yaml
required_software:
  - name: Node.js
    version: '>=18.0.0'
    purpose: document-skills:pptx执行

  - name: Python
    version: '>=3.10'
    purpose: 测试脚本执行

  - name: pptxgenjs
    version: '>=3.12.0'
    purpose: PPTX生成

  - name: playwright
    version: '>=1.40.0'
    purpose: HTML渲染

  - name: sharp
    version: '>=0.33.0'
    purpose: 图片处理
```

### 测试数据

```yaml
test_data_location: bmad/ppt/schemas/examples/
test_data_files:
  - business-pitch-input.yaml
  - product-launch-input.yaml
  - technical-report-input.yaml
```

### 输出目录

```yaml
output_structure:
  base_dir: /tmp/ppt-e2e-test/
  subdirs:
    - scenario1/ # Business Pitch
    - scenario2/ # Product Launch
    - scenario3/ # Technical Report
    - logs/ # 执行日志
    - reports/ # 测试报告
```

---

## 版本历史

| 版本 | 日期       | 变更说明                    |
| ---- | ---------- | --------------------------- |
| v1.0 | 2025-11-22 | 初始版本，定义3场景测试规范 |

---

**文档维护**: PPT Agent System Team
**最后更新**: 2025-11-22
