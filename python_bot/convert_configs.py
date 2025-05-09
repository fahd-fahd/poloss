#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import shutil
from pathlib import Path

def main():
    """
    تحويل ملفات التكوين من JavaScript إلى Python JSON
    """
    # مسارات المجلدات
    js_config_dir = Path('../config')  # مجلد config الأصلي في Node.js
    py_config_dir = Path('config')     # مجلد config في Python
    
    # التأكد من وجود مجلد التكوين في Python
    py_config_dir.mkdir(exist_ok=True)
    
    # التحقق من وجود مجلد التكوين في Node.js
    if not js_config_dir.exists():
        print(f"تحذير: مجلد التكوين الأصلي غير موجود: {js_config_dir}")
        return
    
    # تحويل كل ملف .js في مجلد التكوين
    converted_count = 0
    for js_file in js_config_dir.glob('*.js'):
        try:
            print(f"جاري تحويل الملف: {js_file.name}...")
            
            # قراءة محتويات ملف JavaScript
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # البحث عن الجزء بين module.exports = { و };
            match = re.search(r"module\.exports\s*=\s*{([\s\S]*?)};?\s*$", content)
            if not match:
                print(f"  لا يمكن تحويل {js_file.name}: لا يوجد صيغة module.exports")
                continue
            
            js_obj_str = match.group(1).strip()
            
            # استبدال القيم المنطقية
            js_obj_str = js_obj_str.replace("true", "True").replace("false", "False")
            
            # استبدال التعليقات
            js_obj_str = re.sub(r"//\s*(.*?)$", r"# \1", js_obj_str, flags=re.MULTILINE)
            
            # بناء القاموس
            obj_dict = {}
            
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
                    if current_key and current_value:
                        processed_value = process_value("\n".join(current_value))
                        obj_dict[current_key] = processed_value
                    
                    current_key = key_match.group(1)
                    value = key_match.group(2)
                    
                    # معالجة القيمة الحالية
                    processed_value = process_value(value)
                    obj_dict[current_key] = processed_value
                    current_value = []
                else:
                    if current_key:
                        current_value.append(line)
            
            # حفظ آخر مفتاح إذا كان هناك واحد
            if current_key and current_value:
                processed_value = process_value("\n".join(current_value))
                obj_dict[current_key] = processed_value
            
            # حفظ كملف JSON
            output_file = py_config_dir / f"{js_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(obj_dict, f, ensure_ascii=False, indent=2)
            
            print(f"  تم تحويل {js_file.name} إلى {output_file.name}")
            converted_count += 1
            
        except Exception as e:
            print(f"  خطأ في تحويل {js_file.name}: {str(e)}")
    
    print(f"\nتم تحويل {converted_count} ملف تكوين بنجاح.")

def process_value(value):
    """
    معالجة قيمة من سلسلة نصية JavaScript إلى قيمة Python مناسبة
    
    Args:
        value (str): القيمة المراد معالجتها
        
    Returns:
        object: القيمة المحولة (قد تكون نص، عدد، قائمة، إلخ)
    """
    value = value.strip()
    
    # القيم المنطقية
    if value == "True":
        return True
    elif value == "False":
        return False
    
    # المصفوفات (القوائم)
    if value.startswith("[") and value.endswith("]"):
        try:
            # محاولة تفسير القائمة
            array_str = value.replace("'", '"')  # استبدال الاقتباسات المفردة بمزدوجة
            # استبدال أي فواصل منسية في نهاية العناصر
            array_str = re.sub(r'\s*"\s*\n\s*', '", ', array_str)
            # الآن المحاولة مع json
            return json.loads(array_str)
        except:
            # إذا فشل، أعد القيمة كما هي
            return value
    
    # النصوص
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        return value[1:-1]  # إزالة الاقتباسات
    
    # محاولة تحويل إلى عدد
    try:
        if "." in value:
            return float(value)
        else:
            return int(value)
    except:
        # إرجاع النص كما هو
        return value

if __name__ == "__main__":
    main() 