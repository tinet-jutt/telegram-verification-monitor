#!/usr/bin/env python3
from telethon import TelegramClient
import asyncio
import os
import sys

# API 配置 - 从环境变量获取
api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
api_hash = os.getenv('TELEGRAM_API_HASH', '')

# 验证必需的环境变量
if not api_id or not api_hash:
    print("❌ 缺少必需的环境变量:")
    if not api_id:
        print("  - TELEGRAM_API_ID")
    if not api_hash:
        print("  - TELEGRAM_API_HASH")
    print("请设置这些环境变量后重新运行")
    sys.exit(1)

async def login():
    # 在Docker环境中使用data目录存储session文件
    session_path = os.path.join('data', 'session_auto_jd') if os.path.exists('data') else 'session_auto_jd'
    client = TelegramClient(session_path, api_id, api_hash)
    
    try:
        print("正在连接到Telegram...")
        await client.start()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ 登录成功!")
            print(f"用户: {me.first_name} {me.last_name or ''}")
            print(f"用户名: @{me.username or 'N/A'}")
            print(f"电话: {me.phone or 'N/A'}")
            print(f"用户ID: {me.id}")
            
            # 测试访问Telegram官方
            try:
                telegram_official = await client.get_entity(777000)
                print(f"✅ 可以访问Telegram官方: {telegram_official.first_name}")
                
                messages = await client.get_messages(777000, limit=3)
                print(f"最近收到 {len(messages)} 条官方消息")
                
            except Exception as e:
                print(f"⚠️ 访问Telegram官方时出错: {e}")
                
        else:
            print("❌ 登录失败，用户未授权")
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(login())