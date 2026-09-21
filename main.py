import os
import telebot

# Render üzerindeki BOT_TOKEN değişkenini alır
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    # Yedek token tanımlaması
    TOKEN = "8531178024:AAGTlfjZL6yzWJQqNGC2_Jy9J4g7yopT_nA"

bot = telebot.TeleBot(TOKEN)

# /start ve /help komutları
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👑 *GÖKØ VIP MARKET'e Hoş Geldiniz!*\n\n"
        "Kaliteli ve güvenilir hizmetin adresi.\n"
        "Aşağıdaki komutları kullanarak işlemlerinizi yapabilirsiniz:\n\n"
        "🛒 /market - Ürün ve Hizmet Listesi\n"
        "📞 /iletisim - Destek ve İletişim"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# /market komutu
@bot.message_handler(commands=['market'])
def send_market(message):
    market_text = (
        "🛒 *GÖKØ VIP MARKET ÜRÜNLERİ*\n\n"
        "1️⃣ VIP Üyelik Package A - 100 ₺\n"
        "2️⃣ VIP Üyelik Package B - 250 ₺\n"
        "3️⃣ Özel Hizmetler\n\n"
        "Sipariş vermek veya bilgi almak için lütfen /iletisim komutunu kullanın."
    )
    bot.reply_to(message, market_text, parse_mode="Markdown")

# /iletisim komutu
@bot.message_handler(commands=['iletisim'])
def send_contact(message):
    contact_text = (
        "📞 *İLETİŞİM VE DESTEK*\n\n"
        "Yetkili ile iletişime geçmek için Telegram üzerinden yazabilirsiniz.\n"
        "Destek Hattı: @gokovipdestek"
    )
    bot.reply_to(message, contact_text, parse_mode="Markdown")

# Gelen diğer mesajlar
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Anlayamadım. Komutları görmek için /start yazabilirsiniz.")

if __name__ == '__main__':
    print("GÖKØ VIP MARKET Botu Çalışıyor...")
    bot.infinity_polling()
  
