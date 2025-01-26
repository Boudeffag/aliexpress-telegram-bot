import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()

app = Flask(__name__)

# معلومات OAuth2 من AliExpress
CLIENT_ID = os.getenv("ALIEXPRESS_CLIENT_ID")
CLIENT_SECRET = os.getenv("ALIEXPRESS_CLIENT_SECRET")
REDIRECT_URI = os.getenv("CALLBACK_URL")  # يجب أن يكون متطابقًا مع AliExpress API Console

# استبدال هذا بقناة تيلغرام الخاصة بك
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ✅ 1️⃣ مسار الصفحة الرئيسية
@app.route('/')
def home():
    return "AliExpress Telegram Bot is running!", 200


# ✅ 2️⃣ مسار التحقق من AliExpress OAuth2
@app.route('/callback', methods=['GET', 'POST'])
def handle_callback():
    if request.method == 'GET':
        # ✅ استقبال رمز التفويض (Authorization Code)
        auth_code = request.args.get('code')
        if not auth_code:
            return jsonify({"error": "No auth code received"}), 400
        
        # ✅ استبدال رمز التفويض بـ Access Token
        token_url = "https://auth.aliexpress.com/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": auth_code
        }
        
        response = requests.post(token_url, data=data)
        token_data = response.json()
        
        if "access_token" in token_data:
            access_token = token_data["access_token"]
            return jsonify({"access_token": access_token}), 200
        else:
            return jsonify({"error": "Failed to get access token", "details": token_data}), 400

    elif request.method == 'POST':
        # ✅ استقبال بيانات Callback من AliExpress
        data = request.json
        print("🔹 Callback Data Received:", json.dumps(data, indent=4))
        return jsonify({"status": "success"}), 200


# ✅ 3️⃣ إرسال رسالة إلى تيلغرام
def send_to_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(telegram_url, json=payload)


# ✅ 4️⃣ تشغيل التطبيق
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/callback', methods=['GET'])
def callback():
    auth_code = request.args.get('auth_code')
    
    if not auth_code:
        return jsonify({"error": "No auth code received"}), 400
    
    # يمكنك هنا إرسال auth_code إلى API AliExpress لمتابعة المصادقة
    return jsonify({"status": "success", "auth_code": auth_code}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
