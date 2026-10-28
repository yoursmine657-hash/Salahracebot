import os, asyncio
from datetime import datetime
import pytz
from flask import Flask
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot alive - Salah on time"
def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

TOKEN = os.getenv("TOKEN")
GROUP_ID = -1003710189896
EAT = pytz.timezone("Africa/Nairobi")
TIMES = {"Fajr":"05:30","Dhuhr":"12:40","Asr":"16:15","Maghrib":"18:45","Isha":"20:00"}
sent_times = set()
leaderboard = {}
claimed_today = {}

async def check_times(app):
    while True:
        now = datetime.now(EAT).strftime("%H:%M")
        today = str(datetime.now(EAT).date())
        for name, t in TIMES.items():
            key = (today, name)
            if now == t and key not in sent_times:
                kb = [[InlineKeyboardButton(f"✅ I prayed {name}", callback_data=f"pray:{name}")]]
                try:
                    await app.bot.send_message(GROUP_ID, f"⏰ *{name}* - {t}\nTap to claim reward!", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
                    print(f"Sent {name}")
                except Exception as e:
                    print(f"Send error: {e}")
                sent_times.add(key)
        if now == "00:01":
            sent_times.clear()
            claimed_today.clear()
        await asyncio.sleep(30)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not q.data.startswith("pray:"): return
    prayer = q.data.split(":")[1]
    today = str(datetime.now(EAT).date())
    uid = q.from_user.id
    key = (today, prayer, uid)
    if key in claimed_today:
        await q.answer("Already claimed today!", show_alert=True)
        return
    claimed_today[key] = True
    await q.edit_message_text(f"✅ {q.from_user.first_name} prayed {prayer} at {datetime.now(EAT).strftime('%H:%M')}")

async def main():
    print(f"Starting... TOKEN present: {bool(TOKEN)}")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(button_handler))
    asyncio.create_task(check_times(app))
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
