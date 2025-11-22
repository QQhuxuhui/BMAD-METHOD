# 能力规格: 内容生产能力 (Content Production)

**Capability ID**: `ppt-content-production`
**Owner**: Content Producer Agent + Helpers (Copywriter, Chart Specialist)
**Stage**: Stage 4
**Status**: Proposed

---

## Why

Content quality determines presentation effectiveness, yet 75% of users struggle with concise copywriting and data visualization. Stage 4 bridges design specifications (from Stages 1-3) to executable slide content. This capability addresses:

1. **Copywriting Clarity**: Transform key messages into concise, impactful slide text (respecting character limits)
2. **Data Visualization**: Configure appropriate chart types and format data for visual impact
3. **Content Consistency**: Ensure all slides follow visual design standards (fonts, colors, tone)

**Business Impact**: Reduces content creation from 45-60 minutes (manual) to 20-30 minutes (automated with polish).

---

## What Changes

This capability introduces **Content Production** functionality to the PPT module:

**New Agent Responsibilities**:

- **Content Producer**: Orchestrates slide-by-slide content generation, enforces design standards
- **Copywriter Helper**: Polishes text for clarity, conciseness, and tone
- **Chart Specialist Helper**: Selects chart types and formats data for visualization

**New Expert Library**:

- 4 copywriting formulas (problem-agitation-solution, feature-benefit, storytelling arc, data-driven)
- Chart type decision tree (8 chart types: bar, line, pie, area, scatter, table, combo, infographic)
- Tone templates (formal, persuasive, casual, technical)

**New Outputs**:

- **Slide Content Package**: Per-slide YAML files with complete content (text, charts, images) ready for Stage 5

---

## ADDED Requirements

### Requirement: REQ-CONTENT-001: Text Content Generation

The system SHALL generate text content for each slide's content_slots (title, subtitle, body, footnote) that:

- Adheres to max_chars limits defined in Page Manifest
- Matches tone_of_voice from PPTDesignInputs (formal/persuasive/casual)
- Uses typography specifications from Visual Design Spec
- Achieves readability score ≥70 (Flesch Reading Ease)

**Rationale**: Slide text must balance information density with readability. Character limits prevent overcrowding; tone matching ensures audience engagement; typography consistency maintains professional appearance.

#### Scenario: Business pitch deck page 7 text generation

**Given**:

- Page Manifest page_7:
  ```yaml
  page_number: 7
  page_type: 'data-chart'
  content_slots:
    title: { max_chars: 60, hierarchy: 'H1', content_hint: 'Automation efficiency' }
    insight: { max_chars: 120, hierarchy: 'body', content_hint: 'Key takeaway' }
    footnote: { max_chars: 80, hierarchy: 'caption', content_hint: 'Data source' }
  ```
- Story Blueprint key_message: "85% automation achieved, reducing manual work by 70 hours/week"
- PPTDesignInputs tone_of_voice: "persuasive"

**When**:

- Content Producer generates text content
- Copywriter Helper polishes for persuasiveness

**Then**:

```yaml
page_7_content:
  title:
    text: '85% Automation Achieved in 6 Months'
    char_count: 38 # Within 60 limit
    tone: 'persuasive' # Achievement-focused framing
  insight:
    text: 'Our AI scheduling system eliminated 70 hours/week of manual work, freeing teams for strategic initiatives.'
    char_count: 118 # Within 120 limit
    readability_score: 72 # Flesch Reading Ease
  footnote:
    text: 'Measured across 12 SME clients, Jan-Jun 2025'
    char_count: 48 # Within 80 limit
```

**Acceptance Criteria**:

- ✅ All content_slots filled (no missing text)
- ✅ 100% compliance with max_chars limits (char_count ≤ max_chars)
- ✅ Tone matches PPTDesignInputs.tone_of_voice
- ✅ Readability score ≥70 for body text
- ✅ Typography references Visual Design Spec (H1/H2/body/caption hierarchy)

---

### Requirement: REQ-CONTENT-002: Chart Configuration Generation

The system SHALL generate chart configurations for data-chart and data-table page types, including:

- Chart type selection (bar/line/pie/area/scatter/table/combo) based on data characteristics
- Data formatting (categories, series, values) compatible with document-skills:pptx
- Color mapping aligned with Visual Design Spec theme colors
- Chart title and axis labels

**Rationale**: Effective data visualization requires matching chart type to data structure (e.g., trends→line, comparisons→bar, composition→pie). Consistent color mapping with theme ensures visual cohesion.

#### Scenario: Automation efficiency bar chart configuration

**Given**:

- Page Manifest page_7: type="data-chart", chart_hint="Before/After/Target automation rates"
- Story Blueprint data: {before: 15%, current: 85%, target: 95%}
- Visual Design Spec theme="Professional Dark", accent_colors=["#0F3460", "#16213E", "#1A1A2E"]

**When**:

- Chart Specialist analyzes data structure (3 categories, 1 metric)
- Applies chart type decision tree: "comparison of 3 categories" → bar chart
- Maps theme colors to data series

**Then**:

```yaml
page_7_chart:
  chart_type: 'bar'
  chart_title: 'Automation Progress'
  data:
    categories: ['Before (2024)', 'Current (2025)', 'Target (2025)']
    series:
      - name: 'Automation Rate (%)'
        values: [15, 85, 95]
        colors: ['#16213E', '#0F3460', '#1A1A2E'] # Theme accent colors
  axes:
    x_axis: { label: 'Timeline', show: true }
    y_axis: { label: 'Automation %', show: true, min: 0, max: 100 }
  chart_style:
    show_legend: false
    show_data_labels: true
    bar_width: 0.6
```

**Acceptance Criteria**:

- ✅ Chart type matches data structure (decision tree logic applied)
- ✅ Data format compatible with document-skills:pptx (categories, series, values arrays)
- ✅ Colors selected from Visual Design Spec.theme.accent_colors
- ✅ Chart has descriptive title (≤40 chars)
- ✅ Axes labeled appropriately (if applicable to chart type)

---

### Requirement: REQ-CONTENT-003: Slide Content Package Output

The system SHALL output a Slide Content Package containing:

- Per-slide YAML files (one file per page: slide_01.yaml, slide_02.yaml, etc.)
- Each file includes: page_number, page_type, text_content (all slots), chart_config (if applicable), image_requirements (if applicable)
- Package manifest listing all files and referencing Page Manifest for validation

**Rationale**: Structured per-slide output enables parallel processing in Stage 5 and simplifies debugging (each slide is an independent unit). YAML format supports human review and programmatic consumption.

#### Scenario: Slide Content Package for 15-page deck

**Given**:

- Page Manifest: 15 pages
- Content Producer generated content for all pages
- Copywriter polished text for pages 1-15
- Chart Specialist configured charts for pages 7, 10, 12

**When**:

- Content Producer assembles Slide Content Package

**Then**:
**Package Structure**:

```
slide_content_package/
├── manifest.yaml
├── slide_01_cover.yaml
├── slide_02_agenda.yaml
├── slide_03_problem.yaml
├── slide_04_problem.yaml
├── slide_05_solution.yaml
├── slide_06_solution.yaml
├── slide_07_data_chart.yaml
├── slide_08_solution.yaml
├── slide_09_solution.yaml
├── slide_10_data_chart.yaml
├── slide_11_market.yaml
├── slide_12_data_table.yaml
├── slide_13_market.yaml
├── slide_14_ask.yaml
└── slide_15_summary.yaml
```

**manifest.yaml**:

```yaml
slide_content_package:
  total_slides: 15
  slides:
    - file: 'slide_01_cover.yaml'
      page_number: 1
      page_type: 'cover'
      has_text: true
      has_chart: false
      has_image: true # Company logo
    - file: 'slide_07_data_chart.yaml'
      page_number: 7
      page_type: 'data-chart'
      has_text: true
      has_chart: true
      has_image: false
    # ... (slides 2-6, 8-15)

  validation:
    all_pages_present: true # 15 files = Page Manifest.total_pages
    all_content_slots_filled: true
    char_limit_compliance: 100% # All text within max_chars
    charts_configured: 3 # Pages 7, 10, 12
```

**slide_07_data_chart.yaml (example)**:

```yaml
slide:
  page_number: 7
  page_type: 'data-chart'
  source_page_manifest: 'page_7'

  text_content:
    title:
      text: '85% Automation Achieved in 6 Months'
      char_count: 38
      style_ref: 'Visual_Design_Spec.typography.H1'
    insight:
      text: 'Our AI scheduling system eliminated 70 hours/week of manual work...'
      char_count: 118
      style_ref: 'Visual_Design_Spec.typography.body'
    footnote:
      text: 'Measured across 12 SME clients, Jan-Jun 2025'
      char_count: 48
      style_ref: 'Visual_Design_Spec.typography.caption'

  chart_config:
    chart_type: 'bar'
    data:
      categories: ['Before (2024)', 'Current (2025)', 'Target (2025)']
      series: [{ name: 'Automation Rate (%)', values: [15, 85, 95] }]
    colors: ['#16213E', '#0F3460', '#1A1A2E']

  layout_ref: 'Visual_Design_Spec.layout_assignments.page_7' # References template_id
```

**Acceptance Criteria**:

- ✅ Package contains exactly total_pages files (15 files for 15-page deck)
- ✅ File naming convention: slide*{NN}*{page_type}.yaml
- ✅ manifest.yaml lists all slides with metadata (has_text, has_chart, has_image)
- ✅ Each slide file includes: page_number, page_type, text_content, chart_config (if applicable)
- ✅ All text_content references style_ref from Visual Design Spec
- ✅ All chart_config references theme colors from Visual Design Spec
- ✅ Validation confirms: all_pages_present, all_content_slots_filled, char_limit_compliance

---

## Success Criteria

**Functional**:

- ✅ Generate complete content for 15-page deck in ≤30 minutes
- ✅ Support all 12 page types from Page Manifest
- ✅ Configure 4 basic chart types (bar, line, pie, table) with ≥90% appropriateness

**Quality**:

- ✅ Character limit compliance: 100% (no text exceeds max_chars)
- ✅ Readability score ≥70 for body text (Flesch Reading Ease)
- ✅ Tone consistency: ≥90% of text matches PPTDesignInputs.tone_of_voice
- ✅ Chart type selection accuracy: ≥85% (expert review)
- ✅ Visual consistency: 100% content references Visual Design Spec styles

**Performance**:

- ✅ Text generation latency: <90 seconds for 15 slides (average 6 sec/slide)
- ✅ Chart configuration latency: <30 seconds for 3 charts (average 10 sec/chart)
- ✅ Copywriter polish latency: <60 seconds for 15 slides (average 4 sec/slide)
