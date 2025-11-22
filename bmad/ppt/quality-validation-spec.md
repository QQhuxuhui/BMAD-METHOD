# Quality Validation规范

**版本**: v1.0
**适用阶段**: Stage 5 - File Generation
**最后更新**: 2025-11-22

---

## 概述

Quality Validation是File Generator Agent的关键组成部分,负责验证生成的PowerPoint文件的完整性、准确性和可用性。本规范定义了所有验证规则、标准和处理流程。

---

## 验证层级

Quality Validation分为4个层级,按顺序执行:

```
Level 1: 文件基础验证 (File Basics)
    ↓
Level 2: 结构完整性验证 (Structure Integrity)
    ↓
Level 3: 内容准确性验证 (Content Accuracy)
    ↓
Level 4: 视觉质量验证 (Visual Quality)
```

每个层级的验证失败会立即中止后续验证,返回错误信息。

---

## Level 1: 文件基础验证

### 验证项

#### 1.1 文件存在性

**规则**: PPTX文件必须存在且可访问

```python
def validate_file_exists(pptx_path):
    """验证文件存在"""
    if not os.path.exists(pptx_path):
        return ValidationResult(
            passed=False,
            level="Level 1.1",
            error="PPTX file does not exist",
            details=f"Expected path: {pptx_path}"
        )

    return ValidationResult(passed=True, level="Level 1.1")
```

**失败处理**: 触发Fallback机制

---

#### 1.2 文件大小

**规则**:

- 最小大小: > 1 KB (避免空文件)
- 最大大小: < 50 MB (避免过大文件)

```python
def validate_file_size(pptx_path):
    """验证文件大小"""
    file_size = os.path.getsize(pptx_path)

    if file_size < 1024:  # 1 KB
        return ValidationResult(
            passed=False,
            level="Level 1.2",
            error="File too small (likely corrupted)",
            details=f"Size: {file_size} bytes"
        )

    if file_size > 50 * 1024 * 1024:  # 50 MB
        return ValidationResult(
            passed=False,
            level="Level 1.2",
            error="File too large",
            details=f"Size: {file_size / 1024 / 1024:.2f} MB (max: 50 MB)"
        )

    return ValidationResult(
        passed=True,
        level="Level 1.2",
        details=f"Size: {file_size / 1024:.2f} KB"
    )
```

**失败处理**:

- 太小: 触发Fallback
- 太大: 建议压缩图片或减少页数

---

#### 1.3 文件格式

**规则**: 文件必须是有效的ZIP格式(PPTX本质是ZIP)

```python
import zipfile

def validate_file_format(pptx_path):
    """验证PPTX文件格式"""
    try:
        with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
            # 尝试读取ZIP目录
            namelist = zip_ref.namelist()

            if len(namelist) == 0:
                return ValidationResult(
                    passed=False,
                    level="Level 1.3",
                    error="Empty ZIP archive"
                )

        return ValidationResult(passed=True, level="Level 1.3")

    except zipfile.BadZipFile:
        return ValidationResult(
            passed=False,
            level="Level 1.3",
            error="Invalid ZIP format (file corrupted)"
        )
```

**失败处理**: 触发Fallback机制

---

## Level 2: 结构完整性验证

### 验证项

#### 2.1 必需文件存在

**规则**: PPTX必须包含Office Open XML标准要求的文件

```python
def validate_required_files(pptx_path):
    """验证必需文件"""
    required_files = [
        "[Content_Types].xml",
        "ppt/presentation.xml",
        "ppt/slides/_rels/",
        "_rels/.rels"
    ]

    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        namelist = zip_ref.namelist()

        missing_files = []
        for required in required_files:
            if required.endswith('/'):
                # 检查目录
                if not any(f.startswith(required) for f in namelist):
                    missing_files.append(required)
            else:
                # 检查文件
                if required not in namelist:
                    missing_files.append(required)

        if missing_files:
            return ValidationResult(
                passed=False,
                level="Level 2.1",
                error="Missing required files",
                details=f"Missing: {', '.join(missing_files)}"
            )

    return ValidationResult(passed=True, level="Level 2.1")
```

**失败处理**: 触发Fallback机制

---

#### 2.2 幻灯片文件完整

**规则**: ppt/slides/目录必须包含所有幻灯片XML文件

```python
def validate_slide_files(pptx_path, expected_count):
    """验证幻灯片文件"""
    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        namelist = zip_ref.namelist()

        # 查找所有slide*.xml文件
        slide_files = [f for f in namelist if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
        actual_count = len(slide_files)

        if actual_count != expected_count:
            return ValidationResult(
                passed=False,
                level="Level 2.2",
                error="Slide count mismatch",
                details=f"Expected: {expected_count}, Found: {actual_count}"
            )

        # 验证编号连续性
        slide_numbers = []
        for f in slide_files:
            # 提取编号: ppt/slides/slide12.xml → 12
            import re
            match = re.search(r'slide(\d+)\.xml', f)
            if match:
                slide_numbers.append(int(match.group(1)))

        slide_numbers.sort()
        expected_numbers = list(range(1, expected_count + 1))

        if slide_numbers != expected_numbers:
            return ValidationResult(
                passed=False,
                level="Level 2.2",
                error="Slide numbering not continuous",
                details=f"Expected: {expected_numbers}, Found: {slide_numbers}"
            )

    return ValidationResult(
        passed=True,
        level="Level 2.2",
        details=f"All {actual_count} slides present and numbered correctly"
    )
```

**失败处理**: 重试生成,或触发Fallback

---

#### 2.3 XML格式有效性

**规则**: 关键XML文件必须可解析

```python
from defusedxml import ElementTree as ET

def validate_xml_parseable(pptx_path):
    """验证XML文件可解析"""
    critical_xml_files = [
        "[Content_Types].xml",
        "ppt/presentation.xml"
    ]

    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        for xml_file in critical_xml_files:
            try:
                xml_content = zip_ref.read(xml_file)
                ET.fromstring(xml_content)
            except ET.ParseError as e:
                return ValidationResult(
                    passed=False,
                    level="Level 2.3",
                    error=f"XML parse error in {xml_file}",
                    details=str(e)
                )
            except KeyError:
                # 文件不存在(应该被2.1捕获)
                pass

    return ValidationResult(passed=True, level="Level 2.3")
```

**失败处理**: 触发Fallback机制(文件已损坏)

---

## Level 3: 内容准确性验证

### 验证项

#### 3.1 页面数量验证

**规则**: 实际幻灯片数量必须等于manifest中的预期数量

```python
def validate_page_count(pptx_path, manifest):
    """验证页面数量"""
    # 方法1: 使用markitdown提取
    try:
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'markitdown', pptx_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # 统计"## Slide"出现次数
            slide_count = result.stdout.count('## Slide')

            if slide_count != manifest['total_slides']:
                return ValidationResult(
                    passed=False,
                    level="Level 3.1",
                    error="Page count mismatch",
                    details=f"Expected: {manifest['total_slides']}, Found: {slide_count}"
                )

            return ValidationResult(
                passed=True,
                level="Level 3.1",
                details=f"Page count: {slide_count}"
            )

    except Exception as e:
        # Fallback到方法2
        pass

    # 方法2: 统计slide*.xml文件
    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        slide_files = [f for f in zip_ref.namelist()
                      if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
        actual_count = len(slide_files)

        if actual_count != manifest['total_slides']:
            return ValidationResult(
                passed=False,
                level="Level 3.1",
                error="Page count mismatch",
                details=f"Expected: {manifest['total_slides']}, Found: {actual_count}"
            )

        return ValidationResult(
            passed=True,
            level="Level 3.1",
            details=f"Page count: {actual_count}"
        )
```

**失败处理**:

- 页数少: 重新生成缺失页面
- 页数多: 删除多余页面或重新生成

---

#### 3.2 文本内容存在性

**规则**: 每页必须包含预期的文本内容

```python
def validate_text_content(pptx_path, slide_content_package):
    """验证文本内容存在"""
    # 使用markitdown提取文本
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'markitdown', pptx_path],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return ValidationResult(
            passed=False,
            level="Level 3.2",
            error="Cannot extract text from PPTX"
        )

    extracted_text = result.stdout

    # 验证每页的关键文本
    missing_content = []

    for slide_entry in slide_content_package['manifest']['slides']:
        slide_data = load_yaml(f"slide_content_package/{slide_entry['file']}")

        page_num = slide_data['slide']['page_number']

        # 检查每个text_content slot
        for slot_name, slot_content in slide_data.get('text_content', {}).items():
            text = slot_content['text']

            # 检查文本是否存在于提取内容中
            # 允许部分匹配(前50个字符)
            text_sample = text[:50]

            if text_sample not in extracted_text:
                missing_content.append({
                    'page': page_num,
                    'slot': slot_name,
                    'sample': text_sample
                })

    if missing_content:
        return ValidationResult(
            passed=False,
            level="Level 3.2",
            error="Missing text content",
            details=f"Missing content in {len(missing_content)} slots",
            data=missing_content
        )

    return ValidationResult(
        passed=True,
        level="Level 3.2",
        details=f"All text content validated"
    )
```

**失败处理**: 警告(非致命),记录缺失内容

---

#### 3.3 图表存在性

**规则**: 标记为has_chart的页面必须包含图表

```python
def validate_charts_present(pptx_path, slide_content_package):
    """验证图表存在"""
    # 解压PPTX,检查ppt/charts/目录
    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        namelist = zip_ref.namelist()

        # 查找所有图表文件
        chart_files = [f for f in namelist if f.startswith('ppt/charts/chart') and f.endswith('.xml')]
        actual_chart_count = len(chart_files)

    # 计算预期图表数量
    expected_chart_count = sum(
        1 for entry in slide_content_package['manifest']['slides']
        if entry.get('has_chart', False)
    )

    if actual_chart_count < expected_chart_count:
        return ValidationResult(
            passed=False,
            level="Level 3.3",
            error="Missing charts",
            details=f"Expected: {expected_chart_count}, Found: {actual_chart_count}"
        )

    return ValidationResult(
        passed=True,
        level="Level 3.3",
        details=f"Charts validated: {actual_chart_count}"
    )
```

**失败处理**: 警告,建议检查图表配置

---

## Level 4: 视觉质量验证

### 验证项

#### 4.1 缩略图生成

**规则**: 必须能够生成PPTX的缩略图

```python
def validate_thumbnail_generation(pptx_path, output_dir):
    """验证缩略图生成"""
    import subprocess

    try:
        result = subprocess.run([
            'python',
            '/root/.claude/plugins/marketplaces/anthropic-agent-skills/document-skills/pptx/scripts/thumbnail.py',
            pptx_path,
            f"{output_dir}/thumbnails",
            '--cols', '5'
        ], capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return ValidationResult(
                passed=False,
                level="Level 4.1",
                error="Thumbnail generation failed",
                details=result.stderr
            )

        # 检查缩略图文件是否生成
        thumbnail_path = f"{output_dir}/thumbnails.jpg"
        if not os.path.exists(thumbnail_path):
            return ValidationResult(
                passed=False,
                level="Level 4.1",
                error="Thumbnail file not created"
            )

        return ValidationResult(
            passed=True,
            level="Level 4.1",
            details=f"Thumbnail: {thumbnail_path}"
        )

    except subprocess.TimeoutExpired:
        return ValidationResult(
            passed=False,
            level="Level 4.1",
            error="Thumbnail generation timeout"
        )
```

**失败处理**: 警告(非致命),继续其他验证

---

#### 4.2 可打开性验证

**规则**: PPTX文件必须可以被PowerPoint/LibreOffice打开

```python
def validate_openable(pptx_path):
    """验证文件可打开"""
    # 方法: 尝试转换为PDF(如果能转换说明可打开)
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = f"{temp_dir}/test.pdf"

        try:
            result = subprocess.run([
                'soffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', temp_dir,
                pptx_path
            ], capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                return ValidationResult(
                    passed=False,
                    level="Level 4.2",
                    error="Cannot convert to PDF (file may be corrupted)",
                    details=result.stderr
                )

            # 检查PDF是否生成
            pdf_files = [f for f in os.listdir(temp_dir) if f.endswith('.pdf')]

            if len(pdf_files) == 0:
                return ValidationResult(
                    passed=False,
                    level="Level 4.2",
                    error="PDF conversion produced no output"
                )

            return ValidationResult(
                passed=True,
                level="Level 4.2",
                details="File can be opened and converted"
            )

        except subprocess.TimeoutExpired:
            return ValidationResult(
                passed=False,
                level="Level 4.2",
                error="PDF conversion timeout (file may be too large or corrupted)"
            )
```

**失败处理**:

- 失败: 触发Fallback
- 超时: 警告,但不阻止(可能仅是文件大)

---

## 验证结果数据结构

```python
class ValidationResult:
    """验证结果"""
    def __init__(self, passed, level, error=None, details=None, data=None):
        self.passed = passed          # bool: 是否通过
        self.level = level              # str: 验证层级(如"Level 1.1")
        self.error = error              # str: 错误消息(如果failed)
        self.details = details          # str: 详细信息
        self.data = data                # dict: 附加数据
        self.timestamp = datetime.now()

    def to_dict(self):
        return {
            'passed': self.passed,
            'level': self.level,
            'error': self.error,
            'details': self.details,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }
```

---

## 完整验证流程

```python
def run_quality_validation(pptx_path, slide_content_package, output_dir):
    """
    运行完整的质量验证

    Returns:
        dict: {
            'overall_passed': bool,
            'results': [ValidationResult, ...],
            'failed_level': str or None,
            'summary': dict
        }
    """

    results = []

    # Level 1: 文件基础验证
    print("Running Level 1: File Basics...")

    result = validate_file_exists(pptx_path)
    results.append(result)
    if not result.passed:
        return build_validation_report(results, failed_at='Level 1.1')

    result = validate_file_size(pptx_path)
    results.append(result)
    if not result.passed:
        return build_validation_report(results, failed_at='Level 1.2')

    result = validate_file_format(pptx_path)
    results.append(result)
    if not result.passed:
        return build_validation_report(results, failed_at='Level 1.3')

    # Level 2: 结构完整性验证
    print("Running Level 2: Structure Integrity...")

    result = validate_required_files(pptx_path)
    results.append(result)
    if not result.passed:
        return build_validation_report(results, failed_at='Level 2.1')

    manifest = slide_content_package['manifest']

    result = validate_slide_files(pptx_path, manifest['total_slides'])
    results.append(result)
    if not result.passed:
        return build_validation_report(results, failed_at='Level 2.2')

    result = validate_xml_parseable(pptx_path)
    results.append(result)
    if not result.passed:
        return build_validation_report(results, failed_at='Level 2.3')

    # Level 3: 内容准确性验证
    print("Running Level 3: Content Accuracy...")

    result = validate_page_count(pptx_path, manifest)
    results.append(result)
    if not result.passed:
        return build_validation_report(results, failed_at='Level 3.1')

    result = validate_text_content(pptx_path, slide_content_package)
    results.append(result)
    if not result.passed:
        # 文本缺失是警告,不阻止
        print(f"WARNING: {result.error}")

    result = validate_charts_present(pptx_path, slide_content_package)
    results.append(result)
    if not result.passed:
        # 图表缺失是警告,不阻止
        print(f"WARNING: {result.error}")

    # Level 4: 视觉质量验证
    print("Running Level 4: Visual Quality...")

    result = validate_thumbnail_generation(pptx_path, output_dir)
    results.append(result)
    if not result.passed:
        # 缩略图失败是警告,不阻止
        print(f"WARNING: {result.error}")

    result = validate_openable(pptx_path)
    results.append(result)
    if not result.passed:
        return build_validation_report(results, failed_at='Level 4.2')

    # 所有验证通过
    return build_validation_report(results, failed_at=None)


def build_validation_report(results, failed_at):
    """构建验证报告"""
    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)

    return {
        'overall_passed': (failed_at is None),
        'results': [r.to_dict() for r in results],
        'failed_level': failed_at,
        'summary': {
            'total_checks': total_count,
            'passed_checks': passed_count,
            'failed_checks': total_count - passed_count,
            'success_rate': f"{passed_count / total_count * 100:.1f}%"
        }
    }
```

---

## 质量标准阈值

| 指标           | 最低要求   | 推荐目标      |
| -------------- | ---------- | ------------- |
| 文件大小       | > 1 KB     | 10 KB ~ 10 MB |
| 页面完整性     | 100%       | 100%          |
| 文本内容准确性 | ≥ 90%      | 100%          |
| 图表存在性     | ≥ 90%      | 100%          |
| 缩略图生成     | N/A (可选) | 成功          |
| 可打开性       | 100%       | 100%          |

---

## 错误处理策略

### 致命错误(必须修复)

以下验证失败会触发Fallback:

- Level 1.1: 文件不存在
- Level 1.3: 文件格式损坏
- Level 2.1: 缺少必需文件
- Level 2.3: XML损坏
- Level 4.2: 文件无法打开

### 警告错误(记录但不阻止)

以下验证失败记录警告:

- Level 3.2: 文本内容缺失
- Level 3.3: 图表缺失
- Level 4.1: 缩略图生成失败

### 可重试错误

以下验证失败可以重试:

- Level 1.2: 文件太大 → 压缩后重试
- Level 2.2: 页数不匹配 → 重新生成
- Level 3.1: 页数不匹配 → 重新生成

---

## 验证报告格式

### JSON格式输出

```json
{
  "overall_passed": true,
  "failed_level": null,
  "summary": {
    "total_checks": 10,
    "passed_checks": 10,
    "failed_checks": 0,
    "success_rate": "100.0%"
  },
  "results": [
    {
      "passed": true,
      "level": "Level 1.1",
      "error": null,
      "details": null,
      "timestamp": "2025-11-22T17:00:00"
    },
    {
      "passed": true,
      "level": "Level 1.2",
      "error": null,
      "details": "Size: 125.4 KB",
      "timestamp": "2025-11-22T17:00:01"
    }
  ]
}
```

### 控制台输出格式

```
=== Quality Validation Report ===

Level 1: File Basics
  ✓ 1.1 File Exists
  ✓ 1.2 File Size: 125.4 KB
  ✓ 1.3 File Format: Valid ZIP

Level 2: Structure Integrity
  ✓ 2.1 Required Files Present
  ✓ 2.2 Slide Files: 15 slides, numbered correctly
  ✓ 2.3 XML Parseable

Level 3: Content Accuracy
  ✓ 3.1 Page Count: 15
  ⚠ 3.2 Text Content: Missing 1 slot (warning)
  ✓ 3.3 Charts Present: 3 charts

Level 4: Visual Quality
  ✓ 4.1 Thumbnail Generated
  ✓ 4.2 File Openable

=== Summary ===
Total Checks: 10
Passed: 9
Failed: 0
Warnings: 1
Success Rate: 100.0%

Overall: ✅ PASSED
```

---

## 使用示例

```python
# 在File Generator中调用
from quality_validation import run_quality_validation

# 生成PPTX后
pptx_path = f"{work_dir}/output.pptx"

# 运行验证
validation_report = run_quality_validation(
    pptx_path=pptx_path,
    slide_content_package=slide_content_package,
    output_dir=work_dir
)

if validation_report['overall_passed']:
    print("✅ Quality validation passed!")
    # 继续后续步骤
else:
    print(f"❌ Quality validation failed at {validation_report['failed_level']}")
    # 触发Fallback或重试
```

---

## 附录: 快速检查清单

在提交PPTX文件前,使用此清单快速验证:

- [ ] 文件存在且大小>1KB
- [ ] 文件可以用ZIP工具打开
- [ ] 页数正确(与manifest一致)
- [ ] 主要文本内容可见
- [ ] 图表正常显示
- [ ] 可以用PowerPoint/LibreOffice打开
- [ ] 缩略图可以生成(可选)

---

**文档版本**: v1.0
**维护者**: PPT Agent System Team
**最后审核**: 2025-11-22
