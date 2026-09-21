import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
# Bot Token ve Ana Kurucu Bilgisi
API_TOKEN = '8531178024:AAGTlfjZL6yzWJQqNGC2_Jy9J4g7yopT_nA'
bot = telebot.TeleBot(API_TOKEN)

SUPER_ADMIN_ID = 7731769678
ADMINS = {7731769678}  # Yönetici ID listesi
REF_BONUS = 10         # Davet eden kişiye verilecek hediye bakiye (TL)
DAILY_BONUS = 15       # Günlük bonus miktarı (TL)

# Veri Depolama
balances = {}          # {user_id: bakiye}
invited_by = {}        # {user_id: inviter_id}
referral_counts = {}   # {user_id: davet_sayisi}
last_daily_claim = {}  # {user_id: timestamp}
all_users = set()      # Tüm kullanıcı ID'leri
waiting_support = set()# İletişim mesajı beklenen kullanıcılar

# Ürünler Listesi
PRODUCTS = {
    "cfg": {
        "name": "Gökø vip cfg",
        "price": 150,
        "content": "✅ **Gökø vip cfg** Başarıyla Satın Alındı!\n\n🔗 İndirme Linki / Kurulum: https://t.me/Gokoguvence"
    },
    "hs": {
        "name": "Göko vip hs",
        "price": 200,
        "content": "✅ **Göko vip hs** Başarıyla Satın Alındı!\n\n🔗 İndirme Linki / Kurulum: https://t.me/Gokoguvence"
    },
    "esp_aim": {
        "name": "Gökø vip esp+aim",
        "price": 300,
        "content": "✅ **Gökø vip esp+aim** Başarıyla Satın Alındı!\n\n🔗 İndirme Linki / Kurulum: https://t.me/Gokoguvence"
    }
}

# Ana Menü Butonları
def main_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton('🛒 Market', callback_data='menu_market'),
        InlineKeyboardButton('👤 Profilim', callback_data='menu_profile')
    )
    markup.add(
        InlineKeyboardButton('🎁 Günlük Bonus (+15 TL)', callback_data='menu_daily'),
        InlineKeyboardButton('👥 Referans Sistemi', callback_data='menu_ref')
    )
    markup.add(
        InlineKeyboardButton('💳 Bakiye Yükle', url='https://t.me/Gokoguvence'),
        InlineKeyboardButton('📩 İletişim / Destek', callback_data='menu_contact')
    )
    
    # Sadece Yöneticiler için Admin Paneli
    if user_id in ADMINS:
        markup.add(InlineKeyboardButton('👑 Admin Paneli', callback_data='menu_admin'))
        
    return markup

# Market Ürün Butonları
def market_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    for code, item in PRODUCTS.items():
        btn_text = f"{item['name']} - {item['price']} TL"
        markup.add(InlineKeyboardButton(btn_text, callback_data=f"buy_{code}"))
    markup.add(InlineKeyboardButton('⬅️ Ana Menüye Dön', callback_data='menu_main'))
    return markup

# Admin Paneli Butonları
def admin_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton('➕ Bakiye Ekle', callback_data='admin_add_bal'),
        InlineKeyboardButton('➖ Bakiye Sil', callback_data='admin_rem_bal')
    )
    markup.add(
        InlineKeyboardButton('🏷️ Fiyat Düzenle', callback_data='admin_edit_price'),
        InlineKeyboardButton('👑 Admin Yönetimi', callback_data='admin_manage_admins')
    )
    markup.add(
        InlineKeyboardButton('📢 Duyuru Gönder', callback_data='admin_broadcast'),
        InlineKeyboardButton('📊 İstatistikler', callback_data='admin_stats')
    )
    markup.add(InlineKeyboardButton('⬅️ Ana Menüye Dön', callback_data='menu_main'))
    return markup

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
    
                    bot.send_message(
                        inviter_id,
                        f"🎉 **Yeni Referans!**\nBir kullanıcı davet linkinizle katıldı!\n💰 **+{REF_BONUS} TL** bakiye hesabınıza eklendi.",
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
    
    text = (
        "🔥 **GÖKØ VIP MARKET'E HOŞ GELDİNİZ** 🔥\n\n"
        "Aşağıdaki butonları kullanarak ürünlerimizi inceleyebilir, günlük bonus ve davet linkinizle bakiye kazanabilirsiniz."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
    
# Buton Tıklamaları
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    user_id = call.from_user.id
    if user_id not in balances:
        balances[user_id] = 0

    bot_username = bot.get_me().username

    if call.data == 'menu_main':
        if user_id in waiting_support:
            waiting_support.remove(user_id)
        text = "🔥 **GÖKØ VIP MARKET ANA MENÜ** 🔥\n\nLütfen yapmak istediğiniz işlemi seçin:"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(user_id), parse_mode='Markdown')

    elif call.data == 'menu_daily':
        now = time.time()
        last_claim = last_daily_claim.get(user_id, 0)
        cooldown = 24 * 3600  # 24 Saat (saniye cinsinden)

        if now - last_claim >= cooldown:
            balances[user_id] += DAILY_BONUS
            last_daily_claim[user_id] = now
            bot.answer_callback_query(call.id, f"🎉 Tebrikler! +{DAILY_BONUS} TL Günlük Bonus kazandınız!", show_alert=True)
            
            text = (
                f"🎁 **GÜNLÜK BONUS TOPLANDI!**\n\n"
                f"💰 **+{DAILY_BONUS} TL** hesabınıza eklendi!\n"
                f"💳 **Yeni Bakiyeniz:** {balances[user_id]} TL\n\n"
                f"⏳ Yarın tekrar gelip bonusunuzu alabilirsiniz."
            )
        else:
            remaining_seconds = int(cooldown - (now - last_claim))
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            bot.answer_callback_query(
                call.id, 
                f"⏳ Günlük bonusunuzu zaten aldınız!\nKalan Süre: {hours} saat {minutes} dakika.", 
                show_alert=True
            )
            text = (
                f"⏳ **GÜNLÜK BONUS BEKLEME SÜRESİ**\n\n"
                f"Bir sonraki bonusunuzu almak için kalan süre:\n"
                f"🕒 **{hours} Saat {minutes} Dakika**"
            )

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('⬅️ Ana Menüye Dön', callback_data='menu_main'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

    elif call.data == 'menu_market':
        text = f"🛒 **GÖKØ VIP MARKET**\n\n💰 Bakiyeniz: **{balances[user_id]} TL**\n\nSatın almak istediğiniz ürüne tıklayın:"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=market_keyboard(), parse_mode='Markdown')

    elif call.data == 'menu_profile':
        user_balance = balances.get(user_id, 0)
        ref_count = referral_counts.get(user_id, 0)
        text = (
            f"👤 **KULLANICI PROFİLİ**\n\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"💰 **Bakiye:** {user_balance} TL\n"
            f"👥 **Davet Ettiğiniz:** {ref_count} Kişi"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('⬅️ Ana Menüye Dön', callback_data='menu_main'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

    elif call.data == 'menu_ref':
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        ref_count = referral_counts.get(user_id, 0)
        text = (
            f"👥 **REFERANS SİSTEMİ**\n\n"
            f"Arkadaşlarınızı davet ederek her davet için **+{REF_BONUS} TL** bakiye kazanın!\n\n"
            f"📊 **Mevcut Davet Sayınız:** {ref_count} Kişi\n"
            f"💰 **Kazandığınız Ödül:** {ref_count * REF_BONUS} TL\n\n"
            f"🔗 **Özel Davet Linkiniz:**\n`{ref_link}`"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('⬅️ Ana Menüye Dön', callback_data='menu_main'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

    elif call.data == 'menu_contact':
        waiting_support.add(user_id)
        text = "📩 **@Denktinee ye bildirmek istediğiniz mesajı yazınız:**"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('❌ İptal Et', callback_data='menu_main'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

    elif call.data == 'menu_admin' and user_id in ADMINS:
        text = "👑 **GÖKØ VIP MARKET ADMIN PANELİ**\n\nYapmak istediğiniz yönetici işlemini seçin:"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_keyboard(), parse_mode='Markdown')

    elif call.data == 'admin_stats' and user_id in ADMINS:
        total_users = len(all_users)
        total_balance = sum(balances.values())
        admin_list = "\n".join([f"• `{aid}`" for aid in ADMINS])
        text = (
            f"📊 **BOTA DAHİL İSTATİSTİKLER**\n\n"
            f"👤 **Toplam Kullanıcı:** {total_users}\n"
            f"💰 **Sistemdeki Toplam Bakiye:** {total_balance} TL\n\n"
            f"👑 **Mevcut Yöneticiler:**\n{admin_list}"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('⬅️ Admin Paneline Dön', callback_data='menu_admin'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

    elif call.data == 'admin_edit_price' and user_id in ADMINS:
        prod_info = "\n".join([f"• `{code}` - {item['name']} ({item['price']} TL)" for code, item in PRODUCTS.items()])
        msg = (
            f"🏷️ **ÜRÜN FİYATI GÜNCELLEME**\n\n"
            f"**Mevcut Ürün Kodları ve Fiyatları:**\n{prod_info}\n\n"
            f"💡 **Fiyat değiştirmek için komut:**\n`/fiyatguncelle <urun_kodu> <yeni_fiyat>`\n"
            f"Örnek: `/fiyatguncelle cfg 180`"
        )
        bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')

    elif call.data == 'admin_manage_admins' and user_id in ADMINS:
        admin_list = "\n".join([f"• `{aid}`" for aid in ADMINS])
        msg = (
            f"👑 **YÖNETİCİ YÖNETİMİ**\n\n"
            f"**Mevcut Yöneticiler:**\n{admin_list}\n\n"
            f"➕ **Yönetici Ekle:** `/adminekle <kullanici_id>`\n"
            f"➖ **Yönetici Sil:** `/adminsil <kullanici_id>`"
        )
        bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')

    elif call.data == 'admin_add_bal' and user_id in ADMINS:
        bot.send_message(call.message.chat.id, "💡 Bakiye eklemek için komut:\n`/bakiyeekle <kullanici_id> <miktar>`", parse_mode='Markdown')

    elif call.data == 'admin_rem_bal' and user_id in ADMINS:
        bot.send_message(call.message.chat.id, "💡 Bakiye silmek için komut:\n`/bakiyesil <kullanici_id> <miktar>`", parse_mode='Markdown')

    elif call.data == 'admin_broadcast' and user_id in ADMINS:
        bot.send_message(call.message.chat.id, "💡 Duyuru geçmek için komut:\n`/duyuru <mesajiniz>`", parse_mode='Markdown')

    elif call.data.startswith('buy_'):
        prod_code = call.data.split('_', 1)[1]
        if prod_code in PRODUCTS:
            product = PRODUCTS[prod_code]
            price = product['price']
            
            if balances[user_id] >= price:
                balances[user_id] -= price
                bot.answer_callback_query(call.id, "🎉 Satın alma başarılı!")
                
                bot.send_message(call.message.chat.id, product['content'], parse_mode='Markdown')
                
                for admin_id in ADMINS:
                    try:
                        bot.send_message(admin_id, f"🔔 **YENİ SATIŞ!**\nKullanıcı ID: `{user_id}`\nÜrün: {product['name']}\nFiyat: {price} TL", parse_mode='Markdown')
                    except Exception:
                        pass
                
                text = f"🛒 **GÖKØ VIP MARKET**\n\n💰 Kalan Bakiyeniz: **{balances[user_id]} TL**"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=market_keyboard(), parse_mode='Markdown')
            else:
                bot.answer_callback_query(call.id, f"❌ Yetersiz Bakiye! Bu ürün {price} TL.", show_alert=True)

# 📩 Kullanıcıdan Gelen İletişim Mesajlarını Yakalama
@bot.message_handler(func=lambda message: message.from_user.id in waiting_support and not message.text.startswith('/'))
def process_support_message(message):
    user = message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "Kullanıcı adı yok"
    first_name = user.first_name or "İsimsiz"
    
    bot.reply_to(message, "✅ **Mesajınız @Denktinee ye iletildi.** En kısa sürede dönüş yapılacaktır.")
    waiting_support.remove(user_id)
    
    admin_info = (
        f"📩 **YENİ DESTEK/İLETİŞİM MESAJI!**\n\n"
        f"👤 **Gönderen:** {first_name} ({username})\n"
        f"🆔 **ID:** `{user_id}`\n"
        f"💬 **Mesaj:**\n"
    )
    
    for admin_id in ADMINS:
        try:
            bot.send_message(admin_id, admin_info, parse_mode='Markdown')
            bot.forward_message(admin_id, message.chat.id, message.message_id)
        except Exception:
            pass

# 👑 ADMIN KOMUTLARI
@bot.message_handler(commands=['fiyatguncelle'])
def update_price(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        args = message.text.split()
        code = args[1]
        new_price = int(args[2])

        if code in PRODUCTS:
            PRODUCTS[code]['price'] = new_price
            bot.send_message(message.chat.id, f"✅ **{PRODUCTS[code]['name']}** yeni fiyatı **{new_price} TL** olarak güncellendi!", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❌ Geçersiz ürün kodu! Kodlar: `cfg`, `hs`, `esp_aim`", parse_mode='Markdown')
    except Exception:
        bot.send_message(message.chat.id, "❌ Kullanım: `/fiyatguncelle <urun_kodu> <yeni_fiyat>`", parse_mode='Markdown')

@bot.message_handler(commands=['adminekle'])
def add_admin(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        args = message.text.split()
        new_admin_id = int(args[1])
        ADMINS.add(new_admin_id)
        bot.send_message(message.chat.id, f"✅ `{new_admin_id}` ID'li kullanıcı yeni **Yönetici** olarak eklendi!", parse_mode='Markdown')
    except Exception:
        bot.send_message(message.chat.id, "❌ Kullanım: `/adminekle <kullanici_id>`", parse_mode='Markdown')

@bot.message_handler(commands=['adminsil'])
def remove_admin(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        args = message.text.split()
        remove_id = int(args[1])
        if remove_id == SUPER_ADMIN_ID:
            bot.send_message(message.chat.id, "❌ Ana kurucu hesabı yöneticilikten çıkarılamaz!", parse_mode='Markdown')
            return
        if remove_id in ADMINS:
            ADMINS.remove(remove_id)
            bot.send_message(message.chat.id, f"✅ `{remove_id}` ID'li kullanıcının yöneticiliği kaldırıldı!", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❌ Bu ID yönetici listesinde bulunamadı.", parse_mode='Markdown')
    except Exception:
        bot.send_message(message.chat.id, "❌ Kullanım: `/adminsil <kullanici_id>`", parse_mode='Markdown')

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
