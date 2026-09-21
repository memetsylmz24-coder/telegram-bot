import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Token ve Admin Ayarları
TOKEN = "8531178024:AAH..."  # Kendi token'ını buraya eksiksiz yaz
ADMINS = [7731769678]
REF_BONUS = 10  # Davet başına verilecek bakiye

bot = telebot.TeleBot(TOKEN)

# Bellek Veritabanı
balances = {}
all_users = set()
referral_counts = {}
invited_by = {}
waiting_support = set()

# /start Komutu
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    all_users.add(user_id)
    
    if user_id not in balances:
        balances[user_id] = 0
        referral_counts[user_id] = 0
        
        args = message.text.split()
        if len(args) > 1 and args[1].isdigit():
            inviter_id = int(args[1])
            if inviter_id != user_id and inviter_id in all_users:
                invited_by[user_id] = inviter_id
                referral_counts[inviter_id] += 1
                balances[inviter_id] += REF_BONUS
                try:
                    bot.send_message(
                        inviter_id,
                        f"🎉 **Yeni Referans!** Davetinizle biri katıldı ve hesabınıza **+{REF_BONUS} TL** eklendi!",
                        parse_mode='Markdown'
                    )
                except Exception:
                    pass

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Kanalımıza Katılın", url="https://t.me/yago_frewl"))
    markup.add(
        InlineKeyboardButton("🛒 Market", callback_data="market"),
        InlineKeyboardButton("👤 Profilim", callback_data="profile")
    )
    markup.add(
        InlineKeyboardButton("🎁 Günlük Bonus", callback_data="daily_bonus"),
        InlineKeyboardButton("👥 Referans Sistemi", callback_data="referral")
    )
    markup.add(
        InlineKeyboardButton("💳 Bakiye Yükle", callback_data="deposit"),
        InlineKeyboardButton("✉️ İletişim / Destek", callback_data="support")
    )
    markup.add(InlineKeyboardButton("👑 Admin Paneli", callback_data="admin_panel"))

    text = (
        "🔥 **GÖKØ VIP MARKET'E HOŞ GELDİNİZ** 🔥\n\n"
        "Aşağıdaki butonları kullanarak ürünlerimizi inceleyebilir, günlük bonus ve davet linkinizle bakiye kazanabilirsiniz."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

# Bakiye Ekleme Komutu
@bot.message_handler(commands=['bakiyeekle'])
def add_balance(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        args = message.text.split()
        target_id = int(args[1])
        amount = int(args[2])
        
        balances[target_id] = balances.get(target_id, 0) + amount
        bot.send_message(message.chat.id, f"✅ `{target_id}` ID'li kullanıcıya **+{amount} TL** eklendi!", parse_mode='Markdown')
        
        try:
            bot.send_message(target_id, f"🎉 Hesabınıza **+{amount} TL** bakiye eklendi!\nMevcut Bakiyeniz: {balances[target_id]} TL", parse_mode='Markdown')
        except Exception:
            pass
    except Exception:
        bot.send_message(message.chat.id, "❌ Kullanım: `/bakiyeekle <kullanici_id> <miktar>`", parse_mode='Markdown')

# Bakiye Silme Komutu
@bot.message_handler(commands=['bakiyesil'])
def remove_balance(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        args = message.text.split()
        target_id = int(args[1])
        amount = int(args[2])
        
        balances[target_id] = max(0, balances.get(target_id, 0) - amount)
        bot.send_message(message.chat.id, f"✅ `{target_id}` ID'li kullanıcının bakiyesinden **-{amount} TL** düşüldü!", parse_mode='Markdown')
    except Exception:
        bot.send_message(message.chat.id, "❌ Kullanım: `/bakiyesil <kullanici_id> <miktar>`", parse_mode='Markdown')

# Duyuru Komutu
@bot.message_handler(commands=['duyuru'])
def send_broadcast(message):
    if message.from_user.id not in ADMINS:
        return
    
    text = message.text.replace('/duyuru', '').strip()
    if not text:
        bot.send_message(message.chat.id, "❌ Lütfen gönderilecek duyuru mesajını yazın!\nÖrnek: `/duyuru İndirim Başladı!`", parse_mode='Markdown')
        return

    success_count = 0
    for uid in list(all_users):
        try:
            bot.send_message(uid, f"📢 **GÖKØ VIP MARKET DUYURUSU**\n\n{text}", parse_mode='Markdown')
            success_count += 1
        except Exception:
            pass

    bot.send_message(message.chat.id, f"✅ Duyuru **{success_count}** kullanıcıya başarıyla ulaştırıldı!", parse_mode='Markdown')

# Botu Çalıştır
bot.infinity_polling()
