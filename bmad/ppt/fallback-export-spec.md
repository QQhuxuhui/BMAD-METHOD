# Fallback Export机制规范

**版本**: v1.0
**触发条件**: PPTX生成失败或质量验证失败
**最后更新**: 2025-11-22

---

## 概述

Fallback Export是PPT智能体系统的安全网机制。当PowerPoint文件无法成功生成时,系统会导出完整的设计配置包(`design_export.zip`),允许用户手动创建演示文稿或使用其他工具。

**核心原则**:

- **数据完整性**: 导出所有设计决策和内容
- **可读性**: 包含人类可读的Markdown格式
- **可用性**: 提供清晰的使用说明
- **追溯性**: 保留失败原因和日志

---

## 触发条件

Fallback机制在以下情况触发:

1. **PPTX生成失败**
   - html2pptx执行错误
   - Node.js脚本崩溃
   - 依赖缺失

2. **质量验证失败**
   - Level 1: 文件基础验证失败
   - Level 2: 结构完整性损坏
   - Level 4.2: 文件无法打开

3. **重试耗尽**
   - 内容溢出重试3次后仍失败
   - 其他可重试错误达到最大次数

4. **超时**
   - PPTX生成超过5分钟

---

## design_export.zip结构

```
design_export.zip
├── README.md                           # 使用说明和失败信息
├── METADATA.yaml                       # 元数据和生成信息
│
├── 1_inputs/                           # 用户输入
│   └── ppt-design-inputs.yaml
│
├── 2_story_design/                     # Stage 1输出
│   └── story-blueprint.yaml
│
├── 3_page_planning/                    # Stage 2输出
│   └── page-manifest.yaml
│
├── 4_visual_design/                    # Stage 3输出
│   ├── visual-design-spec.yaml
│   ├── color-palette.md                # 可读色板说明
│   └── typography.md                   # 可读字体说明
│
├── 5_content/                          # Stage 4输出
│   ├── slide-content-package/
│   │   ├── manifest.yaml
│   │   ├── slide_01_cover.yaml
│   │   ├── slide_02_agenda.yaml
│   │   └── ...
│   └── slides-content.md               # Markdown格式内容
│
├── 6_assets/                           # 资源文件(如果有)
│   ├── images/
│   └── data/
│
└── logs/                               # 错误日志
    ├── generation-log.txt
    └── error-details.txt
```

---

## 文件内容规范

### README.md

```markdown
# PPT设计导出包

**生成时间**: 2025-11-22 17:30:45
**系统版本**: PPT Agent System v1.0
**状态**: ⚠️ PPTX生成失败,使用Fallback导出

---

## 失败原因

[自动填充]

- 错误类型: Content Overflow
- 失败阶段: Stage 5 - File Generation
- 详细信息: Slide 7 content overflows by 45pt
- 重试次数: 3/3 (已耗尽)

---

## 导出内容

本包包含完整的PPT设计配置和内容,您可以使用这些文件:

1. **手动创建PowerPoint**
   - 参考`4_visual_design/visual-design-spec.yaml`中的主题和布局
   - 使用`5_content/slides-content.md`中的文本内容
   - 按照`4_visual_design/color-palette.md`中的色板配色

2. **使用其他工具**
   - Google Slides: 导入Markdown内容
   - Canva: 使用色板和布局参考
   - 模板工具: 套用设计规范

3. **调试和修复**
   - 检查`logs/error-details.txt`了解失败详情
   - 调整`5_content/slide-content-package/`中超长的文本
   - 重新尝试生成

---

## 目录结构

- `1_inputs/` - 您的原始需求
- `2_story_design/` - 故事结构设计
- `3_page_planning/` - 页面规划清单
- `4_visual_design/` - 视觉设计规范(主题/色板/字体)
- `5_content/` - 所有幻灯片内容
- `6_assets/` - 图片和数据文件(如果有)
- `logs/` - 错误日志和调试信息

---

## 快速开始

### 方案1: 手动创建(推荐新手)

1. 打开PowerPoint/Google Slides
2. 创建空白演示文稿
3. 阅读`5_content/slides-content.md`,复制文本到幻灯片
4. 参考`4_visual_design/color-palette.md`,设置主题颜色
5. 根据`4_visual_design/visual-design-spec.yaml`,调整字体和布局

### 方案2: 使用YAML配置(推荐开发者)

1. 检查`logs/error-details.txt`,了解失败原因
2. 修复问题(如缩短超长文本)
3. 使用File Generator脚本重新生成
4. 或编写自定义转换脚本读取YAML

### 方案3: 转换为其他格式

1. Markdown演示: 使用`5_content/slides-content.md`配合Marp/reveal.js
2. PDF报告: 将Markdown转换为PDF
3. 网页展示: 使用HTML/CSS实现

---

## 设计要点

### 主题色板

查看`4_visual_design/color-palette.md`获取完整色板,主要颜色:

- 主色: #1A1A2E (深蓝黑)
- 强调色: #0F3460, #16213E, #E94560
- 文字色: #FFFFFF (白色,深色背景上)

### 字体规范

查看`4_visual_design/typography.md`获取完整字体规范:

- 标题: Montserrat Bold, 48-64pt
- 正文: Open Sans Regular, 14-18pt
- 中文: 思源黑体 / Noto Sans CJK SC

### 布局原则

- 16:9宽屏比例
- 标题区域: 上方60pt
- 内容边距: 左右各80pt,底部36pt
- 两栏布局: 40%文本 + 60%图表(推荐)

---

## 支持

### 常见问题

**Q: 为什么PPTX生成失败?**
A: 查看`logs/error-details.txt`,最常见原因是内容超长导致布局溢出。

**Q: 如何修复并重新生成?**
A: 编辑`5_content/slide-content-package/`中的YAML文件,缩短text字段,然后重新运行File Generator。

**Q: 可以直接使用这些文件吗?**
A: 是的!Markdown文件可以直接阅读,YAML文件可以用任何文本编辑器打开和编辑。

### 技术支持

- 文档: https://docs.ppt-agent-system.com
- 问题反馈: https://github.com/xxx/issues
- 邮箱: support@example.com

---

## 附录

### 生成参数

- 总页数: 15
- 主题: Professional Dark
- 语言: zh-CN
- 语气: persuasive

### 文件清单

- YAML配置文件: 18个
- Markdown文档: 4个
- 日志文件: 2个
- 总大小: ~500 KB

---

**导出时间**: 2025-11-22 17:30:45
**系统版本**: v1.0
**导出ID**: export_20251122_173045
```

---

### METADATA.yaml

```yaml
export_metadata:
  export_id: export_20251122_173045
  export_timestamp: 2025-11-22T17:30:45Z
  system_version: v1.0
  fallback_reason: pptx_generation_failed

generation_attempt:
  started_at: 2025-11-22T17:25:00Z
  failed_at: 2025-11-22T17:30:45Z
  duration_seconds: 345
  retry_count: 3
  max_retries: 3

failure_details:
  error_type: ContentOverflowError
  failed_stage: Stage 5 - File Generation
  failed_step: HTML to PPTX Conversion
  error_message: 'Slide 7 content overflows by 45pt horizontally'
  affected_slides: [7, 12]

user_inputs:
  purpose: pitch_deck
  audience_primary: investors
  language: zh-CN
  tone_of_voice: persuasive
  total_pages_requested: 15

output_summary:
  story_blueprint_pages: 15
  page_manifest_pages: 15
  visual_theme: Professional Dark
  content_package_slides: 15
  charts_configured: 3
  tables_configured: 1

validation_results:
  stage_1_validated: true
  stage_2_validated: true
  stage_3_validated: true
  stage_4_validated: true
  stage_5_validated: false # Failed

export_contents:
  total_files: 24
  total_size_bytes: 524288 # ~500 KB
  yaml_files: 18
  markdown_files: 4
  log_files: 2

recommendations:
  - Check logs/error-details.txt for specific overflow details
  - Reduce text length in slide 7 and 12
  - Consider splitting slide 7 into two slides
  - Retry generation after fixing content
```

---

### color-palette.md

```markdown
# 主题色板说明

**主题名称**: Professional Dark
**适用场景**: 商务推介, 正式演讲

---

## 主色系统

### 主色 (Primary)

**颜色**: `#1A1A2E`
**RGB**: (26, 26, 46)
**用途**: 深色背景, 主要底色
**对比度**: 与白色文字对比度 = 15.8 (优秀)

### 强调色 (Accent Colors)

1. **深蓝** `#0F3460`
   - RGB: (15, 52, 96)
   - 用途: 图表主色, 重要元素
   - 示例: 柱状图填充色

2. **中蓝** `#16213E`
   - RGB: (22, 33, 62)
   - 用途: 图表次色, 辅助元素
   - 示例: 折线图第二条线

3. **粉红** `#E94560`
   - RGB: (233, 69, 96)
   - 用途: 强调, 警示
   - 示例: 重要数据标注

### 文字色 (Text Colors)

- **主文字**: `#FFFFFF` (白色) - 在深色背景上
- **次文字**: `#AAB7B8` (浅灰) - 脚注, 说明
- **链接**: `#E94560` (粉红) - 可点击元素

---

## 使用指南

### PowerPoint中设置

1. 打开PowerPoint
2. 设计 > 变体 > 颜色 > 自定义颜色
3. 设置以下颜色:
   - 背景1: #1A1A2E
   - 文本1: #FFFFFF
   - 强调1: #0F3460
   - 强调2: #E94560

### 图表配色

**单系列图表**:

- 使用: #0F3460 (所有柱子/点同色)

**多系列图表**:

- 系列1: #0F3460 (深蓝)
- 系列2: #16213E (中蓝)
- 系列3: #E94560 (粉红)
- 系列4: #AAB7B8 (浅灰)

**饼图**:

- 扇区1: #1A1A2E
- 扇区2: #0F3460
- 扇区3: #16213E
- 扇区4: #AAB7B8

---

## 色彩对比度(WCAG AA)

| 组合              | 对比度 | WCAG评级 |
| ----------------- | ------ | -------- |
| #1A1A2E + #FFFFFF | 15.8   | ✅ AAA   |
| #0F3460 + #FFFFFF | 8.6    | ✅ AAA   |
| #E94560 + #1A1A2E | 4.7    | ✅ AA    |

所有文字色彩组合均符合WCAG AA标准。

---

## 色板预览
```

█████ #1A1A2E 主色
█████ #0F3460 强调1
█████ #16213E 强调2
█████ #E94560 强调3
█████ #FFFFFF 文字

```

---

**生成于**: 2025-11-22
**来源**: Visual Design Spec - Stage 3
```

---

### typography.md

```markdown
# 字体规范说明

**主题名称**: Professional Dark
**字体系统**: 中英文混排

---

## 英文字体

### 标题字体

**字体**: Montserrat Bold
**备选**: Arial Black, Helvetica Bold
**特点**: 无衬线, 粗体, 现代感

### 正文字体

**字体**: Open Sans Regular
**备选**: Arial, Helvetica
**特点**: 无衬线, 易读, 中性

---

## 中文字体

### 标题字体

**字体**: 思源黑体 Bold / Noto Sans CJK SC Bold
**备选**: 微软雅黑 Bold, 黑体
**特点**: 无衬线, 粗体, 清晰

### 正文字体

**字体**: 思源黑体 Regular / Noto Sans CJK SC Regular
**备选**: 微软雅黑, 黑体
**特点**: 无衬线, 易读

---

## 字号层级

### H1 - 主标题

- **英文**: 48-64pt
- **中文**: 48-64pt
- **行高**: 1.2
- **颜色**: #FFFFFF
- **粗细**: Bold
- **用途**: 封面标题, 章节标题

### H2 - 副标题

- **英文**: 32-40pt
- **中文**: 32-40pt
- **行高**: 1.3
- **颜色**: #E94560 或 #FFFFFF
- **粗细**: Bold
- **用途**: 页面标题

### H3 - 小标题

- **英文**: 24-28pt
- **中文**: 24-28pt
- **行高**: 1.4
- **颜色**: #FFFFFF
- **粗细**: Bold
- **用途**: 段落标题

### Body - 正文

- **英文**: 14-18pt
- **中文**: 14-18pt
- **行高**: 1.6
- **颜色**: #FFFFFF
- **粗细**: Regular
- **用途**: 正文内容, 列表

### Caption - 脚注

- **英文**: 10-12pt
- **中文**: 10-12pt
- **行高**: 1.4
- **颜色**: #AAB7B8
- **粗细**: Regular
- **用途**: 数据来源, 说明文字

---

## PowerPoint中设置

1. 开始 > 字体 > 替换字体
2. 设置默认字体:
   - 英文: Open Sans
   - 中文: 思源黑体 或 微软雅黑
3. 设置主题字体:
   - 标题字体: Montserrat Bold
   - 正文字体: Open Sans Regular

---

## 最佳实践

### 可读性

- 最小字号: 10pt (脚注)
- 推荐正文: 14-16pt
- 行距: 1.4-1.6倍
- 段落间距: 0.5-1行

### 对比度

- 白色文字 + 深色背景: 优秀
- 粉色文字 + 深色背景: 良好
- 灰色文字: 仅用于次要信息

### 混排

- 中英文混排时字号相同
- 数字使用英文字体
- 标点符号跟随语言

---

**生成于**: 2025-11-22
**来源**: Visual Design Spec - Stage 3
```

---

### slides-content.md

```markdown
# 幻灯片内容

**总页数**: 15
**主题**: Professional Dark
**语言**: zh-CN

---

## Slide 1: cover

### Title

PPT智能体系统产品推介

### Subtitle

AI驱动的演示文稿自动化解决方案

### Author

Your Company Name

---

## Slide 2: agenda

### Title

今日议程

### Body

- 市场痛点与机遇
- 解决方案概述
- 核心功能演示
- 商业模式与定价
- 团队与里程碑

---

## Slide 3: text-heavy

### Title

市场痛点

### Body

传统PPT制作存在以下痛点:

- 耗时长: 平均15页PPT需要4-6小时
- 设计难: 缺乏专业设计能力
- 一致性差: 多人协作时风格不统一
- 重复劳动: 相似内容反复制作

我们的调研显示,78%的知识工作者认为PPT制作是最耗时的工作之一。

### Footnote

数据来源: 2024年企业效率调研报告

---

## Slide 4: data-chart

### Title

85% 自动化率 - 6个月达成

### Insight

我们的AI调度系统减少了70小时/周的人工工作,释放团队专注战略任务。

### Chart: 自动化进展

Type: bar

Data:

- 自动化率(%): [15, 85, 95]

Categories: ["2024前", "2025当前", "2025目标"]

### Footnote

基于12家中小企业客户数据, 2025年1-6月

---

[继续其他幻灯片...]

---

## Slide 15: summary

### Title

感谢聆听

### Body

联系我们:

- 邮箱: contact@example.com
- 网站: www.example.com
- 电话: 400-123-4567

### Call to Action

立即预约演示,开启PPT自动化之旅

---

**生成于**: 2025-11-22
**导出格式**: Fallback Export
```

---

## 生成流程

### Python实现示例

```python
import os
import shutil
import zipfile
import yaml
from datetime import datetime

def create_fallback_export(
    output_path,
    user_inputs,
    story_blueprint,
    page_manifest,
    visual_design_spec,
    slide_content_package,
    failure_details
):
    """
    创建Fallback导出包

    Args:
        output_path: 输出ZIP文件路径
        user_inputs: 用户输入数据
        story_blueprint: Stage 1输出
        page_manifest: Stage 2输出
        visual_design_spec: Stage 3输出
        slide_content_package: Stage 4输出
        failure_details: 失败详情

    Returns:
        str: 导出包路径
    """

    # 创建临时目录
    temp_dir = f"/tmp/design_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(temp_dir, exist_ok=True)

    # 1. 创建README.md
    readme_content = generate_readme(
        failure_details=failure_details,
        total_pages=page_manifest['total_pages'],
        theme_name=visual_design_spec['theme']['name']
    )
    write_file(f"{temp_dir}/README.md", readme_content)

    # 2. 创建METADATA.yaml
    metadata = generate_metadata(
        user_inputs=user_inputs,
        failure_details=failure_details,
        page_manifest=page_manifest,
        visual_design_spec=visual_design_spec
    )
    write_yaml(f"{temp_dir}/METADATA.yaml", metadata)

    # 3. 复制输入文件
    os.makedirs(f"{temp_dir}/1_inputs", exist_ok=True)
    write_yaml(f"{temp_dir}/1_inputs/ppt-design-inputs.yaml", user_inputs)

    # 4. 复制Stage 1输出
    os.makedirs(f"{temp_dir}/2_story_design", exist_ok=True)
    write_yaml(f"{temp_dir}/2_story_design/story-blueprint.yaml", story_blueprint)

    # 5. 复制Stage 2输出
    os.makedirs(f"{temp_dir}/3_page_planning", exist_ok=True)
    write_yaml(f"{temp_dir}/3_page_planning/page-manifest.yaml", page_manifest)

    # 6. 复制Stage 3输出 + 生成可读文档
    os.makedirs(f"{temp_dir}/4_visual_design", exist_ok=True)
    write_yaml(f"{temp_dir}/4_visual_design/visual-design-spec.yaml", visual_design_spec)

    color_palette_md = generate_color_palette_doc(visual_design_spec)
    write_file(f"{temp_dir}/4_visual_design/color-palette.md", color_palette_md)

    typography_md = generate_typography_doc(visual_design_spec)
    write_file(f"{temp_dir}/4_visual_design/typography.md", typography_md)

    # 7. 复制Stage 4输出 + 生成Markdown内容
    os.makedirs(f"{temp_dir}/5_content/slide-content-package", exist_ok=True)

    # 复制所有YAML文件
    shutil.copytree(
        "slide_content_package/",
        f"{temp_dir}/5_content/slide-content-package/",
        dirs_exist_ok=True
    )

    # 生成Markdown格式
    slides_md = generate_markdown_slides(slide_content_package)
    write_file(f"{temp_dir}/5_content/slides-content.md", slides_md)

    # 8. 创建assets目录(如果有图片)
    os.makedirs(f"{temp_dir}/6_assets/images", exist_ok=True)
    os.makedirs(f"{temp_dir}/6_assets/data", exist_ok=True)

    # 9. 复制日志文件
    os.makedirs(f"{temp_dir}/logs", exist_ok=True)

    if os.path.exists("generation.log"):
        shutil.copy("generation.log", f"{temp_dir}/logs/generation-log.txt")

    error_log = generate_error_log(failure_details)
    write_file(f"{temp_dir}/logs/error-details.txt", error_log)

    # 10. 打包为ZIP
    zip_path = output_path or f"design_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    return zip_path
```

---

## 使用场景

### 场景1: 内容溢出无法修复

```python
# File Generator检测到溢出
try:
    generate_pptx(...)
except ContentOverflowError as e:
    # 重试3次
    for retry in range(3):
        adjust_layout()
        try:
            generate_pptx(...)
            break
        except:
            continue

    # 仍失败,触发Fallback
    fallback_path = create_fallback_export(
        output_path="design_export.zip",
        failure_details={
            'error_type': 'ContentOverflowError',
            'error_message': str(e),
            'retry_count': 3
        }
    )

    return {
        'success': False,
        'fallback_export': fallback_path
    }
```

### 场景2: PPTX文件损坏

```python
# 质量验证失败
validation_report = run_quality_validation(pptx_path, ...)

if not validation_report['overall_passed']:
    if validation_report['failed_level'] in ['Level 1.3', 'Level 2.3', 'Level 4.2']:
        # 致命错误,触发Fallback
        fallback_path = create_fallback_export(
            failure_details={
                'error_type': 'CorruptedPPTX',
                'failed_level': validation_report['failed_level']
            }
        )
```

---

## 质量标准

Fallback导出包必须满足:

1. **完整性**: 包含所有5个Stage的输出
2. **可读性**: 至少3个Markdown文档(README, color-palette, slides-content)
3. **可用性**: README提供清晰的使用指南
4. **追溯性**: 包含失败原因和日志
5. **大小**: < 10 MB (通常~500 KB)

---

## 成功指标

- Fallback触发率: < 10% (目标)
- 导出包完整性: 100%
- 用户使用Fallback成功创建PPT: > 80%
- 导出包可读性评分: > 4/5

---

**文档版本**: v1.0
**维护者**: PPT Agent System Team
**最后审核**: 2025-11-22
