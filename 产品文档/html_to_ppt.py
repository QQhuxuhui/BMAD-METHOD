#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将APS产品汇报HTML转换为PPT
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def add_gradient_rectangle(slide, left, top, width, height, color1, color2):
    """添加渐变矩形背景"""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        left, top, width, height
    )
    # 设置填充色（使用第一个颜色作为主色）
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = color1

    # 设置无边框
    shape.line.fill.background()

    return shape

def create_aps_presentation():
    """创建APS产品汇报PPT"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # ==================== 第一页：产品方案 ====================
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])  # 空白布局

    # 设置背景色（浅灰色）
    background = slide1.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(245, 247, 250)

    # 标题
    title_box = slide1.shapes.add_textbox(
        Inches(0.5), Inches(0.3), Inches(15), Inches(0.8)
    )
    title_frame = title_box.text_frame
    title_frame.text = "产品方案"
    p = title_frame.paragraphs[0]
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = RGBColor(102, 126, 234)
    p.alignment = PP_ALIGN.CENTER

    # 副标题
    subtitle_box = slide1.shapes.add_textbox(
        Inches(0.5), Inches(1.0), Inches(15), Inches(0.4)
    )
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.text = "APS调度智能体系统 - 重新定义调度优化的研发方式"
    p = subtitle_frame.paragraphs[0]
    p.font.size = Pt(16)
    p.font.color.rgb = RGBColor(102, 102, 102)
    p.alignment = PP_ALIGN.CENTER

    # 痛点卡片 - 三个横向排列
    pain_points = [
        ("⏰ 周期过长", "3-4周"),
        ("💰 成本高昂", "2万元+"),
        ("📉 知识流失", "70%")
    ]

    card_width = Inches(4.5)
    card_height = Inches(0.8)
    start_x = Inches(1)
    y_pos = Inches(1.6)
    gap = Inches(0.3)

    for i, (title, stat) in enumerate(pain_points):
        x_pos = start_x + i * (card_width + gap)

        # 添加卡片背景
        card = add_gradient_rectangle(
            slide1, x_pos, y_pos, card_width, card_height,
            RGBColor(255, 107, 107), RGBColor(238, 90, 111)
        )

        # 添加文本
        text_box = slide1.shapes.add_textbox(x_pos, y_pos, card_width, card_height)
        tf = text_box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        # 标题
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(255, 255, 255)
        p1.alignment = PP_ALIGN.CENTER

        # 数据
        p2 = tf.add_paragraph()
        p2.text = stat
        p2.font.size = Pt(24)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(255, 215, 0)
        p2.alignment = PP_ALIGN.CENTER

    # 系统架构标题
    arch_title_box = slide1.shapes.add_textbox(
        Inches(1), Inches(2.6), Inches(14), Inches(0.4)
    )
    tf = arch_title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "系统架构：7大专家智能体 + 4大知识库"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = RGBColor(44, 62, 80)
    p.alignment = PP_ALIGN.CENTER

    # 核心能力 - 三个卡片
    capabilities = [
        ("📚 Agent as Doc", "↑75-87%", "智能体=角色+动态加载"),
        ("🔄 Theory-to-Code", "92%", "需求→建模→代码"),
        ("🤝 Human-in-Loop", "P0-P4", "关键决策人机协作")
    ]

    cap_width = Inches(4.5)
    cap_height = Inches(1)
    cap_y = Inches(7.5)

    for i, (title, value, desc) in enumerate(capabilities):
        x_pos = start_x + i * (cap_width + gap)

        # 添加卡片背景
        card = add_gradient_rectangle(
            slide1, x_pos, cap_y, cap_width, cap_height,
            RGBColor(102, 126, 234), RGBColor(118, 75, 162)
        )

        # 添加文本
        text_box = slide1.shapes.add_textbox(x_pos, cap_y, cap_width, cap_height)
        tf = text_box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        # 标题
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(255, 255, 255)
        p1.alignment = PP_ALIGN.CENTER

        # 数值
        p2 = tf.add_paragraph()
        p2.text = value
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(255, 215, 0)
        p2.alignment = PP_ALIGN.CENTER

        # 描述
        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(12)
        p3.font.color.rgb = RGBColor(255, 255, 255)
        p3.alignment = PP_ALIGN.CENTER

    # 中间区域 - 简化的架构和流程说明
    middle_box = slide1.shapes.add_textbox(
        Inches(1), Inches(3.2), Inches(14), Inches(4)
    )
    tf = middle_box.text_frame
    tf.word_wrap = True

    # 系统架构概述
    p = tf.paragraphs[0]
    p.text = "🎯 总指挥：Phase 0-4 全流程编排与专家协调"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(245, 81, 108)
    p.space_after = Pt(10)

    # 6大专家
    experts = [
        "🏭 领域专家(-56% Token) | 🔒 约束专家(-60% Token) | 🎯 目标专家(-67% Token)",
        "⚡ 算法专家(-87% Token) | 💻 编码专家(-65% Token) | ✅ 质量专家(6层门禁)"
    ]
    for expert_line in experts:
        p = tf.add_paragraph()
        p.text = expert_line
        p.font.size = Pt(14)
        p.font.color.rgb = RGBColor(102, 126, 234)
        p.space_after = Pt(8)

    # 四大知识库
    p = tf.add_paragraph()
    p.text = "\n📚 四大知识库体系 - Agent as Doc核心竞争力："
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(26, 95, 63)
    p.space_after = Pt(10)

    knowledge_bases = [
        "• 🏭 领域知识库(10+ 模板)：物流配送、生产调度、人员排班、项目管理",
        "• 🔒 约束知识库(20+ 模板)：时间窗约束、容量约束、空间约束、逻辑约束",
        "• 🎯 目标知识库(15+ 模板)：成本最小化、时间最优、多目标优化、帕累托分析",
        "• ⚡ 算法知识库(13+ 模板)：遗传算法、禁忌搜索、整数规划、启发式算法"
    ]

    for kb in knowledge_bases:
        p = tf.add_paragraph()
        p.text = kb
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(85, 85, 85)
        p.space_after = Pt(6)
        p.level = 0

    # 工作流程
    p = tf.add_paragraph()
    p.text = "\n🔄 工作流程 (70-130分钟端到端)："
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(44, 62, 80)
    p.space_after = Pt(8)

    workflow = [
        "P0: 任务规划(5-8min) → P1: 需求分析(10-15min) → P1.5: 十要素建模(5-15min)",
        "P2: 专家协调(10-48min) → P3: 方案集成(15-20min) → P4: 质量保证(9-12min)"
    ]

    for wf in workflow:
        p = tf.add_paragraph()
        p.text = wf
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(85, 85, 85)
        p.space_after = Pt(5)

    # ==================== 第二页：产品价值 ====================
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])  # 空白布局

    # 设置背景色
    background = slide2.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(245, 247, 250)

    # 标题
    title_box = slide2.shapes.add_textbox(
        Inches(0.5), Inches(0.3), Inches(15), Inches(0.8)
    )
    title_frame = title_box.text_frame
    title_frame.text = "产品价值"
    p = title_frame.paragraphs[0]
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = RGBColor(102, 126, 234)
    p.alignment = PP_ALIGN.CENTER

    # 副标题
    subtitle_box = slide2.shapes.add_textbox(
        Inches(0.5), Inches(1.0), Inches(15), Inches(0.4)
    )
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.text = "让调度优化能力民主化，让每个企业都能拥有专业级解决方案"
    p = subtitle_frame.paragraphs[0]
    p.font.size = Pt(16)
    p.font.color.rgb = RGBColor(102, 102, 102)
    p.alignment = PP_ALIGN.CENTER

    # 核心价值主张
    value_prop_box = slide2.shapes.add_textbox(
        Inches(1), Inches(1.6), Inches(14), Inches(0.7)
    )
    # 添加背景
    value_bg = add_gradient_rectangle(
        slide2, Inches(1), Inches(1.6), Inches(14), Inches(0.7),
        RGBColor(102, 126, 234), RGBColor(118, 75, 162)
    )

    vp_frame = value_prop_box.text_frame
    vp_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = vp_frame.paragraphs[0]
    p.text = "🎯 核心价值主张"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    p2 = vp_frame.add_paragraph()
    p2.text = "85%效率提升 × 94.5%成本降低 × 92%质量保证 = 调度优化的范式革命"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(255, 255, 255)
    p2.alignment = PP_ALIGN.CENTER

    # 四象限价值矩阵
    quadrants = [
        {
            "icon": "⚡",
            "title": "效率革命",
            "subtitle": "从周到小时的跨越",
            "metrics": [("↑85%", "开发效率", "3-4周 → 2小时"), ("↑95%", "专家时间节省", "80h → 2h")]
        },
        {
            "icon": "💰",
            "title": "成本优势",
            "subtitle": "人力成本断崖式下降",
            "metrics": [("↓94.5%", "人力成本", "2万 → 1100元"), ("↓90%", "试错成本", "快速迭代")]
        },
        {
            "icon": "✅",
            "title": "质量保证",
            "subtitle": "6层门禁严控质量",
            "metrics": [("92%", "代码可用率", "业界领先"), ("100%", "可追溯性", "引用完整")]
        },
        {
            "icon": "📚",
            "title": "知识资产",
            "subtitle": "持续积累组织能力",
            "metrics": [("92.5%", "知识复用率", "模板化"), ("↓87%", "学习曲线", "3月 → 2周")]
        }
    ]

    quad_width = Inches(6.8)
    quad_height = Inches(1.8)
    quad_gap = Inches(0.4)
    quad_start_x = Inches(1)
    quad_start_y = Inches(2.5)

    for i, quad in enumerate(quadrants):
        row = i // 2
        col = i % 2
        x_pos = quad_start_x + col * (quad_width + quad_gap)
        y_pos = quad_start_y + row * (quad_height + quad_gap)

        # 添加象限背景
        quad_bg = add_gradient_rectangle(
            slide2, x_pos, y_pos, quad_width, quad_height,
            RGBColor(245, 247, 250), RGBColor(195, 207, 226)
        )

        # 添加内容
        text_box = slide2.shapes.add_textbox(
            x_pos + Inches(0.1), y_pos + Inches(0.1),
            quad_width - Inches(0.2), quad_height - Inches(0.2)
        )
        tf = text_box.text_frame
        tf.word_wrap = True

        # 标题行
        p = tf.paragraphs[0]
        p.text = f"{quad['icon']} {quad['title']}"
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = RGBColor(44, 62, 80)

        # 副标题
        p2 = tf.add_paragraph()
        p2.text = quad['subtitle']
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(127, 140, 141)
        p2.space_after = Pt(8)

        # 指标
        for metric_num, metric_label, metric_detail in quad['metrics']:
            p3 = tf.add_paragraph()
            p3.text = f"{metric_num} {metric_label} ({metric_detail})"
            p3.font.size = Pt(12)
            p3.font.color.rgb = RGBColor(102, 126, 234)
            p3.font.bold = True
            p3.space_after = Pt(3)

    # ROI对比
    roi_y = Inches(6.5)
    roi_box = slide2.shapes.add_textbox(
        Inches(1), roi_y, Inches(14), Inches(0.5)
    )
    tf = roi_box.text_frame
    p = tf.paragraphs[0]
    p.text = "💎 单项目ROI对比"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = RGBColor(211, 84, 0)
    p.alignment = PP_ALIGN.CENTER

    # 传统方式 vs APS系统
    roi_detail_y = roi_y + Inches(0.6)

    # 传统方式
    trad_box = slide2.shapes.add_textbox(
        Inches(1.5), roi_detail_y, Inches(5.5), Inches(0.8)
    )
    trad_bg = add_gradient_rectangle(
        slide2, Inches(1.5), roi_detail_y, Inches(5.5), Inches(0.8),
        RGBColor(255, 236, 210), RGBColor(252, 182, 159)
    )

    tf = trad_box.text_frame
    p = tf.paragraphs[0]
    p.text = "传统方式"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(44, 62, 80)
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "专家成本: 20,000元 | 周期: 3-4周 | 试错: +10,000元"
    p2.font.size = Pt(12)
    p2.font.color.rgb = RGBColor(85, 85, 85)
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf.add_paragraph()
    p3.text = "总成本: ≈ 20,000+元"
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(231, 76, 60)
    p3.alignment = PP_ALIGN.CENTER

    # 箭头
    arrow_box = slide2.shapes.add_textbox(
        Inches(7.2), roi_detail_y + Inches(0.2), Inches(1.6), Inches(0.4)
    )
    tf = arrow_box.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = "→"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(102, 126, 234)
    p.alignment = PP_ALIGN.CENTER

    # APS系统
    aps_box = slide2.shapes.add_textbox(
        Inches(9), roi_detail_y, Inches(5.5), Inches(0.8)
    )
    aps_bg = add_gradient_rectangle(
        slide2, Inches(9), roi_detail_y, Inches(5.5), Inches(0.8),
        RGBColor(255, 236, 210), RGBColor(252, 182, 159)
    )

    tf = aps_box.text_frame
    p = tf.paragraphs[0]
    p.text = "APS系统"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(44, 62, 80)
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "LLM成本: 100元 | 专家审核: 1,000元 | 周期: 2小时"
    p2.font.size = Pt(12)
    p2.font.color.rgb = RGBColor(85, 85, 85)
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf.add_paragraph()
    p3.text = "总成本: ≈ 1,100元"
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(39, 174, 96)
    p3.alignment = PP_ALIGN.CENTER

    # 竞争优势 - 4个卡片
    edge_y = Inches(7.8)
    edge_width = Inches(3.4)
    edge_height = Inches(0.9)
    edge_gap = Inches(0.2)
    edge_start_x = Inches(1)

    edges = [
        ("💡 技术创新", ["Agent as Doc业界首创", "Theory-to-Code引擎"]),
        ("🎓 专业深度", ["7大专家智能体", "100+知识模板"]),
        ("🚀 应用场景", ["物流成本↓15%", "制造周期↓20%"]),
        ("🎯 战略目标", ["6月: 100+用户", "12月: 200+客户"])
    ]

    for i, (title, points) in enumerate(edges):
        x_pos = edge_start_x + i * (edge_width + edge_gap)

        # 添加卡片
        edge_bg = slide2.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            x_pos, edge_y, edge_width, edge_height
        )
        fill = edge_bg.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 255, 255)
        edge_bg.line.color.rgb = RGBColor(102, 126, 234)
        edge_bg.line.width = Pt(2)

        # 添加文本
        text_box = slide2.shapes.add_textbox(
            x_pos + Inches(0.1), edge_y + Inches(0.1),
            edge_width - Inches(0.2), edge_height - Inches(0.2)
        )
        tf = text_box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = RGBColor(44, 62, 80)

        for point in points:
            p2 = tf.add_paragraph()
            p2.text = f"▸ {point}"
            p2.font.size = Pt(10)
            p2.font.color.rgb = RGBColor(85, 85, 85)
            p2.space_after = Pt(2)

    # 保存PPT
    output_path = "/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/产品文档/APS产品汇报.pptx"
    prs.save(output_path)
    print(f"✅ PPT已成功生成: {output_path}")
    return output_path

if __name__ == "__main__":
    create_aps_presentation()
