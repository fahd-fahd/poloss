from flask import Flask, jsonify, render_template
import os
import threading
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# إعداد التسجيل بشكل مبكر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# إضافة المسار الحالي إلى مسار البحث ليتمكن من العثور على الحزم
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# تحميل متغيرات البيئة من .env إذا كان موجودًا (للتطوير المحلي)
# محاولة #1: التحميل المباشر
env_file = Path(".env")
if env_file.exists():
    logger.info("تم العثور على ملف .env، جاري تحميله... (طريقة 1)")
    load_dotenv(env_file)
    logger.info("تم تحميل ملف .env بطريقة 1")
else:
    logger.info("ملف .env غير موجود. محاولة طريقة أخرى...")
    
    # محاولة #2: البحث عن الملف في المجلد الحالي وجميع المجلدات الفرعية
    env_files = list(Path(".").glob("**/.env"))
    if env_files:
        logger.info(f"تم العثور على ملف .env في {env_files[0]}, جاري تحميله... (طريقة 2)")
        load_dotenv(env_files[0])
        logger.info("تم تحميل ملف .env بطريقة 2")
    else:
        logger.info("لم يتم العثور على ملف .env. استخدام متغيرات البيئة مباشرة...")

# إذا كنا نعمل في Render أو Heroku، يتم تعيين المتغيرات البيئية مباشرة
if not os.getenv("TOKEN") or not os.getenv("MONGODB_URI"):
    logger.warning("بعض متغيرات البيئة المهمة غير موجودة، محاولة التحميل اليدوي من .env...")
    
    # محاولة #3: التحميل اليدوي للملف
    try:
        if env_file.exists():
            logger.info("محاولة تحميل ملف .env يدويًا... (طريقة 3)")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    try:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
                        logger.info(f"تم تعيين متغير البيئة: {key}")
                    except Exception as e:
                        logger.warning(f"خطأ في معالجة السطر: {line}, خطأ: {str(e)}")
            logger.info("تم تحميل ملف .env يدويًا (طريقة 3)")
    except Exception as e:
        logger.error(f"خطأ أثناء تحميل ملف .env يدويًا: {str(e)}")
        logger.info("استخدام متغيرات البيئة المضبوطة على الخادم...")

# تفصيل متغيرات البيئة للتشخيص
logger.info("==== تشخيص متغيرات البيئة بعد التحميل ====")
available_vars = []
important_vars = ["TOKEN", "MONGODB_URI", "PREFIX", "DB_NAME", "NODE_ENV", "PORT", "LOG_LEVEL"]
for var in important_vars:
    if os.getenv(var):
        if var in ["TOKEN", "MONGODB_URI"]:
            value = os.getenv(var)
            masked_value = f"{value[:5]}..." if len(value) > 8 else "***"
            available_vars.append(f"{var}: {masked_value}")
        else:
            available_vars.append(f"{var}: {os.getenv(var)}")
    else:
        available_vars.append(f"{var}: غير موجود")

logger.info(", ".join(available_vars))
logger.info("================================")

# إنشاء تطبيق Flask
app = Flask(__name__)

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

@app.route('/env-debug')
def env_debug():
    """نقطة نهاية للتشخيص (متاحة فقط في وضع التطوير)"""
    if os.getenv('NODE_ENV') != 'production':
        env_vars = {
            "TOKEN_EXISTS": bool(os.getenv('TOKEN')),
            "MONGODB_URI_EXISTS": bool(os.getenv('MONGODB_URI')),
            "PREFIX": os.getenv('PREFIX', '!'),
            "DB_NAME": os.getenv('DB_NAME', 'discord_bot'),
            "NODE_ENV": os.getenv('NODE_ENV', 'development'),
            "PORT": os.getenv('PORT', '3000'),
        }
        return jsonify(env_vars)
    else:
        return jsonify({"error": "هذه النقطة غير متاحة في وضع الإنتاج"}), 403

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
                logger.error(f"فشل التحميل البديل: {str(e)} | {str(e2)}")
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