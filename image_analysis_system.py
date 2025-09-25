"""
نظام تحليل الرسوم البيانية والصور التقنية
يتضمن: تحليل الصور، استخراج البيانات، التوصيات
"""

import json
import asyncio
from datetime import datetime
import base64
import io
from typing import Dict, List, Optional, Tuple
import requests
from PIL import Image
import numpy as np
import cv2
from utils import send_to_telegram
import os

class ImageAnalysisSystem:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN")
        self.analysis_patterns = self.load_analysis_patterns()
        
    def load_analysis_patterns(self):
        """تحميل نماذج التحليل الفني للصور"""
        return {
            # نماذج الاتجاه
            "trend_patterns": {
                "ascending_triangle": {
                    "name": "مثلث صاعد",
                    "signal": "شراء",
                    "confidence_base": 80,
                    "description": "نموذج استمراري صاعد قوي"
                },
                "descending_triangle": {
                    "name": "مثلث هابط", 
                    "signal": "بيع",
                    "confidence_base": 80,
                    "description": "نموذج استمراري هابط قوي"
                },
                "head_and_shoulders": {
                    "name": "رأس وكتفين",
                    "signal": "بيع",
                    "confidence_base": 85,
                    "description": "نموذج انعكاسي هابط موثوق"
                },
                "inverse_head_shoulders": {
                    "name": "رأس وكتفين مقلوب",
                    "signal": "شراء", 
                    "confidence_base": 85,
                    "description": "نموذج انعكاسي صاعد موثوق"
                },
                "double_top": {
                    "name": "قمة مزدوجة",
                    "signal": "بيع",
                    "confidence_base": 75,
                    "description": "نموذج انعكاسي هابط"
                },
                "double_bottom": {
                    "name": "قاع مزدوج",
                    "signal": "شراء",
                    "confidence_base": 75,
                    "description": "نموذج انعكاسي صاعد"
                }
            },
            
            # مستويات الدعم والمقاومة
            "support_resistance": {
                "strong_support": {
                    "name": "دعم قوي",
                    "signal": "شراء",
                    "confidence_base": 70,
                    "description": "مستوى دعم قوي مختبر عدة مرات"
                },
                "strong_resistance": {
                    "name": "مقاومة قوية",
                    "signal": "بيع", 
                    "confidence_base": 70,
                    "description": "مستوى مقاومة قوي مختبر عدة مرات"
                },
                "breakout_support": {
                    "name": "كسر الدعم",
                    "signal": "بيع",
                    "confidence_base": 85,
                    "description": "كسر مستوى دعم مهم"
                },
                "breakout_resistance": {
                    "name": "كسر المقاومة", 
                    "signal": "شراء",
                    "confidence_base": 85,
                    "description": "كسر مستوى مقاومة مهم"
                }
            },
            
            # أنماط الشموع
            "candlestick_patterns": {
                "doji": {
                    "name": "دوجي",
                    "signal": "انعكاس محتمل",
                    "confidence_base": 60,
                    "description": "تردد في السوق"
                },
                "hammer": {
                    "name": "مطرقة",
                    "signal": "شراء",
                    "confidence_base": 70,
                    "description": "نموذج انعكاسي صاعد"
                },
                "shooting_star": {
                    "name": "نجمة الرماية",
                    "signal": "بيع",
                    "confidence_base": 70,
                    "description": "نموذج انعكاسي هابط"
                },
                "engulfing_bullish": {
                    "name": "ابتلاع صاعد",
                    "signal": "شراء",
                    "confidence_base": 80,
                    "description": "نموذج انعكاسي صاعد قوي"
                },
                "engulfing_bearish": {
                    "name": "ابتلاع هابط", 
                    "signal": "بيع",
                    "confidence_base": 80,
                    "description": "نموذج انعكاسي هابط قوي"
                }
            }
        }
    
    async def analyze_chart_image(self, image_data: bytes, user_id: int, chat_type: str = "private") -> str:
        """تحليل صورة الرسم البياني"""
        try:
            print(f"🖼️ بدء تحليل الصورة للمستخدم {user_id}")
            
            # تحويل البيانات إلى صورة
            image = Image.open(io.BytesIO(image_data))
            
            # تحليل الصورة باستخدام معالجة الصور
            analysis_results = await self._process_chart_image(image)
            
            if not analysis_results:
                return "❌ لم أتمكن من تحليل هذه الصورة. تأكد من أنها رسم بياني واضح للأسعار."
            
            # إنتاج التوصية النهائية
            recommendation = self._generate_image_recommendation(analysis_results)
            
            # تنسيق الرسالة النهائية
            message = await self._format_image_analysis_message(analysis_results, recommendation)
            
            print(f"✅ تم تحليل الصورة بنجاح للمستخدم {user_id}")
            return message
            
        except Exception as e:
            print(f"❌ خطأ في تحليل الصورة: {e}")
            return "❌ حدث خطأ في تحليل الصورة. يرجى المحاولة مرة أخرى بصورة أوضح."
    
    async def _process_chart_image(self, image: Image) -> Optional[Dict]:
        """معالجة وتحليل الصورة"""
        try:
            # تحويل إلى مصفوفة numpy
            img_array = np.array(image)
            
            # تحويل إلى رمادي للمعالجة
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # تحليل الخطوط والاتجاهات
            lines_analysis = self._detect_trend_lines(gray)
            
            # تحليل الأنماط
            patterns_analysis = self._detect_chart_patterns(gray)
            
            # تحليل مستويات الدعم والمقاومة
            levels_analysis = self._detect_support_resistance_levels(gray)
            
            # تحليل المؤشرات (إذا كانت موجودة)
            indicators_analysis = self._detect_indicators(gray)
            
            # دمج جميع التحليلات
            combined_analysis = {
                "trends": lines_analysis,
                "patterns": patterns_analysis,
                "levels": levels_analysis,
                "indicators": indicators_analysis,
                "image_quality": self._assess_image_quality(gray),
                "analysis_timestamp": datetime.now()
            }
            
            return combined_analysis
            
        except Exception as e:
            print(f"خطأ في معالجة الصورة: {e}")
            return None
    
    def _detect_trend_lines(self, gray_image: np.ndarray) -> Dict:
        """كشف خطوط الاتجاه"""
        try:
            # كشف الحواف
            edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
            
            # كشف الخطوط
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
            
            if lines is None:
                return {"trend": "غير محدد", "strength": 0, "lines_count": 0}
            
            # تحليل اتجاه الخطوط
            ascending_lines = 0
            descending_lines = 0
            horizontal_lines = 0
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # حساب الميل
                if x2 - x1 != 0:
                    slope = (y2 - y1) / (x2 - x1)
                    
                    if slope > 0.1:
                        ascending_lines += 1
                    elif slope < -0.1:
                        descending_lines += 1
                    else:
                        horizontal_lines += 1
            
            total_lines = len(lines)
            
            # تحديد الاتجاه الغالب
            if ascending_lines > descending_lines and ascending_lines > horizontal_lines:
                trend = "صاعد"
                strength = min(90, 50 + (ascending_lines / total_lines) * 40)
            elif descending_lines > ascending_lines and descending_lines > horizontal_lines:
                trend = "هابط"
                strength = min(90, 50 + (descending_lines / total_lines) * 40)
            else:
                trend = "عرضي"
                strength = min(70, 40 + (horizontal_lines / total_lines) * 30)
            
            return {
                "trend": trend,
                "strength": round(strength),
                "lines_count": total_lines,
                "ascending_lines": ascending_lines,
                "descending_lines": descending_lines,
                "horizontal_lines": horizontal_lines
            }
            
        except Exception as e:
            print(f"خطأ في كشف خطوط الاتجاه: {e}")
            return {"trend": "غير محدد", "strength": 0, "lines_count": 0}
    
    def _detect_chart_patterns(self, gray_image: np.ndarray) -> Dict:
        """كشف الأنماط الفنية"""
        try:
            # تطبيق تنعيم للصورة
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            
            # كشف الحواف
            edges = cv2.Canny(blurred, 30, 100)
            
            # العثور على الكنتورات
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected_patterns = []
            
            for contour in contours:
                # تبسيط الكنتور
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # تحليل شكل الكنتور
                if len(approx) == 3:
                    # مثلث محتمل
                    pattern = self._analyze_triangle_pattern(contour, approx)
                    if pattern:
                        detected_patterns.append(pattern)
                
                elif len(approx) == 4:
                    # مستطيل أو متوازي أضلاع
                    pattern = self._analyze_rectangle_pattern(contour, approx)
                    if pattern:
                        detected_patterns.append(pattern)
                
                # تحليل أنماط أكثر تعقيداً
                pattern = self._analyze_complex_pattern(contour)
                if pattern:
                    detected_patterns.append(pattern)
            
            # ترتيب الأنماط حسب القوة
            detected_patterns.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            return {
                "patterns_found": len(detected_patterns),
                "patterns": detected_patterns[:5],  # أفضل 5 أنماط
                "primary_pattern": detected_patterns[0] if detected_patterns else None
            }
            
        except Exception as e:
            print(f"خطأ في كشف الأنماط: {e}")
            return {"patterns_found": 0, "patterns": [], "primary_pattern": None}
    
    def _analyze_triangle_pattern(self, contour: np.ndarray, approx: np.ndarray) -> Optional[Dict]:
        """تحليل الأنماط المثلثية"""
        try:
            # حساب زوايا المثلث
            points = approx.reshape(-1, 2)
            
            # حساب المساحة والمحيط
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            if area < 1000 or perimeter < 100:  # تجاهل الأشكال الصغيرة
                return None
            
            # تحديد نوع المثلث
            # هذا تحليل مبسط - يمكن تطويره أكثر
            pattern_type = "مثلث متماثل"
            confidence = 60
            signal = "انتظار الكسر"
            
            return {
                "type": "triangle",
                "name": pattern_type,
                "confidence": confidence,
                "signal": signal,
                "area": area,
                "perimeter": perimeter,
                "points": points.tolist()
            }
            
        except Exception as e:
            print(f"خطأ في تحليل المثلث: {e}")
            return None
    
    def _analyze_rectangle_pattern(self, contour: np.ndarray, approx: np.ndarray) -> Optional[Dict]:
        """تحليل الأنماط المستطيلة"""
        try:
            # حساب نسبة العرض للارتفاع
            rect = cv2.boundingRect(contour)
            x, y, w, h = rect
            
            aspect_ratio = w / h if h != 0 else 0
            area = cv2.contourArea(contour)
            
            if area < 1000:  # تجاهل الأشكال الصغيرة
                return None
            
            # تحديد نوع النموذج
            if 0.8 <= aspect_ratio <= 1.2:
                pattern_type = "مربع/دمج"
                signal = "انتظار الكسر"
                confidence = 65
            elif aspect_ratio > 2:
                pattern_type = "مستطيل أفقي"
                signal = "نطاق تداول"
                confidence = 70
            else:
                pattern_type = "مستطيل عمودي"
                signal = "نطاق تداول"
                confidence = 60
            
            return {
                "type": "rectangle",
                "name": pattern_type,
                "confidence": confidence,
                "signal": signal,
                "aspect_ratio": round(aspect_ratio, 2),
                "area": area,
                "dimensions": {"width": w, "height": h}
            }
            
        except Exception as e:
            print(f"خطأ في تحليل المستطيل: {e}")
            return None
    
    def _analyze_complex_pattern(self, contour: np.ndarray) -> Optional[Dict]:
        """تحليل الأنماط المعقدة"""
        try:
            # حساب محيط ومساحة الكنتور
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            if area < 500 or perimeter < 50:
                return None
            
            # حساب نسبة الدائرية
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            
            # تحليل بناءً على الشكل
            if circularity > 0.7:
                return {
                    "type": "curve",
                    "name": "نموذج منحني",
                    "confidence": 50,
                    "signal": "مراقبة",
                    "circularity": round(circularity, 2)
                }
            
            # يمكن إضافة المزيد من التحليلات هنا
            return None
            
        except Exception as e:
            print(f"خطأ في تحليل النموذج المعقد: {e}")
            return None
    
    def _detect_support_resistance_levels(self, gray_image: np.ndarray) -> Dict:
        """كشف مستويات الدعم والمقاومة"""
        try:
            # تطبيق خوارزمية كشف الخطوط الأفقية
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            detect_horizontal = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
            
            # كشف الخطوط
            lines = cv2.HoughLinesP(detect_horizontal, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=5)
            
            levels = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    
                    # التأكد من أن الخط أفقي
                    if abs(y2 - y1) < 5:  # تسامح للخطوط شبه الأفقية
                        level_y = (y1 + y2) / 2
                        length = abs(x2 - x1)
                        
                        levels.append({
                            "y_position": level_y,
                            "length": length,
                            "strength": min(100, length / 5)  # قوة المستوى بناءً على الطول
                        })
            
            # ترتيب المستويات حسب القوة
            levels.sort(key=lambda x: x['strength'], reverse=True)
            
            # تصنيف المستويات
            strong_levels = [l for l in levels if l['strength'] > 50]
            
            return {
                "total_levels": len(levels),
                "strong_levels": len(strong_levels),
                "levels": levels[:10],  # أقوى 10 مستويات
                "analysis": "قوي" if len(strong_levels) > 3 else "متوسط" if len(strong_levels) > 1 else "ضعيف"
            }
            
        except Exception as e:
            print(f"خطأ في كشف مستويات الدعم والمقاومة: {e}")
            return {"total_levels": 0, "strong_levels": 0, "levels": [], "analysis": "غير محدد"}
    
    def _detect_indicators(self, gray_image: np.ndarray) -> Dict:
        """كشف المؤشرات في الصورة"""
        try:
            # تحليل مبسط للمؤشرات
            # يبحث عن خطوط منحنية قد تشير إلى مؤشرات
            
            # تطبيق تنعيم
            blurred = cv2.GaussianBlur(gray_image, (3, 3), 0)
            
            # كشف الحواف
            edges = cv2.Canny(blurred, 50, 150)
            
            # حساب كثافة الخطوط
            line_density = np.sum(edges > 0) / edges.size
            
            indicators_detected = []
            
            # تحليل بناءً على كثافة الخطوط
            if line_density > 0.05:
                indicators_detected.append({
                    "type": "moving_average",
                    "name": "متوسط متحرك محتمل",
                    "confidence": 60
                })
            
            if line_density > 0.08:
                indicators_detected.append({
                    "type": "oscillator",
                    "name": "مذبذب محتمل",
                    "confidence": 55
                })
            
            return {
                "indicators_count": len(indicators_detected),
                "indicators": indicators_detected,
                "line_density": round(line_density, 4)
            }
            
        except Exception as e:
            print(f"خطأ في كشف المؤشرات: {e}")
            return {"indicators_count": 0, "indicators": [], "line_density": 0}
    
    def _assess_image_quality(self, gray_image: np.ndarray) -> Dict:
        """تقييم جودة الصورة"""
        try:
            # حساب التباين
            variance = cv2.Laplacian(gray_image, cv2.CV_64F).var()
            
            # حساب السطوع المتوسط
            brightness = np.mean(gray_image)
            
            # تقييم الجودة
            if variance > 500 and 50 <= brightness <= 200:
                quality = "ممتازة"
                score = 90
            elif variance > 200 and 30 <= brightness <= 220:
                quality = "جيدة"
                score = 70
            elif variance > 100:
                quality = "متوسطة"
                score = 50
            else:
                quality = "ضعيفة"
                score = 30
            
            return {
                "quality": quality,
                "score": score,
                "variance": round(variance, 2),
                "brightness": round(brightness, 2)
            }
            
        except Exception as e:
            print(f"خطأ في تقييم جودة الصورة: {e}")
            return {"quality": "غير محدد", "score": 0, "variance": 0, "brightness": 0}
    
    def _generate_image_recommendation(self, analysis_results: Dict) -> Dict:
        """إنتاج التوصية النهائية بناءً على التحليل"""
        try:
            # تجميع النتائج
            trends = analysis_results.get('trends', {})
            patterns = analysis_results.get('patterns', {})
            levels = analysis_results.get('levels', {})
            
            # حساب النقاط الإجمالية
            total_score = 0
            signals = []
            
            # تقييم الاتجاه
            trend = trends.get('trend', 'غير محدد')
            trend_strength = trends.get('strength', 0)
            
            if trend == 'صاعد' and trend_strength > 60:
                total_score += 30
                signals.append('اتجاه صاعد قوي')
            elif trend == 'هابط' and trend_strength > 60:
                total_score += 30
                signals.append('اتجاه هابط قوي')
            elif trend == 'عرضي':
                total_score += 15
                signals.append('حركة عرضية')
            
            # تقييم الأنماط
            primary_pattern = patterns.get('primary_pattern')
            if primary_pattern:
                pattern_confidence = primary_pattern.get('confidence', 0)
                total_score += pattern_confidence * 0.4
                signals.append(f"نموذج: {primary_pattern.get('name', 'غير محدد')}")
            
            # تقييم مستويات الدعم والمقاومة
            levels_analysis = levels.get('analysis', 'ضعيف')
            if levels_analysis == 'قوي':
                total_score += 20
                signals.append('مستويات دعم/مقاومة قوية')
            elif levels_analysis == 'متوسط':
                total_score += 10
                signals.append('مستويات دعم/مقاومة متوسطة')
            
            # تحديد التوصية النهائية
            if total_score >= 80:
                recommendation = 'شراء قوي' if trend == 'صاعد' else 'بيع قوي' if trend == 'هابط' else 'مراقبة'
                confidence = min(95, total_score)
            elif total_score >= 60:
                recommendation = 'شراء' if trend == 'صاعد' else 'بيع' if trend == 'هابط' else 'انتظار'
                confidence = min(80, total_score)
            elif total_score >= 40:
                recommendation = 'انتظار'
                confidence = total_score
            else:
                recommendation = 'تحليل غير كافٍ'
                confidence = total_score
            
            return {
                'recommendation': recommendation,
                'confidence': round(confidence),
                'total_score': round(total_score),
                'signals': signals,
                'trend': trend,
                'trend_strength': trend_strength
            }
            
        except Exception as e:
            print(f"خطأ في إنتاج التوصية: {e}")
            return {
                'recommendation': 'خطأ في التحليل',
                'confidence': 0,
                'total_score': 0,
                'signals': [],
                'trend': 'غير محدد',
                'trend_strength': 0
            }
    
    async def _format_image_analysis_message(self, analysis_results: Dict, recommendation: Dict) -> str:
        """تنسيق رسالة تحليل الصورة"""
        try:
            # رموز تعبيرية للتوصيات
            rec_emoji = {
                'شراء قوي': '🟢🚀',
                'شراء': '🟢',
                'بيع قوي': '🔴🚀', 
                'بيع': '🔴',
                'انتظار': '🟡',
                'مراقبة': '👁️',
                'تحليل غير كافٍ': '❓',
                'خطأ في التحليل': '❌'
            }
            
            rec_text = recommendation['recommendation']
            emoji = rec_emoji.get(rec_text, '📊')
            
            message = f"""
🖼️ **تحليل الرسم البياني**

{emoji} **التوصية النهائية:** {rec_text}
🎯 **مستوى الثقة:** {recommendation['confidence']}%

📈 **تحليل الاتجاه:**
• الاتجاه العام: {recommendation['trend']}
• قوة الاتجاه: {recommendation['trend_strength']}%

🔍 **الأنماط المكتشفة:**"""
            
            # إضافة الأنماط
            patterns = analysis_results.get('patterns', {})
            if patterns.get('patterns_found', 0) > 0:
                for i, pattern in enumerate(patterns.get('patterns', [])[:3]):
                    pattern_emoji = "📈" if pattern.get('signal') == 'شراء' else "📉" if pattern.get('signal') == 'بيع' else "⚪"
                    message += f"\n• {pattern_emoji} {pattern.get('name', 'نموذج')} ({pattern.get('confidence', 0)}%)"
            else:
                message += "\n• لم يتم العثور على أنماط واضحة"
            
            # إضافة مستويات الدعم والمقاومة
            levels = analysis_results.get('levels', {})
            message += f"""

🛡️ **مستويات الدعم والمقاومة:**
• إجمالي المستويات: {levels.get('total_levels', 0)}
• المستويات القوية: {levels.get('strong_levels', 0)}
• التقييم: {levels.get('analysis', 'غير محدد')}"""
            
            # إضافة المؤشرات
            indicators = analysis_results.get('indicators', {})
            if indicators.get('indicators_count', 0) > 0:
                message += f"\n\n📊 **المؤشرات المحتملة:**"
                for indicator in indicators.get('indicators', []):
                    message += f"\n• {indicator.get('name', 'مؤشر')} ({indicator.get('confidence', 0)}%)"
            
            # إضافة الإشارات
            if recommendation.get('signals'):
                message += f"\n\n🔔 **الإشارات المكتشفة:**"
                for signal in recommendation['signals']:
                    message += f"\n• {signal}"
            
            # إضافة تقييم جودة الصورة
            quality = analysis_results.get('image_quality', {})
            message += f"""

📸 **جودة الصورة:** {quality.get('quality', 'غير محدد')} ({quality.get('score', 0)}%)

⚠️ **ملاحظة:** هذا التحليل مبني على معالجة الصورة وقد يحتاج إلى تأكيد من التحليل المباشر للبيانات.

🕐 **وقت التحليل:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 **تحليل الرسم البياني التلقائي**
"""
            
            return message
            
        except Exception as e:
            print(f"خطأ في تنسيق رسالة التحليل: {e}")
            return "❌ حدث خطأ في تنسيق نتائج التحليل."

# إنشاء مثيل النظام
image_analyzer = ImageAnalysisSystem()