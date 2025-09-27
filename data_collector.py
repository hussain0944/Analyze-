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

    @staticmethod
    def _is_data_fresh(data: pd.DataFrame, max_age_hours: int = 72) -> bool:
        """تحقق من حداثة آخر شمعة في البيانات."""
        try:
            last_ts = data.index[-1]
            if not isinstance(last_ts, pd.Timestamp):
                last_ts = pd.to_datetime(last_ts)
            # استخدم UTC للمقارنة
            now = pd.Timestamp.utcnow()
            # إذا كان last_ts timezone-aware، حرّف now لنفس tz
            if getattr(last_ts, 'tzinfo', None) is not None:
                now = now.tz_localize('UTC').tz_convert(last_ts.tz)
            age = now - last_ts
            return age.total_seconds() <= max_age_hours * 3600
        except Exception:
            return False
        
    def get_data_by_type(self, symbol, market_type=None, period="5d", interval="1h", retries: int = 3, sleep_seconds: int = 2):
        """جمع البيانات بناءً على نوع السوق مع محاولات وإحكام حداثة البيانات"""
        # تحويل الرمز إلى الرمز الصحيح
        correct_symbol = get_correct_symbol(symbol)
        
        # تحديد نوع السوق إذا لم يكن محدداً
        if market_type is None:
            market_type = determine_market_type(correct_symbol)
        
        last_exception = None
        for attempt in range(1, retries + 1):
            try:
                ticker = yf.Ticker(correct_symbol)
                data = ticker.history(period=period, interval=interval)
                if data is None or data.empty:
                    raise ValueError("No data returned from yfinance")
                # تأكد من وجود الأعمدة الأساسية
                for col in ["Open", "High", "Low", "Close"]:
                    if col not in data.columns:
                        raise ValueError(f"Missing required column: {col}")
                # تحقق من حداثة البيانات
                if not self._is_data_fresh(data):
                    raise ValueError("Stale data (older than 72h)")
                return data
            except Exception as e:
                last_exception = e
                if attempt < retries:
                    time.sleep(sleep_seconds)
                else:
                    print(f"خطأ في جمع البيانات للرمز {symbol} بعد {attempt} محاولات: {e}")
        return None

    def get_current_price(self, symbol, market_type=None):
        """الحصول على السعر الحالي فقط بشكل سريع."""
        data = self.get_data_by_type(symbol, market_type=market_type, period="1d", interval="1m")
        if data is None or data.empty:
            return None
        try:
            return float(data["Close"].iloc[-1])
        except Exception:
            return None

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
        """الحصول على البيانات الفورية"""
        try:
            if market_type == "forex":
                return self.get_forex_data(symbol, period="1d", interval="1m")
            elif market_type == "stock":
                return self.get_stock_data(symbol, period="1d", interval="1m")
            elif market_type == "crypto":
                return self.get_crypto_data(symbol, period="1d", interval="1m")
        except Exception as e:
            print(f"خطأ في الحصول على البيانات الفورية: {e}")
            return None