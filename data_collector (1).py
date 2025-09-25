import yfinance as yf
import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import time
from symbol_mapper import get_correct_symbol, determine_market_type

class DataCollector:
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.polygon_key = os.getenv("POLYGON_API_KEY")
        
    def get_data_by_type(self, symbol, market_type=None, period="5d", interval="1h", force_fresh=False):
        """جمع البيانات بناءً على نوع السوق مع ضمان البيانات الحديثة"""
        try:
            # تحويل الرمز إلى الرمز الصحيح
            correct_symbol = get_correct_symbol(symbol)
            
            # تحديد نوع السوق إذا لم يكن محدداً
            if market_type is None:
                market_type = determine_market_type(correct_symbol)
            
            ticker = yf.Ticker(correct_symbol)
            
            # محاولة الحصول على أحدث البيانات
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # استخدام period أكبر لضمان الحصول على بيانات حديثة
                    extended_period = "10d" if period == "5d" else period
                    data = ticker.history(period=extended_period, interval=interval)
                    
                    if not data.empty:
                        # فحص إذا كانت البيانات حديثة (خلال آخر 24 ساعة للبيانات اليومية)
                        last_data_time = data.index[-1]
                        current_time = datetime.now(last_data_time.tz)
                        time_diff = current_time - last_data_time
                        
                        # للفوركس: يعمل 24/5، للأسهم: يعمل خلال ساعات التداول
                        max_delay_hours = 48 if market_type == "forex" else 72  # 3 أيام للأسهم (نهاية الأسبوع)
                        
                        if time_diff.total_seconds() / 3600 < max_delay_hours or force_fresh:
                            print(f"✅ تم جمع بيانات حديثة للرمز {symbol} - آخر تحديث: {last_data_time}")
                            # إرجاع البيانات المطلوبة فقط
                            if period != extended_period:
                                return data.tail(min(len(data), self._get_periods_count(period, interval)))
                            return data
                        else:
                            print(f"⚠️ البيانات قديمة للرمز {symbol} - آخر تحديث قبل {time_diff}")
                    
                    # إذا لم تنجح، انتظر قليلاً وأعد المحاولة
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                        
                except Exception as inner_e:
                    print(f"محاولة {attempt + 1} فشلت للرمز {symbol}: {inner_e}")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
            
            # إذا فشلت جميع المحاولات، جرب البيانات الأساسية
            print(f"جاري المحاولة مع البيانات الأساسية للرمز {symbol}...")
            data = ticker.history(period="1d", interval="5m")
            
            if data.empty:
                print(f"❌ لا توجد بيانات للرمز: {symbol} ({correct_symbol})")
                return None
            
            print(f"✅ تم الحصول على بيانات أساسية للرمز {symbol}")
            return data
            
        except Exception as e:
            print(f"❌ خطأ شامل في جمع البيانات للرمز {symbol}: {e}")
            return None
    
    def _get_periods_count(self, period, interval):
        """حساب عدد النقاط المطلوبة حسب الفترة والفاصل الزمني"""
        period_map = {
            "1d": {"1m": 1440, "5m": 288, "15m": 96, "1h": 24, "4h": 6},
            "5d": {"1m": 7200, "5m": 1440, "15m": 480, "1h": 120, "4h": 30},
            "1mo": {"1h": 720, "4h": 180, "1d": 30}
        }
        return period_map.get(period, {}).get(interval, 100)
    
    def get_forex_data(self, symbol="EURUSD", period="1d", interval="1h"):
        """جمع بيانات الفوركس"""
        return self.get_data_by_type(symbol, 'forex', period, interval)
    
    def get_stock_data(self, symbol="AAPL", period="1d", interval="1h"):
        """جمع بيانات الأسهم"""
        return self.get_data_by_type(symbol, 'stock', period, interval)
    
    def get_crypto_data(self, symbol="BTC-USD", period="1d", interval="1h"):
        """جمع بيانات العملات الرقمية"""
        return self.get_data_by_type(symbol, 'crypto', period, interval)
    
    def get_index_data(self, symbol="US30", period="1d", interval="1h"):
        """جمع بيانات المؤشرات"""
        return self.get_data_by_type(symbol, 'index', period, interval)
    
    def get_commodity_data(self, symbol="GOLD", period="1d", interval="1h"):
        """جمع بيانات السلع"""
        return self.get_data_by_type(symbol, 'commodity', period, interval)
    
    def get_real_time_data(self, symbol, market_type="forex"):
        """الحصول على البيانات الفورية مع فحص التحديث"""
        try:
            print(f"🔄 جاري جمع البيانات الفورية للرمز {symbol}...")
            
            # جرب أولاً البيانات بفاصل زمني قصير
            data = self.get_data_by_type(symbol, market_type, period="1d", interval="1m", force_fresh=True)
            
            if data is None or data.empty:
                # جرب فاصل زمني أكبر
                print(f"⚠️ البيانات بدقيقة واحدة غير متوفرة، جاري المحاولة مع 5 دقائق...")
                data = self.get_data_by_type(symbol, market_type, period="1d", interval="5m", force_fresh=True)
            
            if data is None or data.empty:
                # جرب فاصل زمني أكبر
                print(f"⚠️ البيانات بـ5 دقائق غير متوفرة، جاري المحاولة مع ساعة واحدة...")
                data = self.get_data_by_type(symbol, market_type, period="5d", interval="1h", force_fresh=True)
            
            if data is not None and not data.empty:
                current_price = data['Close'].iloc[-1]
                data_time = data.index[-1]
                print(f"✅ السعر الحالي لـ {symbol}: {current_price:.5f} - وقت البيانات: {data_time}")
                return data
            else:
                print(f"❌ فشل في الحصول على بيانات فورية للرمز {symbol}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في الحصول على البيانات الفورية للرمز {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol, market_type=None):
        """الحصول على السعر الحالي فقط"""
        try:
            data = self.get_real_time_data(symbol, market_type)
            if data is not None and not data.empty:
                return {
                    'price': data['Close'].iloc[-1],
                    'time': data.index[-1],
                    'volume': data['Volume'].iloc[-1] if 'Volume' in data.columns else 0
                }
            return None
        except Exception as e:
            print(f"خطأ في الحصول على السعر الحالي: {e}")
            return None
    
    def verify_data_freshness(self, data, symbol):
        """التحقق من حداثة البيانات"""
        if data is None or data.empty:
            return False, "لا توجد بيانات"
        
        try:
            last_data_time = data.index[-1]
            current_time = datetime.now(last_data_time.tz)
            time_diff = current_time - last_data_time
            hours_old = time_diff.total_seconds() / 3600
            
            if hours_old < 2:
                return True, f"البيانات حديثة (قبل {hours_old:.1f} ساعة)"
            elif hours_old < 24:
                return True, f"البيانات مقبولة (قبل {hours_old:.1f} ساعة)"
            else:
                return False, f"البيانات قديمة (قبل {hours_old:.1f} ساعة)"
                
        except Exception as e:
            return False, f"خطأ في فحص البيانات: {e}"