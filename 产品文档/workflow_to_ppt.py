#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将APS智能体工作流程HTML转换为PPT
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def add_rounded_rect(slide, left, top, width, height, color_rgb, border_color=None):
    """添加圆角矩形"""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left, top, width, height
    )
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = color_rgb

    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(2)
    else:
        shape.line.fill.background()

    return shape

def add_circle(slide, left, top, diameter, color_rgb):
    """添加圆形"""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        left, top, diameter, diameter
    )
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = color_rgb
    shape.line.fill.background()
    return shape

def create_workflow_presentation():
    """创建工作流程PPT"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # ==================== 创建幻灯片 ====================
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白布局

    # 设置深色背景
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(20, 20, 30)

    # ==================== 标题 ====================
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3), Inches(15), Inches(0.6)
    )
    title_frame = title_box.text_frame
    title_frame.text = "APS智能体团队工作流程"
    p = title_frame.paragraphs[0]
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(102, 126, 234)
    p.alignment = PP_ALIGN.CENTER

    # 副标题
    subtitle_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.85), Inches(15), Inches(0.3)
    )
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.text = "Phase 0-4 端到端协作流程 | 双模式交互 | 状态持久化"
    p = subtitle_frame.paragraphs[0]
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(176, 176, 176)
    p.alignment = PP_ALIGN.CENTER

    # ==================== 流程时间线 ====================
    # 绘制连接线
    timeline_y = Inches(2.2)
    timeline_left = Inches(1.5)
    timeline_right = Inches(14.5)
    timeline_width = timeline_right - timeline_left

    # 渐变线条效果（简化为单色）
    line = slide.shapes.add_connector(
        1,  # 直线连接器
        timeline_left, timeline_y,
        timeline_right, timeline_y
    )
    line.line.color.rgb = RGBColor(102, 126, 234)
    line.line.width = Pt(3)

    # ==================== Phase 定义 ====================
    phases = [
        {
            "number": "P0",
            "name": "任务规划",
            "time": "5-8min",
            "color": RGBColor(156, 39, 176),
            "interaction": "P0",
            "interaction_color": RGBColor(211, 47, 47),
            "actors": ["🎯 总指挥", "👤 用户"],
            "tasks": [
                "接收需求，生成Todo List",
                "估算时间成本",
                "用户确认（执行合同）"
            ],
            "deliverable": "📄 phase_0_state.yaml\nTodo List基线"
        },
        {
            "number": "P1",
            "name": "需求分析",
            "time": "10-15min",
            "color": RGBColor(33, 150, 243),
            "interaction": "P1",
            "interaction_color": RGBColor(255, 152, 0),
            "actors": ["🎯 总指挥"],
            "tasks": [
                "深度语义解析",
                "识别关键信息",
                "置信度评估（<0.7触发澄清）"
            ],
            "deliverable": "📄 phase_1_state.yaml\n需求分析结果"
        },
        {
            "number": "P1.5",
            "name": "十要素建模",
            "time": "5-15min",
            "color": RGBColor(255, 152, 0),
            "interaction": "P0",
            "interaction_color": RGBColor(211, 47, 47),
            "actors": ["🎯 总指挥", "👤 用户"],
            "tasks": [
                "构建TenElementModel",
                "模式A:全部确认 | 模式B:框架确认"
            ],
            "highlight": "🔒 统一真相源 - 后续专家基于此模型工作",
            "deliverable": "📄 phase_1_5_state.yaml\nTenElementModel（关键依赖）",
            "critical": True
        },
        {
            "number": "P2",
            "name": "专家协调",
            "time": "10-48min",
            "color": RGBColor(76, 175, 80),
            "actors": ["🏭 领域", "🔒 约束", "🎯 目标", "⚡ 算法"],
            "tasks": [
                "加载TenElementModel（前置验证）",
                "🔌 MCP读取历史数据",
                "跨专家一致性校验",
                "模式B: 逐个确认"
            ],
            "parallel": [
                "🏭 领域识别 Token↓56%",
                "🔒 约束建模 Token↓60%",
                "🎯 目标优化 Token↓67%",
                "⚡ 算法推荐 Token↓87%"
            ],
            "deliverable": "📄 phase_2_state.yaml\n4份专家报告+一致性验证"
        },
        {
            "number": "P3",
            "name": "方案集成",
            "time": "15-20min",
            "color": RGBColor(244, 67, 54),
            "interaction": "P0",
            "interaction_color": RGBColor(211, 47, 47),
            "actors": ["🎯 总指挥", "💻 编码专家"],
            "tasks": [
                "集成4份专家报告",
                "Theory-to-Code生成Python代码",
                "生成完整文档",
                "用户确认最终方案"
            ],
            "highlight": "💡 92%代码直接可用",
            "deliverable": "📄 phase_3_state.yaml\n代码+文档+方案"
        },
        {
            "number": "P4",
            "name": "质量保证",
            "time": "9-12min",
            "color": RGBColor(0, 188, 212),
            "actors": ["✅ 质量专家"],
            "tasks": [
                "语法检查 + 逻辑验证",
                "一致性检查（TenElementModel对齐）",
                "Guardrails验证（引用完整性）",
                "基准测试 + 质量报告"
            ],
            "deliverable": "✅ 最终交付物\n代码+文档+报告 | 可用率: 92%",
            "success": True
        }
    ]

    # ==================== 绘制Phase节点 ====================
    node_diameter = Inches(0.8)
    node_spacing = timeline_width / (len(phases) - 1)
    node_y = timeline_y - node_diameter / 2

    for i, phase in enumerate(phases):
        # 计算位置
        x_pos = timeline_left + i * node_spacing - node_diameter / 2

        # 绘制圆形节点
        circle = add_circle(slide, x_pos, node_y, node_diameter, phase["color"])

        # 节点文本
        text_box = slide.shapes.add_textbox(
            x_pos, node_y, node_diameter, node_diameter
        )
        tf = text_box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        p1 = tf.paragraphs[0]
        p1.text = phase["number"]
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(255, 255, 255)
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = phase["name"]
        p2.font.size = Pt(8)
        p2.font.color.rgb = RGBColor(255, 255, 255)
        p2.alignment = PP_ALIGN.CENTER

        # 时间标签
        time_box = slide.shapes.add_textbox(
            x_pos - Inches(0.2), node_y - Inches(0.35),
            node_diameter + Inches(0.4), Inches(0.25)
        )
        time_bg = add_rounded_rect(
            slide, x_pos - Inches(0.2), node_y - Inches(0.35),
            node_diameter + Inches(0.4), Inches(0.25),
            RGBColor(0, 0, 0)
        )

        tf = time_box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = phase["time"]
        p.font.size = Pt(8)
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

        # 交互标记
        if "interaction" in phase:
            badge_width = Inches(0.4)
            badge_height = Inches(0.2)
            badge_box = slide.shapes.add_textbox(
                x_pos + node_diameter - badge_width,
                node_y - Inches(0.6),
                badge_width, badge_height
            )
            badge_bg = add_rounded_rect(
                slide,
                x_pos + node_diameter - badge_width,
                node_y - Inches(0.6),
                badge_width, badge_height,
                phase["interaction_color"]
            )

            tf = badge_box.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.text = phase["interaction"]
            p.font.size = Pt(7)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER

    # ==================== Phase详情卡片 ====================
    detail_y = Inches(3.2)
    card_width = Inches(2.1)
    card_height = Inches(3.8)
    card_spacing = (Inches(15) - len(phases) * card_width) / (len(phases) + 1)

    for i, phase in enumerate(phases):
        x_pos = Inches(0.5) + card_spacing + i * (card_width + card_spacing)

        # 卡片背景
        card_bg = add_rounded_rect(
            slide, x_pos, detail_y, card_width, card_height,
            RGBColor(40, 40, 50),
            phase["color"]
        )

        # 卡片内容
        content_box = slide.shapes.add_textbox(
            x_pos + Inches(0.1), detail_y + Inches(0.1),
            card_width - Inches(0.2), card_height - Inches(0.2)
        )
        tf = content_box.text_frame
        tf.word_wrap = True

        # 参与者
        p = tf.paragraphs[0]
        p.text = "参与者:"
        p.font.size = Pt(8)
        p.font.bold = True
        p.font.color.rgb = RGBColor(200, 200, 200)
        p.space_after = Pt(3)

        for actor in phase["actors"]:
            p_actor = tf.add_paragraph()
            p_actor.text = actor
            p_actor.font.size = Pt(7)
            p_actor.font.color.rgb = RGBColor(144, 202, 249)
            p_actor.space_after = Pt(2)

        # 任务
        p_task_title = tf.add_paragraph()
        p_task_title.text = "\n任务:"
        p_task_title.font.size = Pt(8)
        p_task_title.font.bold = True
        p_task_title.font.color.rgb = RGBColor(200, 200, 200)
        p_task_title.space_after = Pt(3)

        for task in phase["tasks"][:3]:  # 限制显示3个任务
            p_task = tf.add_paragraph()
            p_task.text = f"▸ {task}"
            p_task.font.size = Pt(6)
            p_task.font.color.rgb = RGBColor(176, 176, 176)
            p_task.space_after = Pt(2)

        # 并行专家（仅P2）
        if "parallel" in phase:
            p_parallel = tf.add_paragraph()
            p_parallel.text = "\n并行执行:"
            p_parallel.font.size = Pt(7)
            p_parallel.font.bold = True
            p_parallel.font.color.rgb = RGBColor(255, 193, 7)

            for expert in phase["parallel"][:2]:  # 限制显示2个
                p_exp = tf.add_paragraph()
                p_exp.text = f"• {expert}"
                p_exp.font.size = Pt(6)
                p_exp.font.color.rgb = RGBColor(144, 202, 249)
                p_exp.space_after = Pt(2)

        # 高亮信息
        if "highlight" in phase:
            p_hl = tf.add_paragraph()
            p_hl.text = f"\n{phase['highlight']}"
            p_hl.font.size = Pt(6)
            p_hl.font.color.rgb = RGBColor(255, 215, 0)
            p_hl.space_after = Pt(4)

        # 交付物
        p_deliv_title = tf.add_paragraph()
        p_deliv_title.text = "\n交付物:"
        p_deliv_title.font.size = Pt(7)
        p_deliv_title.font.bold = True
        p_deliv_title.font.color.rgb = RGBColor(200, 200, 200)

        p_deliv = tf.add_paragraph()
        p_deliv.text = phase["deliverable"]
        p_deliv.font.size = Pt(6)
        if phase.get("critical"):
            p_deliv.font.color.rgb = RGBColor(231, 76, 60)
        elif phase.get("success"):
            p_deliv.font.color.rgb = RGBColor(76, 175, 80)
        else:
            p_deliv.font.color.rgb = RGBColor(176, 176, 176)

    # ==================== 底部指标 ====================
    metrics_y = Inches(7.3)
    metrics_bg = add_rounded_rect(
        slide, Inches(1), metrics_y, Inches(14), Inches(0.9),
        RGBColor(102, 126, 234)
    )

    metrics = [
        ("70-130min", "端到端总时间"),
        ("7个", "智能体协作"),
        ("4-6次", "人机交互"),
        ("100%", "可追溯性")
    ]

    metric_width = Inches(3.5)
    for i, (value, label) in enumerate(metrics):
        x_pos = Inches(1) + i * metric_width

        metric_box = slide.shapes.add_textbox(
            x_pos, metrics_y + Inches(0.15),
            metric_width, Inches(0.6)
        )
        tf = metric_box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        p1 = tf.paragraphs[0]
        p1.text = value
        p1.font.size = Pt(20)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(255, 255, 255)
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(10)
        p2.font.color.rgb = RGBColor(255, 255, 255)
        p2.alignment = PP_ALIGN.CENTER

    # ==================== 图例 ====================
    legend_y = Inches(8.4)

    legends = [
        ("P0: 强制交互", RGBColor(211, 47, 47)),
        ("P1: 建议澄清", RGBColor(255, 152, 0)),
        ("🔌 MCP: 数据访问", RGBColor(255, 193, 7)),
        ("关键依赖: TenElementModel", RGBColor(231, 76, 60))
    ]

    legend_width = Inches(3.5)
    for i, (text, color) in enumerate(legends):
        x_pos = Inches(1) + i * legend_width

        # 颜色方块
        color_box = add_rounded_rect(
            slide, x_pos, legend_y, Inches(0.2), Inches(0.2),
            color
        )

        # 文本
        legend_text = slide.shapes.add_textbox(
            x_pos + Inches(0.3), legend_y,
            legend_width - Inches(0.3), Inches(0.2)
        )
        tf = legend_text.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(8)
        p.font.color.rgb = RGBColor(200, 200, 200)

    # 底部版本信息
    footer_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(8.7), Inches(15), Inches(0.2)
    )
    tf = footer_box.text_frame
    p = tf.paragraphs[0]
    p.text = "APS调度智能体系统 v4.3 | 工作流程详解"
    p.font.size = Pt(9)
    p.font.color.rgb = RGBColor(153, 153, 153)
    p.alignment = PP_ALIGN.CENTER

    # ==================== 保存PPT ====================
    output_path = "/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/产品文档/APS智能体工作流程.pptx"
    prs.save(output_path)
    print(f"✅ PPT已成功生成: {output_path}")
    return output_path

if __name__ == "__main__":
    create_workflow_presentation()
