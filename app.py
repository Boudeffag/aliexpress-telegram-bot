from flask import Flask, request, jsonify, redirect
import requests
import os

app = Flask(__name__)

# متغيرات البيئة
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALIEXPRESS_APP_KEY = os.getenv("ALIEXPRESS_APP_KEY")
ALIEXPRESS_APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET")
ALIEXPRESS_REDIRECT_URI = os.getenv("ALIEXPRESS_REDIRECT_URI")

# خطوة 1: توجيه المستخدم للموافقة على التطبيق
@app.route("/authorize")
def authorize():
    auth_url = f"https://auth.aliexpress.com/oauth2/authorize?response_type=code&client_id={ALIEXPRESS_APP_KEY}&redirect_uri={ALIEXPRESS_REDIRECT_URI}&state=1234"
    return redirect(auth_url)

# خطوة 2: استقبال رمز المصادقة
@app.route("/callback")
def callback():
    auth_code = request.args.get("code")
    if not auth_code:
        return jsonify({"error": "No auth code received"})

    # خطوة 3: طلب access_token
    token_url = "https://api-sg.aliexpress.com/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": ALIEXPRESS_APP_KEY,
        "client_secret": ALIEXPRESS_APP_SECRET,
        "code": auth_code,
        "redirect_uri": ALIEXPRESS_REDIRECT_URI
    }
    
    response = requests.post(token_url, data=data)
    token_info = response.json()
    return jsonify(token_info)

# تشغيل التطبيق على Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
