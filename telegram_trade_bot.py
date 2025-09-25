import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from image_trade_analyzer import analyze_chart_image

# إعداد نظام السجلات (logs)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # ضع توكن البوت هنا

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.photo:
        # جلب الصورة بأكبر جودة متاحة
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        # تحليل الصورة وإعطاء التوصية
        result = analyze_chart_image(image_bytes)
        if "error" in result:
            await update.message.reply_text(result["error"])
        else:
            await update.message.reply_text(result["message"])

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل صورة رسم بياني للشموع اليابانية ليتم تحليلها تلقائيًا وإعطاء توصية تداول مفصلة.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    # استقبال الصور في الخاص أو المجموعات
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    # استقبال أي رسالة نصية
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()