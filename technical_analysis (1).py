import numpy as np
import pandas as pd
# import talib  # سنستخدم حسابات مخصصة بدلاً منها

class TechnicalAnalysis:
    """محرك التحليل الفني المتكامل - يغطي المحاور السبعة"""
    
    def __init__(self, data):
        self.data = data
        self.high = data['High'].values
        self.low = data['Low'].values
        self.close = data['Close'].values
        self.open = data['Open'].values
        self.volume = data['Volume'].values if 'Volume' in data.columns else None
        
    # المحور الأول: مدارس الاتجاه والسلوك السعري
    def trend_and_price_action_analysis(self):
        """تحليل الاتجاه والسلوك السعري"""
        signals = {}
        
        # 1. تحليل موجات إليوت (مبسط)
        elliott_signal = self.elliott_wave_analysis()
        signals['elliott_wave'] = elliott_signal
        
        # 2. Smart Money Concepts
        smart_money = self.smart_money_analysis()
        signals['smart_money'] = smart_money
        
        # 3. مناطق العرض والطلب
        supply_demand = self.supply_demand_zones()
        signals['supply_demand'] = supply_demand
        
        # 4. Break of Structure (BOS) / Change of Character (CHoCH)
        structure_break = self.structure_break_analysis()
        signals['structure_break'] = structure_break
        
        return signals
    
    def elliott_wave_analysis(self):
        """تحليل موجات إليوت المبسط"""
        try:
            # حساب الاتجاه العام
            ma_20 = talib.SMA(self.close, timeperiod=20)
            ma_50 = talib.SMA(self.close, timeperiod=50)
            
            current_price = self.close[-1]
            current_ma20 = ma_20[-1]
            current_ma50 = ma_50[-1]
            
            if current_price > current_ma20 > current_ma50:
                return {"signal": "شراء", "strength": 75, "description": "موجة صاعدة محتملة"}
            elif current_price < current_ma20 < current_ma50:
                return {"signal": "بيع", "strength": 75, "description": "موجة هابطة محتملة"}
            else:
                return {"signal": "محايد", "strength": 50, "description": "موجة تصحيحية"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}
    
    def smart_money_analysis(self):
        """تحليل Smart Money"""
        try:
            # تحليل الكسر الكاذب والعودة
            highs = pd.Series(self.high).rolling(window=10).max()
            lows = pd.Series(self.low).rolling(window=10).min()
            
            current_high = self.high[-1]
            current_low = self.low[-1]
            prev_high = highs.iloc[-2] if len(highs) > 1 else current_high
            prev_low = lows.iloc[-2] if len(lows) > 1 else current_low
            
            # إشارة Smart Money
            if current_high > prev_high and self.close[-1] < prev_high:
                return {"signal": "بيع", "strength": 70, "description": "كسر كاذب في القمة"}
            elif current_low < prev_low and self.close[-1] > prev_low:
                return {"signal": "شراء", "strength": 70, "description": "كسر كاذب في القاع"}
            else:
                return {"signal": "محايد", "strength": 50, "description": "لا توجد إشارة واضحة"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}
    
    def supply_demand_zones(self):
        """تحليل مناطق العرض والطلب"""
        try:
            # تحديد مناطق الدعم والمقاومة
            resistance_levels = []
            support_levels = []
            
            for i in range(10, len(self.close) - 10):
                # مستوى مقاومة
                if (self.high[i] > max(self.high[i-10:i]) and 
                    self.high[i] > max(self.high[i+1:i+10])):
                    resistance_levels.append(self.high[i])
                
                # مستوى دعم
                if (self.low[i] < min(self.low[i-10:i]) and 
                    self.low[i] < min(self.low[i+1:i+10])):
                    support_levels.append(self.low[i])
            
            current_price = self.close[-1]
            nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)
            nearest_support = max([s for s in support_levels if s < current_price], default=None)
            
            if nearest_resistance and (nearest_resistance - current_price) / current_price < 0.01:
                return {"signal": "بيع", "strength": 65, "description": f"اقتراب من مقاومة {nearest_resistance:.4f}"}
            elif nearest_support and (current_price - nearest_support) / current_price < 0.01:
                return {"signal": "شراء", "strength": 65, "description": f"اقتراب من دعم {nearest_support:.4f}"}
            else:
                return {"signal": "محايد", "strength": 50, "description": "في منطقة متوسطة"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}
    
    def structure_break_analysis(self):
        """تحليل كسر الهيكل BOS/CHoCH"""
        try:
            # تحديد الاتجاه الحالي
            ma_10 = talib.SMA(self.close, timeperiod=10)
            ma_20 = talib.SMA(self.close, timeperiod=20)
            
            # كسر الهيكل الصاعد
            if ma_10[-1] > ma_20[-1] and ma_10[-2] <= ma_20[-2]:
                return {"signal": "شراء", "strength": 80, "description": "كسر هيكل صاعد"}
            # كسر الهيكل الهابط
            elif ma_10[-1] < ma_20[-1] and ma_10[-2] >= ma_20[-2]:
                return {"signal": "بيع", "strength": 80, "description": "كسر هيكل هابط"}
            else:
                return {"signal": "محايد", "strength": 50, "description": "استمرار الاتجاه"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}
    
    # المحور الثاني: التحليل الرقمي والزمني
    def digital_time_analysis(self):
        """التحليل الرقمي والزمني"""
        signals = {}
        
        # 1. مستويات فيبوناتشي
        fibonacci = self.fibonacci_analysis()
        signals['fibonacci'] = fibonacci
        
        # 2. أدوات جان (مبسط)
        gann = self.gann_analysis()
        signals['gann'] = gann
        
        # 3. الدورات الزمنية
        time_cycles = self.time_cycles_analysis()
        signals['time_cycles'] = time_cycles
        
        return signals
    
    def fibonacci_analysis(self):
        """تحليل مستويات فيبوناتشي"""
        try:
            # العثور على أعلى وأقل نقطة في آخر 50 شمعة
            period = min(50, len(self.close))
            high_point = max(self.high[-period:])
            low_point = min(self.low[-period:])
            
            # حساب مستويات فيبوناتشي
            diff = high_point - low_point
            levels = {
                'level_236': high_point - 0.236 * diff,
                'level_382': high_point - 0.382 * diff,
                'level_500': high_point - 0.500 * diff,
                'level_618': high_point - 0.618 * diff,
                'level_786': high_point - 0.786 * diff
            }
            
            current_price = self.close[-1]
            
            # تحديد أقرب مستوى فيبوناتشي
            closest_level = min(levels.items(), key=lambda x: abs(x[1] - current_price))
            distance_pct = abs(closest_level[1] - current_price) / current_price * 100
            
            if distance_pct < 0.5:  # إذا كان السعر قريب من مستوى فيبوناتشي
                if current_price > closest_level[1]:
                    return {"signal": "شراء", "strength": 70, "description": f"دعم فيبوناتشي {closest_level[0]}"}
                else:
                    return {"signal": "بيع", "strength": 70, "description": f"مقاومة فيبوناتشي {closest_level[0]}"}
            else:
                return {"signal": "محايد", "strength": 50, "description": "بعيد عن مستويات فيبوناتشي"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}
    
    def gann_analysis(self):
        """تحليل أدوات جان المبسط"""
        try:
            # حساب زوايا جان الأساسية
            period = min(20, len(self.close))
            price_range = max(self.high[-period:]) - min(self.low[-period:])
            time_range = period
            
            # زاوية 45 درجة (1x1)
            gann_angle = price_range / time_range
            current_trend = (self.close[-1] - self.close[-period]) / period
            
            if abs(current_trend - gann_angle) < gann_angle * 0.1:
                return {"signal": "شراء", "strength": 60, "description": "اتجاه متوازن مع زاوية جان"}
            elif abs(current_trend + gann_angle) < gann_angle * 0.1:
                return {"signal": "بيع", "strength": 60, "description": "اتجاه هابط متوازن مع زاوية جان"}
            else:
                return {"signal": "محايد", "strength": 50, "description": "خارج زوايا جان الأساسية"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}
    
    def time_cycles_analysis(self):
        """تحليل الدورات الزمنية"""
        try:
            # دورة 7 أيام و 21 يوم و 50 يوم
            cycles = [7, 21, 50]
            signals_count = 0
            
            for cycle in cycles:
                if len(self.close) >= cycle:
                    cycle_high = max(self.high[-cycle:])
                    cycle_low = min(self.low[-cycle:])
                    current_position = (self.close[-1] - cycle_low) / (cycle_high - cycle_low)
                    
                    if current_position > 0.8:  # قريب من القمة
                        signals_count -= 1
                    elif current_position < 0.2:  # قريب من القاع
                        signals_count += 1
            
            if signals_count > 0:
                return {"signal": "شراء", "strength": 55, "description": "الدورات الزمنية تشير للشراء"}
            elif signals_count < 0:
                return {"signal": "بيع", "strength": 55, "description": "الدورات الزمنية تشير للبيع"}
            else:
                return {"signal": "محايد", "strength": 50, "description": "الدورات الزمنية محايدة"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}
    
    # المحور الثالث: تحليل الحجم والتدفقات
    def volume_flow_analysis(self):
        """تحليل الحجم والتدفقات"""
        if self.volume is None:
            return {"volume_profile": {"signal": "محايد", "strength": 50, "description": "بيانات الحجم غير متوفرة"}}
        
        signals = {}
        
        # 1. Volume Profile
        volume_profile = self.volume_profile_analysis()
        signals['volume_profile'] = volume_profile
        
        # 2. On Balance Volume (OBV)
        obv = self.obv_analysis()
        signals['obv'] = obv
        
        # 3. Volume Weighted Average Price (VWAP)
        vwap = self.vwap_analysis()
        signals['vwap'] = vwap
        
        return signals
    
    def volume_profile_analysis(self):
        """تحليل Volume Profile"""
        try:
            # حساب VWAP كمؤشر على الحجم
            vwap = talib.VWAP(self.high, self.low, self.close, self.volume)
            current_price = self.close[-1]
            current_vwap = vwap[-1]
            
            if current_price > current_vwap * 1.01:
                return {"signal": "شراء", "strength": 65, "description": "السعر فوق VWAP بقوة"}
            elif current_price < current_vwap * 0.99:
                return {"signal": "بيع", "strength": 65, "description": "السعر تحت VWAP بقوة"}
            else:
                return {"signal": "محايد", "strength": 50, "description": "السعر قريب من VWAP"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}
    
    def obv_analysis(self):
        """تحليل On Balance Volume"""
        try:
            obv = talib.OBV(self.close, self.volume)
            obv_ma = talib.SMA(obv, timeperiod=10)
            
            if obv[-1] > obv_ma[-1]:
                return {"signal": "شراء", "strength": 60, "description": "OBV في اتجاه صاعد"}
            else:
                return {"signal": "بيع", "strength": 60, "description": "OBV في اتجاه هابط"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}
    
    def vwap_analysis(self):
        """تحليل VWAP"""
        try:
            vwap = talib.VWAP(self.high, self.low, self.close, self.volume)
            price_distance = (self.close[-1] - vwap[-1]) / vwap[-1] * 100
            
            if price_distance > 2:
                return {"signal": "بيع", "strength": 70, "description": f"السعر أعلى من VWAP بـ {price_distance:.1f}%"}
            elif price_distance < -2:
                return {"signal": "شراء", "strength": 70, "description": f"السعر أقل من VWAP بـ {abs(price_distance):.1f}%"}
            else:
                return {"signal": "محايد", "strength": 50, "description": "السعر قريب من VWAP"}
        except:
            return {"signal": "محايد", "strength": 50, "description": "بيانات غير كافية"}