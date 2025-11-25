# Telegram 验证码监听服务

这是一个基于 Docker 的 Telegram 验证码自动监听和转发服务，可以监听 Telegram 官方发送的验证码并自动转发到指定的服务 URL。

## 功能特性

- 🔄 **自动登录**: 启动时自动检查登录状态，未授权时自动引导登录
- 📁 **日志轮转**: 自动管理日志文件大小，限制为 1MB 并保留 3 个备份
- 🎯 **验证码监听**: 实时监听 Telegram 官方(ID: 777000)的验证码消息
- 🌐 **自动转发**: 检测到验证码后自动发送到指定服务 URL
- 🔍 **智能提取**: 支持多种验证码格式的正则表达式匹配
- 🐳 **Docker 化**: 完全容器化部署，环境隔离

## 快速开始

### 1. 准备工作

1. 获取 Telegram API 凭据：

   - 访问 https://my.telegram.org/apps
   - 创建应用并获取 `api_id` 和 `api_hash`

2. 克隆或下载项目文件

### 2. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```env
# Telegram API 配置
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# 服务配置
BASE_SERVICE_URL=https://your-service.com/webhook?token=your_token&title=telegram_code:
```

### 3. 创建必要目录

```bash
mkdir -p data logs
```

### 4. 首次登录

如果是首次使用，需要先进行登录授权：

```bash
# 使用Docker运行登录脚本
docker-compose run --rm telegram-monitor python login.py
```

按提示输入手机号和验证码完成授权。

### 5. 启动服务

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 使用方法

### Docker Compose (推荐)

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f telegram-monitor
```

### 直接使用 Docker

```bash
# 构建镜像
docker build -t telegram-monitor .

# 运行容器
docker run -d \
  --name telegram-monitor \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  telegram-monitor
```

## 目录结构

```
.
├── main.py              # 主程序
├── login.py             # 登录脚本
├── requirements.txt     # Python依赖
├── Dockerfile          # Docker镜像定义
├── docker-compose.yml  # Docker Compose配置
├── .env.example        # 环境变量模板
├── .dockerignore       # Docker忽略文件
├── README.md           # 说明文档
├── data/               # 数据目录(session文件)
└── logs/               # 日志目录
```

## 环境变量说明

### 必需变量

| 变量名              | 必需 | 说明                 |
| ------------------- | ---- | -------------------- |
| `TELEGRAM_API_ID`   | ✅   | Telegram API ID      |
| `TELEGRAM_API_HASH` | ✅   | Telegram API Hash    |
| `BASE_SERVICE_URL`  | ✅   | 验证码转发的目标 URL |

### 代理配置（可选）

#### Telegram 客户端专用代理

| 变量名                    | 说明               | 示例                       |
| ------------------------- | ------------------ | -------------------------- |
| `TELEGRAM_PROXY_TYPE`     | 代理类型           | `socks5`, `socks4`, `http` |
| `TELEGRAM_PROXY_ADDR`     | 代理地址           | `127.0.0.1`                |
| `TELEGRAM_PROXY_PORT`     | 代理端口           | `1080`                     |
| `TELEGRAM_PROXY_USERNAME` | 代理用户名（可选） | `username`                 |
| `TELEGRAM_PROXY_PASSWORD` | 代理密码（可选）   | `password`                 |
| `TELEGRAM_PROXY_RDNS`     | 远程 DNS 解析      | `true` (推荐)              |

详细配置请参考 [Telethon](https://docs.telethon.dev/en/stable/basic/signing-in.html#signing-in-behind-a-proxy)

## 验证码格式支持

服务支持以下验证码格式：

- `**Login code:** 35628`
- `Login code: 35628`
- `Your login code is 35628`
- `35628 is your Telegram code`
- `code: 35628`
- `验证码: 35628`
- 纯 5 位数字

## 故障排除

### 1. 权限问题

```bash
# 确保目录权限正确
chmod 755 data logs
```

### 2. 登录问题

```bash
# 重新登录
docker-compose run --rm telegram-monitor python login.py
```

### 3. 查看详细日志

```bash
# 查看容器日志
docker-compose logs telegram-monitor

# 查看应用日志文件
tail -f logs/telegram.log
```

### 4. 重置 session

```bash
# 删除session文件重新登录
rm -f data/session_auto_jd.session*
docker-compose run --rm telegram-monitor python login.py
```

## 注意事项

1. **首次使用**: 必须先运行登录脚本完成 Telegram 授权
2. **数据持久化**: session 文件和日志文件通过 volume 挂载，容器重启不会丢失
3. **网络访问**: 容器需要能够访问 Telegram 服务器和目标服务 URL
4. **代理配置**: 如果需要通过代理访问 Telegram，请参考 [PROXY_SETUP.md](PROXY_SETUP.md) 配置代理
5. **安全性**: 请妥善保管 API 凭据，不要泄露给他人

## 许可证

MIT License
