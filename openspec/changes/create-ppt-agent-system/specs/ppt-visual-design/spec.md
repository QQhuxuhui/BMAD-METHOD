# 能力规格: 视觉设计能力 (Visual Design)

**Capability ID**: `ppt-visual-design`
**Owner**: Visual Stylist Agent
**Stage**: Stage 3
**Status**: Proposed

---

## Why

Visual design determines 60% of presentation impact, yet 85% of users lack design training. Inconsistent colors, typography, and layouts create unprofessional perception. This capability addresses:

1. **Design Democratization**: Provide expert-level visual design without requiring user design skills
2. **Brand Consistency**: Apply validated design principles (CRAP: Contrast, Repetition, Alignment, Proximity)
3. **User Control**: Offer 3 theme options (A/B/C) for user selection, balancing automation with personalization

**Business Impact**: Reduces visual design time from 60-90 minutes to 15-20 minutes with HITL theme selection.

---

## What Changes

This capability introduces **Visual Design** functionality to the PPT module:

**New Agent Responsibilities**:

- **Visual Stylist**: Recommends 3 theme options, matches layout templates to page types, defines design standards

**New Expert Library**:

- 8 visual themes (Professional Dark, Modern Light, Creative Gradient, Corporate Blue, Tech Green, Academic Minimal, Creative Bold, Elegant Serif)
- 20 layout templates mapped to page types
- CRAP design principle validation rules

**New Outputs**:

- **Visual Design Spec**: Theme selection (A/B/C options + user choice), layout assignments, design standards (colors, typography, spacing)

---

## ADDED Requirements

### Requirement: REQ-VISUAL-001: Theme Recommendation A/B/C

The system SHALL recommend 3 distinct visual themes based on presentation purpose, audience, and visual preference, each including color palette (primary/secondary/accent), typography (heading/body fonts), and style keywords.

**Rationale**: Multiple options respect user preference while maintaining quality. 3 options balance choice (reducing decision fatigue) with personalization. Themes must be visually distinct (>40% color difference) to provide meaningful choice.

#### Scenario: Business pitch deck theme recommendation

**Given**:

- Purpose: "pitch_deck"
- Audience: "investors"
- Visual preference: "professional"
- Expert library: 8 themes

**When**:

- Visual Stylist analyzes input requirements
- Filters themes by purpose and audience fit
- Selects 3 visually distinct themes

**Then**:
**Theme A: "Professional Dark"**

```yaml
name: 'Professional Dark'
color_palette:
  primary: '#1A1A2E' # Dark navy
  secondary: '#16213E' # Deep blue
  accent: '#0F3460' # Bright blue
  text: '#FFFFFF' # White
  background: '#0F0F0F' # Near black
typography:
  heading_font: 'Montserrat Bold'
  body_font: 'Open Sans Regular'
  heading_size: { H1: 44, H2: 32, body: 18, caption: 14 }
style_keywords: ['bold', 'high-contrast', 'modern', 'tech-focused']
rationale: 'Dark theme conveys innovation and tech expertise, suitable for tech startup pitch'
```

**Theme B: "Corporate Blue"**

```yaml
name: 'Corporate Blue'
color_palette:
  primary: '#003366' # Navy blue
  secondary: '#0055A5' # Medium blue
  accent: '#FF6B35' # Orange accent
  text: '#333333' # Dark gray
  background: '#FFFFFF' # White
typography:
  heading_font: 'Arial Bold'
  body_font: 'Arial Regular'
  heading_size: { H1: 40, H2: 28, body: 16, caption: 12 }
style_keywords: ['trustworthy', 'conservative', 'business-standard']
rationale: 'Traditional business theme, familiar to conservative investors'
```

**Theme C: "Modern Light"**

```yaml
name: 'Modern Light'
color_palette:
  primary: '#2C3E50' # Charcoal
  secondary: '#3498DB' # Sky blue
  accent: '#E74C3C' # Red accent
  text: '#2C3E50' # Charcoal
  background: '#ECF0F1' # Light gray
typography:
  heading_font: 'Lato Bold'
  body_font: 'Lato Regular'
  heading_size: { H1: 42, H2: 30, body: 17, caption: 13 }
style_keywords: ['clean', 'minimal', 'approachable', 'fresh']
rationale: 'Clean modern aesthetic balancing professionalism with approachability'
```

**Acceptance Criteria**:

- ✅ Exactly 3 theme options provided
- ✅ Each theme includes: name, color_palette (5 colors), typography (2 fonts + sizes), style_keywords, rationale
- ✅ Color palettes visually distinct (>40% difference in primary color hue/lightness)
- ✅ Rationale references user input (purpose/audience/preference)
- ✅ All themes from validated expert library (8 themes)

---

### Requirement: REQ-VISUAL-002: Layout Template Matching

The system SHALL assign one layout template from the expert library to each page type in the Page Manifest, ensuring template compatibility with page content_slots.

**Rationale**: Layout templates provide consistent visual structure. Template-to-page-type mapping ensures appropriate visual hierarchy (e.g., data-chart pages get chart-optimized layouts, text-heavy pages get readable text layouts).

#### Scenario: Layout template assignment for 15-page deck

**Given**:

- Page Manifest: 15 pages with assigned page types
- Page 7: type="data-chart", layout_pattern="title+chart+insight"
- Expert library: 20 layout templates

**When**:

- Visual Stylist matches layout templates to page types
- Filters templates compatible with layout_pattern

**Then**:

- Page 1 (cover): Template "centered-hero" (full-bleed image + centered title)
- Page 2 (agenda): Template "sidebar-list" (left sidebar + numbered list)
- Page 7 (data-chart): Template "chart-dominant" (small title + large chart area + bottom insight)
- Page 15 (summary): Template "centered-cta" (centered key message + call-to-action)

**Layout Template Specification (Page 7 example)**:

```yaml
template_id: 'chart-dominant'
page_type_compatibility: ['data-chart', 'data-table']
layout_structure:
  title_area: { position: 'top-left', width: '100%', height: '15%' }
  chart_area: { position: 'center', width: '90%', height: '65%' }
  insight_area: { position: 'bottom', width: '100%', height: '15%' }
  margins: { top: 40, right: 60, bottom: 40, left: 60 }
  grid: { columns: 12, gutter: 20 }
```

**Acceptance Criteria**:

- ✅ Every page has exactly one layout template assigned
- ✅ Template page_type_compatibility includes page's page_type
- ✅ Template layout_structure matches page's content_slots (e.g., if page has chart slot, template has chart_area)
- ✅ All templates from expert library (20 validated templates)

---

### Requirement: REQ-VISUAL-003: Design Standards Definition

The system SHALL define design standards for the selected theme, including typography specifications (font sizes, line heights, weights), color usage rules, spacing system (margins, padding, gutters), and CRAP principle compliance checks.

**Rationale**: Design standards ensure visual consistency across all pages. CRAP principles (Contrast, Repetition, Alignment, Proximity) are research-backed design fundamentals ensuring readability and professional appearance.

#### Scenario: Design standards for "Professional Dark" theme

**Given**:

- User selects Theme A: "Professional Dark"
- Page Manifest: 15 pages

**When**:

- Visual Stylist generates design standards specification

**Then**:

```yaml
design_standards:
  typography:
    H1: { font: 'Montserrat Bold', size: 44, line_height: 1.2, color: '#FFFFFF', weight: 700 }
    H2: { font: 'Montserrat Bold', size: 32, line_height: 1.3, color: '#FFFFFF', weight: 700 }
    body: { font: 'Open Sans Regular', size: 18, line_height: 1.6, color: '#FFFFFF', weight: 400 }
    caption: { font: 'Open Sans Regular', size: 14, line_height: 1.4, color: '#CCCCCC', weight: 400 }

  color_usage:
    backgrounds: ['#0F0F0F', '#1A1A2E'] # Primary backgrounds
    text: '#FFFFFF' # Primary text
    accent_usage: 'Use #0F3460 for CTAs, highlights, charts only (max 20% of page)'
    contrast_ratio: '>7:1 for body text, >4.5:1 for headings (WCAG AAA)'

  spacing:
    page_margins: { top: 60, right: 80, bottom: 60, left: 80 }
    element_padding: { small: 10, medium: 20, large: 40 }
    grid_gutter: 20
    vertical_rhythm: 8 # All vertical spacing multiples of 8px

  crap_compliance:
    contrast:
      - 'Text-background contrast ratio ≥7:1'
      - 'Accent color usage <20% per page'
    repetition:
      - 'Same font for all H1 headings across pages'
      - 'Consistent margin/padding values'
    alignment:
      - 'All elements align to 12-column grid'
      - 'Left-align body text, center-align titles'
    proximity:
      - 'Related elements <40px apart'
      - 'Unrelated sections ≥60px apart'
```

**Acceptance Criteria**:

- ✅ Typography specifications include: font, size, line_height, color, weight for H1/H2/body/caption
- ✅ Color usage rules define: backgrounds (array), text color, accent usage constraints
- ✅ Contrast ratios meet WCAG AA minimum (4.5:1 body, 3:1 headings)
- ✅ Spacing system uses consistent scale (e.g., multiples of 8px)
- ✅ CRAP compliance includes checks for all 4 principles (Contrast, Repetition, Alignment, Proximity)

---

### Requirement: REQ-VISUAL-004: Visual Design Spec Output

The system SHALL output a structured Visual Design Spec in YAML format containing: theme_options (A/B/C), user_selected_theme, layout_assignments (per page), and design_standards.

**Rationale**: Visual Design Spec serves as contract for downstream Content Producer and File Generator. Structured format enables validation and ensures all pages follow consistent design rules.

#### Scenario: Visual Design Spec YAML generation

**Given**:

- 3 theme options recommended
- User selects Theme A via HITL
- Layout templates assigned to all 15 pages
- Design standards defined

**When**:

- Visual Stylist generates Visual Design Spec output

**Then**:

```yaml
visual_design_spec:
  theme_options:
    A: { name: 'Professional Dark', color_palette: { ... }, typography: { ... } }
    B: { name: 'Corporate Blue', color_palette: { ... }, typography: { ... } }
    C: { name: 'Modern Light', color_palette: { ... }, typography: { ... } }

  user_selected_theme: 'A' # Set after HITL confirmation

  layout_assignments:
    - page_number: 1
      template_id: 'centered-hero'
      template_structure: { title_area: { ... }, subtitle_area: { ... } }
    - page_number: 7
      template_id: 'chart-dominant'
      template_structure: { title_area: { ... }, chart_area: { ... }, insight_area: { ... } }
    # ... (pages 2-6, 8-15)

  design_standards:
    typography: { H1: { ... }, H2: { ... }, body: { ... }, caption: { ... } }
    color_usage: { backgrounds: [...], text: '...', accent_usage: '...' }
    spacing: { page_margins: { ... }, element_padding: { ... }, grid_gutter: 20 }
    crap_compliance: { contrast: [...], repetition: [...], alignment: [...], proximity: [...] }

  hitl_status:
    theme_selection_confirmed: true
    selected_at: '2025-11-22T10:30:00Z'
    selection_reason: 'User prefers dark theme for tech-focused presentation'
```

**Acceptance Criteria**:

- ✅ Valid YAML syntax
- ✅ theme_options contains exactly 3 themes (A/B/C)
- ✅ user_selected_theme references one of A/B/C (or null if HITL pending)
- ✅ layout_assignments array length = Page Manifest total_pages
- ✅ Each layout assignment includes: page_number, template_id, template_structure
- ✅ design_standards includes: typography, color_usage, spacing, crap_compliance

---

## Success Criteria

**Functional**:

- ✅ Generate 3 theme options in ≤5 minutes
- ✅ Assign layout templates to 15 pages in ≤10 minutes
- ✅ HITL theme selection workflow completion rate >95%

**Quality**:

- ✅ Theme acceptance rate >75% (user selects one of A/B/C without requesting new options)
- ✅ Layout template appropriateness >90% (expert review)
- ✅ CRAP compliance score >85% (automated validation)
- ✅ Color contrast ratio compliance: 100% pages meet WCAG AA

**Performance**:

- ✅ Theme recommendation latency <3 minutes
- ✅ Layout matching latency <2 minutes for 15 pages
- ✅ Design standards generation latency <1 minute
