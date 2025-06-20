from flask import Flask, request
from telegram import Bot
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# إعدادات البوت
TOKEN = '7975838878:AAE_lke0LIoSyAN6dpL742R2nM-fVBSKhho'  # توكن البوت
CHANNEL = '@TrendMind'  # اسم القناة (تأكد أنه معرف القناة يبدأ بـ @)
bot = Bot(token=TOKEN)

# جلب صورة العقد من Webull (محاكاة مؤقتة)
def get_webull_option_image(strike, expiry, call_or_put):
    try:
        url = f"https://www.webull.com/quote/option/spx{expiry}/{strike}{'C' if call_or_put.upper() == 'CALL' else 'P'}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # حالياً نرجّع صورة ثابتة مؤقتاً – تقدر تستبدلها بـ real screenshot later
        return "https://yourserver.com/contract_example.png"
    except:
        return "https://yourserver.com/fallback.png"

# استقبال الإشارة من TradingView
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    signal_type = data.get('type', 'CALL')
    strike = data.get('strike', 5450)
    expiry = data.get('expiry', '0621')  # مثال: 0621 = 21 يونيو
    entry_price = float(data.get('entry', 2.50))

    # جلب صورة العقد
    image_url = get_webull_option_image(strike, expiry, signal_type)

    msg = f"Tوصية SPX ({signal_type.upper()})\\n" \
          f"Strike: {strike}\\n" \
          f"Expiry: 2025-06-21\\n" \
          f"دخول: {entry_price} $\\n\\n" \
          f"أهداف:\\n" \
          f"30% = {round(entry_price * 1.3, 2)}\\n" \
          f"60% = {round(entry_price * 1.6, 2)}\\n" \
          f"100% = {round(entry_price * 2.0, 2)}\\n\\n" \
          f"وقف خسارة: {round(entry_price * 0.85, 2)} (-15%)"

    bot.send_message(chat_id=CHANNEL, text=msg)
    bot.send_photo(chat_id=CHANNEL, photo=image_url)

    return 'تم إرسال التوصية مع صورة Webull', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
