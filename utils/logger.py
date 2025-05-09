#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import datetime
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(name='bot', log_level=logging.INFO):
    """
    إعداد مسجل أحداث مع تدوير الملفات
    
    المعلمات:
        name (str): اسم المسجل
        log_level (int): مستوى التسجيل
    
    Returns:
        Logger: كائن المسجل
    """
    # إنشاء مجلد السجلات إذا لم يكن موجودًا
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # إنشاء ملف السجل مع تاريخ اليوم
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'{name}_{today}.log')
    
    # إعداد المسجل
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # إزالة جميع المعالجات الموجودة لتجنب التكرار
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # إضافة معالج لتدوير الملفات
    file_handler = RotatingFileHandler(
        filename=log_file,
        encoding='utf-8',
        maxBytes=10 * 1024 * 1024,  # 10 ميجابايت
        backupCount=5
    )
    
    # إضافة معالج للطباعة في وحدة التحكم
    console_handler = logging.StreamHandler(sys.stdout)
    
    # تنسيق السجل
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)
    
    # إضافة المعالجات إلى المسجل
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name='bot'):
    """
    الحصول على مسجل موجود أو إنشاء واحد جديد
    
    المعلمات:
        name (str): اسم المسجل
    
    Returns:
        Logger: كائن المسجل
    """
    logger = logging.getLogger(name)
    
    # إذا لم يكن هناك معالجات، قم بإعداد المسجل
    if not logger.handlers:
        logger = setup_logger(name)
    
    return logger

class CustomAdapter(logging.LoggerAdapter):
    """
    محول مخصص للمسجل لإضافة سياق إضافي
    """
    def __init__(self, logger, prefix=''):
        super().__init__(logger, {})
        self.prefix = prefix
    
    def process(self, msg, kwargs):
        return f'{self.prefix}{msg}', kwargs

def get_custom_logger(name='bot', prefix=''):
    """
    الحصول على مسجل مخصص مع بادئة
    
    المعلمات:
        name (str): اسم المسجل
        prefix (str): بادئة لإضافتها إلى كل رسالة
    
    Returns:
        LoggerAdapter: محول المسجل
    """
    logger = get_logger(name)
    return CustomAdapter(logger, prefix)

# دالة مساعدة لتسجيل الأخطاء
def log_error(error, context=None, logger_name='bot'):
    """
    تسجيل خطأ مع السياق
    
    المعلمات:
        error (Exception): الاستثناء الذي حدث
        context (dict): سياق إضافي
        logger_name (str): اسم المسجل
    """
    logger = get_logger(logger_name)
    
    error_message = f"ERROR: {str(error)}"
    if context:
        error_message += f" | CONTEXT: {context}"
    
    logger.error(error_message, exc_info=True)
    
    return logger

# للاختبار المباشر
if __name__ == "__main__":
    logger = setup_logger()
    logger.debug("رسالة تصحيح")
    logger.info("رسالة معلومات")
    logger.warning("رسالة تحذير")
    logger.error("رسالة خطأ")
    logger.critical("رسالة خطأ حرجة") 