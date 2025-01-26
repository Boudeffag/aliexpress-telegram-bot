from flask import Flask, request, jsonify, redirect
import requests
import os

app = Flask(__name__)

# إعداد متغيرات البيئة (يجب ضبطها في Render)
CLIENT_ID = os.getenv("CLIENT_ID", "509112")  # استبدل بالـ APP KEY الخاص بك
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "YOUR_SECRET")  # استبدل بالـ SECRET KEY الخاص بك
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://aliexpress-telegram-bot-hgx4.onrender.com/callback")

ACCESS_TOKEN = None  # سيتم تخزين التوكن هنا

# ✅ الصفحة الرئيسية (اختياري)
@app.route('/')
def home():
    return "AliExpress Telegram Bot is Running!"

# ✅ الخطوة 1: توجيه المستخدم إلى رابط المصادقة
@app.route('/authorize')
def authorize():
    auth_url = f"https://auth.aliexpress.com/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=1234"
    return redirect(auth_url)

# ✅ الخطوة 2: استقبال `auth_code` عند إعادة التوجيه من AliExpress
@app.route('/callback')
def callback():
    global ACCESS_TOKEN
    auth_code = request.args.get('code')

    if not auth_code:
        return jsonify({"error": "No auth code received"})

    # ✅ الخطوة 3: طلب `access_token` باستخدام `auth_code`
    token_url = "https://api-sg.aliexpress.com/sync"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        ACCESS_TOKEN = token_data.get("access_token")
        return jsonify({"auth_code": auth_code, "access_token": ACCESS_TOKEN, "status": "success"})
    else:
        return jsonify({"error": "Failed to retrieve access_token", "details": response.text})

# ✅ فحص التوكن الحالي
@app.route('/token')
def get_token():
    if ACCESS_TOKEN:
        return jsonify({"access_token": ACCESS_TOKEN})
    return jsonify({"error": "No access token available"})

# ✅ تشغيل التطبيق على Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
