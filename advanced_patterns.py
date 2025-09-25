"""
تحليل النماذج الفنية المتقدمة والشموع اليابانية
"""

import pandas as pd
import numpy as np

try:
    from scipy import stats
    from scipy.signal import find_peaks
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    
    # تطبيق بديل بسيط لـ find_peaks
    def find_peaks(data, distance=1):
        peaks = []
        for i in range(distance, len(data) - distance):
            if all(data[i] >= data[i-j] for j in range(1, distance+1)) and \
               all(data[i] >= data[i+j] for j in range(1, distance+1)):
                peaks.append(i)
        return (peaks,)

class AdvancedPatterns:
    def __init__(self, data):
        self.data = data
        self.high = data['High'].values
        self.low = data['Low'].values
        self.close = data['Close'].values
        self.open = data['Open'].values
        self.volume = data['Volume'].values if 'Volume' in data.columns else np.ones(len(data))
        
    def detect_support_resistance(self, window=20, min_touches=2):
        """كشف مستويات الدعم والمقاومة"""
        levels = []
        
        # العثور على القمم والقيعان
        highs_idx = find_peaks(self.high, distance=window//2)[0]
        lows_idx = find_peaks(-self.low, distance=window//2)[0]
        
        # تحليل مستويات المقاومة (القمم)
        resistance_levels = []
        for i in highs_idx:
            level = self.high[i]
            # عد كم مرة لمس هذا المستوى
            touches = 0
            for j in range(len(self.high)):
                if abs(self.high[j] - level) < level * 0.001:  # 0.1% tolerance
                    touches += 1
            
            if touches >= min_touches:
                resistance_levels.append({
                    'level': level,
                    'type': 'مقاومة',
                    'strength': touches,
                    'last_touch': i
                })
        
        # تحليل مستويات الدعم (القيعان)
        support_levels = []
        for i in lows_idx:
            level = self.low[i]
            touches = 0
            for j in range(len(self.low)):
                if abs(self.low[j] - level) < level * 0.001:
                    touches += 1
            
            if touches >= min_touches:
                support_levels.append({
                    'level': level,
                    'type': 'دعم',
                    'strength': touches,
                    'last_touch': i
                })
        
        # ترتيب المستويات حسب القوة
        all_levels = resistance_levels + support_levels
        all_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        return all_levels[:5]  # أفضل 5 مستويات
    
    def detect_head_and_shoulders(self, window=10):
        """كشف نموذج الرأس والكتفين"""
        if len(self.high) < window * 3:
            return None
        
        peaks = find_peaks(self.high, distance=window)[0]
        if len(peaks) < 3:
            return None
        
        patterns = []
        for i in range(len(peaks) - 2):
            left_shoulder = peaks[i]
            head = peaks[i + 1]
            right_shoulder = peaks[i + 2]
            
            left_shoulder_high = self.high[left_shoulder]
            head_high = self.high[head]
            right_shoulder_high = self.high[right_shoulder]
            
            # شروط نموذج الرأس والكتفين
            if (head_high > left_shoulder_high and 
                head_high > right_shoulder_high and
                abs(left_shoulder_high - right_shoulder_high) < head_high * 0.02):  # الكتفان متقاربان
                
                # حساب خط العنق
                left_valley = np.argmin(self.low[left_shoulder:head]) + left_shoulder
                right_valley = np.argmin(self.low[head:right_shoulder]) + head
                neckline = (self.low[left_valley] + self.low[right_valley]) / 2
                
                patterns.append({
                    'type': 'رأس وكتفين',
                    'direction': 'هبوطي',
                    'strength': 75,
                    'left_shoulder': left_shoulder_high,
                    'head': head_high,
                    'right_shoulder': right_shoulder_high,
                    'neckline': neckline,
                    'target': neckline - (head_high - neckline)
                })
        
        return patterns
    
    def detect_triangles(self, window=20):
        """كشف النماذج المثلثية"""
        if len(self.high) < window * 2:
            return None
        
        patterns = []
        
        # المثلث الصاعد
        recent_highs = self.high[-window:]
        recent_lows = self.low[-window:]
        
        # خط المقاومة الأفقي (قمم متقاربة)
        if SCIPY_AVAILABLE:
            high_slope, _, high_r_value, _, _ = stats.linregress(range(len(recent_highs)), recent_highs)
            low_slope, _, low_r_value, _, _ = stats.linregress(range(len(recent_lows)), recent_lows)
        else:
            # تطبيق بديل بسيط للانحدار الخطي
            high_slope = (recent_highs[-1] - recent_highs[0]) / len(recent_highs)
            low_slope = (recent_lows[-1] - recent_lows[0]) / len(recent_lows)
            high_r_value = 0.8 if abs(high_slope) < 0.001 else 0.5
            low_r_value = 0.8 if low_slope > 0.001 else 0.5
        
        if abs(high_slope) < 0.001 and low_slope > 0.001 and abs(low_r_value) > 0.7:
            patterns.append({
                'type': 'مثلث صاعد',
                'direction': 'صاعد',
                'strength': int(abs(low_r_value) * 100),
                'resistance': np.mean(recent_highs[-5:]),
                'support_slope': low_slope
            })
        
        # المثلث الهابط
        elif abs(low_slope) < 0.001 and high_slope < -0.001 and abs(high_r_value) > 0.7:
            patterns.append({
                'type': 'مثلث هابط',
                'direction': 'هابط',
                'strength': int(abs(high_r_value) * 100),
                'support': np.mean(recent_lows[-5:]),
                'resistance_slope': high_slope
            })
        
        # المثلث المتماثل
        elif (low_slope > 0.001 and high_slope < -0.001 and 
              abs(low_r_value) > 0.6 and abs(high_r_value) > 0.6):
            patterns.append({
                'type': 'مثلث متماثل',
                'direction': 'محايد',
                'strength': int((abs(low_r_value) + abs(high_r_value)) * 50),
                'convergence_point': len(self.data) + 10  # تقدير نقطة التقارب
            })
        
        return patterns
    
    def detect_double_top_bottom(self, window=15, tolerance=0.02):
        """كشف القمة المزدوجة والقاع المزدوج"""
        patterns = []
        
        peaks = find_peaks(self.high, distance=window)[0]
        valleys = find_peaks(-self.low, distance=window)[0]
        
        # القمة المزدوجة
        if len(peaks) >= 2:
            for i in range(len(peaks) - 1):
                peak1 = peaks[i]
                peak2 = peaks[i + 1]
                
                peak1_high = self.high[peak1]
                peak2_high = self.high[peak2]
                
                if abs(peak1_high - peak2_high) < peak1_high * tolerance:
                    # العثور على القاع بين القمتين
                    valley_between = np.argmin(self.low[peak1:peak2]) + peak1
                    valley_low = self.low[valley_between]
                    
                    patterns.append({
                        'type': 'قمة مزدوجة',
                        'direction': 'هبوطي',
                        'strength': 70,
                        'peak1': peak1_high,
                        'peak2': peak2_high,
                        'valley': valley_low,
                        'target': valley_low - (peak1_high - valley_low) * 0.618
                    })
        
        # القاع المزدوج
        if len(valleys) >= 2:
            for i in range(len(valleys) - 1):
                valley1 = valleys[i]
                valley2 = valleys[i + 1]
                
                valley1_low = self.low[valley1]
                valley2_low = self.low[valley2]
                
                if abs(valley1_low - valley2_low) < valley1_low * tolerance:
                    # العثور على القمة بين القاعين
                    peak_between = np.argmax(self.high[valley1:valley2]) + valley1
                    peak_high = self.high[peak_between]
                    
                    patterns.append({
                        'type': 'قاع مزدوج',
                        'direction': 'صاعد',
                        'strength': 70,
                        'valley1': valley1_low,
                        'valley2': valley2_low,
                        'peak': peak_high,
                        'target': peak_high + (peak_high - valley1_low) * 0.618
                    })
        
        return patterns
    
    def detect_flag_pennant(self, window=10):
        """كشف نماذج العلم والراية"""
        if len(self.high) < window * 3:
            return None
        
        patterns = []
        
        # البحث عن حركة قوية (العمود)
        price_changes = np.diff(self.close)
        strong_moves = []
        
        for i in range(window, len(price_changes) - window):
            move_strength = abs(sum(price_changes[i-window:i]))
            avg_move = np.mean(np.abs(price_changes[max(0, i-50):i]))
            
            if move_strength > avg_move * 3:  # حركة قوية
                strong_moves.append({
                    'start': i - window,
                    'end': i,
                    'direction': 'صاعد' if sum(price_changes[i-window:i]) > 0 else 'هابط',
                    'strength': move_strength
                })
        
        # البحث عن توحيد بعد الحركة القوية (العلم)
        for move in strong_moves:
            consolidation_start = move['end']
            consolidation_end = min(consolidation_start + window, len(self.close))
            
            if consolidation_end - consolidation_start < 5:
                continue
            
            consolidation_data = self.close[consolidation_start:consolidation_end]
            volatility = np.std(consolidation_data)
            avg_volatility = np.std(self.close[max(0, consolidation_start-50):consolidation_start])
            
            if volatility < avg_volatility * 0.5:  # توحيد (تقلبات منخفضة)
                patterns.append({
                    'type': 'علم' if move['direction'] == 'صاعد' else 'علم هابط',
                    'direction': move['direction'],
                    'strength': 65,
                    'flagpole_start': move['start'],
                    'flagpole_end': move['end'],
                    'flag_start': consolidation_start,
                    'flag_end': consolidation_end,
                    'target': self.close[consolidation_end-1] + (move['strength'] * (1 if move['direction'] == 'صاعد' else -1))
                })
        
        return patterns
    
    def analyze_all_patterns(self):
        """تحليل شامل لجميع النماذج"""
        results = {
            'support_resistance': self.detect_support_resistance(),
            'head_shoulders': self.detect_head_and_shoulders(),
            'triangles': self.detect_triangles(),
            'double_patterns': self.detect_double_top_bottom(),
            'flags_pennants': self.detect_flag_pennant()
        }
        
        # إنشاء ملخص النماذج المكتشفة
        detected_patterns = []
        
        for pattern_type, patterns in results.items():
            if patterns:
                if isinstance(patterns, list):
                    detected_patterns.extend(patterns)
                else:
                    detected_patterns.append(patterns)
        
        # ترتيب النماذج حسب القوة
        detected_patterns.sort(key=lambda x: x.get('strength', 0), reverse=True)
        
        return {
            'patterns': detected_patterns[:5],  # أقوى 5 نماذج
            'total_patterns': len(detected_patterns),
            'bullish_patterns': len([p for p in detected_patterns if p.get('direction') == 'صاعد']),
            'bearish_patterns': len([p for p in detected_patterns if p.get('direction') == 'هابط']),
            'neutral_patterns': len([p for p in detected_patterns if p.get('direction') == 'محايد'])
        }