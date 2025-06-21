from flask import Flask, request
from telegram import Bot
import requests
from datetime import datetime

app = Flask(__name__)

# إعدادات البوت
TOKEN = '7975838878:AAE_lke0LIoSyAN6dpL742R2nM-fVBSKhho'
CHANNEL_PRIVATE = '@jsospsplemem'
CHANNEL_PUBLIC = '@trendmind_spx'
bot = Bot(token=TOKEN)

# تخزين أعلى توصية
best_contract = {
    'strike': None,
    'entry': 0,
    'max': 0,
    'img_entry': '',
    'img_max': '',
    'type': '',
    'time': '',
    'expiry': ''
}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    strike = data.get('strike')
    entry = float(data.get('entry'))
    expiry = data.get('expiry')
    call_put = data.get('type', 'CALL').upper()

    # صورة الدخول (صورة تلقائية أو ثابتة مؤقتًا)
    image_entry = f"https://yourserver.com/images/{strike}_{call_put}_entry.png"
    image_max = f"https://yourserver.com/images/{strike}_{call_put}_max.png"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # حساب الأهداف والوقف
    target_30 = round(entry * 1.3, 2)
    target_60 = round(entry * 1.6, 2)
    target_100 = round(entry * 2.0, 2)
    stop = round(entry * 0.85, 2)

    # حفظ بيانات العقد
    best_contract.update({
        'strike': strike,
        'entry': entry,
        'max': entry,
        'img_entry': image_entry,
        'img_max': image_max,
        'type': call_put,
        'expiry': expiry,
        'time': now
    })

    # إرسال التوصية للقناة الخاصة فقط
    msg = f"📢 توصية SPX ({call_put})\n" \
          f"Strike: {strike}\nExpiry: 2025-{expiry[:2]}-{expiry[2:]}\n" \
          f"دخول: {entry}$\n\n" \
          f"🎯 أهداف:\n- 30% = {target_30}\n- 60% = {target_60}\n- 100% = {target_100}\n" \
          f"⛔ وقف خسارة: {stop} (-15%)\n\n" \
          f"🕐 {now}"

    bot.send_message(chat_id=CHANNEL_PRIVATE, text=msg)
    bot.send_photo(chat_id=CHANNEL_PRIVATE, photo=image_entry)

    return 'تم إرسال توصية SPX ✅', 200

@app.route('/update_max', methods=['POST'])
def update_max():
    data = request.json
    current_price = float(data.get('price'))
    if current_price > best_contract['max']:
        best_contract['max'] = current_price
        # تحديث صورة أعلى نقطة
        bot.send_photo(chat_id=CHANNEL_PRIVATE, photo=best_contract['img_max'], caption=f"📈 تحديث: وصل {current_price}$ ✅")

    return 'تم تحديث أعلى سعر ✅', 200

@app.route('/final_result', methods=['GET'])
def send_result():
    if best_contract['strike'] is None:
        return 'لا توجد توصية اليوم', 200

    percent = round((best_contract['max'] - best_contract['entry']) / best_contract['entry'] * 100)
    msg = f"🔥 أفضل عقد اليوم\n\n" \
          f"{best_contract['type']} Strike {best_contract['strike']} – Exp: {best_contract['expiry']}\n" \
          f"دخول: {best_contract['entry']}$ – أعلى سعر: {best_contract['max']}$\n" \
          f"نسبة الربح: {percent}% 💰\n\n" \
          f"🕐 {best_contract['time']}"

    bot.send_photo(chat_id=CHANNEL_PUBLIC, photo=best_contract['img_entry'], caption="📥 صورة عند الدخول")
    bot.send_photo(chat_id=CHANNEL_PUBLIC, photo=best_contract['img_max'], caption=msg)

    return 'تم إرسال أفضل عقد اليوم ✅', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
