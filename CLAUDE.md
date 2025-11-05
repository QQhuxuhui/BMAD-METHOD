# 你必须遵循的准则
## 语言要求
1. 所有回复必须使用中文

## 开发要求
1. 在对某项功能进行修改和开发时，你必须要深度思考，不能影响我的其他正常功能，如果改动某项功能的时候必须要改动其他功能的 代码或者文字才能实现，你必须要向我确认
2. 开发过程要严格遵循我的项目的技术框架规范
3. 你可以任意使用现有的MCP
4. 必须使用git做好文件的变更管理，并提交到远程仓库
5. 必须使用合理的git分支策略
6. 基于开源框架的开发，必须使用context7去查询文档，根据官方的文档为依据研发

## 开发环境说明
1. 我的宿主机的环境管理方式如下：
- **nvm**: nodejs的版本管理工具
  - 功能：管理多个Node.js版本的安装和切换
  - 用途：项目版本隔离、版本兼容性测试
  - **🚨 强制要求：所有Node.js版本相关操作必须通过nvm进行，包括版本检查、切换、安装**
  - 常用命令：`nvm list`、`nvm use <version>`、`nvm install <version>`
  - 在使用nvm命令之前，需要执行一下source命令，使环境变量生效：`source ~/.nvm/nvm.sh`
- **uv**: python的虚拟环境管理工具
- **docker**: 容器技术
  - 功能：应用容器化部署和运行
  - 用途：环境一致性、微服务部署、开发环境隔离
  - **🚨 强制要求：生产环境部署和服务容器化必须使用docker**
  - 常用命令：`docker build`、`docker run`、`docker ps`、`docker logs`
- **docker compose**: 容器编排工具
  - 功能：多容器应用的定义和运行
  - 用途：本地开发环境搭建、多服务协调部署
  - **🚨 强制要求：多服务本地开发环境必须使用docker-compose进行编排**
  - 常用命令：`docker-compose up`、`docker-compose down`、`docker-compose logs`

### 环境管理最佳实践
1. **开发环境隔离**：每个项目使用独立的Python虚拟环境和Node.js版本
2. **版本锁定**：在项目中明确指定Python和Node.js的具体版本要求
3. 

## git分支命名规范

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
