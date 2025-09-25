import numpy as np
import pandas as pd
from typing import Dict, List, Any

class TechnicalAnalysisSimple:
    """محرك التحليل الفني المبسط - يغطي المحاور السبعة بدون مكتبات معقدة"""
    
    def __init__(self, data):
        self.data = data
        self.high = data['High'].values
        self.low = data['Low'].values
        self.close = data['Close'].values
        self.open = data['Open'].values
        self.volume = data['Volume'].values if 'Volume' in data.columns else None
        
    def simple_moving_average(self, values, period):
        """حساب المتوسط المتحرك البسيط"""
        return pd.Series(values).rolling(window=period).mean().values
    
    def rsi(self, period=14):
        """حساب مؤشر القوة النسبية RSI"""
        delta = pd.Series(self.close).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.values
    
    def macd(self, fast=12, slow=26, signal=9):
        """حساب MACD"""
        ema_fast = pd.Series(self.close).ewm(span=fast).mean()
        ema_slow = pd.Series(self.close).ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line.values, signal_line.values, histogram.values
    
    def bollinger_bands(self, period=20, std_dev=2):
        """حساب البولنجر باندز"""
        sma = pd.Series(self.close).rolling(window=period).mean()
        std = pd.Series(self.close).rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band.values, sma.values, lower_band.values
    
    def calculate_obv(self):
        """حساب On Balance Volume"""
        obv = [0]
        for i in range(1, len(self.close)):
            if self.close[i] > self.close[i-1]:
                obv.append(obv[-1] + self.volume[i])
            elif self.close[i] < self.close[i-1]:
                obv.append(obv[-1] - self.volume[i])
            else:
                obv.append(obv[-1])
        return np.array(obv)
    
    def comprehensive_analysis(self):
        """التحليل الشامل للمحاور السبعة"""
        analysis = {}
        
        # المحور الأول: الاتجاه والسلوك السعري
        analysis['trend_analysis'] = self.trend_analysis()
        
        # المحور الثاني: التحليل الرقمي والزمني
        analysis['fibonacci_analysis'] = self.fibonacci_analysis()
        
        # المحور الثالث: تحليل الحجم
        analysis['volume_analysis'] = self.volume_analysis()
        
        # المحور الرابع: النماذج الفنية
        analysis['patterns_analysis'] = self.patterns_analysis()
        
        # المحور الخامس: المؤشرات الديناميكية
        analysis['indicators_analysis'] = self.indicators_analysis()
        
        # المحور السادس: تدفق المال
        analysis['money_flow_analysis'] = self.money_flow_analysis()
        
        # المحور السابع: الأدوات الاحترافية
        analysis['professional_tools'] = self.professional_tools_analysis()
        
        # حساب التوصية النهائية
        final_recommendation = self.calculate_final_recommendation(analysis)
        
        return {
            'analysis': analysis,
            'recommendation': final_recommendation
        }
    
    def trend_analysis(self):
        """المحور الأول: تحليل الاتجاه"""
        signals = []
        
        # المتوسطات المتحركة
        ma_10 = self.simple_moving_average(self.close, 10)
        ma_20 = self.simple_moving_average(self.close, 20)
        ma_50 = self.simple_moving_average(self.close, 50)
        
        current_price = self.close[-1]
        
        # إشارة الاتجاه
        if current_price > ma_10[-1] > ma_20[-1] > ma_50[-1]:
            signals.append({"signal": "شراء", "strength": 80, "reason": "اتجاه صاعد قوي"})
        elif current_price < ma_10[-1] < ma_20[-1] < ma_50[-1]:
            signals.append({"signal": "بيع", "strength": 80, "reason": "اتجاه هابط قوي"})
        else:
            signals.append({"signal": "محايد", "strength": 50, "reason": "اتجاه غير واضح"})
        
        # الدعوم والمقاومات
        resistance_level = max(self.high[-20:])
        support_level = min(self.low[-20:])
        
        distance_to_resistance = (resistance_level - current_price) / current_price * 100
        distance_to_support = (current_price - support_level) / current_price * 100
        
        if distance_to_resistance < 1:
            signals.append({"signal": "بيع", "strength": 70, "reason": f"اقتراب من مقاومة {resistance_level:.4f}"})
        elif distance_to_support < 1:
            signals.append({"signal": "شراء", "strength": 70, "reason": f"اقتراب من دعم {support_level:.4f}"})
        
        return signals
    
    def fibonacci_analysis(self):
        """المحور الثاني: تحليل فيبوناتشي"""
        signals = []
        
        # العثور على أعلى وأقل نقطة
        high_point = max(self.high[-50:])
        low_point = min(self.low[-50:])
        diff = high_point - low_point
        
        # مستويات فيبوناتشي
        fib_levels = {
            '23.6%': high_point - 0.236 * diff,
            '38.2%': high_point - 0.382 * diff,
            '50%': high_point - 0.5 * diff,
            '61.8%': high_point - 0.618 * diff
        }
        
        current_price = self.close[-1]
        
        for level_name, level_price in fib_levels.items():
            distance = abs(current_price - level_price) / current_price * 100
            if distance < 0.5:
                if current_price > level_price:
                    signals.append({"signal": "شراء", "strength": 65, "reason": f"دعم فيبوناتشي {level_name}"})
                else:
                    signals.append({"signal": "بيع", "strength": 65, "reason": f"مقاومة فيبوناتشي {level_name}"})
        
        return signals
    
    def volume_analysis(self):
        """المحور الثالث: تحليل الحجم"""
        signals = []
        
        if self.volume is None:
            return [{"signal": "محايد", "strength": 50, "reason": "بيانات الحجم غير متوفرة"}]
        
        # متوسط الحجم
        avg_volume = np.mean(self.volume[-20:])
        current_volume = self.volume[-1]
        
        # OBV
        obv = self.calculate_obv()
        obv_trend = obv[-1] - obv[-10]
        
        if current_volume > avg_volume * 1.5 and obv_trend > 0:
            signals.append({"signal": "شراء", "strength": 75, "reason": "حجم مرتفع مع OBV صاعد"})
        elif current_volume > avg_volume * 1.5 and obv_trend < 0:
            signals.append({"signal": "بيع", "strength": 75, "reason": "حجم مرتفع مع OBV هابط"})
        
        return signals
    
    def patterns_analysis(self):
        """المحور الرابع: النماذج الفنية"""
        signals = []
        
        # نموذج الرأس والكتفين المبسط
        recent_highs = []
        for i in range(10, len(self.high) - 10):
            if (self.high[i] > max(self.high[i-10:i]) and 
                self.high[i] > max(self.high[i+1:i+11])):
                recent_highs.append((i, self.high[i]))
        
        if len(recent_highs) >= 3:
            # تحليل مبسط للرأس والكتفين
            left_shoulder, head, right_shoulder = recent_highs[-3:]
            if head[1] > left_shoulder[1] and head[1] > right_shoulder[1]:
                signals.append({"signal": "بيع", "strength": 70, "reason": "نموذج رأس وكتفين محتمل"})
        
        # نموذج المثلث
        recent_highs_prices = [self.high[i] for i in range(-20, 0)]
        recent_lows_prices = [self.low[i] for i in range(-20, 0)]
        
        high_trend = np.polyfit(range(len(recent_highs_prices)), recent_highs_prices, 1)[0]
        low_trend = np.polyfit(range(len(recent_lows_prices)), recent_lows_prices, 1)[0]
        
        if abs(high_trend) < 0.001 and abs(low_trend) < 0.001:
            signals.append({"signal": "محايد", "strength": 60, "reason": "نموذج مثلث - انتظار الكسر"})
        
        return signals
    
    def indicators_analysis(self):
        """المحور الخامس: المؤشرات الديناميكية"""
        signals = []
        
        # RSI
        rsi = self.rsi()
        current_rsi = rsi[-1]
        
        if current_rsi > 70:
            signals.append({"signal": "بيع", "strength": 65, "reason": f"RSI مرتفع {current_rsi:.1f}"})
        elif current_rsi < 30:
            signals.append({"signal": "شراء", "strength": 65, "reason": f"RSI منخفض {current_rsi:.1f}"})
        
        # MACD
        macd_line, signal_line, histogram = self.macd()
        
        if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
            signals.append({"signal": "شراء", "strength": 70, "reason": "إشارة MACD صاعدة"})
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
            signals.append({"signal": "بيع", "strength": 70, "reason": "إشارة MACD هابطة"})
        
        # البولنجر باندز
        upper_band, middle_band, lower_band = self.bollinger_bands()
        current_price = self.close[-1]
        
        if current_price > upper_band[-1]:
            signals.append({"signal": "بيع", "strength": 60, "reason": "السعر فوق البولنجر العلوي"})
        elif current_price < lower_band[-1]:
            signals.append({"signal": "شراء", "strength": 60, "reason": "السعر تحت البولنجر السفلي"})
        
        return signals
    
    def money_flow_analysis(self):
        """المحور السادس: تدفق المال"""
        signals = []
        
        if self.volume is None:
            return [{"signal": "محايد", "strength": 50, "reason": "بيانات الحجم غير متوفرة"}]
        
        # Money Flow Index مبسط
        typical_price = (self.high + self.low + self.close) / 3
        money_flow = typical_price * self.volume
        
        positive_flow = []
        negative_flow = []
        
        for i in range(1, len(typical_price)):
            if typical_price[i] > typical_price[i-1]:
                positive_flow.append(money_flow[i])
                negative_flow.append(0)
            else:
                positive_flow.append(0)
                negative_flow.append(money_flow[i])
        
        # تجنب القسمة على صفر
        negative_sum = sum(negative_flow[-14:])
        positive_sum = sum(positive_flow[-14:])
        
        if negative_sum == 0 or positive_sum == 0:
            mfi = 50  # قيمة محايدة عند عدم وجود بيانات كافية
        else:
            mfi = 100 - (100 / (1 + (positive_sum / negative_sum)))
        
        if mfi > 80:
            signals.append({"signal": "بيع", "strength": 65, "reason": f"MFI مرتفع {mfi:.1f}"})
        elif mfi < 20:
            signals.append({"signal": "شراء", "strength": 65, "reason": f"MFI منخفض {mfi:.1f}"})
        
        return signals
    
    def professional_tools_analysis(self):
        """المحور السابع: الأدوات الاحترافية"""
        signals = []
        
        # Pivot Points
        yesterday_high = self.high[-2] if len(self.high) > 1 else self.high[-1]
        yesterday_low = self.low[-2] if len(self.low) > 1 else self.low[-1]
        yesterday_close = self.close[-2] if len(self.close) > 1 else self.close[-1]
        
        pivot = (yesterday_high + yesterday_low + yesterday_close) / 3
        r1 = 2 * pivot - yesterday_low
        s1 = 2 * pivot - yesterday_high
        
        current_price = self.close[-1]
        
        if current_price > r1:
            signals.append({"signal": "بيع", "strength": 60, "reason": f"فوق مقاومة Pivot R1 {r1:.4f}"})
        elif current_price < s1:
            signals.append({"signal": "شراء", "strength": 60, "reason": f"تحت دعم Pivot S1 {s1:.4f}"})
        
        # ATR للتقلبات
        tr_values = []
        for i in range(1, len(self.close)):
            tr = max(
                self.high[i] - self.low[i],
                abs(self.high[i] - self.close[i-1]),
                abs(self.low[i] - self.close[i-1])
            )
            tr_values.append(tr)
        
        atr = np.mean(tr_values[-14:]) if len(tr_values) >= 14 else np.mean(tr_values)
        volatility_ratio = atr / current_price * 100
        
        if volatility_ratio > 3:
            signals.append({"signal": "محايد", "strength": 40, "reason": f"تقلبات عالية {volatility_ratio:.1f}%"})
        
        return signals
    
    def calculate_final_recommendation(self, analysis):
        """حساب التوصية النهائية"""
        buy_signals = 0
        sell_signals = 0
        neutral_signals = 0
        total_strength = 0
        supporting_schools = 0
        
        all_signals = []
        
        # جمع كل الإشارات
        for category, signals in analysis.items():
            for signal in signals:
                all_signals.append(signal)
                total_strength += signal['strength']
                supporting_schools += 1
                
                if signal['signal'] == 'شراء':
                    buy_signals += signal['strength']
                elif signal['signal'] == 'بيع':
                    sell_signals += signal['strength']
                else:
                    neutral_signals += signal['strength']
        
        # حساب التوصية
        if buy_signals > sell_signals and buy_signals > neutral_signals:
            recommendation_type = "شراء"
            confidence = (buy_signals / (buy_signals + sell_signals + neutral_signals)) * 100
        elif sell_signals > buy_signals and sell_signals > neutral_signals:
            recommendation_type = "بيع"
            confidence = (sell_signals / (buy_signals + sell_signals + neutral_signals)) * 100
        else:
            recommendation_type = "محايد"
            confidence = 50
        
        # حساب نقاط الدخول والأهداف
        current_price = self.close[-1]
        atr = np.std(self.close[-20:]) * 2  # استخدام الانحراف المعياري كبديل لـ ATR
        
        if recommendation_type == "شراء":
            entry_point = current_price
            tp1 = current_price + atr * 0.5
            tp2 = current_price + atr * 1.0
            tp3 = current_price + atr * 1.5
            stop_loss = current_price - atr * 0.5
        elif recommendation_type == "بيع":
            entry_point = current_price
            tp1 = current_price - atr * 0.5
            tp2 = current_price - atr * 1.0
            tp3 = current_price - atr * 1.5
            stop_loss = current_price + atr * 0.5
        else:
            entry_point = current_price
            tp1 = tp2 = tp3 = stop_loss = current_price
        
        return {
            'type': recommendation_type,
            'entry_point': entry_point,
            'targets': {
                'tp1': tp1,
                'tp2': tp2,
                'tp3': tp3
            },
            'stop_loss': stop_loss,
            'confidence': confidence,
            'supporting_schools': supporting_schools,
            'total_signals': len(all_signals),
            'expected_time': '4-24 ساعة',
            'risk_reward': abs(tp1 - entry_point) / abs(stop_loss - entry_point) if abs(stop_loss - entry_point) > 0 else 1
        }