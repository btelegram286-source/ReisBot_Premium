# -*- coding: utf-8 -*-
import os
import logging
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import telebot
from telebot import types
from github import Github
import openai
import youtube_dl
from bs4 import BeautifulSoup
import utils
from github_manager import GitHubManager
from render_manager import RenderManager
from scheduler import BotScheduler
from premium_features import PremiumFeatures

# ENV YÜKLE
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config.env")
load_dotenv(config_path)

# API ANAHTARLARI
BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER")
OPENAI_API_KEY = os.getenv("OPENAI_KEY")
RENDER_API_KEY = os.getenv("RENDER_API_KEY")
RENDER_SERVICE_ID = os.getenv("RENDER_OWNER_ID")  # RENDER_OWNER_ID olarak değiştirildi

# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# TELEGRAM BOT
bot = telebot.TeleBot(BOT_TOKEN)

# OPENAI KURULUM
if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
    openai.api_key = OPENAI_API_KEY
    AI_ENABLED = True
else:
    AI_ENABLED = False
    logger.warning("OpenAI API anahtarı bulunamadı. AI özellikleri devre dışı.")

# GITHUB KURULUM
if GITHUB_TOKEN:
    try:
        github = Github(GITHUB_TOKEN)
        github_manager = GitHubManager(GITHUB_TOKEN, GITHUB_USER)
        GITHUB_ENABLED = True
    except Exception as e:
        logger.error(f"GitHub bağlantı hatası: {e}")
        GITHUB_ENABLED = False
        github_manager = None
else:
    GITHUB_ENABLED = False
    github_manager = None
    logger.warning("GitHub token bulunamadı. GitHub özellikleri devre dışı.")

# RENDER KURULUM
if RENDER_API_KEY and RENDER_SERVICE_ID:
    try:
        render_manager = RenderManager(RENDER_API_KEY, RENDER_SERVICE_ID)
        RENDER_ENABLED = True
    except Exception as e:
        logger.error(f"Render bağlantı hatası: {e}")
        RENDER_ENABLED = False
        render_manager = None
else:
    RENDER_ENABLED = False
    render_manager = None
    logger.warning("Render API anahtarları bulunamadı. Render özellikleri devre dışı.")

# SCHEDULER KURULUM
scheduler = None
if github_manager and render_manager:
    try:
        scheduler = BotScheduler(bot, github_manager, render_manager)
        SCHEDULER_ENABLED = True
    except Exception as e:
        logger.error(f"Scheduler kurulum hatası: {e}")
        SCHEDULER_ENABLED = False
else:
    SCHEDULER_ENABLED = False
    logger.warning("Scheduler için gerekli bileşenler eksik.")

# PREMIUM FEATURES KURULUM
try:
    premium = PremiumFeatures()
    PREMIUM_ENABLED = True
    logger.info("✅ Premium özellikler aktif!")
except Exception as e:
    logger.error(f"Premium features kurulum hatası: {e}")
    PREMIUM_ENABLED = False
    premium = None

# AI 429 cooldown kontrolü (saniye cinsinden epoch zaman)
AI_COOLDOWN_UNTIL = 0

# YARDIMCI FONKSİYONLAR
def get_ai_response(prompt):
    """OpenAI ile sohbet cevabı al"""
    if not AI_ENABLED:
        return "❌ OpenAI servisi şu anda kullanılamıyor."
    
    # 429 sonrası cooldown kontrolü
    try:
        global AI_COOLDOWN_UNTIL
        now = time.time()
        if now < AI_COOLDOWN_UNTIL:
            remaining = int((AI_COOLDOWN_UNTIL - now) // 60) + 1
            return f"❌ OpenAI kullanım limiti geçici olarak doldu. Lütfen {remaining} dk sonra tekrar deneyin."
    except Exception:
        # Her ihtimale karşı cooldown hataları sessiz geçilir
        pass

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e).lower()
        # 429 veya kota/limit -> cooldown başlat
        if "429" in error_msg or "quota" in error_msg or "limit" in error_msg:
            try:
                AI_COOLDOWN_UNTIL = time.time() + 10 * 60  # 10 dakika
            except Exception:
                pass
            return "❌ OpenAI kotası dolmuş veya çok fazla istek gönderildi. 10 dk sonra tekrar deneyin."
        elif "invalid" in error_msg and "key" in error_msg:
            return "❌ OpenAI API anahtarı geçersiz. Lütfen yönetici ile iletişime geçin."
        elif "rate" in error_msg:
            return "❌ Çok fazla istek gönderildi. Lütfen birkaç saniye bekleyin ve tekrar deneyin."
        else:
            return f"❌ AI hatası: {str(e)}"

def github_push_to_repo(repo_name, file_content, file_name="bot_update.py"):
    """GitHub'a dosya push et"""
    if not GITHUB_ENABLED:
        return "❌ GitHub servisi şu anda kullanılamıyor."
    
    try:
        user = github.get_user()
        try:
            repo = user.get_repo(repo_name)
        except:
            repo = user.create_repo(repo_name)
        
        try:
            contents = repo.get_contents(file_name)
            repo.update_file(contents.path, f"Update {file_name}", file_content, contents.sha)
            return f"✅ {file_name} dosyası güncellendi!"
        except:
            repo.create_file(file_name, f"Create {file_name}", file_content)
            return f"✅ {file_name} dosyası oluşturuldu!"
    except Exception as e:
        return f"❌ GitHub hatası: {str(e)}"

def download_youtube_audio(url):
    """YouTube'dan audio indir"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return f"✅ İndirme tamamlandı: {info['title']}"
    except Exception as e:
        return f"❌ İndirme hatası: {str(e)}"

# KOMUTLAR
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Kullanıcıyı veritabanına ekle
    if PREMIUM_ENABLED and premium is not None:
        try:
            premium.add_user(
                message.from_user.id,
                message.from_user.username,
                message.from_user.first_name,
                message.from_user.last_name
            )
        except Exception as e:
            logger.error(f"Kullanıcı ekleme hatası: {e}")
    
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [
        "🤖 AI Sohbet",
        "📁 GitHub Yönetimi", 
        "🔄 Render Yönetimi",
        "🎵 YouTube İndir",
        "📊 Bot Durumu",
        "🌤️ Hava Durumu",
        "💱 Döviz Kuru",
        "₿ Bitcoin",
        "🔗 QR Kod",
        "🎤 Ses Çevir",
        "🖼️ AI Görsel",
        "📝 Makale Yaz",
        "🌍 Çeviri",
        "🔐 Şifre Üret",
        "📋 Notlarım",
        "⏰ Hatırlatıcı",
        "🧮 Hesap Makinesi",
        "🔗 URL Kısalt",
        "💭 Motivasyon",
        "📈 İstatistiklerim"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    
    welcome_text = """
    🚀 *ReisBot Premium'a Hoşgeldin!*

    *🎯 SÜPER PREMIUM ÖZELLİKLER:*
    
    **🤖 AI & Automation:**
    • Yapay Zeka Sohbeti & Görsel Üretme
    • GitHub Tam Yönetimi (CRUD, Commits)
    • Render Otomatik Deploy & Monitoring
    • 7/24 Cron Job Sistemi
    
    **📝 Content & Productivity:**
    • Makale/Blog Yazma Asistanı
    • 50+ Dil Çeviri Servisi
    • Güvenli Şifre Üretici
    • Kişisel Not Defteri
    • Akıllı Hatırlatıcı Sistemi
    
    **🛠️ Utilities & Tools:**
    • Gelişmiş Hesap Makinesi
    • URL Kısaltma Servisi
    • QR Kod & Ses İşleme
    • Hava Durumu & Finans Takibi
    • Günlük Motivasyon Sözleri
    
    **📊 Analytics & Stats:**
    • Kişisel Kullanım İstatistikleri
    • Sistem Performans Raporları
    • Otomatik Yedekleme & Sync

    /help ile tüm komutları görebilirsin!
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    *🤖 ReisBot Premium Komutları:*

    */start* - Botu başlat
    */help* - Yardım menüsü
    */status* - Bot durumu

    *AI & Medya:*
    */ai <soru>* - AI ile sohbet et
    */image <prompt>* - AI görsel oluştur
    */yt <url>* - YouTube'dan indir
    */tts <metin>* - Metni sese çevir

    *GitHub & Deploy:*
    */github <repo> <dosya>* - GitHub'a dosya push et
    */autodeploy <repo> [zip]* - Otomatik repo oluştur & deploy
    */repos* - Tüm repoları listele
    */deleterepo <repo>* - Repository sil

    *Bilgi & Araçlar:*
    */weather <şehir>* - Hava durumu
    */exchange <from> <to>* - Döviz kuru
    */bitcoin* - Bitcoin fiyatı
    */qr <metin>* - QR kod oluştur
    */calc <ifade>* - Hesap makinesi (örn: 2*(3+4))
    */translate <dil> <metin>* - Çeviri (örn: en merhaba dünya)
    */shorten <url>* - URL kısalt
    */password <uzunluk> <evet/hayır>* - Şifre üret (semboller)

    *Not & Hatırlatıcı:*
    */notes* - Notlarımı listele
    */addnote <başlık> | <içerik>* - Not ekle
    */delnote <id>* - Not sil
    */remind <YYYY-MM-DD HH:MM> | <mesaj>* - Hatırlatıcı ekle
    */reminders* - Hatırlatıcıları listele
    */motivate* - Günün sözü
    */mystats* - Kullanım istatistiklerim

    *Buton Özellikleri:*
    • 🤖 AI Sohbet
    • 📁 GitHub Yönetimi
    • 🔄 Render Yönetimi
    • 🎵 YouTube İndir
    • 🌤️ Hava Durumu
    • 💱 Döviz Kuru
    • ₿ Bitcoin
    • 🔗 QR Kod
    • 🎤 Ses Çevir
    • 🖼️ AI Görsel
    • 🧮 Hesap Makinesi
    • 🌍 Çeviri
    • 🔗 URL Kısalt
    • 🔐 Şifre Üret
    • 📋 Notlarım
    • ⏰ Hatırlatıcı
    • 💭 Motivasyon
    • 📈 İstatistiklerim
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['ai'])
def ai_chat(message):
    try:
        question = message.text.replace("/ai", "").strip()
        if not question:
            bot.reply_to(message, "❌ Lütfen bir soru yaz reis. Örnek: /ai Python nedir?")
            return
        
        bot.send_chat_action(message.chat.id, 'typing')
        response = get_ai_response(question)
        
        # Split long responses
        if len(response) > 4096:
            # Telegram message limit is 4096 characters
            for i in range(0, len(response), 4096):
                chunk = response[i:i+4096]
                if i == 0:
                    bot.reply_to(message, chunk)
                else:
                    bot.send_message(message.chat.id, chunk)
        else:
            bot.reply_to(message, response)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Hata: {str(e)}")

@bot.message_handler(commands=['github'])
def github_command(message):
    if not GITHUB_ENABLED:
        bot.reply_to(message, "❌ GitHub servisi şu anda kullanılamıyor.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Kullanım: /github <repo_adi> <dosya_adi>")
            return
        
        repo_name = parts[1]
        file_name = parts[2]
        
        # Örnek dosya içeriği
        file_content = f"""
# {file_name} - Otomatik oluşturuldu
# Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

print("Merhaba ReisBot!")
print("Bu dosya otomatik olarak oluşturuldu.")
"""
        
        result = github_push_to_repo(repo_name, file_content, file_name)
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, f"❌ GitHub hatası: {str(e)}")

@bot.message_handler(commands=['repos'])
def list_repos_command(message):
    """Tüm GitHub repolarını listele"""
    if not GITHUB_ENABLED:
        bot.reply_to(message, "❌ GitHub servisi şu anda kullanılamıyor.")
        return
    
    try:
        repos = github_manager.get_all_repositories()
        if repos:
            repo_text = "📋 *GitHub Repolarınız:*\n\n"
            for repo in repos[:10]:  # İlk 10 repo
                status = "🔒" if repo['private'] else "🌐"
                repo_text += f"{status} *{repo['name']}*\n"
                repo_text += f"   📝 {repo['description'][:50]}...\n"
                repo_text += f"   🔗 {repo['url']}\n"
            
            if len(repos) > 10:
                repo_text += f"📊 Toplam {len(repos)} repo bulundu. İlk 10 gösteriliyor."
        else:
            repo_text = "❌ Hiç repo bulunamadı."
        
        bot.reply_to(message, repo_text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Repo listesi alınamadı: {str(e)}")

@bot.message_handler(commands=['deleterepo'])
def delete_repo_command(message):
    """GitHub repository sil"""
    if not GITHUB_ENABLED:
        bot.reply_to(message, "❌ GitHub servisi şu anda kullanılamıyor.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Kullanım: /deleterepo <repo_adi>")
            return
        
        repo_name = parts[1]
        
        # Onay için inline keyboard oluştur
        markup = types.InlineKeyboardMarkup()
        confirm_btn = types.InlineKeyboardButton("✅ Evet, Sil", callback_data=f"delete_repo_confirm_{repo_name}")
        cancel_btn = types.InlineKeyboardButton("❌ İptal", callback_data="delete_repo_cancel")
        markup.add(confirm_btn, cancel_btn)
        
        bot.reply_to(message, f"⚠️ *{repo_name}* repository'sini silmek istediğine emin misin? Bu işlem geri alınamaz!", 
                    parse_mode='Markdown', reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"❌ Hata: {str(e)}")

@bot.message_handler(commands=['yt'])
def youtube_download(message):
    """YouTube'dan audio indir"""
    try:
        url = message.text.replace("/yt", "").strip()
        if not url:
            bot.reply_to(message, "❌ Lütfen bir YouTube URL'si yaz reis. Örnek: /yt https://youtube.com/...")
            return
        
        bot.send_chat_action(message.chat.id, 'upload_audio')
        result = download_youtube_audio(url)
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, f"❌ Hata: {str(e)}")

@bot.message_handler(commands=['status'])
def bot_status(message):
    """Bot durumunu göster"""
    status_text = f"""
🤖 *ReisBot Premium Durumu*

• 📊 **Sistem:** {'✅ Çalışıyor' if True else '❌ Kapalı'}
• 🤖 **AI Servisi:** {'✅ Aktif' if AI_ENABLED else '❌ Devre Dışı'}
• 📁 **GitHub:** {'✅ Aktif' if GITHUB_ENABLED else '❌ Devre Dışı'}
• 🔄 **Render:** {'✅ Aktif' if RENDER_ENABLED else '❌ Devre Dışı'}
• ⏰ **Scheduler:** {'✅ Aktif' if SCHEDULER_ENABLED else '❌ Devre Dışı'}
• 💎 **Premium:** {'✅ Aktif' if PREMIUM_ENABLED else '❌ Devre Dışı'}

📈 **Son Güncelleme:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    bot.reply_to(message, status_text, parse_mode='Markdown')

# BUTON İŞLEMLERİ
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text
    
    if text == "🤖 AI Sohbet":
        bot.reply_to(message, "🤖 Sorunuzu yazın reis! Örnek: 'Python nedir?'")
    elif text == "📁 GitHub Yönetimi":
        bot.reply_to(message, "📁 GitHub komutları için /help yazabilirsiniz")
    elif text == "🔄 Render Yönetimi":
        bot.reply_to(message, "🔄 Render komutları için /help yazabilirsiniz")
    elif text == "🎵 YouTube İndir":
        bot.reply_to(message, "🎵 YouTube URL'si yazın reis! Örnek: /yt https://youtube.com/...")
    elif text == "📊 Bot Durumu":
        bot_status(message)
    elif text == "🌤️ Hava Durumu":
        bot.reply_to(message, "🌤️ Hava durumu için /weather şehir yazabilirsiniz")
    elif text == "💱 Döviz Kuru":
        bot.reply_to(message, "💱 Döviz kuru için /exchange USD TRY yazabilirsiniz")
    elif text == "₿ Bitcoin":
        bot.reply_to(message, "₿ Bitcoin fiyatı için /bitcoin yazabilirsiniz")
    elif text == "🔗 QR Kod":
        bot.reply_to(message, "🔗 QR kod için /qr metin yazabilirsiniz")
    elif text == "🎤 Ses Çevir":
        bot.reply_to(message, "🎤 Ses çeviri için /tts metin yazabilirsiniz")
    elif text == "🖼️ AI Görsel":
        bot.reply_to(message, "🖼️ AI görsel için /image açıklama yazabilirsiniz")
    else:
        bot.reply_to(message, "❌ Anlamadım reis! /help ile komutları görebilirsin.")

# CALLBACK QUERY HANDLER
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.data.startswith("delete_repo_confirm_"):
            repo_name = call.data.replace("delete_repo_confirm_", "")
            try:
                user = github.get_user()
                repo = user.get_repo(repo_name)
                repo.delete()
                bot.answer_callback_query(call.id, f"✅ {repo_name} silindi!")
                bot.edit_message_text(f"✅ *{repo_name}* repository'si başarıyla silindi!", 
                                    call.message.chat.id, call.message.message_id, parse_mode='Markdown')
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ Silme hatası: {str(e)}")
        elif call.data == "delete_repo_cancel":
            bot.answer_callback_query(call.id, "❌ İşlem iptal edildi")
            bot.edit_message_text("❌ Repository silme işlemi iptal edildi.", 
                                call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Hata: {str(e)}")

# BOTU BAŞLAT
if __name__ == "__main__":
    logger.info("🤖 ReisBot Premium başlatılıyor...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Bot başlatma hatası: {e}")
