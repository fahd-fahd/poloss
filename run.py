#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت تشغيل بوت ديسكورد
يوفر طريقة سهلة لتشغيل البوت مع التعامل مع الأخطاء الأساسية
"""

import os
import sys
from pathlib import Path

# التأكد من وجود Python 3.8+
if sys.version_info < (3, 8):
    print("خطأ: هذا البوت يتطلب Python 3.8 أو أحدث.")
    print(f"الإصدار الحالي: Python {sys.version}")
    sys.exit(1)

try:
    # التحقق من تثبيت المكتبات الأساسية
    import discord
    import motor
    import dotenv
    import flask
    import colorlog
    
    print(f"✅ تم التحقق من المكتبات الأساسية")
except ImportError as e:
    print(f"❌ خطأ: لم يتم تثبيت جميع المكتبات المطلوبة.")
    print(f"المكتبة المفقودة: {str(e)}")
    print("قم بتثبيت المكتبات المطلوبة باستخدام:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def check_env_file():
    """التحقق من وجود ملف .env"""
    env_path = Path(".") / ".env"
    if not env_path.exists():
        print("⚠️ تحذير: ملف .env غير موجود.")
        
        # التحقق مما إذا كان TOKEN متوفرًا في متغيرات البيئة
        if not os.getenv("TOKEN"):
            print("⚠️ تحذير: لم يتم تعيين TOKEN في متغيرات البيئة.")
            print("سيعمل البوت في وضع خادم الويب فقط.")
        
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
        print("\nلإنشاء ملف .env، انسخ المحتوى التالي إلى ملف .env:")
        print("-" * 40)
        print(example_env)
        print("-" * 40)
        
        return False
    return True

def check_config_dir():
    """التحقق من وجود مجلد config وملفاته"""
    config_dir = Path("python_bot") / "config"
    if not config_dir.exists() or not list(config_dir.glob("*.json")):
        print("⚠️ تحذير: مجلد config فارغ أو غير موجود.")
        print("سيتم إنشاء ملفات التكوين عند بدء تشغيل البوت.")
    return True

def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("🤖 بدء تشغيل بوت ديسكورد")
    print("=" * 50)
    
    # التحقق من الملفات المطلوبة
    check_env_file()
    check_config_dir()
    
    # إضافة مسار البوت إلى مسار البحث
    bot_path = str(Path("python_bot").absolute())
    if bot_path not in sys.path:
        sys.path.append(bot_path)
    
    # تشغيل البوت
    try:
        print("🚀 جاري تشغيل البوت...")
        sys.path.insert(0, bot_path)
        from python_bot.src.main import main
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف البوت بواسطة المستخدم.")
    except Exception as e:
        print(f"\n❌ حدث خطأ أثناء تشغيل البوت: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 