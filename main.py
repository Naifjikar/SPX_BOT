from flask import Flask, request
from telegram import Bot
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# إعدادات البوت
TOKEN = '7975838878:AAE_lke0LIoSyAN6dpL742R2nM-fVBSKhho'
CHANNEL = '@TrendMind'
bot = Bot(token=TOKEN)

# جلب صورة العقد من Webull
def get_webull_option_image(strike, expiry, call_or_put):
    try:
        url = f"https://www.webull.com/quote/option/spx{expiry}/{strike}{'C' if call_or_put.upper() == 'CALL' else 'P'}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # صورة ثابتة مؤقتًا (حتى يتم الربط بسيرفر صور تلقائي)
        return "https://yourserver.com/contract_example.png"
    except:
        return "https://yourserver.com/fallback.png"

# Webhook من TradingView
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    signal_type = data.get('type', 'CALL').upper()
    strike = data.get('strike', 5450)
    expiry = data.get('expiry', '0621')  # تاريخ الانتهاء: 21 يونيو
    entry_price = float(data.get('entry', 2.50))

    # حساب الأهداف والوقف
    target_1 = round(entry_price * 1.30, 2)
    target_2 = round(entry_price * 1.60, 2)
    target_3 = round(entry_price * 2.00, 2)
    stop_loss = round(entry_price * 0.85, 2)

    # جلب صورة Webull
    image_url = get_webull_option_image(strike, expiry, signal_type)

    # توليد التوصية
    msg = f"🔔 توصية SPX ({signal_type})\n\n" \
          f"📍 Strike: {strike}\n" \
          f"📆 Expiry: 2025-06-21\n" \
          f"🎯 دخول: {entry_price} $\n\n" \
          f"🎯 أهداف:\n" \
          f"- 30% = {target_1}\n" \
          f"- 60% = {target_2}\n" \
          f"- 100% = {target_3}\n\n" \
          f"❌ وقف الخسارة: {stop_loss} (-15%)"

    bot.send_photo(chat_id=CHANNEL, photo=image_url, caption=msg)
    return 'تم إرسال التوصية ✅', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
