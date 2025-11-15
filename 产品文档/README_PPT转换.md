# html_to_ppt.py 使用说明

## 📖 脚本简介

`html_to_ppt.py` 是一个将APS产品汇报HTML内容转换为PowerPoint演示文稿的Python脚本。它使用 `python-pptx` 库创建专业的PPT文件。

## 🚀 快速使用

### 基本用法

```bash
# 方法1: 直接运行脚本
cd /usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/产品文档
python3 html_to_ppt.py

# 方法2: 作为可执行文件运行
chmod +x html_to_ppt.py
./html_to_ppt.py
```

**输出**:

- 生成文件: `产品文档/APS产品汇报.pptx`
- 控制台输出: `✅ PPT已成功生成: /usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/产品文档/APS产品汇报.pptx`

## 📋 环境要求

### 必需依赖

```bash
# 安装 python-pptx
pip3 install python-pptx
```

### 验证环境

```bash
# 检查是否已安装
python3 -c "import pptx; print('✅ python-pptx 版本:', pptx.__version__)"
```

## 🎨 自定义修改

### 1️⃣ 修改PPT尺寸

```python
# 在 create_aps_presentation() 函数中
prs = Presentation()

# 16:9 宽屏格式（默认）
prs.slide_width = Inches(16)
prs.slide_height = Inches(9)

# 4:3 标准格式
# prs.slide_width = Inches(10)
# prs.slide_height = Inches(7.5)
```

### 2️⃣ 修改配色方案

脚本中使用的主要颜色：

```python
# 品牌主色
RGBColor(102, 126, 234)  # 紫色 #667eea
RGBColor(118, 75, 162)   # 深紫 #764ba2

# 痛点卡片
RGBColor(255, 107, 107)  # 红色 #ff6b6b

# 知识库/成功色
RGBColor(39, 174, 96)    # 绿色 #27ae60

# 背景色
RGBColor(245, 247, 250)  # 浅灰 #f5f7fa
```

修改示例：

```python
# 在痛点卡片部分 (约第 81 行)
card = add_gradient_rectangle(
    slide1, x_pos, y_pos, card_width, card_height,
    RGBColor(255, 107, 107),  # 改为你想要的颜色
    RGBColor(238, 90, 111)
)
```

### 3️⃣ 修改字体大小

```python
# 主标题
p.font.size = Pt(44)  # 修改为你想要的大小

# 正文
p.font.size = Pt(16)

# 小字
p.font.size = Pt(12)
```

### 4️⃣ 修改输出路径

```python
# 在脚本末尾的 create_aps_presentation() 函数中
output_path = "/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/产品文档/APS产品汇报.pptx"

# 改为自定义路径
output_path = "/path/to/your/custom_name.pptx"
```

### 5️⃣ 修改文本内容

所有文本内容都在脚本中定义，例如：

```python
# 痛点卡片内容 (约第 78 行)
pain_points = [
    ("⏰ 周期过长", "3-4周"),      # 修改这里
    ("💰 成本高昂", "2万元+"),
    ("📉 知识流失", "70%")
]

# 四象限内容 (约第 336 行)
quadrants = [
    {
        "icon": "⚡",
        "title": "效率革命",         # 修改这里
        "subtitle": "从周到小时的跨越",
        "metrics": [...]
    },
    ...
]
```

## 🔧 高级用法

### 创建自定义幻灯片

在 `create_aps_presentation()` 函数末尾添加新幻灯片：

```python
def create_aps_presentation():
    # ... 现有代码 ...

    # 添加第三页
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])

    # 设置背景
    background = slide3.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(245, 247, 250)

    # 添加标题
    title_box = slide3.shapes.add_textbox(
        Inches(0.5), Inches(0.3), Inches(15), Inches(0.8)
    )
    title_frame = title_box.text_frame
    title_frame.text = "第三页标题"
    p = title_frame.paragraphs[0]
    p.font.size = Pt(44)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER

    # ... 添加更多内容 ...

    # 保存
    prs.save(output_path)
```

### 作为模块导入

```python
# 在其他Python脚本中使用
from html_to_ppt import create_aps_presentation

# 生成PPT
ppt_path = create_aps_presentation()
print(f"PPT已生成: {ppt_path}")
```

### 批量生成不同版本

```python
# 创建一个新脚本
import os
from html_to_ppt import create_aps_presentation

# 生成多个版本
versions = ["v1.0", "v2.0", "v3.0"]

for version in versions:
    # 修改输出路径
    output_path = f"/path/to/APS产品汇报_{version}.pptx"
    # 生成PPT
    create_aps_presentation()
    print(f"✅ {version} 已生成")
```

## 📐 常用尺寸参考

### Inches 转换

```python
from pptx.util import Inches

Inches(1)    # 1英寸
Inches(0.5)  # 0.5英寸
Inches(16)   # 16英寸（标准宽屏宽度）
Inches(9)    # 9英寸（标准宽屏高度）
```

### Pt (点) 字体大小参考

```python
Pt(10)  # 小字
Pt(12)  # 正文小
Pt(14)  # 正文
Pt(16)  # 正文大
Pt(18)  # 子标题
Pt(22)  # 小标题
Pt(28)  # 标题
Pt(36)  # 大标题
Pt(44)  # 主标题
```

### 对齐方式

```python
from pptx.enum.text import PP_ALIGN

PP_ALIGN.LEFT     # 左对齐
PP_ALIGN.CENTER   # 居中
PP_ALIGN.RIGHT    # 右对齐
PP_ALIGN.JUSTIFY  # 两端对齐
```

## 🐛 常见问题

### 问题1: 中文显示乱码

**解决方案**: 确保脚本文件使用UTF-8编码

```bash
# 检查文件编码
file -i html_to_ppt.py

# 应该显示: charset=utf-8
```

### 问题2: ModuleNotFoundError: No module named 'pptx'

**解决方案**: 安装依赖

```bash
pip3 install python-pptx
```

### 问题3: 生成的PPT打开后格式不对

**解决方案**:

- 使用较新版本的PowerPoint (2016+)
- 或使用WPS Office
- 或使用Keynote导入

### 问题4: 想要添加图片

**解决方案**:

```python
# 在幻灯片中添加图片
img_path = '/path/to/image.png'
left = Inches(2)
top = Inches(2)
width = Inches(5)

pic = slide.shapes.add_picture(img_path, left, top, width=width)
```

## 📚 python-pptx 文档资源

- 官方文档: https://python-pptx.readthedocs.io/
- GitHub: https://github.com/scanny/python-pptx
- 示例代码: https://python-pptx.readthedocs.io/en/latest/user/quickstart.html

## 💡 使用建议

1. **备份原文件**: 修改前先备份脚本
2. **小步测试**: 每次只修改一个部分，立即测试
3. **版本控制**: 使用git管理不同版本
4. **注释说明**: 修改时添加注释，方便后续维护

## 📝 示例：生成不同配色版本

```python
# 创建一个包装函数
def create_custom_ppt(color_scheme="default"):
    """
    生成自定义配色的PPT

    Args:
        color_scheme: 配色方案 ('default', 'blue', 'green')
    """
    # 根据配色方案设置颜色
    if color_scheme == "blue":
        primary_color = RGBColor(33, 150, 243)
        secondary_color = RGBColor(25, 118, 210)
    elif color_scheme == "green":
        primary_color = RGBColor(76, 175, 80)
        secondary_color = RGBColor(56, 142, 60)
    else:  # default
        primary_color = RGBColor(102, 126, 234)
        secondary_color = RGBColor(118, 75, 162)

    # ... 在脚本中使用这些颜色 ...

    output_path = f"APS产品汇报_{color_scheme}.pptx"
    prs.save(output_path)
    return output_path

# 使用
create_custom_ppt("blue")   # 蓝色版本
create_custom_ppt("green")  # 绿色版本
```

## 🎯 总结

这个脚本是一个功能完整的PPT生成工具，你可以：

- ✅ 直接运行生成标准PPT
- ✅ 修改配色、字体、尺寸
- ✅ 添加新的幻灯片
- ✅ 自定义内容和布局
- ✅ 作为模块在其他项目中使用

如有问题，参考python-pptx官方文档或修改脚本代码。
