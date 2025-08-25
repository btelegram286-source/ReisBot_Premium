#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube İndirme Sorunları Çözümü
yt-dlp ile youtube-dl arasında geçiş yapar ve sorunları çözer.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_yt_dlp():
    """yt-dlp kurulu mu kontrol et"""
    try:
        import yt_dlp
        return True
    except ImportError:
        return False

def check_youtube_dl():
    """youtube-dl kurulu mu kontrol et"""
    try:
        import youtube_dl
        return True
    except ImportError:
        return False

def install_yt_dlp():
    """yt-dlp kur"""
    print("📦 yt-dlp kuruluyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "--upgrade"])
        print("✅ yt-dlp başarıyla kuruldu!")
        return True
    except Exception as e:
        print(f"❌ yt-dlp kurulum hatası: {e}")
        return False

def install_youtube_dl():
    """youtube-dl kur"""
    print("📦 youtube-dl kuruluyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-dl", "--upgrade"])
        print("✅ youtube-dl başarıyla kuruldu!")
        return True
    except Exception as e:
        print(f"❌ youtube-dl kurulum hatası: {e}")
        return False

def switch_to_yt_dlp():
    """yt-dlp'ye geçiş yap"""
    print("🔄 yt-dlp'ye geçiş yapılıyor...")
    
    # Önce mevcut youtube-dl'yi kaldır
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "youtube-dl", "-y"])
        print("✅ youtube-dl kaldırıldı")
    except:
        print("ℹ️  youtube-dl zaten kaldırılmış")
    
    # yt-dlp kur
    if install_yt_dlp():
        # requirements.txt güncelle
        update_requirements("yt-dlp")
        return True
    return False

def switch_to_youtube_dl():
    """youtube-dl'ye geçiş yap"""
    print("🔄 youtube-dl'ye geçiş yapılıyor...")
    
    # Önce mevcut yt-dlp'yi kaldır
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "yt-dlp", "-y"])
        print("✅ yt-dlp kaldırıldı")
    except:
        print("ℹ️  yt-dlp zaten kaldırılmış")
    
    # youtube-dl kur
    if install_youtube_dl():
        # requirements.txt güncelle
        update_requirements("youtube-dl")
        return True
    return False

def update_requirements(library):
    """requirements.txt dosyasını güncelle"""
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Eski youtube kütüphanelerini kaldır
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if not any(x in line.lower() for x in ['youtube-dl', 'yt-dlp']):
                    new_lines.append(line)
            
            # Yeni kütüphaneyi ekle
            if library == "yt-dlp":
                new_lines.append("yt-dlp==2023.11.16")
            else:
                new_lines.append("youtube-dl==2021.12.17")
            
            with open(req_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"✅ requirements.txt {library} ile güncellendi")
            
        except Exception as e:
            print(f"❌ requirements.txt güncelleme hatası: {e}")
    else:
        print("ℹ️  requirements.txt bulunamadı, yeni oluşturuluyor...")
        try:
            with open(req_file, 'w', encoding='utf-8') as f:
                if library == "yt-dlp":
                    f.write("yt-dlp==2023.11.16")
                else:
                    f.write("youtube-dl==2021.12.17")
            print(f"✅ requirements.txt {library} ile oluşturuldu")
        except Exception as e:
            print(f"❌ requirements.txt oluşturma hatası: {e}")

def update_download_function():
    """İndirme fonksiyonunu güncelle"""
    print("📝 İndirme fonksiyonu güncelleniyor...")
    
    main_file = "main.py"
    if not os.path.exists(main_file):
        print("❌ main.py bulunamadı!")
        return False
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # yt-dlp için import ve fonksiyon güncelleme
        if "import yt_dlp" not in content:
            # youtube_dl import'unu yt_dlp ile değiştir
            content = content.replace("import youtube_dl", "import yt_dlp as youtube_dl")
            content = content.replace("from youtube_dl", "from yt_dlp")
        
        # Fonksiyon içeriğini güncelle
        if "def download_youtube_audio" in content:
            # Modern yt-dlp formatına uygun hale getir
            new_function = """
def download_youtube_audio(url):
    \"\"\"YouTube'dan audio indir\"\"\"
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
"""
            # Eski fonksiyonu yeniyle değiştir
            content = re.sub(
                r'def download_youtube_audio\(url\):.*?return f".*?"\)',
                new_function,
                content,
                flags=re.DOTALL
            )
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ İndirme fonksiyonu güncellendi")
        return True
        
    except Exception as e:
        print(f"❌ Fonksiyon güncelleme hatası: {e}")
        return False

def check_ffmpeg():
    """FFmpeg kurulu mu kontrol et"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def install_ffmpeg_windows():
    """Windows için FFmpeg kurulum rehberi"""
    print("🎵 FFmpeg kurulumu gerekiyor!")
    print("\n📥 FFmpeg'i şuradan indirin:")
    print("https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z")
    print("\n📁 İndirdikten sonra:")
    print("1. Dosyayı açın")
    print("2. 'bin' klasöründeki ffmpeg.exe'yi kopyalayın")
    print("3. C:\\Windows\\System32\\ klasörüne yapıştırın")
    print("4. Veya proje dizinine koyun")
    print("\n🔍 Alternatif olarak Chocolatey ile:")
    print("choco install ffmpeg")

def main():
    print("🎵 YouTube İndirme Sorun Çözücü")
    print("=" * 40)
    
    # Mevcut durumu kontrol et
    yt_dlp_installed = check_yt_dlp()
    youtube_dl_installed = check_youtube_dl()
    ffmpeg_installed = check_ffmpeg()
    
    print(f"📦 yt-dlp kurulu: {'✅' if yt_dlp_installed else '❌'}")
    print(f"📦 youtube-dl kurulu: {'✅' if youtube_dl_installed else '❌'}")
    print(f"🎵 FFmpeg kurulu: {'✅' if ffmpeg_installed else '❌'}")
    
    if not ffmpeg_installed:
        install_ffmpeg_windows()
    
    print("\n🔧 Çözüm seçenekleri:")
    print("1. yt-dlp'ye geçiş yap (önerilen)")
    print("2. youtube-dl'ye geçiş yap")
    print("3. Sadece requirements.txt güncelle")
    print("4. Çıkış")
    
    choice = input("\nSeçiminiz (1-4): ").strip()
    
    if choice == "1":
        if switch_to_yt_dlp():
            update_download_function()
    elif choice == "2":
        if switch_to_youtube_dl():
            update_download_function()
    elif choice == "3":
        lib = input("Hangi kütüphane? (yt-dlp/youtube-dl): ").strip().lower()
        if lib in ["yt-dlp", "youtube-dl"]:
            update_requirements(lib)
        else:
            print("❌ Geçersiz seçim!")
    elif choice == "4":
        print("👋 Çıkış yapılıyor...")
        return
    else:
        print("❌ Geçersiz seçim!")
    
    print("\n✅ İşlem tamamlandı!")
    print("📋 Sonraki adımlar:")
    print("1. Botu yeniden başlatın")
    print("2. YouTube indirmeyi test edin")

if __name__ == "__main__":
    import re  # re modülünü import et
    main()
