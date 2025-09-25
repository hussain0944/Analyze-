"""
نظام التداول المتقدم بدقة عالية
يتضمن: ثلاثة أهداف، منطقتي دخول، تحليل متعدد الأطر الزمنية، تتبع متقدم
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import pandas as pd
import numpy as np
from data_collector import DataCollector
from recommendation_system import RecommendationSystem
from utils import load_permissions, send_to_telegram
import os

class AdvancedTradingSystem:
    def __init__(self):
        self.data_collector = DataCollector()
        self.recommendation_system = RecommendationSystem()
        self.active_trades = {}
        self.trading_config = self.load_advanced_config()
        self.bot_token = os.getenv("BOT_TOKEN")
        
        # قائمة شاملة للرموز المدعومة
        self.supported_symbols = {
            # أزواج الفوركس الرئيسية
            'forex_majors': [
                'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 
                'AUDUSD=X', 'USDCAD=X', 'NZDUSD=X'
            ],
            # أزواج الفوركس الثانوية
            'forex_minors': [
                'EURGBP=X', 'EURJPY=X', 'EURCHF=X', 'EURAUD=X',
                'GBPJPY=X', 'GBPCHF=X', 'AUDJPY=X', 'CHFJPY=X'
            ],
            # السلع
            'commodities': [
                'GC=F',    # الذهب
                'SI=F',    # الفضة
                'CL=F',    # النفط الخام
                'BZ=F',    # برنت
                'NG=F',    # الغاز الطبيعي
                'HG=F',    # النحاس
            ],
            # المؤشرات
            'indices': [
                '^GSPC',   # S&P 500
                '^DJI',    # Dow Jones
                '^IXIC',   # NASDAQ
                '^FTSE',   # FTSE 100
                '^GDAXI',  # DAX
                '^N225',   # Nikkei
            ],
            # العملات الرقمية
            'crypto': [
                'BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD',
                'ADA-USD', 'SOL-USD', 'DOGE-USD', 'MATIC-USD',
                'DOT-USD', 'AVAX-USD', 'LINK-USD', 'UNI-USD'
            ]
        }
        
        # الأطر الزمنية المدعومة
        self.timeframes = ['1m', '5m', '15m', '30m', '1h']
        
    def load_advanced_config(self):
        """تحميل إعدادات التداول المتقدمة"""
        try:
            with open("advanced_trading_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            default_config = {
                "auto_trading_enabled": False,
                "min_confidence": 85,  # رفع معايير الثقة
                "risk_per_trade": 1.5,
                "max_daily_trades": 3,  # تقليل عدد الصفقات لضمان الجودة
                "timeframes_to_analyze": ["1m", "5m", "15m", "30m", "1h"],
                "entry_zones": 2,  # منطقتين للدخول
                "targets": 3,      # ثلاثة أهداف
                "trailing_stop": True,  # تحريك وقف الخسارة
                "partial_close": True,  # إغلاق جزئي عند الأهداف
                "pip_precision": {
                    "JPY_pairs": 2,     # أزواج الين
                    "other_pairs": 4,   # باقي الأزواج
                    "metals": 2,        # المعادن
                    "oil": 2,          # النفط
                    "indices": 1,       # المؤشرات
                    "crypto": 2        # العملات الرقمية
                },
                "risk_reward_ratios": [1.5, 2.5, 4.0],  # نسب المخاطرة للأهداف الثلاثة
                "notification_groups": []
            }
            
            with open("advanced_trading_config.json", "w") as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def calculate_pip_value(self, symbol: str, price: float) -> float:
        """حساب قيمة النقطة بدقة عالية حسب نوع الرمز"""
        symbol_upper = symbol.upper()
        
        # أزواج الين اليابانية
        if 'JPY' in symbol_upper:
            return 0.01
        # أزواج العملات العادية
        elif any(curr in symbol_upper for curr in ['USD', 'EUR', 'GBP', 'CHF', 'AUD', 'CAD', 'NZD']):
            return 0.0001
        # المعادن
        elif symbol_upper in ['GC=F', 'GOLD', 'XAUUSD']:  # الذهب
            return 0.1
        elif symbol_upper in ['SI=F', 'SILVER', 'XAGUSD']:  # الفضة
            return 0.001
        # النفط
        elif symbol_upper in ['CL=F', 'BZ=F']:
            return 0.01
        # المؤشرات
        elif symbol_upper.startswith('^') or 'INDEX' in symbol_upper:
            return 1.0
        # العملات الرقمية
        elif '-USD' in symbol_upper or 'USDT' in symbol_upper:
            if 'BTC' in symbol_upper:
                return 1.0
            elif 'ETH' in symbol_upper:
                return 0.1
            else:
                return 0.0001
        else:
            return 0.0001  # افتراضي
    
    def calculate_pips_difference(self, symbol: str, price1: float, price2: float) -> float:
        """حساب الفرق بالنقاط بين سعرين"""
        pip_value = self.calculate_pip_value(symbol, price1)
        return abs(price2 - price1) / pip_value
    
    def get_multi_timeframe_analysis(self, symbol: str) -> Dict:
        """تحليل متعدد الأطر الزمنية"""
        analyses = {}
        
        for timeframe in self.timeframes:
            try:
                # تحويل الإطار الزمني لتنسيق yfinance
                if timeframe == '1m':
                    period, interval = '1d', '1m'
                elif timeframe == '5m':
                    period, interval = '5d', '5m'
                elif timeframe == '15m':
                    period, interval = '1mo', '15m'
                elif timeframe == '30m':
                    period, interval = '1mo', '30m'
                elif timeframe == '1h':
                    period, interval = '3mo', '1h'
                else:
                    continue
                
                # الحصول على البيانات
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, interval=interval)
                
                if data.empty:
                    continue
                
                # التحليل الفني للإطار الزمني
                analysis = self._analyze_timeframe_data(data, timeframe)
                analyses[timeframe] = analysis
                
            except Exception as e:
                print(f"خطأ في تحليل الإطار الزمني {timeframe} للرمز {symbol}: {e}")
                continue
        
        return analyses
    
    def _analyze_timeframe_data(self, data: pd.DataFrame, timeframe: str) -> Dict:
        """تحليل بيانات إطار زمني واحد"""
        if data.empty or len(data) < 20:
            return {'trend': 'غير محدد', 'strength': 0, 'signals': []}
        
        # حساب المؤشرات
        closes = data['Close']
        highs = data['High']
        lows = data['Low']
        
        # المتوسطات المتحركة
        ma_short = closes.rolling(window=10).mean().iloc[-1]
        ma_long = closes.rolling(window=20).mean().iloc[-1]
        current_price = closes.iloc[-1]
        
        # RSI
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        
        # تحديد الاتجاه
        trend = 'صاعد' if current_price > ma_short > ma_long else 'هابط' if current_price < ma_short < ma_long else 'عرضي'
        
        # قوة الإشارة
        strength = 0
        signals = []
        
        if trend == 'صاعد':
            strength += 30
            if current_rsi < 70:  # ليس في منطقة التشبع الشرائي
                strength += 20
                signals.append('فرصة شراء')
        elif trend == 'هابط':
            strength += 30
            if current_rsi > 30:  # ليس في منطقة التشبع البيعي
                strength += 20
                signals.append('فرصة بيع')
        
        # إشارات إضافية
        if current_rsi > 70:
            signals.append('تشبع شرائي')
        elif current_rsi < 30:
            signals.append('تشبع بيعي')
        
        return {
            'trend': trend,
            'strength': min(strength, 100),
            'rsi': round(current_rsi, 2),
            'ma_short': round(ma_short, 5),
            'ma_long': round(ma_long, 5),
            'current_price': round(current_price, 5),
            'signals': signals
        }
    
    def generate_advanced_signal(self, symbol: str) -> Optional[Dict]:
        """إنتاج إشارة تداول متقدمة بدقة عالية"""
        try:
            print(f"🔍 تحليل متقدم للرمز: {symbol}")
            
            # تحليل متعدد الأطر الزمنية
            multi_tf_analysis = self.get_multi_timeframe_analysis(symbol)
            
            if not multi_tf_analysis:
                print(f"❌ فشل في التحليل متعدد الأطر الزمنية للرمز {symbol}")
                return None
            
            # تقييم الإجماع عبر الأطر الزمنية
            consensus = self._calculate_timeframe_consensus(multi_tf_analysis)
            
            if consensus['confidence'] < self.trading_config['min_confidence']:
                print(f"⚠️ إجماع ضعيف للرمز {symbol}: {consensus['confidence']}%")
                return None
            
            # الحصول على السعر الحالي
            current_price_data = self.data_collector.get_current_price(symbol)
            if not current_price_data:
                return None
            
            current_price = current_price_data['price']
            
            # تحديد نوع الإشارة
            signal_type = consensus['signal_type']
            if signal_type not in ['شراء', 'بيع']:
                return None
            
            # حساب منطقتي الدخول والأهداف الثلاثة
            entry_zones, targets, stop_loss = self._calculate_advanced_levels(
                symbol, current_price, signal_type, multi_tf_analysis
            )
            
            # إنشاء الإشارة المتقدمة
            signal = {
                'symbol': symbol,
                'type': signal_type,
                'confidence': consensus['confidence'],
                'current_price': current_price,
                'entry_zone_1': entry_zones[0],
                'entry_zone_2': entry_zones[1],
                'stop_loss': stop_loss,
                'target_1': targets[0],
                'target_2': targets[1],
                'target_3': targets[2],
                'timeframe_analysis': multi_tf_analysis,
                'consensus': consensus,
                'timestamp': datetime.now(),
                'risk_reward_ratios': self._calculate_risk_reward_ratios(entry_zones[0], targets, stop_loss),
                'pip_values': {
                    'entry_to_sl': self.calculate_pips_difference(symbol, entry_zones[0], stop_loss),
                    'entry_to_tp1': self.calculate_pips_difference(symbol, entry_zones[0], targets[0]),
                    'entry_to_tp2': self.calculate_pips_difference(symbol, entry_zones[0], targets[1]),
                    'entry_to_tp3': self.calculate_pips_difference(symbol, entry_zones[0], targets[2])
                },
                'recommended_timeframe': self._get_recommended_timeframe(multi_tf_analysis),
                'status': 'pending'
            }
            
            print(f"✅ إشارة متقدمة جديدة: {symbol} - {signal_type} - {consensus['confidence']}%")
            return signal
            
        except Exception as e:
            print(f"❌ خطأ في إنتاج الإشارة المتقدمة للرمز {symbol}: {e}")
            return None
    
    def _calculate_timeframe_consensus(self, multi_tf_analysis: Dict) -> Dict:
        """حساب الإجماع عبر الأطر الزمنية"""
        buy_signals = 0
        sell_signals = 0
        total_strength = 0
        
        for tf, analysis in multi_tf_analysis.items():
            strength = analysis.get('strength', 0)
            trend = analysis.get('trend', 'عرضي')
            
            total_strength += strength
            
            if trend == 'صاعد' and strength > 60:
                buy_signals += 2 if tf in ['15m', '30m', '1h'] else 1
            elif trend == 'هابط' and strength > 60:
                sell_signals += 2 if tf in ['15m', '30m', '1h'] else 1
        
        avg_strength = total_strength / len(multi_tf_analysis) if multi_tf_analysis else 0
        
        # تحديد نوع الإشارة والثقة
        if buy_signals > sell_signals and buy_signals >= 3:
            signal_type = 'شراء'
            confidence = min(85 + (buy_signals - sell_signals) * 5, 95)
        elif sell_signals > buy_signals and sell_signals >= 3:
            signal_type = 'بيع'
            confidence = min(85 + (sell_signals - buy_signals) * 5, 95)
        else:
            signal_type = 'محايد'
            confidence = avg_strength
        
        return {
            'signal_type': signal_type,
            'confidence': round(confidence, 1),
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'avg_strength': round(avg_strength, 1)
        }
    
    def _calculate_advanced_levels(self, symbol: str, current_price: float, signal_type: str, multi_tf_analysis: Dict) -> Tuple[List[float], List[float], float]:
        """حساب منطقتي الدخول والأهداف الثلاثة ووقف الخسارة"""
        pip_value = self.calculate_pip_value(symbol, current_price)
        
        # حساب المسافات بناءً على التقلبات من التحليل
        base_distance = self._calculate_base_distance(symbol, multi_tf_analysis)
        
        if signal_type == 'شراء':
            # منطقتي الدخول للشراء
            entry_zone_1 = current_price - (base_distance * 0.3)  # منطقة أقرب
            entry_zone_2 = current_price - (base_distance * 0.8)  # منطقة أبعد
            
            # وقف الخسارة
            stop_loss = entry_zone_2 - (base_distance * 1.2)
            
            # الأهداف الثلاثة
            target_1 = entry_zone_1 + (base_distance * 1.5)  # نسبة مخاطرة 1:1.5
            target_2 = entry_zone_1 + (base_distance * 2.5)  # نسبة مخاطرة 1:2.5
            target_3 = entry_zone_1 + (base_distance * 4.0)  # نسبة مخاطرة 1:4.0
            
        else:  # بيع
            # منطقتي الدخول للبيع
            entry_zone_1 = current_price + (base_distance * 0.3)
            entry_zone_2 = current_price + (base_distance * 0.8)
            
            # وقف الخسارة
            stop_loss = entry_zone_2 + (base_distance * 1.2)
            
            # الأهداف الثلاثة
            target_1 = entry_zone_1 - (base_distance * 1.5)
            target_2 = entry_zone_1 - (base_distance * 2.5)
            target_3 = entry_zone_1 - (base_distance * 4.0)
        
        return [entry_zone_1, entry_zone_2], [target_1, target_2, target_3], stop_loss
    
    def _calculate_base_distance(self, symbol: str, multi_tf_analysis: Dict) -> float:
        """حساب المسافة الأساسية بناءً على التقلبات"""
        pip_value = self.calculate_pip_value(symbol, 1.0)
        
        # قيم افتراضية بناءً على نوع الرمز
        if 'JPY' in symbol.upper():
            base_pips = 25
        elif any(curr in symbol.upper() for curr in ['EUR', 'GBP', 'USD']):
            base_pips = 15
        elif 'GC=F' in symbol.upper() or 'GOLD' in symbol.upper():
            base_pips = 20  # 20 دولار للذهب
        elif 'BTC' in symbol.upper():
            base_pips = 500  # 500 دولار للبيتكوين
        elif 'ETH' in symbol.upper():
            base_pips = 50   # 50 دولار للإيثيريوم
        else:
            base_pips = 20
        
        # تعديل بناءً على قوة التحليل
        if multi_tf_analysis:
            avg_strength = sum(tf.get('strength', 50) for tf in multi_tf_analysis.values()) / len(multi_tf_analysis)
            multiplier = 0.8 + (avg_strength / 100) * 0.4  # من 0.8 إلى 1.2
            base_pips *= multiplier
        
        return base_pips * pip_value
    
    def _calculate_risk_reward_ratios(self, entry_price: float, targets: List[float], stop_loss: float) -> List[float]:
        """حساب نسب المخاطرة للمكافأة للأهداف الثلاثة"""
        risk = abs(entry_price - stop_loss)
        
        if risk == 0:
            return [0, 0, 0]
        
        ratios = []
        for target in targets:
            reward = abs(target - entry_price)
            ratio = reward / risk
            ratios.append(round(ratio, 2))
        
        return ratios
    
    def _get_recommended_timeframe(self, multi_tf_analysis: Dict) -> str:
        """تحديد الإطار الزمني الموصى به للصفقة"""
        # العثور على الإطار الزمني الأقوى
        best_tf = '15m'  # افتراضي
        best_strength = 0
        
        for tf, analysis in multi_tf_analysis.items():
            strength = analysis.get('strength', 0)
            if strength > best_strength:
                best_strength = strength
                best_tf = tf
        
        return best_tf
    
    async def format_advanced_signal_message(self, signal: Dict) -> str:
        """تنسيق رسالة الإشارة المتقدمة"""
        symbol = signal['symbol']
        signal_type = signal['type']
        confidence = signal['confidence']
        
        # رموز تعبيرية حسب نوع الإشارة
        arrow = "🔴" if signal_type == "بيع" else "🟢"
        direction = "⬇️" if signal_type == "بيع" else "⬆️"
        
        message = f"""
🚀 **إشارة تداول متقدمة عالية الدقة**

{arrow} **{symbol}** - **{signal_type}** {direction}
🎯 **مستوى الثقة:** {confidence}%
⏰ **الإطار الزمني الموصى به:** {signal['recommended_timeframe']}

💰 **منطقتي الدخول:**
🎯 المنطقة الأولى: {signal['entry_zone_1']:.5f}
🎯 المنطقة الثانية: {signal['entry_zone_2']:.5f}

🛡️ **وقف الخسارة:** {signal['stop_loss']:.5f}

🎯 **الأهداف الثلاثة:**
🥇 الهدف الأول: {signal['target_1']:.5f} (نسبة {signal['risk_reward_ratios'][0]}:1)
🥈 الهدف الثاني: {signal['target_2']:.5f} (نسبة {signal['risk_reward_ratios'][1]}:1)  
🥉 الهدف الثالث: {signal['target_3']:.5f} (نسبة {signal['risk_reward_ratios'][2]}:1)

📊 **تحليل النقاط:**
🔻 المخاطرة: {signal['pip_values']['entry_to_sl']:.1f} نقطة
🔹 الهدف الأول: +{signal['pip_values']['entry_to_tp1']:.1f} نقطة
🔸 الهدف الثاني: +{signal['pip_values']['entry_to_tp2']:.1f} نقطة  
🔶 الهدف الثالث: +{signal['pip_values']['entry_to_tp3']:.1f} نقطة

📈 **تحليل الأطر الزمنية:**"""

        # إضافة تحليل كل إطار زمني
        for tf, analysis in signal['timeframe_analysis'].items():
            trend_emoji = "📈" if analysis['trend'] == 'صاعد' else "📉" if analysis['trend'] == 'هابط' else "↔️"
            message += f"\n• {tf}: {trend_emoji} {analysis['trend']} ({analysis['strength']}%)"
        
        message += f"""

🧠 **الإجماع العام:**
✅ إشارات الشراء: {signal['consensus']['buy_signals']}
❌ إشارات البيع: {signal['consensus']['sell_signals']}
💪 القوة المتوسطة: {signal['consensus']['avg_strength']}%

⚠️ **تعليمات الدخول:**
1. ادخل بـ 50% من حجم الصفقة في المنطقة الأولى
2. ادخل بـ 50% المتبقية في المنطقة الثانية (إذا وصل السعر)
3. أغلق 30% عند الهدف الأول وحرك وقف الخسارة للتعادل
4. أغلق 40% عند الهدف الثاني وحرك وقف الخسارة لنصف المسافة
5. احتفظ بـ 30% للهدف الثالث مع التريلنغ ستوب

🕐 **وقت الإشارة:** {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

⚡ **نظام التداول المتقدم** ⚡
"""
        
        return message
    
    async def send_advanced_signal(self, signal: Dict):
        """إرسال الإشارة المتقدمة للمستخدمين"""
        try:
            message = await self.format_advanced_signal_message(signal)
            
            # حفظ الصفقة في النظام
            trade_id = f"{signal['symbol']}_{int(signal['timestamp'].timestamp())}"
            signal['trade_id'] = trade_id
            self.active_trades[trade_id] = signal
            self.save_active_trades()
            
            # إرسال للمستخدمين المصرح لهم
            permissions = load_permissions()
            authorized_users = permissions.get('authorized_users', [])
            
            for user_id in authorized_users:
                try:
                    send_to_telegram(user_id, message, self.bot_token)
                except Exception as e:
                    print(f"خطأ في إرسال الإشارة للمستخدم {user_id}: {e}")
            
            # إرسال للمجموعات المفعلة
            groups = permissions.get('groups', {})
            for group_id, group_info in groups.items():
                if group_info.get('notifications_enabled', False):
                    try:
                        send_to_telegram(group_id, message, self.bot_token)
                    except Exception as e:
                        print(f"خطأ في إرسال الإشارة للمجموعة {group_id}: {e}")
            
            print(f"✅ تم إرسال الإشارة المتقدمة: {signal['symbol']} - {signal['type']}")
            
        except Exception as e:
            print(f"❌ خطأ في إرسال الإشارة المتقدمة: {e}")
    
    def save_active_trades(self):
        """حفظ الصفقات النشطة"""
        try:
            with open("advanced_active_trades.json", "w") as f:
                json.dump(self.active_trades, f, indent=2, default=str)
        except Exception as e:
            print(f"خطأ في حفظ الصفقات النشطة: {e}")
    
    def load_active_trades(self):
        """تحميل الصفقات النشطة"""
        try:
            with open("advanced_active_trades.json", "r") as f:
                self.active_trades = json.load(f)
        except FileNotFoundError:
            self.active_trades = {}
        except Exception as e:
            print(f"خطأ في تحميل الصفقات النشطة: {e}")
            self.active_trades = {}
    
    async def advanced_monitoring_loop(self):
        """حلقة المراقبة المتقدمة"""
        self.load_active_trades()
        
        while True:
            try:
                if not self.trading_config.get('auto_trading_enabled', False):
                    await asyncio.sleep(60)
                    continue
                
                print("🔄 بدء دورة المراقبة المتقدمة...")
                
                # مراقبة الصفقات النشطة
                await self.monitor_active_trades()
                
                # البحث عن إشارات جديدة
                await self.scan_for_new_signals()
                
                # انتظار قبل الدورة التالية
                await asyncio.sleep(self.trading_config.get('monitoring_interval', 300))
                
            except Exception as e:
                print(f"❌ خطأ في حلقة المراقبة المتقدمة: {e}")
                await asyncio.sleep(300)
    
    async def monitor_active_trades(self):
        """مراقبة الصفقات النشطة"""
        for trade_id, trade in list(self.active_trades.items()):
            try:
                if trade['status'] in ['closed', 'cancelled']:
                    continue
                
                # فحص الأهداف ووقف الخسارة
                await self.check_trade_levels(trade_id, trade)
                
            except Exception as e:
                print(f"خطأ في مراقبة الصفقة {trade_id}: {e}")
    
    async def check_trade_levels(self, trade_id: str, trade: Dict):
        """فحص مستويات الصفقة"""
        try:
            symbol = trade['symbol']
            current_price_data = self.data_collector.get_current_price(symbol)
            
            if not current_price_data:
                return
            
            current_price = current_price_data['price']
            signal_type = trade['type']
            
            # فحص الأهداف
            targets_hit = []
            
            if signal_type == 'شراء':
                # فحص الأهداف للشراء
                if current_price >= trade['target_1'] and 'target_1' not in trade.get('targets_hit', []):
                    targets_hit.append('target_1')
                if current_price >= trade['target_2'] and 'target_2' not in trade.get('targets_hit', []):
                    targets_hit.append('target_2')
                if current_price >= trade['target_3'] and 'target_3' not in trade.get('targets_hit', []):
                    targets_hit.append('target_3')
                
                # فحص وقف الخسارة
                if current_price <= trade['stop_loss']:
                    await self.close_trade(trade_id, current_price, 'stop_loss')
                    return
                    
            else:  # بيع
                # فحص الأهداف للبيع
                if current_price <= trade['target_1'] and 'target_1' not in trade.get('targets_hit', []):
                    targets_hit.append('target_1')
                if current_price <= trade['target_2'] and 'target_2' not in trade.get('targets_hit', []):
                    targets_hit.append('target_2')
                if current_price <= trade['target_3'] and 'target_3' not in trade.get('targets_hit', []):
                    targets_hit.append('target_3')
                
                # فحص وقف الخسارة
                if current_price >= trade['stop_loss']:
                    await self.close_trade(trade_id, current_price, 'stop_loss')
                    return
            
            # إرسال تنبيهات للأهداف المحققة
            for target in targets_hit:
                await self.send_target_hit_notification(trade_id, trade, target, current_price)
                
                # تحديث وقف الخسارة
                await self.update_trailing_stop(trade_id, trade, target, current_price)
            
        except Exception as e:
            print(f"خطأ في فحص مستويات الصفقة {trade_id}: {e}")
    
    async def send_target_hit_notification(self, trade_id: str, trade: Dict, target: str, current_price: float):
        """إرسال تنبيه عند تحقق الهدف"""
        target_num = target.split('_')[1]
        target_price = trade[target]
        
        pips_gained = self.calculate_pips_difference(trade['symbol'], trade['entry_zone_1'], current_price)
        
        message = f"""
🎯 **تم تحقيق الهدف!**

📈 **{trade['symbol']}** - **{trade['type']}**
✅ **الهدف {target_num} محقق!**

💰 **السعر الحالي:** {current_price:.5f}
🎯 **سعر الهدف:** {target_price:.5f}
📊 **النقاط المحققة:** +{pips_gained:.1f} نقطة

⚠️ **تعليمات:**
{"أغلق 30% من الصفقة وحرك وقف الخسارة للتعادل" if target_num == "1" else ""}
{"أغلق 40% من الصفقة وحرك وقف الخسارة لنصف المسافة" if target_num == "2" else ""}
{"أغلق باقي الصفقة - تم تحقيق جميع الأهداف!" if target_num == "3" else ""}

🕐 **وقت التحقق:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # إرسال التنبيه للمستخدمين
        permissions = load_permissions()
        authorized_users = permissions.get('authorized_users', [])
        
        for user_id in authorized_users:
            try:
                send_to_telegram(user_id, message, self.bot_token)
            except Exception as e:
                print(f"خطأ في إرسال تنبيه الهدف للمستخدم {user_id}: {e}")
        
        # تحديث الصفقة
        if 'targets_hit' not in trade:
            trade['targets_hit'] = []
        trade['targets_hit'].append(target)
        self.save_active_trades()
    
    async def update_trailing_stop(self, trade_id: str, trade: Dict, target: str, current_price: float):
        """تحديث وقف الخسارة المتحرك"""
        if not self.trading_config.get('trailing_stop', True):
            return
        
        target_num = target.split('_')[1]
        signal_type = trade['type']
        
        if target_num == "1":
            # حرك وقف الخسارة للتعادل
            trade['stop_loss'] = trade['entry_zone_1']
        elif target_num == "2":
            # حرك وقف الخسارة لنصف المسافة
            if signal_type == 'شراء':
                midpoint = (trade['entry_zone_1'] + trade['target_1']) / 2
                trade['stop_loss'] = max(trade['stop_loss'], midpoint)
            else:
                midpoint = (trade['entry_zone_1'] + trade['target_1']) / 2
                trade['stop_loss'] = min(trade['stop_loss'], midpoint)
        
        self.save_active_trades()
    
    async def close_trade(self, trade_id: str, close_price: float, reason: str):
        """إغلاق الصفقة"""
        trade = self.active_trades.get(trade_id)
        if not trade:
            return
        
        trade['status'] = 'closed'
        trade['close_price'] = close_price
        trade['close_time'] = datetime.now()
        trade['close_reason'] = reason
        
        # حساب النتيجة
        pips_result = self.calculate_pips_difference(trade['symbol'], trade['entry_zone_1'], close_price)
        if trade['type'] == 'بيع':
            pips_result = -pips_result if close_price > trade['entry_zone_1'] else pips_result
        else:
            pips_result = pips_result if close_price > trade['entry_zone_1'] else -pips_result
        
        trade['pips_result'] = pips_result
        
        # إرسال تنبيه الإغلاق
        reason_text = {
            'stop_loss': '🛑 وقف الخسارة',
            'take_profit': '🎯 الهدف',
            'manual': '✋ إغلاق يدوي'
        }.get(reason, reason)
        
        result_emoji = "✅" if pips_result > 0 else "❌"
        
        message = f"""
{result_emoji} **تم إغلاق الصفقة**

📈 **{trade['symbol']}** - **{trade['type']}**
🔚 **سبب الإغلاق:** {reason_text}

💰 **سعر الدخول:** {trade['entry_zone_1']:.5f}
💰 **سعر الإغلاق:** {close_price:.5f}
📊 **النتيجة:** {pips_result:+.1f} نقطة

🕐 **وقت الإغلاق:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # إرسال للمستخدمين
        permissions = load_permissions()
        authorized_users = permissions.get('authorized_users', [])
        
        for user_id in authorized_users:
            try:
                send_to_telegram(user_id, message, self.bot_token)
            except Exception as e:
                print(f"خطأ في إرسال تنبيه الإغلاق للمستخدم {user_id}: {e}")
        
        self.save_active_trades()
    
    async def scan_for_new_signals(self):
        """البحث عن إشارات جديدة"""
        if not self.trading_config.get('auto_trading_enabled', False):
            return
        
        # فحص الحد الأقصى للصفقات اليومية
        today_trades = sum(1 for trade in self.active_trades.values() 
                          if trade.get('timestamp', '').startswith(datetime.now().strftime('%Y-%m-%d')) 
                          and trade['status'] != 'cancelled')
        
        if today_trades >= self.trading_config.get('max_daily_trades', 3):
            print(f"⚠️ تم الوصول للحد الأقصى من الصفقات اليومية: {today_trades}")
            return
        
        # فحص جميع الرموز المدعومة
        all_symbols = []
        for category in self.supported_symbols.values():
            all_symbols.extend(category)
        
        for symbol in all_symbols[:10]:  # فحص أول 10 رموز في كل دورة
            try:
                signal = self.generate_advanced_signal(symbol)
                if signal:
                    await self.send_advanced_signal(signal)
                    await asyncio.sleep(5)  # فترة انتظار بين الإشارات
                    
            except Exception as e:
                print(f"خطأ في فحص الرمز {symbol}: {e}")

# إنشاء مثيل النظام المتقدم
advanced_trading = AdvancedTradingSystem()