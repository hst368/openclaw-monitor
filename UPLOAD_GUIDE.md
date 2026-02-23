# GitHub 上传指南

本指南说明如何将 OpenClaw Monitor 上传到 GitHub。

## 准备工作

### 1. 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `openclaw-monitor` (或你喜欢的名字)
   - Description: `Web dashboard for monitoring OpenClaw AI agents`
   - 选择 "Public" 或 "Private"
   - **不要勾选** "Initialize this repository with a README"
   - 点击 "Create repository"

### 2. 复制仓库地址

创建后会看到类似：
```
https://github.com/yourusername/openclaw-monitor.git
```

## 上传步骤

### 方式一：命令行（推荐）

在 WSL2 中执行：

```bash
# 1. 进入项目目录
cd ~/openclaw-monitor

# 2. 初始化 Git 仓库
git init

# 3. 添加所有文件
git add .

# 4. 提交
git commit -m "Initial commit: OpenClaw Monitor v1.0.0

Features:
- Real-time monitoring dashboard
- Multi-model pricing management
- Token usage and cost analysis
- Task tracking and error logs
- Mobile responsive design
- Basic authentication"

# 5. 关联远程仓库（替换 yourusername）
git remote add origin https://github.com/yourusername/openclaw-monitor.git

# 6. 推送到 GitHub
git branch -M main
git push -u origin main
```

### 方式二：GitHub Desktop

1. 下载 [GitHub Desktop](https://desktop.github.com/)
2. File → Add local repository
3. 选择 `~/openclaw-monitor` 目录
4. 填写 Summary: "Initial commit"
5. 点击 "Commit to main"
6. 点击 "Publish repository"
7. 输入仓库名和描述，点击 "Publish"

## 验证上传

上传完成后，访问：
```
https://github.com/yourusername/openclaw-monitor
```

确认以下文件存在：
- [ ] README.md
- [ ] LICENSE
- [ ] .gitignore
- [ ] app.py
- [ ] pricing_manager.py
- [ ] data_collector.py
- [ ] requirements.txt
- [ ] Dockerfile
- [ ] docker-compose.yml
- [ ] templates/index.html
- [ ] static/style.css
- [ ] static/dashboard.js

## 后续更新

修改代码后上传更新：

```bash
cd ~/openclaw-monitor

git add .
git commit -m "feat: your update description"
git push origin main
```

## 设置 GitHub Secrets（可选）

如果启用 GitHub Actions CI/CD：

1. 进入仓库 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加以下 secrets：
   - `DOCKER_USERNAME`: Docker Hub 用户名
   - `DOCKER_PASSWORD`: Docker Hub 密码

## 添加截图（推荐）

在 README 中展示界面效果：

1. 在项目中创建 `screenshots/` 目录
2. 添加截图图片
3. 在 README.md 中引用：

```markdown
![Overview](screenshots/overview.png)
![Pricing](screenshots/pricing.png)
```

## 发布 Release

发布正式版本：

1. 在 GitHub 仓库点击 "Releases" → "Create a new release"
2. 选择 "Choose a tag" → 输入 `v1.0.0` → "Create new tag"
3. Release title: `v1.0.0 - Initial Release`
4. 描述主要功能
5. 点击 "Publish release"

## 相关链接

上传完成后，可以添加这些徽章到 README：

```markdown
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
```

## 常见问题

### Q: 提示 "fatal: not a git repository"

A: 确保在项目目录执行了 `git init`

### Q: 提示 "Permission denied"

A: 使用 HTTPS 链接而非 SSH，或配置 SSH key

### Q: 提示 "failed to push some refs"

A: 先执行 `git pull origin main` 再 push

### Q: 大文件上传失败

A: 确保没有提交日志文件或虚拟环境目录（已被 .gitignore 排除）

---

上传完成后，你的项目就正式开源了！🎉
