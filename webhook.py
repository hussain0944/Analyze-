from flask import Flask, request
from utils import send_alert_to_enabled_groups
import os

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route('/tradingview', methods=['POST'])
def tradingview_alert():
    data = request.get_json()
    message = data.get("text", "🚨 إشعار من TradingView")
    send_alert_to_enabled_groups(message, BOT_TOKEN)
    return "Alert dispatched", 200

app.run(host='0.0.0.0', port=8080)