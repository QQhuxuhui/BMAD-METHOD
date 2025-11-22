# PPT智能体系统 - HITL体验与进度可视化规范

**版本**: v1.0
**创建日期**: 2025-11-22
**对应任务**: TASK-024, TASK-025

---

## 概述

本规范定义PPT智能体系统的人机交互(HITL)体验优化和进度可视化设计，确保用户在PPT生成过程中获得清晰的反馈和流畅的交互体验。

---

## Part 1: HITL体验优化 (TASK-024)

### 1.1 HITL触发点定义

系统在5-Stage工作流中有**2个关键HITL点**：

| HITL点 | 阶段      | 触发时机                | 用户操作          |
| ------ | --------- | ----------------------- | ----------------- |
| HITL-1 | Stage 1后 | Story Blueprint生成完成 | 确认/修改叙事结构 |
| HITL-2 | Stage 3后 | 3个主题选项生成完成     | 选择主题A/B/C     |

### 1.2 HITL-1: Story Blueprint确认

#### 用户界面设计

```
╔══════════════════════════════════════════════════════════════════╗
║                    📋 Story Blueprint 确认                        ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  叙事结构: [Problem-Solution] ⬇️                                  ║
║                                                                  ║
║  ┌────────────────────────────────────────────────────────────┐  ║
║  │  Section 1: 问题陈述 (3页)                                  │  ║
║  │    └─ 市场痛点、用户困境、数据支撑                          │  ║
║  │                                                            │  ║
║  │  Section 2: 解决方案 (4页)                                  │  ║
║  │    └─ 产品介绍、核心功能、技术创新                          │  ║
║  │                                                            │  ║
║  │  Section 3: 价值主张 (3页)                                  │  ║
║  │    └─ 客户收益、ROI分析、成功案例                           │  ║
║  │                                                            │  ║
║  │  Section 4: 市场机会 (3页)                                  │  ║
║  │    └─ 市场规模、增长趋势、竞争分析                          │  ║
║  │                                                            │  ║
║  │  Section 5: 团队与行动 (2页)                                │  ║
║  │    └─ 团队介绍、下一步计划                                  │  ║
║  └────────────────────────────────────────────────────────────┘  ║
║                                                                  ║
║  总页数: 15页 | 预计时长: 20分钟                                  ║
║                                                                  ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           ║
║  │  ✅ 确认继续  │  │  ✏️ 修改结构  │  │  🔄 重新生成  │           ║
║  └──────────────┘  └──────────────┘  └──────────────┘           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

#### 交互选项

**选项1: 确认继续**

```yaml
action: confirm
behavior:
  - 保存Story Blueprint为最终版本
  - 进入Stage 2 Page Planning
  - 记录用户确认时间
```

**选项2: 修改结构**

```yaml
action: modify
interface:
  - 显示Section编辑面板
  - 允许调整Section数量（3-7个）
  - 允许调整每Section页数
  - 允许修改Section标题和描述
  - 总页数实时更新

modification_options:
  - add_section: '添加新章节'
  - remove_section: '删除章节'
  - reorder_sections: '调整顺序'
  - change_page_count: '修改页数分配'
  - change_narrative: '更换叙事结构'
```

**选项3: 重新生成**

```yaml
action: regenerate
behavior:
  - 清除当前Story Blueprint
  - 使用不同叙事结构重新生成
  - 最多允许3次重新生成
  - 显示可选叙事结构列表
```

#### 修改界面详细设计

```
╔══════════════════════════════════════════════════════════════════╗
║                    ✏️ 修改Story Blueprint                         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  叙事结构: [Problem-Solution ▼]                                  ║
║            ├─ Problem-Solution (当前)                            ║
║            ├─ Timeline                                           ║
║            ├─ Feature-Showcase                                   ║
║            ├─ Comparison                                         ║
║            └─ Process                                            ║
║                                                                  ║
║  ─────────────────────────────────────────────────────────────── ║
║                                                                  ║
║  章节列表:                                                        ║
║                                                                  ║
║  ┌─ Section 1 ──────────────────────────────────────────────┐    ║
║  │  标题: [问题陈述________________]                         │    ║
║  │  页数: [3] [+] [-]                                       │    ║
║  │  描述: [市场痛点、用户困境、数据支撑__________]          │    ║
║  │  [↑] [↓] [🗑️]                                            │    ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                  ║
║  ┌─ Section 2 ──────────────────────────────────────────────┐    ║
║  │  标题: [解决方案________________]                         │    ║
║  │  页数: [4] [+] [-]                                       │    ║
║  │  ...                                                     │    ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                  ║
║  [+ 添加章节]                                                     ║
║                                                                  ║
║  ─────────────────────────────────────────────────────────────── ║
║  总页数: 15页 | 目标: 10-20页 ✅                                  ║
║  ─────────────────────────────────────────────────────────────── ║
║                                                                  ║
║  ┌──────────────┐  ┌──────────────┐                             ║
║  │  💾 保存修改  │  │  ❌ 取消     │                             ║
║  └──────────────┘  └──────────────┘                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 1.3 HITL-2: 主题选择

#### 用户界面设计

```
╔══════════════════════════════════════════════════════════════════════════╗
║                         🎨 选择视觉主题                                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  请选择您偏好的视觉主题 (3个选项基于您的内容自动生成):                      ║
║                                                                          ║
║  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐    ║
║  │                    │ │                    │ │                    │    ║
║  │   [Theme A 预览]   │ │   [Theme B 预览]   │ │   [Theme C 预览]   │    ║
║  │                    │ │                    │ │                    │    ║
║  │  ██ Professional   │ │  ██ Modern Light   │ │  ██ Corporate Blue │    ║
║  │     Dark           │ │                    │ │                    │    ║
║  │                    │ │                    │ │                    │    ║
║  │  深色背景          │ │  浅色背景          │ │  专业蓝色          │    ║
║  │  高对比度          │ │  清新现代          │ │  企业风格          │    ║
║  │  商务专业          │ │  科技感            │ │  稳重可靠          │    ║
║  │                    │ │                    │ │                    │    ║
║  │     [选择 A]       │ │     [选择 B]       │ │     [选择 C]       │    ║
║  └────────────────────┘ └────────────────────┘ └────────────────────┘    ║
║                                                                          ║
║  ─────────────────────────────────────────────────────────────────────── ║
║                                                                          ║
║  💡 提示: 选择主题后，系统将自动应用到所有页面。                            ║
║          主题包含: 配色方案、字体样式、布局模板                             ║
║                                                                          ║
║  ┌──────────────────────────────────────────────────────────────────┐    ║
║  │  ⏱️ 默认选择: 30秒后自动选择 Theme A                              │    ║
║  └──────────────────────────────────────────────────────────────────┘    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

#### 主题预览卡片详细设计

```yaml
theme_preview_card:
  thumbnail:
    width: 200px
    height: 150px
    content: '封面页缩略图'

  theme_info:
    name: 'Theme A: Professional Dark'
    color_preview:
      - primary: '#1A1A2E'
      - accent: '#0F3460'
      - highlight: '#E94560'
    font_preview:
      heading: 'Noto Sans SC Bold'
      body: 'Noto Sans SC Regular'
    characteristics:
      - '深色背景'
      - '高对比度'
      - '商务专业'

  action_button:
    text: '选择 A'
    style: 'primary_button'
```

#### 主题比较详情弹窗

```
╔══════════════════════════════════════════════════════════════════════════╗
║                      🔍 主题详细比较                                       ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  ┌────────────────┬────────────────┬────────────────┬────────────────┐   ║
║  │    属性        │    Theme A     │    Theme B     │    Theme C     │   ║
║  ├────────────────┼────────────────┼────────────────┼────────────────┤   ║
║  │  风格          │  深色专业      │  浅色现代      │  企业蓝色      │   ║
║  │  主色          │  ██ #1A1A2E    │  ██ #F5F5F5    │  ██ #1E3A5F    │   ║
║  │  强调色        │  ██ #E94560    │  ██ #2196F3    │  ██ #F39C12    │   ║
║  │  对比度        │  ⭐⭐⭐⭐⭐    │  ⭐⭐⭐⭐      │  ⭐⭐⭐⭐      │   ║
║  │  适用场景      │  投资演讲      │  产品发布      │  企业汇报      │   ║
║  │  字体风格      │  现代无衬线    │  清新圆润      │  经典稳重      │   ║
║  └────────────────┴────────────────┴────────────────┴────────────────┘   ║
║                                                                          ║
║  📊 系统推荐: Theme A (基于您的内容类型: pitch_deck)                       ║
║                                                                          ║
║                                          ┌──────────────┐                ║
║                                          │    关闭      │                ║
║                                          └──────────────┘                ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 1.4 HITL历史记录

#### 历史记录界面

```
╔══════════════════════════════════════════════════════════════════╗
║                     📜 HITL决策历史                               ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  会话ID: ppt_session_20251122_143000                             ║
║                                                                  ║
║  ┌─ HITL-1: Story Blueprint确认 ────────────────────────────┐    ║
║  │  时间: 2025-11-22 14:35:22                               │    ║
║  │  操作: 修改结构                                          │    ║
║  │  修改内容:                                               │    ║
║  │    - Section 3 页数: 3 → 4                               │    ║
║  │    - 添加新Section: "团队介绍"                            │    ║
║  │  最终页数: 15 → 17                                       │    ║
║  │                                             [查看详情]    │    ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                  ║
║  ┌─ HITL-2: 主题选择 ───────────────────────────────────────┐    ║
║  │  时间: 2025-11-22 14:52:10                               │    ║
║  │  操作: 选择 Theme B                                      │    ║
║  │  选择原因: 用户手动选择                                  │    ║
║  │  可选项: A (Professional Dark), B (Modern Light), C...   │    ║
║  │                                             [查看详情]    │    ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                  ║
║  ┌──────────────────┐  ┌──────────────────┐                     ║
║  │  🔄 回滚到HITL-1  │  │  📥 导出历史记录  │                     ║
║  └──────────────────┘  └──────────────────┘                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 1.5 快速重试机制

#### 从HITL点重新生成

```yaml
quick_retry:
  from_hitl_1:
    description: '从Story Blueprint阶段重新开始'
    preserves:
      - user_inputs (ppt-design-inputs.yaml)
    regenerates:
      - story_blueprint
      - page_manifest
      - visual_design_spec
      - slide_content_package
      - presentation.pptx
    estimated_time: '60-90分钟'

  from_hitl_2:
    description: '从Visual Design阶段重新开始'
    preserves:
      - user_inputs
      - story_blueprint
      - page_manifest
    regenerates:
      - visual_design_spec
      - slide_content_package
      - presentation.pptx
    estimated_time: '30-45分钟'

  retry_limit: 3
  timeout_per_retry: 120 minutes
```

---

## Part 2: 进度可视化 (TASK-025)

### 2.1 总体进度条

#### 主进度界面

```
╔══════════════════════════════════════════════════════════════════════════╗
║                     🚀 PPT生成进度                                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  ┌────────────────────────────────────────────────────────────────────┐  ║
║  │  Stage 1    Stage 2    Stage 3    Stage 4    Stage 5              │  ║
║  │  [✅]  →   [✅]  →   [🔄]  →   [⏳]  →   [⏳]                     │  ║
║  │  Story     Page      Visual    Content    File                    │  ║
║  │  Design    Planning  Design    Production Generation              │  ║
║  └────────────────────────────────────────────────────────────────────┘  ║
║                                                                          ║
║  ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  45%               ║
║                                                                          ║
║  当前阶段: Stage 3 - Visual Design                                       ║
║  当前任务: 生成主题选项 (2/3)                                             ║
║                                                                          ║
║  ─────────────────────────────────────────────────────────────────────── ║
║                                                                          ║
║  ⏱️ 已用时间: 25分钟 | 预计剩余: 35分钟 | 预计总时长: 60分钟              ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 2.2 Stage详细进度

#### Stage子任务进度

```
╔══════════════════════════════════════════════════════════════════╗
║              Stage 3: Visual Design - 详细进度                    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ┌─ 子任务列表 ─────────────────────────────────────────────┐    ║
║  │                                                          │    ║
║  │  ✅ 3.1 分析Page Manifest                                │    ║
║  │     └─ 识别12种页面类型分布                              │    ║
║  │                                                          │    ║
║  │  ✅ 3.2 生成主题选项A                                    │    ║
║  │     └─ Professional Dark - 完成                          │    ║
║  │                                                          │    ║
║  │  🔄 3.3 生成主题选项B                                    │    ║
║  │     └─ Modern Light - 进行中 (75%)                       │    ║
║  │     ████████████████████░░░░░░░                          │    ║
║  │                                                          │    ║
║  │  ⏳ 3.4 生成主题选项C                                    │    ║
║  │     └─ 待开始                                            │    ║
║  │                                                          │    ║
║  │  ⏳ 3.5 匹配布局模板                                     │    ║
║  │     └─ 待开始 (依赖主题选择)                             │    ║
║  │                                                          │    ║
║  │  ⏳ 3.6 生成Visual Design Spec                           │    ║
║  │     └─ 待开始                                            │    ║
║  │                                                          │    ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                  ║
║  Stage进度: ████████████░░░░░░░░░░░░░░░░░░  40%                  ║
║  预计完成: 还需 12 分钟                                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 2.3 进度数据模型

```yaml
progress_model:
  session_id: 'ppt_session_20251122_143000'
  start_time: '2025-11-22T14:30:00Z'

  overall_progress:
    percentage: 45
    current_stage: 3
    total_stages: 5
    status: 'in_progress'

  stages:
    - stage_id: 1
      name: 'Story Design'
      status: 'completed'
      start_time: '2025-11-22T14:30:00Z'
      end_time: '2025-11-22T14:42:35Z'
      duration_seconds: 755
      hitl_triggered: true
      hitl_wait_seconds: 120

    - stage_id: 2
      name: 'Page Planning'
      status: 'completed'
      start_time: '2025-11-22T14:44:35Z'
      end_time: '2025-11-22T14:55:10Z'
      duration_seconds: 635

    - stage_id: 3
      name: 'Visual Design'
      status: 'in_progress'
      start_time: '2025-11-22T14:55:10Z'
      current_task: '3.3 生成主题选项B'
      task_progress: 75
      subtasks:
        - id: '3.1'
          name: '分析Page Manifest'
          status: 'completed'
        - id: '3.2'
          name: '生成主题选项A'
          status: 'completed'
        - id: '3.3'
          name: '生成主题选项B'
          status: 'in_progress'
          progress: 75
        - id: '3.4'
          name: '生成主题选项C'
          status: 'pending'
        - id: '3.5'
          name: '匹配布局模板'
          status: 'pending'
        - id: '3.6'
          name: '生成Visual Design Spec'
          status: 'pending'

    - stage_id: 4
      name: 'Content Production'
      status: 'pending'

    - stage_id: 5
      name: 'File Generation'
      status: 'pending'

  time_tracking:
    elapsed_seconds: 1500 # 25分钟
    estimated_remaining_seconds: 2100 # 35分钟
    estimated_total_seconds: 3600 # 60分钟
```

### 2.4 时间估算算法

```python
def estimate_remaining_time(progress_data, historical_data=None):
    """
    估算剩余时间

    基于:
    1. 当前Stage的历史平均耗时
    2. 已完成Stage的实际耗时
    3. HITL等待时间预估
    """

    # 基准耗时 (秒)
    baseline_duration = {
        1: 900,   # Stage 1: 15分钟
        2: 900,   # Stage 2: 15分钟
        3: 1200,  # Stage 3: 20分钟
        4: 1800,  # Stage 4: 30分钟
        5: 600    # Stage 5: 10分钟
    }

    current_stage = progress_data['overall_progress']['current_stage']
    completed_stages = [s for s in progress_data['stages'] if s['status'] == 'completed']

    # 计算实际速度因子
    if completed_stages:
        actual_total = sum(s['duration_seconds'] for s in completed_stages)
        baseline_total = sum(baseline_duration[s['stage_id']] for s in completed_stages)
        speed_factor = actual_total / baseline_total
    else:
        speed_factor = 1.0

    # 估算剩余时间
    remaining_stages = [s for s in progress_data['stages'] if s['status'] in ['pending', 'in_progress']]
    remaining_estimate = 0

    for stage in remaining_stages:
        stage_baseline = baseline_duration[stage['stage_id']]

        if stage['status'] == 'in_progress':
            # 当前Stage: 基于子任务进度
            task_progress = stage.get('task_progress', 50)
            remaining_ratio = (100 - task_progress) / 100
            remaining_estimate += stage_baseline * speed_factor * remaining_ratio
        else:
            # 待开始Stage
            remaining_estimate += stage_baseline * speed_factor

    # 添加HITL等待时间预估
    if current_stage < 3:
        remaining_estimate += 180  # HITL-2预估3分钟
    if current_stage == 1:
        remaining_estimate += 180  # HITL-1预估3分钟

    return remaining_estimate
```

### 2.5 错误提示与恢复建议

#### 错误提示界面

```
╔══════════════════════════════════════════════════════════════════╗
║              ⚠️ 生成警告                                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Stage 5: File Generation 遇到问题                               ║
║                                                                  ║
║  ┌─ 问题详情 ───────────────────────────────────────────────┐    ║
║  │                                                          │    ║
║  │  错误类型: Content Overflow                              │    ║
║  │  影响页面: Slide 7, Slide 12                             │    ║
║  │  详细信息: HTML内容超出720pt×405pt边界                    │    ║
║  │                                                          │    ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                  ║
║  🔧 系统正在自动修复...                                          ║
║                                                                  ║
║  修复策略: 减少padding (尝试 1/3)                                 ║
║  ████████████████░░░░░░░░░░░░░░░░░░  45%                         ║
║                                                                  ║
║  ─────────────────────────────────────────────────────────────── ║
║                                                                  ║
║  💡 如果自动修复失败，系统将导出design_export.zip供手动创建。     ║
║                                                                  ║
║  ┌──────────────┐  ┌──────────────┐                             ║
║  │  等待修复    │  │  跳过并导出  │                             ║
║  └──────────────┘  └──────────────┘                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

#### 恢复建议界面

```
╔══════════════════════════════════════════════════════════════════╗
║              🔄 恢复建议                                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Stage 5生成失败，以下是可行的恢复选项:                          ║
║                                                                  ║
║  ┌─ 选项1: 重试生成 (推荐) ────────────────────────────────┐     ║
║  │  • 使用更激进的布局调整                                 │     ║
║  │  • 预计耗时: 5-10分钟                                   │     ║
║  │  • 成功率: 75%                                          │     ║
║  │                                      [🔄 重试]          │     ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                  ║
║  ┌─ 选项2: 导出设计文档 ───────────────────────────────────┐     ║
║  │  • 导出完整设计配置(design_export.zip)                  │     ║
║  │  • 包含所有Stage输出和使用指南                          │     ║
║  │  • 可手动创建PowerPoint                                 │     ║
║  │                                      [📥 导出]          │     ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                  ║
║  ┌─ 选项3: 修改内容后重试 ─────────────────────────────────┐     ║
║  │  • 返回Stage 4修改超长内容                              │     ║
║  │  • 手动精简Slide 7和12的文本                            │     ║
║  │  • 重新生成PPTX                                         │     ║
║  │                                      [✏️ 修改]          │     ║
║  └──────────────────────────────────────────────────────────┘    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 2.6 实时日志视图

```
╔══════════════════════════════════════════════════════════════════╗
║              📜 实时执行日志                                      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  [14:55:10] Stage 3 - Visual Design 开始                         ║
║  [14:55:12] 分析Page Manifest: 15页, 12种页面类型                 ║
║  [14:55:15] 页面类型分布: cover(1), agenda(1), content(8)...     ║
║  [14:55:20] 开始生成主题选项A: Professional Dark                  ║
║  [14:56:45] 主题A生成完成: 8个颜色, 12个字体规格                  ║
║  [14:56:48] 开始生成主题选项B: Modern Light                       ║
║  [14:57:30] 主题B生成中: 配色方案完成, 字体规格进行中...          ║
║  [14:58:15] 主题B生成完成: 8个颜色, 12个字体规格                  ║
║  [14:58:18] 开始生成主题选项C: Corporate Blue                     ║
║  [14:59:00] 主题C生成中...                                        ║
║  ▼                                                               ║
║                                                                  ║
║  ─────────────────────────────────────────────────────────────── ║
║  [🔍 过滤] [📥 导出日志] [🔄 自动滚动: ON]                        ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Part 3: 数据规范

### 3.1 HITL事件日志格式

```yaml
hitl_event:
  event_id: 'hitl_20251122_143522'
  session_id: 'ppt_session_20251122_143000'
  hitl_point: 'HITL-1' # or "HITL-2"
  stage: 1
  timestamp: '2025-11-22T14:35:22Z'

  trigger:
    type: 'stage_completion'
    stage_output: 'story-blueprint.yaml'

  presentation:
    displayed_options:
      - confirm: '确认继续'
      - modify: '修改结构'
      - regenerate: '重新生成'
    default_option: 'confirm'
    timeout_seconds: 300

  user_response:
    action: 'modify'
    response_time_seconds: 45
    modifications:
      - type: 'change_page_count'
        section: 3
        old_value: 3
        new_value: 4
      - type: 'add_section'
        section_name: '团队介绍'
        page_count: 2

  outcome:
    new_total_pages: 17
    approved: true
    next_stage: 2
```

### 3.2 进度更新消息格式

```yaml
progress_update:
  message_type: 'progress_update'
  session_id: 'ppt_session_20251122_143000'
  timestamp: '2025-11-22T14:57:30Z'

  overall:
    percentage: 47
    current_stage: 3
    status: 'in_progress'

  current_stage:
    stage_id: 3
    name: 'Visual Design'
    task: '3.3 生成主题选项B'
    task_progress: 85

  time:
    elapsed_seconds: 1650
    estimated_remaining_seconds: 1950
    estimated_total_seconds: 3600

  message: '正在生成主题选项B的字体规格...'
```

### 3.3 错误事件格式

```yaml
error_event:
  event_type: 'error'
  session_id: 'ppt_session_20251122_143000'
  timestamp: '2025-11-22T15:15:30Z'

  error:
    type: 'ContentOverflowError'
    stage: 5
    task: 'HTML to PPTX Conversion'
    message: 'Slide 7 content overflows by 45pt horizontally'
    affected_items:
      - slide_number: 7
        overflow_horizontal: 45
        overflow_vertical: 0
      - slide_number: 12
        overflow_horizontal: 30
        overflow_vertical: 20

  recovery:
    strategy: 'auto_retry'
    retry_number: 1
    max_retries: 3
    adjustment:
      type: 'padding_reduction'
      value: 0.1

  user_options:
    - action: 'wait_for_retry'
      description: '等待自动修复'
    - action: 'export_fallback'
      description: '跳过并导出设计文档'
    - action: 'return_to_stage_4'
      description: '返回修改内容'
```

---

## Part 4: 实现指南

### 4.1 HITL实现要点

```yaml
hitl_implementation:
  timeout_handling:
    default_timeout: 300 # 5分钟
    warning_at: 240 # 4分钟时提醒
    auto_select: true # 超时自动选择默认选项

  state_persistence:
    save_on_hitl_trigger: true
    save_user_response: true
    enable_rollback: true
    max_rollback_depth: 2 # 最多回滚2个HITL点

  user_interface:
    platform: 'CLI' # 或 "Web", "Desktop"
    accessibility:
      - keyboard_navigation: true
      - screen_reader_support: true
      - high_contrast_mode: true
```

### 4.2 进度可视化实现要点

```yaml
progress_visualization:
  update_frequency:
    overall_progress: 'every_5_seconds'
    stage_progress: 'every_1_second'
    log_messages: 'realtime'

  display_modes:
    - compact: '单行进度条'
    - detailed: 'Stage详细视图'
    - log: '实时日志视图'

  performance:
    buffer_log_messages: true
    max_buffer_size: 1000
    auto_scroll: true
```

---

## 验收标准

### TASK-024 验收标准

- [ ] HITL-1界面可正常显示Story Blueprint
- [ ] 用户可确认、修改或重新生成Story Blueprint
- [ ] HITL-2界面显示3个主题预览
- [ ] 用户可选择主题或查看详细比较
- [ ] HITL历史记录可查看和回滚
- [ ] 超时自动选择功能正常工作
- [ ] 用户满意度调研>80%

### TASK-025 验收标准

- [ ] 总体进度条准确显示当前进度
- [ ] Stage详细进度显示子任务状态
- [ ] 时间估算误差<20%
- [ ] 错误提示清晰，提供恢复建议
- [ ] 实时日志可查看执行详情
- [ ] 用户能清晰了解当前进度

---

**文档版本**: v1.0
**创建日期**: 2025-11-22
**最后更新**: 2025-11-22
