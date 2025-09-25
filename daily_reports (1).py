"""
نظام التقارير اليومية والإحصائيات
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_collector import DataCollector

class DailyReports:
    def __init__(self):
        self.trades_file = "trading_history.json"
        self.reports_file = "daily_reports.json"
        self.data_collector = DataCollector()
        self.trading_history = self.load_trading_history()
    
    def load_trading_history(self):
        """تحميل تاريخ الصفقات"""
        try:
            with open(self.trades_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "trades": [],
                "daily_stats": {}
            }
    
    def save_trading_history(self):
        """حفظ تاريخ الصفقات"""
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(self.trading_history, f, ensure_ascii=False, indent=2)
    
    def add_trade_result(self, symbol, recommendation_type, entry_price, exit_price, 
                        pips_gained, success, timeframe, analysis_time):
        """إضافة نتيجة صفقة"""
        trade = {
            "id": len(self.trading_history["trades"]) + 1,
            "symbol": symbol,
            "type": recommendation_type,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pips_gained": pips_gained,
            "success": success,
            "timeframe": timeframe,
            "analysis_time": analysis_time,
            "trade_date": datetime.now().strftime('%Y-%m-%d'),
            "trade_time": datetime.now().strftime('%H:%M:%S')
        }
        
        self.trading_history["trades"].append(trade)
        self.update_daily_stats(trade)
        self.save_trading_history()
    
    def update_daily_stats(self, trade):
        """تحديث الإحصائيات اليومية"""
        today = trade["trade_date"]
        
        if today not in self.trading_history["daily_stats"]:
            self.trading_history["daily_stats"][today] = {
                "total_trades": 0,
                "successful_trades": 0,
                "failed_trades": 0,
                "total_pips": 0,
                "success_rate": 0,
                "symbols_traded": set(),
                "timeframes_used": set(),
                "best_trade": {"pips": 0, "symbol": "", "type": ""},
                "worst_trade": {"pips": 0, "symbol": "", "type": ""}
            }
        
        stats = self.trading_history["daily_stats"][today]
        
        # تحديث الإحصائيات
        stats["total_trades"] += 1
        stats["total_pips"] += trade["pips_gained"]
        stats["symbols_traded"].add(trade["symbol"])
        stats["timeframes_used"].add(trade["timeframe"])
        
        if trade["success"]:
            stats["successful_trades"] += 1
        else:
            stats["failed_trades"] += 1
        
        # حساب نسبة النجاح
        stats["success_rate"] = (stats["successful_trades"] / stats["total_trades"]) * 100
        
        # أفضل وأسوأ صفقة
        if trade["pips_gained"] > stats["best_trade"]["pips"]:
            stats["best_trade"] = {
                "pips": trade["pips_gained"],
                "symbol": trade["symbol"],
                "type": trade["type"]
            }
        
        if trade["pips_gained"] < stats["worst_trade"]["pips"]:
            stats["worst_trade"] = {
                "pips": trade["pips_gained"],
                "symbol": trade["symbol"],
                "type": trade["type"]
            }
        
        # تحويل sets إلى lists للتخزين
        stats["symbols_traded"] = list(stats["symbols_traded"])
        stats["timeframes_used"] = list(stats["timeframes_used"])
    
    def generate_daily_report(self, date=None):
        """إنشاء التقرير اليومي"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if date not in self.trading_history["daily_stats"]:
            return self.generate_empty_report(date)
        
        stats = self.trading_history["daily_stats"][date]
        
        # حساب إحصائيات إضافية
        day_trades = [t for t in self.trading_history["trades"] if t["trade_date"] == date]
        
        # تحليل الأداء حسب الرمز
        symbol_performance = {}
        for trade in day_trades:
            symbol = trade["symbol"]
            if symbol not in symbol_performance:
                symbol_performance[symbol] = {"trades": 0, "successful": 0, "pips": 0}
            
            symbol_performance[symbol]["trades"] += 1
            symbol_performance[symbol]["pips"] += trade["pips_gained"]
            if trade["success"]:
                symbol_performance[symbol]["successful"] += 1
        
        # تحليل الأداء حسب الفريم الزمني
        timeframe_performance = {}
        for trade in day_trades:
            tf = trade["timeframe"]
            if tf not in timeframe_performance:
                timeframe_performance[tf] = {"trades": 0, "successful": 0, "pips": 0}
            
            timeframe_performance[tf]["trades"] += 1
            timeframe_performance[tf]["pips"] += trade["pips_gained"]
            if trade["success"]:
                timeframe_performance[tf]["successful"] += 1
        
        # تنسيق التقرير
        report = f"""
📊 **التقرير اليومي - {date}** 📊

📈 **الإحصائيات العامة:**
• إجمالي الصفقات: `{stats['total_trades']}`
• الصفقات الناجحة: `{stats['successful_trades']}` ✅
• الصفقات الخاسرة: `{stats['failed_trades']}` ❌
• نسبة النجاح: `{stats['success_rate']:.1f}%`
• إجمالي النقاط: `{stats['total_pips']:+.1f}` نقطة

🏆 **أفضل صفقة:**
• الرمز: `{stats['best_trade']['symbol']}`
• النوع: {stats['best_trade']['type']}
• النقاط: `+{stats['best_trade']['pips']:.1f}`

📉 **أسوأ صفقة:**
• الرمز: `{stats['worst_trade']['symbol']}`
• النوع: {stats['worst_trade']['type']}
• النقاط: `{stats['worst_trade']['pips']:+.1f}`

💹 **الأداء حسب الرمز:**"""
        
        for symbol, perf in symbol_performance.items():
            success_rate = (perf["successful"] / perf["trades"]) * 100 if perf["trades"] > 0 else 0
            report += f"""
• **{symbol}:** {perf['trades']} صفقة | {success_rate:.1f}% | {perf['pips']:+.1f} نقطة"""
        
        report += f"""

⏰ **الأداء حسب الفريم الزمني:**"""
        
        for tf, perf in timeframe_performance.items():
            success_rate = (perf["successful"] / perf["trades"]) * 100 if perf["trades"] > 0 else 0
            report += f"""
• **{tf}:** {perf['trades']} صفقة | {success_rate:.1f}% | {perf['pips']:+.1f} نقطة"""
        
        return report
    
    def generate_empty_report(self, date):
        """إنشاء تقرير فارغ"""
        return f"""
📊 **التقرير اليومي - {date}** 📊

📭 لا توجد صفقات لهذا اليوم.
        """
    
    def generate_weekly_report(self):
        """إنشاء تقرير أسبوعي"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        week_trades = []
        total_pips = 0
        successful_trades = 0
        total_trades = 0
        
        # جمع صفقات الأسبوع
        for trade in self.trading_history["trades"]:
            trade_date = datetime.strptime(trade["trade_date"], '%Y-%m-%d')
            if start_date <= trade_date <= end_date:
                week_trades.append(trade)
                total_pips += trade["pips_gained"]
                total_trades += 1
                if trade["success"]:
                    successful_trades += 1
        
        if total_trades == 0:
            return "📭 لا توجد صفقات للأسبوع الماضي."
        
        success_rate = (successful_trades / total_trades) * 100
        
        # أفضل وأسوأ يوم
        daily_pips = {}
        for trade in week_trades:
            date = trade["trade_date"]
            if date not in daily_pips:
                daily_pips[date] = 0
            daily_pips[date] += trade["pips_gained"]
        
        best_day = max(daily_pips.items(), key=lambda x: x[1])
        worst_day = min(daily_pips.items(), key=lambda x: x[1])
        
        report = f"""
📊 **التقرير الأسبوعي** 📊
🗓️ {start_date.strftime('%Y-%m-%d')} إلى {end_date.strftime('%Y-%m-%d')}

📈 **الإحصائيات العامة:**
• إجمالي الصفقات: `{total_trades}`
• الصفقات الناجحة: `{successful_trades}` ✅
• الصفقات الخاسرة: `{total_trades - successful_trades}` ❌
• نسبة النجاح: `{success_rate:.1f}%`
• إجمالي النقاط: `{total_pips:+.1f}` نقطة
• متوسط النقاط يومياً: `{total_pips/7:+.1f}`

🏆 **أفضل يوم:**
• التاريخ: {best_day[0]}
• النقاط: `+{best_day[1]:.1f}`

📉 **أسوأ يوم:**
• التاريخ: {worst_day[0]}
• النقاط: `{worst_day[1]:+.1f}`
        """
        
        return report
    
    def analyze_pair_correlation(self, pairs=None, period="1mo"):
        """تحليل الارتباط بين أزواج العملات"""
        if pairs is None:
            pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
        
        correlation_data = {}
        
        # جمع البيانات لكل زوج
        for pair in pairs:
            try:
                data = self.data_collector.get_data_by_type(pair, period=period, interval="1d")
                if data is not None and not data.empty:
                    correlation_data[pair] = data['Close'].pct_change().dropna()
            except Exception as e:
                print(f"خطأ في جمع بيانات {pair}: {e}")
        
        if len(correlation_data) < 2:
            return "❌ لا توجد بيانات كافية لتحليل الارتباط."
        
        # إنشاء DataFrame للارتباط
        df = pd.DataFrame(correlation_data)
        correlation_matrix = df.corr()
        
        # تنسيق التقرير
        report = """
🔗 **تحليل الارتباط بين أزواج العملات** 🔗

📊 **مصفوفة الارتباط:**
```
"""
        
        # إضافة مصفوفة الارتباط
        for i, pair1 in enumerate(correlation_matrix.columns):
            row = f"{pair1:8}"
            for j, pair2 in enumerate(correlation_matrix.columns):
                if i <= j:
                    correlation = correlation_matrix.loc[pair1, pair2]
                    row += f" {correlation:6.2f}"
                else:
                    row += "       "
            report += row + "\n"
        
        report += "```\n\n"
        
        # تحليل الارتباطات القوية
        strong_correlations = []
        for i, pair1 in enumerate(correlation_matrix.columns):
            for j, pair2 in enumerate(correlation_matrix.columns):
                if i < j:  # تجنب التكرار
                    correlation = correlation_matrix.loc[pair1, pair2]
                    if abs(correlation) > 0.7:
                        strong_correlations.append((pair1, pair2, correlation))
        
        if strong_correlations:
            report += "🔥 **ارتباطات قوية (أكثر من 0.7):**\n"
            for pair1, pair2, corr in strong_correlations:
                correlation_type = "طردي" if corr > 0 else "عكسي"
                report += f"• **{pair1}** و **{pair2}**: {corr:.2f} ({correlation_type})\n"
        else:
            report += "📊 لا توجد ارتباطات قوية حالياً.\n"
        
        report += f"""

📈 **تفسير الارتباط:**
• **+1.0**: ارتباط طردي كامل
• **0.0**: لا يوجد ارتباط
• **-1.0**: ارتباط عكسي كامل
• **>0.7**: ارتباط قوي
• **0.3-0.7**: ارتباط متوسط
• **<0.3**: ارتباط ضعيف
        """
        
        return report
    
    def generate_performance_summary(self, days=30):
        """إنشاء ملخص الأداء لفترة معينة"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        period_trades = []
        for trade in self.trading_history["trades"]:
            trade_date = datetime.strptime(trade["trade_date"], '%Y-%m-%d')
            if start_date <= trade_date <= end_date:
                period_trades.append(trade)
        
        if not period_trades:
            return f"📭 لا توجد صفقات في آخر {days} يوم."
        
        # حساب الإحصائيات
        total_trades = len(period_trades)
        successful_trades = sum(1 for t in period_trades if t["success"])
        total_pips = sum(t["pips_gained"] for t in period_trades)
        success_rate = (successful_trades / total_trades) * 100
        
        # أفضل وأسوأ صفقة
        best_trade = max(period_trades, key=lambda x: x["pips_gained"])
        worst_trade = min(period_trades, key=lambda x: x["pips_gained"])
        
        # الأداء حسب نوع التوصية
        buy_trades = [t for t in period_trades if t["type"] == "شراء"]
        sell_trades = [t for t in period_trades if t["type"] == "بيع"]
        
        buy_success = sum(1 for t in buy_trades if t["success"]) / len(buy_trades) * 100 if buy_trades else 0
        sell_success = sum(1 for t in sell_trades if t["success"]) / len(sell_trades) * 100 if sell_trades else 0
        
        return f"""
📊 **ملخص الأداء - آخر {days} يوم** 📊

📈 **الإحصائيات العامة:**
• إجمالي الصفقات: `{total_trades}`
• نسبة النجاح: `{success_rate:.1f}%`
• إجمالي النقاط: `{total_pips:+.1f}`
• متوسط النقاط للصفقة: `{total_pips/total_trades:+.1f}`

🎯 **الأداء حسب نوع التوصية:**
• صفقات الشراء: `{len(buy_trades)}` | نجاح `{buy_success:.1f}%`
• صفقات البيع: `{len(sell_trades)}` | نجاح `{sell_success:.1f}%`

🏆 **أفضل صفقة:**
• {best_trade['symbol']} | {best_trade['type']} | `+{best_trade['pips_gained']:.1f}` نقطة

📉 **أسوأ صفقة:**
• {worst_trade['symbol']} | {worst_trade['type']} | `{worst_trade['pips_gained']:+.1f}` نقطة
        """