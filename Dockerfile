# 使用官方Python 3.11镜像作为基础镜像
FROM python:3.11-slim

# 构建时代理参数（可选）
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG SOCKS_PROXY
ARG ALL_PROXY
ARG NO_PROXY

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --fix-missing gcc || \
    (apt-get update && apt-get install -y --fix-missing gcc) && \
    rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 设置日志文件权限
RUN chmod 755 /app

# 暴露端口（如果需要）
# EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; exit(0 if all([os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH'), os.getenv('BASE_SERVICE_URL')]) else 1)"

# 默认命令
CMD ["python", "main.py"]