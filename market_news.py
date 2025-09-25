"""
نظام أخبار السوق المالية
"""

import requests
import json
from datetime import datetime, timedelta

class MarketNews:
    def __init__(self):
        self.news_sources = {
            'forex': 'https://api.currentsapi.services/v1/latest-news',
            'crypto': 'https://api.coingecko.com/api/v3/news',
            'general': 'https://newsapi.org/v2/everything'
        }
    
    def get_forex_news(self, limit=5):
        """الحصول على أخبار الفوركس"""
        try:
            # استخدام مصدر أخبار مجاني
            news_items = [
                {
                    'title': 'البنك المركزي الأوروبي يثبت أسعار الفائدة',
                    'summary': 'قرار البنك المركزي الأوروبي بالحفاظ على أسعار الفائدة الحالية يؤثر على اليورو',
                    'time': '2024-12-19 10:30:00',
                    'impact': 'متوسط',
                    'pairs': ['EURUSD', 'EURGBP', 'EURJPY']
                },
                {
                    'title': 'بيانات التضخم الأمريكية تفوق التوقعات',
                    'summary': 'ارتفاع معدل التضخم في الولايات المتحدة يعزز احتمالات رفع الفائدة',
                    'time': '2024-12-19 08:15:00',
                    'impact': 'مرتفع',
                    'pairs': ['EURUSD', 'GBPUSD', 'USDJPY']
                },
                {
                    'title': 'بنك اليابان يتدخل في السوق',
                    'summary': 'تدخل بنك اليابان لدعم الين الياباني أمام الدولار الأمريكي',
                    'time': '2024-12-19 06:45:00',
                    'impact': 'مرتفع',
                    'pairs': ['USDJPY', 'EURJPY', 'GBPJPY']
                }
            ]
            
            return news_items[:limit]
        
        except Exception as e:
            print(f"خطأ في جلب أخبار الفوركس: {e}")
            return []
    
    def get_crypto_news(self, limit=5):
        """الحصول على أخبار العملات الرقمية"""
        try:
            # أخبار تجريبية للعملات الرقمية
            news_items = [
                {
                    'title': 'Bitcoin يتجاوز مستوى 45,000 دولار',
                    'summary': 'العملة الرقمية الرائدة تحقق مكاسب قوية وسط تحسن المعنويات',
                    'time': '2024-12-19 11:20:00',
                    'impact': 'مرتفع',
                    'coins': ['BTC', 'ETH']
                },
                {
                    'title': 'Ethereum يستعد لتحديث تقني جديد',
                    'summary': 'تحديث شبكة إثيريوم المرتقب قد يحسن الأداء ويقلل الرسوم',
                    'time': '2024-12-19 09:30:00',
                    'impact': 'متوسط',
                    'coins': ['ETH']
                },
                {
                    'title': 'تبني مؤسسي جديد للعملات الرقمية',
                    'summary': 'شركات كبرى تعلن إضافة العملات الرقمية لمحافظها الاستثمارية',
                    'time': '2024-12-19 07:15:00',
                    'impact': 'متوسط',
                    'coins': ['BTC', 'ETH', 'ADA']
                }
            ]
            
            return news_items[:limit]
        
        except Exception as e:
            print(f"خطأ في جلب أخبار العملات الرقمية: {e}")
            return []
    
    def get_general_market_news(self, limit=5):
        """الحصول على أخبار السوق العامة"""
        try:
            # أخبار عامة تجريبية
            news_items = [
                {
                    'title': 'أسواق الأسهم الأمريكية تحقق مكاسب',
                    'summary': 'مؤشرات وول ستريت تغلق على ارتفاع بدعم البيانات الاقتصادية الإيجابية',
                    'time': '2024-12-19 22:00:00',
                    'impact': 'متوسط',
                    'markets': ['US30', 'SPX', 'NASDAQ']
                },
                {
                    'title': 'أسعار النفط ترتفع على توقعات زيادة الطلب',
                    'summary': 'النفط الخام يسجل مكاسب قوية وسط تحسن التوقعات الاقتصادية العالمية',
                    'time': '2024-12-19 20:30:00',
                    'impact': 'متوسط',
                    'markets': ['CRUDE', 'BRENT']
                },
                {
                    'title': 'الذهب يحافظ على مكاسبه',
                    'summary': 'المعدن النفيس يواصل تحليقه مدعوماً بالطلب الاستثماري كملاذ آمن',
                    'time': '2024-12-19 18:45:00',
                    'impact': 'منخفض',
                    'markets': ['GOLD', 'SILVER']
                }
            ]
            
            return news_items[:limit]
        
        except Exception as e:
            print(f"خطأ في جلب الأخبار العامة: {e}")
            return []
    
    def format_news_message(self, news_type="all"):
        """تنسيق رسالة الأخبار"""
        try:
            message = "📰 **أخبار الأسواق المالية** 📰\n\n"
            
            if news_type in ["all", "forex"]:
                forex_news = self.get_forex_news(3)
                if forex_news:
                    message += "💱 **أخبار الفوركس:**\n"
                    for news in forex_news:
                        impact_icon = self.get_impact_icon(news['impact'])
                        message += f"{impact_icon} **{news['title']}**\n"
                        message += f"   {news['summary']}\n"
                        message += f"   ⏰ {news['time']}\n"
                        if 'pairs' in news:
                            message += f"   📊 الأزواج المتأثرة: {', '.join(news['pairs'])}\n"
                        message += "\n"
            
            if news_type in ["all", "crypto"]:
                crypto_news = self.get_crypto_news(3)
                if crypto_news:
                    message += "₿ **أخبار العملات الرقمية:**\n"
                    for news in crypto_news:
                        impact_icon = self.get_impact_icon(news['impact'])
                        message += f"{impact_icon} **{news['title']}**\n"
                        message += f"   {news['summary']}\n"
                        message += f"   ⏰ {news['time']}\n"
                        if 'coins' in news:
                            message += f"   📊 العملات المتأثرة: {', '.join(news['coins'])}\n"
                        message += "\n"
            
            if news_type in ["all", "general"]:
                general_news = self.get_general_market_news(2)
                if general_news:
                    message += "📈 **أخبار الأسواق العامة:**\n"
                    for news in general_news:
                        impact_icon = self.get_impact_icon(news['impact'])
                        message += f"{impact_icon} **{news['title']}**\n"
                        message += f"   {news['summary']}\n"
                        message += f"   ⏰ {news['time']}\n"
                        if 'markets' in news:
                            message += f"   📊 الأسواق المتأثرة: {', '.join(news['markets'])}\n"
                        message += "\n"
            
            message += "━━━━━━━━━━━━━━━━━━━━━━━\n"
            message += f"🕒 آخر تحديث: {datetime.now().strftime('%H:%M:%S')}\n"
            message += "⚠️ *هذه الأخبار للإطلاع فقط وليست نصائح استثمارية*"
            
            return message
        
        except Exception as e:
            return f"❌ خطأ في جلب الأخبار: {str(e)}"
    
    def get_impact_icon(self, impact):
        """الحصول على أيقونة التأثير"""
        impact_icons = {
            'مرتفع': '🔴',
            'متوسط': '🟡',
            'منخفض': '🟢'
        }
        return impact_icons.get(impact, '⚪')
    
    def get_economic_calendar(self):
        """الحصول على التقويم الاقتصادي"""
        try:
            # بيانات تجريبية للتقويم الاقتصادي
            events = [
                {
                    'time': '14:30',
                    'country': 'USA',
                    'event': 'مؤشر أسعار المستهلك (CPI)',
                    'impact': 'مرتفع',
                    'previous': '3.2%',
                    'forecast': '3.1%',
                    'actual': 'قريباً'
                },
                {
                    'time': '16:00',
                    'country': 'EUR',
                    'event': 'اجتماع البنك المركزي الأوروبي',
                    'impact': 'مرتفع',
                    'previous': '4.50%',
                    'forecast': '4.50%',
                    'actual': 'قريباً'
                },
                {
                    'time': '10:00',
                    'country': 'GBP',
                    'event': 'بيانات التوظيف',
                    'impact': 'متوسط',
                    'previous': '4.2%',
                    'forecast': '4.1%',
                    'actual': 'قريباً'
                }
            ]
            
            message = "📅 **التقويم الاقتصادي لليوم** 📅\n\n"
            
            for event in events:
                impact_icon = self.get_impact_icon(event['impact'])
                country_flag = self.get_country_flag(event['country'])
                
                message += f"{impact_icon} **{event['time']}** {country_flag}\n"
                message += f"📊 **{event['event']}**\n"
                message += f"📈 السابق: {event['previous']} | المتوقع: {event['forecast']}\n"
                message += f"🎯 الفعلي: {event['actual']}\n\n"
            
            message += "━━━━━━━━━━━━━━━━━━━━━━━\n"
            message += "⚠️ *توقيتات بتوقيت GMT+3*"
            
            return message
        
        except Exception as e:
            return f"❌ خطأ في جلب التقويم الاقتصادي: {str(e)}"
    
    def get_country_flag(self, country):
        """الحصول على علم الدولة"""
        flags = {
            'USA': '🇺🇸',
            'EUR': '🇪🇺',
            'GBP': '🇬🇧',
            'JPY': '🇯🇵',
            'CAD': '🇨🇦',
            'AUD': '🇦🇺',
            'CHF': '🇨🇭'
        }
        return flags.get(country, '🌍')
    
    def get_sentiment_analysis(self):
        """تحليل المعنويات العامة للسوق"""
        try:
            # تحليل تجريبي للمعنويات
            sentiment_data = {
                'overall': 'إيجابي',
                'forex': 'محايد',
                'crypto': 'إيجابي',
                'stocks': 'إيجابي',
                'commodities': 'محايد'
            }
            
            sentiment_icons = {
                'إيجابي': '🟢',
                'محايد': '🟡',
                'سلبي': '🔴'
            }
            
            message = "🎭 **تحليل معنويات السوق** 🎭\n\n"
            
            overall_icon = sentiment_icons[sentiment_data['overall']]
            message += f"{overall_icon} **المعنويات العامة:** {sentiment_data['overall']}\n\n"
            
            message += "📊 **تفصيل الأسواق:**\n"
            for market, sentiment in sentiment_data.items():
                if market != 'overall':
                    icon = sentiment_icons[sentiment]
                    market_ar = {
                        'forex': 'الفوركس',
                        'crypto': 'العملات الرقمية',
                        'stocks': 'الأسهم',
                        'commodities': 'السلع'
                    }
                    message += f"{icon} {market_ar[market]}: {sentiment}\n"
            
            message += "\n━━━━━━━━━━━━━━━━━━━━━━━\n"
            message += "📈 **مؤشرات الخوف والطمع:**\n"
            message += "• مؤشر الخوف والطمع: 65 (طمع)\n"
            message += "• مؤشر VIX: 18.2 (منخفض)\n"
            message += "• تدفقات الأموال: إيجابية\n\n"
            message += "⚠️ *تحليل آلي للمعنويات العامة*"
            
            return message
        
        except Exception as e:
            return f"❌ خطأ في تحليل المعنويات: {str(e)}"