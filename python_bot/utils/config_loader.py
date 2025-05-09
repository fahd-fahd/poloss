#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import yaml
from pathlib import Path

def create_config_dirs():
    """
    إنشاء مجلدات التكوين والسجلات إذا لم تكن موجودة
    """
    base_dir = Path(__file__).parent.parent
    
    # إنشاء المجلدات الأساسية
    dirs = [
        base_dir / "config",
        base_dir / "logs",
        base_dir / "data",
        base_dir / "commands" / "general",
        base_dir / "commands" / "bank",
        base_dir / "commands" / "admin",
        base_dir / "commands" / "games",
        base_dir / "commands" / "music",
        base_dir / "events"
    ]
    
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        
    print(f"تم إنشاء أو التحقق من وجود {len(dirs)} مجلد")

def load_config():
    """
    تحميل ملفات التكوين من مجلد config
    
    Returns:
        dict: قاموس يحتوي على جميع إعدادات التكوين
    """
    config = {}
    config_dir = Path(__file__).parent.parent / "config"
    
    # التحقق من وجود مجلد التكوين وإنشاؤه إذا لم يكن موجودًا
    create_config_dirs()
    
    # تحميل ملفات التكوين بامتداد json أو yaml أو yml
    for config_file in config_dir.glob("*.*"):
        if config_file.suffix not in [".json", ".yaml", ".yml"]:
            continue
        
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                if config_file.suffix == ".json":
                    file_config = json.load(f)
                else:  # yaml or yml
                    file_config = yaml.safe_load(f)
                
                # استخدام اسم الملف (بدون امتداد) كمفتاح في القاموس
                config[config_file.stem] = file_config
                print(f"تم تحميل ملف التكوين: {config_file.name}")
        except Exception as e:
            print(f"خطأ في تحميل ملف التكوين {config_file.name}: {str(e)}")
    
    return config

def save_config(config_name, config_data):
    """
    حفظ بيانات التكوين إلى ملف
    
    Args:
        config_name (str): اسم ملف التكوين (بدون امتداد)
        config_data (dict): البيانات المراد حفظها
    
    Returns:
        bool: True إذا تم الحفظ بنجاح، False في حالة الفشل
    """
    config_dir = Path(__file__).parent.parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    try:
        # حفظ بتنسيق JSON بشكل افتراضي
        config_file = config_dir / f"{config_name}.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        print(f"تم حفظ ملف التكوين: {config_file.name}")
        return True
    except Exception as e:
        print(f"خطأ في حفظ ملف التكوين {config_name}: {str(e)}")
        return False

def convert_js_to_py_config():
    """
    تحويل ملفات التكوين من JavaScript إلى Python
    """
    config_dir = Path(__file__).parent.parent.parent / "config"  # الوصول إلى مجلد config الأصلي
    py_config_dir = Path(__file__).parent.parent / "config"      # مجلد config في نسخة بايثون
    py_config_dir.mkdir(exist_ok=True)
    
    if not config_dir.exists():
        print(f"تحذير: مجلد التكوين الأصلي غير موجود: {config_dir}")
        return
    
    for js_file in config_dir.glob("*.js"):
        try:
            # قراءة محتويات ملف JavaScript
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # التحويل الأساسي
            # البحث عن الجزء بين module.exports = { و };
            import re
            match = re.search(r"module\.exports\s*=\s*{([\s\S]*?)};?\s*$", content)
            if not match:
                print(f"لا يمكن تحويل {js_file.name}: لا يوجد صيغة module.exports")
                continue
            
            js_obj_str = match.group(1).strip()
            
            # استبدال القيم المنطقية
            js_obj_str = js_obj_str.replace("true", "True").replace("false", "False")
            
            # استبدال التعليقات
            js_obj_str = re.sub(r"//\s*(.*?)$", r"# \1", js_obj_str, flags=re.MULTILINE)
            
            # بناء القاموس
            obj_dict = {}
            try:
                # محاولة تقييم الكود كـ Python dict مباشرة (قد لا تنجح دائماً)
                # تحتاج إلى معالجة إضافية للحالات المعقدة
                
                # تقسيم بواسطة الأسطر والبحث عن الأزواج الرئيسية-قيمية
                lines = js_obj_str.split('\n')
                current_key = None
                current_value = []
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # البحث عن زوج رئيسي-قيمي
                    key_match = re.match(r"([a-zA-Z0-9_]+)\s*:\s*(.*?),?\s*$", line)
                    if key_match:
                        # إذا كان هناك مفتاح سابق، احفظه
                        if current_key:
                            obj_dict[current_key] = "\n".join(current_value)
                        
                        current_key = key_match.group(1)
                        value = key_match.group(2)
                        
                        # معالجة القيم المختلفة
                        if value in ["True", "False"]:
                            obj_dict[current_key] = value == "True"
                        elif value.startswith("[") and value.endswith("]"):
                            # حاول تحويل المصفوفة
                            try:
                                array_str = value.replace("'", '"')  # استبدال الاقتباسات المفردة بمزدوجة
                                array_val = json.loads(array_str)
                                obj_dict[current_key] = array_val
                            except:
                                obj_dict[current_key] = value
                        elif value.startswith("'") and value.endswith("'"):
                            obj_dict[current_key] = value[1:-1]  # إزالة الاقتباسات
                        else:
                            obj_dict[current_key] = value
                        
                        current_value = []
                    else:
                        if current_key:
                            current_value.append(line)
                
                # حفظ آخر مفتاح إذا كان هناك واحد
                if current_key and current_value:
                    obj_dict[current_key] = "\n".join(current_value)
            except Exception as e:
                print(f"خطأ في تحليل {js_file.name}: {str(e)}")
                continue
            
            # حفظ كملف JSON
            output_file = py_config_dir / f"{js_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(obj_dict, f, ensure_ascii=False, indent=2)
            
            print(f"تم تحويل {js_file.name} إلى {output_file.name}")
        
        except Exception as e:
            print(f"خطأ في تحويل {js_file.name}: {str(e)}")

# للاختبار المباشر
if __name__ == "__main__":
    # إنشاء المجلدات اللازمة
    create_config_dirs()
    
    # تحويل ملفات التكوين الموجودة
    convert_js_to_py_config()
    
    # تحميل التكوين
    config = load_config()
    print(f"تم تحميل {len(config)} ملف تكوين") 