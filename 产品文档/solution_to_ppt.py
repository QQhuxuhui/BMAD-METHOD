#!/usr/bin/env python3
"""
将 APS产品方案.html 转换为 PowerPoint 演示文稿

使用方法：
    python solution_to_ppt.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

def hex_to_rgb(hex_color):
    """将十六进制颜色转换为 RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_presentation():
    """创建 PowerPoint 演示文稿"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # 定义配色（现代科技渐变风格）
    colors = {
        'primary_purple': RGBColor(*hex_to_rgb('#667EEA')),
        'secondary_purple': RGBColor(*hex_to_rgb('#764BA2')),
        'pain_red': RGBColor(*hex_to_rgb('#FF6B6B')),
        'pain_orange': RGBColor(*hex_to_rgb('#FF8E53')),
        'orchestrator': RGBColor(*hex_to_rgb('#8B5CF6')),
        'agent_blue': RGBColor(*hex_to_rgb('#4F46E5')),
        'knowledge_green': RGBColor(*hex_to_rgb('#10B981')),
        'output_green': RGBColor(*hex_to_rgb('#10B981')),
        'highlight_yellow': RGBColor(*hex_to_rgb('#FCD34D')),
        'white': RGBColor(255, 255, 255),
        'dark_text': RGBColor(74, 85, 104),
        'light_bg': RGBColor(248, 249, 251),
    }

    # 创建单页幻灯片
    blank_slide_layout = prs.slide_layouts[6]  # 空白布局
    slide = prs.slides.add_slide(blank_slide_layout)

    # 设置背景
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(254, 254, 254)

    # ==================== 标题区 ====================
    # 主标题
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3),
        Inches(15), Inches(0.8)
    )
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    title_p = title_frame.paragraphs[0]
    title_p.text = "产品方案"
    title_p.font.size = Pt(48)
    title_p.font.bold = True
    title_p.font.color.rgb = colors['primary_purple']
    title_p.alignment = PP_ALIGN.CENTER

    # 副标题
    subtitle_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(1.0),
        Inches(15), Inches(0.5)
    )
    subtitle_frame = subtitle_box.text_frame
    subtitle_p = subtitle_frame.paragraphs[0]
    subtitle_p.text = "APS调度智能体系统 - 重新定义调度优化的研发方式"
    subtitle_p.font.size = Pt(18)
    subtitle_p.font.color.rgb = RGBColor(125, 138, 153)
    subtitle_p.alignment = PP_ALIGN.CENTER

    # ==================== 痛点卡片 ====================
    pain_points = [
        {"icon": "⏰", "title": "周期过长", "stat": "3-4周"},
        {"icon": "💰", "title": "成本高昂", "stat": "2万元+"},
        {"icon": "📉", "title": "知识流失", "stat": "70%"}
    ]

    pain_y = Inches(1.7)
    pain_width = Inches(4.5)
    pain_height = Inches(1.2)
    pain_gap = Inches(0.5)
    pain_start_x = Inches(1.0)

    for i, pain in enumerate(pain_points):
        x = pain_start_x + i * (pain_width + pain_gap)

        # 背景框
        pain_box = slide.shapes.add_shape(
            1,  # 矩形
            x, pain_y, pain_width, pain_height
        )
        pain_box.fill.solid()
        pain_box.fill.fore_color.rgb = colors['pain_red']
        pain_box.line.color.rgb = colors['pain_orange']
        pain_box.line.width = Pt(1)

        # 图标
        icon_box = slide.shapes.add_textbox(x, pain_y + Inches(0.1), pain_width, Inches(0.4))
        icon_p = icon_box.text_frame.paragraphs[0]
        icon_p.text = pain['icon']
        icon_p.font.size = Pt(36)
        icon_p.alignment = PP_ALIGN.CENTER

        # 标题
        title_box = slide.shapes.add_textbox(x, pain_y + Inches(0.5), pain_width, Inches(0.3))
        title_p = title_box.text_frame.paragraphs[0]
        title_p.text = pain['title']
        title_p.font.size = Pt(18)
        title_p.font.color.rgb = colors['white']
        title_p.alignment = PP_ALIGN.CENTER

        # 数据
        stat_box = slide.shapes.add_textbox(x, pain_y + Inches(0.8), pain_width, Inches(0.35))
        stat_p = stat_box.text_frame.paragraphs[0]
        stat_p.text = pain['stat']
        stat_p.font.size = Pt(28)
        stat_p.font.bold = True
        stat_p.font.color.rgb = RGBColor(255, 229, 229)
        stat_p.alignment = PP_ALIGN.CENTER

    # ==================== 系统架构区 ====================
    arch_y = Inches(3.1)
    arch_height = Inches(2.3)

    # 标题
    arch_title_box = slide.shapes.add_textbox(
        Inches(0.5), arch_y,
        Inches(15), Inches(0.4)
    )
    arch_title_p = arch_title_box.text_frame.paragraphs[0]
    arch_title_p.text = "系统架构：7大专家智能体 + 4大知识库"
    arch_title_p.font.size = Pt(22)
    arch_title_p.font.bold = True
    arch_title_p.font.color.rgb = colors['dark_text']
    arch_title_p.alignment = PP_ALIGN.CENTER

    # 架构流程布局
    arch_content_y = arch_y + Inches(0.5)

    # 输入列
    input_x = Inches(0.8)
    input_width = Inches(2.0)

    # 输入框1
    input1 = slide.shapes.add_shape(1, input_x, arch_content_y, input_width, Inches(0.6))
    input1.fill.solid()
    input1.fill.fore_color.rgb = colors['white']
    input1.line.color.rgb = colors['orchestrator']
    input1.line.width = Pt(2)

    input1_text = input1.text_frame
    input1_p = input1_text.paragraphs[0]
    input1_p.text = "💬 自然语言\n业务需求"
    input1_p.font.size = Pt(12)
    input1_p.alignment = PP_ALIGN.CENTER
    input1_text.vertical_anchor = MSO_ANCHOR.MIDDLE

    # 输入框2
    input2 = slide.shapes.add_shape(1, input_x, arch_content_y + Inches(0.8), input_width, Inches(0.6))
    input2.fill.solid()
    input2.fill.fore_color.rgb = colors['white']
    input2.line.color.rgb = colors['orchestrator']
    input2.line.width = Pt(2)

    input2_text = input2.text_frame
    input2_p = input2_text.paragraphs[0]
    input2_p.text = "🤝 人机协作\nP0-P4交互"
    input2_p.font.size = Pt(12)
    input2_p.alignment = PP_ALIGN.CENTER
    input2_text.vertical_anchor = MSO_ANCHOR.MIDDLE

    # 核心系统（中间）
    core_x = Inches(3.5)
    core_width = Inches(9.0)

    # 总指挥
    orch_box = slide.shapes.add_shape(1, core_x, arch_content_y, core_width, Inches(0.5))
    orch_box.fill.solid()
    orch_box.fill.fore_color.rgb = colors['orchestrator']
    orch_box.line.width = Pt(0)

    orch_text = orch_box.text_frame
    orch_p = orch_text.paragraphs[0]
    orch_p.text = "🎯 总指挥 | Phase 0-4编排 | 专家协调"
    orch_p.font.size = Pt(14)
    orch_p.font.bold = True
    orch_p.font.color.rgb = colors['white']
    orch_p.alignment = PP_ALIGN.CENTER
    orch_text.vertical_anchor = MSO_ANCHOR.MIDDLE

    # 6大专家
    agents = [
        "🏭 领域\n-56%",
        "🔒 约束\n-60%",
        "🎯 目标\n-67%",
        "⚡ 算法\n-87%",
        "💻 编码\n-65%",
        "✅ 质量\n6层"
    ]

    agent_width = Inches(1.4)
    agent_height = Inches(0.5)
    agent_gap = Inches(0.08)
    agents_y = arch_content_y + Inches(0.6)

    for i, agent in enumerate(agents):
        agent_x = core_x + i * (agent_width + agent_gap)

        agent_box = slide.shapes.add_shape(1, agent_x, agents_y, agent_width, agent_height)
        agent_box.fill.solid()
        agent_box.fill.fore_color.rgb = colors['agent_blue']
        agent_box.line.width = Pt(0)

        agent_text = agent_box.text_frame
        agent_p = agent_text.paragraphs[0]
        agent_p.text = agent
        agent_p.font.size = Pt(9)
        agent_p.font.color.rgb = colors['white']
        agent_p.alignment = PP_ALIGN.CENTER
        agent_text.vertical_anchor = MSO_ANCHOR.MIDDLE

    # 知识库
    kb_y = agents_y + Inches(0.6)
    kb_box = slide.shapes.add_shape(1, core_x, kb_y, core_width, Inches(0.7))
    kb_box.fill.solid()
    kb_box.fill.fore_color.rgb = colors['knowledge_green']
    kb_box.line.width = Pt(0)

    kb_text = kb_box.text_frame
    kb_p = kb_text.paragraphs[0]
    kb_p.text = "📚 四大知识库体系 - Agent as Doc核心\n领域(10+) | 约束(20+) | 目标(15+) | 算法(13+)"
    kb_p.font.size = Pt(13)
    kb_p.font.color.rgb = colors['white']
    kb_p.alignment = PP_ALIGN.CENTER
    kb_text.vertical_anchor = MSO_ANCHOR.MIDDLE

    # 输出列
    output_x = Inches(13.2)
    output_width = Inches(2.0)

    # 输出框1
    output1 = slide.shapes.add_shape(1, output_x, arch_content_y, output_width, Inches(0.6))
    output1.fill.solid()
    output1.fill.fore_color.rgb = colors['white']
    output1.line.color.rgb = colors['output_green']
    output1.line.width = Pt(2)

    output1_text = output1.text_frame
    output1_p = output1_text.paragraphs[0]
    output1_p.text = "💻 可执行代码\n92%可用率"
    output1_p.font.size = Pt(12)
    output1_p.alignment = PP_ALIGN.CENTER
    output1_text.vertical_anchor = MSO_ANCHOR.MIDDLE

    # 输出框2
    output2 = slide.shapes.add_shape(1, output_x, arch_content_y + Inches(0.8), output_width, Inches(0.6))
    output2.fill.solid()
    output2.fill.fore_color.rgb = colors['white']
    output2.line.color.rgb = colors['output_green']
    output2.line.width = Pt(2)

    output2_text = output2.text_frame
    output2_p = output2_text.paragraphs[0]
    output2_p.text = "📊 完整文档\n100%可追溯"
    output2_p.font.size = Pt(12)
    output2_p.alignment = PP_ALIGN.CENTER
    output2_text.vertical_anchor = MSO_ANCHOR.MIDDLE

    # ==================== 工作流程 ====================
    workflow_y = Inches(5.6)

    # 标题
    workflow_title_box = slide.shapes.add_textbox(
        Inches(0.5), workflow_y,
        Inches(15), Inches(0.4)
    )
    workflow_title_p = workflow_title_box.text_frame.paragraphs[0]
    workflow_title_p.text = "工作流程：70-130分钟端到端完成"
    workflow_title_p.font.size = Pt(20)
    workflow_title_p.font.bold = True
    workflow_title_p.font.color.rgb = colors['dark_text']
    workflow_title_p.alignment = PP_ALIGN.CENTER

    # Phase节点
    phases = [
        {"num": "0", "name": "任务规划", "time": "5-8min", "interaction": True},
        {"num": "1", "name": "需求分析", "time": "10-15min", "interaction": True},
        {"num": "1.5", "name": "十要素建模", "time": "5-15min", "interaction": True},
        {"num": "2", "name": "专家协调", "time": "10-48min", "interaction": False},
        {"num": "3", "name": "方案集成", "time": "15-20min", "interaction": True},
        {"num": "4", "name": "质量保证", "time": "9-12min", "interaction": False},
    ]

    phase_y = workflow_y + Inches(0.5)
    phase_width = Inches(2.2)
    phase_gap = Inches(0.2)
    phase_start_x = Inches(1.2)

    for i, phase in enumerate(phases):
        x = phase_start_x + i * (phase_width + phase_gap)

        # Phase圆圈
        circle = slide.shapes.add_shape(
            3,  # 椭圆
            x + Inches(0.7), phase_y,
            Inches(0.8), Inches(0.8)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = colors['agent_blue']
        circle.line.width = Pt(0)

        # Phase数字
        circle_text = circle.text_frame
        circle_p = circle_text.paragraphs[0]
        circle_p.text = phase['num']
        circle_p.font.size = Pt(22)
        circle_p.font.bold = True
        circle_p.font.color.rgb = colors['white']
        circle_p.alignment = PP_ALIGN.CENTER
        circle_text.vertical_anchor = MSO_ANCHOR.MIDDLE

        # 交互标记
        if phase['interaction']:
            badge = slide.shapes.add_textbox(
                x + Inches(1.3), phase_y - Inches(0.15),
                Inches(0.35), Inches(0.35)
            )
            badge_p = badge.text_frame.paragraphs[0]
            badge_p.text = "P0"
            badge_p.font.size = Pt(9)
            badge_p.font.bold = True
            badge_p.font.color.rgb = colors['white']
            badge_p.alignment = PP_ALIGN.CENTER

            badge_shape = slide.shapes.add_shape(
                3,  # 椭圆
                x + Inches(1.3), phase_y - Inches(0.15),
                Inches(0.35), Inches(0.35)
            )
            badge_shape.fill.solid()
            badge_shape.fill.fore_color.rgb = colors['pain_red']
            badge_shape.line.width = Pt(0)
            # 移到后面
            slide.shapes._spTree.remove(badge_shape._element)
            slide.shapes._spTree.insert(len(slide.shapes._spTree) - 1, badge_shape._element)

        # Phase名称
        name_box = slide.shapes.add_textbox(x, phase_y + Inches(0.9), phase_width, Inches(0.3))
        name_p = name_box.text_frame.paragraphs[0]
        name_p.text = phase['name']
        name_p.font.size = Pt(12)
        name_p.font.bold = True
        name_p.font.color.rgb = colors['dark_text']
        name_p.alignment = PP_ALIGN.CENTER

        # 时间
        time_box = slide.shapes.add_textbox(x, phase_y + Inches(1.2), phase_width, Inches(0.25))
        time_p = time_box.text_frame.paragraphs[0]
        time_p.text = phase['time']
        time_p.font.size = Pt(10)
        time_p.font.color.rgb = colors['pain_red']
        time_p.alignment = PP_ALIGN.CENTER

    # ==================== 核心能力 ====================
    cap_y = Inches(7.8)
    capabilities = [
        {"icon": "📚", "title": "Agent as Doc", "value": "↑75-87%", "desc": "智能体=角色+动态加载 | Token效率提升"},
        {"icon": "🔄", "title": "Theory-to-Code", "value": "92%", "desc": "需求→建模→代码 | 全自动生成"},
        {"icon": "🤝", "title": "Human-in-Loop", "value": "P0-P4", "desc": "关键决策人机协作 | 任务偏离↓67%"}
    ]

    cap_width = Inches(4.5)
    cap_height = Inches(1.0)
    cap_gap = Inches(0.5)
    cap_start_x = Inches(1.0)

    for i, cap in enumerate(capabilities):
        x = cap_start_x + i * (cap_width + cap_gap)

        # 背景框
        cap_box = slide.shapes.add_shape(1, x, cap_y, cap_width, cap_height)
        cap_box.fill.solid()
        cap_box.fill.fore_color.rgb = colors['agent_blue']
        cap_box.line.width = Pt(0)

        # 图标
        icon_box = slide.shapes.add_textbox(x, cap_y + Inches(0.05), cap_width, Inches(0.25))
        icon_p = icon_box.text_frame.paragraphs[0]
        icon_p.text = cap['icon']
        icon_p.font.size = Pt(28)
        icon_p.alignment = PP_ALIGN.CENTER

        # 标题
        title_box = slide.shapes.add_textbox(x, cap_y + Inches(0.28), cap_width, Inches(0.2))
        title_p = title_box.text_frame.paragraphs[0]
        title_p.text = cap['title']
        title_p.font.size = Pt(14)
        title_p.font.bold = True
        title_p.font.color.rgb = colors['white']
        title_p.alignment = PP_ALIGN.CENTER

        # 数值
        value_box = slide.shapes.add_textbox(x, cap_y + Inches(0.48), cap_width, Inches(0.22))
        value_p = value_box.text_frame.paragraphs[0]
        value_p.text = cap['value']
        value_p.font.size = Pt(20)
        value_p.font.bold = True
        value_p.font.color.rgb = colors['highlight_yellow']
        value_p.alignment = PP_ALIGN.CENTER

        # 描述
        desc_box = slide.shapes.add_textbox(x + Inches(0.2), cap_y + Inches(0.72), cap_width - Inches(0.4), Inches(0.25))
        desc_p = desc_box.text_frame.paragraphs[0]
        desc_p.text = cap['desc']
        desc_p.font.size = Pt(9)
        desc_p.font.color.rgb = colors['white']
        desc_p.alignment = PP_ALIGN.CENTER

    return prs

def main():
    """主函数"""
    print("🚀 开始生成 APS产品方案 PPT...")

    # 创建演示文稿
    prs = create_presentation()

    # 保存文件
    output_file = "APS产品方案.pptx"
    prs.save(output_file)

    print(f"✅ PPT 已成功生成：{output_file}")
    print(f"📊 幻灯片数量：{len(prs.slides)}")
    print(f"📐 尺寸：16:9 (1600×900px)")

if __name__ == "__main__":
    main()
