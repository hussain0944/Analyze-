"""
رسوم بيانية بسيطة للأسعار والمؤشرات
"""

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
from datetime import datetime
import pandas as pd
import numpy as np
import io
import base64

class SimpleCharts:
    def __init__(self):
        # إعداد الخط العربي
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial']
        plt.style.use('default')
    
    def create_price_chart(self, data, symbol, timeframe="1h"):
        """إنشاء رسم بياني للأسعار"""
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
            
            # الرسم البياني الرئيسي للأسعار
            ax1.plot(data.index, data['Close'], color='#2E86AB', linewidth=2, label='السعر')
            
            # إضافة المتوسطات المتحركة
            if len(data) >= 20:
                ma20 = data['Close'].rolling(window=20).mean()
                ax1.plot(data.index, ma20, color='#A23B72', linewidth=1.5, label='MA20', alpha=0.8)
            
            if len(data) >= 50:
                ma50 = data['Close'].rolling(window=50).mean()
                ax1.plot(data.index, ma50, color='#F18F01', linewidth=1.5, label='MA50', alpha=0.8)
            
            # تنسيق الرسم البياني الرئيسي
            ax1.set_title(f'{symbol} - {timeframe}', fontsize=16, fontweight='bold')
            ax1.set_ylabel('السعر', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # رسم بياني للحجم
            if 'Volume' in data.columns:
                ax2.bar(data.index, data['Volume'], color='#C73E1D', alpha=0.6, width=0.8)
                ax2.set_ylabel('الحجم', fontsize=12)
                ax2.grid(True, alpha=0.3)
            
            # تنسيق التواريخ
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            
            # تدوير التسميات
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # حفظ الرسم كصورة في الذاكرة
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            # تحويل إلى base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            plt.close(fig)
            return image_base64
        
        except Exception as e:
            print(f"خطأ في إنشاء الرسم البياني: {e}")
            return None
    
    def create_indicators_chart(self, data, symbol):
        """إنشاء رسم بياني للمؤشرات الفنية"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # RSI
            try:
                delta = data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                ax1.plot(data.index, rsi, color='#2E86AB', linewidth=2)
                ax1.axhline(y=70, color='r', linestyle='--', alpha=0.7)
                ax1.axhline(y=30, color='g', linestyle='--', alpha=0.7)
                ax1.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
                ax1.set_title('RSI (14)', fontweight='bold')
                ax1.set_ylabel('RSI')
                ax1.grid(True, alpha=0.3)
                ax1.set_ylim(0, 100)
            except:
                ax1.text(0.5, 0.5, 'خطأ في حساب RSI', transform=ax1.transAxes, ha='center')
            
            # MACD
            try:
                exp1 = data['Close'].ewm(span=12).mean()
                exp2 = data['Close'].ewm(span=26).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9).mean()
                histogram = macd - signal
                
                ax2.plot(data.index, macd, color='#2E86AB', label='MACD', linewidth=2)
                ax2.plot(data.index, signal, color='#A23B72', label='Signal', linewidth=2)
                ax2.bar(data.index, histogram, color='gray', alpha=0.3, label='Histogram')
                ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
                ax2.set_title('MACD', fontweight='bold')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            except:
                ax2.text(0.5, 0.5, 'خطأ في حساب MACD', transform=ax2.transAxes, ha='center')
            
            # Bollinger Bands
            try:
                sma = data['Close'].rolling(window=20).mean()
                std = data['Close'].rolling(window=20).std()
                upper_band = sma + (std * 2)
                lower_band = sma - (std * 2)
                
                ax3.plot(data.index, data['Close'], color='#2E86AB', label='السعر', linewidth=2)
                ax3.plot(data.index, sma, color='#F18F01', label='SMA20', linewidth=1.5)
                ax3.fill_between(data.index, upper_band, lower_band, alpha=0.2, color='gray')
                ax3.plot(data.index, upper_band, color='red', linestyle='--', alpha=0.7)
                ax3.plot(data.index, lower_band, color='green', linestyle='--', alpha=0.7)
                ax3.set_title('Bollinger Bands', fontweight='bold')
                ax3.legend()
                ax3.grid(True, alpha=0.3)
            except:
                ax3.text(0.5, 0.5, 'خطأ في حساب Bollinger Bands', transform=ax3.transAxes, ha='center')
            
            # Stochastic
            try:
                low_14 = data['Low'].rolling(window=14).min()
                high_14 = data['High'].rolling(window=14).max()
                k_percent = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
                d_percent = k_percent.rolling(window=3).mean()
                
                ax4.plot(data.index, k_percent, color='#2E86AB', label='%K', linewidth=2)
                ax4.plot(data.index, d_percent, color='#A23B72', label='%D', linewidth=2)
                ax4.axhline(y=80, color='r', linestyle='--', alpha=0.7)
                ax4.axhline(y=20, color='g', linestyle='--', alpha=0.7)
                ax4.set_title('Stochastic', fontweight='bold')
                ax4.set_ylabel('Stochastic')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
                ax4.set_ylim(0, 100)
            except:
                ax4.text(0.5, 0.5, 'خطأ في حساب Stochastic', transform=ax4.transAxes, ha='center')
            
            # تنسيق التواريخ لجميع الرسوم البيانية
            for ax in [ax1, ax2, ax3, ax4]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.suptitle(f'المؤشرات الفنية - {symbol}', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # حفظ الرسم كصورة في الذاكرة
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            # تحويل إلى base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            plt.close(fig)
            return image_base64
        
        except Exception as e:
            print(f"خطأ في إنشاء رسم المؤشرات: {e}")
            return None
    
    def create_pattern_chart(self, data, patterns, symbol):
        """إنشاء رسم بياني يظهر النماذج الفنية المكتشفة"""
        try:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # رسم السعر
            ax.plot(data.index, data['Close'], color='#2E86AB', linewidth=2, label='السعر')
            
            # إضافة النماذج المكتشفة
            colors = ['red', 'orange', 'purple', 'brown', 'pink']
            
            for i, pattern in enumerate(patterns[:5]):  # أول 5 نماذج فقط
                if i < len(colors):
                    # إضافة نقاط أو خطوط للنماذج
                    if 'support' in pattern.get('type', '').lower():
                        level = pattern.get('level', data['Close'].iloc[-1])
                        ax.axhline(y=level, color='green', linestyle='--', alpha=0.7, 
                                 label=f"دعم: {pattern.get('type', 'غير محدد')}")
                    elif 'resistance' in pattern.get('type', '').lower() or 'مقاومة' in pattern.get('type', ''):
                        level = pattern.get('level', data['Close'].iloc[-1])
                        ax.axhline(y=level, color='red', linestyle='--', alpha=0.7, 
                                 label=f"مقاومة: {pattern.get('type', 'غير محدد')}")
                    else:
                        # للنماذج الأخرى، أضف نقطة في المنتصف
                        mid_point = len(data) // 2
                        if mid_point < len(data):
                            ax.scatter(data.index[mid_point], data['Close'].iloc[mid_point], 
                                     color=colors[i], s=100, alpha=0.8, 
                                     label=f"{pattern.get('type', 'غير محدد')}")
            
            ax.set_title(f'النماذج الفنية المكتشفة - {symbol}', fontsize=16, fontweight='bold')
            ax.set_ylabel('السعر', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # تنسيق التواريخ
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # حفظ الرسم كصورة في الذاكرة
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            # تحويل إلى base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            plt.close(fig)
            return image_base64
        
        except Exception as e:
            print(f"خطأ في إنشاء رسم النماذج: {e}")
            return None
    
    def save_chart_as_file(self, image_base64, filename):
        """حفظ الرسم البياني كملف"""
        try:
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(image_base64))
            return filename
        except Exception as e:
            print(f"خطأ في حفظ الملف: {e}")
            return None