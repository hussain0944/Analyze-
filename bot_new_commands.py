"""
أوامر البوت الجديدة للتنبيهات والتقارير والواجهة المحسنة
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import is_authorized, is_admin
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