# 能力规格: 页面规划能力 (Page Planning)

**Capability ID**: `ppt-page-planning`
**Owner**: Page Planner Agent
**Stage**: Stage 2
**Status**: Proposed

---

## Why

Story blueprints need detailed page-level specifications before visual design can begin. 70% of design inconsistency stems from unclear page type definitions and information architecture. This capability addresses:

1. **Page Type Standardization**: Classify each page into validated templates (cover, agenda, content, data, summary)
2. **Information Architecture**: Define content slots, hierarchy, and layout patterns for each page
3. **Special Requirements Identification**: Flag pages needing charts, images, or custom layouts

**Business Impact**: Reduces visual design rework from 40% to <10% by providing clear page-level specifications.

---

## What Changes

This capability introduces **Page Planning** functionality to the PPT module:

**New Agent Responsibilities**:

- **Page Planner**: Converts Story Blueprint into detailed Page Manifest with page-by-page specifications

**New Expert Library**:

- 12 page type templates (cover, title, agenda, text-heavy, text-light, data-chart, data-table, image-focus, quote, section-divider, comparison, summary)
- 15 layout patterns (title+3bullets, title+2columns, title+chart, full-image+caption, etc.)

**New Outputs**:

- **Page Manifest**: Array of page blueprints, each with page_number, page_type, layout_pattern, content_slots, special_requirements

---

## ADDED Requirements

### Requirement: REQ-PAGE-001: Page Type Assignment

The system SHALL assign one validated page type to each page based on Story Blueprint section context and position (first page → cover, last page → summary, data-heavy message → data-chart).

**Rationale**: Consistent page type classification enables layout template matching and design pattern application. Page type determines visual hierarchy, content density, and interaction patterns.

#### Scenario: 15-page pitch deck page type assignment

**Given**:

- Story Blueprint: 4 sections, 15 pages
- Section 2 "Our AI Solution" contains message "85% automation" (data-heavy)
- Page 1 is presentation start, Page 15 is end

**When**:

- Page Planner processes Story Blueprint
- Applies page type classification rules

**Then**:

- Page 1: type="cover"
- Page 2: type="agenda"
- Pages 3-4: type="text-heavy" (problem description)
- Pages 5-6: type="text-light" (solution overview)
- Page 7: type="data-chart" (automation metrics)
- Pages 8-9: type="image-focus" (product screenshots)
- Pages 10-13: type="data-chart" + "comparison" (market analysis)
- Page 14: type="text-light" (funding ask)
- Page 15: type="summary"

**Acceptance Criteria**:

- ✅ Every page has exactly one page_type from validated expert library (12 types)
- ✅ Page 1 always type="cover"
- ✅ Last page always type="summary" or "thank-you"
- ✅ Data-heavy messages (numbers, percentages, metrics) assigned type="data-chart" or "data-table"
- ✅ Image-focused messages assigned type="image-focus"

---

### Requirement: REQ-PAGE-002: Information Architecture Definition

The system SHALL define information architecture for each page, specifying content_slots (title, subtitle, body, footnote), layout_pattern, and content hierarchy.

**Rationale**: Information architecture guides content creation and visual design. Clear slot definitions prevent content overflow and ensure visual consistency.

#### Scenario: Data-chart page information architecture

**Given**:

- Page 7: type="data-chart", message="85% automation achieved"
- Expert library layout pattern: "title+chart+insight"

**When**:

- Page Planner defines information architecture
- Applies data-chart layout pattern

**Then**:

```yaml
page_7:
  page_number: 7
  page_type: 'data-chart'
  layout_pattern: 'title+chart+insight'
  content_slots:
    title:
      max_chars: 60
      hierarchy: 'H1'
      content_hint: 'Automation efficiency metric'
    chart:
      type: 'bar_chart'
      data_points: 3
      chart_hint: 'Before/After/Target automation rates'
    insight:
      max_chars: 120
      hierarchy: 'body'
      content_hint: 'Key takeaway: 85% reduction in manual work'
    footnote:
      max_chars: 80
      hierarchy: 'caption'
      content_hint: 'Data source and measurement period'
```

**Acceptance Criteria**:

- ✅ All pages have content_slots defined (minimum: title)
- ✅ Each slot includes: max_chars, hierarchy, content_hint
- ✅ Layout pattern matches page type (e.g., data-chart pages use chart-containing layouts)
- ✅ Hierarchy values: "H1" (title), "H2" (subtitle), "body", "caption"
- ✅ max_chars follows research-backed limits (title ≤60, body ≤300, caption ≤100)

---

### Requirement: REQ-PAGE-003: Page Manifest Output

The system SHALL output a structured Page Manifest in YAML format containing an array of page blueprints (total 10-20 pages), each with page_number, page_type, layout_pattern, content_slots, and special_requirements.

**Rationale**: Page Manifest serves as contract between Page Planner and downstream agents (Visual Stylist, Content Producer). YAML format supports validation and programmatic consumption.

#### Scenario: Page Manifest YAML generation for 15-page deck

**Given**:

- Story Blueprint: 4 sections, 15 pages
- Page types assigned, information architecture defined

**When**:

- Page Planner generates Page Manifest output

**Then**:

```yaml
page_manifest:
  total_pages: 15
  pages:
    - page_number: 1
      page_type: 'cover'
      layout_pattern: 'centered-title+subtitle'
      content_slots:
        title: { max_chars: 60, hierarchy: 'H1', content_hint: 'Company name + tagline' }
        subtitle: { max_chars: 120, hierarchy: 'H2', content_hint: 'Elevator pitch' }
      special_requirements: ['company_logo', 'background_image']

    - page_number: 2
      page_type: 'agenda'
      layout_pattern: 'title+numbered-list'
      content_slots:
        title: { max_chars: 40, hierarchy: 'H1', content_hint: 'Presentation roadmap' }
        body: { max_chars: 200, hierarchy: 'body', content_hint: '4 section titles' }
      special_requirements: []

    - page_number: 7
      page_type: 'data-chart'
      layout_pattern: 'title+chart+insight'
      content_slots:
        title: { max_chars: 60, hierarchy: 'H1', content_hint: 'Automation efficiency' }
        chart: { type: 'bar_chart', data_points: 3, chart_hint: 'Before/After/Target' }
        insight: { max_chars: 120, hierarchy: 'body', content_hint: '85% reduction' }
        footnote: { max_chars: 80, hierarchy: 'caption', content_hint: 'Data source' }
      special_requirements: ['chart_generation']

    # ... (pages 3-6, 8-15 omitted for brevity)

  validation:
    page_count_match: true # 15 pages = Story Blueprint total_pages
    all_types_valid: true
    all_layouts_valid: true
```

**Acceptance Criteria**:

- ✅ Valid YAML syntax
- ✅ total_pages matches Story Blueprint.total_pages
- ✅ pages array length = total_pages
- ✅ page_number sequential from 1 to total_pages
- ✅ All page_type values from expert library (12 validated types)
- ✅ All layout_pattern values from expert library (15 validated patterns)
- ✅ special_requirements array contains only recognized values (chart_generation, image_search, custom_layout, video_embed)

---

## Success Criteria

**Functional**:

- ✅ Generate Page Manifest for 15-page deck in ≤15 minutes
- ✅ Support 12 page types covering >95% of common page scenarios
- ✅ Information architecture completeness: 100% pages have defined content_slots

**Quality**:

- ✅ Page type classification accuracy >90% (expert review)
- ✅ Layout pattern matching correctness >95%
- ✅ Content slot specification completeness score >90%

**Performance**:

- ✅ Page Manifest generation latency <3 minutes for 15 pages
- ✅ Expert library template matching <100ms per page
