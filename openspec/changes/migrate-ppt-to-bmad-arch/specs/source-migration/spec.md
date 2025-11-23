# Spec: 源码目录迁移 (Source Migration)

**Capability ID**: `source-migration`
**Change**: `migrate-ppt-to-bmad-arch`
**Status**: Proposed

---

## ADDED Requirements

### Requirement: MUST Create README and Documentation

The system MUST create README.md in source directory to document development workflow.

**ID**: `source-migration-005`
**Priority**: P0 (Critical)

**Acceptance Criteria**:
- README.md存在于`src/modules/ppt/`
- 文档说明构建流程
- 文档说明开发规范

#### Scenario: 创建开发者README

**Given**: 源码目录结构已创建
**When**: 创建README.md
**Then**:
- `src/modules/ppt/README.md`存在
- README包含以下章节：
  - "PPT Module - Source Code"
  - "Architecture: BMAD-METHOD v6 - YAML Agents"
  - "Development Workflow"
  - "Build System"

**Validation**:
```bash
test -f src/modules/ppt/README.md
grep -q "Development Workflow" src/modules/ppt/README.md
grep -q "Build System" src/modules/ppt/README.md
```

---

## MODIFIED Requirements

无（此capability为全新创建，无修改现有需求）

---

## REMOVED Requirements

无（此迁移不删除现有功能）

---

## Cross-References

**依赖于**：
- 无（这是第一步）

**被依赖于**：
- `agent-conversion` - 需要源码目录结构存在
- `build-system` - 需要资源文件已迁移

**相关Specs**：
- `build-system/spec.md` - 构建系统将从此源码目录读取
- `agent-conversion/spec.md` - Agent将在此目录中创建

---

## Implementation Notes

**技术要点**：
1. 使用`fs-extra`的`copy`方法进行文件复制（保留权限和时间戳）
2. 备份使用日期格式：`YYYYMMDD`
3. 验证使用Node.js脚本而非bash（跨平台兼容性）

**注意事项**：
- 复制前确保目标目录不存在（避免覆盖）
- 复制后验证文件数量和大小
- 保留`.gitkeep`文件以维护空目录结构

**参考实现**：
```javascript
// src/modules/ppt/build.js中的copyResources函数
const fs = require('fs-extra');
const path = require('path');

async function copyResources() {
  const COPY_ITEMS = [
    'workflows',
    'expert-library',
    'schemas',
    'config.yaml',
    '_module-installer'
  ];

  for (const item of COPY_ITEMS) {
    const sourcePath = path.join(SOURCE_DIR, item);
    const targetPath = path.join(TARGET_DIR, item);

    if (await fs.pathExists(sourcePath)) {
      await fs.copy(sourcePath, targetPath, {
        overwrite: true,
        errorOnExist: false
      });
    }
  }
}
```

---

## Testing Strategy

**单元测试**：
- 测试目录创建逻辑
- 测试文件复制逻辑
- 测试备份命名逻辑

**集成测试**：
- 完整迁移流程测试
- 验证资源完整性
- 测试回滚机制

**验收测试**：
- 手动验证目录结构
- 检查关键文件清单
- 对比源目录和目标目录

---

_此spec由OpenSpec系统生成 - 2025-11-23_
