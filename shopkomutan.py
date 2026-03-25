from telebot import TeleBot, types

TOKEN = "7950309639:AAEDGFIHcx4YJ8-KFzSq9sqGYyAYpFsTk4o"
bot = TeleBot(TOKEN)

ADMINS = [7279061074]
REQUIRED_CHANNELS = ["@example_channel1"]

users = {}
REF_BONUS = 5

# -------- START --------
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
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
    if message.from_user.id in ADMINS:
        kb.add("/panel")
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

# -------- ADMIN PANEL --------
@bot.message_handler(commands=['panel'])
def panel(message):
    if message.from_user.id not in ADMINS:
        bot.send_message(message.chat.id, "Yetkin yok!")
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("⭐ Bakiye Ver", callback_data="panel_balance"),
        types.InlineKeyboardButton("➕ Kanal Ekle", callback_data="panel_add_channel"),
        types.InlineKeyboardButton("➖ Kanal Sil", callback_data="panel_remove_channel"),
        types.InlineKeyboardButton("👑 Admin Ekle", callback_data="panel_add_admin"),
        types.InlineKeyboardButton("📊 Kullanıcı Listesi", callback_data="panel_users")
    )
    bot.send_message(message.chat.id, "👑 Admin Paneli", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("panel_"))
def panel_callback(call):
    data = call.data

    if data == "panel_balance":
        msg = bot.send_message(call.message.chat.id, "Kullanıcı ID ve miktarı yaz (örn: 123456 10)")
        bot.register_next_step_handler(msg, add_balance)

    elif data == "panel_add_channel":
        msg = bot.send_message(call.message.chat.id, "Eklemek istediğin kanalı yaz (@kanal)")
        bot.register_next_step_handler(msg, add_channel)

    elif data == "panel_remove_channel":
        msg = bot.send_message(call.message.chat.id, "Silmek istediğin kanalı yaz (@kanal)")
        bot.register_next_step_handler(msg, remove_channel)

    elif data == "panel_add_admin":
        msg = bot.send_message(call.message.chat.id, "Yeni adminin ID'sini yaz")
        bot.register_next_step_handler(msg, add_admin)

    elif data == "panel_users":
        text = "👥 Kullanıcı Listesi:\n"
        for uid, info in users.items():
            text += f"{uid} - ⭐ {info['balance']} - Referal: {info['invited']}\n"
        bot.send_message(call.message.chat.id, text)

# -------- PANEL FONKSIYONLARI --------
def add_balance(message):
    try:
        uid, amt = map(int, message.text.split())
        users[uid]["balance"] += amt
        bot.send_message(message.chat.id, f"{amt}⭐ {uid} kullanıcısına eklendi.")
    except:
        bot.send_message(message.chat.id, "Hata! Örn: 123456 10")

def add_channel(message):
    ch = message.text.strip()
    if ch not in REQUIRED_CHANNELS:
        REQUIRED_CHANNELS.append(ch)
        bot.send_message(message.chat.id, f"{ch} kanalı eklendi.")
    else:
        bot.send_message(message.chat.id, "Zaten mevcut.")

def remove_channel(message):
    ch = message.text.strip()
    if ch in REQUIRED_CHANNELS:
        REQUIRED_CHANNELS.remove(ch)
        bot.send_message(message.chat.id, f"{ch} kanalı silindi.")
    else:
        bot.send_message(message.chat.id, "Böyle bir kanal yok.")

def add_admin(message):
    try:
        new_admin = int(message.text.strip())
        if new_admin not in ADMINS:
            ADMINS.append(new_admin)
            bot.send_message(message.chat.id, f"{new_admin} artık admin!")
        else:
            bot.send_message(message.chat.id, "Zaten admin.")
    except:
        bot.send_message(message.chat.id, "Geçerli bir ID gir.")

# -------- RUN --------
bot.infinity_polling()
