"""
نظام تنبيهات الأسعار المتقدم
"""

import json
import os
from datetime import datetime, timedelta
import asyncio
from data_collector import DataCollector

class PriceAlerts:
    def __init__(self):
        self.alerts_file = "price_alerts.json"
        self.data_collector = DataCollector()
        self.alerts = self.load_alerts()
    
    def load_alerts(self):
        """تحميل التنبيهات المحفوظة"""
        try:
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "price_alerts": [],
                "indicator_alerts": [],
                "level_break_alerts": []
            }
    
    def save_alerts(self):
        """حفظ التنبيهات"""
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, ensure_ascii=False, indent=2)
    
    def add_price_alert(self, user_id, symbol, target_price, alert_type, timeframe="1h"):
        """إضافة تنبيه سعر"""
        alert = {
            "id": len(self.alerts["price_alerts"]) + 1,
            "user_id": user_id,
            "symbol": symbol.upper(),
            "target_price": float(target_price),
            "alert_type": alert_type,  # "above" أو "below"
            "timeframe": timeframe,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.alerts["price_alerts"].append(alert)
        self.save_alerts()
        return alert["id"]
    
    def add_indicator_alert(self, user_id, symbol, indicator, condition, value, timeframe="1h"):
        """إضافة تنبيه مؤشر فني"""
        alert = {
            "id": len(self.alerts["indicator_alerts"]) + 1,
            "user_id": user_id,
            "symbol": symbol.upper(),
            "indicator": indicator,  # "RSI", "MACD", "Stochastic"
            "condition": condition,  # "above", "below", "crossover"
            "value": float(value),
            "timeframe": timeframe,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.alerts["indicator_alerts"].append(alert)
        self.save_alerts()
        return alert["id"]
    
    def add_level_break_alert(self, user_id, symbol, level, level_type, timeframe="1h"):
        """إضافة تنبيه كسر المستويات"""
        alert = {
            "id": len(self.alerts["level_break_alerts"]) + 1,
            "user_id": user_id,
            "symbol": symbol.upper(),
            "level": float(level),
            "level_type": level_type,  # "support", "resistance"
            "timeframe": timeframe,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.alerts["level_break_alerts"].append(alert)
        self.save_alerts()
        return alert["id"]
    
    def check_price_alerts(self):
        """فحص تنبيهات الأسعار"""
        triggered_alerts = []
        
        for alert in self.alerts["price_alerts"]:
            if alert["status"] != "active":
                continue
            
            try:
                # جمع السعر الحالي
                data = self.data_collector.get_data_by_type(
                    alert["symbol"], 
                    period="1d", 
                    interval=alert["timeframe"]
                )
                
                if data is None or data.empty:
                    continue
                
                current_price = data['Close'].iloc[-1]
                
                # فحص الشرط
                alert_triggered = False
                if alert["alert_type"] == "above" and current_price >= alert["target_price"]:
                    alert_triggered = True
                elif alert["alert_type"] == "below" and current_price <= alert["target_price"]:
                    alert_triggered = True
                
                if alert_triggered:
                    triggered_alerts.append({
                        "alert": alert,
                        "current_price": current_price,
                        "message": self.format_price_alert_message(alert, current_price)
                    })
                    
                    # تغيير حالة التنبيه إلى مُفعل
                    alert["status"] = "triggered"
                    alert["triggered_at"] = datetime.now().isoformat()
                    alert["triggered_price"] = current_price
            
            except Exception as e:
                print(f"خطأ في فحص تنبيه السعر {alert['id']}: {e}")
        
        if triggered_alerts:
            self.save_alerts()
        
        return triggered_alerts
    
    def check_indicator_alerts(self):
        """فحص تنبيهات المؤشرات"""
        triggered_alerts = []
        
        for alert in self.alerts["indicator_alerts"]:
            if alert["status"] != "active":
                continue
            
            try:
                # جمع البيانات وحساب المؤشر
                data = self.data_collector.get_data_by_type(
                    alert["symbol"], 
                    period="5d", 
                    interval=alert["timeframe"]
                )
                
                if data is None or data.empty:
                    continue
                
                # حساب المؤشر المطلوب
                indicator_value = self.calculate_indicator_value(data, alert["indicator"])
                
                if indicator_value is None:
                    continue
                
                # فحص الشرط
                alert_triggered = False
                if alert["condition"] == "above" and indicator_value >= alert["value"]:
                    alert_triggered = True
                elif alert["condition"] == "below" and indicator_value <= alert["value"]:
                    alert_triggered = True
                
                if alert_triggered:
                    triggered_alerts.append({
                        "alert": alert,
                        "current_value": indicator_value,
                        "message": self.format_indicator_alert_message(alert, indicator_value)
                    })
                    
                    alert["status"] = "triggered"
                    alert["triggered_at"] = datetime.now().isoformat()
                    alert["triggered_value"] = indicator_value
            
            except Exception as e:
                print(f"خطأ في فحص تنبيه المؤشر {alert['id']}: {e}")
        
        if triggered_alerts:
            self.save_alerts()
        
        return triggered_alerts
    
    def calculate_indicator_value(self, data, indicator):
        """حساب قيمة المؤشر"""
        try:
            if indicator == "RSI":
                # حساب RSI مبسط
                delta = data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return rsi.iloc[-1]
            
            elif indicator == "MACD":
                # حساب MACD
                exp1 = data['Close'].ewm(span=12).mean()
                exp2 = data['Close'].ewm(span=26).mean()
                macd = exp1 - exp2
                return macd.iloc[-1]
            
            elif indicator == "Stochastic":
                # حساب Stochastic %K
                low_14 = data['Low'].rolling(window=14).min()
                high_14 = data['High'].rolling(window=14).max()
                k_percent = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
                return k_percent.iloc[-1]
            
        except Exception as e:
            print(f"خطأ في حساب المؤشر {indicator}: {e}")
            return None
    
    def format_price_alert_message(self, alert, current_price):
        """تنسيق رسالة تنبيه السعر"""
        direction = "فوق" if alert["alert_type"] == "above" else "تحت"
        
        message = f"""
🚨 **تنبيه سعر** 🚨

**الرمز:** `{alert['symbol']}`
**السعر المستهدف:** `{alert['target_price']:.4f}`
**السعر الحالي:** `{current_price:.4f}`
**الاتجاه:** {direction}

📊 **تفاصيل التنبيه:**
• **الفريم الزمني:** {alert['timeframe']}
• **تاريخ الإنشاء:** {alert['created_at'][:19]}
• **وقت التفعيل:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ تم الوصول للسعر المستهدف!
        """
        return message
    
    def format_indicator_alert_message(self, alert, current_value):
        """تنسيق رسالة تنبيه المؤشر"""
        condition_text = "فوق" if alert["condition"] == "above" else "تحت"
        
        message = f"""
📈 **تنبيه مؤشر فني** 📈

**الرمز:** `{alert['symbol']}`
**المؤشر:** {alert['indicator']}
**القيمة المستهدفة:** `{alert['value']:.2f}`
**القيمة الحالية:** `{current_value:.2f}`
**الشرط:** {condition_text}

📊 **تفاصيل التنبيه:**
• **الفريم الزمني:** {alert['timeframe']}
• **تاريخ الإنشاء:** {alert['created_at'][:19]}
• **وقت التفعيل:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ تم الوصول للشرط المطلوب!
        """
        return message
    
    def get_user_alerts(self, user_id):
        """الحصول على تنبيهات المستخدم"""
        user_alerts = {
            "price_alerts": [],
            "indicator_alerts": [],
            "level_break_alerts": []
        }
        
        for alert in self.alerts["price_alerts"]:
            if alert["user_id"] == user_id:
                user_alerts["price_alerts"].append(alert)
        
        for alert in self.alerts["indicator_alerts"]:
            if alert["user_id"] == user_id:
                user_alerts["indicator_alerts"].append(alert)
        
        for alert in self.alerts["level_break_alerts"]:
            if alert["user_id"] == user_id:
                user_alerts["level_break_alerts"].append(alert)
        
        return user_alerts
    
    def remove_alert(self, user_id, alert_type, alert_id):
        """حذف تنبيه"""
        alert_list = self.alerts.get(alert_type, [])
        
        for i, alert in enumerate(alert_list):
            if alert["id"] == alert_id and alert["user_id"] == user_id:
                del alert_list[i]
                self.save_alerts()
                return True
        
        return False
    
    async def monitor_alerts(self, bot, check_interval=60):
        """مراقبة التنبيهات بشكل مستمر"""
        while True:
            try:
                # فحص تنبيهات الأسعار
                price_alerts = self.check_price_alerts()
                for triggered in price_alerts:
                    try:
                        await bot.send_message(
                            chat_id=triggered["alert"]["user_id"],
                            text=triggered["message"],
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        print(f"خطأ في إرسال تنبيه السعر: {e}")
                
                # فحص تنبيهات المؤشرات
                indicator_alerts = self.check_indicator_alerts()
                for triggered in indicator_alerts:
                    try:
                        await bot.send_message(
                            chat_id=triggered["alert"]["user_id"],
                            text=triggered["message"],
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        print(f"خطأ في إرسال تنبيه المؤشر: {e}")
                
                # انتظار قبل الفحص التالي
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"خطأ في مراقبة التنبيهات: {e}")
                await asyncio.sleep(check_interval)