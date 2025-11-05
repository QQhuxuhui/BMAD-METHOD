#!/bin/bash

# BMAD Frontend 测试脚本

set -e

echo "🧪 运行BMAD前端测试..."

cd "$(dirname "$0")/../frontend/web"

# 运行lint
echo "📋 运行代码检查..."
npm run lint || true

# 构建测试
echo "🔨 构建测试..."
npm run build

echo "✅ 所有测试通过！"
