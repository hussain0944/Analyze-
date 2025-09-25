import cv2
import numpy as np
from PIL import Image
import io

def detect_price_action(candles):
    results = []
    for c in candles[-5:]:
        x, y, w, h = c
        # المطرقة (Hammer): جسم صغير وظل سفلي طويل
        if h > 3*w and y > 20:
            results.append('Hammer')
        # الابتلاع الشرائي/البيعي: يمكن تطويره أكثر
    return results

def moving_average(prices, window=5):
    if len(prices) < window:
        return sum(prices) / len(prices)
    return np.convolve(prices, np.ones(window)/window, mode='valid')

def calc_rsi(prices, period=14):
    prices = np.array(prices)
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed > 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calc_macd(prices):
    ema_12 = moving_average(prices, window=12)
    ema_26 = moving_average(prices, window=26)
    if isinstance(ema_12, float) or isinstance(ema_26, float):
        return 0
    macd = ema_12[-1] - ema_26[-1]
    return macd

def detect_support_resistance(prices):
    support = min(prices)
    resistance = max(prices)
    return support, resistance

def detect_patterns(prices):
    # اكتشاف الرأس والكتفين بشكل مبسط
    if len(prices) >= 5:
        p = prices[-5:]
        if p[1] > p[0] and p[1] > p[2] and p[3] > p[2] and p[3] > p[4] and p[2] < p[1] and p[2] < p[3]:
            return ['Head and Shoulders']
    return []

def analyze_chart_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_np = np.array(image)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candlesticks = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 10 and h > 10:
            candlesticks.append((x, y, w, h))

    candlesticks = sorted(candlesticks, key=lambda tup: tup[0])
    last_20 = candlesticks[-20:] if len(candlesticks) >= 20 else candlesticks
    prices = [y + h // 2 for (x, y, w, h) in last_20]
    if not prices or len(prices) < 5:
        return {"error": "تعذر تحديد الشموع من الصورة. يرجى رفع صورة أوضح."}

    # المؤشرات والمدارس الفنية
    price_action_results = detect_price_action(last_20)
    ma_5 = moving_average(prices, window=5)
    ma_10 = moving_average(prices, window=10)
    rsi_val = calc_rsi(prices, period=5) if len(prices) >= 6 else 50
    macd_val = calc_macd(prices)
    support, resistance = detect_support_resistance(prices)
    patterns = detect_patterns(prices)

    # توصية التداول
    entry_zone_1 = support
    entry_zone_2 = resistance
    take_profit_1 = resistance + 15
    take_profit_2 = resistance + 30
    take_profit_3 = resistance + 50
    stop_loss = support - 20
    entry_point = (entry_zone_1 + entry_zone_2) // 2

    recommendation = {
        "entry_zone_1": entry_zone_1,
        "entry_zone_2": entry_zone_2,
        "take_profit_1": take_profit_1,
        "take_profit_2": take_profit_2,
        "take_profit_3": take_profit_3,
        "stop_loss": stop_loss,
        "entry_point": entry_point,
        "price_action": price_action_results,
        "rsi": rsi_val,
        "ma_5": ma_5,
        "ma_10": ma_10,
        "macd": macd_val,
        "support": support,
        "resistance": resistance,
        "patterns": patterns,
        "message": f"""نتيجة التحليل الفني للمدارس والمؤشرات:
- Price Action: {','.join(price_action_results) if price_action_results else 'لا يوجد نموذج واضح'}
- نماذج فنية: {','.join(patterns) if patterns else 'لا يوجد'}
- RSI: {rsi_val:.2f}
- MACD: {macd_val:.2f}
- MA5: {ma_5:.2f}
- MA10: {ma_10:.2f}
- الدعم: {support}
- المقاومة: {resistance}
توصية التداول:
منطقة الدخول الأولى: {entry_zone_1}
منطقة الدخول الثانية: {entry_zone_2}
TP1: {take_profit_1}
TP2: {take_profit_2}
TP3: {take_profit_3}
وقف الخسارة: {stop_loss}
نقطة الدخول: {entry_point}
"""
    }
    return recommendation

# مثال للاستخدام:
# with open("chart.png", "rb") as f:
#     result = analyze_chart_image(f.read())
#     print(result["message"])
