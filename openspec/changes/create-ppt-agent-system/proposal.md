# Proposal: Create PPT Agent System

**Change ID**: `create-ppt-agent-system`
**Type**: Feature
**Status**: Proposed
**Date**: 2025-11-22

---

## Executive Summary

Create a new BMAD module: **PPT (Presentation Creator)**, a 5-stage intelligent system that automates professional PowerPoint creation through progressive design decisions. Unlike optimization-focused workflows, this system follows the natural creative flow: Story Design → Page Planning → Visual Design → Content Production → File Generation.

**Key Innovation**: Progressive design decision-making with clear stage boundaries, minimal HITL points, and embedded quality assurance.

---

## Why

Professional presentation creation is time-intensive (2-4 hours for 15 slides) and quality-inconsistent. This change addresses:

1. **Democratization**: 80% of users lack design skills but need professional PPTs
2. **Efficiency**: Automated approach targets 60-90 minutes (3-4x faster)
3. **Creativity Support**: Guide users through design decisions rather than fully automating them

**Why Now**: document-skills:pptx capability enables hybrid architecture (agent decision-making + tool execution) without building full PPTX generation from scratch.

**Why Different from APS**: PPT creation is a **linear creative process**, not an **iterative optimization process**. It requires progressive refinement (story→structure→style→content) rather than multi-expert negotiation.

---

## What Changes

This change introduces a new BMAD module `bmad/ppt/` with a **5-Stage creative workflow**:

**New Workflow Stages** (5):

1. **Story Design**: Narrative structure selection, content outline design
2. **Page Planning**: Page type assignment, information architecture
3. **Visual Design**: Theme recommendation, layout matching, design specs
4. **Content Production**: Copywriting, chart generation, asset preparation
5. **File Generation**: PPTX creation via document-skills:pptx

**New Agents** (4 core + 2 optional):

- **Core**: Story Designer, Page Planner, Visual Stylist, File Generator
- **Optional**: Copywriter (Stage 4 helper), Chart Specialist (on-demand)

**New Data Model**:

- **PPTDesignInputs** (8 elements): Purpose, Audience, Message, Narrative, Constraints, Visual Preference, Tone of Voice, Language
- **Intermediate Outputs**: Story Blueprint, Page Manifest, Visual Design Spec, Slide Content Package

**New Capabilities** (5 specs):

1. `ppt-story-design`: Narrative structure selection, content outline generation
2. `ppt-page-planning`: Page type classification, information architecture design
3. `ppt-visual-design`: Theme recommendation, layout matching, design specification
4. `ppt-content-production`: Text generation, chart configuration, content packaging
5. `ppt-file-generation`: document-skills:pptx integration, quality validation

---

## Proposed Solution

### 5-Stage Creative Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Story Design                                        │
│ Agent: Story Designer                                        │
│ Input: User requirements (natural language)                 │
│ Output: Story Blueprint (narrative + sections + key points) │
│ Duration: 10-15 min                                         │
│ HITL: ✓ User confirms story structure                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 2: Page Planning                                       │
│ Agent: Page Planner                                          │
│ Input: Story Blueprint                                       │
│ Output: Page Manifest (page types + info architecture)      │
│ Duration: 10-15 min                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 3: Visual Design                                       │
│ Agent: Visual Stylist                                        │
│ Input: Page Manifest + Brand Guidelines (optional)          │
│ Output: Visual Design Spec (theme + layouts + standards)    │
│ Duration: 15-20 min                                         │
│ HITL: ✓ User selects theme (A/B/C)                          │
└─────────────────────────────────────────────────────────────┐
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 4: Content Production                                  │
│ Agent: Content Producer                                      │
│ Helpers: Copywriter (text polish), Chart Specialist (data)  │
│ Input: Page Manifest + Visual Spec                          │
│ Output: Complete Slide Content (text + charts + assets)     │
│ Duration: 20-30 min                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 5: File Generation                                     │
│ Agent: File Generator                                        │
│ Input: Complete Slide Content                               │
│ Output: presentation.pptx + quality report                   │
│ Duration: 5-10 min                                          │
│ Fallback: Export design documents if generation fails       │
└─────────────────────────────────────────────────────────────┘
```

**Total Time**: 90-120 minutes (conservative estimate with LLM latency and HITL wait time)

**Note**: While the primary workflow is linear (Stage 1→2→3→4→5), limited feedback loops are supported to handle edge cases:

### Stage Feedback Mechanisms

Although the workflow is primarily linear, certain failure conditions allow limited backward feedback:

**Feedback Loop 1: Visual Design → Page Planning**

- **Trigger**: Layout template mismatch (Visual Stylist cannot find suitable layout for assigned page type)
- **Action**: Visual Stylist sends feedback to Page Planner with incompatible page types
- **Page Planner Response**: Reassign problematic pages to alternative page types with compatible layouts
- **Max Retries**: 1 iteration
- **Fallback**: If still unresolved, Visual Stylist assigns closest-matching layout and logs warning

```yaml
# Example feedback scenario
stage_3_issue:
  page_7:
    assigned_type: 'custom_diagram'
    issue: "No layout template found for 'custom_diagram'"
  feedback_to_stage_2:
    request: 'Reassign page_7 to alternative type with layout support'

stage_2_adjustment:
  page_7:
    new_type: 'image-focus' # Has compatible layouts
    layout_hint: 'Use full-width image area for diagram'
```

**Feedback Loop 2: Content Production → Page Planning**

- **Trigger**: Severe content overflow (>40% over max_chars after Copywriter condensing)
- **Action**: Content Producer requests content_slots adjustment from Page Planner
- **Page Planner Response**: Increase max_chars limit OR split content across multiple pages
- **Max Retries**: 1 iteration
- **Fallback**: If still unresolved, Content Producer uses aggressive summarization (may lose detail)

```yaml
# Example feedback scenario
stage_4_issue:
  page_5:
    content_slot: 'body'
    max_chars: 300
    generated_chars: 450
    after_copywriter: 420 # Still 40% over
  feedback_to_stage_2:
    request: 'Increase body max_chars OR split into 2 pages'

stage_2_adjustment:
  option: 'split_page'
  page_5a: { body_max_chars: 250, content: 'Part 1...' }
  page_5b: { body_max_chars: 250, content: 'Part 2...' }
  total_pages: 16 # Updated from 15
```

**Design Rationale**:

- Feedback loops are **exception-based**, not routine workflow
- Maximum 1 retry per loop prevents infinite cycles
- Fallback strategies ensure workflow always completes
- Feedback is structured (not free-form negotiation) for predictability

### Core Agents

**1. Story Designer (Stage 1)**

- **Responsibility**: Transform user requirements into structured story blueprint
- **Decision Points**:
  - Select narrative structure (problem-solution, timeline, feature showcase, etc.)
  - Design content outline (3-5 sections with key messages)
  - Allocate page count per section
- **Expert Library**: 5 narrative structures, 8 audience analysis templates, 6 content organization patterns

**2. Page Planner (Stage 2)**

- **Responsibility**: Convert story blueprint into detailed page manifest
- **Decision Points**:
  - Assign page type for each slide (cover, agenda, content, data, summary)
  - Define information architecture (title + 3 bullets? title + chart?)
  - Identify special requirements (charts, images, diagrams)
- **Expert Library**: 12 page type templates, 15 layout patterns

**3. Visual Stylist (Stage 3)**

- **Responsibility**: Design visual specification for the presentation
- **Decision Points**:
  - Recommend 3 theme options (color + typography + style)
  - Match layout templates to each page type
  - Define design standards (font sizes, margins, spacing)
- **Expert Library**: 8 visual themes, 20 layout templates, CRAP design principles

**4. Content Producer (Stage 4)**

- **Responsibility**: Generate complete slide content
- **Decision Points**:
  - Write titles and body text (within character limits)
  - Prepare chart configurations for data pages
  - Provide image/icon requirements
- **Collaborates With**:
  - Copywriter: Text polishing, tone adjustment
  - Chart Specialist: Chart type selection, data formatting

**5. File Generator (Stage 5)**

- **Responsibility**: Convert design data to PPTX file
- **Tasks**:
  - Transform slide content → document-skills:pptx input format
  - Invoke document-skills:pptx to generate file
  - Run quality checks (page count, file size, completeness)
  - Fallback: Export design documents if generation fails

### Data Model

**PPTDesignInputs** (8 Core Elements):

```yaml
purpose: 'pitch_deck' # persuade/report/educate/train
audience:
  primary: 'investors'
  knowledge_level: 'business_professional'
  pain_points: ['ROI', 'market_size', 'team_capability']
message:
  core_points: ['problem_severity', 'solution_innovation', 'market_potential']
narrative: 'problem-solution' # selected by Story Designer
constraints:
  target_pages: 15
  duration_minutes: 20
  brand_guidelines: 'optional/path'
visual_preference: 'professional' # user selects or Visual Stylist recommends
tone_of_voice: 'persuasive' # formal/persuasive/casual/technical (affects copywriting)
language: 'zh-CN' # zh-CN/en-US (affects fonts, character limits, grammar)
```

**Element Descriptions**:

1. **purpose**: Presentation goal (persuade/report/educate/train)
2. **audience**: Target viewers (demographics, knowledge level, concerns)
3. **message**: Core points to communicate
4. **narrative**: Story structure template (selected by Story Designer)
5. **constraints**: Technical limits (pages, duration, brand guidelines)
6. **visual_preference**: Design style preference (professional/creative/minimal)
7. **tone_of_voice**: Copywriting tone (formal/persuasive/casual/technical) - **NEW**
8. **language**: Content language (zh-CN/en-US, affects fonts and character limits) - **NEW**

**Rationale for New Elements**:

- **tone_of_voice**: Different audiences need different tones (investors→persuasive, academics→formal). Guides Copywriter Helper's style adjustments.
- **language**: Affects font selection (Chinese fonts vs Latin fonts), character limits (Chinese: ~15 chars/line vs English: ~60 chars/line), and grammar rules.

**Intermediate Outputs**:

- **Story Blueprint** (Stage 1 output): Sections, key messages, page allocation
- **Page Manifest** (Stage 2 output): Page-by-page blueprints with types and info architecture
- **Visual Design Spec** (Stage 3 output): Theme, layouts, design standards
- **Slide Content Package** (Stage 4 output): Complete content for each slide

---

## Scope

**In Scope (MVP v1.0)**:

- 5 narrative structures (problem-solution, timeline, feature showcase, comparison, process)
- 3 presentation scenarios (Business pitch, Product launch, Technical report)
- 10-20 slide medium-sized decks
- **8 visual themes (general-purpose, non-industry-specific)**:
  - Professional Dark, Modern Light, Corporate Blue, Creative Gradient
  - Tech Green, Academic Minimal, Creative Bold, Elegant Serif
  - **Coverage**: ~70% of common business scenarios
  - **Limitation**: No industry-specific themes (finance, healthcare, education)
- **20 layout templates (1.67 avg per page type)**:
  - Covers 12 page types with basic variations
  - **Limitation**: Limited diversity (1-2 options per page type)
- Basic charts (bar, pie, line, table)
- **Language support**: Chinese (zh-CN) + English (en-US) only
- **Tone support**: 4 tones (formal, persuasive, casual, technical)
- Mode A (Quick mode: minimal HITL, 2 fixed points)

**Expert Library Coverage Limitations**:

- Visual themes optimized for **business/tech** presentations only
- Layout templates assume **standard aspect ratio** (16:9)
- Chart types limited to **basic visualizations** (no advanced analytics charts)
- No cultural customization beyond language (e.g., no region-specific design patterns)

**Out of Scope (Future v2.0+)**:

- Mode B (Thorough mode: HITL after each stage)
- **Industry-specific themes** (finance, healthcare, education, government - requires 12+ additional themes)
- **Advanced layout diversity** (36+ templates, 3 avg per page type)
- Advanced animations, video embedding
- 20+ slide large decks
- Complex charts (radar, sankey, waterfall, heatmap)
- Custom brand theme builder (user-defined color palettes and fonts)
- Multi-language (beyond CN/EN: Japanese, Korean, Spanish, etc.)
- **Cultural design adaptations** (Asian vs Western design preferences)

**Non-Goals**:

- Not replacing PowerPoint software (generates .pptx files)
- Not a general-purpose design tool (focused on presentations)
- Not supporting PDF/Keynote formats in MVP

---

## Success Criteria

**Functional Requirements**:

- ✅ Generate 15-slide professional PPT in ≤120 minutes
- ✅ Support 5 narrative structures across 3 scenarios
- ✅ Provide 3 visual theme options for user selection
- ✅ 100% design decisions traceable to expert library references

**Quality Metrics**:

- ✅ Design consistency score >85% (color, fonts, spacing uniformity)
- ✅ Content clarity >90% (readability, information hierarchy)
- ✅ Generation success rate >80% (document-skills:pptx)

**User Experience**:

- ✅ User satisfaction >80% (survey)
- ✅ Story structure accuracy >85% (user confirms without major changes)
- ✅ Visual theme acceptance >75% (user accepts one of A/B/C options)
- ✅ One-shot success rate >60% (no major revisions needed)

---

## Benefits

**vs. Manual PPT Creation**:

- 2-3x faster (90-120 min vs. 2-4 hours)
- Consistent design quality (template-driven)
- Built-in best practices (narrative structures, CRAP principles)

**vs. APS Module Design**:

- Simpler workflow (5 linear stages vs. Phase 0-4 with iterations)
- Fewer HITL points (2 vs. 5 potential interruptions)
- Clearer data flow (progressive refinement vs. model convergence)

**Architectural Benefits**:

- Reusable stage pattern for future office automation (Word, Excel)
- Clear separation of concerns (story/page/visual/content/file)
- Minimal cross-stage dependencies (clean interfaces)

---

## Risks & Mitigation

| Risk                                  | Impact    | Probability | Mitigation                                                                              |
| ------------------------------------- | --------- | ----------- | --------------------------------------------------------------------------------------- |
| **document-skills:pptx insufficient** | 🔴 High   | 🟡 Medium   | ✅ Week 2 capability validation<br/>✅ Fallback: Export design docs for manual creation |
| **Visual theme quality subjective**   | 🟡 Medium | 🟢 Low      | ✅ Provide 3 options (A/B/C)<br/>✅ Allow custom brand guidelines                       |
| **Story structure misunderstood**     | 🟡 Medium | 🟡 Medium   | ✅ HITL after Stage 1<br/>✅ Show examples during selection                             |
| **Content too verbose**               | 🟢 Low    | 🟡 Medium   | ✅ Character limits per page type<br/>✅ Copywriter helper for condensing               |

---

## Dependencies

**External**:

- document-skills:pptx capability (critical)
- BMAD-CORE v6 framework (required)

**Internal**:

- Reference APS module for "Agent as Doc" patterns
- Reuse workflow engine, state management, HITL mechanisms

---

## Implementation Plan

**Week 1: Foundation**

- Design PPTDesignInputs data model
- Create 5 stage workflow definitions
- Set up module structure

**Week 2: Core Agents (Stage 1-2)**

- Implement Story Designer + 5 narrative structure templates
- Implement Page Planner + 12 page type templates
- Test Story Blueprint → Page Manifest pipeline

**Week 3: Visual & Content (Stage 3-4)**

- Implement Visual Stylist + 8 themes + 20 layouts
- Implement Content Producer + Copywriter helper
- Validate document-skills:pptx capabilities

**Week 4: Integration & Testing**

- Implement File Generator + fallback mechanism
- End-to-end testing (3 scenarios)
- Documentation + user guide

**Timeline**: 4 weeks (20 working days)
