from data_collector import DataCollector
from technical_analysis_simple import TechnicalAnalysisSimple
from advanced_patterns import AdvancedPatterns
from candlestick_patterns import CandlestickPatterns
from additional_indicators import AdditionalIndicators
from symbol_mapper import get_correct_symbol, determine_market_type, get_timeframe_config
import pandas as pd
from datetime import datetime
import json

class RecommendationSystem:
    """نظام التوصيات المتكامل"""
    
    def __init__(self):
        self.data_collector = DataCollector()
        
    def analyze_symbol(self, symbol, market_type=None, timeframe="1h"):
        """تحليل رمز معين وإخراج توصية شاملة"""
        try:
            # الحصول على إعدادات الفريم الزمني
            timeframe_config = get_timeframe_config(timeframe)
            period = timeframe_config['period']
            interval = timeframe_config['interval']
            
            # تحديد نوع السوق إذا لم يكن محدداً
            if market_type is None:
                correct_symbol = get_correct_symbol(symbol)
                market_type = determine_market_type(correct_symbol)
            
            # جمع البيانات
            data = self.data_collector.get_data_by_type(symbol, market_type, period, interval)
            
            if data is None or data.empty:
                return None
            
            # إجراء التحليل الفني الشامل
            analyzer = TechnicalAnalysisSimple(data)
            analysis_result = analyzer.comprehensive_analysis()
            
            # إضافة التحليلات المتقدمة
            try:
                advanced_patterns = AdvancedPatterns(data)
                patterns_result = advanced_patterns.analyze_all_patterns()
                analysis_result['advanced_patterns'] = patterns_result
            except Exception as e:
                print(f"خطأ في تحليل النماذج المتقدمة: {e}")
                analysis_result['advanced_patterns'] = {}
            
            try:
                candlestick_analyzer = CandlestickPatterns(data)
                candlestick_result = candlestick_analyzer.analyze_all_candlestick_patterns()
                analysis_result['candlestick_patterns'] = candlestick_result
            except Exception as e:
                print(f"خطأ في تحليل الشموع اليابانية: {e}")
                analysis_result['candlestick_patterns'] = {}
            
            try:
                additional_indicators = AdditionalIndicators(data)
                indicators_result = additional_indicators.analyze_all_additional_indicators()
                analysis_result['additional_indicators'] = indicators_result
            except Exception as e:
                print(f"خطأ في المؤشرات الإضافية: {e}")
                analysis_result['additional_indicators'] = {}
            
            # تحسين التوصية
            recommendation = self.enhance_recommendation(analysis_result, symbol, market_type, timeframe)
            
            return recommendation
            
        except Exception as e:
            print(f"خطأ في تحليل الرمز {symbol}: {e}")
            return None
    
    def enhance_recommendation(self, analysis_result, symbol, market_type, timeframe):
        """تحسين التوصية بإضافة معلومات إضافية"""
        recommendation = analysis_result['recommendation']
        
        # إضافة معلومات الرمز
        recommendation['symbol'] = symbol
        recommendation['market_type'] = market_type
        recommendation['timeframe'] = timeframe
        recommendation['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # تحسين نسبة النجاح بناءً على قوة الإشارات والتحليلات المتقدمة
        base_success_rate = 60
        
        # إضافة نقاط إضافية للنماذج والشموع
        pattern_bonus = 0
        if 'advanced_patterns' in analysis_result and analysis_result['advanced_patterns'].get('patterns'):
            pattern_bonus += len(analysis_result['advanced_patterns']['patterns']) * 2
        
        if 'candlestick_patterns' in analysis_result and analysis_result['candlestick_patterns'].get('patterns'):
            pattern_bonus += len(analysis_result['candlestick_patterns']['patterns']) * 1.5
        
        if recommendation['confidence'] > 80:
            success_rate = min(90, base_success_rate + 25 + pattern_bonus)
        elif recommendation['confidence'] > 70:
            success_rate = min(85, base_success_rate + 20 + pattern_bonus)
        elif recommendation['confidence'] > 60:
            success_rate = min(80, base_success_rate + 15 + pattern_bonus)
        else:
            success_rate = min(75, base_success_rate + pattern_bonus)
        
        recommendation['success_rate'] = success_rate
        
        # تحسين الوقت المتوقع بناءً على نوع السوق والفريم الزمني
        if timeframe in ['1m', '5m']:
            recommendation['expected_time'] = "5-30 دقيقة"
        elif timeframe in ['15m', '30m']:
            recommendation['expected_time'] = "30 دقيقة - 2 ساعة"
        elif timeframe == '1h':
            if market_type == "forex":
                recommendation['expected_time'] = "2-8 ساعات"
            elif market_type == "crypto":
                recommendation['expected_time'] = "1-6 ساعات"
            else:
                recommendation['expected_time'] = "4-12 ساعة"
        elif timeframe == '4h':
            recommendation['expected_time'] = "8-24 ساعة"
        elif timeframe == '1d':
            recommendation['expected_time'] = "1-5 أيام"
        elif timeframe == '1w':
            recommendation['expected_time'] = "1-4 أسابيع"
        else:
            recommendation['expected_time'] = "1-3 أشهر"
        
        return recommendation
    
    def format_recommendation_message(self, recommendation):
        """تنسيق رسالة التوصية للإرسال عبر التلغرام"""
        if not recommendation:
            return "❌ لم يتم العثور على بيانات كافية للتحليل"
        
        symbol = recommendation.get('symbol', 'غير محدد')
        rec_type = recommendation.get('type', 'محايد')
        entry = recommendation.get('entry_point', 0)
        targets = recommendation.get('targets', {})
        stop_loss = recommendation.get('stop_loss', 0)
        confidence = recommendation.get('confidence', 0)
        success_rate = recommendation.get('success_rate', 0)
        supporting_schools = recommendation.get('supporting_schools', 0)
        expected_time = recommendation.get('expected_time', 'غير محدد')
        risk_reward = recommendation.get('risk_reward', 0)
        market_type = recommendation.get('market_type', 'غير محدد')
        timeframe = recommendation.get('timeframe', '1h')
        
        # تحديد نوع السوق بالعربية
        market_types_ar = {
            'forex': 'فوركس',
            'crypto': 'عملة رقمية',
            'stock': 'سهم',
            'index': 'مؤشر',
            'commodity': 'سلعة'
        }
        market_type_ar = market_types_ar.get(market_type, market_type)
        
        # اختيار الأيقونة بناءً على نوع التوصية
        if rec_type == "شراء":
            icon = "🟢"
            action_icon = "📈"
        elif rec_type == "بيع":
            icon = "🔴"
            action_icon = "📉"
        else:
            icon = "🟡"
            action_icon = "⏸️"
        
        # إضافة معلومات النماذج والشموع المكتشفة
        patterns_info = ""
        candlestick_info = ""
        
        # النماذج الفنية المتقدمة
        if 'advanced_patterns' in recommendation and recommendation['advanced_patterns'].get('patterns'):
            top_patterns = recommendation['advanced_patterns']['patterns'][:3]
            if top_patterns:
                patterns_info = "\n\n**🔍 النماذج الفنية المكتشفة:**\n"
                for pattern in top_patterns:
                    strength = pattern.get('strength', 50)
                    pattern_type = pattern.get('type', 'غير محدد')
                    direction = pattern.get('direction', 'محايد')
                    patterns_info += f"• {pattern_type}: {direction} ({strength}%)\n"
        
        # الشموع اليابانية
        if 'candlestick_patterns' in recommendation and recommendation['candlestick_patterns'].get('patterns'):
            top_candles = recommendation['candlestick_patterns']['patterns'][:3]
            if top_candles:
                candlestick_info = "\n\n**🕯️ الشموع اليابانية:**\n"
                for candle in top_candles:
                    strength = candle.get('strength', 50)
                    candle_type = candle.get('type', 'غير محدد')
                    signal = candle.get('signal', 'محايد')
                    candlestick_info += f"• {candle_type}: {signal} ({strength}%)\n"

        message = f"""
{icon} **توصية تحليل متكامل متقدم** {action_icon}

**الرمز:** `{symbol}` ({market_type_ar})
**الفريم الزمني:** `{timeframe}`
**نوع الصفقة:** {rec_type}
**نقطة الدخول:** `{entry:.4f}`

**🎯 الأهداف:**
• الهدف الأول: `{targets.get('tp1', 0):.4f}`
• الهدف الثاني: `{targets.get('tp2', 0):.4f}`
• الهدف الثالث: `{targets.get('tp3', 0):.4f}`

**🛑 وقف الخسارة:** `{stop_loss:.4f}`

**📊 إحصائيات التحليل:**
• المدارس المؤيدة: {supporting_schools} من 7
• نسبة الثقة: {confidence:.1f}%
• نسبة النجاح المتوقعة: {success_rate}%
• نسبة المخاطر/المكافأة: 1:{risk_reward:.1f}
• الزمن المتوقع: {expected_time}{patterns_info}{candlestick_info}

**⏰ وقت التحليل:** {recommendation.get('timestamp', 'غير محدد')}

━━━━━━━━━━━━━━━━━━━━━━━
🤖 *تحليل آلي متعدد المدارس + نماذج متقدمة*
⚠️ *يُرجى إدارة المخاطر بحكمة*
"""
        
        return message
    
    def get_multiple_recommendations(self, symbols_config):
        """الحصول على توصيات متعددة"""
        recommendations = []
        
        for config in symbols_config:
            symbol = config.get('symbol')
            market_type = config.get('market_type', 'forex')
            
            rec = self.analyze_symbol(symbol, market_type)
            if rec:
                recommendations.append(rec)
        
        return recommendations
    
    def get_market_overview(self):
        """نظرة عامة على السوق"""
        major_pairs = [
            {'symbol': 'EURUSD', 'market_type': 'forex'},
            {'symbol': 'GBPUSD', 'market_type': 'forex'},
            {'symbol': 'USDJPY', 'market_type': 'forex'},
            {'symbol': 'BTC-USD', 'market_type': 'crypto'},
            {'symbol': 'ETH-USD', 'market_type': 'crypto'}
        ]
        
        overview = {
            'bullish': 0,
            'bearish': 0,
            'neutral': 0,
            'recommendations': []
        }
        
        for pair in major_pairs:
            rec = self.analyze_symbol(pair['symbol'], pair['market_type'])
            if rec:
                overview['recommendations'].append(rec)
                
                if rec['type'] == 'شراء':
                    overview['bullish'] += 1
                elif rec['type'] == 'بيع':
                    overview['bearish'] += 1
                else:
                    overview['neutral'] += 1
        
        return overview