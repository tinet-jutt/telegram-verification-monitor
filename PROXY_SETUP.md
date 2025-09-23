# 🌐 Docker容器网络代理配置指南

本指南介绍如何为Telegram监听服务配置网络代理。

## 📋 配置方法

### 方法一：环境变量配置（推荐）

1. **编辑 `.env` 文件**：
```bash
# 取消注释并配置代理
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
NO_PROXY=localhost,127.0.0.1,::1
```

2. **重启容器**：
```bash
docker-compose down
docker-compose up -d
```

### 方法二：临时代理配置

```bash
# 设置环境变量后启动
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
docker-compose up -d
```

### 方法三：构建时代理配置

```bash
# 构建时使用代理
docker-compose build --build-arg HTTP_PROXY=http://127.0.0.1:7890 --build-arg HTTPS_PROXY=http://127.0.0.1:7890
```

## 🔧 常见代理配置

### HTTP/HTTPS 代理
```bash
# 在 .env 文件中配置
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
NO_PROXY=localhost,127.0.0.1,::1
```

### SOCKS5 代理
```bash
# 在 .env 文件中配置
SOCKS_PROXY=socks5://127.0.0.1:1080
ALL_PROXY=socks5://127.0.0.1:1080
NO_PROXY=localhost,127.0.0.1,::1
```

### 混合代理配置
```bash
# 可以同时配置多种代理类型
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
SOCKS_PROXY=socks5://127.0.0.1:1080
ALL_PROXY=socks5://127.0.0.1:1080
NO_PROXY=localhost,127.0.0.1,::1
```

### Clash/ClashX
```bash
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### V2Ray/V2RayN
```bash
HTTP_PROXY=http://127.0.0.1:10809
HTTPS_PROXY=http://127.0.0.1:10809
```

### Shadowsocks
```bash
HTTP_PROXY=http://127.0.0.1:1087
HTTPS_PROXY=http://127.0.0.1:1087
```

### SOCKS5代理
```bash
HTTP_PROXY=socks5://127.0.0.1:1080
HTTPS_PROXY=socks5://127.0.0.1:1080
```

## 🧪 测试代理配置

运行测试脚本验证代理是否正常工作：

```bash
# 在容器内测试
docker-compose exec telegram-monitor python test_proxy.py

# 或者直接运行测试容器
docker-compose run --rm telegram-monitor python test_proxy.py
```

## 🔍 故障排除

### 1. 代理连接失败
- 检查代理服务是否运行
- 确认代理端口是否正确
- 验证防火墙设置

### 2. Telegram API无法访问
- 确认代理支持HTTPS
- 检查代理是否允许访问api.telegram.org
- 尝试不同的代理节点

### 3. 容器内网络问题
```bash
# 检查容器网络
docker-compose exec telegram-monitor ping 8.8.8.8

# 检查DNS解析
docker-compose exec telegram-monitor nslookup api.telegram.org

# 查看环境变量
docker-compose exec telegram-monitor env | grep -i proxy
```

## 📝 配置示例

### 完整的 `.env` 配置
```bash
# Telegram API 配置
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# 服务配置
BASE_SERVICE_URL=https://your-service.com/webhook

# 代理配置
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
NO_PROXY=localhost,127.0.0.1,::1,*.local
```

### Docker Compose 网络配置
```yaml
services:
  telegram-monitor:
    # ... 其他配置
    extra_hosts:
      - "host.docker.internal:host-gateway"  # 访问宿主机代理
```

## ⚠️ 注意事项

1. **代理地址**: 容器内访问宿主机代理时，使用 `host.docker.internal` 或 `172.17.0.1`
2. **端口映射**: 确保代理服务监听在 `0.0.0.0` 而不是 `127.0.0.1`
3. **认证**: 如果代理需要认证，格式为 `http://username:password@proxy:port`
4. **SSL**: 某些代理可能需要额外的SSL配置

## 🔗 相关链接

- [Docker网络文档](https://docs.docker.com/network/)
- [Telegram API文档](https://core.telegram.org/api)
- [代理配置最佳实践](https://docs.docker.com/network/proxy/)