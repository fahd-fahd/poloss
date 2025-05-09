#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إدارة إعدادات المستخدمين
تُستخدم لحفظ تفضيلات المستخدمين مثل اللغة المفضلة
"""

import os
import json
from pathlib import Path

# مسار ملف حفظ إعدادات المستخدمين
USER_SETTINGS_PATH = Path(__file__).parent.parent / "data" / "user_settings.json"

def ensure_directory_exists():
    """التأكد من وجود مجلد البيانات"""
    USER_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_user_settings():
    """
    تحميل إعدادات المستخدمين من الملف
    
    Returns:
        dict: قاموس يحتوي على إعدادات المستخدمين
    """
    ensure_directory_exists()
    
    try:
        if USER_SETTINGS_PATH.exists():
            with open(USER_SETTINGS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"خطأ في تحميل إعدادات المستخدمين: {str(e)}")
    
    return {"users": {}, "servers": {}}

def save_user_settings(settings):
    """
    حفظ إعدادات المستخدمين في الملف
    
    Args:
        settings (dict): قاموس يحتوي على إعدادات المستخدمين
    """
    ensure_directory_exists()
    
    try:
        with open(USER_SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"خطأ في حفظ إعدادات المستخدمين: {str(e)}")

# تحميل الإعدادات عند استيراد الوحدة
user_settings = load_user_settings()

def set_user_language(user_id, language, config):
    """
    تعيين لغة المستخدم المفضلة
    
    Args:
        user_id (int): معرف المستخدم
        language (str): اللغة المفضلة
        config (dict): قاموس التكوين
        
    Returns:
        bool: True إذا تم تعيين اللغة بنجاح
    """
    global user_settings
    
    supported_languages = config.get('prefix', {}).get('SUPPORTED_LANGUAGES', ['arabic', 'english'])
    
    if language not in supported_languages:
        return False
    
    user_id_str = str(user_id)  # تحويل المعرف إلى نص للاستخدام كمفتاح
    
    if user_id_str not in user_settings["users"]:
        user_settings["users"][user_id_str] = {}
    
    user_settings["users"][user_id_str]["language"] = language
    save_user_settings(user_settings)
    return True

def get_user_language(user_id, config):
    """
    الحصول على لغة المستخدم المفضلة
    
    Args:
        user_id (int): معرف المستخدم
        config (dict): قاموس التكوين
        
    Returns:
        str: اللغة المفضلة للمستخدم
    """
    user_id_str = str(user_id)
    
    if (user_id_str in user_settings["users"] and 
        "language" in user_settings["users"][user_id_str]):
        return user_settings["users"][user_id_str]["language"]
    
    return config.get('prefix', {}).get('DEFAULT_LANGUAGE', 'arabic')

def set_server_language(server_id, language, config):
    """
    تعيين لغة السيرفر الافتراضية
    
    Args:
        server_id (int): معرف السيرفر
        language (str): اللغة المفضلة
        config (dict): قاموس التكوين
        
    Returns:
        bool: True إذا تم تعيين اللغة بنجاح
    """
    global user_settings
    
    supported_languages = config.get('prefix', {}).get('SUPPORTED_LANGUAGES', ['arabic', 'english'])
    
    if language not in supported_languages:
        return False
    
    server_id_str = str(server_id)
    
    if server_id_str not in user_settings["servers"]:
        user_settings["servers"][server_id_str] = {}
    
    user_settings["servers"][server_id_str]["language"] = language
    save_user_settings(user_settings)
    return True

def get_server_language(server_id, config):
    """
    الحصول على لغة السيرفر الافتراضية
    
    Args:
        server_id (int): معرف السيرفر
        config (dict): قاموس التكوين
        
    Returns:
        str: اللغة الافتراضية للسيرفر
    """
    server_id_str = str(server_id)
    
    if (server_id_str in user_settings["servers"] and 
        "language" in user_settings["servers"][server_id_str]):
        return user_settings["servers"][server_id_str]["language"]
    
    return config.get('prefix', {}).get('DEFAULT_LANGUAGE', 'arabic')

def save_last_command(user_id, command):
    """
    حفظ آخر أمر استخدمه المستخدم للرجوع إليه
    
    Args:
        user_id (int): معرف المستخدم
        command (str): الأمر المستخدم
    """
    global user_settings
    
    user_id_str = str(user_id)
    
    if user_id_str not in user_settings["users"]:
        user_settings["users"][user_id_str] = {}
    
    if "commandHistory" not in user_settings["users"][user_id_str]:
        user_settings["users"][user_id_str]["commandHistory"] = []
    
    # إضافة الأمر للتاريخ مع الاحتفاظ بآخر 10 أوامر فقط
    user_settings["users"][user_id_str]["commandHistory"].insert(0, command)
    if len(user_settings["users"][user_id_str]["commandHistory"]) > 10:
        user_settings["users"][user_id_str]["commandHistory"].pop()
    
    save_user_settings(user_settings)

def get_last_command(user_id):
    """
    استرجاع آخر أمر استخدمه المستخدم
    
    Args:
        user_id (int): معرف المستخدم
        
    Returns:
        str: آخر أمر استخدمه المستخدم، أو None إذا لم يكن هناك أمر سابق
    """
    user_id_str = str(user_id)
    
    if (user_id_str in user_settings["users"] and 
        "commandHistory" in user_settings["users"][user_id_str] and 
        user_settings["users"][user_id_str]["commandHistory"]):
        return user_settings["users"][user_id_str]["commandHistory"][0]
    
    return None

def get_user_command_history(user_id):
    """
    استرجاع تاريخ أوامر المستخدم
    
    Args:
        user_id (int): معرف المستخدم
        
    Returns:
        list: قائمة بآخر الأوامر التي استخدمها المستخدم
    """
    user_id_str = str(user_id)
    
    if (user_id_str in user_settings["users"] and 
        "commandHistory" in user_settings["users"][user_id_str]):
        return user_settings["users"][user_id_str]["commandHistory"]
    
    return [] 