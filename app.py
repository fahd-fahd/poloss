from flask import Flask, jsonify, render_template
import os
import threading
import logging
from dotenv import load_dotenv

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
        
        # تشغيل البوت
        sys.path.insert(0, bot_path)
        from python_bot.src.main import main
        import asyncio
        
        # تغيير حالة البوت
        bot_status["status"] = "running"
        
        # تشغيل البوت
        asyncio.run(main())
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تشغيل البوت: {str(e)}")
        bot_status["status"] = "error"
        bot_status["last_error"] = str(e)
        import traceback
        traceback.print_exc()

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