"""
إعدادات المشروع - آمنة عبر المتغيرات البيئية
لا تضع مفاتيحك هنا. استخدم متغيرات البيئة التالية:
- BOT_TOKEN
- ALPHA_VANTAGE_API_KEY (اختياري)
- POLYGON_API_KEY (اختياري)
"""
import os

# مفاتيح حساسة من البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# إعدادات أخرى
APP_VERSION = "2.0"
DEFAULT_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1H", "4H", "1D"]

# معرفات المشرفين الافتراضية (يمكن ضبطها لاحقاً عبر permissions.json)
DEFAULT_ADMIN_USER_IDS = [1142810150]
