"""
نظام التداول التلقائي وإرسال ومتابعة الصفقات
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from data_collector import DataCollector
from recommendation_system import RecommendationSystem
from utils import load_permissions, send_to_telegram, send_alert_to_enabled_groups
import os

class AutoTradingSystem:
    def __init__(self):
        self.data_collector = DataCollector()
        self.recommendation_system = RecommendationSystem()
        self.active_trades = {}
        self.trading_config = self.load_trading_config()
        self.bot_token = os.getenv("BOT_TOKEN")
        
    def load_trading_config(self):
        """تحميل إعدادات التداول"""
        try:
            with open("trading_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # إنشاء إعدادات افتراضية
            default_config = {
                "auto_trading_enabled": False,
                "symbols_to_monitor": ["EURUSD", "GBPUSD", "USDJPY", "GOLD", "BTC-USD"],
                "min_confidence": 75,  # الحد الأدنى للثقة لإرسال الصفقة
                "risk_per_trade": 2,   # نسبة المخاطرة لكل صفقة
                "max_daily_trades": 5,
                "trading_hours": {"start": "08:00", "end": "18:00"},
                "stop_loss_pips": 30,
                "take_profit_pips": 60,
                "monitoring_interval": 300,  # 5 دقائق
                "notification_groups": []
            }
            
            with open("trading_config.json", "w") as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def save_trading_config(self):
        """حفظ إعدادات التداول"""
        with open("trading_config.json", "w") as f:
            json.dump(self.trading_config, f, indent=2)
    
    def load_active_trades(self):
        """تحميل الصفقات النشطة"""
        try:
            with open("active_trades.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_active_trades(self):
        """حفظ الصفقات النشطة"""
        with open("active_trades.json", "w") as f:
            json.dump(self.active_trades, f, indent=2, default=str)
    
    async def generate_trading_signal(self, symbol):
        """إنتاج إشارة تداول للرمز المحدد"""
        try:
            print(f"🔍 فحص إشارة تداول للرمز: {symbol}")
            
            # الحصول على التوصية
            recommendation = self.recommendation_system.analyze_symbol(symbol)
            
            if not recommendation:
                return None
            
            confidence = recommendation.get('confidence', 0)
            signal_type = recommendation.get('type', 'محايد')
            
            # فحص إذا كانت الثقة كافية
            if confidence < self.trading_config['min_confidence']:
                print(f"⚠️ ثقة منخفضة للرمز {symbol}: {confidence}%")
                return None
            
            # فحص إذا كان النوع قابل للتداول
            if signal_type not in ['شراء', 'بيع']:
                print(f"⚠️ إشارة محايدة للرمز {symbol}")
                return None
            
            # الحصول على السعر الحالي
            current_price_data = self.data_collector.get_current_price(symbol)
            if not current_price_data:
                print(f"❌ فشل في الحصول على السعر الحالي للرمز {symbol}")
                return None
            
            current_price = current_price_data['price']
            
            # حساب مستويات الدخول والخروج
            if signal_type == 'شراء':
                entry_price = current_price
                stop_loss = entry_price - (self.trading_config['stop_loss_pips'] / 10000)
                take_profit = entry_price + (self.trading_config['take_profit_pips'] / 10000)
            else:  # بيع
                entry_price = current_price
                stop_loss = entry_price + (self.trading_config['stop_loss_pips'] / 10000)
                take_profit = entry_price - (self.trading_config['take_profit_pips'] / 10000)
            
            signal = {
                'symbol': symbol,
                'type': signal_type,
                'confidence': confidence,
                'entry_price': entry_price,
                'current_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': datetime.now(),
                'recommendation_details': recommendation,
                'status': 'pending',
                'risk_reward_ratio': abs(take_profit - entry_price) / abs(stop_loss - entry_price)
            }
            
            print(f"✅ إشارة تداول جديدة: {symbol} - {signal_type} - {confidence}%")
            return signal
            
        except Exception as e:
            print(f"❌ خطأ في إنتاج إشارة التداول للرمز {symbol}: {e}")
            return None
    
    async def send_trading_signal(self, signal):
        """إرسال إشارة التداول للمستخدمين"""
        try:
            signal_id = f"{signal['symbol']}_{int(signal['timestamp'].timestamp())}"
            
            # تنسيق رسالة الإشارة
            direction_emoji = "🟢" if signal['type'] == 'شراء' else "🔴"
            
            message = f"""
{direction_emoji} **إشارة تداول جديدة** {direction_emoji}

📊 **الرمز:** `{signal['symbol']}`
📈 **النوع:** {signal['type']}
🎯 **الثقة:** {signal['confidence']:.1f}%
💰 **سعر الدخول:** `{signal['entry_price']:.5f}`

🛑 **وقف الخسارة:** `{signal['stop_loss']:.5f}`
🎯 **جني الأرباح:** `{signal['take_profit']:.5f}`
📊 **نسبة المخاطرة/المكافأة:** 1:{signal['risk_reward_ratio']:.1f}

⏰ **الوقت:** {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

🔔 **معرف الإشارة:** `{signal_id}`

**⚠️ تنبيه:** هذه إشارة تحليلية وليست نصيحة استثمارية. يرجى إدارة المخاطر بعناية.
            """
            
            # إرسال للمجموعات المفعلة
            if self.bot_token:
                send_alert_to_enabled_groups(message, self.bot_token)
            
            # إضافة الصفقة للصفقات النشطة
            self.active_trades[signal_id] = signal
            self.active_trades[signal_id]['id'] = signal_id
            self.active_trades[signal_id]['status'] = 'active'
            self.save_active_trades()
            
            print(f"✅ تم إرسال إشارة التداول: {signal_id}")
            return signal_id
            
        except Exception as e:
            print(f"❌ خطأ في إرسال إشارة التداول: {e}")
            return None
    
    async def monitor_active_trades(self):
        """مراقبة الصفقات النشطة"""
        try:
            if not self.active_trades:
                return
                
            print(f"📊 مراقبة {len(self.active_trades)} صفقة نشطة...")
            
            for trade_id, trade in list(self.active_trades.items()):
                if trade['status'] != 'active':
                    continue
                    
                try:
                    # الحصول على السعر الحالي
                    current_price_data = self.data_collector.get_current_price(trade['symbol'])
                    
                    if not current_price_data:
                        continue
                    
                    current_price = current_price_data['price']
                    trade['current_price'] = current_price
                    
                    # فحص وقف الخسارة وجني الأرباح
                    trade_closed = False
                    close_reason = ""
                    
                    if trade['type'] == 'شراء':
                        if current_price <= trade['stop_loss']:
                            trade_closed = True
                            close_reason = "وقف خسارة"
                            trade['result'] = 'loss'
                        elif current_price >= trade['take_profit']:
                            trade_closed = True
                            close_reason = "جني أرباح"
                            trade['result'] = 'profit'
                    else:  # بيع
                        if current_price >= trade['stop_loss']:
                            trade_closed = True
                            close_reason = "وقف خسارة"
                            trade['result'] = 'loss'
                        elif current_price <= trade['take_profit']:
                            trade_closed = True
                            close_reason = "جني أرباح"
                            trade['result'] = 'profit'
                    
                    if trade_closed:
                        await self.close_trade(trade_id, current_price, close_reason)
                    
                    # حفظ التحديثات
                    self.save_active_trades()
                    
                except Exception as trade_error:
                    print(f"❌ خطأ في مراقبة الصفقة {trade_id}: {trade_error}")
            
        except Exception as e:
            print(f"❌ خطأ في مراقبة الصفقات النشطة: {e}")
    
    async def close_trade(self, trade_id, close_price, reason):
        """إغلاق صفقة"""
        try:
            if trade_id not in self.active_trades:
                return
            
            trade = self.active_trades[trade_id]
            trade['close_price'] = close_price
            trade['close_time'] = datetime.now()
            trade['close_reason'] = reason
            trade['status'] = 'closed'
            
            # حساب النتيجة
            if trade['type'] == 'شراء':
                pips = (close_price - trade['entry_price']) * 10000
            else:  # بيع
                pips = (trade['entry_price'] - close_price) * 10000
            
            trade['pips'] = round(pips, 1)
            
            # تنسيق رسالة الإغلاق
            result_emoji = "✅" if trade['result'] == 'profit' else "❌"
            
            message = f"""
{result_emoji} **إغلاق صفقة** {result_emoji}

📊 **الرمز:** `{trade['symbol']}`
📈 **النوع:** {trade['type']}
💰 **سعر الدخول:** `{trade['entry_price']:.5f}`
💰 **سعر الإغلاق:** `{close_price:.5f}`

📊 **النتيجة:** {pips:+.1f} نقطة
📝 **السبب:** {reason}
⏰ **مدة الصفقة:** {self._calculate_trade_duration(trade)}

**معرف الصفقة:** `{trade_id}`
            """
            
            # إرسال الإشعار
            if self.bot_token:
                send_alert_to_enabled_groups(message, self.bot_token)
            
            print(f"✅ تم إغلاق الصفقة {trade_id}: {pips:+.1f} نقطة - {reason}")
            
        except Exception as e:
            print(f"❌ خطأ في إغلاق الصفقة {trade_id}: {e}")
    
    def _calculate_trade_duration(self, trade):
        """حساب مدة الصفقة"""
        try:
            start_time = trade['timestamp']
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            
            end_time = trade.get('close_time', datetime.now())
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)
            
            duration = end_time - start_time
            
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            
            if hours > 0:
                return f"{hours}س {minutes}د"
            else:
                return f"{minutes}د"
                
        except Exception:
            return "غير محدد"
    
    async def auto_trading_loop(self):
        """الحلقة الرئيسية للتداول التلقائي"""
        while True:
            try:
                if not self.trading_config.get('auto_trading_enabled', False):
                    await asyncio.sleep(60)  # انتظار دقيقة واحدة
                    continue
                
                print("🤖 تشغيل دورة التداول التلقائي...")
                
                # مراقبة الصفقات النشطة
                await self.monitor_active_trades()
                
                # فحص إشارات جديدة
                symbols = self.trading_config.get('symbols_to_monitor', [])
                
                for symbol in symbols:
                    try:
                        # فحص إذا وصلنا للحد الأقصى من الصفقات اليومية
                        daily_trades = self._count_daily_trades()
                        max_daily_trades = self.trading_config.get('max_daily_trades', 5)
                        
                        if daily_trades >= max_daily_trades:
                            print(f"⚠️ تم الوصول للحد الأقصى من الصفقات اليومية: {daily_trades}")
                            break
                        
                        # فحص إذا كان لدينا صفقة نشطة للرمز
                        if self._has_active_trade_for_symbol(symbol):
                            continue
                        
                        # إنتاج إشارة جديدة
                        signal = await self.generate_trading_signal(symbol)
                        
                        if signal:
                            await self.send_trading_signal(signal)
                            await asyncio.sleep(5)  # انتظار بين الإشارات
                    
                    except Exception as symbol_error:
                        print(f"❌ خطأ في معالجة الرمز {symbol}: {symbol_error}")
                
                # انتظار الفترة التالية
                interval = self.trading_config.get('monitoring_interval', 300)
                print(f"⏳ انتظار {interval} ثانية حتى الدورة التالية...")
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"❌ خطأ في حلقة التداول التلقائي: {e}")
                await asyncio.sleep(60)  # انتظار دقيقة في حالة الخطأ
    
    def _count_daily_trades(self):
        """عد الصفقات اليومية"""
        today = datetime.now().date()
        count = 0
        
        for trade in self.active_trades.values():
            trade_date = trade['timestamp']
            if isinstance(trade_date, str):
                trade_date = datetime.fromisoformat(trade_date)
            
            if trade_date.date() == today:
                count += 1
        
        return count
    
    def _has_active_trade_for_symbol(self, symbol):
        """فحص إذا كان لدينا صفقة نشطة للرمز"""
        for trade in self.active_trades.values():
            if trade['symbol'] == symbol and trade['status'] == 'active':
                return True
        return False
    
    def enable_auto_trading(self):
        """تفعيل التداول التلقائي"""
        self.trading_config['auto_trading_enabled'] = True
        self.save_trading_config()
        return True
    
    def disable_auto_trading(self):
        """إيقاف التداول التلقائي"""
        self.trading_config['auto_trading_enabled'] = False
        self.save_trading_config()
        return True
    
    def get_trading_statistics(self):
        """إحصائيات التداول"""
        try:
            total_trades = len(self.active_trades)
            if total_trades == 0:
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0,
                    'total_pips': 0,
                    'average_pips': 0
                }
            
            winning_trades = 0
            losing_trades = 0
            total_pips = 0
            
            for trade in self.active_trades.values():
                if trade['status'] == 'closed':
                    pips = trade.get('pips', 0)
                    total_pips += pips
                    
                    if pips > 0:
                        winning_trades += 1
                    else:
                        losing_trades += 1
            
            closed_trades = winning_trades + losing_trades
            win_rate = (winning_trades / closed_trades * 100) if closed_trades > 0 else 0
            average_pips = total_pips / closed_trades if closed_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'closed_trades': closed_trades,
                'active_trades': total_trades - closed_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 1),
                'total_pips': round(total_pips, 1),
                'average_pips': round(average_pips, 1)
            }
            
        except Exception as e:
            print(f"خطأ في حساب الإحصائيات: {e}")
            return {}

# إنشاء نظام التداول التلقائي
auto_trading = AutoTradingSystem()