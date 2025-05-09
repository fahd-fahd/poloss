from flask import Flask, jsonify, render_template
import os
import threading
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# إضافة المسار الحالي إلى مسار البحث ليتمكن من العثور على الحزم
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# تحميل متغيرات البيئة
load_dotenv()

# إنشاء تطبيق Flask
app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# متغيرات حالة البوت
bot_status = {
    "status": "starting",
    "uptime": 0,
    "users_served": 0,
    "commands_processed": 0,
    "last_error": None
}

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return jsonify({
        "name": "بوت ديسكورد",
        "status": bot_status["status"],
        "uptime": bot_status["uptime"],
        "environment": os.getenv("NODE_ENV", "development")
    })

@app.route('/health')
def health():
    """نقطة نهاية للتحقق من صحة البوت"""
    return jsonify({
        "status": "healthy" if bot_status["status"] == "running" else "unhealthy",
        "details": bot_status
    })

@app.route('/stats')
def stats():
    """إحصائيات البوت"""
    return jsonify({
        "users_served": bot_status["users_served"],
        "commands_processed": bot_status["commands_processed"],
        "uptime": bot_status["uptime"]
    })

def run_bot():
    """تشغيل البوت في خيط منفصل"""
    try:
        # تغيير حالة البوت
        bot_status["status"] = "starting"
        
        # استيراد وتشغيل البوت
        import sys
        from pathlib import Path
        
        # إضافة مسار البوت إلى مسار البحث
        bot_path = str(Path("python_bot").absolute())
        if bot_path not in sys.path:
            sys.path.append(bot_path)
        
        # طباعة مسارات البحث للتشخيص
        logger.info(f"مسارات البحث: {sys.path}")
        
        # محاولة استيراد واختبار وجود المكتبات
        try:
            # محاولة استيراد الملف المطلوب مباشرة
            import python_bot.src.main as bot_main
            logger.info("تم استيراد main.py بنجاح")
        except ImportError as e:
            logger.error(f"خطأ استيراد: {str(e)}")
            
            # محاولة بديلة باستخدام الاستيراد الديناميكي
            try:
                import importlib.util
                main_path = os.path.join(bot_path, "src", "main.py")
                logger.info(f"محاولة تحميل: {main_path}")
                
                if os.path.exists(main_path):
                    spec = importlib.util.spec_from_file_location("main", main_path)
                    bot_main = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(bot_main)
                    logger.info("تم تحميل main.py بطريقة بديلة")
                else:
                    logger.error(f"الملف غير موجود: {main_path}")
                    raise FileNotFoundError(f"الملف غير موجود: {main_path}")
            except Exception as e2:
                logger.error(f"فشل التحميل البديل: {str(e2)}")
                bot_status["status"] = "error"
                bot_status["last_error"] = f"فشل تحميل الوحدات: {str(e)} | {str(e2)}"
                return
                
        import asyncio
        
        # تغيير حالة البوت
        bot_status["status"] = "running"
        
        # تشغيل البوت
        if hasattr(bot_main, 'main'):
            asyncio.run(bot_main.main())
        else:
            logger.error("لم يتم العثور على دالة main()")
            bot_status["status"] = "error"
            bot_status["last_error"] = "لم يتم العثور على دالة main()"
            
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تشغيل البوت: {str(e)}")
        bot_status["status"] = "error"
        bot_status["last_error"] = str(e)
        import traceback
        logger.error(traceback.format_exc())

def start_bot_thread():
    """بدء خيط البوت"""
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("تم بدء خيط البوت")

if __name__ == "__main__":
    # تشغيل البوت في خيط منفصل
    start_bot_thread()
    
    # تشغيل خادم الويب
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
else:
    # عند استخدام WSGI، قم بتشغيل البوت في خيط منفصل
    start_bot_thread() 