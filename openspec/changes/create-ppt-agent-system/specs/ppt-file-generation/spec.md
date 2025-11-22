# 能力规格: 文件生成能力 (File Generation)

**Capability ID**: `ppt-file-generation`
**Owner**: File Generator Agent
**Stage**: Stage 5
**Status**: Proposed

---

## Why

The final deliverable is a professional .pptx file, not design documents. 30% of presentation projects fail at the "export" stage due to tool limitations or format incompatibility. This capability addresses:

1. **Reliable PPTX Generation**: Leverage document-skills:pptx to convert design data into PowerPoint-compatible files
2. **Quality Validation**: Ensure generated file meets specifications (page count, file size, structural integrity)
3. **Graceful Degradation**: Provide fallback mechanism (export design documents) when generation fails

**Business Impact**: Achieves 80%+ one-shot generation success rate, with 100% user delivery (via fallback).

---

## What Changes

This capability introduces **File Generation** functionality to the PPT module:

**New Agent Responsibilities**:

- **File Generator**: Transforms slide content into document-skills:pptx input format, invokes skill, validates output, handles fallback

**New External Dependencies**:

- document-skills:pptx (MCP skill for PPTX creation)

**New Outputs**:

- **presentation.pptx**: Final PowerPoint file (primary output)
- **design_export.zip**: Design documents package (fallback output, contains YAML specs + content files)
- **quality_report.md**: Generation quality report (page count, file size, validation results)

---

## ADDED Requirements

### Requirement: REQ-FILEGEN-001: document-skills:pptx Integration

The system SHALL transform Slide Content Package into document-skills:pptx compatible input format, invoke the skill to generate .pptx file, and handle skill invocation errors with retry logic (max 3 attempts).

**Rationale**: document-skills:pptx requires specific input format (slide structure, text formatting, chart data). Transformation layer decouples PPT module's internal data model from external skill interface. Retry logic handles transient failures (network issues, LLM timeouts).

#### Scenario: Successful PPTX generation for 15-page deck

**Given**:

- Slide Content Package: 15 pages with complete content (text, charts, images)
- Visual Design Spec: "Professional Dark" theme, layout assignments
- document-skills:pptx skill available and responsive

**When**:

- File Generator transforms content to skill input format
- Invokes document-skills:pptx with transformed input

**Then**:
**Input Format (example for Page 7 - data chart)**:

```json
{
  "slides": [
    {
      "slideNumber": 7,
      "layout": "chart-dominant",
      "elements": [
        {
          "type": "text",
          "role": "title",
          "content": "85% Automation Achieved",
          "style": {
            "font": "Montserrat Bold",
            "fontSize": 44,
            "color": "#FFFFFF",
            "alignment": "left"
          },
          "position": { "x": 60, "y": 40, "width": 880, "height": 80 }
        },
        {
          "type": "chart",
          "chartType": "bar",
          "data": {
            "categories": ["Before", "After", "Target"],
            "series": [{ "name": "Automation Rate", "values": [15, 85, 95] }]
          },
          "style": {
            "colors": ["#0F3460", "#16213E", "#1A1A2E"],
            "showLegend": false
          },
          "position": { "x": 100, "y": 150, "width": 800, "height": 400 }
        },
        {
          "type": "text",
          "role": "insight",
          "content": "Our AI system reduced manual scheduling work by 70 hours/week",
          "style": {
            "font": "Open Sans Regular",
            "fontSize": 18,
            "color": "#FFFFFF"
          },
          "position": { "x": 100, "y": 580, "width": 800, "height": 60 }
        }
      ],
      "background": { "color": "#0F0F0F" }
    }
    // ... (slides 1-6, 8-15)
  ],
  "theme": {
    "name": "Professional Dark",
    "colors": { "primary": "#1A1A2E", "accent": "#0F3460" }
  }
}
```

**Skill Invocation**:

```python
result = await document_skills.pptx.create_presentation(
    slides=transformed_input["slides"],
    theme=transformed_input["theme"],
    output_path="presentation.pptx"
)
```

**Output**:

- File created: `presentation.pptx` (3.2 MB)
- Skill response: `{"status": "success", "file_path": "presentation.pptx", "page_count": 15}`

**Acceptance Criteria**:

- ✅ Transformation completes without data loss (all content slots → skill elements)
- ✅ Skill invocation succeeds on first attempt (or retry ≤3 times on transient errors)
- ✅ Generated .pptx file exists and is readable by PowerPoint/LibreOffice
- ✅ Transformation handles all page types (cover, agenda, text-heavy, data-chart, etc.)
- ✅ Chart data correctly formatted for document-skills:pptx (categories, series, values)

---

### Requirement: REQ-FILEGEN-002: Quality Validation

The system SHALL validate the generated .pptx file against specifications: page_count matches Page Manifest total_pages (±0), file_size is reasonable (1-50 MB for 15 pages), and structural integrity (file opens without errors, all pages render).

**Rationale**: Quality validation catches generation errors early (missing pages, corrupted file, oversized file). Automated checks ensure user receives usable output without manual inspection.

#### Scenario: Quality validation for 15-page deck

**Given**:

- Page Manifest: total_pages=15
- Generated file: presentation.pptx (3.2 MB)
- Visual Design Spec: theme="Professional Dark"

**When**:

- File Generator runs quality validation checks

**Then**:
**Quality Report**:

```yaml
quality_report:
  file_info:
    file_path: 'presentation.pptx'
    file_size_mb: 3.2
    generation_time_seconds: 45

  validation_results:
    page_count:
      expected: 15
      actual: 15
      status: 'PASS'
      variance: 0

    file_size:
      size_mb: 3.2
      reasonable_range: [1.0, 50.0]
      status: 'PASS'
      note: 'Within expected range for 15-page deck with charts'

    structural_integrity:
      file_opens: true
      all_pages_render: true
      no_corruption: true
      status: 'PASS'

    content_completeness:
      pages_with_title: 15
      pages_with_body_content: 13
      charts_rendered: 6
      images_embedded: 4
      status: 'PASS'

  theme_consistency:
    color_palette_applied: true
    typography_consistent: true
    layout_templates_used: true
    status: 'PASS'

  overall_status: 'PASS'
  generation_success: true
  ready_for_delivery: true
```

**Acceptance Criteria**:

- ✅ Page count validation: actual = expected (0 variance tolerance)
- ✅ File size validation: 0.5 MB ≤ size ≤ 50 MB (reject if outside range)
- ✅ Structural integrity: File opens in PowerPoint/LibreOffice without errors
- ✅ Content completeness: ≥90% pages have title, ≥80% have body content
- ✅ Theme consistency: Color palette and typography match Visual Design Spec
- ✅ Overall status: PASS if all checks pass, FAIL if any critical check fails

**Critical Checks** (must pass):

- Page count match
- File opens without errors
- File size within range

**Non-Critical Checks** (warnings only):

- Content completeness <90%
- Theme consistency <100%

---

### Requirement: REQ-FILEGEN-003: Fallback Mechanism

The system SHALL provide fallback export when document-skills:pptx generation fails (after 3 retry attempts) or quality validation fails, exporting design documents package (design_export.zip) containing: Story Blueprint, Page Manifest, Visual Design Spec, Slide Content Package (YAML), and assembly instructions (README.md).

**Rationale**: Graceful degradation ensures 100% user delivery even when PPTX generation fails. Design export enables manual PPT creation or debugging. Assembly instructions guide users through manual file creation.

#### Scenario: Fallback export when generation fails

**Given**:

- document-skills:pptx invocation failed after 3 retries (error: "Chart rendering timeout")
- Quality validation status: FAIL (file_size=0, generation failed)
- All intermediate outputs available: Story Blueprint, Page Manifest, Visual Design Spec, Slide Content

**When**:

- File Generator triggers fallback mechanism
- Exports design documents package

**Then**:
**design_export.zip contents**:

```
design_export/
├── README.md                     # Assembly instructions
├── 01_story_blueprint.yaml       # Story design output
├── 02_page_manifest.yaml         # Page planning output
├── 03_visual_design_spec.yaml    # Visual design output
├── 04_slide_content/             # Content for each slide
│   ├── slide_01_cover.yaml
│   ├── slide_02_agenda.yaml
│   ├── slide_07_data_chart.yaml
│   └── ... (slides 3-6, 8-15)
├── assets/                       # Chart data, images
│   ├── charts/
│   │   ├── slide_07_automation_chart.csv
│   │   └── slide_10_market_chart.csv
│   └── images/
│       ├── company_logo.png
│       └── product_screenshot.png
└── generation_error_log.txt      # Error details for debugging
```

**README.md (assembly instructions)**:

```markdown
# PPT Assembly Instructions

## Generation Status

❌ Automatic PPTX generation failed after 3 attempts
Error: Chart rendering timeout (document-skills:pptx)

## Manual Assembly Steps

### Option 1: Use PowerPoint (Recommended)

1. Open PowerPoint, select "Professional Dark" theme (or import `visual_design_spec.yaml` colors)
2. Create 15 blank slides
3. For each slide, open `04_slide_content/slide_XX_*.yaml` and copy:
   - Title → slide title placeholder
   - Body → slide body placeholder
   - Charts → Insert > Chart, import data from `assets/charts/slide_XX_*.csv`
4. Apply layout templates from `02_page_manifest.yaml` (page_type → PowerPoint layout)

### Option 2: Use LibreOffice Impress

(Similar steps for LibreOffice)

### Option 3: Debug & Retry

1. Check `generation_error_log.txt` for error details
2. Fix data issues (e.g., chart data format)
3. Re-run File Generator with corrected inputs

## Design Specifications

- Theme: Professional Dark (colors in `03_visual_design_spec.yaml`)
- Total pages: 15
- Fonts: Montserrat Bold (headings), Open Sans Regular (body)
- See `03_visual_design_spec.yaml` for full design standards
```

**Acceptance Criteria**:

- ✅ Fallback triggers only when: (a) generation fails after 3 retries, OR (b) quality validation fails critically
- ✅ design_export.zip contains all intermediate outputs (4 YAML files + content folder + assets folder)
- ✅ README.md includes: error description, manual assembly steps (PowerPoint + LibreOffice), debug instructions
- ✅ Chart data exported as .csv files (readable by Excel/PowerPoint)
- ✅ Images exported as original formats (.png, .jpg)
- ✅ generation_error_log.txt contains: timestamp, error message, stack trace, skill response

---

## Success Criteria

**Functional**:

- ✅ Generate .pptx file for 15-page deck in ≤10 minutes (Stage 5 duration)
- ✅ Support all page types from Page Manifest (12 types)
- ✅ Fallback export triggers correctly on generation failure

**Quality**:

- ✅ Generation success rate ≥80% (first attempt, no fallback needed)
- ✅ Quality validation pass rate ≥95% (when generation succeeds)
- ✅ Page count accuracy: 100% (0 variance)
- ✅ File integrity: 100% (no corrupted files delivered)

**Performance**:

- ✅ PPTX generation latency ≤8 minutes for 15 pages
- ✅ Quality validation latency ≤2 minutes
- ✅ Fallback export latency ≤3 minutes

**Reliability**:

- ✅ Retry logic recovers from ≥60% transient failures
- ✅ Fallback delivery rate: 100% (user always receives deliverable, either .pptx or design_export.zip)
