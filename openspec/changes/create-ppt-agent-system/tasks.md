# 实施任务清单 (Implementation Tasks)

> **项目**: PPT智能体系统 (5-Stage Architecture)
> **版本**: v1.0
> **开始日期**: 2025-11-22
> **预计完成**: 2025-12-20 (4周)

---

## 总体里程碑

| 里程碑                     | 时间      | 交付物                                     | 状态       |
| -------------------------- | --------- | ------------------------------------------ | ---------- |
| **Week 1**: 基础架构       | Day 1-5   | 数据模型 + 工作流引擎 + Stage 1-2          | ⏳ Pending |
| **Week 2**: 核心阶段       | Day 6-10  | Stage 3-4 实现 + 专家库                    | ⏳ Pending |
| **Week 3**: 文件生成与验证 | Day 11-15 | Stage 5 + document-skills验证 + 端到端测试 | ⏳ Pending |
| **Week 4**: 优化与发布     | Day 16-20 | HITL优化 + 文档 + 发布                     | ⏳ Pending |

---

## Week 1: 基础架构 (Day 1-5)

### Day 1: 项目初始化

**TASK-001**: 创建PPT模块目录结构

- [ ] 创建 `bmad/ppt/` 根目录
- [ ] 创建子目录: `agents/`, `workflows/`, `expert-library/`, `schemas/`, `state/`
- [ ] 创建 `config.yaml` 配置文件
- [ ] 创建 `README.md` 模块说明文档
- **负责人**: 开发者
- **验收标准**: 目录结构符合BMAD模块规范

**TASK-002**: 定义PPTDesignInputs数据模型

- [ ] 创建 `schemas/ppt_design_inputs.yaml`
- [ ] 定义6核心要素Schema: purpose, audience, message, narrative, constraints, visual_preference
- [ ] 实现数据验证逻辑
- [ ] 编写Schema单元测试
- [ ] 创建示例输入文件（3个场景）
- **负责人**: 开发者
- **验收标准**: Schema验证通过率100%，3个示例场景可加载

### Day 2: 工作流引擎

**TASK-003**: 5-Stage工作流引擎

- [ ] 创建 `workflows/ppt_workflow.yaml`（5个Stage定义）
- [ ] 实现Stage状态管理（pending/in_progress/completed/failed）
- [ ] 实现Stage间数据传递接口
- [ ] 实现进度跟踪（Stage 1/5 → Stage 5/5）
- [ ] 实现错误处理与回滚机制
- **负责人**: 开发者
- **验收标准**: 工作流可按顺序执行Stage 1→2→3→4→5

**TASK-004**: HITL机制实现

- [ ] 实现HITL触发点1（Stage 1后，Story Blueprint确认）
- [ ] 实现HITL触发点2（Stage 3后，主题A/B/C选择）
- [ ] 创建用户确认界面模板
- [ ] 实现确认超时处理（默认选项）
- **负责人**: 开发者
- **验收标准**: 2个HITL点可正常触发，用户可确认/修改

### Day 3: Stage 1 - Story Design

**TASK-005**: Story Designer Agent

- [ ] 创建 `agents/story_designer.md`（Agent定义）
- [ ] 实现叙事结构推荐逻辑（5种结构）
- [ ] 实现内容大纲生成（3-5个Section）
- [ ] 实现页面分配算法（10-20页范围）
- [ ] 实现Story Blueprint输出（YAML格式）
- **负责人**: 开发者
- **验收标准**: 能生成符合REQ-STORY-003格式的Story Blueprint

**TASK-006**: Story Designer专家库

- [ ] 创建 `expert-library/story-design/narrative-structures/`（5个叙事结构模板）
- [ ] 创建 `expert-library/story-design/audience-analysis/`（8个受众分析模板）
- [ ] 创建 `expert-library/story-design/content-organization/`（6个组织模式）
- [ ] 实现专家库按需加载机制
- **负责人**: 开发者
- **验收标准**: 专家库模板完整，可按场景加载

### Day 4: Stage 2 - Page Planning

**TASK-007**: Page Planner Agent

- [ ] 创建 `agents/page_planner.md`（Agent定义）
- [ ] 实现页面类型分配逻辑（12种页面类型）
- [ ] 实现信息架构设计（content_slots定义）
- [ ] 实现特殊需求识别（charts, images, diagrams）
- [ ] 实现Page Manifest输出（YAML格式）
- **负责人**: 开发者
- **验收标准**: 能生成符合REQ-PAGE-003格式的Page Manifest

**TASK-008**: Page Planner专家库

- [ ] 创建 `expert-library/page-planning/page-types/`（12个页面类型模板）
- [ ] 创建 `expert-library/page-planning/layout-patterns/`（15个布局模式）
- [ ] 创建信息架构模板（title+bullets, title+chart, etc.）
- [ ] 实现页面类型匹配算法
- **负责人**: 开发者
- **验收标准**: 12种页面类型覆盖>95%常见场景

### Day 5: 中间输出验证

**TASK-009**: Story Blueprint → Page Manifest集成测试

- [ ] 测试Scene 1: Business pitch deck（15页）
- [ ] 测试Scene 2: Product launch（20页）
- [ ] 测试Scene 3: Technical report（10页）
- [ ] 验证输出YAML格式正确性
- [ ] 验证页面数量一致性（Story.total_pages = Manifest.total_pages）
- **负责人**: 测试
- **验收标准**: 3个场景测试通过，输出符合Schema

---

## Week 2: 核心阶段 (Day 6-10)

### Day 6-7: Stage 3 - Visual Design

**TASK-010**: Visual Stylist Agent

- [ ] 创建 `agents/visual_stylist.md`（Agent定义）
- [ ] 实现主题推荐逻辑（生成A/B/C 3个选项）
- [ ] 实现布局模板匹配（20个布局→12个页面类型）
- [ ] 实现设计标准生成（typography, colors, spacing, CRAP）
- [ ] 实现Visual Design Spec输出（YAML格式）
- **负责人**: 开发者
- **验收标准**: 能生成符合REQ-VISUAL-004格式的Visual Design Spec

**TASK-011**: Visual Stylist专家库

- [ ] 创建 `expert-library/visual-design/themes/`（8个视觉主题）
- [ ] 创建 `expert-library/visual-design/layouts/`（20个布局模板）
- [ ] 创建CRAP设计原则验证规则
- [ ] 实现色彩对比度计算（WCAG AA标准）
- [ ] 创建主题A/B/C差异算法（>40%色相/亮度差异）
- **负责人**: 开发者
- **验收标准**: 8个主题视觉上可区分，布局模板覆盖12种页面类型

**TASK-012**: 主题选择HITL集成

- [ ] 实现主题预览生成（A/B/C 3个缩略图）
- [ ] 实现用户选择界面
- [ ] 实现选择结果写回Visual Design Spec（user_selected_theme字段）
- [ ] 实现默认选择（用户未响应时选Theme A）
- **负责人**: 开发者
- **验收标准**: HITL点2正常工作，用户可选择主题

### Day 8-9: Stage 4 - Content Production

**TASK-013**: Content Producer Agent

- [ ] 创建 `agents/content_producer.md`（Agent定义）
- [ ] 实现标题生成（max_chars限制）
- [ ] 实现正文内容生成（符合content_slots定义）
- [ ] 实现图表配置生成（chart_type, data_points）
- [ ] 实现Slide Content Package输出（YAML格式，每页一个文件）
- **负责人**: 开发者
- **验收标准**: 生成15页完整内容，符合字符数限制

**TASK-014**: Copywriter Helper

- [ ] 创建 `agents/helpers/copywriter.md`（辅助Agent）
- [ ] 实现文案精简算法（3-5-15规则：3个要点，每点≤5词，全页≤15词）
- [ ] 实现语气调整（formal/casual/persuasive）
- [ ] 集成到Content Producer调用链
- **负责人**: 开发者
- **验收标准**: 文案简洁度提升>30%，可读性评分>90

**TASK-015**: Chart Specialist Helper

- [ ] 创建 `agents/helpers/chart_specialist.md`（按需调用）
- [ ] 实现图表类型选择决策树（bar/line/pie/table）
- [ ] 实现数据格式化逻辑
- [ ] 实现颜色映射（与主题色一致）
- **负责人**: 开发者
- **验收标准**: 图表类型选择准确率>90%

### Day 10: 内容验证

**TASK-016**: Content Production端到端测试

- [ ] 测试15页deck内容生成完整性
- [ ] 验证字符数限制遵守率（100%）
- [ ] 验证图表配置正确性
- [ ] 验证视觉一致性（字体、颜色符合Visual Design Spec）
- **负责人**: 测试
- **验收标准**: 3个场景内容生成测试通过

---

## Week 3: 文件生成与验证 (Day 11-15)

### Day 11-12: Stage 5 - File Generation (关键验证)

**TASK-017**: document-skills:pptx能力验证 🔥

- [ ] 测试document-skills:pptx基础功能（创建演示文稿）
- [ ] 测试20种布局模板支持度
- [ ] 测试基础图表生成（bar, line, pie, table）
- [ ] 测试图片插入与定位
- [ ] 测试中文字体支持
- [ ] 识别能力边界（哪些功能不支持）
- **负责人**: 开发者 + 测试
- **验收标准**: 明确document-skills支持的功能列表，记录不支持的功能
- **风险**: 如果能力不足，启动Fallback方案（导出design_export.zip）

**TASK-018**: File Generator Agent

- [ ] 创建 `agents/file_generator.md`（Agent定义）
- [ ] 实现Slide Content → document-skills输入格式转换
- [ ] 实现document-skills:pptx调用逻辑
- [ ] 实现重试机制（最多3次，处理临时错误）
- [ ] 实现presentation.pptx输出
- **负责人**: 开发者
- **验收标准**: 符合REQ-FILEGEN-001，成功生成.pptx文件

**TASK-019**: Quality Validation

- [ ] 实现页面数量校验（actual = expected, 0容错）
- [ ] 实现文件大小校验（1-50 MB合理范围）
- [ ] 实现结构完整性检查（文件可打开，页面可渲染）
- [ ] 实现内容完整性检查（≥90%页面有标题）
- [ ] 生成quality_report.yaml
- **负责人**: 开发者
- **验收标准**: 符合REQ-FILEGEN-002，质量报告生成

**TASK-020**: Fallback机制

- [ ] 实现Fallback触发条件（生成失败或质量验证失败）
- [ ] 实现design_export.zip打包（Story Blueprint + Page Manifest + Visual Spec + Slide Content）
- [ ] 生成README.md（手动组装指南）
- [ ] 导出图表数据为.csv
- [ ] 导出图片资源
- **负责人**: 开发者
- **验收标准**: 符合REQ-FILEGEN-003，Fallback成功率100%

### Day 13-14: 端到端测试

**TASK-021**: 3场景完整流程测试

- [ ] 场景1: Business pitch deck（15页，Professional Dark主题）
- [ ] 场景2: Product launch（20页，Modern Light主题）
- [ ] 场景3: Technical report（10页，Academic Minimal主题）
- [ ] 记录每个场景的耗时（Stage 1-5分段计时）
- [ ] 记录Token消耗
- **负责人**: 测试
- **验收标准**: 3个场景全部生成成功，质量评分≥80分

**TASK-022**: 性能与成功率测试

- [ ] 测试总耗时（目标：60-90分钟）
- [ ] 测试生成成功率（目标：≥80%）
- [ ] 测试HITL响应时间（用户交互延迟）
- [ ] 测试并发场景（多用户同时使用）
- **负责人**: 测试
- **验收标准**: 符合proposal.md的成功标准

### Day 15: Bug修复

**TASK-023**: 问题修复与优化

- [ ] 修复端到端测试发现的问题
- [ ] 优化性能瓶颈（如专家库加载、LLM调用）
- [ ] 完善错误处理与日志
- [ ] 优化用户提示信息
- **负责人**: 开发者
- **验收标准**: 无P0/P1级别bug

---

## Week 4: 优化与发布 (Day 16-20)

### Day 16-17: 用户体验优化

**TASK-024**: HITL体验优化

- [ ] 优化Story Blueprint确认界面（可视化展示section结构）
- [ ] 优化主题选择界面（显示主题预览图）
- [ ] 实现HITL历史记录（用户可查看之前的选择）
- [ ] 实现快速重试（HITL点修改后重新生成）
- **负责人**: 开发者
- **验收标准**: 用户满意度调研>80%

**TASK-025**: 进度可视化

- [ ] 实现Stage进度条（Stage 1/5 [=====> ] 20%）
- [ ] 实现每个Stage的子任务进度
- [ ] 实现预计剩余时间估算
- [ ] 实现错误提示与恢复建议
- **负责人**: 开发者
- **验收标准**: 用户能清晰了解当前进度

### Day 18: 文档编写

**TASK-026**: 用户文档

- [ ] 编写用户使用指南（Quick Start）
- [ ] 编写3个场景使用示例
- [ ] 编写常见问题FAQ
- [ ] 编写故障排查指南
- **负责人**: 技术写作
- **验收标准**: 文档完整，可独立使用

**TASK-027**: 开发文档

- [ ] 编写专家库扩展指南（如何添加新主题、布局）
- [ ] 编写Agent开发指南
- [ ] 编写数据模型Schema文档
- [ ] 编写API接口文档
- **负责人**: 开发者
- **验收标准**: 开发者可基于文档扩展功能

### Day 19: 发布准备

**TASK-028**: 完整回归测试

- [ ] 5个场景完整测试（Business pitch, Product launch, Technical report, Training deck, Sales proposal）
- [ ] 所有HITL点测试
- [ ] Fallback机制测试
- [ ] 性能基准测试
- **负责人**: 测试
- **验收标准**: 所有测试通过，符合v1.0验收标准

**TASK-029**: 模块安装器

- [ ] 创建 `_module-installer/install.sh`
- [ ] 检查依赖项（BMAD-CORE v6, document-skills:pptx）
- [ ] 创建配置向导
- [ ] 创建快速开始示例
- **负责人**: 开发者
- **验收标准**: 一键安装成功

### Day 20: 发布

**TASK-030**: 代码发布

- [ ] 代码合并到主分支（hanyun分支 → main分支）
- [ ] 创建v1.0 Git Tag
- [ ] 发布Release Notes
- [ ] 更新项目README
- **负责人**: 项目负责人
- **验收标准**: v1.0正式发布

---

## 依赖与风险

### 关键依赖

| 依赖项               | 类型     | 风险等级 | 缓解措施                                   |
| -------------------- | -------- | -------- | ------------------------------------------ |
| document-skills:pptx | 外部技能 | 🔥 高    | Week 3 Day 11-12提前验证，准备Fallback方案 |
| BMAD-CORE v6         | 内部框架 | ✅ 低    | 已验证稳定                                 |
| Claude Sonnet 4.5    | LLM服务  | ⚠️ 中    | 配置超时重试，限制单次调用token数          |

### 风险清单

**RISK-001**: document-skills:pptx能力不足

- **影响**: 部分布局/图表无法生成
- **概率**: 30%
- **缓解**: Week 3提前验证能力边界
- **应对**: 启用Fallback机制（design_export.zip），v2.0引入python-pptx备选

**RISK-002**: 生成耗时超过90分钟

- **影响**: 用户体验下降
- **概率**: 20%
- **缓解**: 优化LLM调用，缓存专家库模板
- **应对**: 拆分Stage 4（Content Production）为并行子任务

**RISK-003**: HITL用户响应超时

- **影响**: 工作流卡住
- **概率**: 15%
- **缓解**: 实现默认选择（Story确认→继续，主题选择→Theme A）
- **应对**: 增加超时提示，允许后续修改

---

## 资源需求

| 角色       | 人数 | 投入时间       |
| ---------- | ---- | -------------- |
| 开发者     | 1    | 100% (4周)     |
| 测试工程师 | 1    | 50% (Week 2-4) |
| 技术写作   | 1    | 25% (Week 4)   |
| 项目负责人 | 1    | 10% (全程)     |

---

## 验收标准汇总

### Week 1验收标准

- [ ] PPTDesignInputs数据模型完成
- [ ] 5-Stage工作流引擎可运行
- [ ] Stage 1-2 Agent实现完成
- [ ] Story Blueprint → Page Manifest集成测试通过

### Week 2验收标准

- [ ] Stage 3-4 Agent实现完成
- [ ] 8个视觉主题 + 20个布局模板完成
- [ ] 内容生成测试通过（字符数限制、视觉一致性）

### Week 3验收标准

- [ ] document-skills:pptx能力验证完成
- [ ] Stage 5 File Generator实现完成
- [ ] 3个场景端到端测试通过
- [ ] 生成成功率≥80%

### v1.0最终验收标准 (Week 4结束)

- [ ] 5个场景完整测试通过
- [ ] 总耗时：60-90分钟（Quick mode目标）
- [ ] 生成成功率≥80%
- [ ] 质量评分≥80分（设计一致性>85%, 内容清晰度>90%）
- [ ] HITL用户满意度>80%
- [ ] 一次性成功率>60%（无需大幅修改）
- [ ] Fallback交付率100%
- [ ] 用户文档完整

---

**任务清单版本**: v1.0 (5-Stage Architecture)
**最后更新**: 2025-11-22
**下次评审**: Week 2结束（Day 10）
