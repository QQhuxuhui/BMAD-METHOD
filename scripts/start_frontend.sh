#!/bin/bash

# BMAD Frontend 启动脚本

set -e

echo "🚀 启动BMAD前端开发服务器..."

cd "$(dirname "$0")/../frontend/web"

# 检查node_modules
if [ ! -d "node_modules" ]; then
  echo "📦 安装依赖..."
  npm install
fi

# 启动开发服务器
echo "✅ 启动开发服务器 http://localhost:3000"
npm run dev
