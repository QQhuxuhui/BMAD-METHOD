# APS Module - Developer Guide

**BMAD-METHOD v6 Architecture | YAML-based Source-to-Distribution Workflow**

This document explains how to develop and maintain the APS (Advanced Planning & Scheduling) module following the v6 architecture principles with YAML agent format.

---

## 📂 Directory Structure

```
BMAD-METHOD/
├── src/modules/aps/          # SOURCE CODE (你的开发目录)
│   ├── agents/               # 7个专家智能体 YAML 文件 (.agent.yaml)
│   ├── workflows/            # Phase 0-4 工作流定义
│   ├── templates/            # 9大专家知识库
│   │   ├── algorithm-library/
│   │   ├── constraint-library/
│   │   ├── objective-library/
│   │   ├── domain-library/
│   │   ├── orchestrator-library/
│   │   ├── quality-library/
│   │   ├── modeling-library/
│   │   ├── collaboration/
│   │   └── examples/
│   ├── tasks/                # 单一操作任务
│   ├── scripts/              # Python 工具脚本 (开发工具，不分发)
│   │   ├── add_metadata_headers.py
│   │   └── generate_index.py
│   ├── config.yaml           # 模块配置
│   ├── README.md             # 用户文档
│   ├── MIGRATION_GUIDE.md    # 迁移指南
│   ├── DEVELOPMENT.md        # 本文档 (开发者文档)
│   ├── build.js              # 构建脚本
│   └── _module-installer/    # 模块安装器
│
└── bmad/aps/                 # DISTRIBUTION (构建产物，自动生成)
    ├── agents/               # ← 从 src/modules/aps/agents/*.agent.yaml 构建生成
    ├── workflows/            # ← 从 src/modules/aps/workflows/ 复制
    ├── templates/            # ← 从 src/modules/aps/templates/ 复制
    ├── tasks/                # ← 从 src/modules/aps/tasks/ 复制
    ├── config.yaml           # ← 从 src/modules/aps/config.yaml 复制
    ├── README.md             # ← 从 src/modules/aps/README.md 复制
    ├── MIGRATION_GUIDE.md    # ← 从源码复制
    ├── _module-installer/    # ← 从源码复制
    └── .build-meta.json      # 构建元数据 (自动生成)
```

---

## 🚀 Development Workflow

### 1. 修改源码

**所有开发工作都在 `src/modules/aps/` 进行！**

```bash
# 修改智能体
vi src/modules/aps/agents/orchestrator.agent.yaml

# 添加新知识模块
vi src/modules/aps/templates/algorithm-library/heuristic/new-algorithm.md

# 更新配置
vi src/modules/aps/config.yaml

# 运行开发工具（可选）
python3 src/modules/aps/scripts/generate_index.py
```

### 2. 构建分发版本

修改完成后，运行构建脚本将源码同步到 `bmad/aps/`：

```bash
# 方式1: 使用 npm 脚本 (推荐)
npm run build:aps

# 方式2: 直接运行构建脚本
node src/modules/aps/build.js
```

**构建脚本做什么？**
- 清理 `bmad/aps/` 目录（保留备份文件）
- 从 `src/modules/aps/` 复制内容
- 排除开发工具文件（`scripts/`, `build.js`, `DEVELOPMENT.md`）
- 生成构建元数据 (`.build-meta.json`)
- 验证关键文件完整性

### 3. 测试验证

```bash
# 检查构建结果
ls -la bmad/aps/

# 验证文件数量
find src/modules/aps -type f \( -name "*.md" -o -name "*.yaml" \) | wc -l
find bmad/aps -type f \( -name "*.md" -o -name "*.yaml" \) | wc -l

# 查看构建元数据
cat bmad/aps/.build-meta.json
```

### 4. 提交到 Git

```bash
# 提交源码和产物（两者都需要提交）
git add src/modules/aps/
git add bmad/aps/
git commit -m "feat(aps): Your changes description"
```

---

## 🎯 Core Design Principles

在开发 APS 模块时，请遵循以下核心设计理念：

### 1. **Agent as Doc** 理念
- 智能体 = 知识文档化载体
- 专业能力 = 模板化知识模块
- 工作流程 = 知识模块调用机制

### 2. **Sidecar 模式**
- 主智能体轻量（< 5KB）
- 按需加载专家库 (`@专家库/xxx`)
- Token 节省 75-87%

### 3. **Guardrails 强约束**
```yaml
allowed_sources:
  - TenElementModel        # 十要素模型
  - @专家库/*              # 专家知识库
  - @知识模块库/*          # 通用知识模块

requirements:
  - citations_required: true  # 强制引用路径
  - no_hallucination: true    # 禁止虚构
  - cite_everything: true     # 所有输出必须附@引用
```

### 4. **十要素模型 (TenElementModel)**
统一真相源 (Single Source of Truth)：
1. 决策变量
2. 参数
3. 约束
4. 优化目标
5. 算法
6. 时间模型
7. 不确定性
8. 求解配置
9. 输入数据
10. 输出格式

---

## 📝 Common Development Tasks

### 添加新的算法知识模块

```bash
# 1. 创建算法文件
vi src/modules/aps/templates/algorithm-library/heuristic/new-algorithm.md

# 2. 按照模板结构编写
#    - 算法描述
#    - 适用场景
#    - 核心参数
#    - 伪代码
#    - 代码示例
#    - 引用 citation

# 3. 更新配置 (可选)
vi src/modules/aps/config.yaml

# 4. 构建
npm run build:aps

# 5. 测试
# 激活智能体，测试新算法是否能被正确加载和使用
```

### 添加新的专家智能体

```bash
# 1. 在源码创建智能体 YAML 文件
vi src/modules/aps/agents/new-expert.agent.yaml

# 2. 按照 YAML 格式编写 (参考其他智能体)
#    agent:
#      metadata: {id, name, title, icon, module}
#      persona: {role, identity, communication_style, principles}
#      critical_actions: [...]
#      menu: [{trigger, workflow/exec, description}, ...]

# 3. 更新配置
vi src/modules/aps/config.yaml
# 添加专家库路径

# 4. 构建
npm run build:aps

# 5. 更新 installer
vi src/modules/aps/_module-installer/installer.js
# 添加新智能体到安装配置
```

### 修改工作流

```bash
# 1. 编辑工作流源文件
vi src/modules/aps/workflows/phase-2-coordination/workflow.yaml

# 2. 测试工作流
# 通过智能体触发工作流测试

# 3. 构建
npm run build:aps
```

---

## 🛡️ Quality Assurance

### Pre-commit Checklist

在提交代码前，请确认：

- [ ] 所有修改都在 `src/modules/aps/` 中进行
- [ ] 运行了构建脚本 `npm run build:aps`
- [ ] 验证了构建成功（检查输出日志）
- [ ] YAML 语法正确（运行 `yaml-lint` 或测试加载）
- [ ] Markdown 引用路径正确（`@专家库/xxx`）
- [ ] 更新了相关文档（如有必要）
- [ ] 测试了修改的功能

### 验证工具

```bash
# YAML 语法检查
npm run lint

# Markdown 格式化
npm run format:check
npm run format:fix

# 构建验证
npm run build:aps
```

---

## 🔧 Troubleshooting

### 构建失败

**问题**：构建脚本报错
```bash
❌ Build failed: ENOENT: no such file or directory
```

**解决**：
1. 检查源文件是否存在于 `src/modules/aps/`
2. 确认路径大小写正确
3. 查看构建脚本的 `COPY_ITEMS` 配置

### 文件数量不匹配

**问题**：源码和产物文件数量不一致

**解决**：
```bash
# 对比文件列表
diff <(find src/modules/aps -name "*.md" | sort) \
     <(find bmad/aps -name "*.md" | sort)

# 重新构建
npm run build:aps
```

### Python 脚本不在分发版本中

这是**正常的**！

`scripts/` 目录中的 Python 工具（如 `generate_index.py`）是开发工具，不会被复制到 `bmad/aps/`。它们被构建脚本的 `EXCLUDE_PATTERNS` 排除。

---

## 📚 Architecture References

### v6 Architecture Principles

1. **源码与产物分离**
   - 源码：`src/modules/` (开发)
   - 产物：`bmad/` (分发)

2. **构建转换流程**
   - 支持预处理、验证、转换
   - 为未来扩展留空间

3. **版本控制策略**
   - 源码和产物都提交到 git
   - 源码是 Single Source of Truth
   - 产物方便用户直接使用

### Related Modules

参考其他模块的实现：
- **BMM** (BMAD Module Maker) - 使用 YAML → MD 构建转换
- **BMB** (BMAD Builder) - 类似的模块结构
- **Core** - 核心工作流和任务

---

## 🤝 Contributing

### 扩展知识库

1. 准备知识内容（算法、约束、目标等）
2. 按照模板格式编写 Markdown 文件
3. 放置到相应的专家库目录
4. 更新 `config.yaml` 的 `knowledge_modules` 配置
5. 运行 `scripts/generate_index.py` 生成索引（可选）
6. 构建并测试

### 代码审查要点

- 是否遵循 "Agent as Doc" 理念？
- 是否强制引用 (`citations_required`)？
- Token 使用是否高效（Sidecar 模式）？
- 知识模块是否模板化、可复用？
- 文档是否清晰、完整？

---

## 📄 License

继承自 BMAD-METHOD 项目 - MIT License

---

**Last Updated**: 2025-10-21
**Architecture Version**: BMAD-METHOD v6 - YAML Architecture
**Module Version**: APS 1.0.0-alpha

---

## 🔄 v2.0 YAML Architecture Update

**2025-10-21: 架构统一升级**

APS 模块已升级为 YAML 架构，与 BMM/BMB 模块完全一致：

**变更内容**：
- ✅ 智能体源码从 `.md` 转换为 `.agent.yaml`
- ✅ 使用 `YamlXmlBuilder` 进行构建
- ✅ `<activation>` 块自动生成
- ✅ 标准化的 YAML 结构（metadata, persona, critical_actions, menu）

**迁移说明**：
- 原始 MD 文件已备份到 `agents-md-backup/`
- YAML 文件通过逆向转换工具生成
- 功能完全保持，架构更统一

---

**Questions?**

参考 `src/modules/aps/README.md` 用户文档了解模块功能
参考 `bmad/aps/README.md` 分发版本文档了解使用方法
参考其他模块 `src/modules/bmm/agents/*.agent.yaml` 了解 YAML 格式
