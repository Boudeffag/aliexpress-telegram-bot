from flask import Flask, request, jsonify
import logging
import requests

# تهيئة Flask
app = Flask(__name__)

# تفعيل تسجيل الأخطاء لمساعدتك في اكتشاف المشاكل
logging.basicConfig(level=logging.INFO)

# بيانات التطبيق من AliExpress API Console
ALIEXPRESS_CLIENT_ID = "ضع_client_id_هنا"
ALIEXPRESS_CLIENT_SECRET = "ضع_client_secret_هنا"
ALIEXPRESS_REDIRECT_URI = "https://aliexpress-telegram-bot-hgx4.onrender.com/callback"

# دالة للحصول على رمز الوصول (Access Token) من AliExpress
def get_access_token(auth_code):
    url = "https://oauth.aliexpress.com/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": ALIEXPRESS_CLIENT_ID,
        "client_secret": ALIEXPRESS_CLIENT_SECRET,
        "code": auth_code,
        "redirect_uri": ALIEXPRESS_REDIRECT_URI
    }
    
    response = requests.post(url, data=data)
    return response.json()

# الصفحة الرئيسية للتحقق من أن البوت يعمل
@app.route('/')
def home():
    return "AliExpress Telegram Bot is running!"

# ✅ استلام كود التحقق من AliExpress OAuth
@app.route('/callback', methods=['GET', 'POST'])
def callback():
    # الحصول على كود التحقق من الطلب
    auth_code = request.args.get('auth_code') or request.form.get('auth_code')
    
    if not auth_code:
        logging.error("❌ No auth code received")
        return jsonify({"error": "No auth code received"}), 400
    
    logging.info(f"✅ Received auth_code: {auth_code}")
    
    # الحصول على رمز الوصول باستخدام كود التحقق
    token_response = get_access_token(auth_code)
    
    # إرجاع الاستجابة
    return jsonify({"status": "success", "auth_code": auth_code, "token_response": token_response})

# ✅ استقبال Webhooks من AliExpress
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        logging.error("❌ No data received in webhook")
        return jsonify({"error": "No data received"}), 400

    logging.info(f"📩 Webhook received: {data}")
    return jsonify({"status": "received", "data": data})

# تشغيل السيرفر
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
