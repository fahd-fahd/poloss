#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة مساعدة للترجمة وتعدد اللغات في البوت
تسمح هذه الوحدة بترجمة نصوص البوت بين العربية والإنجليزية
"""

import json
import os
from pathlib import Path

# مسار ملفات الترجمة
TRANSLATIONS_DIR = Path(__file__).parent.parent / "data" / "translations"

# التأكد من وجود مجلد الترجمات
def ensure_translations_dir():
    """التأكد من وجود مجلد الترجمات"""
    TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)
    return True

# الحصول على لغة المستخدم
def get_user_language(bot, user_id):
    """
    الحصول على لغة المستخدم المحددة
    
    Args:
        bot: كائن البوت
        user_id: معرف المستخدم
        
    Returns:
        str: رمز اللغة ('ar' للعربية، 'en' للإنجليزية)
    """
    # محاولة الوصول إلى إعدادات اللغة
    try:
        # استيراد الدالة من وحدة اللغة
        from commands.general.language import get_user_language as get_lang
        return get_lang(user_id)
    except ImportError:
        # في حالة عدم وجود وحدة اللغة، استخدم العربية كلغة افتراضية
        return "ar"

# نصوص الترجمة الأساسية
DEFAULT_TRANSLATIONS = {
    # نصوص عامة
    "general": {
        "error": {
            "ar": "خطأ",
            "en": "Error"
        },
        "success": {
            "ar": "نجاح",
            "en": "Success"
        },
        "cancel": {
            "ar": "إلغاء",
            "en": "Cancel"
        },
        "confirm": {
            "ar": "تأكيد",
            "en": "Confirm"
        },
        "yes": {
            "ar": "نعم",
            "en": "Yes"
        },
        "no": {
            "ar": "لا",
            "en": "No"
        },
        "loading": {
            "ar": "جاري التحميل...",
            "en": "Loading..."
        },
        "not_found": {
            "ar": "غير موجود",
            "en": "Not found"
        }
    },
    
    # نصوص الألعاب
    "games": {
        "bet": {
            "ar": "رهان",
            "en": "Bet"
        },
        "win": {
            "ar": "فوز",
            "en": "Win"
        },
        "lose": {
            "ar": "خسارة",
            "en": "Loss"
        },
        "draw": {
            "ar": "تعادل",
            "en": "Draw"
        },
        "insufficient_balance": {
            "ar": "رصيد غير كافٍ",
            "en": "Insufficient balance"
        },
        "bet_amount": {
            "ar": "قيمة الرهان",
            "en": "Bet amount"
        },
        "invalid_bet": {
            "ar": "رهان غير صالح",
            "en": "Invalid bet"
        }
    },
    
    # نصوص البنك
    "bank": {
        "balance": {
            "ar": "الرصيد",
            "en": "Balance"
        },
        "transfer": {
            "ar": "تحويل",
            "en": "Transfer"
        },
        "deposit": {
            "ar": "إيداع",
            "en": "Deposit"
        },
        "withdraw": {
            "ar": "سحب",
            "en": "Withdraw"
        },
        "transaction": {
            "ar": "معاملة",
            "en": "Transaction"
        },
        "daily": {
            "ar": "المكافأة اليومية",
            "en": "Daily Reward"
        }
    },
    
    # نصوص الموسيقى
    "music": {
        "now_playing": {
            "ar": "يتم الآن تشغيل",
            "en": "Now Playing"
        },
        "queue": {
            "ar": "قائمة الانتظار",
            "en": "Queue"
        },
        "skip": {
            "ar": "تخطي",
            "en": "Skip"
        },
        "pause": {
            "ar": "إيقاف مؤقت",
            "en": "Pause"
        },
        "resume": {
            "ar": "استئناف",
            "en": "Resume"
        },
        "stop": {
            "ar": "إيقاف",
            "en": "Stop"
        },
        "volume": {
            "ar": "مستوى الصوت",
            "en": "Volume"
        }
    },
    
    # نصوص الإدارة
    "admin": {
        "kick": {
            "ar": "طرد",
            "en": "Kick"
        },
        "ban": {
            "ar": "حظر",
            "en": "Ban"
        },
        "mute": {
            "ar": "كتم",
            "en": "Mute"
        },
        "unmute": {
            "ar": "إلغاء الكتم",
            "en": "Unmute"
        },
        "clear": {
            "ar": "مسح",
            "en": "Clear"
        }
    }
}

# تحميل ملف الترجمة
def load_translations():
    """
    تحميل ملفات الترجمة
    
    Returns:
        dict: قاموس يحتوي على جميع النصوص المترجمة
    """
    ensure_translations_dir()
    
    # مسار ملف الترجمة الرئيسي
    trans_file = TRANSLATIONS_DIR / "translations.json"
    
    # إذا كان الملف موجوداً، قم بتحميله
    if trans_file.exists():
        try:
            with open(trans_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"خطأ في تحميل ملف الترجمة: {str(e)}")
    
    # إذا لم يكن الملف موجوداً، قم بإنشائه
    try:
        with open(trans_file, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_TRANSLATIONS, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في إنشاء ملف الترجمة: {str(e)}")
    
    return DEFAULT_TRANSLATIONS

# الحصول على نص مترجم
def get_text(key, language="ar"):
    """
    الحصول على نص مترجم حسب المفتاح واللغة
    
    Args:
        key (str): مفتاح النص في صيغة "مجموعة.مفتاح" (مثل "general.error")
        language (str): رمز اللغة ('ar' للعربية، 'en' للإنجليزية)
        
    Returns:
        str: النص المترجم
    """
    translations = load_translations()
    
    # تقسيم المفتاح إلى مستويات (مثل "general.error" إلى ["general", "error"])
    key_parts = key.split(".")
    
    # البحث في قاموس الترجمة
    current_level = translations
    for part in key_parts:
        if part in current_level:
            current_level = current_level[part]
        else:
            # إذا لم يتم العثور على المفتاح، أعد المفتاح نفسه
            return key
    
    # الحصول على النص المترجم باللغة المطلوبة
    if isinstance(current_level, dict) and language in current_level:
        return current_level[language]
    elif isinstance(current_level, dict) and "ar" in current_level:
        # إذا لم تكن اللغة المطلوبة متوفرة، استخدم اللغة العربية كاحتياطي
        return current_level["ar"]
    else:
        # إذا لم يتم العثور على ترجمة، أعد المفتاح نفسه
        return key

# ترجمة رسالة كاملة
def translate_message(message, language="ar"):
    """
    ترجمة رسالة كاملة تحتوي على مفاتيح ترجمة بالصيغة {key}
    
    Args:
        message (str): الرسالة التي تحتوي على مفاتيح ترجمة
        language (str): رمز اللغة ('ar' للعربية، 'en' للإنجليزية)
        
    Returns:
        str: الرسالة المترجمة
    """
    # البحث عن جميع المفاتيح في الرسالة بين {}
    import re
    keys = re.findall(r'\{([^}]+)\}', message)
    
    # استبدال كل مفتاح بالنص المترجم
    result = message
    for key in keys:
        result = result.replace(f"{{{key}}}", get_text(key, language))
    
    return result

# دالة مختصرة للترجمة
def t(key, language="ar"):
    """
    دالة مختصرة للحصول على نص مترجم
    
    Args:
        key (str): مفتاح النص
        language (str): رمز اللغة
        
    Returns:
        str: النص المترجم
    """
    return get_text(key, language)

# إضافة ترجمة جديدة
def add_translation(group, key, ar_text, en_text):
    """
    إضافة ترجمة جديدة إلى ملف الترجمة
    
    Args:
        group (str): مجموعة الترجمة (مثل "general")
        key (str): مفتاح الترجمة
        ar_text (str): النص العربي
        en_text (str): النص الإنجليزي
        
    Returns:
        bool: نجاح العملية
    """
    translations = load_translations()
    
    # التأكد من وجود المجموعة
    if group not in translations:
        translations[group] = {}
    
    # إضافة النص المترجم
    translations[group][key] = {
        "ar": ar_text,
        "en": en_text
    }
    
    # حفظ التغييرات
    try:
        with open(TRANSLATIONS_DIR / "translations.json", "w", encoding="utf-8") as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"خطأ في حفظ ملف الترجمة: {str(e)}")
        return False 