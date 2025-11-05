#!/bin/bash

# BMAD Frontend 构建脚本

set -e

echo "🔨 构建BMAD前端生产版本..."

cd "$(dirname "$0")/../frontend/web"

# 构建
npm run build

echo "✅ 构建完成！输出目录: dist/"
