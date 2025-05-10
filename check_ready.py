#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت للتحقق من جاهزية المشروع للنشر على Render
"""

import os
import sys
import logging
from pathlib import Path
import traceback
import importlib.util
import json

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("check-ready")

def check_files_existence():
    """التحقق من وجود الملفات الضرورية"""
    logger.info("فحص وجود الملفات الضرورية:")
    
    required_files = [
        "app.py", "run.py", "Procfile", "requirements.txt", "render.yaml",
        "python_bot/__init__.py", "python_bot/src/__init__.py", "python_bot/src/main.py",
        ".env"
    ]
    
    status = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            logger.info(f"✅ {file_path}: موجود")
        else:
            logger.error(f"❌ {file_path}: غير موجود")
            status = False
    
    return status

def check_render_yaml():
    """التحقق من صحة ملف render.yaml"""
    logger.info("فحص صحة ملف render.yaml:")
    
    render_path = Path("render.yaml")
    if not render_path.exists():
        logger.error("❌ ملف render.yaml غير موجود")
        return False
    
    try:
        with open(render_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # تحقق من وجود الإعدادات الضرورية
        checks = {
            "services": "services:" in content,
            "type: web": "type: web" in content,
            "env: python": "env: python" in content,
            "buildCommand": "buildCommand:" in content,
            "startCommand": "startCommand:" in content,
            "gunicorn": "gunicorn" in content,
            "app:app": "app:app" in content,
            "TOKEN": "TOKEN" in content,
            "MONGODB_URI": "MONGODB_URI" in content
        }
        
        status = True
        for name, check in checks.items():
            if check:
                logger.info(f"✅ {name}: موجود")
            else:
                logger.error(f"❌ {name}: غير موجود")
                status = False
        
        return status
    except Exception as e:
        logger.error(f"❌ خطأ أثناء فحص ملف render.yaml: {str(e)}")
        return False

def check_procfile():
    """التحقق من صحة ملف Procfile"""
    logger.info("فحص صحة ملف Procfile:")
    
    procfile_path = Path("Procfile")
    if not procfile_path.exists():
        logger.error("❌ ملف Procfile غير موجود")
        return False
    
    try:
        with open(procfile_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        expected_content = "web: gunicorn app:app"
        if content == expected_content:
            logger.info(f"✅ محتوى Procfile صحيح: {content}")
            return True
        else:
            logger.error(f"❌ محتوى Procfile غير صحيح: {content}")
            logger.error(f"   المحتوى المتوقع: {expected_content}")
            return False
    except Exception as e:
        logger.error(f"❌ خطأ أثناء فحص ملف Procfile: {str(e)}")
        return False

def check_requirements():
    """التحقق من وجود جميع المتطلبات"""
    logger.info("فحص ملف requirements.txt:")
    
    req_path = Path("requirements.txt")
    if not req_path.exists():
        logger.error("❌ ملف requirements.txt غير موجود")
        return False
    
    try:
        with open(req_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # التحقق من وجود المتطلبات الأساسية
        required_packages = [
            "discord.py", "flask", "python-dotenv", "motor", "gunicorn", 
            "wavelink==2.6.5", "PyNaCl"
        ]
        
        status = True
        for package in required_packages:
            base_package = package.split("==")[0] if "==" in package else package
            if base_package in content:
                logger.info(f"✅ {package}: موجود")
            else:
                logger.error(f"❌ {package}: غير موجود")
                status = False
        
        return status
    except Exception as e:
        logger.error(f"❌ خطأ أثناء فحص ملف requirements.txt: {str(e)}")
        return False

def load_and_check_env():
    """تحميل وفحص متغيرات البيئة"""
    logger.info("تحميل وفحص متغيرات البيئة:")
    
    try:
        # محاولة استيراد python-dotenv
        try:
            from dotenv import load_dotenv
            logger.info("✅ تم استيراد مكتبة dotenv بنجاح")
        except ImportError:
            logger.error("❌ فشل استيراد مكتبة dotenv")
            logger.info("محاولة تثبيت المكتبة...")
            os.system("pip install python-dotenv")
            from dotenv import load_dotenv
            logger.info("✅ تم تثبيت واستيراد مكتبة dotenv بنجاح")
        
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("✅ تم تحميل ملف .env بنجاح")
        else:
            logger.warning("⚠️ ملف .env غير موجود")
        
        # التحقق من متغيرات البيئة الضرورية
        required_env = ["TOKEN", "MONGODB_URI", "PREFIX", "DB_NAME"]
        status = True
        for env_var in required_env:
            value = os.getenv(env_var)
            if value:
                if env_var in ["TOKEN", "MONGODB_URI"]:
                    masked_value = value[:5] + "..." if len(value) > 8 else "***"
                    logger.info(f"✅ {env_var}: {masked_value}")
                else:
                    logger.info(f"✅ {env_var}: {value}")
            else:
                logger.error(f"❌ {env_var} غير موجود")
                status = False
        
        return status
    except Exception as e:
        logger.error(f"❌ خطأ أثناء فحص متغيرات البيئة: {str(e)}")
        return False

def check_imports():
    """التحقق من إمكانية استيراد المكتبات الضرورية"""
    logger.info("فحص إمكانية استيراد المكتبات الضرورية:")
    
    required_modules = {
        "flask": "flask",
        "dotenv": "dotenv",
        "discord": "discord",
        "motor": "motor",
        "asyncio": "asyncio",
        "logging": "logging",
        "yaml": "yaml",
        "json": "json"
    }
    
    all_success = True
    
    # فحص مكتبة Flask
    try:
        import flask
        logger.info("✅ flask: تم استيراده بنجاح")
    except ImportError:
        logger.error("❌ flask: فشل استيراده")
        all_success = False
    
    # فحص مكتبة dotenv
    try:
        from dotenv import load_dotenv
        logger.info("✅ dotenv: تم استيراده بنجاح")
    except ImportError:
        logger.error("❌ dotenv: فشل استيراده")
        all_success = False
    
    # فحص مكتبة discord
    try:
        import discord
        logger.info("✅ discord: تم استيراده بنجاح")
    except ImportError:
        logger.error("❌ discord: فشل استيراده")
        all_success = False
    
    # فحص مكتبة motor
    try:
        import motor
        logger.info("✅ motor: تم استيراده بنجاح")
    except ImportError:
        logger.error("❌ motor: فشل استيراده")
        all_success = False
    
    # فحص مكتبة asyncio
    try:
        import asyncio
        logger.info("✅ asyncio: تم استيراده بنجاح")
    except ImportError:
        logger.error("❌ asyncio: فشل استيراده")
        all_success = False
    
    # فحص مكتبة yaml
    try:
        import yaml
        logger.info("✅ yaml: تم استيراده بنجاح")
    except ImportError:
        logger.error("❌ yaml: فشل استيراده")
        all_success = False
    
    # فحص json
    try:
        import json
        logger.info("✅ json: تم استيراده بنجاح")
    except ImportError:
        logger.error("❌ json: فشل استيراده")
        all_success = False
    
    return all_success

def main():
    """الدالة الرئيسية"""
    logger.info("=" * 50)
    logger.info("🔍 فحص جاهزية المشروع للنشر على Render")
    logger.info("=" * 50)
    
    # إجراء الفحوصات
    files_check = check_files_existence()
    render_check = check_render_yaml()
    procfile_check = check_procfile()
    requirements_check = check_requirements()
    env_check = load_and_check_env()
    imports_check = check_imports()
    
    # تجميع النتائج
    checks = {
        "وجود الملفات": files_check,
        "صحة ملف render.yaml": render_check,
        "صحة ملف Procfile": procfile_check,
        "متطلبات المشروع": requirements_check,
        "متغيرات البيئة": env_check,
        "استيراد المكتبات": imports_check
    }
    
    # طباعة ملخص النتائج
    logger.info("=" * 50)
    logger.info("ملخص النتائج:")
    overall_status = True
    for name, status in checks.items():
        if status:
            logger.info(f"✅ {name}: ناجح")
        else:
            logger.error(f"❌ {name}: فاشل")
            overall_status = False
    
    logger.info("=" * 50)
    if overall_status:
        logger.info("✅ المشروع جاهز للنشر على Render!")
    else:
        logger.error("❌ يجب إصلاح المشاكل المذكورة أعلاه قبل النشر")
    logger.info("=" * 50)

if __name__ == "__main__":
    main() 