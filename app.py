from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# تفعيل تسجيل الأخطاء لمساعدتك في اكتشاف المشاكل
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "AliExpress Telegram Bot is running!"

# ✅ استلام كود التحقق من AliExpress OAuth
@app.route('/callback', methods=['GET', 'POST'])
def callback():
    auth_code = request.args.get('auth_code') or request.form.get('auth_code')
    if not auth_code:
        logging.error("❌ No auth code received")
        return jsonify({"error": "No auth code received"}), 400
    
    logging.info(f"✅ Received auth_code: {auth_code}")
    return jsonify({"status": "success", "auth_code": auth_code})

# ✅ استقبال Webhooks من AliExpress
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        logging.error("❌ No data received in webhook")
        return jsonify({"error": "No data received"}), 400

    logging.info(f"📩 Webhook received: {data}")
    return jsonify({"status": "received", "data": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
