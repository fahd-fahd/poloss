#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import logging
from pathlib import Path

# إضافة المجلد الرئيسي إلى مسار البحث
sys.path.append(str(Path(__file__).parent.parent))

# استيراد الوحدات اللازمة
from utils.logger import setup_logger
from utils.config_loader import load_config, create_config_dirs

# التأكد من إنشاء المجلدات اللازمة
create_config_dirs()

# تحميل متغيرات البيئة
from dotenv import load_dotenv
load_dotenv()

# إعداد التسجيل
logger = setup_logger()

# استيراد المكتبات بعد إعداد التسجيل
try:
    import discord
    from discord.ext import commands
    import motor.motor_asyncio
    from flask import Flask, jsonify, request, render_template_string
    logger.info("تم استيراد جميع المكتبات بنجاح")
except ImportError as e:
    logger.critical(f"فشل استيراد مكتبة: {str(e)}")
    logger.critical("تأكد من تثبيت جميع المكتبات باستخدام: pip install -r requirements.txt")
    sys.exit(1)

# إعداد Flask
app = Flask(__name__)
PORT = int(os.getenv("PORT", 3000))

# إعداد أوامر بوت Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=os.getenv("PREFIX", "!"),
    intents=intents,
    help_command=None
)

# تخزين معلومات إضافية في البوت
bot.commands_count = 0
bot.categories = set()
bot.start_time = None
bot.config = {}


@app.route("/")
def home():
    """الصفحة الرئيسية لخادم الويب"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>بوت ديسكورد</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #2c2f33;
                color: #ffffff;
                text-align: center;
                padding: 50px;
                direction: rtl;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: #23272a;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5);
            }
            h1 {
                color: #7289da;
            }
            p {
                font-size: 18px;
                line-height: 1.6;
            }
            .status {
                display: inline-block;
                background-color: #43b581;
                padding: 10px 20px;
                border-radius: 5px;
                margin-top: 20px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>بوت ديسكورد</h1>
            <p>البوت يعمل الآن! يحتوي على ألعاب متنوعة مثل الصيد، سباق الخيول، اليانصيب وغيرها.</p>
            <div class="status">الحالة: متصل</div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/health")
def health_check():
    """نقطة فحص حالة البوت"""
    import time
    return jsonify({
        "status": "up",
        "uptime": int(time.time() - (bot.start_time or time.time()))
    })


async def load_commands():
    """تحميل جميع الأوامر من مجلد الأوامر"""
    commands_path = Path(__file__).parent.parent / "commands"
    if not commands_path.exists():
        logger.warning(f"مجلد الأوامر غير موجود: {commands_path}")
        create_config_dirs()  # محاولة إنشاء المجلدات
        if not commands_path.exists():
            logger.error("فشل إنشاء مجلد الأوامر")
            return

    for category in os.listdir(commands_path):
        category_path = commands_path / category
        
        # تجاهل الملفات غير المجلدات
        if not category_path.is_dir():
            continue
            
        # إضافة الفئة إلى مجموعة الفئات
        bot.categories.add(category)
        
        # تحميل جميع الأوامر في الفئة
        for command_file in category_path.glob("*.py"):
            # تجاهل الملفات الخاصة
            if command_file.name.startswith("_"):
                continue
                
            try:
                # تحميل الوحدة
                command_name = f"commands.{category}.{command_file.stem}"
                await bot.load_extension(command_name)
                logger.info(f"تم تحميل الأمر: {command_file.stem}")
                bot.commands_count += 1
            except Exception as e:
                logger.error(f"فشل تحميل الأمر {command_file.name}: {str(e)}")
    
    logger.info(f"تم تحميل {bot.commands_count} أمر من {len(bot.categories)} فئة")


async def load_events():
    """تحميل جميع الأحداث من مجلد الأحداث"""
    events_path = Path(__file__).parent.parent / "events"
    if not events_path.exists():
        logger.warning(f"مجلد الأحداث غير موجود: {events_path}")
        create_config_dirs()  # محاولة إنشاء المجلدات
        if not events_path.exists():
            logger.error("فشل إنشاء مجلد الأحداث")
            return

    events_count = 0
    for event_file in events_path.glob("*.py"):
        # تجاهل الملفات الخاصة
        if event_file.name.startswith("_"):
            continue
            
        try:
            # تحميل الوحدة
            event_name = f"events.{event_file.stem}"
            await bot.load_extension(event_name)
            logger.info(f"تم تحميل الحدث: {event_file.stem}")
            events_count += 1
        except Exception as e:
            logger.error(f"فشل تحميل الحدث {event_file.name}: {str(e)}")
    
    logger.info(f"تم تحميل {events_count} حدث")


@bot.event
async def on_ready():
    """الحدث الذي يتم تشغيله عند تسجيل الدخول إلى Discord"""
    import time
    bot.start_time = time.time()
    
    logger.info("===================================")
    logger.info(f"✅ تم تسجيل الدخول باسم {bot.user.name}!")
    logger.info(f"معرف البوت: {bot.user.id}")
    logger.info(f"عدد الخوادم: {len(bot.guilds)}")
    logger.info(f"عدد المستخدمين: {sum(guild.member_count for guild in bot.guilds)}")
    logger.info(f"نسخة Discord.py: {discord.__version__}")
    logger.info("===================================")
    
    # تعيين حالة البوت
    status = os.getenv("BOT_STATUS", "!مساعدة | !help | البنك والموسيقى")
    await bot.change_presence(
        activity=discord.Activity(
            name=status,
            type=discord.ActivityType.listening
        ),
        status=discord.Status.online
    )
    
    logger.info(f"تم تعيين حالة البوت: {status}")


async def start_bot():
    """بدء تشغيل البوت وخادم الويب"""
    # تحميل الإعدادات
    bot.config = load_config()
    
    # تحميل الأوامر والأحداث
    await load_commands()
    await load_events()
    
    # محاولة الاتصال بقاعدة البيانات MongoDB
    mongodb_uri = os.getenv("MONGODB_URI")
    if mongodb_uri:
        try:
            # إنشاء اتصال MongoDB
            mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000
            )
            # فحص الاتصال
            await mongo_client.server_info()
            
            # تعيين قاعدة البيانات في البوت
            db_name = os.getenv("DB_NAME", "discord_bot")
            bot.db = mongo_client[db_name]
            logger.info("تم الاتصال بقاعدة البيانات MongoDB")
        except Exception as e:
            logger.error(f"فشل الاتصال بقاعدة البيانات: {str(e)}")
            logger.warning("متابعة التشغيل بدون قاعدة بيانات")
    else:
        logger.warning("لم يتم تعيين MONGODB_URI، متابعة التشغيل بدون قاعدة بيانات")
    
    # محاولة الاتصال بـ Discord
    token = os.getenv("TOKEN")
    if not token or token == "dev_token":
        logger.warning("رمز Discord غير صالح، تشغيل خادم الويب فقط")
        return False
    
    try:
        await bot.start(token)
        return True
    except discord.LoginFailure:
        logger.error("رمز Discord غير صالح. تأكد من تعيين TOKEN بشكل صحيح في ملف .env")
        return False
    except Exception as e:
        logger.error(f"فشل الاتصال بـ Discord: {str(e)}")
        return False


def run_flask():
    """تشغيل خادم Flask في وضع التطوير"""
    app.run(host="0.0.0.0", port=PORT)


async def main():
    """الدالة الرئيسية لتشغيل البوت"""
    # إعداد معالجي الأخطاء لعملية asyncio
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(lambda _, context: logger.error(
        f"خطأ غير معالج في asyncio: {context['message']}"
    ))
    
    # تشغيل خادم الويب في مؤشر ترابط منفصل
    import threading
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info(f"خادم الويب يعمل على المنفذ {PORT}")
    
    # محاولة تشغيل البوت
    discord_connected = await start_bot()
    logger.info(f"حالة التطبيق: خادم الويب: متصل | Discord: {'متصل' if discord_connected else 'غير متصل'}")
    
    # إبقاء البرنامج مشغلاً حتى إذا فشل الاتصال بـ Discord
    if not discord_connected:
        # الانتظار إلى ما لا نهاية
        while True:
            await asyncio.sleep(3600)  # انتظار ساعة


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"خطأ في البرنامج الرئيسي: {str(e)}") 