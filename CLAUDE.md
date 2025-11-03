# Claude Code 开发备忘

个人开发快速参考。

## 分支命名

**主分支**: `hanyun`

**功能分支**: `hanyun-{描述}`

```bash
# 新功能/修复
hanyun-feature-xxx
hanyun-fix-xxx

# 重要：不能用 hanyun/xxx（Git 限制）
```

## 提交信息

简单格式：`类型: 描述`

```bash
feat: 添加新功能
fix: 修复bug
docs: 更新文档
chore: 其他改动
```

## 常用命令

```bash
# 新建分支
git checkout -b hanyun-feature-xxx

# 提交推送
git add .
git commit -m "feat: 描述"
git push

# 合并到主分支
git checkout hanyun
git merge hanyun-feature-xxx
git push

# 查看我的分支
git branch | grep hanyun
```
