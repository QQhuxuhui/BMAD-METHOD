# BMAD 前端项目

基于 Vue 3 + TypeScript + Ant Design Vue 的企业级前端监控平台。

## 技术栈

- **框架**: Vue 3.5+ (Composition API)
- **语言**: TypeScript 5.9+
- **构建工具**: Vite 7.1+
- **UI组件库**: Ant Design Vue 4.1+
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios
- **工具库**: @vueuse/core, dayjs
- **代码规范**: ESLint + Prettier

## 快速开始

### 前置要求

- Node.js >= 20.x
- npm >= 10.x

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录

## 使用脚本启动

项目根目录提供了便捷脚本：

```bash
# 启动开发服务器
./scripts/start_frontend.sh

# 构建生产版本
./scripts/build_frontend.sh

# 运行测试
./scripts/test_frontend.sh
```

## 参考资源

- [Vue 3 文档](https://cn.vuejs.org/)
- [Vite 文档](https://cn.vitejs.dev/)
- [Ant Design Vue](https://antdv.com/)
