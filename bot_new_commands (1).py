"""
أوامر البوت الجديدة للتنبيهات والتقارير والواجهة المحسنة
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import is_authorized, is_admin, approve_user, reject_user, load_permissions
from price_alerts import PriceAlerts
from daily_reports import DailyReports
import asyncio

# تنبيهات الأسعار
async def price_alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة تنبيه سعر"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "⚠️ **استخدام التنبيهات:**\n\n"
            "**تنبيه السعر:**\n"
            "`/price_alert EURUSD 1.2000 above`\n"
            "`/price_alert BTC 50000 below`\n\n"
            "**المعاملات:**\n"
            "• SYMBOL - رمز التداول\n"
            "• PRICE - السعر المستهدف\n"
            "• above/below - فوق أو تحت السعر",
            parse_mode='Markdown'
        )
        return
    
    symbol = context.args[0].upper()
    try:
        target_price = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ السعر المدخل غير صحيح.")
        return
    
    alert_type = context.args[2].lower()
    if alert_type not in ['above', 'below']:
        await update.message.reply_text("❌ نوع التنبيه يجب أن يكون above أو below.")
        return
    
    timeframe = context.args[3] if len(context.args) > 3 else "1h"
    
    try:
        price_alerts = PriceAlerts()
        alert_id = price_alerts.add_price_alert(user_id, symbol, target_price, alert_type, timeframe)
        
        direction_text = "فوق" if alert_type == "above" else "تحت"
        
        await update.message.reply_text(
            f"✅ **تم إضافة التنبيه بنجاح!**\n\n"
            f"🎯 **الرمز:** `{symbol}`\n"
            f"📊 **السعر المستهدف:** `{target_price}`\n"
            f"📈 **الاتجاه:** {direction_text}\n"
            f"⏰ **الفريم الزمني:** `{timeframe}`\n"
            f"🆔 **معرف التنبيه:** `{alert_id}`\n\n"
            f"🔔 سيتم إشعارك عند الوصول للسعر المحدد!",
            parse_mode='Markdown'
        )
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في إضافة التنبيه: {str(e)}")

# عرض التنبيهات
async def my_alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض تنبيهات المستخدم"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    try:
        price_alerts = PriceAlerts()
        user_alerts = price_alerts.get_user_alerts(user_id)
        
        if not any(user_alerts.values()):
            await update.message.reply_text("📭 لا توجد تنبيهات حالياً.")
            return
        
        message = "🔔 **تنبيهاتك النشطة:**\n\n"
        
        # تنبيهات الأسعار
        if user_alerts['price_alerts']:
            message += "💰 **تنبيهات الأسعار:**\n"
            for alert in user_alerts['price_alerts']:
                if alert['status'] == 'active':
                    direction = "فوق" if alert['alert_type'] == 'above' else "تحت"
                    message += f"• `{alert['symbol']}` - {alert['target_price']} ({direction}) | ID: {alert['id']}\n"
            message += "\n"
        
        # تنبيهات المؤشرات
        if user_alerts['indicator_alerts']:
            message += "📊 **تنبيهات المؤشرات:**\n"
            for alert in user_alerts['indicator_alerts']:
                if alert['status'] == 'active':
                    condition = "فوق" if alert['condition'] == 'above' else "تحت"
                    message += f"• `{alert['symbol']}` - {alert['indicator']} {condition} {alert['value']} | ID: {alert['id']}\n"
            message += "\n"
        
        message += "**حذف تنبيه:** `/remove_alert price [ID]`"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب التنبيهات: {str(e)}")

# التقرير اليومي
async def daily_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنشاء التقرير اليومي"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    await update.message.reply_text("📊 جاري إنشاء التقرير اليومي...")
    
    try:
        daily_reports = DailyReports()
        report = daily_reports.generate_daily_report()
        await update.message.reply_text(report, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في إنشاء التقرير: {str(e)}")

# التقرير الأسبوعي
async def weekly_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنشاء التقرير الأسبوعي"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    await update.message.reply_text("📈 جاري إنشاء التقرير الأسبوعي...")
    
    try:
        daily_reports = DailyReports()
        report = daily_reports.generate_weekly_report()
        await update.message.reply_text(report, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في إنشاء التقرير: {str(e)}")

# تحليل الارتباط
async def correlation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل الارتباط بين أزواج العملات"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    await update.message.reply_text("🔗 جاري تحليل الارتباط...")
    
    try:
        daily_reports = DailyReports()
        correlation_report = daily_reports.analyze_pair_correlation()
        await update.message.reply_text(correlation_report, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تحليل الارتباط: {str(e)}")

# ملخص الأداء
async def performance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ملخص أداء التوصيات"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    days = 30
    if context.args and context.args[0].isdigit():
        days = int(context.args[0])
    
    await update.message.reply_text(f"📊 جاري إنشاء ملخص الأداء لآخر {days} يوم...")
    
    try:
        daily_reports = DailyReports()
        performance_report = daily_reports.generate_performance_summary(days)
        await update.message.reply_text(performance_report, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في إنشاء ملخص الأداء: {str(e)}")

# القائمة السريعة
async def quick_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض القائمة السريعة مع أزرار تفاعلية"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    # إنشاء الأزرار التفاعلية
    keyboard = [
        [
            InlineKeyboardButton("📈 EURUSD", callback_data="analyze_EURUSD"),
            InlineKeyboardButton("📉 GBPUSD", callback_data="analyze_GBPUSD")
        ],
        [
            InlineKeyboardButton("🥇 ذهب", callback_data="analyze_GOLD"),
            InlineKeyboardButton("🇺🇸 US30", callback_data="analyze_US30")
        ],
        [
            InlineKeyboardButton("₿ BTC", callback_data="analyze_BTC"),
            InlineKeyboardButton("⟠ ETH", callback_data="analyze_ETH")
        ],
        [
            InlineKeyboardButton("📊 نظرة عامة", callback_data="market_overview"),
            InlineKeyboardButton("🔔 تنبيهاتي", callback_data="my_alerts")
        ],
        [
            InlineKeyboardButton("📋 تقرير يومي", callback_data="daily_report"),
            InlineKeyboardButton("🔗 ارتباط", callback_data="correlation")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🚀 **القائمة السريعة** 🚀

اختر من القائمة أدناه للحصول على تحليل سريع:

📈 **أزواج العملات الرئيسية**
🥇 **السلع والمؤشرات**
₿ **العملات الرقمية**
📊 **التقارير والإحصائيات**

💡 **نصيحة:** يمكنك أيضاً استخدام الأوامر مباشرة!
    """
    
    await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

# معالج الأزرار التفاعلية
async def handle_quick_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار التفاعلية"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_authorized(user_id):
        await query.edit_message_text("🚫 ليس لديك صلاحية لهذا الإجراء.")
        return
    
    callback_data = query.data
    
    if callback_data.startswith("analyze_"):
        symbol = callback_data.replace("analyze_", "")
        await query.edit_message_text(f"🔄 جاري تحليل {symbol}...")
        
        try:
            from recommendation_system import RecommendationSystem
            recommendation_system = RecommendationSystem()
            recommendation = recommendation_system.analyze_symbol(symbol)
            
            if recommendation:
                message = recommendation_system.format_recommendation_message(recommendation)
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text(f"❌ لم يتم العثور على بيانات كافية لـ {symbol}")
        
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ في التحليل: {str(e)}")
    
    elif callback_data == "market_overview":
        await query.edit_message_text("📊 جاري تحليل السوق العام...")
        
        try:
            from recommendation_system import RecommendationSystem
            recommendation_system = RecommendationSystem()
            overview = recommendation_system.get_market_overview()
            
            message = f"""
📊 **نظرة عامة على الأسواق** 📊

**إحصائيات عامة:**
🟢 إشارات شراء: {overview['bullish']}
🔴 إشارات بيع: {overview['bearish']}
🟡 إشارات محايدة: {overview['neutral']}

**توصيات سريعة:**
"""
            
            for rec in overview['recommendations'][:3]:
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
            
            await query.edit_message_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ في جمع البيانات: {str(e)}")
    
    elif callback_data == "my_alerts":
        try:
            price_alerts = PriceAlerts()
            user_alerts = price_alerts.get_user_alerts(user_id)
            
            if not any(user_alerts.values()):
                await query.edit_message_text("📭 لا توجد تنبيهات حالياً.")
                return
            
            message = "🔔 **تنبيهاتك النشطة:**\n\n"
            
            if user_alerts['price_alerts']:
                message += "💰 **تنبيهات الأسعار:**\n"
                for alert in user_alerts['price_alerts'][:5]:  # أول 5 فقط
                    if alert['status'] == 'active':
                        direction = "فوق" if alert['alert_type'] == 'above' else "تحت"
                        message += f"• `{alert['symbol']}` - {alert['target_price']} ({direction})\n"
            
            await query.edit_message_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ في جلب التنبيهات: {str(e)}")
    
    elif callback_data == "daily_report":
        await query.edit_message_text("📊 جاري إنشاء التقرير اليومي...")
        
        try:
            daily_reports = DailyReports()
            report = daily_reports.generate_daily_report()
            await query.edit_message_text(report, parse_mode='Markdown')
        
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ في إنشاء التقرير: {str(e)}")
    
    elif callback_data == "correlation":
        await query.edit_message_text("🔗 جاري تحليل الارتباط...")
        
        try:
            daily_reports = DailyReports()
            correlation_report = daily_reports.analyze_pair_correlation()
            # إرسال جزء من التقرير فقط بسبب حدود الرسائل
            short_report = correlation_report[:1000] + "...\n\nللتقرير الكامل استخدم: /correlation"
            await query.edit_message_text(short_report, parse_mode='Markdown')
        
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ في تحليل الارتباط: {str(e)}")

# النماذج الفنية المكتشفة
async def patterns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض النماذج الفنية المكتشفة لرمز معين"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ يرجى إدخال رمز للتحليل\n"
            "**مثال:** `/patterns EURUSD`",
            parse_mode='Markdown'
        )
        return
    
    symbol = context.args[0].upper()
    timeframe = context.args[1] if len(context.args) > 1 else "1h"
    
    await update.message.reply_text(f"🔍 جاري البحث عن النماذج الفنية في {symbol}...")
    
    try:
        from data_collector import DataCollector
        from advanced_patterns import AdvancedPatterns
        from candlestick_patterns import CandlestickPatterns
        
        data_collector = DataCollector()
        data = data_collector.get_data_by_type(symbol, timeframe=timeframe)
        
        if data is None or data.empty:
            await update.message.reply_text("❌ لم يتم العثور على بيانات كافية لهذا الرمز")
            return
        
        # تحليل النماذج
        advanced_patterns = AdvancedPatterns(data)
        patterns_result = advanced_patterns.analyze_all_patterns()
        
        candlestick_analyzer = CandlestickPatterns(data)
        candlestick_result = candlestick_analyzer.analyze_all_candlestick_patterns()
        
        message = f"""
🔍 **النماذج الفنية المكتشفة - {symbol}** 🔍

📊 **إحصائيات عامة:**
• النماذج الفنية: {patterns_result.get('total_patterns', 0)}
• الشموع اليابانية: {candlestick_result.get('total_patterns', 0)}
• النماذج الصاعدة: {patterns_result.get('bullish_patterns', 0)}
• النماذج الهابطة: {patterns_result.get('bearish_patterns', 0)}
        """
        
        # أقوى النماذج الفنية
        if patterns_result.get('patterns'):
            message += "\n\n**🏆 أقوى النماذج الفنية:**\n"
            for pattern in patterns_result['patterns'][:3]:
                strength = pattern.get('strength', 50)
                pattern_type = pattern.get('type', 'غير محدد')
                direction = pattern.get('direction', 'محايد')
                message += f"• **{pattern_type}**: {direction} - القوة: {strength}%\n"
        
        # أقوى الشموع اليابانية
        if candlestick_result.get('patterns'):
            message += "\n\n**🕯️ أقوى الشموع اليابانية:**\n"
            for candle in candlestick_result['patterns'][:3]:
                strength = candle.get('strength', 50)
                candle_type = candle.get('type', 'غير محدد')
                signal = candle.get('signal', 'محايد')
                message += f"• **{candle_type}**: {signal} - القوة: {strength}%\n"
        
        if not patterns_result.get('patterns') and not candlestick_result.get('patterns'):
            message += "\n\n📭 لم يتم العثور على نماذج فنية واضحة حالياً."
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تحليل النماذج: {str(e)}")

# معالج الموافقة على المستخدمين الجدد
async def handle_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الموافقة أو الرفض للمستخدمين الجدد"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("🚫 هذا الإجراء مخصص للمشرفين فقط.")
        return
    
    try:
        # استخراج الإجراء ومعرف المستخدم من البيانات
        callback_data = query.data  # مثل: "approve_123456789" أو "reject_123456789"
        action, target_user_id = callback_data.split("_", 1)
        target_user_id = int(target_user_id)
        
        if action == "approve":
            if approve_user(target_user_id):
                await query.edit_message_text(
                    f"✅ تم قبول المستخدم `{target_user_id}` بنجاح!\n\n"
                    f"📝 الآن يمكنه استخدام جميع أوامر البوت.",
                    parse_mode='Markdown'
                )
                
                # إشعار المستخدم بالموافقة
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text="🎉 **تم قبول طلبك!**\n\n"
                             "✅ يمكنك الآن استخدام جميع أوامر البوت.\n"
                             "📋 اكتب `/help` لعرض قائمة الأوامر المتاحة.",
                        parse_mode='Markdown'
                    )
                except Exception as notify_error:
                    print(f"خطأ في إشعار المستخدم {target_user_id}: {notify_error}")
                    
            else:
                await query.edit_message_text(f"❌ خطأ في الموافقة على المستخدم `{target_user_id}`")
                
        elif action == "reject":
            if reject_user(target_user_id):
                await query.edit_message_text(
                    f"❌ تم رفض المستخدم `{target_user_id}`.\n\n"
                    f"📝 لن يتمكن من استخدام البوت.",
                    parse_mode='Markdown'
                )
                
                # إشعار المستخدم بالرفض
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text="❌ **تم رفض طلبك**\n\n"
                             "🚫 عذراً، لا يمكنك استخدام هذا البوت حالياً.\n"
                             "📧 للاستفسار، تواصل مع المشرفين.",
                        parse_mode='Markdown'
                    )
                except Exception as notify_error:
                    print(f"خطأ في إشعار المستخدم {target_user_id}: {notify_error}")
                    
            else:
                await query.edit_message_text(f"❌ خطأ في رفض المستخدم `{target_user_id}`")
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في معالجة الطلب: {str(e)}")
        print(f"خطأ في معالج الموافقة: {e}")

# إضافة مستخدم بالمعرف (للمشرفين)
async def add_user_by_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة مستخدم جديد بواسطة معرفه على تلغرام"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ **استخدام الأمر:**\n\n"
            "`/add_user @username` - بالمعرف\n"
            "`/add_user 123456789` - بمعرف المستخدم\n\n"
            "**مثال:**\n"
            "`/add_user @ahmed_trader`\n"
            "`/add_user 123456789`",
            parse_mode='Markdown'
        )
        return
    
    user_input = context.args[0]
    
    # إزالة @ إذا كان موجوداً
    if user_input.startswith('@'):
        username = user_input[1:]
        await update.message.reply_text(
            f"🔍 **البحث عن المستخدم:** `@{username}`\n\n"
            f"⚠️ **ملاحظة:** نظراً لقيود تلغرام، لا يمكن البحث عن المستخدمين بالمعرف مباشرة.\n\n"
            f"**بدلاً من ذلك:**\n"
            f"1. اطلب من المستخدم إرسال رسالة للبوت أولاً\n"
            f"2. استخدم `/pending` لرؤية طلبات الانتظار\n"
            f"3. وافق على الطلب من هناك\n\n"
            f"**أو استخدم معرف المستخدم الرقمي إذا كان متوفراً:**\n"
            f"`/add_user 123456789`",
            parse_mode='Markdown'
        )
        return
    
    # إذا كان رقماً (معرف المستخدم)
    try:
        target_user_id = int(user_input)
    except ValueError:
        await update.message.reply_text(
            "❌ **خطأ في التنسيق**\n\n"
            "يرجى إدخال:\n"
            "• معرف رقمي صحيح (مثل: 123456789)\n"
            "• أو معرف المستخدم (@username)\n\n"
            "**مثال صحيح:** `/add_user 123456789`",
            parse_mode='Markdown'
        )
        return
    
    # فحص إذا كان المستخدم موجود مسبقاً
    permissions = load_permissions()
    existing_users = permissions.get("1142810150", [])
    
    if target_user_id in existing_users:
        await update.message.reply_text(
            f"⚠️ المستخدم `{target_user_id}` معتمد مسبقاً!",
            parse_mode='Markdown'
        )
        return
    
    # إضافة المستخدم مباشرة
    if approve_user(target_user_id):
        # محاولة إشعار المستخدم
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="🎉 **مرحباً بك!**\n\n"
                     "✅ تم إضافتك إلى البوت بواسطة أحد المشرفين.\n"
                     "📋 يمكنك الآن استخدام جميع أوامر البوت.\n"
                     "🆘 اكتب `/help` لعرض قائمة الأوامر المتاحة.",
                parse_mode='Markdown'
            )
            
            await update.message.reply_text(
                f"✅ **تم بنجاح!**\n\n"
                f"👤 تم إضافة المستخدم: `{target_user_id}`\n"
                f"📨 تم إرسال إشعار ترحيب للمستخدم\n"
                f"🔓 يمكنه الآن استخدام جميع أوامر البوت",
                parse_mode='Markdown'
            )
            
        except Exception as notify_error:
            await update.message.reply_text(
                f"✅ **تم إضافة المستخدم بنجاح!**\n\n"
                f"👤 المستخدم: `{target_user_id}`\n"
                f"⚠️ لكن لم يتم إرسال الإشعار (ربما لم يبدأ محادثة مع البوت)\n"
                f"📝 المستخدم مضاف ويمكنه استخدام البوت عند بدء المحادثة",
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(f"❌ خطأ في إضافة المستخدم `{target_user_id}`")

# بحث عن مستخدم في تلغرام (تجريبي)
async def search_telegram_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """البحث عن مستخدم في تلغرام بالمعرف"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ **استخدام الأمر:**\n\n"
            "`/search_telegram @username`\n\n"
            "**مثال:** `/search_telegram @ahmed_trader`",
            parse_mode='Markdown'
        )
        return
    
    username = context.args[0]
    if username.startswith('@'):
        username = username[1:]
    
    await update.message.reply_text(
        f"🔍 **البحث عن:** `@{username}`\n\n"
        f"⚠️ **القيود التقنية:**\n"
        f"• واجهة تلغرام لا تسمح بالبحث المباشر عن المستخدمين\n"
        f"• يحتاج المستخدم لإرسال رسالة للبوت أولاً\n\n"
        f"**الطريقة الأفضل:**\n"
        f"1. شارك رابط البوت مع المستخدم\n"
        f"2. اطلب منه الضغط على `/start`\n"
        f"3. استخدم `/pending` لرؤية طلبه والموافقة عليه\n\n"
        f"🔗 **رابط البوت:** `https://t.me/{context.bot.username}`",
        parse_mode='Markdown'
    )

# أوامر التداول التلقائي
async def auto_trading_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض حالة التداول التلقائي"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    
    try:
        from auto_trading_system import auto_trading
        
        config = auto_trading.trading_config
        stats = auto_trading.get_trading_statistics()
        
        status_icon = "🟢" if config.get('auto_trading_enabled', False) else "🔴"
        status_text = "مفعل" if config.get('auto_trading_enabled', False) else "متوقف"
        
        message = f"""
🤖 **حالة التداول التلقائي** 🤖

{status_icon} **الحالة:** {status_text}

📊 **الإحصائيات:**
• إجمالي الصفقات: {stats.get('total_trades', 0)}
• الصفقات النشطة: {stats.get('active_trades', 0)}
• الصفقات المغلقة: {stats.get('closed_trades', 0)}
• معدل النجاح: {stats.get('win_rate', 0)}%
• إجمالي النقاط: {stats.get('total_pips', 0):+.1f}

⚙️ **الإعدادات:**
• الحد الأدنى للثقة: {config.get('min_confidence', 75)}%
• أقصى صفقات يومية: {config.get('max_daily_trades', 5)}
• فترة المراقبة: {config.get('monitoring_interval', 300)} ثانية

**الأوامر المتاحة:**
• `/enable_trading` - تفعيل التداول التلقائي
• `/disable_trading` - إيقاف التداول التلقائي
• `/trading_stats` - إحصائيات مفصلة
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب حالة التداول: {str(e)}")

async def enable_auto_trading_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل التداول التلقائي"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    
    try:
        from auto_trading_system import auto_trading
        
        if auto_trading.enable_auto_trading():
            await update.message.reply_text(
                "✅ **تم تفعيل التداول التلقائي!**\n\n"
                "🤖 سيبدأ النظام بمراقبة الأسواق وإرسال الإشارات التلقائية.\n"
                "🔔 ستصل الإشارات للمجموعات المفعلة.\n\n"
                "⚠️ **تذكير:** هذه إشارات تحليلية وليست نصائح استثمارية.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ فشل في تفعيل التداول التلقائي.")
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تفعيل التداول: {str(e)}")

async def disable_auto_trading_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إيقاف التداول التلقائي"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 هذا الأمر مخصص للمشرفين فقط.")
        return
    
    try:
        from auto_trading_system import auto_trading
        
        if auto_trading.disable_auto_trading():
            await update.message.reply_text(
                "🔴 **تم إيقاف التداول التلقائي**\n\n"
                "🛑 توقف النظام عن إرسال إشارات جديدة.\n"
                "📊 الصفقات النشطة ستستمر في المراقبة.\n\n"
                "💡 يمكنك إعادة تفعيله باستخدام `/enable_trading`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ فشل في إيقاف التداول التلقائي.")
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في إيقاف التداول: {str(e)}")

async def trading_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إحصائيات التداول المفصلة"""
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("🚫 ليس لديك صلاحية استخدام هذا الأمر.")
        return
    
    try:
        from auto_trading_system import auto_trading
        
        stats = auto_trading.get_trading_statistics()
        active_trades = [trade for trade in auto_trading.active_trades.values() if trade['status'] == 'active']
        
        message = f"""
📊 **إحصائيات التداول المفصلة** 📊

**📈 الأداء العام:**
• إجمالي الصفقات: {stats.get('total_trades', 0)}
• الصفقات المغلقة: {stats.get('closed_trades', 0)}
• الصفقات النشطة: {stats.get('active_trades', 0)}

**🎯 معدلات النجاح:**
• الصفقات الرابحة: {stats.get('winning_trades', 0)}
• الصفقات الخاسرة: {stats.get('losing_trades', 0)}
• معدل النجاح: {stats.get('win_rate', 0)}%

**💰 النقاط:**
• إجمالي النقاط: {stats.get('total_pips', 0):+.1f}
• متوسط النقاط: {stats.get('average_pips', 0):+.1f}
        """
        
        if active_trades:
            message += f"\n\n**🔄 الصفقات النشطة ({len(active_trades)}):**\n"
            for trade in active_trades[:5]:  # أول 5 صفقات فقط
                symbol = trade['symbol']
                trade_type = trade['type']
                entry_price = trade['entry_price']
                current_price = trade.get('current_price', entry_price)
                
                if trade_type == 'شراء':
                    pips = (current_price - entry_price) * 10000
                else:
                    pips = (entry_price - current_price) * 10000
                
                pips_text = f"{pips:+.1f} نقطة"
                message += f"• `{symbol}` - {trade_type} - {pips_text}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب الإحصائيات: {str(e)}")