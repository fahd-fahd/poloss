#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت تشغيل بوت ديسكورد
يوفر طريقة سهلة لتشغيل البوت مع التعامل مع الأخطاء الأساسية
"""

import os
import sys
from pathlib import Path
import logging

# إعداد التسجيل البسيط
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# التأكد من وجود Python 3.8+
if sys.version_info < (3, 8):
    logger.critical("خطأ: هذا البوت يتطلب Python 3.8 أو أحدث.")
    logger.critical(f"الإصدار الحالي: Python {sys.version}")
    sys.exit(1)

try:
    # التحقق من تثبيت المكتبات الأساسية
    import discord
    import motor
    import dotenv
    import flask
    import colorlog
    
    logger.info("✅ تم التحقق من المكتبات الأساسية")
except ImportError as e:
    logger.critical(f"❌ خطأ: لم يتم تثبيت جميع المكتبات المطلوبة.")
    logger.critical(f"المكتبة المفقودة: {str(e)}")
    logger.critical("قم بتثبيت المكتبات المطلوبة باستخدام:")
    logger.critical("pip install -r requirements.txt")
    sys.exit(1)

# تحميل متغيرات البيئة
from dotenv import load_dotenv

def check_env_file():
    """التحقق من وجود ملف .env"""
    env_path = Path(".") / ".env"
    
    # طباعة متغيرات البيئة الحالية
    from pprint import pformat
    logger.info("متغيرات البيئة المتاحة:")
    
    # طباعة قائمة متغيرات البيئة المتوفرة (بدون إظهار القيم)
    env_vars = [key for key in os.environ.keys()]
    logger.info(f"متغيرات البيئة: {', '.join(env_vars)}")
    
    # طباعة حالة المتغيرات المهمة
    logger.info(f"TOKEN موجود: {bool(os.getenv('TOKEN'))}")
    logger.info(f"MONGODB_URI موجود: {bool(os.getenv('MONGODB_URI'))}")
    logger.info(f"PREFIX موجود: {bool(os.getenv('PREFIX'))}")
    logger.info(f"DB_NAME موجود: {bool(os.getenv('DB_NAME'))}")
    
    # تحميل ملف .env إذا كان موجودًا
    if env_path.exists():
        logger.info("✅ تم العثور على ملف .env، جاري تحميله...")
        load_dotenv()
        logger.info("تم تحميل ملف .env بنجاح")
        return True
        
    logger.warning("⚠️ ملف .env غير موجود.")
    
    # التحقق مما إذا كان TOKEN متوفرًا في متغيرات البيئة
    if not os.getenv("TOKEN"):
        logger.warning("⚠️ لم يتم تعيين TOKEN في متغيرات البيئة.")
        logger.warning("سيعمل البوت في وضع خادم الويب فقط.")
    else:
        logger.info("✅ تم العثور على TOKEN في متغيرات البيئة.")
    
    if not os.getenv("MONGODB_URI"):
        logger.warning("⚠️ لم يتم تعيين MONGODB_URI في متغيرات البيئة.")
        logger.warning("سيعمل البوت بدون اتصال بقاعدة البيانات.")
    else:
        logger.info("✅ تم العثور على MONGODB_URI في متغيرات البيئة.")
        
        # التحقق من تنسيق MONGODB_URI
        mongodb_uri = os.getenv("MONGODB_URI")
        if mongodb_uri.startswith("mongodb://") or mongodb_uri.startswith("mongodb+srv://"):
            logger.info("✅ تنسيق MONGODB_URI صحيح")
        else:
            logger.warning("⚠️ تنسيق MONGODB_URI غير صحيح")
            logger.warning(f"التنسيق المتوقع: mongodb://user:pass@host:port/dbname أو mongodb+srv://user:pass@host/dbname")
    
    # إنشاء نموذج ملف .env
    example_env = """# Discord Bot settings
TOKEN=your_discord_bot_token_here
PREFIX=!
NODE_ENV=development

# MongoDB settings
MONGODB_URI=mongodb://localhost:27017
DB_NAME=discord_bot

# Web server settings
PORT=3000

# Logging
LOG_LEVEL=debug
"""
    logger.info("\nلإنشاء ملف .env، انسخ المحتوى التالي إلى ملف .env:")
    logger.info("-" * 40)
    logger.info(example_env)
    logger.info("-" * 40)
    
    return False

def check_config_dir():
    """التحقق من وجود مجلد config وملفاته"""
    config_dir = Path("python_bot") / "config"
    if not config_dir.exists() or not list(config_dir.glob("*.json")):
        logger.warning("⚠️ مجلد config فارغ أو غير موجود.")
        logger.info("سيتم إنشاء ملفات التكوين عند بدء تشغيل البوت.")
    return True

def main():
    """الدالة الرئيسية"""
    logger.info("=" * 50)
    logger.info("🤖 بدء تشغيل بوت ديسكورد")
    logger.info("=" * 50)
    
    # طباعة معلومات النظام
    logger.info(f"Python: {sys.version}")
    logger.info(f"المسار الحالي: {Path.cwd()}")
    logger.info(f"مسارات البحث: {sys.path}")
    
    # التحقق من الملفات المطلوبة
    check_env_file()
    check_config_dir()
    
    # إضافة مسار البوت إلى مسار البحث
    bot_path = str(Path("python_bot").absolute())
    if bot_path not in sys.path:
        sys.path.append(bot_path)
    
    # إظهار محتويات مجلد python_bot لأغراض تشخيصية
    python_bot_dir = Path("python_bot")
    if python_bot_dir.exists():
        logger.info("محتويات مجلد python_bot:")
        for item in python_bot_dir.iterdir():
            logger.info(f" - {item.name} {'[د]' if item.is_dir() else '[م]'}")
    else:
        logger.warning("⚠️ مجلد python_bot غير موجود!")
    
    # تشغيل البوت
    try:
        logger.info("🚀 جاري تشغيل البوت...")
        sys.path.insert(0, bot_path)
        
        # محاولة استيراد وحدة main
        try:
            from python_bot.src.main import main
            logger.info("✅ تم استيراد وحدة main بنجاح")
        except ImportError as e:
            logger.error(f"❌ فشل استيراد وحدة main: {str(e)}")
            
            # محاولة تشخيصية إضافية
            logger.info("جاري محاولة تشخيص المشكلة...")
            try:
                import importlib
                logger.info("محاولة استيراد جزء من الوحدة...")
                import python_bot
                logger.info("✅ تم استيراد حزمة python_bot")
                
                # فحص وجود ملف init في src
                src_init = Path("python_bot/src/__init__.py")
                if not src_init.exists():
                    logger.info("إنشاء ملف __init__.py في مجلد src")
                    src_init.write_text("# Package initialization\n")
                
                # محاولة أخرى
                from python_bot.src.main import main
                logger.info("✅ نجحت المحاولة الثانية للاستيراد")
            except Exception as e2:
                logger.error(f"❌ فشلت المحاولة الثانية: {str(e2)}")
                raise e
        
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️ تم إيقاف البوت بواسطة المستخدم.")
    except Exception as e:
        logger.error(f"\n❌ حدث خطأ أثناء تشغيل البوت: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 