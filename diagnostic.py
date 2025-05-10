#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت تشخيصي للتحقق من متغيرات البيئة والاتصال بقاعدة البيانات
"""

import os
import sys
import json
import logging
from pathlib import Path
import traceback

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("diagnostics")

# محاولة تحميل ملف .env يدويًا
def load_dotenv_file():
    """تحميل ملف .env يدويًا"""
    logger.info("محاولة تحميل ملف .env يدويًا...")
    env_path = Path(".env")
    
    if not env_path.exists():
        logger.error("❌ ملف .env غير موجود")
        return False
    
    try:
        # محاولة استيراد المكتبة
        try:
            from dotenv import load_dotenv
            logger.info("✅ تم استيراد مكتبة dotenv بنجاح")
        except ImportError:
            logger.error("❌ فشل استيراد مكتبة dotenv")
            logger.info("محاولة تثبيت المكتبة...")
            os.system("pip install python-dotenv")
            from dotenv import load_dotenv
            logger.info("✅ تم تثبيت واستيراد مكتبة dotenv بنجاح")
        
        # تحميل الملف
        load_dotenv(env_path)
        logger.info("✅ تم تحميل ملف .env بنجاح")
        
        # طريقة بديلة لتحميل الملف يدويًا
        logger.info("محاولة تحميل ملف .env يدويًا كنسخة احتياطية...")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key, value = line.split('=', 1)
                os.environ[key] = value
        logger.info("✅ تم تحميل ملف .env يدويًا بنجاح")
        
        return True
    except Exception as e:
        logger.error(f"❌ خطأ أثناء تحميل ملف .env: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def check_env_variables():
    """التحقق من متغيرات البيئة الرئيسية"""
    logger.info("فحص متغيرات البيئة:")
    
    # قائمة المتغيرات المهمة
    important_vars = [
        "TOKEN", "MONGODB_URI", "PREFIX", "DB_NAME", 
        "NODE_ENV", "PORT", "LOG_LEVEL"
    ]
    
    # فحص كل متغير
    results = {}
    for var in important_vars:
        value = os.getenv(var)
        if value:
            # إخفاء قيم المتغيرات الحساسة
            if var in ["TOKEN", "MONGODB_URI"]:
                masked_value = value[:5] + "..." if len(value) > 8 else "***"
                results[var] = f"✅ موجود ({masked_value})"
            else:
                results[var] = f"✅ موجود ({value})"
        else:
            results[var] = "❌ غير موجود"
    
    # عرض النتائج
    for var, status in results.items():
        logger.info(f"{var}: {status}")
    
    return all(value.startswith("✅") for value in results.values())

def test_mongodb_connection():
    """محاولة الاتصال بقاعدة البيانات MongoDB"""
    logger.info("محاولة الاتصال بقاعدة البيانات MongoDB:")
    
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        logger.error("❌ MONGODB_URI غير موجود")
        return False
    
    try:
        # محاولة استيراد المكتبة
        try:
            import motor.motor_asyncio
            logger.info("✅ تم استيراد مكتبة motor بنجاح")
        except ImportError:
            logger.error("❌ فشل استيراد مكتبة motor")
            logger.info("محاولة تثبيت المكتبة...")
            os.system("pip install motor")
            import motor.motor_asyncio
            logger.info("✅ تم تثبيت واستيراد مكتبة motor بنجاح")
        
        # استيراد asyncio
        import asyncio
        
        # محاولة الاتصال
        async def test_connection():
            try:
                # إنشاء اتصال MongoDB
                client = motor.motor_asyncio.AsyncIOMotorClient(
                    mongodb_uri,
                    serverSelectionTimeoutMS=5000
                )
                
                # محاولة الاتصال والتحقق
                await client.server_info()
                
                # الحصول على اسم قاعدة البيانات
                db_name = os.getenv("DB_NAME", "discord_bot")
                db = client[db_name]
                
                # محاولة قراءة أسماء المجموعات
                collections = await db.list_collection_names()
                logger.info(f"✅ تم الاتصال بنجاح بقاعدة البيانات: {db_name}")
                logger.info(f"المجموعات المتاحة: {collections}")
                return True
            except Exception as e:
                logger.error(f"❌ فشل الاتصال بقاعدة البيانات: {str(e)}")
                logger.error(traceback.format_exc())
                return False
        
        # تشغيل الاختبار
        result = asyncio.run(test_connection())
        return result
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_discord_connection():
    """محاولة التحقق من توكن Discord"""
    logger.info("محاولة التحقق من توكن Discord:")
    
    token = os.getenv("TOKEN")
    if not token:
        logger.error("❌ TOKEN غير موجود")
        return False
    
    try:
        # محاولة استيراد المكتبة
        try:
            import discord
            logger.info("✅ تم استيراد مكتبة discord بنجاح")
        except ImportError:
            logger.error("❌ فشل استيراد مكتبة discord")
            logger.info("محاولة تثبيت المكتبة...")
            os.system("pip install discord.py")
            import discord
            logger.info("✅ تم تثبيت واستيراد مكتبة discord بنجاح")
        
        # استيراد asyncio
        import asyncio
        
        # محاولة التحقق من التوكن
        async def test_token():
            try:
                # إنشاء عميل Discord
                client = discord.Client(intents=discord.Intents.default())
                
                # محاولة تسجيل الدخول
                try:
                    await client.login(token)
                    logger.info("✅ تم التحقق من توكن Discord بنجاح")
                    await client.close()
                    return True
                except discord.LoginFailure:
                    logger.error("❌ توكن Discord غير صالح")
                    return False
                except Exception as e:
                    logger.error(f"❌ خطأ أثناء محاولة تسجيل الدخول: {str(e)}")
                    return False
            except Exception as e:
                logger.error(f"❌ خطأ غير متوقع: {str(e)}")
                logger.error(traceback.format_exc())
                return False
        
        # تشغيل الاختبار
        result = asyncio.run(test_token())
        return result
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def check_file_structure():
    """التحقق من هيكل الملفات"""
    logger.info("فحص هيكل الملفات:")
    
    # قائمة الملفات والمجلدات المهمة
    important_files = [
        "app.py", "run.py", "Procfile", "requirements.txt",
        "python_bot/src/main.py", "python_bot/__init__.py", 
        "python_bot/src/__init__.py", "python_bot/utils/__init__.py"
    ]
    
    # فحص كل ملف
    results = {}
    for file_path in important_files:
        path = Path(file_path)
        if path.exists():
            results[file_path] = "✅ موجود"
        else:
            results[file_path] = "❌ غير موجود"
    
    # عرض النتائج
    for file_path, status in results.items():
        logger.info(f"{file_path}: {status}")
    
    return all(value.startswith("✅") for value in results.values())

def main():
    """الدالة الرئيسية"""
    logger.info("=" * 50)
    logger.info("🔍 بدء التشخيص")
    logger.info("=" * 50)
    
    # محاولة تحميل ملف .env
    load_dotenv_file()
    
    # فحص متغيرات البيئة
    env_ok = check_env_variables()
    logger.info(f"نتيجة فحص متغيرات البيئة: {'✅ ناجح' if env_ok else '❌ فاشل'}")
    
    # فحص هيكل الملفات
    files_ok = check_file_structure()
    logger.info(f"نتيجة فحص هيكل الملفات: {'✅ ناجح' if files_ok else '❌ فاشل'}")
    
    # محاولة الاتصال بقاعدة البيانات
    mongodb_ok = test_mongodb_connection()
    logger.info(f"نتيجة الاتصال بقاعدة البيانات: {'✅ ناجح' if mongodb_ok else '❌ فاشل'}")
    
    # محاولة التحقق من توكن Discord
    discord_ok = test_discord_connection()
    logger.info(f"نتيجة التحقق من توكن Discord: {'✅ ناجح' if discord_ok else '❌ فاشل'}")
    
    # عرض محتوى ملف .env بدون القيم الحساسة
    logger.info("=" * 50)
    logger.info("محتوى ملف .env (بدون القيم الحساسة):")
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    logger.info(line)
                    continue
                try:
                    key, value = line.split('=', 1)
                    if key in ["TOKEN", "MONGODB_URI"]:
                        masked_value = value[:5] + "..." if len(value) > 8 else "***"
                        logger.info(f"{key}={masked_value}")
                    else:
                        logger.info(line)
                except Exception:
                    logger.info(line)
    else:
        logger.info("❌ ملف .env غير موجود")
    
    # النتيجة الإجمالية
    overall = env_ok and files_ok and mongodb_ok and discord_ok
    logger.info("=" * 50)
    logger.info(f"النتيجة الإجمالية: {'✅ كل الفحوصات ناجحة' if overall else '❌ بعض الفحوصات فشلت'}")
    logger.info("=" * 50)

if __name__ == "__main__":
    main() 