from telebot import TeleBot, types

TOKEN = "7950309639:AAEDGFIHcx4YJ8-KFzSq9sqGYyAYpFsTk4o"
bot = TeleBot(TOKEN)

ADMINS = [7279061074]
REQUIRED_CHANNELS = ["@example_channel1"]

# basit veritabanı
users = {}

REF_BONUS = 5

# -------- START --------
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id

    # referal
    ref = None
    args = message.text.split()
    if len(args) > 1:
        try:
            ref = int(args[1])
        except:
            pass

    if uid not in users:
        users[uid] = {"balance": 0, "ref": ref, "invited": 0}

        if ref and ref != uid and ref in users:
            users[ref]["balance"] += REF_BONUS
            users[ref]["invited"] += 1
            bot.send_message(ref, f"🎉 Yeni referal! +{REF_BONUS}⭐")

    if not check_channels(uid):
        join_menu(message)
        return

    menu(message)

# -------- MENÜ --------
def menu(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⭐ Kazan", "👤 Profil")
    kb.add("🤝 Referal")
    bot.send_message(message.chat.id, "Menü:", reply_markup=kb)

# -------- KANAL --------
def check_channels(uid):
    for ch in REQUIRED_CHANNELS:
        try:
            m = bot.get_chat_member(ch, uid)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

def join_menu(message):
    kb = types.InlineKeyboardMarkup()
    for ch in REQUIRED_CHANNELS:
        kb.add(types.InlineKeyboardButton(
            text=f"➕ {ch}",
            url=f"https://t.me/{ch.replace('@','')}"
        ))
    kb.add(types.InlineKeyboardButton("✅ Kontrol", callback_data="check"))
    bot.send_message(message.chat.id, "Kanallara katıl:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(call):
    if check_channels(call.from_user.id):
        bot.answer_callback_query(call.id, "Tamam")
        menu(call.message)
    else:
        bot.answer_callback_query(call.id, "Katılmadın!", show_alert=True)

# -------- KAZAN --------
@bot.message_handler(func=lambda m: m.text == "⭐ Kazan")
def earn(message):
    uid = message.from_user.id
    users[uid]["balance"] += 1
    bot.send_message(message.chat.id, "⭐ +1 kazandın!")

# -------- PROFIL --------
@bot.message_handler(func=lambda m: m.text == "👤 Profil")
def profil(message):
    u = users.get(message.from_user.id, {})
    bot.send_message(
        message.chat.id,
        f"👤 Profil\n⭐ {u.get('balance',0)}\n👥 Referal: {u.get('invited',0)}"
    )

# -------- REFERAL --------
@bot.message_handler(func=lambda m: m.text == "🤝 Referal")
def referal(message):
    uid = message.from_user.id
    link = f"https://t.me/{bot.get_me().username}?start={uid}"
    bot.send_message(message.chat.id, f"Linkin:\n{link}")

# -------- ADMIN --------
@bot.message_handler(commands=['add'])
def add(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        uid, amt = map(int, message.text.split()[1:])
        users[uid]["balance"] += amt
        bot.send_message(message.chat.id, "Eklendi")
    except:
        bot.send_message(message.chat.id, "Hata")

# -------- RUN --------
bot.infinity_polling()
