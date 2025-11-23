# Spec: Slash Command集成 (Slash Command Integration)

**Capability ID**: `slash-command-integration`
**Change**: `migrate-ppt-to-bmad-arch`
**Status**: Proposed

---

## ADDED Requirements

### Requirement: Ensure Command Path References are Correct

All Slash Command files MUST reference built agent paths (`bmad/ppt/agents/`).

**ID**: `slash-command-003`
**Priority**: P0 (Critical)

**Acceptance Criteria**:

- 所有引用路径以`@/bmad/ppt/agents/`开头
- 引用的文件在构建后存在
- 路径格式符合BMAD规范

#### Scenario: 验证所有命令路径有效

**Given**: 所有Slash Commands已创建
**When**: 验证路径引用
**Then**:

- 每个命令文件引用的agent文件存在于`bmad/ppt/agents/`
- 路径使用`@/`前缀（相对项目根目录）

**Validation**:

```bash
for cmd in .claude/commands/bmad/ppt*.md; do
  agent_path=$(cat "$cmd" | sed 's/@\///')
  if [ ! -f "$agent_path" ]; then
    echo "Invalid path in $cmd: $agent_path"
    exit 1
  fi
done
echo "✅ All command paths valid"
```

---

## Cross-References

**依赖于**:

- `build-system` - 需要agents已构建到`bmad/ppt/agents/`

**被依赖于**:

- `installer-upgrade` - 安装器需要创建这些命令

---

_此spec由OpenSpec系统生成 - 2025-11-23_
