#!/bin/bash
# PPT智能体系统安装脚本
# 版本: v1.0
# 日期: 2025-11-22

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印横幅
print_banner() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              PPT智能体系统 - 安装向导                         ║"
    echo "║                     版本 v1.0                                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# 检查命令是否存在
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 检查Node.js版本
check_nodejs() {
    print_info "检查 Node.js..."

    if ! check_command "node"; then
        print_error "Node.js 未安装"
        print_info "请安装 Node.js 18.0.0 或更高版本"
        print_info "推荐使用 nvm 安装: https://github.com/nvm-sh/nvm"
        return 1
    fi

    # 获取版本号
    NODE_VERSION=$(node -v | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)

    if [ "$NODE_MAJOR" -lt 18 ]; then
        print_error "Node.js 版本过低: v$NODE_VERSION"
        print_info "需要 Node.js 18.0.0 或更高版本"
        return 1
    fi

    print_success "Node.js v$NODE_VERSION ✓"
    return 0
}

# 检查Python版本
check_python() {
    print_info "检查 Python..."

    # 尝试 python3 或 python
    if check_command "python3"; then
        PYTHON_CMD="python3"
    elif check_command "python"; then
        PYTHON_CMD="python"
    else
        print_warning "Python 未安装 (可选依赖)"
        return 0
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_warning "Python 版本较低: $PYTHON_VERSION (推荐 3.10+)"
    else
        print_success "Python $PYTHON_VERSION ✓"
    fi

    return 0
}

# 检查npm
check_npm() {
    print_info "检查 npm..."

    if ! check_command "npm"; then
        print_error "npm 未安装"
        return 1
    fi

    NPM_VERSION=$(npm -v)
    print_success "npm v$NPM_VERSION ✓"
    return 0
}

# 安装Node.js依赖
install_node_dependencies() {
    print_info "安装 Node.js 依赖..."

    # 检查是否已安装
    DEPS_INSTALLED=true

    if ! npm list pptxgenjs &> /dev/null; then
        DEPS_INSTALLED=false
    fi

    if ! npm list playwright &> /dev/null; then
        DEPS_INSTALLED=false
    fi

    if ! npm list sharp &> /dev/null; then
        DEPS_INSTALLED=false
    fi

    if [ "$DEPS_INSTALLED" = true ]; then
        print_success "Node.js 依赖已安装 ✓"
        return 0
    fi

    # 安装依赖
    print_info "正在安装 pptxgenjs, playwright, sharp..."

    npm install pptxgenjs playwright sharp --save

    if [ $? -eq 0 ]; then
        print_success "Node.js 依赖安装完成 ✓"
    else
        print_error "Node.js 依赖安装失败"
        return 1
    fi

    return 0
}

# 验证document-skills:pptx
verify_document_skills() {
    print_info "验证 document-skills:pptx..."

    # 创建测试脚本
    TEST_SCRIPT=$(mktemp /tmp/pptx_test_XXXXXX.js)

    cat > "$TEST_SCRIPT" << 'EOF'
const pptxgen = require('pptxgenjs');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_16x9';
const slide = pptx.addSlide();
slide.addText('Test', { x: 1, y: 1, w: 5, h: 1 });
console.log('pptxgenjs: OK');
EOF

    if node "$TEST_SCRIPT" 2>/dev/null; then
        print_success "document-skills:pptx 可用 ✓"
        rm -f "$TEST_SCRIPT"
        return 0
    else
        print_error "document-skills:pptx 验证失败"
        rm -f "$TEST_SCRIPT"
        return 1
    fi
}

# 检查BMAD框架
check_bmad_framework() {
    print_info "检查 BMAD 框架..."

    # 查找bmad目录
    if [ -d "./bmad" ]; then
        BMAD_DIR="./bmad"
    elif [ -d "../bmad" ]; then
        BMAD_DIR="../bmad"
    else
        print_error "未找到 BMAD 框架目录"
        print_info "请确保在 BMAD-METHOD 项目根目录运行此脚本"
        return 1
    fi

    # 检查ppt模块
    if [ -d "$BMAD_DIR/ppt" ]; then
        print_success "BMAD PPT 模块已存在 ✓"
    else
        print_error "BMAD PPT 模块不存在"
        return 1
    fi

    return 0
}

# 验证专家库
verify_expert_library() {
    print_info "验证专家库..."

    EXPERT_LIB="./bmad/ppt/expert-library"

    if [ ! -d "$EXPERT_LIB" ]; then
        print_error "专家库目录不存在"
        return 1
    fi

    # 检查主题数量
    THEME_COUNT=$(ls -1 "$EXPERT_LIB/visual-design/themes/"*.yaml 2>/dev/null | wc -l)
    if [ "$THEME_COUNT" -ge 8 ]; then
        print_success "视觉主题: $THEME_COUNT 个 ✓"
    else
        print_warning "视觉主题数量不足: $THEME_COUNT (期望 ≥8)"
    fi

    # 检查布局模板数量
    LAYOUT_COUNT=$(ls -1 "$EXPERT_LIB/visual-design/layouts/"*.yaml 2>/dev/null | wc -l)
    if [ "$LAYOUT_COUNT" -ge 20 ]; then
        print_success "布局模板: $LAYOUT_COUNT 个 ✓"
    else
        print_warning "布局模板数量不足: $LAYOUT_COUNT (期望 ≥20)"
    fi

    # 检查叙事结构数量
    NARRATIVE_COUNT=$(ls -1 "$EXPERT_LIB/story-design/narrative-structures/"*.yaml 2>/dev/null | wc -l)
    if [ "$NARRATIVE_COUNT" -ge 5 ]; then
        print_success "叙事结构: $NARRATIVE_COUNT 个 ✓"
    else
        print_warning "叙事结构数量不足: $NARRATIVE_COUNT (期望 ≥5)"
    fi

    return 0
}

# 创建快速开始示例
create_quickstart_example() {
    print_info "创建快速开始示例..."

    EXAMPLE_DIR="./bmad/ppt/examples"
    mkdir -p "$EXAMPLE_DIR"

    # 创建示例输入文件
    cat > "$EXAMPLE_DIR/quickstart-input.yaml" << 'EOF'
# 快速开始示例 - 商务推介PPT
# 使用方法: 将此文件作为PPT生成的输入

purpose: pitch_deck

audience:
  primary: investors
  knowledge_level: business_professional
  pain_points:
    - ROI证明
    - 市场规模验证

message:
  core_points:
    - 市场痛点严重性
    - 解决方案创新性
    - 市场潜力巨大
  key_data:
    - metric: market_size
      value: "100亿美元"
      context: TAM(总体可达市场)

constraints:
  target_pages: 15
  duration_minutes: 20

visual_preference: professional

tone_of_voice: persuasive

language: zh-CN
EOF

    print_success "快速开始示例已创建: $EXAMPLE_DIR/quickstart-input.yaml ✓"
    return 0
}

# 打印安装摘要
print_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                     安装完成                                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    print_success "PPT智能体系统安装成功!"
    echo ""
    echo "快速开始:"
    echo "  1. 查看示例输入文件: bmad/ppt/examples/quickstart-input.yaml"
    echo "  2. 查看用户指南: docs/ppt-agent-system/user-guide.md"
    echo "  3. 查看开发文档: docs/ppt-agent-system/developer-guide.md"
    echo ""
    echo "使用方法:"
    echo "  claude \"请使用PPT智能体系统，基于 quickstart-input.yaml 生成演示文稿\""
    echo ""
}

# 主函数
main() {
    print_banner

    echo "正在检查系统依赖..."
    echo ""

    # 检查依赖
    DEPS_OK=true

    check_nodejs || DEPS_OK=false
    check_npm || DEPS_OK=false
    check_python

    if [ "$DEPS_OK" = false ]; then
        echo ""
        print_error "依赖检查失败，请先安装缺失的依赖"
        exit 1
    fi

    echo ""
    echo "正在安装组件..."
    echo ""

    # 安装依赖
    install_node_dependencies || exit 1

    echo ""
    echo "正在验证安装..."
    echo ""

    # 验证
    verify_document_skills || exit 1
    check_bmad_framework || exit 1
    verify_expert_library

    echo ""
    echo "正在配置..."
    echo ""

    # 配置
    create_quickstart_example

    # 完成
    print_summary
}

# 运行主函数
main "$@"
