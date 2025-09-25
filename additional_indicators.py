"""
مؤشرات فنية إضافية متقدمة
"""

import pandas as pd
import numpy as np

class AdditionalIndicators:
    def __init__(self, data):
        self.data = data
        self.high = data['High'].values
        self.low = data['Low'].values
        self.close = data['Close'].values
        self.volume = data['Volume'].values if 'Volume' in data.columns else np.ones(len(data))
    
    def stochastic_oscillator(self, k_period=14, d_period=3):
        """مذبذب ستوكاستيك"""
        # حساب %K
        lowest_low = pd.Series(self.low).rolling(window=k_period).min()
        highest_high = pd.Series(self.high).rolling(window=k_period).max()
        
        k_percent = 100 * ((self.close - lowest_low) / (highest_high - lowest_low))
        
        # حساب %D (متوسط متحرك لـ %K)
        d_percent = k_percent.rolling(window=d_period).mean()
        
        # تحليل الإشارات
        signals = []
        current_k = k_percent.iloc[-1] if not pd.isna(k_percent.iloc[-1]) else 50
        current_d = d_percent.iloc[-1] if not pd.isna(d_percent.iloc[-1]) else 50
        
        if current_k < 20 and current_d < 20:
            signals.append({"signal": "شراء", "strength": 70, "reason": f"ستوكاستيك في منطقة التشبع البيعي K={current_k:.1f}, D={current_d:.1f}"})
        elif current_k > 80 and current_d > 80:
            signals.append({"signal": "بيع", "strength": 70, "reason": f"ستوكاستيك في منطقة التشبع الشرائي K={current_k:.1f}, D={current_d:.1f}"})
        
        # تقاطع الخطوط
        if len(k_percent) > 1 and len(d_percent) > 1:
            if k_percent.iloc[-2] < d_percent.iloc[-2] and k_percent.iloc[-1] > d_percent.iloc[-1]:
                signals.append({"signal": "شراء", "strength": 65, "reason": "تقاطع صاعد في ستوكاستيك"})
            elif k_percent.iloc[-2] > d_percent.iloc[-2] and k_percent.iloc[-1] < d_percent.iloc[-1]:
                signals.append({"signal": "بيع", "strength": 65, "reason": "تقاطع هابط في ستوكاستيك"})
        
        return {
            'k_percent': current_k,
            'd_percent': current_d,
            'signals': signals
        }
    
    def williams_percent_r(self, period=14):
        """مؤشر وليامز %R"""
        highest_high = pd.Series(self.high).rolling(window=period).max()
        lowest_low = pd.Series(self.low).rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - self.close) / (highest_high - lowest_low))
        
        current_wr = williams_r.iloc[-1] if not pd.isna(williams_r.iloc[-1]) else -50
        
        signals = []
        if current_wr < -80:
            signals.append({"signal": "شراء", "strength": 65, "reason": f"وليامز %R في منطقة التشبع البيعي {current_wr:.1f}"})
        elif current_wr > -20:
            signals.append({"signal": "بيع", "strength": 65, "reason": f"وليامز %R في منطقة التشبع الشرائي {current_wr:.1f}"})
        
        return {
            'williams_r': current_wr,
            'signals': signals
        }
    
    def commodity_channel_index(self, period=20):
        """مؤشر قناة السلع CCI"""
        # حساب السعر النموذجي
        typical_price = (self.high + self.low + self.close) / 3
        
        # المتوسط المتحرك البسيط للسعر النموذجي
        sma_tp = pd.Series(typical_price).rolling(window=period).mean()
        
        # متوسط الانحراف المطلق
        mad = pd.Series(typical_price).rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - x.mean()))
        )
        
        # حساب CCI
        cci = (typical_price - sma_tp) / (0.015 * mad)
        
        current_cci = cci.iloc[-1] if not pd.isna(cci.iloc[-1]) else 0
        
        signals = []
        if current_cci < -100:
            signals.append({"signal": "شراء", "strength": 70, "reason": f"CCI في منطقة التشبع البيعي {current_cci:.1f}"})
        elif current_cci > 100:
            signals.append({"signal": "بيع", "strength": 70, "reason": f"CCI في منطقة التشبع الشرائي {current_cci:.1f}"})
        
        # تقاطع خط الصفر
        if len(cci) > 1:
            if cci.iloc[-2] < 0 and cci.iloc[-1] > 0:
                signals.append({"signal": "شراء", "strength": 60, "reason": "CCI يتقاطع فوق خط الصفر"})
            elif cci.iloc[-2] > 0 and cci.iloc[-1] < 0:
                signals.append({"signal": "بيع", "strength": 60, "reason": "CCI يتقاطع تحت خط الصفر"})
        
        return {
            'cci': current_cci,
            'signals': signals
        }
    
    def average_directional_index(self, period=14):
        """مؤشر الاتجاه المتوسط ADX"""
        # حساب True Range
        tr1 = self.high - self.low
        tr2 = np.abs(self.high - np.roll(self.close, 1))
        tr3 = np.abs(self.low - np.roll(self.close, 1))
        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # حساب Directional Movement
        dm_plus = np.where((self.high - np.roll(self.high, 1)) > (np.roll(self.low, 1) - self.low), 
                          np.maximum(self.high - np.roll(self.high, 1), 0), 0)
        dm_minus = np.where((np.roll(self.low, 1) - self.low) > (self.high - np.roll(self.high, 1)), 
                           np.maximum(np.roll(self.low, 1) - self.low, 0), 0)
        
        # Smoothed values
        tr_smooth = pd.Series(true_range).rolling(window=period).mean()
        dm_plus_smooth = pd.Series(dm_plus).rolling(window=period).mean()
        dm_minus_smooth = pd.Series(dm_minus).rolling(window=period).mean()
        
        # Directional Indicators
        di_plus = 100 * (dm_plus_smooth / tr_smooth)
        di_minus = 100 * (dm_minus_smooth / tr_smooth)
        
        # ADX calculation
        dx = 100 * np.abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = pd.Series(dx).rolling(window=period).mean()
        
        current_adx = adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0
        current_di_plus = di_plus.iloc[-1] if not pd.isna(di_plus.iloc[-1]) else 0
        current_di_minus = di_minus.iloc[-1] if not pd.isna(di_minus.iloc[-1]) else 0
        
        signals = []
        
        # قوة الاتجاه
        if current_adx > 25:
            if current_di_plus > current_di_minus:
                signals.append({"signal": "شراء", "strength": 75, "reason": f"اتجاه صاعد قوي ADX={current_adx:.1f}"})
            else:
                signals.append({"signal": "بيع", "strength": 75, "reason": f"اتجاه هابط قوي ADX={current_adx:.1f}"})
        elif current_adx < 20:
            signals.append({"signal": "محايد", "strength": 40, "reason": f"اتجاه ضعيف ADX={current_adx:.1f}"})
        
        return {
            'adx': current_adx,
            'di_plus': current_di_plus,
            'di_minus': current_di_minus,
            'signals': signals
        }
    
    def parabolic_sar(self, af=0.02, max_af=0.2):
        """مؤشر البارابوليك SAR"""
        length = len(self.close)
        psar = np.zeros(length)
        trend = np.zeros(length)
        af_values = np.zeros(length)
        ep = np.zeros(length)
        
        # Initialize
        psar[0] = self.low[0]
        trend[0] = 1  # 1 for uptrend, -1 for downtrend
        af_values[0] = af
        ep[0] = self.high[0]
        
        for i in range(1, length):
            if trend[i-1] == 1:  # Uptrend
                psar[i] = psar[i-1] + af_values[i-1] * (ep[i-1] - psar[i-1])
                
                if self.low[i] <= psar[i]:
                    trend[i] = -1
                    psar[i] = ep[i-1]
                    ep[i] = self.low[i]
                    af_values[i] = af
                else:
                    trend[i] = 1
                    if self.high[i] > ep[i-1]:
                        ep[i] = self.high[i]
                        af_values[i] = min(af_values[i-1] + af, max_af)
                    else:
                        ep[i] = ep[i-1]
                        af_values[i] = af_values[i-1]
                        
            else:  # Downtrend
                psar[i] = psar[i-1] - af_values[i-1] * (psar[i-1] - ep[i-1])
                
                if self.high[i] >= psar[i]:
                    trend[i] = 1
                    psar[i] = ep[i-1]
                    ep[i] = self.high[i]
                    af_values[i] = af
                else:
                    trend[i] = -1
                    if self.low[i] < ep[i-1]:
                        ep[i] = self.low[i]
                        af_values[i] = min(af_values[i-1] + af, max_af)
                    else:
                        ep[i] = ep[i-1]
                        af_values[i] = af_values[i-1]
        
        current_psar = psar[-1]
        current_trend = trend[-1]
        current_price = self.close[-1]
        
        signals = []
        if current_trend == 1 and current_price > current_psar:
            signals.append({"signal": "شراء", "strength": 70, "reason": f"البارابوليك SAR يدعم الاتجاه الصاعد {current_psar:.4f}"})
        elif current_trend == -1 and current_price < current_psar:
            signals.append({"signal": "بيع", "strength": 70, "reason": f"البارابوليك SAR يدعم الاتجاه الهابط {current_psar:.4f}"})
        
        return {
            'psar': current_psar,
            'trend': current_trend,
            'signals': signals
        }
    
    def analyze_all_additional_indicators(self):
        """تحليل شامل لجميع المؤشرات الإضافية"""
        results = {}
        all_signals = []
        
        try:
            # Stochastic
            stoch = self.stochastic_oscillator()
            results['stochastic'] = stoch
            all_signals.extend(stoch['signals'])
            
            # Williams %R
            williams = self.williams_percent_r()
            results['williams_r'] = williams
            all_signals.extend(williams['signals'])
            
            # CCI
            cci = self.commodity_channel_index()
            results['cci'] = cci
            all_signals.extend(cci['signals'])
            
            # ADX
            adx = self.average_directional_index()
            results['adx'] = adx
            all_signals.extend(adx['signals'])
            
            # Parabolic SAR
            psar = self.parabolic_sar()
            results['parabolic_sar'] = psar
            all_signals.extend(psar['signals'])
            
        except Exception as e:
            print(f"خطأ في تحليل المؤشرات الإضافية: {e}")
        
        # تحليل الإشارات العامة
        buy_signals = len([s for s in all_signals if s['signal'] == 'شراء'])
        sell_signals = len([s for s in all_signals if s['signal'] == 'بيع'])
        
        # حساب متوسط القوة
        avg_strength = np.mean([s['strength'] for s in all_signals]) if all_signals else 50
        
        overall_signal = "محايد"
        if buy_signals > sell_signals:
            overall_signal = "شراء"
        elif sell_signals > buy_signals:
            overall_signal = "بيع"
        
        return {
            'indicators': results,
            'all_signals': all_signals,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'overall_signal': overall_signal,
            'average_strength': avg_strength
        }