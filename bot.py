from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
try:
    from pyrogram.types import KeyboardButtonStyle
    STYLED_BUTTONS_SUPPORTED = True
except ImportError:
    KeyboardButtonStyle = None
    STYLED_BUTTONS_SUPPORTED = False
from pyrogram.errors import SessionPasswordNeeded
import json, os, asyncio, subprocess, sys, time, threading, traceback


def styled_button(text, *, callback_data=None, url=None, style=None, **kwargs):
    """رنگ دکمه در صورت پشتیبانی؛ در غیر این صورت بدون کرش دکمه معمولی."""
    params = {"text": text, **kwargs}
    if callback_data is not None:
        params["callback_data"] = callback_data
    if url is not None:
        params["url"] = url
    if STYLED_BUTTONS_SUPPORTED and style:
        try:
            if style == "primary":
                params["style"] = KeyboardButtonStyle(bg_primary=True)
            elif style == "success":
                params["style"] = KeyboardButtonStyle(bg_success=True)
            elif style == "danger":
                params["style"] = KeyboardButtonStyle(bg_danger=True)
            return InlineKeyboardButton(**params)
        except Exception:
            params.pop("style", None)
    return InlineKeyboardButton(**params)
import html
from pyrogram import enums

user_temp_codes = {}
active_clients = {}
BOT_TOKEN = "8778279581:AAHbHoiTGq1D7lMw8IgOEqloVTyBueLQMHs"
API_ID = 35656061
API_HASH = "b37f2596516bc0439bf505d1d230395c"
ADMIN_ID = 7845464086

# تنظیمات منوی جدید
# یوزرنیم‌ها را بدون @ وارد کنید
SUPPORT_USERNAME = "Aliconfigs"
BUY_CHANNEL_USERNAME = "SelfPersiangulf"
HELPER_BOT_USERNAME = "Helpselfbotvippersian_bot"

os.makedirs("sessions", exist_ok=True)

# لیست کانال ها کم یا زیاد میتونید کنید بدون @
FORCE_CHANNELS = [
    "SH0PAL1",
 
]


COIN_RATE = 1440  # 1440 سکه = 50,000 تومان
TOMAN_PER_COIN = 50000 / 1440
card_info = {
                "card_number": "6037-1234-1234-1234",
                "card_owner": "نام صاحب کارت",
                "bank_name": "نام بانک"
            }

bot = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

class JSONDatabase:
    def __init__(self, filename="database.json"):
        self.filename = filename
        self.data = self.load_data()
    
    def load_data(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                initial_data = {
                    "users": {}, 
                    "processes": {}, 
                    "temp_data": {}, 
                    "credits": {}, 
                    "timers": {},
                    "verifications": {},
                    "payments": {},
                    "settings": {
                        "coin_rate": COIN_RATE,
                        "toman_per_coin": TOMAN_PER_COIN,
                        "admin_id": ADMIN_ID
                    }
                }
                self.save_data(initial_data)
                return initial_data
        except Exception as e:
            return {
                "users": {}, "processes": {}, "temp_data": {}, 
                "credits": {}, "timers": {}, "verifications": {}, 
                "payments": {}, "settings": {}
            }
    
    def save_data(self, data=None):
        try:
            if data: 
                self.data = data
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            return False
    
    def get(self, category, key, default=None):
        try:
            return self.data.get(category, {}).get(str(key), default)
        except:
            return default
    
    def set(self, category, key, value):
        try:
            if category not in self.data: 
                self.data[category] = {}
            self.data[category][str(key)] = value
            return self.save_data()
        except Exception as e:
            return False
    
    def delete(self, category, key):
        try:
            if category in self.data and str(key) in self.data[category]:
                del self.data[category][str(key)]
                return self.save_data()
            return False
        except Exception as e:
            return False  
    def get_all(self, category):
        try:
            return self.data.get(category, {})
        except:
            return {}
    
    def get_pending_verifications(self):
        try:
            verifications = self.data.get("verifications", {})
            return {k: v for k, v in verifications.items() if v.get('status') == 'pending'}
        except:
            return {}
    
    def get_pending_payments(self):
        try:
            payments = self.data.get("payments", {})
            return {k: v for k, v in payments.items() if v.get('status') == 'pending'}
        except:
            return {}
    
    def get_verified_users(self):
        try:
            users = self.data.get("users", {})
            return {k: v for k, v in users.items() if v.get('verified')}
        except:
            return {}
    
    def get_rejected_users(self):
        try:
            users = self.data.get("users", {})
            return {k: v for k, v in users.items() if v.get('rejected')}
        except:
            return {}

db = JSONDatabase()
user_timers = {}

class UserTimer:
    def __init__(self, user_id, callback):
        self.user_id, self.callback, self.timer, self.is_running = user_id, callback, None, False
    
    def start(self):
        if self.is_running: 
            self.stop()
        self.is_running = True
        self.timer = threading.Timer(3600, self._on_timer)
        self.timer.start()
        db.set("timers", self.user_id, {"start_time": time.time(), "is_running": True})
    
    def stop(self):
        if self.timer: 
            self.timer.cancel()
        self.is_running = False
        db.delete("timers", self.user_id)
    
    def _on_timer(self):
        self.is_running = False
        db.delete("timers", self.user_id)
        self.callback(self.user_id)
async def betting_info_handler(client, message):
    info_text = """
🎲 **سیستم شرطبندی گروهی 1v1**

**📋 قوانین شرطبندی:**
1️⃣ در گروه با نوشتن `شرطبندی 100` (یا هر مقدار دیگر) می‌توانید شرط ایجاد کنید
2️⃣ نفر دوم می‌تواند با کلیک روی دکمه «پیوستن به شرط» وارد شود
3️⃣ پس از پیوستن نفر دوم، ۵ ثانیه بعد برنده مشخص می‌شود
4️⃣ برنده تمام مبلغ شرط را دریافت می‌کند
5️⃣ اگر در ۵ دقیقه کسی شرکت نکند، شرط لغو و مبلغ بازگردانده می‌شود

**💰 مثال:**
- شما: `شرطبندی 500`
- حریف: پیوستن به شرط
- برنده: تمام 1000 سکه را می‌برد (500+500)

"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ])
    
    await message.edit_text(info_text, reply_markup=keyboard)
def create_numpad_keyboard(prefix="code"):
    buttons = []
    
    row1 = [
        InlineKeyboardButton("1️⃣", callback_data=f"{prefix}_1"),
        InlineKeyboardButton("2️⃣", callback_data=f"{prefix}_2"),
        InlineKeyboardButton("3️⃣", callback_data=f"{prefix}_3")
    ]
    
    row2 = [
        InlineKeyboardButton("4️⃣", callback_data=f"{prefix}_4"),
        InlineKeyboardButton("5️⃣", callback_data=f"{prefix}_5"),
        InlineKeyboardButton("6️⃣", callback_data=f"{prefix}_6")
    ]
    
    row3 = [
        InlineKeyboardButton("7️⃣", callback_data=f"{prefix}_7"),
        InlineKeyboardButton("8️⃣", callback_data=f"{prefix}_8"),
        InlineKeyboardButton("9️⃣", callback_data=f"{prefix}_9")
    ]
    
    row4 = [
        InlineKeyboardButton("⌨️ پاک کن", callback_data=f"{prefix}_clear"),
        InlineKeyboardButton("0️⃣", callback_data=f"{prefix}_0"),
        InlineKeyboardButton("✅ ارسال", callback_data=f"{prefix}_send")
    ]
    
    row5 = [
        InlineKeyboardButton("🔙 انصراف", callback_data=f"{prefix}_cancel")
    ]
    
    buttons.append(row1)
    buttons.append(row2)
    buttons.append(row3)
    buttons.append(row4)
    buttons.append(row5)
    
    return InlineKeyboardMarkup(buttons)

def format_code_display(code):
    if not code:
        return "⚪.⚪.⚪.⚪.⚪"
    
    digits = list(code)
    while len(digits) < 5:
        digits.append("⚪")
    
    return ".".join(digits)
async def handle_code_from_keyboard(client, code_message):
    user_id = code_message.from_user.id
    code = code_message.text 

    code = code.replace(".", "")
    
    temp_data = db.get("temp_data", user_id)
    
    if not temp_data:
        await client.send_message(user_id, "❌ اطلاعات یافت نشد\nلطفا دوباره شماره تلفن را ارسال کنید")
        return
    
    try:
        if user_id in active_clients:
            user_client = active_clients[user_id]
        else:
            session_name = f"sessions/{user_id}"
            user_client = Client(session_name, api_id=API_ID, api_hash=API_HASH)
            await user_client.connect()
            active_clients[user_id] = user_client
        
        try: 
            await user_client.sign_in(temp_data["phone"], temp_data["phone_code_hash"], code)
        except SessionPasswordNeeded:
            await client.send_message(
                user_id,
                "🔒 **رمز دو مرحله‌ای نیاز است**\n\n"
                "لطفا رمز دو مرحله‌ای خود را به صورت متن ارسال کنید:"
            )
            db.set("temp_data", user_id, {**temp_data, "needs_password": True})
            return
        
        user_info = {
            "phone": temp_data["phone"],
            "status": "active", 
            "created_at": time.time(),
            "last_active": time.time(),
            "verified": db.get("users", user_id, {}).get("verified", False)
        }
        db.set("users", user_id, user_info)
        db.delete("temp_data", user_id)
        
        if user_id in active_clients:
            try:
                await active_clients[user_id].disconnect()
                del active_clients[user_id]
            except:
                pass

        if run_selfbot(user_id, temp_data["phone"]):
            credits = db.get("credits", user_id, 0)
            await client.send_message(
                user_id,
                f"✅ **سلف بات فعال شد!**\n\n"
                f"💰 سکه های شما: {credits}\n"
                f"⏰ زمان باقی‌مانده: {credits} ساعت"
            )
        else: 
            await client.send_message(user_id, "❌ خطا در اجرای سلف بات")
        
    except Exception as e: 
        error_msg = str(e)
        if "PHONE_CODE_EXPIRED" in error_msg:
            await client.send_message(
                user_id,
                "❌ **کد منقضی شده!**\n\n"
                "لطفا دوباره شماره تلفن خود را ارسال کنید."
            )
            db.delete("temp_data", user_id)
            if user_id in active_clients:
                try:
                    await active_clients[user_id].disconnect()
                    del active_clients[user_id]
                except:
                    pass
        else:
            await client.send_message(user_id, f"❌ **خطا:** {error_msg}")

async def cancel_group_bet_if_no_joiner(client, bet_key):
    await asyncio.sleep(300) 

    bet_data = db.get("group_bets", bet_key)
    if not bet_data or bet_data.get("finished"):
        return

    participants = bet_data.get("participants", [])
    chat_id = bet_data["chat_id"]
    message_id = bet_data["message_id"]
    amount = bet_data["amount"]
    creator_id = bet_data["creator_id"]
    creator_first_name = html.escape(bet_data.get('creator_name', 'کاربر'))
    creator_mention = f'<a href="tg://user?id={creator_id}"><b>{creator_first_name}</b></a>'
    
    if len(participants) > 0:
        return
    
    if bet_data.get("refunded"):
        return
    
    creator_credits = db.get("credits", creator_id, 0)
    db.set("credits", creator_id, creator_credits + amount)

    bet_data["finished"] = True
    bet_data["is_active"] = False
    bet_data["refunded"] = True
    db.set("group_bets", bet_key, bet_data)

    text = (
        "⛔ شرط به دلیل عدم شرکت‌کننده لغو شد.\n\n"
        f"👤 سازنده: {creator_mention}\n"
        f"💰 مبلغ شرط: <code>{amount}</code> سکه\n"
        "💸 مبلغ به سازنده برگشت داده شد."
    )
    
    try:
        await client.edit_message_text(chat_id, message_id, text, reply_markup=None, parse_mode=enums.ParseMode.HTML)
    except:
        pass

    try:
        await client.send_message(
            creator_id,
            f"⛔ **شرط شما لغو شد!**\n\n"
            f"به دلیل عدم شرکت‌کننده، شرط شما لغو شد.\n"
            f"💰 مبلغ شرط: <code>{amount}</code> سکه\n"
            f"💸 مبلغ به حساب شما برگشت داده شد.\n\n"
            f"📊 موجودی جدید شما: <code>{db.get('credits', creator_id, 0)}</code> سکه"
        )
    except:
        pass

async def finish_group_bet(client, bet_key):
    await asyncio.sleep(5)

    bet_data = db.get("group_bets", bet_key)
    if not bet_data or bet_data.get("finished"):
        return

    chat_id = bet_data["chat_id"]
    message_id = bet_data["message_id"]
    amount = bet_data["amount"]
    creator_id = bet_data["creator_id"]
    creator_first_name = html.escape(bet_data.get('creator_name', 'کاربر'))
    creator_mention = f'<a href="tg://user?id={creator_id}"><b>{creator_first_name}</b></a>'
    participants = bet_data.get("participants", [])
    
    if len(participants) == 0:
        if not bet_data.get("refunded"):
            creator_credits = db.get("credits", creator_id, 0)
            db.set("credits", creator_id, creator_credits + amount)
            bet_data["refunded"] = True

        bet_data["finished"] = True
        bet_data["is_active"] = False
        db.set("group_bets", bet_key, bet_data)

        text = (
            "⛔ شرط به حد نصاب نرسید و لغو شد.\n\n"
            f"💰 مبلغ هر نفر: <code>{amount}</code> سکه\n"
            f"👤 سازنده: {creator_mention}"
        )
        try:
            await client.edit_message_text(chat_id, message_id, text, reply_markup=None, parse_mode=enums.ParseMode.HTML)
        except:
            pass
        return
    
    players = [{"id": creator_id, "name": bet_data.get('creator_name', 'کاربر')}] + participants
    player_ids = [creator_id] + [p["id"] for p in participants]
    player_mentions = [creator_mention]
    for p in participants:
        p_name = html.escape(p.get('name', 'کاربر'))
        player_mentions.append(f'<a href="tg://user?id={p["id"]}"><b>{p_name}</b></a>')
    
    pot = (1 + len(participants)) * amount 

    import random
    winner_index = random.choice(range(len(players)))
    winner_id = player_ids[winner_index]
    winner_mention = player_mentions[winner_index]
    winner_credits = db.get("credits", winner_id, 0) + pot
    db.set("credits", winner_id, winner_credits)

    bet_data["finished"] = True
    bet_data["is_active"] = False
    bet_data["winner_id"] = winner_id
    bet_data["winner_name"] = players[winner_index].get("name", "کاربر")
    bet_data["pot"] = pot
    db.set("group_bets", bet_key, bet_data)

    players_text = "\n".join([f"• {mention}" for mention in player_mentions])

    result_text = (
        "🎉 **نتیجه شرط 1v1**\n\n"
        f"💰 مبلغ هر نفر: <code>{amount}</code> سکه\n"
        f"👥 تعداد بازیکنان: <code>{len(players)}</code> نفر\n"
        f"📋 فهرست بازیکنان:\n{players_text}\n\n"
        f"🏆 **برنده:** {winner_mention}\n"
        f"💎 **جایزه:** <b>{pot}</b> سکه"
    )

    try:
        await client.edit_message_text(chat_id, message_id, result_text, reply_markup=None, parse_mode=enums.ParseMode.HTML)
    except:
        pass

    try:
        await client.send_message(
            chat_id,
            f"🏆 {winner_mention} برنده شرط <code>{amount}</code> سکه‌ای شد و <b>{pot}</b> سکه دریافت کرد!",
            parse_mode=enums.ParseMode.HTML
        )
    except:
        pass
    try:
        await client.send_message(
            winner_id,
            f"🎉 **تبریک! شما برنده شرط شدید!**\n\n"
            f"💰 مبلغ شرط: <code>{amount}</code> سکه\n"
            f"💎 جایزه دریافتی: <b>{pot}</b> سکه\n"
            f"👥 تعداد بازیکنان: {len(players)} نفر\n\n"
            f"📊 موجودی جدید شما: <code>{db.get('credits', winner_id, 0)}</code> سکه"
        )
    except:
        pass

    for player in players:
        if player["id"] != winner_id:
            try:
                await client.send_message(
                    player["id"],
                    f"😔 **متاسفانه شما در شرط باختید!**\n\n"
                    f"💰 مبلغ شرط: <code>{amount}</code> سکه\n"
                    f"👥 تعداد بازیکنان: {len(players)} نفر\n"
                    f"🏆 برنده: {winner_mention}\n\n"
                    f"📊 موجودی فعلی شما: <code>{db.get('credits', player['id'], 0)}</code> سکه"
                )
            except:
                pass
async def check_force_join(client, user_id):
    not_joined = []

    for ch in FORCE_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in ("kicked", "banned"):
                not_joined.append(ch)
        except:
            not_joined.append(ch)

    if not_joined:
        return False, not_joined
    
    return True, []

def deduct_credit_callback(user_id):
    try:
        if not db.get("processes", user_id): 
            return
        credits = db.get("credits", user_id, 0)
        if credits > 0:
            new_credits = credits - 1
            db.set("credits", user_id, new_credits)
            if new_credits <= 0:
                stop_selfbot(user_id)
                db.set("credits", user_id, 0) 
                try: 
                    bot.send_message(
                        user_id, 
                        "❌ **سکه های شما تمام شد!**\n\n"
                        "سلف بات متوقف شد.\n\n"
                        "💰 برای ادامه استفاده، از طریق منوی «افزایش موجودی» حساب خود را شارژ کنید."
                    )
                except: 
                    pass
            else:
                if user_id in user_timers: 
                    user_timers[user_id].start()
        else:
            stop_selfbot(user_id)
            db.set("credits", user_id, 0)
            try: 
                bot.send_message(
                    user_id, 
                    "❌ **سکه های شما تمام شد!**\n\n"
                    "سلف بات متوقف شد.\n\n"
                    "💰 برای ادامه استفاده، از طریق منوی «افزایش موجودی» حساب خود را شارژ کنید."
                )
            except: 
                pass
    except Exception as e:
        print(f"❌ خطا در deduct_credit_callback: {e}")

def run_selfbot(user_id, phone=None):
    try:
        stop_selfbot(user_id)

        if phone:
            cmd = [sys.executable, "self.py", str(user_id), phone, str(API_ID), API_HASH]
        else:
            cmd = [sys.executable, "self.py", str(user_id)]
        
        process = subprocess.Popen(cmd)
        pid = process.pid

        db.set("processes", user_id, pid)
        
        with open(f"process_{user_id}.pid", "w") as f:
            f.write(str(pid))
        
        print(f"✅ سلف‌بات برای کاربر {user_id} راه‌اندازی شد")
        print(f"   📱 شماره: {phone}")
        print(f"   🆔 PID: {pid}")
        print(f"   💰 سکه: {db.get('credits', user_id, 0)}")
        print("-" * 50)
        
        if user_id not in user_timers:
            user_timers[user_id] = UserTimer(user_id, deduct_credit_callback)
        user_timers[user_id].start()
        
        return True
    except Exception as e:
        print(f"❌ خطا در اجرای سلف‌بات: {e}")
        return False

def stop_selfbot(user_id):
    try:
        if user_id in user_timers:
            user_timers[user_id].stop()
            if not db.get("users", user_id): 
                del user_timers[user_id]
        
        pid = db.get("processes", user_id)
        if pid:
            try:
                import os
                import signal
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.5)
                except:
                    pass
                try:
                    os.kill(pid, signal.SIGKILL)
                except:
                    pass
                try:
                    import subprocess
                    subprocess.run(["pkill", "-f", f"self.py {user_id}"], 
                                 capture_output=True, check=False)
                    subprocess.run(["pkill", "-f", "self.py"], 
                                 capture_output=True, check=False)
                except:
                    pass
                
            except Exception as e:
                print(f"⚠️ خطا در قطع پروسس: {e}")
            
            db.delete("processes", user_id)
            user_data = db.get("users", user_id, {})
            if user_data:
                user_data["status"] = "inactive"
                db.set("users", user_id, user_data)
            
            try:
                os.remove(f"process_{user_id}.pid")
            except:
                pass
            
            print(f"✅ سلف‌بات کاربر {user_id} قطع شد (PID: {pid})")
            return True
        
        try:
            import subprocess
            subprocess.run(["pkill", "-f", f"self.py {user_id}"], check=False)
            subprocess.run(["pkill", "-f", "self.py"], check=False)
            db.delete("processes", user_id)
            print(f"✅ سلف‌بات کاربر {user_id} قطع شد (از طریق pkill)")
            return True
        except:
            pass
            
        return False
    except Exception as e:
        print(f"❌ خطا در stop_selfbot: {e}")
        return False

def stop_all_selfbots():
    try:
        for timer in list(user_timers.values()): 
            timer.stop()
        user_timers.clear()
        for pid in db.data.get("processes", {}).values():
            try: 
                import psutil
                psutil.Process(pid).terminate()
            except: 
                pass
        db.data["processes"], db.data["timers"] = {}, {}
        db.save_data()
    except: 
        pass
@bot.on_message(filters.group & filters.regex(r'^موجودی$'))
async def group_balance_simple(client, message: Message):
    user_id = message.from_user.id
    ok, not_joined = await check_force_join(client, user_id)
    if not ok:
        buttons = []
        for ch in FORCE_CHANNELS:
            buttons.append([InlineKeyboardButton(f"📢 عضویت در @{ch}", url=f"https://t.me/{ch}")])
        buttons.append([InlineKeyboardButton("🔁 بررسی مجدد", callback_data="check_join")])
        
        await message.reply_text(
            "⚠️ **برای مشاهده موجودی باید در کانال‌های زیر عضو باشید:**\n\n" +
            "\n".join([f"• @{channel}" for channel in FORCE_CHANNELS]),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    credits = db.get("credits", user_id, 0)
    toman_value = int(credits * TOMAN_PER_COIN)
    user_first_name = html.escape(message.from_user.first_name or "کاربر")
    user_mention = f'<a href="tg://user?id={user_id}"><b>{user_first_name}</b></a>'
    balance_text = f"""
💎 <b>موجودی {user_mention}</b> 💎

<b>━━━━━━━━━━━━━━━━━━</b>

💰 <b>موجودی سکه‌ها:</b>
└─ <code>{credits:,}</code> سکه

💵 <b>ارزش تومانی:</b>
└─ <code>{toman_value:,}</code> تومان

<b>━━━━━━━━━━━━━━━━━━</b>

"""
    
    await message.reply_text(
        balance_text,
        parse_mode=enums.ParseMode.HTML
    )
@bot.on_message(filters.command("set") & filters.user(ADMIN_ID))
async def set_credits(client, message: Message):
    if len(message.command) != 3:
        await message.reply_text("❌ فرمت: `/set آیدی تعداد`")
        return
    
    try:
        target_id = int(message.command[1])
        amount = int(message.command[2])
        db.set("credits", target_id, amount)
        
        await message.reply_text(f"✅ سکه کاربر {target_id} تنظیم شد به {amount}")
        
        try:
            await bot.send_message(target_id, f"🔧 موجودی سکه شما تنظیم شد\n💰 جدید: {amount} سکه")
        except: 
            pass
        
    except: 
        await message.reply_text("❌ آیدی/تعداد باید عدد باشد")
@bot.on_message(filters.group & filters.regex(r'^شرطبندی\s+(\d+)(?:\s*سکه)?$'))
async def group_bet_handler(client, message: Message):
    chat_id = message.chat.id
    creator_id = message.from_user.id

    try:
        amount = int(message.matches[0].group(1))
    except:
        return

    if amount <= 0:
        await message.reply_text("❌ مقدار شرط باید بیشتر از صفر باشد.")
        return
    creator_credits = db.get("credits", creator_id, 0)
    if creator_credits < amount:
        await message.reply_text(
            f"❌ سکه کافی برای ساخت شرط ندارید.\n"
            f"💰 موجودی شما: {creator_credits} سکه"
        )
        return
    db.set("credits", creator_id, creator_credits - amount)
    creator_first_name = html.escape(message.from_user.first_name or 'کاربر')
    creator_mention = f'<a href="tg://user?id={creator_id}"><b>{creator_first_name}</b></a>'

    bet_text = (
        "🎲 شرطبندی درحال اجرا ...\n\n"
        f"💰 مبلغ هر نفر: <code>{amount}</code> سکه\n"
        f"👤 سازنده: {creator_mention}\n\n"
        "برای شرکت در این شرط روی دکمه «پیوستن به شرط» بزنید.\n"
        "⛔ اگر تا ۵ دقیقه کسی شرکت نکند، شرط لغو و مبلغ به سازنده برمی‌گردد.\n"
        "⏳ پس از پیوستن نفر دوم، ۵ ثانیه بعد برنده مشخص می‌شود."
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ پیوستن به شرط", callback_data=f"joinbet_waiting"),
            InlineKeyboardButton("⛔ لغو شرط", callback_data=f"cancelbet_waiting")
        ]
    ])

    bet_msg = await message.reply_text(bet_text, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)

    bet_key = f"{chat_id}_{bet_msg.id}"

    bet_data = {
        "chat_id": chat_id,
        "message_id": bet_msg.id,
        "amount": amount,
        "creator_id": creator_id,
        "creator_name": message.from_user.first_name or "",
        "creator_username": message.from_user.username or "",
        "participants": [],
        "is_active": True,
        "finished": False,
        "timer_started": False,
        "created_at": time.time(),
        "refunded": False
    }

    db.set("group_bets", bet_key, bet_data)
    
    try:
        new_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ پیوستن به شرط", callback_data=f"joinbet_{chat_id}_{bet_msg.id}"),
                InlineKeyboardButton("⛔ لغو شرط", callback_data=f"cancelbet_{chat_id}_{bet_msg.id}")
            ]
        ])
        await bet_msg.edit_reply_markup(new_keyboard)
    except Exception as e:
        print(f"Error updating keyboard: {e}")
        
    asyncio.create_task(cancel_group_bet_if_no_joiner(client, bet_key))
@bot.on_message(filters.command("user") & filters.user(ADMIN_ID))
async def user_info(client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("❌ فرمت: `/user آیدی`")
        return
    
    try:
        target_id = int(message.command[1])
        user_data = db.get("users", target_id, {})
        credits = db.get("credits", target_id, 0)
        process = db.get("processes", target_id)
        timer = db.get("timers", target_id)
        
        if not user_data:
            await message.reply_text("❌ کاربر یافت نشد")
            return
        
        status = "🟢 فعال" if user_data.get('status') == 'active' else "🔴 غیرفعال"
        phone = user_data.get('phone', '❌ ثبت نشده')
        created = time.ctime(user_data.get('created_at', time.time()))
        running = "🟢 بله" if process else "🔴 خیر"
        has_timer = "🟢 فعال" if timer and timer.get('is_running') else "🔴 غیرفعال"
        verified_status = "✅ تایید شده" if user_data.get('verified') else "❌ تایید نشده"
        rejected_status = "❌ رد شده" if user_data.get('rejected') else "✅ فعال"
        
        created_time = user_data.get('created_at', time.time())
        time_diff = time.time() - created_time
        days = int(time_diff // 86400)
        hours = int((time_diff % 86400) // 3600)
        
        info_text = f"""
👤 **اطلاعات کاربر {target_id}**

📱 **شماره:** `{phone}`
📊 **وضعیت:** {status}
🔐 **احراز هویت:** {verified_status}
🚫 **وضعیت رد:** {rejected_status}
💰 **سکه ها:** `{credits}`
🔄 **سلف:** {running}
📅 **تاریخ ایجاد:** `{created}`
⏳ **عضو شده:** {days} روز و {hours} ساعت

⏱ **زمان باقی‌مانده:** `{credits}` ساعت
💸 **مصرف سکه:** 1 سکه در ساعت
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 تنظیم سکه", callback_data=f"set_{target_id}"),
             InlineKeyboardButton("🛑 توقف سلف", callback_data=f"stop_{target_id}")],
            [InlineKeyboardButton("✅ تایید احراز", callback_data=f"verify_approve_{target_id}"),
             InlineKeyboardButton("❌ رد احراز", callback_data=f"verify_reject_{target_id}")]
        ])
        
        await message.reply_text(info_text, reply_markup=keyboard)
        
    except: 
        await message.reply_text("❌ آیدی باید عدد باشد")

@bot.on_message(filters.command("admin") & filters.user(ADMIN_ID))
async def admin_panel(client, message: Message):
    users = db.data.get("users", {})
    active_count = len(db.data.get("processes", {}))
    total_credits = sum(db.data.get("credits", {}).values())
    verified_users = len(db.get_verified_users())
    pending_verifications = len(db.get_pending_verifications())
    pending_payments = len(db.get_pending_payments())
    
    today = time.time() - 86400
    new_today = sum(1 for user_data in users.values() if user_data.get('created_at', 0) > today)
    
    stats_text = f"""
🛠 **پنل مدیریت ادمین**

👥 **کل کاربران:** `{len(users)}`
🟢 **کاربران فعال:** `{active_count}`
✅ **کاربران تایید شده:** `{verified_users}`
🆕 **کاربران امروز:** `{new_today}`
💰 **مجموع سکه ها:** `{total_credits}`

📋 **درخواست‌های در انتظار:**
├─ 🔐 احراز هویت: `{pending_verifications}`
└─ 💰 پرداخت: `{pending_payments}`

**📋 دستورات سریع:**
`/set آیدی تعداد` - تنظیم سکه
`/user آیدی` - اطلاعات کاربر
`/admin` - این پنل
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 لیست کاربران", callback_data="admin_list"),
         InlineKeyboardButton("📊 آمار کامل", callback_data="admin_stats")],
        [InlineKeyboardButton("💰 برترین کاربران", callback_data="admin_top"),
         InlineKeyboardButton("🛑 توقف همه", callback_data="admin_stop_all")],
        [InlineKeyboardButton("🔐 درخواست احراز", callback_data="admin_verifications"),
         InlineKeyboardButton("💳 درخواست پرداخت", callback_data="admin_payments")]
    ])
    
    await message.reply_text(stats_text, reply_markup=keyboard)

@bot.on_callback_query(filters.regex(r'^code_'))
async def numpad_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    current_code = user_temp_codes.get(user_id, "")
    
    if data == "code_clear":
        user_temp_codes[user_id] = current_code[:-1]
        display_code = user_temp_codes[user_id]

        formatted = format_code_display(display_code)
        
        try:
            await callback_query.message.edit_text(
                f"🔢 **کد تایید را وارد کنید:**\n\n"
                f"<b><code>{formatted}</code></b>\n\n"
                f"📱 کد {len(display_code)}/5 رقم وارد شد",
                reply_markup=create_numpad_keyboard(),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            print(f"❌ خطا در ویرایش پیام: {e}")
        
        await callback_query.answer()
        
    elif data == "code_send":
        if len(current_code) == 5:
            await callback_query.answer("✅ کد ارسال شد...", show_alert=True)
            class FakeMessage:
                def __init__(self, user_id, code):
                    self.from_user = type('obj', (object,), {'id': user_id})()
                    self.text = code
                    self.chat = type('obj', (object,), {'id': user_id})()
                    self.reply_text = None
                    
                async def reply_text(self, text, *args, **kwargs):
                    await client.send_message(user_id, text, *args, **kwargs)
            
            fake_msg = FakeMessage(user_id, current_code)

            await handle_code_from_keyboard(client, fake_msg)
            
            user_temp_codes.pop(user_id, None)
        else:
            await callback_query.answer(f"❌ کد باید 5 رقم باشد (الان {len(current_code)} رقم)", show_alert=True)
            
    elif data == "code_cancel":
        user_temp_codes.pop(user_id, None)
        try:
            await callback_query.message.edit_text(
                "❌ **ورود کد لغو شد**\n\n"
                "برای شروع مجدد از /start استفاده کنید",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
                ])
            )
        except Exception as e:
            print(f"❌ خطا در ویرایش پیام: {e}")
        
        await callback_query.answer()
        
    else:
        number = data.split("_")[1]
        
        if len(current_code) < 5:
            new_code = current_code + number
            user_temp_codes[user_id] = new_code
            formatted = format_code_display(new_code)
            
            try:
                await callback_query.message.edit_text(
                    f"🔢 **کد تایید را وارد کنید:**\n\n"
                    f"<b><code>{formatted}</code></b>\n\n"
                    f"📱 کد {len(new_code)}/5 رقم وارد شد",
                    reply_markup=create_numpad_keyboard(),
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception as e:
                print(f"❌ خطا در ویرایش پیام: {e}")
            
            await callback_query.answer()
        else:
            await callback_query.answer("❌ کد کامل شده است! روی 'ارسال' کلیک کنید", show_alert=True)

async def admin_callback_handler(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    # ====== لیست کاربران ======
    if data == "admin_list":
        users = db.get_all("users")
        if not users:
            await callback_query.message.edit_text("❌ هیچ کاربری ثبت نشده است.")
            return
        
        text = "👥 **لیست کاربران:**\n\n"
        for i, (uid, info) in enumerate(list(users.items())[:20], 1):
            credits = db.get("credits", int(uid), 0)
            status = "🟢" if info.get('status') == 'active' else "🔴"
            verified = "✅" if info.get('verified') else "❌"
            text += f"{i}. {status} {verified} `{uid}` → {credits} سکه\n"
        
        if len(users) > 20:
            text += f"\n... و {len(users) - 20} کاربر دیگر"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
    
    # ====== آمار کامل ======
    elif data == "admin_stats":
        users = db.get_all("users")
        processes = db.get_all("processes")
        credits = db.get_all("credits")
        verifications = db.get_all("verifications")
        payments = db.get_all("payments")
        
        total_users = len(users)
        active_users = len(processes)
        total_credits = sum(credits.values()) if credits else 0
        pending_verif = sum(1 for v in verifications.values() if v.get('status') == 'pending')
        pending_pay = sum(1 for p in payments.values() if p.get('status') == 'pending')
        verified_users = sum(1 for u in users.values() if u.get('verified'))
        rejected_users = sum(1 for u in users.values() if u.get('rejected'))
        
        text = f"""
📊 **آمار کامل سیستم**

👥 **کاربران کل:** {total_users}
🟢 **فعال:** {active_users}
✅ **تایید شده:** {verified_users}
❌ **رد شده:** {rejected_users}

💰 **مجموع سکه‌ها:** {total_credits:,}

🔐 **درخواست احراز:** {pending_verif}
💳 **درخواست پرداخت:** {pending_pay}

📅 **تاریخ:** {time.ctime()}
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
    
    # ====== برترین کاربران ======
    elif data == "admin_top":
        credits = db.get_all("credits")
        if not credits:
            await callback_query.message.edit_text("❌ هیچ کاربری سکه ندارد.")
            return
        
        sorted_users = sorted(credits.items(), key=lambda x: x[1], reverse=True)[:10]
        text = "🏆 **برترین کاربران از نظر سکه:**\n\n"
        for i, (uid, amount) in enumerate(sorted_users, 1):
            user_data = db.get("users", int(uid), {})
            name = user_data.get('first_name', 'ناشناس')
            text += f"{i}. {name} → `{amount:,}` سکه\n"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
    
    # ====== توقف همه ======
    elif data == "admin_stop_all":
        await callback_query.message.edit_text("🛑 **در حال توقف همه سلف‌بات‌ها...**")
        stop_all_selfbots()
        await asyncio.sleep(1)
        await callback_query.message.edit_text("✅ **همه سلف‌بات‌ها متوقف شدند.**")
        await callback_query.answer()
    
    # ====== درخواست‌های احراز ======
    elif data == "admin_verifications":
        verifications = db.get_pending_verifications()
        if not verifications:
            await callback_query.message.edit_text("❌ هیچ درخواست احراز در انتظاری وجود ندارد.")
            return
        
        text = "🔐 **درخواست‌های احراز هویت:**\n\n"
        for uid, info in list(verifications.items())[:10]:
            name = info.get('first_name', 'ناشناس')
            text += f"👤 {name} → `{uid}`\n"
        
        if len(verifications) > 10:
            text += f"\n... و {len(verifications) - 10} درخواست دیگر"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
    
    # ====== درخواست‌های پرداخت ======
    elif data == "admin_payments":
        payments = db.get_pending_payments()
        if not payments:
            await callback_query.message.edit_text("❌ هیچ درخواست پرداخت در انتظاری وجود ندارد.")
            return
        
        text = "💳 **درخواست‌های پرداخت:**\n\n"
        for uid, info in list(payments.items())[:10]:
            name = info.get('first_name', 'ناشناس')
            coins = info.get('coins', 0)
            text += f"👤 {name} → `{uid}` | {coins} سکه\n"
        
        if len(payments) > 10:
            text += f"\n... و {len(payments) - 10} درخواست دیگر"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
    
    # ====== بازگشت به پنل ادمین ======
    elif data == "admin_back":
        await admin_panel(client, callback_query.message)
        await callback_query.answer()
    
    # ====== تنظیم سکه (از دکمه) ======
    elif data.startswith("set_"):
        target_id = int(data.split("_")[1])
        db.set("temp_data", f"admin_set_{user_id}", target_id)
        await callback_query.message.edit_text(
            f"💰 **تعداد سکه جدید برای کاربر {target_id} را وارد کنید:**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="admin_back")]
            ])
        )
        await callback_query.answer()
    
    # ====== توقف سلف (از دکمه) ======
    elif data.startswith("stop_"):
        target_id = int(data.split("_")[1])
        if stop_selfbot(target_id):
            await callback_query.message.edit_text(f"✅ سلف‌بات کاربر {target_id} متوقف شد.")
        else:
            await callback_query.message.edit_text(f"ℹ️ سلف‌بات کاربر {target_id} از قبل متوقف بود.")
        await callback_query.answer()
    
    # ====== تایید احراز ======
    elif data.startswith("verify_approve_"):
        target_id = int(data.split("_")[2])
        user_data = db.get("users", target_id, {})
        user_data["verified"] = True
        user_data["rejected"] = False
        db.set("users", target_id, user_data)
        db.delete("verifications", target_id)
        
        await callback_query.message.edit_text(f"✅ احراز هویت کاربر {target_id} تایید شد.")
        try:
            await bot.send_message(
                target_id,
                "✅ **احراز هویت شما تایید شد!**\n\n"
                "اکنون می‌توانید از بخش «افزایش موجودی» استفاده کنید."
            )
        except:
            pass
        await callback_query.answer()
    
    # ====== رد احراز ======
    elif data.startswith("verify_reject_"):
        target_id = int(data.split("_")[2])
        user_data = db.get("users", target_id, {})
        user_data["verified"] = False
        user_data["rejected"] = True
        db.set("users", target_id, user_data)
        db.delete("verifications", target_id)
        
        await callback_query.message.edit_text(f"❌ احراز هویت کاربر {target_id} رد شد.")
        try:
            await bot.send_message(
                target_id,
                "❌ **احراز هویت شما رد شد!**\n\n"
                "لطفا مجدداً با ارسال عکس واضح‌تر اقدام کنید."
            )
        except:
            pass
        await callback_query.answer()
    
    # ====== تایید پرداخت ======
    elif data.startswith("payment_approve_"):
        target_id = int(data.split("_")[2])
        payment_data = db.get("payments", target_id)
        if payment_data:
            coins = payment_data.get("coins", 0)
            current = db.get("credits", target_id, 0)
            db.set("credits", target_id, current + coins)
            payment_data["status"] = "approved"
            db.set("payments", target_id, payment_data)
            
            await callback_query.message.edit_text(
                f"✅ پرداخت کاربر {target_id} تایید شد.\n"
                f"💰 {coins} سکه به حسابش اضافه شد."
            )
            try:
                await bot.send_message(
                    target_id,
                    f"✅ **پرداخت شما تایید شد!**\n\n"
                    f"💰 {coins} سکه به حساب شما اضافه شد.\n"
                    f"📊 موجودی جدید: {db.get('credits', target_id, 0)} سکه"
                )
            except:
                pass
        else:
            await callback_query.message.edit_text(f"❌ اطلاعات پرداخت کاربر {target_id} یافت نشد.")
        await callback_query.answer()
    
    # ====== رد پرداخت ======
    elif data.startswith("payment_reject_"):
        target_id = int(data.split("_")[2])
        payment_data = db.get("payments", target_id)
        if payment_data:
            payment_data["status"] = "rejected"
            db.set("payments", target_id, payment_data)
            
            await callback_query.message.edit_text(f"❌ پرداخت کاربر {target_id} رد شد.")
            try:
                await bot.send_message(
                    target_id,
                    "❌ **پرداخت شما رد شد!**\n\n"
                    "لطفا مجدداً با ارسال رسید واضح‌تر اقدام کنید."
                )
            except:
                pass
        else:
            await callback_query.message.edit_text(f"❌ اطلاعات پرداخت کاربر {target_id} یافت نشد.")
        await callback_query.answer()
        
@bot.on_message(filters.command("set") & filters.user(ADMIN_ID))
async def set_credits(client, message: Message):
    if len(message.command) != 3:
        await message.reply_text("❌ فرمت: `/set آیدی تعداد`")
        return
    
    try:
        target_id = int(message.command[1])
        amount = int(message.command[2])
        db.set("credits", target_id, amount)
        
        await message.reply_text(f"✅ سکه کاربر {target_id} تنظیم شد به {amount}")
        
        try:
            await bot.send_message(target_id, f"🔧 موجودی سکه شما تنظیم شد\n💰 جدید: {amount} سکه")
        except: 
            pass
        
    except: 
        await message.reply_text("❌ آیدی/تعداد باید عدد باشد")

@bot.on_message(filters.command("user") & filters.user(ADMIN_ID))
async def user_info(client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("❌ فرمت: `/user آیدی`")
        return
    
    try:
        target_id = int(message.command[1])
        user_data = db.get("users", target_id, {})
        credits = db.get("credits", target_id, 0)
        process = db.get("processes", target_id)
        timer = db.get("timers", target_id)
        
        if not user_data:
            await message.reply_text("❌ کاربر یافت نشد")
            return
        
        status = "🟢 فعال" if user_data.get('status') == 'active' else "🔴 غیرفعال"
        phone = user_data.get('phone', '❌ ثبت نشده')
        created = time.ctime(user_data.get('created_at', time.time()))
        running = "🟢 بله" if process else "🔴 خیر"
        has_timer = "🟢 فعال" if timer and timer.get('is_running') else "🔴 غیرفعال"
        verified_status = "✅ تایید شده" if user_data.get('verified') else "❌ تایید نشده"
        rejected_status = "❌ رد شده" if user_data.get('rejected') else "✅ فعال"
        
        created_time = user_data.get('created_at', time.time())
        time_diff = time.time() - created_time
        days = int(time_diff // 86400)
        hours = int((time_diff % 86400) // 3600)
        
        info_text = f"""
👤 **اطلاعات کاربر {target_id}**

📱 **شماره:** `{phone}`
📊 **وضعیت:** {status}
🔐 **احراز هویت:** {verified_status}
🚫 **وضعیت رد:** {rejected_status}
💰 **سکه ها:** `{credits}`
🔄 **سلف:** {running}
📅 **تاریخ ایجاد:** `{created}`
⏳ **عضو شده:** {days} روز و {hours} ساعت

⏱ **زمان باقی‌مانده:** `{credits}` ساعت
💸 **مصرف سکه:** 1 سکه در ساعت
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 تنظیم سکه", callback_data=f"set_{target_id}"),
             InlineKeyboardButton("🛑 توقف سلف", callback_data=f"stop_{target_id}")],
            [InlineKeyboardButton("✅ تایید احراز", callback_data=f"verify_approve_{target_id}"),
             InlineKeyboardButton("❌ رد احراز", callback_data=f"verify_reject_{target_id}")]
        ])
        
        await message.reply_text(info_text, reply_markup=keyboard)
        
    except: 
        await message.reply_text("❌ آیدی باید عدد باشد")

@bot.on_message(filters.command("admin") & filters.user(ADMIN_ID))
async def admin_panel(client, message: Message):
    users = db.data.get("users", {})
    active_count = len(db.data.get("processes", {}))
    total_credits = sum(db.data.get("credits", {}).values())
    verified_users = len(db.get_verified_users())
    pending_verifications = len(db.get_pending_verifications())
    pending_payments = len(db.get_pending_payments())
    
    today = time.time() - 86400
    new_today = sum(1 for user_data in users.values() if user_data.get('created_at', 0) > today)
    
    stats_text = f"""
🛠 **پنل مدیریت ادمین**

👥 **کل کاربران:** `{len(users)}`
🟢 **کاربران فعال:** `{active_count}`
✅ **کاربران تایید شده:** `{verified_users}`
🆕 **کاربران امروز:** `{new_today}`
💰 **مجموع سکه ها:** `{total_credits}`

📋 **درخواست‌های در انتظار:**
├─ 🔐 احراز هویت: `{pending_verifications}`
└─ 💰 پرداخت: `{pending_payments}`

**📋 دستورات سریع:**
`/set آیدی تعداد` - تنظیم سکه
`/user آیدی` - اطلاعات کاربر
`/admin` - این پنل
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 لیست کاربران", callback_data="admin_list"),
         InlineKeyboardButton("📊 آمار کامل", callback_data="admin_stats")],
        [InlineKeyboardButton("💰 برترین کاربران", callback_data="admin_top"),
         InlineKeyboardButton("🛑 توقف همه", callback_data="admin_stop_all")],
        [InlineKeyboardButton("🔐 درخواست احراز", callback_data="admin_verifications"),
         InlineKeyboardButton("💳 درخواست پرداخت", callback_data="admin_payments")]
    ])
    
    await message.reply_text(stats_text, reply_markup=keyboard)
def create_main_menu(user_id):
    """منوی اصلی؛ رنگ‌ها فقط در صورت پشتیبانی کتابخانه اعمال می‌شوند."""
    return InlineKeyboardMarkup([
        [styled_button("🛒 خرید سلف", callback_data="increase_balance", style="success")],
        [
            styled_button("👤 حساب کاربری", callback_data="status_credits", style="primary"),
            styled_button("👥 زیرمجموعه", callback_data="referral", style="primary")
        ],
        [
            styled_button("👨‍💻 پشتیبانی", callback_data="support", style="success"),
            styled_button("⚙️ مدیریت بات", callback_data="self_management", style="primary")
        ],
        [styled_button("📣 کانال خرید", callback_data="buy_channel", style="success")],
        [styled_button("📢 راهنما", callback_data="help", style="danger")]
    ])


@bot.on_callback_query()
async def callback_handler(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data

    # ==============================
    # زیرمجموعه
    # ==============================
    if data == "referral":
        bot_info = await client.get_me()
        referral_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"

        referral_text = (
            "👥 **سیستم زیرمجموعه**\n\n"
            "با لینک اختصاصی خود دوستانتان را به ربات دعوت کنید.\n\n"
            f"🔗 **لینک دعوت شما:**\n`{referral_link}`\n\n"
            "📊 تعداد زیرمجموعه‌های شما در نسخه فعلی هنوز ذخیره نمی‌شود."
        )

        keyboard = InlineKeyboardMarkup([
            [styled_button("🔙 بازگشت", callback_data="back", style="primary")]
        ])

        await callback_query.message.edit_text(referral_text, reply_markup=keyboard)
        await callback_query.answer()
        return

    # ==============================
    # پشتیبانی
    # ==============================
    if data == "support":
        if not SUPPORT_USERNAME or SUPPORT_USERNAME == "YourSupportUsername":
            await callback_query.answer("⚠️ یوزرنیم پشتیبانی هنوز تنظیم نشده است.", show_alert=True)
            return

        support_text = (
            "👨‍💻 **پشتیبانی**\n\n"
            "برای ارتباط با پشتیبانی روی دکمه زیر کلیک کنید."
        )

        keyboard = InlineKeyboardMarkup([
            [styled_button("💬 ارتباط با پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}", style="success")],
            [styled_button("🔙 بازگشت", callback_data="back", style="primary")]
        ])

        await callback_query.message.edit_text(support_text, reply_markup=keyboard)
        await callback_query.answer()
        return

    # ==============================
    # کانال خرید
    # ==============================
    if data == "buy_channel":
        if not BUY_CHANNEL_USERNAME or BUY_CHANNEL_USERNAME == "YourChannelUsername":
            await callback_query.answer("⚠️ یوزرنیم کانال خرید هنوز تنظیم نشده است.", show_alert=True)
            return

        channel_text = (
            "📣 **کانال خرید**\n\n"
            "برای مشاهده اطلاعات خرید و اطلاعیه‌ها وارد کانال شوید."
        )

        keyboard = InlineKeyboardMarkup([
            [styled_button("📣 ورود به کانال", url=f"https://t.me/{BUY_CHANNEL_USERNAME}", style="success")],
            [styled_button("🔙 بازگشت", callback_data="back", style="primary")]
        ])

        await callback_query.message.edit_text(channel_text, reply_markup=keyboard)
        await callback_query.answer()
        return

    # ==============================
    # راهنما
    # ==============================
    if data == "help":
        help_text = (
            "📢 **راهنمای سلف بات**\n\n"
            "برای مشاهده راهنمای کامل دستورات و امکانات، وارد ربات هلپر شوید."
        )

        keyboard = InlineKeyboardMarkup([
            [styled_button("📖 ورود به ربات راهنما", url=f"https://t.me/{HELPER_BOT_USERNAME}", style="primary")],
            [styled_button("🔙 بازگشت", callback_data="back", style="primary")]
        ])

        await callback_query.message.edit_text(help_text, reply_markup=keyboard)
        await callback_query.answer()
        return
    
    if data.startswith("joinbet_"):
        if data == "joinbet_waiting":
            await callback_query.answer("⏳ لطفا چند لحظه صبر کنید...", show_alert=True)
            return
        await join_group_bet_handler(client, callback_query)
        return
    
    if data.startswith("cancelbet_"):
        if data == "cancelbet_waiting":
            await callback_query.answer("⏳ لطفا چند لحظه صبر کنید...", show_alert=True)
            return
        await cancel_group_bet_handler(client, callback_query)
        return
    if data.startswith(("admin_", "set_", "stop_", "verify_", "payment_")):
        if user_id != ADMIN_ID:
            await callback_query.answer("❌ دسترسی غیرمجاز!", show_alert=True)
            return
        await admin_callback_handler(client, callback_query)
        return
    if data == "login":
        credits = db.get("credits", user_id, 0)
        if credits <= 0:
            await callback_query.message.edit_text(
                f"❌ **سکه کافی ندارید!**\n\n💰 سکه های شما: `{credits}`\n\n💡 برای دریافت سکه با پشتیبانی تماس بگیرید.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
            )
            return
            
        await callback_query.message.edit_text(
            "📱 **لطفا شماره تلفن خود را ارسال کنید:**\n\n"
            "**فرمت:** +989123456789\n\n"
            "⚠️ شماره باید با کد کشور شروع شود",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        )
        await callback_query.answer()
    
    elif data == "login_again":
        await callback_query.message.edit_text(
            "📱 **لطفا شماره تلفن جدید خود را ارسال کنید:**\n\n"
            "**فرمت:** +989123456789\n\n"
            "⚠️ شماره باید با کد کشور شروع شود",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        )
        await callback_query.answer()
    elif data == "status_credits":
        user_data = db.get("users", user_id, {})
        credits = db.get("credits", user_id, 0)
        
        if not user_data:
            text = "❌ **شما هیچ سلف باتی ندارید**\n\nابتدا باید لاگین کنید و سلف بات را فعال کنید."
        elif user_data.get('status') == 'active':
            text = (
                f"🟢 **سلف بات فعال**\n\n"
                f"📱 **شماره:** `{user_data.get('phone', '')}`\n"
                f"💰 **سکه باقی‌مانده:** `{credits}`\n"
                f"⏰ **زمان باقی‌مانده:** `{credits}` ساعت\n\n"
                f"⏱ **مصرف:** 1 سکه در ساعت"
            )
        else:
            text = (
                f"🔴 **سلف بات غیرفعال**\n\n"
                f"📱 **شماره:** `{user_data.get('phone', '')}`\n"
                f"💰 **سکه های شما:** `{credits}`\n\n"
                f"💡 برای فعال کردن سلف بات روی 'فعالسازی' کلیک کنید."
            )
        
        await callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        )
        await callback_query.answer()
    elif data == "bet":
        await betting_info_handler(client, callback_query.message)
        await callback_query.answer()
    elif data == "self_management":
        user_data = db.get("users", user_id, {})
        credits = db.get("credits", user_id, 0)
        
        is_active = user_data.get('status') == 'active'
        process = db.get("processes", user_id)
        status_text = "🟢 **فعال**" if is_active and process else "🔴 **غیرفعال**"
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("▶️ روشن کردن سلف", callback_data="self_start"),
                InlineKeyboardButton("⏹ خاموش کردن سلف", callback_data="self_stop")
            ],
            [
                InlineKeyboardButton("🔄 آپدیت سلف", callback_data="self_update")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back")
            ]
        ])
        
        await callback_query.message.edit_text(
            f"⚙️ **مدیریت سلف بات**\n\n"
            f"📊 **وضعیت فعلی:** {status_text}\n"
            f"💰 **سکه ها:** `{credits}`\n\n"
            f"🔹 **روشن کردن:** سلف بات را فعال می‌کند\n"
            f"🔹 **خاموش کردن:** سلف بات را متوقف می‌کند\n"
            f"🔹 **آپدیت سلف:** سلف بات را مجدداً راه‌اندازی می‌کند\n\n"
            f"📱 **شماره:** `{user_data.get('phone', 'ثبت نشده')}`",
            reply_markup=keyboard
        )
        await callback_query.answer()
    elif data == "self_start":
        user_data = db.get("users", user_id, {})
        credits = db.get("credits", user_id, 0)
        
        if credits <= 0:
            await callback_query.message.edit_text(
                "❌ **سکه کافی ندارید!**\n\n"
                f"💰 سکه های شما: `{credits}`\n\n"
                "💡 لطفا ابتدا موجودی خود را افزایش دهید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💰 افزایش موجودی", callback_data="increase_balance")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="self_management")]
                ])
            )
            return
        
        if not user_data.get('phone'):
            await callback_query.message.edit_text(
                "❌ **شماره تلفن ثبت نشده است!**\n\n"
                "لطفا ابتدا از طریق دکمه «فعالسازی» شماره خود را ثبت کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("● فعالسازی ●", callback_data="login")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="self_management")]
                ])
            )
            return
        
        if db.get("processes", user_id):
            await callback_query.message.edit_text(
                "ℹ️ **سلف بات در حال حاضر فعال است!**\n\n"
                "برای راه‌اندازی مجدد از گزینه «آپدیت سلف» استفاده کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 آپدیت سلف", callback_data="self_update")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="self_management")]
                ])
            )
            return
        
        if run_selfbot(user_id, user_data.get('phone')):
            credits = db.get("credits", user_id, 0)
            await callback_query.message.edit_text(
                f"✅ **سلف بات با موفقیت روشن شد!**\n\n"
                f"💰 **سکه باقی‌مانده:** `{credits}`\n"
                f"⏰ **زمان باقی‌مانده:** `{credits}` ساعت\n\n"
                f"📱 **شماره:** `{user_data.get('phone')}`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت به مدیریت", callback_data="self_management")]
                ])
            )
        else:
            await callback_query.message.edit_text(
                "❌ **خطا در روشن کردن سلف بات!**\n\n"
                "لطفا دوباره تلاش کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 تلاش مجدد", callback_data="self_start")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="self_management")]
                ])
            )
        await callback_query.answer()
    elif data == "self_stop":
        if stop_selfbot(user_id):
            await callback_query.message.edit_text(
                "✅ **سلف بات با موفقیت خاموش شد!**\n\n"
                "برای روشن کردن مجدد از گزینه «روشن کردن سلف» استفاده کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("▶️ روشن کردن سلف", callback_data="self_start")],
                    [InlineKeyboardButton("🔙 بازگشت به مدیریت", callback_data="self_management")]
                ])
            )
        else:
            await callback_query.message.edit_text(
                "ℹ️ **سلف بات در حال حاضر خاموش است!**\n\n"
                "برای روشن کردن از گزینه «روشن کردن سلف» استفاده کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("▶️ روشن کردن سلف", callback_data="self_start")],
                    [InlineKeyboardButton("🔙 بازگشت به مدیریت", callback_data="self_management")]
                ])
            )
        await callback_query.answer()
    elif data == "self_update":
        user_data = db.get("users", user_id, {})
        credits = db.get("credits", user_id, 0)
        
        if credits <= 0:
            await callback_query.message.edit_text(
                "❌ **سکه کافی ندارید!**\n\n"
                f"💰 سکه های شما: `{credits}`\n\n"
                "💡 لطفا ابتدا موجودی خود را افزایش دهید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💰 افزایش موجودی", callback_data="increase_balance")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="self_management")]
                ])
            )
            return
        
        if not user_data.get('phone'):
            await callback_query.message.edit_text(
                "❌ **شماره تلفن ثبت نشده است!**\n\n"
                "لطفا ابتدا از طریق دکمه «فعالسازی» شماره خود را ثبت کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("● فعالسازی ●", callback_data="login")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="self_management")]
                ])
            )
            return
        
        await callback_query.message.edit_text(
            "🔄 **در حال آپدیت سلف بات...**\n\n"
            "لطفا چند لحظه صبر کنید...",
            reply_markup=None
        )
        
        stop_selfbot(user_id)
        await asyncio.sleep(1)
        
        if run_selfbot(user_id, user_data.get('phone')):
            credits = db.get("credits", user_id, 0)
            await callback_query.message.edit_text(
                f"✅ **سلف بات با موفقیت آپدیت شد!**\n\n"
                f"💰 **سکه باقی‌مانده:** `{credits}`\n"
                f"⏰ **زمان باقی‌مانده:** `{credits}` ساعت\n\n"
                f"📱 **شماره:** `{user_data.get('phone')}`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت به مدیریت", callback_data="self_management")]
                ])
            )
        else:
            await callback_query.message.edit_text(
                "❌ **خطا در آپدیت سلف بات!**\n\n"
                "لطفا دوباره تلاش کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 تلاش مجدد", callback_data="self_update")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="self_management")]
                ])
            )
        await callback_query.answer()
    
    elif data == "increase_balance":
        user_data = db.get("users", user_id, {})
        
        if user_data.get('rejected'):
            await callback_query.answer("❌ حساب شما توسط ادمین رد شده است. امکان افزایش موجودی ندارید.", show_alert=True)
            return
        
        if not user_data.get('verified'):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("● احراز هویت ●", callback_data="start_verification")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
            ])
            
            await callback_query.message.edit_text(
                "🔒 **برای افزایش موجودی نیاز به احراز هویت دارید**\n\n"
                "📋 **مراحل احراز هویت:**\n"
                "1️⃣ کلیک روی دکمه 'احراز هویت'\n"
                "2️⃣ ارسال عکس از کارت بانکی\n"
                "3️⃣ تایید توسط ادمین\n"
                "4️⃣ افزایش موجودی\n\n"
                "⚠️ **توجه:** اطلاعات حساس (CVV2، تاریخ انقضا) در عکس پوشیده شود",
                reply_markup=keyboard
            )
            return
        else:
            await callback_query.message.edit_text(
                "💰 **افزایش موجودی**\n\n"
                f"💎 **نرخ تبدیل:** هر {COIN_RATE} سکه = 50,000 تومان\n"
                f"💵 **قیمت هر سکه:** {TOMAN_PER_COIN:.0f} تومان\n\n"
                "🔢 **تعداد سکه مورد نظر خود را وارد کنید:**\n"
                "مثال: 1440\n\n"
                "💡 **توجه:** فقط عدد وارد کنید (بدون نقطه یا کاما)",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
            )
            
            db.delete("temp_data", f"waiting_coins_{user_id}")
            db.set("temp_data", f"waiting_coins_{user_id}", True)
            await callback_query.answer("✅ لطفا تعداد سکه مورد نظر را وارد کنید")

    elif data == "start_verification":
        user_data = db.get("users", user_id, {})
        if user_data.get('rejected'):
            await callback_query.answer("❌ حساب شما توسط ادمین رد شده است.", show_alert=True)
            return
        
        await callback_query.message.edit_text(
            "📸 **لطفا عکس کارت بانکی خود را ارسال کنید**\n\n"
            "⚠️ **قبل از ارسال مطمئن شوید:**\n"
            "• نام صاحب کارت مشخص باشد\n"
            "• شماره کارت واضح باشد\n"
            "• CVV2 ❌ پوشیده شود\n"
            "• تاریخ انقضا ❌ پوشیده شود\n\n"
            "📎 یک عکس با کیفیت مناسب ارسال کنید",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="increase_balance")]])
        )
        db.set("temp_data", f"waiting_card_photo_{user_id}", True)
   
    elif data == "back":
        if user_id != ADMIN_ID:
            credits = db.get("credits", user_id, 0)
            user_data = db.get("users", user_id, {})
            
            status_text = "🔴 سلف غیرفعال"
            phone_text = ""
            verified_status = "❌ احراز نشده"
            
            if user_data and user_data.get('status') == 'active':
                status_text = f"🟢 سلف فعال"
                phone_text = f"\n📱 شماره: {user_data.get('phone', '')}"
            
            if user_data.get('verified'):
                verified_status = "✅ احراز شده"
            
            keyboard = create_main_menu(user_id)
            
            text = f"🤖 **ربات مدیریت سلف بات**\n\n**وضعیت:** {status_text}{phone_text}\n**🔐 احراز:** {verified_status}\n**💰 سکه ها:** `{credits}` سکه\n**⏰ مصرف:** 1 سکه در ساعت"
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        else:
            await admin_panel(client, callback_query.message)
        await callback_query.answer()
    
    elif data == "check_join":
        ok, not_joined = await check_force_join(client, user_id)
        if ok:
            await callback_query.message.edit_text("✅ عضویت شما در همه کانال‌ها تایید شد!\nدوباره /start بزنید.")
            return
        buttons = []
        for ch in not_joined:
            buttons.append([InlineKeyboardButton(f"📢 عضویت در @{ch}", url=f"https://t.me/{ch}")])
        buttons.append([InlineKeyboardButton("🔄 بررسی مجدد", callback_data="check_join")])
        await callback_query.message.edit_text(
            "❌ هنوز عضو همه کانال‌ها نیستید!",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await callback_query.answer()
@bot.on_message(filters.user(ADMIN_ID) & filters.regex(r'^\d+$'))
async def handle_admin_input(client, message: Message):
    user_id = message.from_user.id
    amount = int(message.text)
    
    set_target = db.get("temp_data", f"admin_set_{user_id}")
    if set_target:
        db.delete("temp_data", f"admin_set_{user_id}")
        db.set("credits", set_target, amount)
        
        await message.reply_text(f"✅ سکه کاربر {set_target} تنظیم شد به {amount}")
        
        try:
            await bot.send_message(set_target, f"🔧 موجودی سکه شما تنظیم شد\n💰 جدید: {amount} سکه")
        except: pass
@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    print(f"🔥 START RECEIVED from user_id={message.from_user.id}", flush=True)
    ok, not_joined = await check_force_join(client, message.from_user.id)
    if not ok:
        buttons = []
        for ch in not_joined:
            buttons.append([InlineKeyboardButton(f"📢 عضویت در @{ch}", url=f"https://t.me/{ch}")])
        buttons.append([InlineKeyboardButton("● بررسی عضویت ●", callback_data="check_join")])
        await message.reply_text(
            "❌ برای استفاده از ربات باید در تمام کانال‌های زیر عضو شوید:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    user_id = message.from_user.id
    
    existing_user = db.get("users", user_id)
    is_new_user = False
    
    if not existing_user:
        user_info = {
            "status": "inactive",
            "created_at": time.time(),
            "first_name": message.from_user.first_name or "",
            "username": message.from_user.username or "",
            "verified": False,
            "rejected": False
        }
        db.set("users", user_id, user_info)
        is_new_user = True
    else:
        user_info = existing_user
        user_info["first_name"] = message.from_user.first_name or ""
        user_info["username"] = message.from_user.username or ""
        db.set("users", user_id, user_info)
    
    credits = db.get("credits", user_id, 0)
    if is_new_user and credits == 0:
        db.set("credits", user_id, 5)
        credits = 5
    
    if user_id == ADMIN_ID:
        await admin_panel(client, message)
        return
    
    user_data = db.get("users", user_id, {})
    status = "🟢 فعال" if user_data.get('status') == 'active' else "🔴 غیرفعال"
    phone = user_data.get('phone', '')
    verified_status = "✅ احراز شده" if user_data.get('verified') else "❌ احراز نشده"
    
    keyboard = create_main_menu(user_id)
    
    welcome_text = f"""**🌺 به ربات سلف ساز خوش آمدید!**

🤖 **ربات مدیریت سلف بات حرفه‌ای**
├─ ساخت سلف شخصی
📊 **وضعیت حساب شما:**
├─ 👤 کاربر: {message.from_user.first_name or "ناشناس"}
├─ 🔋 وضعیت: {status}
├─ 🔐 وضعیت احراز: {verified_status}
├─ 💰 سکه: {credits} عدد
└─ ⏰ مصرف 1 سکه در ساعت

{f"📱 **شماره:** `{phone}`" if phone else "⚠️ **شماره ثبت نشده**"}

💡 برای شروع روی «فعالسازی» کلیک کنید."""

    await message.reply_text(welcome_text, reply_markup=keyboard)
@bot.on_callback_query(filters.regex(r'^joinbet_(-?\d+)_(-?\d+)$'))
async def join_group_bet_handler(client, callback_query):
    user_id = callback_query.from_user.id
    user_first_name = html.escape(callback_query.from_user.first_name or 'کاربر')
    user_mention = f'<a href="tg://user?id={user_id}"><b>{user_first_name}</b></a>'
    data = callback_query.data
    _, chat_id_str, msg_id_str = data.split('_')

    chat_id = int(chat_id_str)
    message_id = int(msg_id_str)
    bet_key = f"{chat_id}_{message_id}"

    bet_data = db.get("group_bets", bet_key)
    if not bet_data or not bet_data.get("is_active"):
        await callback_query.answer("❌ این شرط دیگر فعال نیست.", show_alert=True)
        return

    if bet_data.get("finished"):
        await callback_query.answer("❌ این شرط قبلا به پایان رسیده است.", show_alert=True)
        return
    if callback_query.message.chat.id != chat_id:
        await callback_query.answer("❌ این دکمه مخصوص گروه اصلی شرط است.", show_alert=True)
        return

    creator_id = bet_data["creator_id"]
    creator_first_name = html.escape(bet_data.get('creator_name', 'کاربر'))
    creator_mention = f'<a href="tg://user?id={creator_id}"><b>{creator_first_name}</b></a>'
    participants = bet_data.get("participants", [])
    if user_id == creator_id:
        await callback_query.answer("ℹ️ شما سازنده این شرط هستید و قبلاً داخل شرط هستید.", show_alert=True)
        return
    if len(participants) >= 1:
        await callback_query.answer("⛔ ظرفیت این شرط تکمیل شده است.", show_alert=True)
        return

    if user_id in [p["id"] for p in participants]:
        await callback_query.answer("ℹ️ شما قبلا در این شرط شرکت کرده‌اید.", show_alert=True)
        return

    amount = bet_data["amount"]
    current_credits = db.get("credits", user_id, 0)

    if current_credits < amount:
        await callback_query.answer(
            f"❌ سکه کافی ندارید!\n💰 موجودی شما: {current_credits} سکه",
            show_alert=True
        )
        return
    db.set("credits", user_id, current_credits - amount)

    participants.append({
        "id": user_id,
        "name": callback_query.from_user.first_name or "",
        "username": callback_query.from_user.username or ""
    })
    bet_data["participants"] = participants
    if not bet_data.get("timer_started"):
        bet_data["timer_started"] = True
        db.set("group_bets", bet_key, bet_data)
        asyncio.create_task(finish_group_bet(client, bet_key))
    else:
        db.set("group_bets", bet_key, bet_data)
    try:
        participants_mentions = []
        for p in participants:
            p_name = html.escape(p.get('name', 'کاربر'))
            participants_mentions.append(f'<a href="tg://user?id={p["id"]}"><b>{p_name}</b></a>')
        
        all_players_mentions = [creator_mention] + participants_mentions
        
        new_text = (
            "🎲 شرط 1v1 در حال اجرا\n\n"
            f"💰 مبلغ هر نفر: <code>{amount}</code> سکه\n"
            f"👥 شرکت‌کننده‌ها: <code>{len(participants) + 1}/2</code> نفر\n"
            f"👤 بازیکنان: {', '.join(all_players_mentions)}\n\n"
            "⏳ ۵ ثانیه بعد بین این دو نفر قرعه‌کشی می‌شود."
        )
        new_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ پیوستن به شرط", callback_data=f"joinbet_{chat_id}_{message_id}"),
                InlineKeyboardButton("⛔ لغو شرط", callback_data=f"cancelbet_{chat_id}_{message_id}")
            ]
        ])
        await callback_query.message.edit_text(new_text, reply_markup=new_keyboard, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        print(f"Error updating bet message: {e}")

    await callback_query.answer("✅ در شرط شرکت کردید و سکه از حساب شما کسر شد.")
@bot.on_callback_query(filters.regex(r'^cancelbet_(-?\d+)_(-?\d+)$'))
async def cancel_group_bet_handler(client, callback_query):
    user_id = callback_query.from_user.id
    user_first_name = html.escape(callback_query.from_user.first_name or 'کاربر')
    user_mention = f'<a href="tg://user?id={user_id}"><b>{user_first_name}</b></a>'
    data = callback_query.data
    _, chat_id_str, msg_id_str = data.split('_')

    chat_id = int(chat_id_str)
    message_id = int(msg_id_str)
    bet_key = f"{chat_id}_{message_id}"

    bet_data = db.get("group_bets", bet_key)
    if not bet_data:
        await callback_query.answer("❌ این شرط یافت نشد یا قبلا حذف شده.", show_alert=True)
        return

    creator_id = bet_data["creator_id"]
    creator_first_name = html.escape(bet_data.get('creator_name', 'کاربر'))
    creator_mention = f'<a href="tg://user?id={creator_id}"><b>{creator_first_name}</b></a>'

    if user_id != creator_id:
        await callback_query.answer("❌ فقط سازنده شرط می‌تواند آن را لغو کند.", show_alert=True)
        return

    if bet_data.get("finished"):
        await callback_query.answer("❌ این شرط قبلا تمام شده است.", show_alert=True)
        return

    amount = bet_data["amount"]
    participants = bet_data.get("participants", [])
    if not bet_data.get("refunded"):
        creator_credits = db.get("credits", creator_id, 0)
        db.set("credits", creator_id, creator_credits + amount)
        bet_data["refunded"] = True
    for participant in participants:
        uid = participant["id"]
        credits = db.get("credits", uid, 0)
        db.set("credits", uid, credits + amount)

    bet_data["finished"] = True
    bet_data["is_active"] = False
    db.set("group_bets", bet_key, bet_data)

    participants_mentions = []
    for p in participants:
        p_name = html.escape(p.get('name', 'کاربر'))
        participants_mentions.append(f'<a href="tg://user?id={p["id"]}"><b>{p_name}</b></a>')
    
    all_users_text = creator_mention
    if participants_mentions:
        all_users_text += f", {', '.join(participants_mentions)}"

    text = (
        "⛔ این شرط توسط سازنده لغو شد.\n\n"
        f"👤 سازنده: {creator_mention}\n"
        f"👥 سایر بازیکنان: {', '.join(participants_mentions) if participants_mentions else 'ندارد'}\n"
        f"💰 مبلغ شرط: <code>{amount}</code> سکه\n"
        "💸 مبلغ به تمام افراد (سازنده و شرکت‌کننده‌ها) برگشت داده شد."
    )

    try:
        await callback_query.message.edit_text(text, reply_markup=None, parse_mode=enums.ParseMode.HTML)
    except:
        pass

    await callback_query.answer("✅ شرط با موفقیت لغو شد.", show_alert=True)
@bot.on_callback_query(filters.regex("check_join"))
async def check_join(client, callback_query):
    user_id = callback_query.from_user.id
    ok, not_joined = await check_force_join(client, user_id)

    if ok:
        await callback_query.message.edit_text("✅ عضویت شما در همه کانال‌ها تایید شد!\nدوباره /start بزنید.")
        return

    buttons = []
    for ch in not_joined:
        buttons.append([InlineKeyboardButton(f"📢 عضویت در @{ch}", url=f"https://t.me/{ch}")])

    buttons.append([InlineKeyboardButton("🔄 بررسی مجدد", callback_data="check_join")])

    await callback_query.message.edit_text(
        "❌ هنوز عضو همه کانال‌ها نیستید!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
@bot.on_message(filters.private & filters.regex(r'^\+\d{10,15}$'))
async def handle_phone(client, message: Message):
    user_id, phone = message.from_user.id, message.text
    
    if user_id in active_clients:
        try:
            await active_clients[user_id].disconnect()
            del active_clients[user_id]
        except:
            pass
    
    credits = db.get("credits", user_id, 0)
    if credits <= 0:
        await message.reply_text(f"❌ سکه کافی ندارید!\nسکه های شما: {credits}")
        return
    
    try:
        session_name = f"sessions/{user_id}"
        temp_client = Client(session_name, api_id=API_ID, api_hash=API_HASH)
        await temp_client.connect()
        
        active_clients[user_id] = temp_client
        sent_code = await temp_client.send_code(phone)
        user_data = db.get("users", user_id, {})
        user_data["phone"] = phone
        db.set("users", user_id, user_data)
        await message.reply_text(
            "✅ **کد تأیید ارسال شد**\n\n"
            "🔢 **کد ۵ رقمی را با دکمه‌های زیر وارد کنید:**\n\n"
            f"<b><code>{format_code_display('')}</code></b>\n\n"
            "📱 کد ارسال شده به شماره شما",
            reply_markup=create_numpad_keyboard(),
            parse_mode=enums.ParseMode.HTML
        )
        
        db.set("temp_data", user_id, {
            "phone": phone, 
            "phone_code_hash": sent_code.phone_code_hash,
            "client_active": True
        })
        
    except Exception as e:
        await message.reply_text(f"❌ **خطا:** {str(e)}")
        if user_id in active_clients:
            try:
                await active_clients[user_id].disconnect()
                del active_clients[user_id]
            except:
                pass
@bot.on_message(filters.private & filters.text)
async def handle_all_messages(client, message: Message):
    user_id = message.from_user.id
    text = message.text
    if db.get("temp_data", f"waiting_coins_{user_id}"):
        try:
            coins_amount = int(text)
            if coins_amount <= 0:
                await message.reply_text("❌ تعداد سکه باید بیشتر از صفر باشد")
                return
            
            toman_amount = coins_amount * TOMAN_PER_COIN
            
            payment_data = {
                "user_id": user_id,
                "coins": coins_amount,
                "toman": toman_amount,
                "timestamp": time.time(),
                "status": "pending",
                "first_name": message.from_user.first_name or "",
                "username": message.from_user.username or ""
            }
            
            db.set("payments", user_id, payment_data)
            db.delete("temp_data", f"waiting_coins_{user_id}")
            
            payment_text = (
                f"💳 **برای پرداخت لطفا مبلغ {toman_amount:,.0f} تومان به حساب زیر واریز کنید:**\n\n"
                f"🏦 **بانک:** {card_info['bank_name']}\n"
                f"🔢 **شماره کارت:** `{card_info['card_number']}`\n"
                f"👤 **به نام:** {card_info['card_owner']}\n\n"
                f"💎 **تعداد سکه دریافتی:** {coins_amount} سکه\n\n"
                f"📸 **پس از واریز، رسید یا عکس پرداخت را ارسال کنید**\n"
                f"⏰ پرداخت شما حداکثر تا 24 ساعت بررسی خواهد شد"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="increase_balance")]
            ])
            
            await message.reply_text(payment_text, reply_markup=keyboard)
            db.set("temp_data", f"waiting_payment_proof_{user_id}", True)
            
        except ValueError:
            await message.reply_text("❌ لطفا یک عدد معتبر وارد کنید")
        return

    temp_data = db.get("temp_data", user_id)
    if temp_data and temp_data.get("needs_password"):
        try:
            if user_id not in active_clients:
                await message.reply_text("❌ کلاینت فعال نیست. لطفا دوباره شماره را ارسال کنید.")
                return
            
            user_client = active_clients[user_id]
            await user_client.check_password(text)
            
            user_info = {
                "phone": temp_data["phone"],
                "status": "active",
                "created_at": time.time(),
                "last_active": time.time(),
                "verified": db.get("users", user_id, {}).get("verified", False)
            }
            db.set("users", user_id, user_info)
            db.delete("temp_data", user_id)
            
            if user_id in active_clients:
                try:
                    await active_clients[user_id].disconnect()
                    del active_clients[user_id]
                except:
                    pass
            
            if run_selfbot(user_id, temp_data["phone"]):
                credits = db.get("credits", user_id, 0)
                await message.reply_text(
                    f"✅ **سلف بات فعال شد!**\n\n"
                    f"💰 سکه های شما: {credits}\n"
                    f"⏰ زمان باقی‌مانده: {credits} ساعت"
                )
            else: 
                await message.reply_text("❌ خطا در اجرای سلف")
            
        except Exception as e: 
            await message.reply_text(f"❌ رمز اشتباه: {str(e)}")
        return

    if user_id == ADMIN_ID:
        set_target = db.get("temp_data", f"admin_set_{user_id}")
        if set_target and text.isdigit():
            amount = int(text)
            db.delete("temp_data", f"admin_set_{user_id}")
            db.set("credits", set_target, amount)
            
            await message.reply_text(f"✅ سکه کاربر {set_target} تنظیم شد به {amount}")
            
            try:
                await bot.send_message(set_target, f"🔧 موجودی سکه شما تنظیم شد\n💰 جدید: {amount} سکه")
            except: 
                pass
            return
    
    pass
@bot.on_message(filters.photo & filters.private)
async def handle_card_photo(client, message: Message):
    user_id = message.from_user.id
    
    if db.get("temp_data", f"waiting_card_photo_{user_id}"):
        verification_data = {
            "user_id": user_id,
            "first_name": message.from_user.first_name or "",
            "username": message.from_user.username or "",
            "photo_id": message.photo.file_id,
            "timestamp": time.time(),
            "status": "pending"
        }
        
        db.set("verifications", user_id, verification_data)
        db.delete("temp_data", f"waiting_card_photo_{user_id}")
        
        admin_text = f"🆕 **درخواست احراز هویت جدید**\n\n"
        admin_text += f"👤 **کاربر:** {verification_data['first_name']}\n"
        admin_text += f"🆔 **آیدی:** `{user_id}`\n"
        admin_text += f"📧 **یوزرنیم:** @{verification_data['username']}\n"
        admin_text += f"⏰ **زمان:** {time.ctime()}"
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ تایید", callback_data=f"verify_approve_{user_id}"),
                InlineKeyboardButton("❌ رد", callback_data=f"verify_reject_{user_id}")
            ]
        ])
        
        try:
            await message.forward(ADMIN_ID)
            await bot.send_message(ADMIN_ID, admin_text, reply_markup=keyboard)
            
            await message.reply_text(
                "✅ **عکس شما دریافت شد و برای تایید به ادمین ارسال شد**\n\n"
                "⏳ لطفا منتظر تایید ادمین باشید\n"
                "🔔 پس از تایید به شما اطلاع داده خواهد شد",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
            )
        except Exception as e:
            await message.reply_text("❌ خطا در ارسال به ادمین. لطفا بعدا تلاش کنید.")
    
    elif db.get("temp_data", f"waiting_payment_proof_{user_id}"):
        payment_data = db.get("payments", user_id)
        if not payment_data:
            await message.reply_text("❌ اطلاعات پرداخت یافت نشد. لطفا دوباره تلاش کنید.")
            return
        
        payment_data["proof_photo_id"] = message.photo.file_id
        payment_data["proof_sent_at"] = time.time()
        db.set("payments", user_id, payment_data)
        
        admin_text = (
            f"💰 **درخواست افزایش موجودی جدید**\n\n"
            f"👤 **کاربر:** {message.from_user.first_name or 'ناشناس'}\n"
            f"🆔 **آیدی:** `{user_id}`\n"
            f"📧 **یوزرنیم:** @{message.from_user.username or 'ندارد'}\n"
            f"💎 **تعداد سکه:** {payment_data['coins']}\n"
            f"💵 **مبلغ:** {payment_data['toman']:,.0f} تومان\n"
            f"⏰ **زمان:** {time.ctime()}"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ تایید پرداخت", callback_data=f"payment_approve_{user_id}"),
                InlineKeyboardButton("❌ رد پرداخت", callback_data=f"payment_reject_{user_id}")
            ]
        ])
        
        try:
            await message.forward(ADMIN_ID)
            await bot.send_message(ADMIN_ID, admin_text, reply_markup=keyboard)
            
            await message.reply_text(
                "✅ **رسید پرداخت شما دریافت شد و برای تایید به ادمین ارسال شد**\n\n"
                "⏳ لطفا منتظر تایید ادمین باشید\n"
                "🔔 پس از تایید، سکه ها به حساب شما اضافه خواهد شد",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
            )
            
            db.delete("temp_data", f"waiting_payment_proof_{user_id}")
            
        except Exception as e:
            await message.reply_text("❌ خطا در ارسال به ادمین. لطفا بعدا تلاش کنید.")
@bot.on_callback_query(filters.regex("increase_balance"))
async def increase_balance_handler(client, callback_query):
    user_id = callback_query.from_user.id
    ok, not_joined = await check_force_join(client, user_id)
    if not ok:
        buttons = []
        for ch in not_joined:
            buttons.append([InlineKeyboardButton(f"📢 عضویت در @{ch}", url=f"https://t.me/{ch}")])
        buttons.append([InlineKeyboardButton("🔄 بررسی عضویت", callback_data="check_join")])
        
        await callback_query.message.edit_text(
            "❌ برای استفاده از ربات باید در تمام کانال‌های زیر عضو شوید:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    user_data = db.get("users", user_id, {})
    if user_data.get('rejected'):
        await callback_query.answer("❌ حساب شما توسط ادمین رد شده است. امکان افزایش موجودی ندارید.", show_alert=True)
        return
    if not user_data.get('verified'):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("● احراز هویت ●", callback_data="start_verification")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ])
        
        await callback_query.message.edit_text(
            "🔒 **برای افزایش موجودی نیاز به احراز هویت دارید**\n\n"
            "📋 **مراحل احراز هویت:**\n"
            "1️⃣ کلیک روی دکمه 'احراز هویت'\n"
            "2️⃣ ارسال عکس از کارت بانکی\n"
            "3️⃣ تایید توسط ادمین\n"
            "4️⃣ افزایش موجودی\n\n"
            "⚠️ **توجه:** اطلاعات حساس (CVV2، تاریخ انقضا) در عکس پوشیده شود",
            reply_markup=keyboard
        )
        return
    else:
        await callback_query.message.edit_text(
            "💰 **افزایش موجودی**\n\n"
            f"💎 **نرخ تبدیل:** هر {COIN_RATE} سکه = 50,000 تومان\n"
            f"💵 **قیمت هر سکه:** {TOMAN_PER_COIN:.0f} تومان\n\n"
            "🔢 **تعداد سکه مورد نظر خود را وارد کنید:**\n"
            "مثال: 1440\n\n"
            "💡 **توجه:** فقط عدد وارد کنید (بدون نقطه یا کاما)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
        )
        
        db.delete("temp_data", f"waiting_coins_{user_id}")
        db.set("temp_data", f"waiting_coins_{user_id}", True)
        await callback_query.answer("✅ لطفا تعداد سکه مورد نظر را وارد کنید")
def main():
    print("● ربات سلف ساز روشن شد ●")
    try: 
        bot.run()
    except KeyboardInterrupt: 
        print("\n🛑 توقف ربات...")
    except Exception as e:
        print(f"❌ خطای اجرای bot.py: {e}")
        traceback.print_exc()
    finally: 
        stop_all_selfbots()
        print("✅ ربات متوقف شد")

if __name__ == "__main__":
    main()
