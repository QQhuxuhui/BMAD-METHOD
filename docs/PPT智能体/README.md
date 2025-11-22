# PPT智能体系统文档

本目录包含PPT智能体系统的完整文档，提供两种不同的使用模式。

---

## 📚 文档导航

### 1. [PPT-AGENT.md](./PPT-AGENT.md) - 单智能体模式（快速版）

**适合场景**:

- ✅ 公司内部汇报
- ✅ 团队分享、项目总结
- ✅ 快速迭代需求（30-60分钟）
- ✅ 固定设计规范（蓝黄白灰色系）

**核心特点**:

- 1个PPT设计师智能体
- 5-15页演示文���
- 5-8次HITL确认（需求→大纲→布局→内容→审核）
- 30-60分钟完成

**使用方式**: 直接调用PPT设计师智能体，按照5阶段流程互动式创建。

---

### 2. [PPT-SYSTEM-GUIDE.md](./PPT-SYSTEM-GUIDE.md) - 5-Stage系统（专业版）

**适合场景**:

- ✅ 商业路演（投资人演示）
- ✅ 产品发布会
- ✅ 技术汇报、学术报告
- ✅ 需要专业设计和质量保证

**核心特点**:

- 4个核心智能体 + 2个辅助智能体（多智能体协作）
- 10-20页专业演示文稿
- 仅2次HITL确认（故事结构 + 主题选择）
- 90-120分钟完成
- 8个视觉主题可选（Professional Dark, Modern Light, Corporate Blue等）
- 自动CRAP设计原则验证
- Fallback机制（设计文档导出）

**基于**: OpenSpec提案 `create-ppt-agent-system`

**使用方式**:

```bash
bmad-ppt create --input ppt_design_inputs.yaml
```

---

## 🔄 两种模式对比

| ���度            | 单智能体模式         | 5-Stage系统               |
| ---------------- | -------------------- | ------------------------- |
| **文档**         | PPT-AGENT.md         | PPT-SYSTEM-GUIDE.md       |
| **智能体数量**   | 1个                  | 6个（4核心+2辅助）        |
| **适用场景**     | 内部汇报             | 专业演示                  |
| **页面数量**     | 5-15页               | 10-20页                   |
| **生成时长**     | 30-60分钟            | 90-120分钟                |
| **HITL次数**     | 5-8次                | 2次（关键决策点）         |
| **设计灵活性**   | 固定（公司标准色系） | 灵活（8个主题）           |
| **专家库**       | 无                   | 5叙事+12页面+8主题+20布局 |
| **质量验证**     | 人工审核             | 自动CRAP验证+结构检查     |
| **一次性成功率** | ~40%（需多次修改）   | >60%（无需大改）          |
| **Fallback**     | 无                   | design_export.zip         |
| **实现状态**     | ✅ 已实现            | 📋 设计完成（待实现）     |

---

## 🎯 如何选择？

### 使用单智能体模式（PPT-AGENT.md）如果你：

- 🏢 为公司内部会议准备汇报
- ⏱️ 时间紧迫，需要快速交付
- 🎨 接受固定的设计规范（蓝黄白灰）
- 🔄 允许多次人工确认和迭代
- 📄 页面数量在15页以���

### 使用5-Stage系统（PPT-SYSTEM-GUIDE.md）如果你：

- 💼 为外部演示准备专业演示文稿
- 🎯 需要一次性成功，减少后期修改
- 🎨 需要灵活的视觉主题选择
- 🤖 希望最小化人工干预（自动化）
- 📊 需要复杂的页面类型（数据图表、对比分析等）
- ✅ 需要系统化的质量保证

---

## 📖 相关资源

### OpenSpec设计文档（5-Stage系统）

如果你是开发者，想了解5-Stage系统的设计细节或参与开发：

- **提案**: `/openspec/changes/create-ppt-agent-system/proposal.md`
- **能力规格**:
  - `/openspec/changes/create-ppt-agent-system/specs/ppt-story-design/spec.md`
  - `/openspec/changes/create-ppt-agent-system/specs/ppt-page-planning/spec.md`
  - `/openspec/changes/create-ppt-agent-system/specs/ppt-visual-design/spec.md`
  - `/openspec/changes/create-ppt-agent-system/specs/ppt-content-production/spec.md`
  - `/openspec/changes/create-ppt-agent-system/specs/ppt-file-generation/spec.md`
- **实施任务**: `/openspec/changes/create-ppt-agent-system/tasks.md` (153个任务，4周计划)

### PPT设计规范手册

- 位置: `/docs/PPT智能体/PPT设计规范手册.md` (如果存在)
- 内容: 详细的色彩、字体、版式、视觉元素规范

---

## 🚀 快速开始

### 开始使用单智能体模式

1. 阅读 [PPT-AGENT.md](./PPT-AGENT.md)
2. 调用PPT设计师智能体
3. 按照5阶段流程互动式确认
4. 获��presentation.pptx

### 开始使用5-Stage系统（待实现）

1. 阅读 [PPT-SYSTEM-GUIDE.md](./PPT-SYSTEM-GUIDE.md)
2. 准备 `ppt_design_inputs.yaml`（8要素输入）
3. 运行 `bmad-ppt create --input ppt_design_inputs.yaml`
4. 在2个HITL点确认（故事结构 + 主题选择）
5. 获取 presentation.pptx 或 design_export.zip

---

## 📝 版本历史

- **v1.0** (2025-11-22):
  - ✅ 单智能体模式文档（PPT-AGENT.md）
  - ✅ 5-Stage系统设计文档（PPT-SYSTEM-GUIDE.md）
  - ✅ OpenSpec提案和能力规格完成
  - 📋 5-Stage系统实施待开始（4周计划）

---

## 🤝 贡献

欢迎贡献以下内容：

- 📖 使用案例和最佳实践
- 🎨 新的视觉主题（扩展8主题库）
- 📐 新的布局模板（扩展20模板库）
- 📝 叙事结构模板（扩展5叙事库）
- 🐛 Bug修复和改进建议

---

**维护者**: BMAD-PPT团队
**最后更新**: 2025-11-22
