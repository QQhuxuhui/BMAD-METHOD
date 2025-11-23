# Spec: 构建系统集成 (Build System)

**Capability ID**: `build-system`
**Change**: `migrate-ppt-to-bmad-arch`
**Status**: Proposed

---

## ADDED Requirements

### Requirement: MUST Generate Build Metadata

The build system MUST generate metadata file to record build information.

**ID**: `build-system-005`
**Priority**: P0 (Critical)

**Acceptance Criteria**:

- 文件`.build-meta.json`包含模块名称
- 包含构建时间戳
- 包含源码哈希值
- 包含agents数量

#### Scenario: 验证构建元数据内容

**Given**: 构建已完成
**When**: 读取`bmad/ppt/.build-meta.json`
**Then**:

- JSON包含`module: "ppt"`
- 包含`buildTime`字段（ISO 8601格式）
- 包含`sourceHash`字段
- 包含`agents: 8`

**Validation**:

```bash
node -e "
const meta = require('./bmad/ppt/.build-meta.json');
if (meta.module !== 'ppt') throw new Error('Invalid module');
if (!meta.buildTime) throw new Error('Missing buildTime');
if (!meta.sourceHash) throw new Error('Missing sourceHash');
if (meta.agents !== 8) throw new Error('Invalid agents count');
console.log('✅ Build metadata valid');
"
```

---

## Cross-References

**依赖于**:

- `source-migration` - 需要源码目录和资源文件
- `agent-conversion` - 需要YAML agents已创建

**被依赖于**:

- `installer-upgrade` - 安装器需要触发构建

---

_此spec由OpenSpec系统生成 - 2025-11-23_
