# 能力规格: 故事设计能力 (Story Design)

**Capability ID**: `ppt-story-design`
**Owner**: Story Designer Agent
**Stage**: Stage 1
**Status**: Proposed

---

## Why

Professional presentation success depends on clear narrative structure. 85% of failed presentations lack coherent story flow, leading to audience confusion and message loss. This capability addresses:

1. **Narrative Clarity**: Transform vague user requirements into structured story blueprint
2. **Message Focus**: Ensure 3-5 core points are identified and prioritized
3. **Content Planning**: Allocate page count strategically across story sections

**Business Impact**: Reduces story structure iteration from 3-5 rounds to 1 HITL confirmation.

---

## What Changes

This capability introduces **Story Design** functionality to the PPT module:

**New Agent Responsibilities**:

- **Story Designer**: Analyzes user requirements, selects narrative structure, generates story blueprint

**New Expert Library**:

- 5 narrative structure templates (problem-solution, timeline, feature showcase, comparison, process)
- 8 audience analysis templates
- 6 content organization patterns

**New Outputs**:

- **Story Blueprint**: Structured YAML with narrative type, sections, key messages, page allocation

---

## ADDED Requirements

### Requirement: REQ-STORY-001: Narrative Structure Selection

The system SHALL analyze user requirements (purpose, audience, message) and recommend 1 primary narrative structure from the expert library (problem-solution, timeline, feature showcase, comparison, process).

**Rationale**: Different presentation purposes require different story patterns. A pitch deck needs problem-solution; a product launch needs timeline; a comparison report needs side-by-side structure.

#### Scenario: Business pitch deck narrative selection

**Given**:

- User input: purpose="pitch_deck", audience="investors", message="AI scheduling platform value"
- Expert library contains 5 narrative structures

**When**:

- Story Designer analyzes input requirements
- Matches purpose="pitch_deck" + audience="investors" pattern

**Then**:

- System recommends "problem-solution" narrative
- Provides rationale: "Investors need problem severity → solution innovation → market potential flow"

**Acceptance Criteria**:

- ✅ Recommendation includes narrative structure name and description
- ✅ Rationale references user input elements (purpose/audience/message)
- ✅ Structure selected from validated expert library templates

---

### Requirement: REQ-STORY-002: Content Outline Design

The system SHALL generate a content outline with 3-5 sections, each containing 2-4 key messages and target page allocation (total 10-20 pages).

**Rationale**: Clear section boundaries and page limits prevent content overload. Research shows 3-5 sections optimize audience retention, and 15-slide decks are industry standard for business presentations.

#### Scenario: 15-page pitch deck outline generation

**Given**:

- Narrative structure: "problem-solution"
- User constraints: target_pages=15, duration_minutes=20
- Core messages: ["problem_severity", "solution_innovation", "market_potential"]

**When**:

- Story Designer generates content outline
- Applies problem-solution template with page allocation rules

**Then**:

- Section 1 "Problem" (3 pages): pain points, market gap, cost of inaction
- Section 2 "Solution" (5 pages): product overview, key features, technical advantages
- Section 3 "Market" (4 pages): TAM/SAM/SOM, competition, go-to-market
- Section 4 "Ask" (3 pages): funding needs, roadmap, team

**Acceptance Criteria**:

- ✅ Total sections: 3-5
- ✅ Total pages: 10-20 (matches user constraints ±2 pages)
- ✅ Each section has 2-4 key messages
- ✅ Page allocation proportional to section importance

---

### Requirement: REQ-STORY-003: Story Blueprint Output

The system SHALL output a structured Story Blueprint in YAML format containing: narrative_type, sections (with titles, key_messages, page_count), total_pages, estimated_duration, and HITL confirmation status.

**Rationale**: Structured output enables downstream agents (Page Planner) to consume story decisions programmatically. YAML format supports human review during HITL confirmation.

#### Scenario: Story Blueprint YAML generation

**Given**:

- Narrative structure: "problem-solution"
- Content outline: 4 sections, 15 pages total

**When**:

- Story Designer finalizes story design
- Generates Story Blueprint output

**Then**:

```yaml
story_blueprint:
  narrative_type: 'problem-solution'
  sections:
    - title: "The Problem We're Solving"
      key_messages: ['SME scheduling inefficiency', '80% manual work', '$2.3M annual cost']
      page_count: 3
      page_range: [2, 4] # excluding cover
    - title: 'Our AI Solution'
      key_messages: ['Multi-agent architecture', '85% automation', 'Real-time optimization']
      page_count: 5
      page_range: [5, 9]
    - title: 'Market Opportunity'
      key_messages: ['$12B TAM', '3 competitors', 'B2B SaaS model']
      page_count: 4
      page_range: [10, 13]
    - title: 'The Ask'
      key_messages: ['$2M seed round', '18-month roadmap', 'Experienced team']
      page_count: 3
      page_range: [14, 16] # including summary
  total_pages: 15
  estimated_duration: 20
  hitl_confirmed: false
```

**Acceptance Criteria**:

- ✅ Valid YAML syntax
- ✅ All required fields present (narrative_type, sections, total_pages)
- ✅ Sections include: title, key_messages (array), page_count, page_range
- ✅ total_pages = sum of section page_counts
- ✅ page_range values are sequential and non-overlapping

---

## Success Criteria

**Functional**:

- ✅ Generate Story Blueprint for 3 scenarios (business pitch, product launch, technical report) in ≤15 minutes
- ✅ Support 5 narrative structures with >90% coverage of common use cases
- ✅ HITL confirmation acceptance rate >85% (user approves without major changes)

**Quality**:

- ✅ Story structure accuracy >85% (user feedback survey)
- ✅ Page allocation variance ≤10% from optimal distribution
- ✅ Key message clarity score >90% (readability metrics)

**Performance**:

- ✅ Story Blueprint generation latency <2 minutes (LLM calls + template matching)
- ✅ Expert library query response time <500ms
