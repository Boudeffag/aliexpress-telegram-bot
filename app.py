from flask import Flask, request
import requests
import os
import hmac
import hashlib
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

app = Flask(__name__)

# تحميل المتغيرات من البيئة
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALIEXPRESS_APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")
ALIEXPRESS_APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")
ALIEXPRESS_API_URL = os.getenv("ALIEXPRESS_API_URL")

if not TELEGRAM_TOKEN or not ALIEXPRESS_APP_KEY or not ALIEXPRESS_APP_SECRET or not ALIEXPRESS_API_URL:
    raise ValueError("❌ تأكد من تعيين جميع المتغيرات البيئية!")

app_telegram = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("مرحباً! أرسل لي رابط منتج من AliExpress وسأرسل لك تفاصيله.")

def generate_signature(params, app_secret):
    sorted_params = sorted(params.items())
    query_string = "".join(f"{k}{v}" for k, v in sorted_params)
    signature = hmac.new(app_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature

async def fetch_aliexpress_product(url):
    params = {
        "app_key": ALIEXPRESS_APP_KEY,
        "timestamp": int(time.time() * 1000),
        "product_url": url
    }
    params["sign"] = generate_signature(params, ALIEXPRESS_APP_SECRET)
    response = requests.get(ALIEXPRESS_API_URL, params=params)
    return response.json() if response.status_code == 200 else None

async def handle_message(update: Update, context: CallbackContext):
    product_url = update.message.text.strip()
    if "aliexpress.com" not in product_url:
        await update.message.reply_text("❌ يرجى إرسال رابط منتج صحيح من AliExpress.")
        return
    product_data = await fetch_aliexpress_product(product_url)
    reply_text = f"📌 المنتج: {product_data.get('name', 'غير متوفر')}\n💰 السعر: {product_data.get('price', 'غير متوفر')}\n🔗 رابط: {product_data.get('url', product_url)}"
    await update.message.reply_text(reply_text)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, app_telegram.bot)
    app_telegram.update_queue.put(update)
    return "OK", 200

app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
