# OpenClaw Monitor

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</p>

<p align="center">
  <b>开源的 OpenClaw AI 代理监控面板</b><br>
  实时监控任务状态、Token 用量、成本分析，支持多模型定价管理
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#安装">安装</a> •
  <a href="#使用说明">使用说明</a> •
  <a href="#api文档">API 文档</a> •
  <a href="#配置">配置</a> •
  <a href="#截图">截图</a>
</p>

---

## 📋 目录

- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装](#安装)
- [使用说明](#使用说明)
- [配置](#配置)
- [API 文档](#api文档)
- [安全](#安全)
- [常见问题](#常见问题)
- [贡献](#贡献)
- [许可证](#许可证)

---

## ✨ 功能特性

### 核心监控
- 📊 **实时概览** - Gateway 状态、任务数、Token 用量、成本统计
- 📋 **任务管理** - 查看运行中、已完成任务，支持会话追踪
- ⚠️ **错误日志** - 聚合错误日志，支持 7 天历史查询
- 🖥️ **系统信息** - CPU、内存、磁盘、网络实时监控

### 定价管理
- 💰 **多模型定价** - 支持 Kimi、GPT-4、Claude 等主流模型
- 💱 **货币切换** - 支持人民币(CNY)和美元(USD)显示
- 📈 **成本分析** - 按日/周/月统计 Token 成本和用量趋势
- 🔄 **汇率自动更新** - 支持手动或自动获取最新汇率

### 安全特性
- 🔐 **基础身份验证** - HTTP Basic Auth 保护访问
- 🔒 **定价修改保护** - 所有定价变更需认证
- 📝 **操作历史** - 记录所有定价修改历史

### 其他特性
- 📱 **响应式设计** - 支持桌面、平板、手机访问
- 🌙 **暗色/亮色主题** - 一键切换
- 🔄 **自动刷新** - 数据每 10 秒自动更新
- 🌐 **局域网访问** - 支持同一 WiFi 下多设备访问

---

## 🔧 环境要求

- **Python**: 3.8+
- **OpenClaw**: 已安装并配置
- **操作系统**: Linux / macOS / Windows (WSL2)
- **内存**: 建议 2GB+

---

## 🚀 安装

### 方式一：一键安装脚本

```bash
# 克隆仓库
git clone https://github.com/yourusername/openclaw-monitor.git
cd openclaw-monitor

# 运行安装脚本
chmod +x install.sh
./install.sh
```

### 方式二：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/openclaw-monitor.git
cd openclaw-monitor

# 2. 安装依赖
pip3 install -r requirements.txt --user

# 3. 启动服务
python3 app.py
```

### 方式三：Docker 部署

```bash
# 构建镜像
docker build -t openclaw-monitor .

# 运行容器
docker run -d \
  --name openclaw-monitor \
  -p 8080:8080 \
  -v ~/.openclaw:/root/.openclaw:ro \
  -e MONITOR_USERNAME=admin \
  -e MONITOR_PASSWORD=yourpassword \
  openclaw-monitor
```

---

## 📖 使用说明

### 启动服务

```bash
# 基础启动
python3 app.py

# 指定端口
export PORT=8081
python3 app.py

# 自定义账号密码
export MONITOR_USERNAME=admin
export MONITOR_PASSWORD=yourpassword
python3 app.py
```

### 访问面板

| 地址 | 说明 |
|------|------|
| `http://localhost:8080` | 本机访问 |
| `http://192.168.x.x:8080` | 局域网其他设备访问 |
| `http://127.0.0.1:8080` | WSL2 内部访问 |

**默认账号密码：**
- 用户名: `admin`
- 密码: `2026` (建议修改)

### 页面导航

- **概览** - 查看总体状态、成本统计、系统信息
- **任务** - 查看运行中和已完成的任务
- **日志** - 查看错误日志和警告
- **定价** - 管理模型定价、货币设置

---

## ⚙️ 配置

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MONITOR_USERNAME` | `admin` | 登录用户名 |
| `MONITOR_PASSWORD` | `admin123` | 登录密码 |
| `PORT` | `8080` | 服务端口 |
| `HOST` | `0.0.0.0` | 监听地址 |

### 定价配置文件

配置文件位置：`~/.openclaw-monitor/pricing.json`

```json
{
  "currency": "CNY",
  "exchange_rate": {
    "USD_TO_CNY": 7.25,
    "CNY_TO_USD": 0.1379,
    "last_updated": "2026-02-23T12:00:00",
    "auto_update": true
  },
  "models": {
    "moonshot/kimi-k2.5": {
      "input_per_1k": 0.0005,
      "output_per_1k": 0.002,
      "currency": "CNY",
      "provider": "Moonshot"
    },
    "gpt-4o": {
      "input_per_1k": 0.005,
      "output_per_1k": 0.015,
      "currency": "USD",
      "provider": "OpenAI"
    }
  }
}
```

### 预置模型定价

| 模型 | 输入价格/1K | 输出价格/1K | 货币 |
|------|------------|------------|------|
| moonshot/kimi-k2.5 | ¥0.0005 | ¥0.002 | CNY |
| moonshot/kimi-k1.5 | ¥0.0002 | ¥0.001 | CNY |
| moonshot/kimi-k2 | ¥0.001 | ¥0.004 | CNY |
| gpt-4o | $0.005 | $0.015 | USD |
| gpt-4o-mini | $0.00015 | $0.0006 | USD |
| claude-3-opus | $0.015 | $0.075 | USD |
| claude-3-sonnet | $0.003 | $0.015 | USD |
| claude-3-haiku | $0.00025 | $0.00125 | USD |
| deepseek-chat | ¥0.00014 | ¥0.00028 | CNY |

---

## 🔌 API 文档

### 基础信息

- **Base URL**: `http://localhost:8080`
- **认证方式**: HTTP Basic Auth
- **Content-Type**: `application/json`

### 端点列表

#### 健康检查
```http
GET /api/health
```

**响应：**
```json
{
  "status": "ok",
  "timestamp": "2026-02-23T12:00:00",
  "version": "1.0.0-secure",
  "secure": true
}
```

#### 获取概览数据
```http
GET /api/summary
```

#### 获取定价配置
```http
GET /api/pricing
```

#### 更新模型定价
```http
POST /api/pricing
Content-Type: application/json

{
  "model": "moonshot/kimi-k2.5",
  "input_per_1k": 0.0005,
  "output_per_1k": 0.002,
  "currency": "CNY",
  "provider": "Moonshot",
  "reason": "供应商调价"
}
```

#### 计算成本
```http
POST /api/pricing/calculate
Content-Type: application/json

{
  "model": "moonshot/kimi-k2.5",
  "input_tokens": 1000,
  "output_tokens": 500
}
```

**响应：**
```json
{
  "input_cost": 0.0005,
  "output_cost": 0.001,
  "total_cost": 0.0015,
  "currency": "CNY"
}
```

#### 获取任务列表
```http
GET /api/tasks
```

#### 获取错误日志
```http
GET /api/logs?days=7
```

#### 获取系统信息
```http
GET /api/system
```

---

## 🔒 安全

### 访问控制

默认启用 HTTP Basic Auth，所有 API 和页面都需要认证。

### 修改密码

```bash
export MONITOR_USERNAME=yourname
export MONITOR_PASSWORD=yourpassword
python3 app.py
```

### 防火墙配置

建议限制只有局域网可访问：

```bash
# Linux (iptables)
iptables -A INPUT -p tcp --dport 8080 -s 192.168.0.0/16 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP

# Windows
netsh advfirewall firewall add rule name="OpenClaw Monitor" dir=in action=allow protocol=tcp localport=8080 remoteip=192.168.0.0/16
```

### HTTPS 部署

推荐使用反向代理（Nginx/Caddy）启用 HTTPS：

```nginx
server {
    listen 443 ssl;
    server_name monitor.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📸 截图

### 概览页面
概览页面展示 Gateway 状态、任务统计、Token 用量和成本分析。

### 定价管理
支持多模型定价配置、货币切换、汇率设置。

### 移动端适配
响应式设计，支持手机浏览器访问。

---

## ❓ 常见问题

### Q: Mac/手机无法访问面板？

A: WSL2 需要设置端口转发：

```powershell
# 在 Windows PowerShell (管理员) 中执行
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=172.25.x.x
netsh advfirewall firewall add rule name="OpenClaw Monitor" dir=in action=allow protocol=tcp localport=8080
```

### Q: 如何修改监听端口？

A: 修改 `app.py` 中的 `PORT` 变量，或使用环境变量：

```bash
export PORT=8081
python3 app.py
```

### Q: 成本计算不准确？

A: 确保在"定价"页面正确设置了模型价格。成本按 60% input / 40% output 估算。

### Q: 如何备份配置？

A: 定价配置保存在 `~/.openclaw-monitor/pricing.json`，直接复制备份即可。

### Q: 支持多用户吗？

A: 当前版本仅支持单用户基础认证。如需多用户，建议配合反向代理的认证功能。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境搭建

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/yourusername/openclaw-monitor.git
cd openclaw-monitor

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. 运行开发服务器
export FLASK_ENV=development
python3 app.py
```

### 提交规范

- 使用 [Conventional Commits](https://www.conventionalcommits.org/)
- 确保代码通过 `flake8` 检查
- 更新相关文档

---

## 📄 许可证

[MIT License](LICENSE) © 2026 OpenClaw Monitor Contributors

---

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - 优秀的 AI 代理框架
- [Flask](https://flask.palletsprojects.com/) - 轻量级 Web 框架
- [Chart.js](https://www.chartjs.org/) - 图表库

---

<p align="center">
  Made with ❤️ for OpenClaw Community
</p>
