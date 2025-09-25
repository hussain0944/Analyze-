"""
أوامر التداول المتقدم ومعالجة الصور
"""

import asyncio
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils import is_authorized, is_admin, load_permissions
import json
import os
from datetime import datetime
import io

async def advanced_trading_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض حالة التداول المتقدم"""
    try:
        if not is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ غير مصرح لك باستخدام هذا الأمر.")
            return
        
        try:
            from advanced_trading_system import advanced_trading
            
            # تحميل إعدادات التداول المتقدم
            config = advanced_trading.trading_config
            
            # تحميل الصفقات النشطة
            advanced_trading.load_active_trades()
            active_trades = advanced_trading.active_trades
            
            # إحصائيات سريعة
            total_trades = len(active_trades)
            active_count = sum(1 for trade in active_trades.values() if trade.get('status') not in ['closed', 'cancelled'])
            closed_trades = sum(1 for trade in active_trades.values() if trade.get('status') == 'closed')
            
            winning_trades = 0
            total_pips = 0
            
            for trade in active_trades.values():
                if trade.get('status') == 'closed':
                    pips = trade.get('pips_result', 0)
                    total_pips += pips
                    if pips > 0:
                        winning_trades += 1
            
            win_rate = (winning_trades / closed_trades * 100) if closed_trades > 0 else 0
            
            status_emoji = "🟢" if config.get('auto_trading_enabled', False) else "🔴"
            
            message = f"""
🤖 **نظام التداول المتقدم**

{status_emoji} **الحالة:** {"نشط" if config.get('auto_trading_enabled', False) else "متوقف"}

⚙️ **إعدادات النظام:**
🎯 أقل نسبة ثقة: {config.get('min_confidence', 85)}%
📊 عدد الرموز المراقبة: {len(advanced_trading.supported_symbols.get('forex_majors', [])) + len(advanced_trading.supported_symbols.get('commodities', [])) + len(advanced_trading.supported_symbols.get('crypto', []))}
⏰ الأطر الزمنية: {', '.join(config.get('timeframes_to_analyze', []))}
🎯 عدد الأهداف: {config.get('targets', 3)}
🚪 مناطق الدخول: {config.get('entry_zones', 2)}

📈 **إحصائيات الصفقات:**
📊 إجمالي الصفقات: {total_trades}
🔄 الصفقات النشطة: {active_count}
✅ الصفقات المغلقة: {closed_trades}
🏆 معدل النجاح: {win_rate:.1f}%
💰 إجمالي النقاط: {total_pips:+.1f}

🔄 **مراقبة متقدمة:**
• تحليل متعدد الأطر الزمنية
• ثلاثة أهداف لكل صفقة
• منطقتان للدخول
• وقف الخسارة المتحرك
• تنبيهات عند تحقق كل هدف

🕐 **آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # أزرار التحكم (للمشرفين فقط)
            if is_admin(update.effective_user.id):
                keyboard = []
                if config.get('auto_trading_enabled', False):
                    keyboard.append([InlineKeyboardButton("⏸️ إيقاف التداول المتقدم", callback_data="disable_advanced")])
                else:
                    keyboard.append([InlineKeyboardButton("▶️ تفعيل التداول المتقدم", callback_data="enable_advanced")])
                
                keyboard.append([InlineKeyboardButton("📊 تفاصيل الصفقات النشطة", callback_data="advanced_active_trades")])
                keyboard.append([InlineKeyboardButton("⚙️ إعدادات النظام", callback_data="advanced_settings")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في الوصول لنظام التداول المتقدم: {e}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

async def enable_advanced_trading_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل التداول المتقدم (للمشرفين فقط)"""
    try:
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ هذا الأمر مخصص للمشرفين فقط.")
            return
        
        from advanced_trading_system import advanced_trading
        
        advanced_trading.trading_config['auto_trading_enabled'] = True
        advanced_trading.save_trading_config()
        
        await update.message.reply_text("""
✅ **تم تفعيل التداول المتقدم بنجاح!**

🚀 **الميزات المفعلة:**
• تحليل متعدد الأطر الزمنية (1m - 1h)
• ثلاثة أهداف لكل صفقة
• منطقتان للدخول
• وقف الخسارة المتحرك
• نسبة ثقة عالية (85%+)
• تنبيهات فورية عند تحقق الأهداف

⚠️ **تنبيه:** سيتم تحليل جميع الأزواج والسلع والعملات الرقمية تلقائياً وإرسال الصفقات عالية الجودة فقط.
""", parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ في تفعيل التداول المتقدم: {e}")

async def disable_advanced_trading_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إيقاف التداول المتقدم (للمشرفين فقط)"""
    try:
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ هذا الأمر مخصص للمشرفين فقط.")
            return
        
        from advanced_trading_system import advanced_trading
        
        advanced_trading.trading_config['auto_trading_enabled'] = False
        advanced_trading.save_trading_config()
        
        await update.message.reply_text("""
⏸️ **تم إيقاف التداول المتقدم**

🔄 **الصفقات الحالية:**
• الصفقات النشطة ستستمر في المراقبة
• لن يتم إرسال صفقات جديدة
• التنبيهات ستستمر للصفقات النشطة

💡 **لإعادة التفعيل:** استخدم الأمر `/enable_advanced`
""", parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ في إيقاف التداول المتقدم: {e}")

async def advanced_trading_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إحصائيات التداول المتقدم المفصلة"""
    try:
        if not is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ غير مصرح لك باستخدام هذا الأمر.")
            return
        
        from advanced_trading_system import advanced_trading
        
        # تحميل الصفقات
        advanced_trading.load_active_trades()
        trades = advanced_trading.active_trades
        
        if not trades:
            await update.message.reply_text("📊 لا توجد صفقات في النظام المتقدم حتى الآن.")
            return
        
        # تحليل الإحصائيات
        total_trades = len(trades)
        active_trades = [t for t in trades.values() if t.get('status') not in ['closed', 'cancelled']]
        closed_trades = [t for t in trades.values() if t.get('status') == 'closed']
        
        winning_trades = [t for t in closed_trades if t.get('pips_result', 0) > 0]
        losing_trades = [t for t in closed_trades if t.get('pips_result', 0) < 0]
        
        total_pips = sum(t.get('pips_result', 0) for t in closed_trades)
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
        avg_pips = total_pips / len(closed_trades) if closed_trades else 0
        
        # تحليل بحسب الرمز
        symbol_stats = {}
        for trade in closed_trades:
            symbol = trade.get('symbol', 'UNKNOWN')
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {'trades': 0, 'wins': 0, 'pips': 0}
            
            symbol_stats[symbol]['trades'] += 1
            symbol_stats[symbol]['pips'] += trade.get('pips_result', 0)
            if trade.get('pips_result', 0) > 0:
                symbol_stats[symbol]['wins'] += 1
        
        message = f"""
📊 **إحصائيات التداول المتقدم المفصلة**

📈 **ملخص عام:**
• إجمالي الصفقات: {total_trades}
• الصفقات النشطة: {len(active_trades)}
• الصفقات المغلقة: {len(closed_trades)}
• الصفقات الرابحة: {len(winning_trades)}
• الصفقات الخاسرة: {len(losing_trades)}

🎯 **نتائج الأداء:**
• معدل النجاح: {win_rate:.1f}%
• إجمالي النقاط: {total_pips:+.1f}
• متوسط النقاط: {avg_pips:+.1f}

💰 **أفضل الصفقات:**"""
        
        # أفضل 3 صفقات
        best_trades = sorted(closed_trades, key=lambda x: x.get('pips_result', 0), reverse=True)[:3]
        for i, trade in enumerate(best_trades, 1):
            message += f"\n{i}. {trade.get('symbol', 'UNKNOWN')}: {trade.get('pips_result', 0):+.1f} نقطة"
        
        message += f"\n\n📊 **إحصائيات بحسب الرمز:**"
        
        # أفضل 5 رموز
        sorted_symbols = sorted(symbol_stats.items(), key=lambda x: x[1]['pips'], reverse=True)[:5]
        for symbol, stats in sorted_symbols:
            win_rate_symbol = (stats['wins'] / stats['trades'] * 100) if stats['trades'] > 0 else 0
            message += f"\n• {symbol}: {stats['pips']:+.1f} نقاط ({win_rate_symbol:.0f}% نجاح)"
        
        if active_trades:
            message += f"\n\n🔄 **الصفقات النشطة:**"
            for trade in active_trades[:5]:  # أول 5 صفقات نشطة
                confidence = trade.get('confidence', 0)
                symbol = trade.get('symbol', 'UNKNOWN')
                trade_type = trade.get('type', 'غير محدد')
                message += f"\n• {symbol} ({trade_type}) - ثقة {confidence}%"
        
        message += f"\n\n🕐 **آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ في عرض الإحصائيات: {e}")

async def handle_chart_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج تحليل الصور"""
    try:
        if not is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ غير مصرح لك باستخدام هذا الأمر.")
            return
        
        if not update.message.photo:
            return
        
        await update.message.reply_text("🖼️ جاري تحليل الصورة... قد يستغرق هذا بضع لحظات...")
        
        try:
            # الحصول على أكبر حجم للصورة
            photo = update.message.photo[-1]
            
            # تحميل الصورة
            photo_file = await photo.get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            # تحليل الصورة
            from image_analysis_system import image_analyzer
            
            chat_type = "group" if update.effective_chat.type in ["group", "supergroup"] else "private"
            analysis_result = await image_analyzer.analyze_chart_image(
                bytes(photo_bytes), 
                update.effective_user.id, 
                chat_type
            )
            
            await update.message.reply_text(analysis_result, parse_mode='Markdown')
            
        except ImportError:
            await update.message.reply_text("""
❌ **نظام تحليل الصور غير متاح حالياً**

🔧 **السبب:** مكتبات معالجة الصور مفقودة

💡 **البديل:** يمكنك:
• إرسال رابط الرسم البياني لتحليله يدوياً
• استخدام أوامر التحليل المباشر مثل `/analyze [SYMBOL]`
• طلب تحليل رمز معين
""", parse_mode='Markdown')
        
        except Exception as e:
            await update.message.reply_text(f"""
❌ **فشل في تحليل الصورة**

🔍 **السبب المحتمل:**
• الصورة غير واضحة أو منخفضة الجودة
• ليست رسماً بيانياً مالياً
• خطأ تقني في المعالجة

💡 **يرجى المحاولة مع:**
• صورة أوضح وأكبر حجماً
• رسم بياني يحتوي على الأسعار والزمن
• إزالة أي نصوص أو عناصر إضافية

**تفاصيل الخطأ:** {e}
""", parse_mode='Markdown')
            
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ في معالجة الصورة: {e}")

async def timeframes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الأطر الزمنية المدعومة"""
    try:
        if not is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ غير مصرح لك باستخدام هذا الأمر.")
            return
        
        message = """
⏰ **الأطر الزمنية المدعومة في النظام المتقدم**

📊 **أطر التحليل:**
• **1m** - دقيقة واحدة (للتحليل السريع)
• **5m** - 5 دقائق (للدخول الدقيق)
• **15m** - 15 دقيقة (للاتجاه قصير المدى)
• **30m** - 30 دقيقة (للاتجاه متوسط المدى)
• **1h** - ساعة واحدة (للاتجاه العام)

🔍 **كيفية عمل التحليل:**
1. **التحليل المتعدد:** يحلل النظام جميع الأطر الزمنية
2. **الإجماع:** يبحث عن إجماع بين الأطر المختلفة
3. **الثقة العالية:** يتطلب ثقة 85%+ من عدة أطر
4. **الإطار الموصى به:** يحدد أفضل إطار زمني للصفقة

⚙️ **إعدادات متقدمة:**
• تحليل كل إطار زمني بشكل منفصل
• دمج الإشارات للحصول على توصية نهائية
• تحديد أقوى إطار زمني للصفقة
• تتبع الأداء لكل إطار زمني

🎯 **للحصول على أفضل النتائج:**
• الإشارات من الأطر الزمنية الأعلى أكثر موثوقية
• الدخول يكون بناءً على الأطر الأقل
• وقف الخسارة والأهداف تحسب من التحليل الشامل

📈 **مثال على التحليل:**
إذا كان الاتجاه صاعد في 1h و 30m ولكن هابط في 5m، سيختار النظام التوقيت المناسب للدخول عند تحسن الإطار قصير المدى.
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

async def supported_symbols_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الرموز المدعومة"""
    try:
        if not is_authorized(update.effective_user.id):
            await update.message.reply_text("❌ غير مصرح لك باستخدام هذا الأمر.")
            return
        
        try:
            from advanced_trading_system import advanced_trading
            symbols = advanced_trading.supported_symbols
            
            message = """
📈 **الرموز المدعومة في النظام المتقدم**

💱 **أزواج الفوركس الرئيسية:**
"""
            
            for symbol in symbols.get('forex_majors', []):
                clean_symbol = symbol.replace('=X', '')
                message += f"• {clean_symbol}\n"
            
            message += "\n💱 **أزواج الفوركس الثانوية:**\n"
            for symbol in symbols.get('forex_minors', []):
                clean_symbol = symbol.replace('=X', '')
                message += f"• {clean_symbol}\n"
            
            message += "\n🥇 **السلع:**\n"
            commodity_names = {
                'GC=F': 'الذهب (GOLD)',
                'SI=F': 'الفضة (SILVER)', 
                'CL=F': 'النفط الخام (OIL)',
                'BZ=F': 'برنت (BRENT)',
                'NG=F': 'الغاز الطبيعي (NATGAS)',
                'HG=F': 'النحاس (COPPER)'
            }
            
            for symbol in symbols.get('commodities', []):
                name = commodity_names.get(symbol, symbol)
                message += f"• {name}\n"
            
            message += "\n📊 **المؤشرات:**\n"
            index_names = {
                '^GSPC': 'S&P 500',
                '^DJI': 'Dow Jones',
                '^IXIC': 'NASDAQ',
                '^FTSE': 'FTSE 100',
                '^GDAXI': 'DAX',
                '^N225': 'Nikkei'
            }
            
            for symbol in symbols.get('indices', []):
                name = index_names.get(symbol, symbol)
                message += f"• {name}\n"
            
            message += "\n₿ **العملات الرقمية:**\n"
            for symbol in symbols.get('crypto', []):
                clean_symbol = symbol.replace('-USD', '')
                message += f"• {clean_symbol}\n"
            
            total_symbols = sum(len(category) for category in symbols.values())
            
            message += f"""

📊 **إجمالي الرموز:** {total_symbols}

🔍 **كيفية الاستخدام:**
• النظام يراقب جميع هذه الرموز تلقائياً
• يرسل إشارات فقط للفرص عالية الجودة
• كل رمز يحلل بدقة حسب خصائصه
• حساب النقاط مخصص لكل نوع من الأصول

⚙️ **للتحليل اليدوي:** استخدم `/analyze [SYMBOL]`
"""
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في الوصول لقائمة الرموز: {e}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

def register_advanced_handlers(app):
    """تسجيل معالجات الأوامر المتقدمة"""
    
    # أوامر التداول المتقدم
    app.add_handler(CommandHandler("advanced_trading", advanced_trading_command))
    app.add_handler(CommandHandler("enable_advanced", enable_advanced_trading_command))
    app.add_handler(CommandHandler("disable_advanced", disable_advanced_trading_command))
    app.add_handler(CommandHandler("advanced_stats", advanced_trading_stats_command))
    
    # أوامر الدعم
    app.add_handler(CommandHandler("timeframes", timeframes_command))
    app.add_handler(CommandHandler("symbols", supported_symbols_command))
    app.add_handler(CommandHandler("supported_symbols", supported_symbols_command))
    
    # معالج الصور
    app.add_handler(MessageHandler(filters.PHOTO, handle_chart_image))
    
    print("✅ تم تسجيل معالجات الأوامر المتقدمة")