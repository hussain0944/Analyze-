"""
تحليل الشموع اليابانية المتقدمة
"""

import pandas as pd
import numpy as np

class CandlestickPatterns:
    def __init__(self, data):
        self.data = data
        self.open = data['Open'].values
        self.high = data['High'].values
        self.low = data['Low'].values
        self.close = data['Close'].values
        
        # حساب خصائص الشموع
        self.body_size = np.abs(self.close - self.open)
        self.upper_shadow = self.high - np.maximum(self.open, self.close)
        self.lower_shadow = np.minimum(self.open, self.close) - self.low
        self.total_range = self.high - self.low
        
        # تحديد لون الشمعة
        self.is_bullish = self.close > self.open
        self.is_bearish = self.close < self.open
        self.is_doji = np.abs(self.close - self.open) < (self.total_range * 0.1)
    
    def detect_doji(self):
        """كشف شموع الدوجي وأنواعها"""
        patterns = []
        
        for i in range(len(self.data)):
            if self.is_doji[i]:
                doji_type = "دوجي عادي"
                
                # دوجي طويل الأرجل
                if (self.upper_shadow[i] > self.body_size[i] * 2 and 
                    self.lower_shadow[i] > self.body_size[i] * 2):
                    doji_type = "دوجي طويل الأرجل"
                
                # دوجي اليعسوب
                elif (self.lower_shadow[i] > self.body_size[i] * 3 and 
                      self.upper_shadow[i] < self.body_size[i]):
                    doji_type = "دوجي اليعسوب"
                
                # دوجي شاهد القبر
                elif (self.upper_shadow[i] > self.body_size[i] * 3 and 
                      self.lower_shadow[i] < self.body_size[i]):
                    doji_type = "دوجي شاهد القبر"
                
                patterns.append({
                    'index': i,
                    'type': doji_type,
                    'signal': 'انعكاس محتمل',
                    'strength': 60 if doji_type == "دوجي عادي" else 75
                })
        
        return patterns
    
    def detect_hammer_hanging_man(self):
        """كشف شموع المطرقة والرجل المشنوق"""
        patterns = []
        
        for i in range(1, len(self.data)):
            # شروط المطرقة/الرجل المشنوق
            small_body = self.body_size[i] < self.total_range[i] * 0.3
            long_lower_shadow = self.lower_shadow[i] > self.body_size[i] * 2
            short_upper_shadow = self.upper_shadow[i] < self.body_size[i] * 0.5
            
            if small_body and long_lower_shadow and short_upper_shadow:
                # تحديد النوع بناءً على الاتجاه السابق
                prev_trend = self.close[i-1] - self.close[max(0, i-5)]
                
                if prev_trend < 0:  # اتجاه هابط سابق
                    patterns.append({
                        'index': i,
                        'type': 'مطرقة',
                        'signal': 'انعكاس صاعد محتمل',
                        'strength': 70
                    })
                elif prev_trend > 0:  # اتجاه صاعد سابق
                    patterns.append({
                        'index': i,
                        'type': 'رجل مشنوق',
                        'signal': 'انعكاس هابط محتمل',
                        'strength': 70
                    })
        
        return patterns
    
    def detect_engulfing_patterns(self):
        """كشف نماذج الابتلاع"""
        patterns = []
        
        for i in range(1, len(self.data)):
            current_body = self.body_size[i]
            prev_body = self.body_size[i-1]
            
            # الابتلاع الصاعد
            if (self.is_bearish[i-1] and self.is_bullish[i] and
                self.open[i] < self.close[i-1] and self.close[i] > self.open[i-1]):
                patterns.append({
                    'index': i,
                    'type': 'ابتلاع صاعد',
                    'signal': 'انعكاس صاعد قوي',
                    'strength': 85
                })
            
            # الابتلاع الهابط
            elif (self.is_bullish[i-1] and self.is_bearish[i] and
                  self.open[i] > self.close[i-1] and self.close[i] < self.open[i-1]):
                patterns.append({
                    'index': i,
                    'type': 'ابتلاع هابط',
                    'signal': 'انعكاس هابط قوي',
                    'strength': 85
                })
        
        return patterns
    
    def detect_piercing_dark_cloud(self):
        """كشف نماذج الاختراق والغيمة السوداء"""
        patterns = []
        
        for i in range(1, len(self.data)):
            # نموذج الاختراق
            if (self.is_bearish[i-1] and self.is_bullish[i] and
                self.open[i] < self.low[i-1] and 
                self.close[i] > (self.open[i-1] + self.close[i-1]) / 2):
                patterns.append({
                    'index': i,
                    'type': 'اختراق',
                    'signal': 'انعكاس صاعد',
                    'strength': 75
                })
            
            # الغيمة السوداء
            elif (self.is_bullish[i-1] and self.is_bearish[i] and
                  self.open[i] > self.high[i-1] and 
                  self.close[i] < (self.open[i-1] + self.close[i-1]) / 2):
                patterns.append({
                    'index': i,
                    'type': 'غيمة سوداء',
                    'signal': 'انعكاس هابط',
                    'strength': 75
                })
        
        return patterns
    
    def detect_morning_evening_star(self):
        """كشف نجمة الصباح ونجمة المساء"""
        patterns = []
        
        for i in range(2, len(self.data)):
            # نجمة الصباح
            if (self.is_bearish[i-2] and self.body_size[i-2] > np.mean(self.body_size) and
                self.body_size[i-1] < np.mean(self.body_size) * 0.3 and  # شمعة صغيرة/دوجي
                self.is_bullish[i] and self.body_size[i] > np.mean(self.body_size) and
                self.close[i] > (self.open[i-2] + self.close[i-2]) / 2):
                patterns.append({
                    'index': i,
                    'type': 'نجمة الصباح',
                    'signal': 'انعكاس صاعد قوي',
                    'strength': 90
                })
            
            # نجمة المساء
            elif (self.is_bullish[i-2] and self.body_size[i-2] > np.mean(self.body_size) and
                  self.body_size[i-1] < np.mean(self.body_size) * 0.3 and
                  self.is_bearish[i] and self.body_size[i] > np.mean(self.body_size) and
                  self.close[i] < (self.open[i-2] + self.close[i-2]) / 2):
                patterns.append({
                    'index': i,
                    'type': 'نجمة المساء',
                    'signal': 'انعكاس هابط قوي',
                    'strength': 90
                })
        
        return patterns
    
    def detect_shooting_star_inverted_hammer(self):
        """كشف النجم الساقط والمطرقة المقلوبة"""
        patterns = []
        
        for i in range(1, len(self.data)):
            # شروط النجم الساقط/المطرقة المقلوبة
            small_body = self.body_size[i] < self.total_range[i] * 0.3
            long_upper_shadow = self.upper_shadow[i] > self.body_size[i] * 2
            short_lower_shadow = self.lower_shadow[i] < self.body_size[i] * 0.5
            
            if small_body and long_upper_shadow and short_lower_shadow:
                prev_trend = self.close[i-1] - self.close[max(0, i-5)]
                
                if prev_trend > 0:  # اتجاه صاعد سابق
                    patterns.append({
                        'index': i,
                        'type': 'نجم ساقط',
                        'signal': 'انعكاس هابط محتمل',
                        'strength': 70
                    })
                elif prev_trend < 0:  # اتجاه هابط سابق
                    patterns.append({
                        'index': i,
                        'type': 'مطرقة مقلوبة',
                        'signal': 'انعكاس صاعد محتمل',
                        'strength': 65
                    })
        
        return patterns
    
    def detect_three_soldiers_crows(self):
        """كشف الجنود الثلاثة والغربان الثلاثة"""
        patterns = []
        
        for i in range(2, len(self.data)):
            # الجنود الثلاثة البيض
            if (self.is_bullish[i-2] and self.is_bullish[i-1] and self.is_bullish[i] and
                self.close[i-1] > self.close[i-2] and self.close[i] > self.close[i-1] and
                self.open[i-1] > self.open[i-2] and self.open[i] > self.open[i-1] and
                all(self.body_size[j] > np.mean(self.body_size) * 0.7 for j in [i-2, i-1, i])):
                patterns.append({
                    'index': i,
                    'type': 'الجنود الثلاثة البيض',
                    'signal': 'استمرار صاعد قوي',
                    'strength': 85
                })
            
            # الغربان الثلاثة السود
            elif (self.is_bearish[i-2] and self.is_bearish[i-1] and self.is_bearish[i] and
                  self.close[i-1] < self.close[i-2] and self.close[i] < self.close[i-1] and
                  self.open[i-1] < self.open[i-2] and self.open[i] < self.open[i-1] and
                  all(self.body_size[j] > np.mean(self.body_size) * 0.7 for j in [i-2, i-1, i])):
                patterns.append({
                    'index': i,
                    'type': 'الغربان الثلاثة السود',
                    'signal': 'استمرار هابط قوي',
                    'strength': 85
                })
        
        return patterns
    
    def analyze_all_candlestick_patterns(self):
        """تحليل شامل لجميع الشموع اليابانية"""
        all_patterns = []
        
        # تجميع جميع النماذج
        pattern_methods = [
            self.detect_doji,
            self.detect_hammer_hanging_man,
            self.detect_engulfing_patterns,
            self.detect_piercing_dark_cloud,
            self.detect_morning_evening_star,
            self.detect_shooting_star_inverted_hammer,
            self.detect_three_soldiers_crows
        ]
        
        for method in pattern_methods:
            patterns = method()
            all_patterns.extend(patterns)
        
        # ترتيب النماذج حسب القوة والحداثة
        all_patterns.sort(key=lambda x: (x['strength'], x['index']), reverse=True)
        
        # تحليل الإشارات
        bullish_signals = len([p for p in all_patterns if 'صاعد' in p['signal']])
        bearish_signals = len([p for p in all_patterns if 'هابط' in p['signal']])
        
        return {
            'patterns': all_patterns[:5],  # أقوى 5 نماذج
            'total_patterns': len(all_patterns),
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals,
            'overall_sentiment': 'صاعد' if bullish_signals > bearish_signals else 'هابط' if bearish_signals > bullish_signals else 'محايد'
        }