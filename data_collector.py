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
        
    def get_data_by_type(self, symbol, market_type=None, period="5d", interval="1h"):
        """جمع البيانات بناءً على نوع السوق"""
        try:
            # تحويل الرمز إلى الرمز الصحيح
            correct_symbol = get_correct_symbol(symbol)
            
            # تحديد نوع السوق إذا لم يكن محدداً
            if market_type is None:
                market_type = determine_market_type(correct_symbol)
            
            ticker = yf.Ticker(correct_symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"لا توجد بيانات للرمز: {symbol} ({correct_symbol})")
                return None
            
            return data
        except Exception as e:
            print(f"خطأ في جمع البيانات للرمز {symbol}: {e}")
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