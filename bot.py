import os, asyncio, threading
from datetime import datetime
import pytz
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Salah Bot Alive"
def run_flask(): flask_app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

TOKEN = os.getenv("TOKEN")
GROUP_ID = -1003710189896
EAT = pytz.timezone("Africa/Nairobi")
TIMES = {"Fajr":"04:50","Dhuhr":"12:25","Asr":"15:40","Maghrib":"18:15","Isha":"19:30"}
sent=set()

async def checker(app):
    while True:
        n=datetime.now(EAT).strftime("%H:%M"); d=str(datetime.now(EAT).date())
        for k,v in TIMES.items():
            if n==v and (d,k) not in sent:
                try:
                    await app.bot.send_message(GROUP_ID,f"⏰ *{k}* - {v}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"✅ I prayed {k}",callback_data=f"pray:{k}")]]),parse_mode='Markdown')
                    sent.add((d,k))
                except Exception as e: print(e)
        await asyncio.sleep(30)

async def on_button(u,c):
    q=u.callback_query; await q.answer()
    await q.edit_message_text(f"✅ {q.from_user.first_name} prayed {q.data.split(':')[1]} at {datetime.now(EAT).strftime('%H:%M')}")

async def post_init(app):
    print("Bot starting ONLINE")
    try: await app.bot.send_message(GROUP_ID,"✅ Bot restarted and ONLINE"); print("ONLINE sent")
    except Exception as e: print(f"Fail {e}")
    asyncio.create_task(checker(app))

async def main():
    app=Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CallbackQueryHandler(on_button))
    await app.run_polling()

if __name__=="__main__": asyncio.run(main())
