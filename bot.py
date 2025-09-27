from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from utils import load_permissions, is_authorized, is_admin, add_user_request, approve_user, reject_user, get_pending_requests, get_all_users, remove_user_approval, search_user_by_id, save_permissions
from recommendation_system import RecommendationSystem
from symbol_mapper import TIMEFRAMES
from price_alerts import PriceAlerts
from daily_reports import DailyReports
from datetime import datetime
import json
import os
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")

# إنشاء الأنظمة
recommendation_system = RecommendationSystem()
price_alerts = PriceAlerts()
daily_reports = DailyReports()

# أوامر البوت:
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # التحقق من الصلاحية
    if not is_authorized(user_id):
        # التحقق من وجود طلب سابق أو رفض
        permissions = load_permissions()
        
        if user_id in permissions.get("rejected_users", []):
            await update.message.reply_text("❌ تم رفض طلبك سابقاً. لا يمكنك استخدام هذا البوت.")
            return
        
        if str(user_id) in permissions.get("pending_requests", {}):
            await update.message.reply_text("⏳ طلبك قيد المراجعة. يرجى انتظار موافقة المشرف.")
            return
        
        # إضافة طلب جديد
        user_info = {
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "",
            "request_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        add_user_request(user_id, user_info)
        
        # إرسال إشعار للمشرفين
        await notify_admins_new_request(context.bot, user_id, user_info)
        
        await update.message.reply_text(
            "📋 تم إرسال طلبك للمشرف. سيتم إشعارك عند الموافقة أو الرفض.\n"
            "⏳ يرجى انتظار المراجعة."
        )
        return
    
    user_type = "👤 مستخدم" if not is_admin(user_id) else "🔑 مشرف"
    
    welcome_message = f"""
🎯 **أهلاً بك في نظام التحليل المالي المتكامل** 🎯
{user_type}

🔍 **أوامر التحليل المتقدم:**
• `/analyze [SYMBOL] [TIMEFRAME]` - تحليل رمز معين
• `/forex [PAIR] [TIMEFRAME]` - تحليل زوج عملات
• `/crypto [SYMBOL] [TIMEFRAME]` - تحليل عملة رقمية  
• `/stock [SYMBOL] [TIMEFRAME]` - تحليل سهم
• `/gold [TIMEFRAME]` - تحليل الذهب
• `/us30 [TIMEFRAME]` - تحليل مؤشر داو جونز
• `/overview` - نظرة عامة على السوق

🔔 **أوامر التنبيهات:**
• `/price_alert [SYMBOL] [PRICE] [above/below]` - تنبيه سعر
• `/indicator_alert [SYMBOL] [INDICATOR] [VALUE]` - تنبيه مؤشر
• `/my_alerts` - عرض تنبيهاتي
• `/remove_alert [TYPE] [ID]` - حذف تنبيه

📊 **التقارير والإحصائيات:**
• `/daily_report` - التقرير اليومي
• `/weekly_report` - التقرير الأسبوعي
• `/correlation` - تحليل الارتباط
• `/performance` - ملخص الأداء

📰 **الأخبار والمعنويات:**
• `/news [forex/crypto/all]` - أخبار الأسواق
• `/calendar` - التقويم الاقتصادي
• `/sentiment` - تحليل معنويات السوق

⚙️ **أدوات إضافية:**
• `/timeframes` - عرض الفريمات المتاحة
• `/quick_menu` - القائمة السريعة التفاعلية
• `/patterns [SYMBOL]` - النماذج الفنية المكتشفة

**مثال:** `/analyze EURUSD 5m`
**مثال:** `/gold 1h`
**مثال:** `/us30 4h`"""

    if is_admin(user_id):
        welcome_message += """

🔑 **أوامر الإدارة (للمشرفين):**
• `/users` - عرض جميع المستخدمين المعتمدين
• `/pending` - عرض طلبات الانتظار
• `/remove_user [ID]` - إلغاء موافقة مستخدم
• `/search_user [ID]` - البحث عن مستخدم
• `/enable` / `/disable` - تفعيل/إيقاف المجموعات"""

    welcome_message += """

━━━━━━━━━━━━━━━━━━━━━━━
🚀 **الميزات الجديدة:**
🔍 النماذج الفنية المتقدمة (رأس وكتفين، مثلثات، إلخ)
🕯️ تحليل الشموع اليابانية المتقدم
📊 مؤشرات إضافية (Stochastic, Williams %R, CCI, ADX)
🔔 تنبيهات الأسعار والمؤشرات
📈 تقارير يومية وأسبوعية مفصلة
🔗 تحليل الارتباط بين الأزواج
📰 أخبار الأسواق والتقويم الاقتصادي
🎭 تحليل معنويات السوق

━━━━━━━━━━━━━━━━━━━━━━━
🤖 نظام تحليل متعدد المدارس (7 محاور)
📊 أكثر من 150 أداة تحليلية متقدمة
⏰ دعم الفريمات من 1 دقيقة إلى شهر
    """
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def enable_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    config = load_permissions()
    config["groups"][chat_id] = { "enabled": True }
    with open("permissions.json", "w") as f:
        json.dump(config, f)
    await update.message.reply_text("✅ تم تفعيل استقبال إشعارات TradingView لهذه المجموعة.")

async def disable_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    config = load_permissions()
    if chat_id in config["groups"]:
        config["groups"][chat_id]["enabled"] = False
        with open("permissions.json", "w") as f:
            json.dump(config, f)
        await update.message.reply_text("⛔️ تم إيقاف استقبال التنبيهات في هذه المجموعة.")
    else:
        await update.message.reply_text("⚠️ هذه المجموعة غير مسجلة بعد.")

async def analyze_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل رمز معين"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ يرجى إدخال رمز للتحليل\n"
            "**مثال:** `/analyze EURUSD 5m`\n"
            "**مثال:** `/analyze GOLD 1h`\n"
            "**مثال:** `/analyze US30 1d`",
            parse_mode='Markdown'
        )
        return
    
    symbol = context.args[0].upper()
    timeframe = context.args[1] if len(context.args) > 1 else "1h"
    
    await update.message.reply_text("🔄 جاري التحليل... يرجى الانتظار")
    
    try:
        recommendation = recommendation_system.analyze_symbol(symbol, timeframe=timeframe)
        
        if recommendation:
            message = recommendation_system.format_recommendation_message(recommendation)
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ لم يتم العثور على بيانات كافية لهذا الرمز")
    
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحليل: {str(e)}")

async def analyze_forex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل زوج عملات"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ يرجى إدخال زوج عملات للتحليل\n"
            "**مثال:** `/forex EURUSD 15m`\n"
            "**مثال:** `/forex GBPUSD 1h`",
            parse_mode='Markdown'
        )
        return
    
    symbol = context.args[0].upper()
    timeframe = context.args[1] if len(context.args) > 1 else "1h"
    
    await update.message.reply_text("🔄 جاري تحليل زوج العملات... يرجى الانتظار")
    
    try:
        recommendation = recommendation_system.analyze_symbol(symbol, timeframe=timeframe)
        
        if recommendation:
            message = recommendation_system.format_recommendation_message(recommendation)
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ لم يتم العثور على بيانات كافية لهذا الزوج")
    
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحليل: {str(e)}")

async def analyze_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل عملة رقمية"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ يرجى إدخال عملة رقمية للتحليل\n"
            "**مثال:** `/crypto BTC 5m`\n"
            "**مثال:** `/crypto ETH 1h`",
            parse_mode='Markdown'
        )
        return
    
    symbol = context.args[0].upper()
    timeframe = context.args[1] if len(context.args) > 1 else "1h"
    
    await update.message.reply_text("🔄 جاري تحليل العملة الرقمية... يرجى الانتظار")
    
    try:
        recommendation = recommendation_system.analyze_symbol(symbol, timeframe=timeframe)
        
        if recommendation:
            message = recommendation_system.format_recommendation_message(recommendation)
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ لم يتم العثور على بيانات كافية لهذه العملة")
    
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحليل: {str(e)}")

async def analyze_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل سهم"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ يرجى إدخال رمز السهم للتحليل\n"
            "**مثال:** `/stock AAPL 1d`\n"
            "**مثال:** `/stock TSLA 4h`",
            parse_mode='Markdown'
        )
        return
    
    symbol = context.args[0].upper()
    timeframe = context.args[1] if len(context.args) > 1 else "1h"
    
    await update.message.reply_text("🔄 جاري تحليل السهم... يرجى الانتظار")
    
    try:
        recommendation = recommendation_system.analyze_symbol(symbol, timeframe=timeframe)
        
        if recommendation:
            message = recommendation_system.format_recommendation_message(recommendation)
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ لم يتم العثور على بيانات كافية لهذا السهم")
    
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحليل: {str(e)}")

async def market_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نظرة عامة على السوق"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    await update.message.reply_text("🔄 جاري تحليل السوق العام... يرجى الانتظار")
    
    try:
        overview = recommendation_system.get_market_overview()
        
        message = f"""
📊 **نظرة عامة على الأسواق** 📊

**إحصائيات عامة:**
🟢 إشارات شراء: {overview['bullish']}
🔴 إشارات بيع: {overview['bearish']}
🟡 إشارات محايدة: {overview['neutral']}

**توصيات سريعة:**
"""
        
        for rec in overview['recommendations'][:3]:  # أول 3 توصيات
            symbol = rec.get('symbol', 'غير محدد')
            rec_type = rec.get('type', 'محايد')
            confidence = rec.get('confidence', 0)
            
            if rec_type == "شراء":
                icon = "🟢"
            elif rec_type == "بيع":
                icon = "🔴"
            else:
                icon = "🟡"
            
            message += f"\n{icon} {symbol}: {rec_type} ({confidence:.0f}%)"
        
        message += "\n\n━━━━━━━━━━━━━━━━━━━━━━━\n🤖 *تحديث كل 30 دقيقة*"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء جمع البيانات: {str(e)}")

# أوامر رموز محددة
async def analyze_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل الذهب"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    timeframe = context.args[0] if context.args else "1h"
    await update.message.reply_text("🥇 جاري تحليل الذهب... يرجى الانتظار")
    
    try:
        recommendation = recommendation_system.analyze_symbol("GOLD", timeframe=timeframe)
        
        if recommendation:
            message = recommendation_system.format_recommendation_message(recommendation)
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ لم يتم العثور على بيانات كافية للذهب")
    
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحليل: {str(e)}")

async def analyze_us30(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل مؤشر داو جونز"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    timeframe = context.args[0] if context.args else "1h"
    await update.message.reply_text("🇺🇸 جاري تحليل مؤشر داو جونز... يرجى الانتظار")
    
    try:
        recommendation = recommendation_system.analyze_symbol("US30", timeframe=timeframe)
        
        if recommendation:
            message = recommendation_system.format_recommendation_message(recommendation)
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ لم يتم العثور على بيانات كافية للمؤشر")
    
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحليل: {str(e)}")

async def show_timeframes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الفريمات المتاحة"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    timeframes_text = """
⏰ **الفريمات الزمنية المتاحة** ⏰

• `1m` - دقيقة واحدة
• `5m` - خمس دقائق
• `15m` - ربع ساعة
• `30m` - نصف ساعة
• `1h` - ساعة واحدة (افتراضي)
• `4h` - أربع ساعات
• `1d` - يوم واحد
• `1w` - أسبوع واحد
• `1M` - شهر واحد

**أمثلة:**
• `/analyze EURUSD 5m`
• `/gold 1h`
• `/crypto BTC 1d`
• `/us30 4h`

⚙️ **نصائح:**
• الفريمات القصيرة (1m-30m) للتداول السريع
• الفريمات المتوسطة (1h-4h) للتداول اليومي
• الفريمات الطويلة (1d-1M) للاستثمار
    """
    
    await update.message.reply_text(timeframes_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المساعدة"""
    help_text = """
🆘 **دليل استخدام البوت** 🆘

**أوامر التحليل:**
• `/analyze [SYMBOL]` - تحليل شامل لأي رمز
• `/forex [PAIR]` - تحليل أزواج العملات (EURUSD, GBPUSD...)
• `/crypto [SYMBOL]` - تحليل العملات الرقمية (BTC, ETH...)
• `/stock [SYMBOL]` - تحليل الأسهم (AAPL, TSLA...)
• `/overview` - نظرة عامة على السوق

**أوامر الإدارة:** (للمشرفين فقط)
• `/enable` - تفعيل التنبيهات في المجموعة
• `/disable` - إيقاف التنبيهات في المجموعة

**نظام التحليل يشمل:**
🎯 7 محاور تحليلية رئيسية
📈 130+ أداة ونموذج فني
🔍 تحليل الاتجاه والسلوك السعري
📊 فيبوناتشي والتحليل الرقمي
💰 تحليل الحجم والتدفقات
🎨 النماذج الفنية المتقدمة
⚡ المؤشرات الديناميكية
💹 تدفق المال والبيانات المؤسسية
🛠️ الأدوات الاحترافية

━━━━━━━━━━━━━━━━━━━━━━━
⚠️ **تنبيه:** هذا النظام أداة مساعدة للتحليل وليس نصيحة استثمارية
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# استيراد الأوامر الجديدة
from bot_new_commands import (
    price_alert_command, my_alerts_command, daily_report_command,
    weekly_report_command, correlation_command, performance_command,
    quick_menu_command, handle_quick_menu_callback, patterns_command
)
from market_news import MarketNews

# إنشاء نظام الأخبار
market_news = MarketNews()

# أوامر الأخبار والتقارير الجديدة
async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أخبار السوق"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    news_type = context.args[0] if context.args else "all"
    
    await update.message.reply_text("📰 جاري جلب آخر الأخبار...")
    
    try:
        news_message = market_news.format_news_message(news_type)
        await update.message.reply_text(news_message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب الأخبار: {str(e)}")

async def economic_calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض التقويم الاقتصادي"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    await update.message.reply_text("📅 جاري جلب التقويم الاقتصادي...")
    
    try:
        calendar_message = market_news.get_economic_calendar()
        await update.message.reply_text(calendar_message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب التقويم: {str(e)}")

async def sentiment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل معنويات السوق"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    await update.message.reply_text("🎭 جاري تحليل معنويات السوق...")
    
    try:
        sentiment_message = market_news.get_sentiment_analysis()
        await update.message.reply_text(sentiment_message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تحليل المعنويات: {str(e)}")

# وظائف إدارة المستخدمين
async def notify_admins_new_request(bot, user_id, user_info):
    """إشعار المشرفين بطلب جديد"""
    permissions = load_permissions()
    admins = permissions.get('admins', [])
    
    keyboard = [
        [
            InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
📝 **طلب مستخدم جديد**

**معرف المستخدم:** `{user_id}`
**الاسم الأول:** {user_info.get('first_name', 'غير محدد')}
**الاسم الأخير:** {user_info.get('last_name', 'غير محدد')}
**اسم المستخدم:** @{user_info.get('username', 'غير محدد')}
**وقت الطلب:** {user_info.get('request_time')}

🔎 يرجى مراجعة الطلب واتخاذ القرار المناسب.
    """
    
    for admin_id in admins:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"خطأ في إرسال إشعار للمشرف {admin_id}: {e}")

async def handle_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة استجابات الموافقة/الرفض"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("🚫 ليس لديك صلاحية لهذا الإجراء.")
        return
    
    callback_data = query.data
    action, target_user_id = callback_data.split('_')
    target_user_id = int(target_user_id)
    
    if action == "approve":
        if approve_user(target_user_id):
            await query.edit_message_text(f"✅ تمت الموافقة على المستخدم {target_user_id}")
            
            # إشعار المستخدم بالموافقة
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="🎉 تمت الموافقة على طلبك! يمكنك الآن استخدام البوت. اكتب /start للبدء."
                )
            except Exception as e:
                print(f"خطأ في إشعار المستخدم {target_user_id}: {e}")
        else:
            await query.edit_message_text("❌ خطأ في الموافقة على المستخدم")
    
    elif action == "reject":
        if reject_user(target_user_id):
            await query.edit_message_text(f"❌ تم رفض المستخدم {target_user_id}")
            
            # إشعار المستخدم بالرفض
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="❌ تم رفض طلبك لاستخدام البوت. للمزيد من المعلومات، يرجى التواصل مع المشرف."
                )
            except Exception as e:
                print(f"خطأ في إشعار المستخدم {target_user_id}: {e}")
        else:
            await query.edit_message_text("❌ خطأ في رفض المستخدم")

async def list_pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض طلبات الانتظار"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    
    pending_requests = get_pending_requests()
    
    if not pending_requests:
        await update.message.reply_text("✅ لا توجد طلبات معلقة.")
        return
    
    message = "📝 **طلبات الانتظار:**\n\n"
    
    for user_id, user_info in pending_requests.items():
        message += f"• **معرف:** `{user_id}`\n"
        message += f"  **الاسم:** {user_info.get('first_name', '')}"
        if user_info.get('last_name'):
            message += f" {user_info.get('last_name')}"
        message += "\n"
        if user_info.get('username'):
            message += f"  **المستخدم:** @{user_info.get('username')}\n"
        message += f"  **الوقت:** {user_info.get('request_time')}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def list_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض جميع المستخدمين المعتمدين"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    
    all_users = get_all_users()
    
    if not all_users:
        await update.message.reply_text("📭 لا يوجد مستخدمين معتمدين حالياً.")
        return
    
    message = f"👥 **قائمة المستخدمين المعتمدين** ({len(all_users)})\n\n"
    
    for i, user_id in enumerate(all_users, 1):
        message += f"{i}. **معرف المستخدم:** `{user_id}`\n"
        
        # إضافة زر إلغاء الموافقة (ما عدا المشرفين)
        permissions = load_permissions()
        if user_id not in permissions.get('admins', []):
            message += f"   • `/remove_user {user_id}` - إلغاء الموافقة\n"
        else:
            message += f"   • 🔑 **مشرف**\n"
        message += "\n"
    
    message += "\n📝 **الأوامر المتاحة:**\n"
    message += "• `/pending` - عرض طلبات الانتظار\n"
    message += "• `/remove_user [ID]` - إلغاء موافقة مستخدم\n"
    message += "• `/search_user [ID]` - البحث عن مستخدم"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def remove_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء موافقة مستخدم"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ يرجى إدخال معرف المستخدم\n"
            "**مثال:** `/remove_user 123456789`",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ معرف المستخدم يجب أن يكون رقماً.")
        return
    
    # منع حذف المشرفين
    permissions = load_permissions()
    if target_user_id in permissions.get('admins', []):
        await update.message.reply_text("❌ لا يمكن حذف المشرفين.")
        return
    
    if remove_user_approval(target_user_id):
        await update.message.reply_text(f"✅ تم إلغاء موافقة المستخدم `{target_user_id}` بنجاح.", parse_mode='Markdown')
        
        # إشعار المستخدم بإلغاء الموافقة
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="❌ تم إلغاء موافقتك لاستخدام البوت. لم تعد تستطيع استخدام الأوامر."
            )
        except Exception as e:
            print(f"خطأ في إشعار المستخدم {target_user_id}: {e}")
    else:
        await update.message.reply_text(f"❌ لم يتم العثور على المستخدم `{target_user_id}` في قائمة المعتمدين.", parse_mode='Markdown')

async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة مستخدم مباشرة عبر معرفه (Admins only)"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ يرجى إدخال معرف المستخدم\n"
            "**مثال:** `/add_user 123456789`",
            parse_mode='Markdown'
        )
        return

    try:
        target_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ معرف المستخدم يجب أن يكون رقماً.")
        return

    perms = load_permissions()
    authorized = perms.get("authorized_users", perms.get("1142810150", []))
    if target_user_id not in authorized:
        authorized.append(target_user_id)
        perms["authorized_users"] = authorized
        save_permissions(perms)

    await update.message.reply_text(f"✅ تم اعتماد المستخدم `{target_user_id}`.", parse_mode='Markdown')

async def search_telegram_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إيجاد معرف مستخدم عبر Username باستخدام getChat (Admins only)"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return

    if not context.args or not context.args[0].startswith('@'):
        await update.message.reply_text(
            "⚠️ يرجى إدخال اسم المستخدم مع @\n"
            "**مثال:** `/search_telegram @username`",
            parse_mode='Markdown'
        )
        return

    username = context.args[0]
    try:
        chat = await context.bot.get_chat(username)
        await update.message.reply_text(
            f"🔎 نتيجة البحث:\n\n• Username: `{username}`\n• ID: `{chat.id}`\n\n📝 يمكنك إضافته: `/add_user {chat.id}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ لم أستطع إيجاد المستخدم {username}: {e}")

async def search_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """البحث عن مستخدم"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ يرجى إدخال معرف المستخدم\n"
            "**مثال:** `/search_user 123456789`",
            parse_mode='Markdown'
        )
        return
    
    try:
        search_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ معرف المستخدم يجب أن يكون رقماً.")
        return
    
    if search_user_by_id(search_id):
        permissions = load_permissions()
        is_admin_user = search_id in permissions.get('admins', [])
        
        status = "🔑 مشرف" if is_admin_user else "✅ معتمد"
        message = f"🔍 **نتيجة البحث:**\n\n"
        message += f"• **المعرف:** `{search_id}`\n"
        message += f"• **الحالة:** {status}\n\n"
        
        if not is_admin_user:
            message += f"📝 لإلغاء الموافقة: `/remove_user {search_id}`"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ لم يتم العثور على المستخدم `{search_id}` في قائمة المعتمدين.", parse_mode='Markdown')

# تشغيل البوت
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر الأساسية
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # أوامر التحليل
    app.add_handler(CommandHandler("analyze", analyze_symbol))
    app.add_handler(CommandHandler("forex", analyze_forex))
    app.add_handler(CommandHandler("crypto", analyze_crypto))
    app.add_handler(CommandHandler("stock", analyze_stock))
    app.add_handler(CommandHandler("gold", analyze_gold))
    app.add_handler(CommandHandler("us30", analyze_us30))
    app.add_handler(CommandHandler("overview", market_overview))
    app.add_handler(CommandHandler("timeframes", show_timeframes))
    
    # أوامر إدارة المجموعات
    app.add_handler(CommandHandler("enable", enable_group))
    app.add_handler(CommandHandler("disable", disable_group))
    
    # أوامر إدارة المستخدمين (للمشرفين)
    app.add_handler(CommandHandler("pending", list_pending_requests))
    app.add_handler(CommandHandler("users", list_all_users))
    app.add_handler(CommandHandler("remove_user", remove_user_command))
    app.add_handler(CommandHandler("search_user", search_user_command))

    # أوامر إدارية إضافية
    app.add_handler(CommandHandler("add_user", add_user_command))
    app.add_handler(CommandHandler("search_telegram", search_telegram_command))
    
    # أوامر التنبيهات والتقارير الجديدة
    app.add_handler(CommandHandler("price_alert", price_alert_command))
    app.add_handler(CommandHandler("my_alerts", my_alerts_command))
    app.add_handler(CommandHandler("daily_report", daily_report_command))
    app.add_handler(CommandHandler("weekly_report", weekly_report_command))
    app.add_handler(CommandHandler("correlation", correlation_command))
    app.add_handler(CommandHandler("performance", performance_command))
    app.add_handler(CommandHandler("patterns", patterns_command))
    
    # أوامر الواجهة المحسنة
    app.add_handler(CommandHandler("quick_menu", quick_menu_command))
    
    # أوامر الأخبار والمعنويات
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("calendar", economic_calendar_command))
    app.add_handler(CommandHandler("sentiment", sentiment_command))
    
    # معالج الإجابات المضمنة (أزرار الموافقة/الرفض والقائمة السريعة)
    app.add_handler(CallbackQueryHandler(handle_approval_callback, pattern="^(approve|reject)_"))
    app.add_handler(CallbackQueryHandler(handle_quick_menu_callback, pattern="^(analyze_|market_overview|my_alerts|daily_report|correlation)"))
    
    # بدء مراقبة التنبيهات في الخلفية
    async def start_alert_monitoring():
        await price_alerts.monitor_alerts(app.bot)
    
    # إضافة مهمة مراقبة التنبيهات
    import threading
    
    def run_alert_monitoring():
        asyncio.run(start_alert_monitoring())
    
    # تشغيل مراقبة التنبيهات في thread منفصل
    alert_thread = threading.Thread(target=run_alert_monitoring, daemon=True)
    alert_thread.start()
    
    print("🤖 البوت يعمل الآن مع جميع الميزات المتقدمة...")
    print("🔔 نظام التنبيهات نشط...")
    print("📊 النماذج الفنية المتقدمة جاهزة...")
    print("📰 نظام الأخبار والتقارير متاح...")
    
    app.run_polling()