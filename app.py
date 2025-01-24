from flask import Flask, request
import requests
import os
import hmac
import hashlib
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# إعداد Flask
app = Flask(__name__)

# تحميل المتغيرات من البيئة
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # توكن بوت تيليغرام
ALIEXPRESS_APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")  # AppKey من AliExpress
ALIEXPRESS_APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")  # AppSecret من AliExpress
ALIEXPRESS_API_URL = os.getenv("ALIEXPRESS_API_URL")  # رابط AliExpress API الأساسي

if not TELEGRAM_TOKEN or not ALIEXPRESS_APP_KEY or not ALIEXPRESS_APP_SECRET or not ALIEXPRESS_API_URL:
    raise ValueError("❌ تأكد من تعيين جميع المتغيرات البيئية المطلوبة!")

# إنشاء تطبيق تيليغرام باستخدام `Application`
app_telegram = Application.builder().token(TELEGRAM_TOKEN).build()

# دالة بدء البوت
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("مرحباً! أرسل لي رابط منتج من AliExpress وسأرسل لك تفاصيله.")

# دالة إنشاء توقيع الأمان لـ AliExpress API
def generate_aliexpress_signature(params):
    """إنشاء توقيع HMAC للمصادقة مع AliExpress API"""
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{k}={v}" for k, v in sorted_params)
    
    signature = hmac.new(
        ALIEXPRESS_APP_SECRET.encode("utf-8"), 
        query_string.encode("utf-8"), 
        hashlib.sha256
    ).hexdigest()
    
    return signature

# دالة جلب بيانات المنتج من AliExpress API
async def fetch_aliexpress_product(url):
    params = {
        "appKey": ALIEXPRESS_APP_KEY,
        "timestamp": int(time.time() * 1000),  # تحويل الوقت إلى milliseconds
        "product_url": url
    }

    # إنشاء التوقيع الأمني
    params["signature"] = generate_aliexpress_signature(params)

    response = requests.get(ALIEXPRESS_API_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# دالة استقبال رسائل المستخدم
async def handle_message(update: Update, context: CallbackContext):
    product_url = update.message.text.strip()

    if "aliexpress.com" not in product_url:
        await update.message.reply_text("❌ يرجى إرسال رابط منتج صحيح من AliExpress.")
        return

    product_data = await fetch_aliexpress_product(product_url)

    if product_data:
        reply_text = (
            f"📌 المنتج: {product_data.get('name', 'غير متوفر')}\n"
            f"💰 السعر: {product_data.get('price', 'غير متوفر')}\n"
            f"🔻 التخفيض: {product_data.get('discount', 'غير متوفر')}\n"
            f"🔗 رابط المنتج: {product_data.get('url', product_url)}"
        )
    else:
        reply_text = "❌ لم أتمكن من العثور على تفاصيل المنتج."

    await update.message.reply_text(reply_text)

# إعداد Webhook لاستقبال التحديثات
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, app_telegram.bot)
    app_telegram.update_queue.put(update)
    return "OK", 200

# إضافة الأوامر إلى البوت
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# تشغيل السيرفر
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
