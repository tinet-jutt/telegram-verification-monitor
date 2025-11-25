#!/usr/bin/env python3
from telethon import TelegramClient, events
import asyncio
import logging
import requests
import re
import sys
import os

# 配置日志
from logging.handlers import RotatingFileHandler

# 创建日志格式器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# 创建logs目录（如果不存在）
os.makedirs('/app/logs', exist_ok=True)

# 创建文件处理器，限制大小为1MB，保留3个备份文件
file_handler = RotatingFileHandler(
    '/app/logs/telegram.log', 
    maxBytes=1024*1024,  # 1MB
    backupCount=3,       # 保留3个备份文件
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

# 配置根日志器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# API 配置 - 从环境变量获取
api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
api_hash = os.getenv('TELEGRAM_API_HASH', '')

# 服务配置 - 从环境变量获取
BASE_SERVICE_URL = os.getenv('BASE_SERVICE_URL', '')
TELEGRAM_OFFICIAL_ID = 777000

# 验证必需的环境变量
if not api_id or not api_hash or not BASE_SERVICE_URL:
    logger.error("❌ 缺少必需的环境变量:")
    if not api_id:
        logger.error("  - TELEGRAM_API_ID")
    if not api_hash:
        logger.error("  - TELEGRAM_API_HASH")
    if not BASE_SERVICE_URL:
        logger.error("  - BASE_SERVICE_URL")
    logger.error("请设置这些环境变量后重新运行")
    sys.exit(1)

def get_proxy_config():
    """从环境变量获取代理配置"""
    proxy_type = os.getenv('TELEGRAM_PROXY_TYPE', '').lower()
    proxy_addr = os.getenv('TELEGRAM_PROXY_ADDR', '')
    proxy_port = os.getenv('TELEGRAM_PROXY_PORT', '')
    proxy_username = os.getenv('TELEGRAM_PROXY_USERNAME', '')
    proxy_password = os.getenv('TELEGRAM_PROXY_PASSWORD', '')
    proxy_rdns = os.getenv('TELEGRAM_PROXY_RDNS', 'true').lower() == 'true'
    
    # 如果没有配置代理类型或地址，返回 None
    if not proxy_type or not proxy_addr or not proxy_port:
        return None
    
    try:
        proxy_port = int(proxy_port)
    except ValueError:
        logger.warning(f"⚠️ 代理端口无效: {proxy_port}")
        return None
    
    # 构建代理配置字典
    proxy_config = {
        'proxy_type': proxy_type,  # 'socks5', 'socks4', 'http'
        'addr': proxy_addr,
        'port': proxy_port,
        'rdns': proxy_rdns
    }
    
    # 如果有用户名和密码，添加到配置中
    if proxy_username:
        proxy_config['username'] = proxy_username
    if proxy_password:
        proxy_config['password'] = proxy_password
    
    logger.info(f"✅ 代理配置: {proxy_type}://{proxy_addr}:{proxy_port}")
    return proxy_config

# 验证码正则表达式模式
AUTH_CODE_PATTERNS = [
    r'\*\*Login code:\*\*\s*(\d{5})',  # **Login code:** 35628
    r'Login code:\s*(\d{5})',
    r'Your login code is (\d{5})',
    r'(\d{5}) is your Telegram code',
    r'code[：:]\s*(\d{5})',
    r'验证码[：:]\s*(\d{5})',
    r'(\d{5})',  # 最后匹配任何5位数字
]

def extract_auth_code(text):
    """从消息文本中提取验证码"""
    if not text:
        return None
    
    for pattern in AUTH_CODE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

async def send_auth_code_to_service(auth_code):
    """发送验证码到指定服务"""
    try:
        # 构建完整的URL，直接拼接验证码
        target_url = f"{BASE_SERVICE_URL}{auth_code}"
        logger.info(f"🌐 发送请求到: {target_url}")
        
        response = requests.get(target_url, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ 验证码 {auth_code} 成功发送到服务")
            logger.info(f"📋 服务响应: {response.text}")
            return True
        else:
            logger.error(f"❌ 发送验证码失败，状态码: {response.status_code}")
            logger.error(f"📋 响应内容: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 发送验证码时发生错误: {e}")
        return False

class TelegramMonitor:
    def __init__(self):
        # 在Docker环境中使用data目录存储session文件
        session_path = os.path.join('data', 'session_auto_jd') if os.path.exists('data') else 'session_auto_jd'
        
        # 获取代理配置
        proxy = get_proxy_config()
        
        # 创建 TelegramClient，如果有代理配置则使用代理
        self.client = TelegramClient(session_path, api_id, api_hash, proxy=proxy)
        self.running = False
    
    async def auto_login_if_needed(self):
        """自动检查并执行登录（如果需要）"""
        try:
            logger.info("🔍 检查登录状态...")
            
            # 连接到Telegram
            await self.client.connect()
            
            # 检查是否已授权
            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                logger.info(f"✅ 用户已登录: {me.first_name} (ID: {me.id})")
                return True
            else:
                logger.info("⚠️ 用户未授权，开始自动登录流程...")
                
                # 开始登录流程
                await self.client.start()
                
                # 再次检查授权状态
                if await self.client.is_user_authorized():
                    me = await self.client.get_me()
                    logger.info(f"✅ 自动登录成功: {me.first_name} (ID: {me.id})")
                    
                    # 测试访问Telegram官方
                    try:
                        telegram_official = await self.client.get_entity(TELEGRAM_OFFICIAL_ID)
                        logger.info(f"✅ 可以访问Telegram官方: {telegram_official.first_name}")
                        
                        messages = await self.client.get_messages(TELEGRAM_OFFICIAL_ID, limit=3)
                        logger.info(f"📋 最近收到 {len(messages)} 条官方消息")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ 访问Telegram官方时出错: {e}")
                    
                    return True
                else:
                    logger.error("❌ 自动登录失败，用户仍未授权")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 自动登录过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def message_handler(self, event):
        """处理新消息"""
        try:
            message = event.message
            sender = await event.get_sender()
            
            if not sender:
                return
            
            logger.info(f"📨 收到消息 - 发送者: {getattr(sender, 'first_name', 'Unknown')} (ID: {sender.id})")
            
            # 只处理来自Telegram官方的消息
            if sender.id == TELEGRAM_OFFICIAL_ID:
                logger.info(f"🎯 Telegram官方消息: {message.text}")
                
                # 提取验证码
                auth_code = extract_auth_code(message.text)
                
                if auth_code:
                    logger.info(f"🔍 检测到验证码: {auth_code}")
                    success = await send_auth_code_to_service(auth_code)
                    
                    if success:
                        logger.info(f"📤 验证码 {auth_code} 已成功转发")
                    else:
                        logger.error(f"❌ 验证码 {auth_code} 转发失败")
                else:
                    logger.info("⚠️ 消息中未检测到验证码")
            else:
                logger.debug(f"📨 非官方消息，发送者ID: {sender.id}")
                
        except Exception as e:
            logger.error(f"❌ 处理消息时发生错误: {e}")
    
    async def start_monitoring(self):
        """开始监听"""
        try:
            logger.info("🚀 启动Telegram验证码监听服务...")
            
            # 自动检查并登录（如果需要）
            if not await self.auto_login_if_needed():
                logger.error("❌ 登录失败，无法启动监听服务")
                return False
            
            # 注册事件处理器
            self.client.add_event_handler(self.message_handler, events.NewMessage)
            logger.info("✅ 消息监听器已注册")
            
            logger.info(f"🎯 开始监听Telegram官方验证码 (ID: {TELEGRAM_OFFICIAL_ID})")
            logger.info(f"🌐 目标服务: {BASE_SERVICE_URL}[验证码]")
            logger.info("💡 现在可以发送消息来测试监听功能")
            
            self.running = True
            
            # 保持运行
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ 监听服务启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.client.disconnect()
            logger.info("🔌 已断开连接")
    
    def stop(self):
        """停止监听"""
        self.running = False
        logger.info("🛑 停止监听服务")

async def main():
    """主函数"""
    monitor = TelegramMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("👋 收到中断信号，正在停止...")
        monitor.stop()
    except Exception as e:
        logger.error(f"❌ 程序错误: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 程序已退出")
    except Exception as e:
        logger.error(f"❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()